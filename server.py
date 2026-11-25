import asyncio, json, sys, os, uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from engine import Engine

ROOT=Path(__file__).resolve().parent
engine=Engine(json.loads((ROOT/'config.json').read_text(encoding='utf-8')))
@asynccontextmanager
async def lifespan(app):
    yield
    await stop_session()

app=FastAPI(docs_url=None,redoc_url=None,lifespan=lifespan)
peers=set()
lock=asyncio.Lock()

class Event(BaseModel):
    type: Literal['comment','gift','like','control','connection']
    user_id: str=Field(default='test-user',min_length=1,max_length=80)
    name: str=Field(default='Misafir',min_length=1,max_length=40)
    text: str=Field(default='',max_length=250)
    gift: str=Field(default='Rose',max_length=80)
    gift_id: int=Field(default=0,ge=0)
    count: int=Field(default=1,ge=1,le=100000)
    event_id: str=Field(default='',max_length=180)
    avatar: str=Field(default='',max_length=1000)
    @field_validator('avatar')
    @classmethod
    def avatar_url(cls,v):
        if v and not v.startswith('https://'): raise ValueError('Avatar HTTPS olmalı')
        return v

def allowed(origin):
    if not origin: return True # Local Python listener has no Origin header.
    try:
        url=urlparse(origin)
        return url.scheme=='http' and url.hostname in ('127.0.0.1','localhost','::1') and url.port==8765
    except ValueError: return False

@app.middleware('http')
async def local_only(request:Request,call_next):
    if request.headers.get('host','') not in ('127.0.0.1:8765','localhost:8765','[::1]:8765'):
        return __import__('fastapi').responses.JSONResponse({'detail':'Yerel adres gerekli'},status_code=403)
    if request.method in ('POST','DELETE','PUT','PATCH'):
        if not allowed(request.headers.get('origin')):
            return __import__('fastapi').responses.JSONResponse({'detail':'Kaynak reddedildi'},status_code=403)
        if int(request.headers.get('content-length','0'))>32768:
            return __import__('fastapi').responses.JSONResponse({'detail':'İstek çok büyük'},status_code=413)
    response=await call_next(request)
    response.headers['Cache-Control']='no-store'
    return response

@app.get('/')
async def setup(): return FileResponse(ROOT/'app'/'setup.html')
@app.get('/panel')
async def panel(): return FileResponse(ROOT/'app'/'index.html')
@app.get('/overlay')
async def overlay(): return FileResponse(ROOT/'app'/'overlay.html')
@app.get('/api/health')
async def health(): return {'pid':os.getpid(),'instance':os.environ.get('HALAY_TEST_INSTANCE','')}
@app.get('/api/state')
async def state(): return snapshot()

async def broadcast():
    payload=snapshot()
    async def send(ws):
        try: await asyncio.wait_for(ws.send_json(payload),2)
        except Exception:
            peers.discard(ws)
            try: await ws.close()
            except Exception: pass
    await asyncio.gather(*(send(ws) for ws in tuple(peers)))


# The web server owns listener/demo lifecycle: the operator starts once.
session={'running':False,'mode':'demo','username':'','scene':'halay','capacity':24}
listener=None
demo_task=None
listener_log=None
listener_watch=None
session_lock=asyncio.Lock()

def snapshot():
    result=engine.snapshot()
    result['session']={**session,'listener_running':listener is not None and listener.returncode is None}
    return result

class SessionSettings(BaseModel):
    mode: Literal['demo','live']='demo'
    scene: Literal['halay','orbit']='halay'
    capacity: int=Field(default=80,ge=4,le=120)
    username: str=Field(default='',max_length=32)
    layout: Literal['circle','arc','wide','line']='circle'
    theme: Literal['night','sunset']='night'
    quality: Literal['balanced','high']='balanced'
    music: Literal['halay','drum','off']='halay'
    volume: int=Field(default=45,ge=0,le=100)
    @field_validator('username')
    @classmethod
    def clean_username(cls,value):
        value=value.strip().lstrip('@')
        if value and not all(ch.isascii() and (ch.isalnum() or ch in '._') for ch in value):
            raise ValueError('TikTok kullanıcı adı harf, sayı, nokta veya alt çizgi içermeli')
        return value

SETTINGS_PATH=ROOT/'runtime'/'settings.json'

def saved_settings():
    try: return SessionSettings.model_validate_json(SETTINGS_PATH.read_text(encoding='utf-8')).model_dump()
    except (OSError,ValueError): return SessionSettings().model_dump()

@app.get('/api/settings')
async def get_settings(): return saved_settings()

@app.post('/api/settings')
async def save_settings(settings:SessionSettings):
    async with session_lock:
        SETTINGS_PATH.parent.mkdir(exist_ok=True)
        temporary=SETTINGS_PATH.with_suffix('.tmp')
        temporary.write_text(settings.model_dump_json(indent=2),encoding='utf-8')
        temporary.replace(SETTINGS_PATH)
    return {'ok':True}

class AudioSettings(BaseModel):
    music: Literal['halay','drum','off']='halay'
    volume: int=Field(default=45,ge=0,le=100)

@app.post('/api/audio')
async def set_audio(settings:AudioSettings):
    async with session_lock:
        selected=saved_settings()
        selected.update(settings.model_dump())
        SETTINGS_PATH.parent.mkdir(exist_ok=True)
        temporary=SETTINGS_PATH.with_suffix('.tmp')
        temporary.write_text(SessionSettings(**selected).model_dump_json(indent=2),encoding='utf-8')
        temporary.replace(SETTINGS_PATH)
        async with lock:
            engine.music=settings.music
            engine.volume=settings.volume
            session.update(settings.model_dump())
            await broadcast()
    return {'ok':True}

CONFIG_PATH=ROOT/'config.json'
PROFILES_PATH=ROOT/'runtime'/'profiles.json'

class GiftBinding(BaseModel):
    name: str=Field(min_length=1,max_length=80)
    gift_id: int=Field(default=0,ge=0)
    action: Literal['join','speed','drummer','zurna','confetti']='join'
    points: int=Field(default=1,ge=0,le=10000)
    @field_validator('name')
    @classmethod
    def clean_name(cls,name):
        if not name.strip(): raise ValueError('Hediye adı boş olamaz')
        return name.strip()

class RulesSettings(BaseModel):
    bpm: int=Field(default=112,ge=60,le=220)
    like_threshold: int=Field(default=300,ge=1,le=10000)
    gifts: list[GiftBinding]=Field(min_length=1,max_length=40)
    @field_validator('gifts')
    @classmethod
    def unique_gifts(cls,gifts):
        names=[g.name for g in gifts];ids=[g.gift_id for g in gifts if g.gift_id]
        if len(names)!=len(set(names)) or len(ids)!=len(set(ids)): raise ValueError('Hediye adı ve kimliği tekrar edemez')
        return gifts

def current_rules():
    bindings=[]
    for name,rule in engine.config['gift_rules'].items():
        bindings.append(dict(name=name,gift_id=0,**rule))
    for gid,rule in engine.config.get('gift_ids',{}).items():
        match=next((b for b in bindings if b['action']==rule['action'] and b['points']==rule['points'] and b['gift_id']==0),None)
        if match: match['gift_id']=int(gid)
        else: bindings.append(dict(name='Hediye '+str(gid),gift_id=int(gid),**rule))
    return dict(bpm=engine.config['base_bpm'],like_threshold=engine.config['like_threshold'],gifts=bindings)

@app.get('/api/rules')
async def get_rules(): return current_rules()

@app.post('/api/rules')
async def save_rules(rules:RulesSettings):
    async with lock:
        config={**engine.config,'base_bpm':rules.bpm,'like_threshold':rules.like_threshold,
                'gift_rules':{g.name:{'action':g.action,'points':g.points} for g in rules.gifts},
                'gift_ids':{str(g.gift_id):{'action':g.action,'points':g.points} for g in rules.gifts if g.gift_id}}
        temporary=CONFIG_PATH.with_suffix('.tmp')
        temporary.write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
        temporary.replace(CONFIG_PATH)
        engine.config.update(config)
        await broadcast()
    return {'ok':True}

class Profile(BaseModel):
    id: str=Field(default='',max_length=40)
    name: str=Field(min_length=1,max_length=40)
    settings: SessionSettings
    rules: RulesSettings | None=None
    @field_validator('name')
    @classmethod
    def clean_profile_name(cls,name):
        if not name.strip(): raise ValueError('Profil adı boş olamaz')
        return name.strip()

def profiles():
    try:
        raw=json.loads(PROFILES_PATH.read_text(encoding='utf-8'))
        if not isinstance(raw,list): return []
        return [Profile.model_validate(item).model_dump() for item in raw[:20]]
    except (OSError,ValueError): return []

def write_profiles(items):
    PROFILES_PATH.parent.mkdir(exist_ok=True)
    temporary=PROFILES_PATH.with_suffix('.tmp')
    temporary.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
    temporary.replace(PROFILES_PATH)

@app.get('/api/profiles')
async def get_profiles(): return profiles()

@app.post('/api/profiles')
async def save_profile(profile:Profile):
    async with session_lock:
        items=profiles();value=profile.model_dump()
        if profile.id:
            index=next((i for i,p in enumerate(items) if p['id']==profile.id),None)
            if index is None: raise HTTPException(404,'Profil bulunamadı')
            items[index]=value
        else:
            if len(items)>=20: raise HTTPException(409,'En fazla 20 profil kaydedilebilir')
            value['id']=uuid.uuid4().hex;items.append(value)
        write_profiles(items)
    return value

@app.delete('/api/profiles/{profile_id}')
async def delete_profile(profile_id:str):
    async with session_lock:
        items=profiles();remaining=[p for p in items if p['id']!=profile_id]
        if len(items)==len(remaining): raise HTTPException(404,'Profil bulunamadı')
        write_profiles(remaining)
    return {'ok':True}

@app.post('/api/shutdown')
async def shutdown():
    async with session_lock:
        await stop_session()
    import signal
    asyncio.get_running_loop().call_later(.3,os.kill,os.getpid(),signal.SIGTERM)
    return {'ok':True}

async def watch_listener(process):
    await process.wait()
    async with lock:
        if listener is process and session['running']:
            session['running']=False
            engine.source='TikTok dinleyicisi durdu. Bağlantıyı yeniden başlatın.'
            await broadcast()

async def stop_session():
    global listener,demo_task,listener_log,listener_watch
    session['running']=False
    if listener_watch:
        listener_watch.cancel()
        await asyncio.gather(listener_watch,return_exceptions=True)
        listener_watch=None
    if demo_task:
        demo_task.cancel()
        await asyncio.gather(demo_task,return_exceptions=True)
        demo_task=None
    if listener:
        if listener.returncode is None:
            try:
                if sys.platform=='win32':
                    killer=await asyncio.create_subprocess_exec('taskkill','/PID',str(listener.pid),'/T','/F',stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.DEVNULL,creationflags=0x08000000)
                    await killer.wait()
                else: listener.terminate()
            except ProcessLookupError: pass
            try: await asyncio.wait_for(listener.wait(),5)
            except asyncio.TimeoutError:
                listener.kill();await listener.wait()
        listener=None
    if listener_log:
        listener_log.close();listener_log=None
    session['running']=False

async def automatic_demo():
    # Videodaki gibi izleyiciler hızla yorum yazıp halkaya katılır; ara sıra hediye ve beğeni gelir.
    names=['Melih','Zeynep','Efe','Elif','Baran','Dilan','Deniz','Yağmur','Can','Sinem','Mert','Bahar','Ali','Ceren','Umut','Nehir','Aslı','Emre','Duru','Özgür','Nizo','Gamze','Tayyip','Fatoş','Ceylan','Murat','Sevgi','Hazal','Arda','Ebru']
    # Videodaki gibi çoğunluk katılım yorumu; kıyafet ve kostüm komutları arada bir gelir.
    comments=['katıl','halaya katıl','katıl','çok güzel','katıl','👏👏','yallıya katıl','halay!','katıl','harika','kız','katıl','halaya katıl','qız','çok güzel','katıl','erkek','yallıya katıl','harika','tilki','katıl','kedi','tavşan']
    index=0
    while True:
        async with lock:
            uid='auto'+str(index%150)
            name=names[index%len(names)]+(' '+str(index//len(names)+1) if index>=len(names) else '')
            payload=dict(type='comment',user_id=uid,name=name,text=comments[(index*5)%len(comments)],count=1)
            if uid not in engine.users and len(engine.users)>=engine.config['max_users']:
                uid=next(iter(engine.users));payload['user_id']=uid;payload['name']=engine.users[uid]['name']
            engine.apply(payload)
            if index%3==2:
                gift='Drum' if index%12==11 else 'Zurna' if index%12==5 else 'Heart Me' if index%7==6 else 'Rose'
                engine.apply(dict(type='gift',user_id=uid,name=payload['name'],gift=gift,count=1+index%3))
            await broadcast()
        index+=1
        # Açılışta kalabalık hızla dolar (videodaki gibi), sonra yeni gelenler tek tek katılır.
        await asyncio.sleep(.3 if index<70 else 1.6)

@app.post('/api/session/start')
async def start_session(settings:SessionSettings):
    global listener,demo_task,listener_log,listener_watch
    async with session_lock:
        if settings.mode=='live':
            if not settings.username: raise HTTPException(422,'Canlı modda TikTok kullanıcı adını girin.')
            import importlib.util
            if importlib.util.find_spec('TikTokLive') is None: raise HTTPException(409,'Önce TIKTOK_KUR.cmd dosyasını çalıştırın.')
        await stop_session()
        async with lock:
            engine.reset()
            engine.ring_capacity=settings.capacity
            engine.scene=settings.scene
            engine.layout=settings.layout
            engine.theme=settings.theme
            engine.quality=settings.quality
            engine.music=settings.music
            engine.volume=settings.volume
            session.update(running=True,**settings.model_dump())
            engine.source='TikTok bağlanıyor: @'+settings.username if settings.mode=='live' else 'Otomatik demo'
            try:
                if settings.mode=='live':
                    (ROOT/'runtime').mkdir(exist_ok=True)
                    (ROOT/'work').mkdir(exist_ok=True)
                    listener_log=(ROOT/'runtime'/'tiktok.log').open('a',encoding='utf-8')
                    env={**os.environ,'TEMP':str(ROOT/'work'),'TMP':str(ROOT/'work'),'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8'}
                    listener=await asyncio.create_subprocess_exec(sys.executable,'-B',str(ROOT/'tiktok_listener.py'),settings.username,
                        cwd=str(ROOT),env=env,stdout=listener_log,stderr=listener_log,
                        creationflags=0x08000000 if sys.platform=='win32' else 0)
                    if listener.returncode is None: listener_watch=asyncio.create_task(watch_listener(listener))
                else:
                    demo_task=asyncio.create_task(automatic_demo())
            except OSError as exc:
                session['running']=False
                engine.source='Başlatılamadı'
                if listener_log: listener_log.close();listener_log=None
                raise HTTPException(503,'Dinleyici başlatılamadı. runtime/tiktok.log dosyasını kontrol edin.') from exc
            await broadcast()
    return {'ok':True,'session':snapshot()['session']}

@app.post('/api/session/stop')
async def end_session():
    async with session_lock:
        await stop_session()
        async with lock:
            engine.source='Durduruldu'
            await broadcast()
    return {'ok':True}


@app.post('/api/event')
async def event(e:Event):
    async with lock:
        try: changed=engine.apply(e.model_dump())
        except ValueError as exc: raise HTTPException(409,str(exc))
        if changed: await broadcast()
    return {'ok':True,'changed':changed,'revision':engine.revision}

@app.websocket('/ws')
async def ws(ws:WebSocket):
    if not allowed(ws.headers.get('origin')):
        await ws.close(code=1008);return
    await ws.accept()
    async with lock:
        peers.add(ws)
        await ws.send_json(snapshot())
    try:
        while True:
            # Read-only socket; all events pass through the validated HTTP endpoint.
            if await ws.receive_text()=='ping': await ws.send_json({'type':'pong'})
    except (WebSocketDisconnect,RuntimeError): pass
    finally: peers.discard(ws)

app.mount('/assets',StaticFiles(directory=ROOT/'app'),name='assets')
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8765,ws_max_size=8192)
