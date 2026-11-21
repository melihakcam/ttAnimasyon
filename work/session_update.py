from pathlib import Path
r=Path(r'D:\tiktokAnimasyon')
p=r/'engine.py';s=p.read_text(encoding='utf-8').replace("self.scene = 'halay'", "self.scene = 'halay'\n        self.ring_capacity = self.config.get('ring_capacity',24)")
s=s.replace("if eid:\n            self.seen[eid]=True", "self.admit()\n        if eid:\n            self.seen[eid]=True")
s=s.replace("    def snapshot(self):", "    def admit(self):\n        count=0\n        for u in self.users.values():\n            if not (u['joined'] or u.get('queued')): continue\n            count+=1\n            u['joined']=count<=self.ring_capacity\n            u['queued']=not u['joined']\n\n    def snapshot(self):")
s=s.replace("events=self.events,scene=self.scene,", "events=self.events,scene=self.scene,ring_capacity=self.ring_capacity,queued=sum(bool(u.get('queued')) for u in self.users.values()),")
p.write_text(s,encoding='utf-8')
p=r/'server.py';s=p.read_text(encoding='utf-8').replace('import asyncio, json, ipaddress','import asyncio, json, sys, os\nfrom contextlib import asynccontextmanager')
s=s.replace("app=FastAPI(docs_url=None,redoc_url=None)", """@asynccontextmanager
async def lifespan(app):
    yield
    await stop_session()

app=FastAPI(docs_url=None,redoc_url=None,lifespan=lifespan)""")
s=s.replace("async def panel(): return FileResponse(ROOT/'app'/'index.html')", "async def setup(): return FileResponse(ROOT/'app'/'setup.html')\n@app.get('/panel')\nasync def panel(): return FileResponse(ROOT/'app'/'index.html')")
s=s.replace("async def state(): return engine.snapshot()", "async def state(): return snapshot()")
s=s.replace('payload=engine.snapshot()','payload=snapshot()').replace('await ws.send_json(engine.snapshot())','await ws.send_json(snapshot())')
insert=r'''
# The web server owns listener/demo lifecycle: the operator starts once.
session={'running':False,'mode':'demo','username':'','scene':'halay','capacity':24}
listener=None
demo_task=None
listener_log=None
session_lock=asyncio.Lock()

def snapshot():
    result=engine.snapshot()
    result['session']={**session,'listener_running':listener is not None and listener.returncode is None}
    return result

class SessionSettings(BaseModel):
    mode: Literal['demo','live']='demo'
    scene: Literal['halay','orbit']='halay'
    capacity: int=Field(default=24,ge=4,le=60)
    username: str=Field(default='',max_length=32)
    @field_validator('username')
    @classmethod
    def clean_username(cls,value):
        value=value.strip().lstrip('@')
        if value and not all(ch.isascii() and (ch.isalnum() or ch in '._') for ch in value):
            raise ValueError('TikTok kullanıcı adı harf, sayı, nokta veya alt çizgi içermeli')
        return value

async def stop_session():
    global listener,demo_task,listener_log
    if demo_task:
        demo_task.cancel()
        await asyncio.gather(demo_task,return_exceptions=True)
        demo_task=None
    if listener:
        if listener.returncode is None:
            try: listener.terminate()
            except ProcessLookupError: pass
            try: await asyncio.wait_for(listener.wait(),5)
            except asyncio.TimeoutError:
                listener.kill();await listener.wait()
        listener=None
    if listener_log:
        listener_log.close();listener_log=None
    session['running']=False

async def automatic_demo():
    names=['Melih','Zeynep','Efe','Elif','Baran','Dilan','Deniz','Yağmur','Can','Sinem','Mert','Bahar','Ali','Ceren','Umut','Nehir','Aslı','Emre']
    index=0
    while True:
        async with lock:
            uid='auto'+str(index%60)
            name=names[index%len(names)]+(' '+str(index//len(names)+1) if index>=len(names) else '')
            payload=dict(type='comment',user_id=uid,name=name,text='erkek' if index%3==0 else 'halay',count=1)
            if uid not in engine.users and len(engine.users)>=engine.config['max_users']:
                uid=next(iter(engine.users));payload['user_id']=uid;payload['name']=engine.users[uid]['name']
            engine.apply(payload)
            if index%4==3:
                engine.apply(dict(type='gift',user_id=uid,name=payload['name'],gift='Drum' if index%8==7 else 'Rose',count=1))
            await broadcast()
        index+=1
        await asyncio.sleep(2)

@app.post('/api/session/start')
async def start_session(settings:SessionSettings):
    global listener,demo_task,listener_log
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

'''
s=s.replace("@app.post('/api/event')", insert+"\n@app.post('/api/event')")
p.write_text(s,encoding='utf-8')
(r/'app/setup.html').write_text('''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Halay Stüdyo • Yayını hazırla</title><link rel="stylesheet" href="/assets/panel.css"><style>main.setup{display:block;max-width:900px;padding-top:60px}.setup h1{margin-bottom:16px}.choices{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:28px 0}.choice{display:block;border:1px solid #3b4048;border-radius:14px;padding:22px;background:#22262c;cursor:pointer}.choice:has(input:checked){border-color:#ebc577;background:#302b21}.choice input{width:auto;margin:0 0 18px}.choice strong{display:block;color:#f8e6bc;font-size:22px;margin-bottom:8px}.choice small{font-size:14px}.setup .desk{margin:30px 0}.setup .intro{line-height:1.8}.setup .two{gap:22px}.setup .liveinfo{padding:15px;border:1px solid #494234;border-radius:8px;margin-bottom:20px;color:#e9cf91;font-size:14px;line-height:1.7}.statusrow{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:20px}#status{color:#bbc6b8;font-size:14px}@media(max-width:600px){.setup .two{grid-template-columns:1fr}.choices{gap:10px}.choice{padding:16px}}</style></head><body><header><a class="brand" href="/">H<span>•</span> HALAY STÜDYO</a><span id="connection">Bağlanıyor…</span></header><main class="setup"><div class="eyebrow">SAHNENİ SEÇ · KAPASİTEYİ AYARLA · BAŞLAT</div><h1>Yayını bir kez hazırla.</h1><p class="intro">Başlattıktan sonra yorum ve hediyeler katılımcıları otomatik sahneye getirir.<br>İsimleri tek tek eklemene gerek yok.</p><form id="setupform" class="desk"><h2>Hangi sahne açılsın?</h2><div class="choices"><label class="choice"><input type="radio" name="scene" value="halay" checked><strong>Halay meydanı</strong><small>Halka halinde dans, kullanıcı isimleri ve davulcu.</small></label><label class="choice"><input type="radio" name="scene" value="orbit"><strong>Çember dansı</strong><small>Aynı katılımcılarla alternatif animasyon.</small></label></div><div class="two"><label>Halkadaki kişi sayısı<input id="capacity" type="number" min="4" max="60" value="24" required><small>4–60 kişi. Halka dolunca yeniler sıraya alınır.</small></label><label>Çalışma modu<select id="mode"><option value="demo">Otomatik demo · hesap gerekmez</option><option value="live">Gerçek TikTok yayını</option></select></label></div><label id="userrow" hidden>TikTok kullanıcı adı<input id="username" maxlength="32" placeholder="@kullaniciadi" autocomplete="off"><small>Görünen ad yerine profilindeki kullanıcı adını yaz. Şifre gerekmez.</small></label><p id="liveinfo" class="liveinfo" hidden>Başlat düğmesi TikTok dinleyicisini de açar. Hesabında canlı yayın açık olmalı. Bu ekran, görüntüyü TikTok'a yayınlamaz; OBS bağlantısı ayrıca yapılır.</p><button id="start" class="primary" type="submit">Başlat · sahneyi aç</button><p class="note">Demo modunda örnek izleyiciler kendiliğinden gelir. Canlı modda sadece TikTok'tan gelen gerçek olaylar kullanılır. Yeni oturum mevcut katılımcıları ve puanları sıfırlar.</p><div class="statusrow"><span id="status" role="status" aria-live="polite"></span><button id="stop" type="button" hidden>Oturumu durdur</button></div></form><p><a href="/panel">Ayrıntılı kontrol ve test paneli</a> · <a href="/overlay" target="_blank" rel="noopener">Yayın sahnesi</a></p><p class="note">Bu sürümde halay ve alternatif çember sahnesi hazır. Cenaze gibi ayrı sahneler henüz eklenmedi.</p></main><script type="module" src="/assets/setup.js"></script></body></html>''',encoding='utf-8')
(r/'app/setup.js').write_text('''import {connect} from './transport.js';
const $=s=>document.querySelector(s);let running=false,initial=true;
$('#mode').onchange=()=>{const live=$('#mode').value==='live';$('#userrow').hidden=!live;$('#liveinfo').hidden=!live;$('#username').required=live};
connect(s=>{const t=s.session||{};running=t.running;$('#status').textContent=`${s.source} · ${s.users.filter(u=>u.joined).length}/${s.ring_capacity} kişi · ${s.queued||0} sırada`;$('#stop').hidden=!running;$('#start').textContent=running?'Yeni oturum başlat':'Başlat · sahneyi aç';if(initial&&running){$('#mode').value=t.mode;$('#username').value=t.username;$('#capacity').value=t.capacity;document.querySelector(`input[name="scene"][value="${t.scene}"]`).checked=true;$('#mode').onchange()}initial=false},ok=>{$('#connection').textContent=ok?'Yerel sunucu bağlı':'Yeniden bağlanıyor…'});
async function call(path,payload){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await r.json();if(!r.ok)throw Error(typeof data.detail==='string'?data.detail:'Ayarları kontrol edin.');return data}
$('#setupform').onsubmit=async e=>{e.preventDefault();if(running&&!confirm('Yeni oturum mevcut katılımcıları ve puanları sıfırlasın mı?'))return;$('#start').disabled=true;try{await call('/api/session/start',{mode:$('#mode').value,scene:document.querySelector('input[name="scene"]:checked').value,capacity:Number($('#capacity').value),username:$('#username').value});location.href='/overlay'}catch(err){$('#status').textContent=err.message;$('#start').disabled=false}};
$('#stop').onclick=async()=>{try{await call('/api/session/stop',{});$('#status').textContent='Oturum durduruldu.'}catch(err){$('#status').textContent=err.message}};
''',encoding='utf-8')
# Include capacity in the panel and retain the setup as the navigation home.
p=r/'app/panel.js';s=p.read_text(encoding='utf-8').replace("`${joined.length} dansçı ·", "`${joined.length}/${s.ring_capacity} dansçı · ${s.queued||0} sırada ·");s=s.replace("${u.joined?'':' · bekliyor'}", "${u.joined?'':u.queued?' · sırada':' · beğeni bekliyor'}");p.write_text(s,encoding='utf-8')
# Keep automated browser checks pointed to the explicit test panel.
p=r/'tests/browser_qa.py';s=p.read_text(encoding='utf-8').replace("page.goto('http://127.0.0.1:8765')", "page.goto('http://127.0.0.1:8765/panel')").replace("startsWith('20 dansçı')", "startsWith('20/24 dansçı')");p.write_text(s,encoding='utf-8')
# API integration tests now check both the setup and panel routes.
p=r/'tests/integration.py';s=p.read_text(encoding='utf-8').replace("['/','/overlay'", "['/','/panel','/overlay'");p.write_text(s,encoding='utf-8')
print('Automatic session setup implemented.')
