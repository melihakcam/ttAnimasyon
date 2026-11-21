from pathlib import Path
r=Path(r'D:\tiktokAnimasyon')
p=r/'server.py';s=p.read_text(encoding='utf-8').replace('import asyncio, json, sys, os','import asyncio, json, sys, os, uuid')
s=s.replace("if request.method=='POST':", "if request.method in ('POST','DELETE','PUT','PATCH'):")
s=s.replace("if int(request.headers.get('content-length','0'))>8192:", "if int(request.headers.get('content-length','0'))>32768:")
needle='async def watch_listener(process):'
extra=r'''CONFIG_PATH=ROOT/'config.json'
PROFILES_PATH=ROOT/'runtime'/'profiles.json'

class GiftBinding(BaseModel):
    name: str=Field(min_length=1,max_length=80)
    gift_id: int=Field(default=0,ge=0)
    action: Literal['join','speed','drummer','confetti']='join'
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

'''
s=s.replace(needle,extra+needle)
p.write_text(s,encoding='utf-8')
# Add reusable profiles and a non-technical gift editor to the preparation screen.
p=r/'app/setup.html';s=p.read_text(encoding='utf-8')
s=s.replace('<form id="setupform" class="desk"><h2>Sahne</h2>', '''<form id="setupform" class="desk"><div class="profilebox"><h2>Kayıtlı hazırlıklarım</h2><label>Profil seç<select id="profiles"><option value="">Yeni hazırlık</option></select></label><label>Bu hazırlığın adı<input id="profilename" maxlength="40" placeholder="Örn. Akşam halayı · 24 kişi"></label><div class="quick"><button type="button" id="saveprofile">Profili kaydet</button><button type="button" id="deleteprofile" disabled>Profili sil</button></div><p class="note" id="profilestatus" role="status">Sahne, halka ve hediye kuralları birlikte kaydedilir.</p></div><h2>Sahne</h2>''')
s=s.replace('<div class="divider"></div><label>Çalışma modu', '''<div class="divider"></div><details class="ruleeditor"><summary>Hediye ve katılım kuralları</summary><div class="two"><label>Dans hızı (BPM)<input id="bpm" type="number" min="60" max="220" value="112" required></label><label>Katılım için beğeni<input id="likethreshold" type="number" min="1" max="10000" value="300" required></label></div><p class="note">Yorum yapan kişi otomatik katılır. Hediyeye göre katılım, hızlandırma, davulcu veya konfeti seçebilirsin. Puanlar oyun içindir.</p><div id="giftrules"></div><button type="button" id="addrule">Hediye kuralı ekle</button><small>Canlı hediye adıyla eşleştir. Gerçek hediye kimliğini biliyorsan isteğe bağlı olarak gir; kimlik eşleşmesi önceliklidir. Listedeki hediyeler başlangıç örnekleridir.</small></details><div class="divider"></div><label>Çalışma modu''')
s=s.replace('<small>OBS’ye sadece bu adresi ekle. Kontrol ekranı ve önizleme yayına girmez.</small>', '<small>OBS’ye sadece bu adresi ekle. Kontrol ekranı ve önizleme yayına girmez. Bu sürüm sessizdir; müziğini OBS’de ayrı Medya Kaynağı olarak ekleyebilirsin.</small>')
p.write_text(s,encoding='utf-8')
p=r/'app/setup.css';s=p.read_text(encoding='utf-8')+'''
.profilebox{padding-bottom:22px;border-bottom:1px solid #343940;margin-bottom:25px}.profilebox h2{margin-bottom:17px}.profilebox .quick{margin-bottom:8px}.ruleeditor summary{cursor:pointer;font-size:15px;font-weight:700;color:#e6cc96;padding:9px 0 18px}.ruleeditor[open] summary{margin-bottom:8px}.ruleeditor .two{gap:15px}.giftrule{padding:14px;border:1px solid #3a4049;border-radius:9px;margin:14px 0;background:#22262d}.giftrule .rulegrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.giftrule label{margin-bottom:10px;font-size:12px}.giftrule input,.giftrule select{font-size:13px;padding:10px}.giftrule .remove{font-size:12px;color:#e7a9ae;padding:7px 10px}.profilebox .note{min-height:19px}button:disabled{cursor:default}.ruleeditor>small{line-height:1.6}
''';p.write_text(s,encoding='utf-8')
p=r/'app/setup.js';s=p.read_text(encoding='utf-8')
s=s.replace("try{const r=await fetch('/api/settings');if(r.ok)fill(await r.json())}catch{fill({})}", "")
s=s.replace("const s=settings();await call('/api/settings',s);", "const s=settings(),rules=readRules();await call('/api/rules',rules);await call('/api/settings',s);")
s+=r'''
let savedProfiles=[];
function ruleRow(rule={name:'',gift_id:0,action:'join',points:1}){
 const row=document.createElement('div');row.className='giftrule';
 const grid=document.createElement('div');grid.className='rulegrid';row.append(grid);
 for(const [field,label,type] of [['name','Hediye adı','text'],['gift_id','Hediye kimliği · isteğe bağlı','number'],['action','Ne yapsın?','select'],['points','Adet başına puan','number']]){
  const wrapper=document.createElement('label');wrapper.textContent=label;let input;
  if(type==='select'){input=document.createElement('select');for(const [value,title] of [['join','Halaya katıl'],['speed','Hızlandır'],['drummer','Davulcu olsun'],['confetti','Konfeti göster']])input.add(new Option(title,value))}
  else{input=document.createElement('input');input.type=type;if(type==='number'){input.min='0';input.max=field==='points'?'10000':'999999999'}if(field==='name'){input.required=true;input.maxLength=80}}
  input.dataset.field=field;input.value=field==='gift_id'&&!rule[field]?'':rule[field];wrapper.append(input);grid.append(wrapper);
 }
 const remove=document.createElement('button');remove.type='button';remove.className='remove';remove.textContent='Bu kuralı kaldır';remove.onclick=()=>{if($('#giftrules').children.length>1)row.remove();else $('#profilestatus').textContent='En az bir hediye kuralı kalmalı.'};row.append(remove);return row;
}
function setRules(rules){$('#bpm').value=rules.bpm;$('#likethreshold').value=rules.like_threshold;$('#giftrules').replaceChildren(...rules.gifts.map(ruleRow))}
function readRules(){const gifts=[...$('#giftrules').children].map(row=>{const value={};for(const input of row.querySelectorAll('[data-field]'))value[input.dataset.field]=input.type==='number'?Number(input.value||0):input.value;return value});if(!gifts.length)throw Error('En az bir hediye kuralı ekle.');return {bpm:Number($('#bpm').value),like_threshold:Number($('#likethreshold').value),gifts}}
async function loadProfiles(selected=''){const r=await fetch('/api/profiles');if(!r.ok)throw Error('Profiller alınamadı');savedProfiles=await r.json();$('#profiles').replaceChildren(new Option('Yeni hazırlık',''),...savedProfiles.map(p=>new Option(p.name,p.id)));$('#profiles').value=selected;$('#deleteprofile').disabled=!selected}
$('#profiles').onchange=()=>{const selected=savedProfiles.find(p=>p.id===$('#profiles').value);$('#deleteprofile').disabled=!selected;if(selected){fill(selected.settings);if(selected.rules)setRules(selected.rules);$('#profilename').value=selected.name;$('#profilestatus').textContent='Profil yüklendi. Başlat ile seçili hazırlık uygulanır.'}else{$('#profilename').value='';$('#profilestatus').textContent='Hazırlığını yeni bir isimle kaydedebilirsin.'}};
$('#saveprofile').onclick=async()=>{try{if(!$('#setupform').reportValidity())return;const name=$('#profilename').value.trim();if(!name)throw Error('Hazırlığına bir isim ver.');const result=await call('/api/profiles',{id:$('#profiles').value,name,settings:settings(),rules:readRules()});await loadProfiles(result.id);$('#profilestatus').textContent='Profil kaydedildi.'}catch(err){$('#profilestatus').textContent=err.message}};
$('#deleteprofile').onclick=async()=>{const id=$('#profiles').value;if(!id||!confirm('Seçili kayıtlı profil silinsin mi?'))return;try{const r=await fetch('/api/profiles/'+encodeURIComponent(id),{method:'DELETE'});if(!r.ok)throw Error('Profil silinemedi');await loadProfiles();$('#profilename').value='';$('#profilestatus').textContent='Profil silindi.'}catch(err){$('#profilestatus').textContent=err.message}};
$('#addrule').onclick=()=>{if($('#giftrules').children.length>=40){$('#profilestatus').textContent='En fazla 40 hediye kuralı olabilir.';return}$('#giftrules').append(ruleRow())};
try{const [settingsResponse,rulesResponse]=await Promise.all([fetch('/api/settings'),fetch('/api/rules')]);if(settingsResponse.ok&&!running)fill(await settingsResponse.json());if(rulesResponse.ok)setRules(await rulesResponse.json());await loadProfiles()}catch(err){$('#profilestatus').textContent=err.message}
'''
p.write_text(s,encoding='utf-8')
print('Reusable studio profiles and gift rule editor added.')
