from pathlib import Path
R=Path(r'D:\tiktokAnimasyon')
(R/'app/music.js').write_text(r'''// Original locally rendered loops. The audio clock also drives the dancers.
export class HalayMusic {
 constructor(onStatus=()=>{}){this.onStatus=onStatus;this.ctx=null;this.source=null;this.track='';this.buffers=new Map();this.offset=0;this.anchor=0;this.rate=1;this.generation=0;this.desired={music:'off',volume:45,bpm:112,fast:false,running:false};this.status='off';this.error='';this.metaPromise=null}
 statusChanged(status,error=''){this.status=status;this.error=error;this.onStatus(status,error)}
 ensureContext(){if(this.ctx)return;const Constructor=window.AudioContext||window.webkitAudioContext;if(!Constructor)throw Error('Bu tarayıcı ses motorunu desteklemiyor.');this.ctx=new Constructor();this.gain=this.ctx.createGain();this.gain.gain.value=0;this.analyser=this.ctx.createAnalyser();this.analyser.fftSize=2048;this.gain.connect(this.analyser);this.analyser.connect(this.ctx.destination);this.ctx.onstatechange=()=>{if(this.ctx.state==='running'&&this.desired.running&&this.desired.music!=='off')this.reconcile();else if(this.desired.running&&this.desired.music!=='off')this.statusChanged('blocked')};}
 async metadata(){if(!this.metaPromise)this.metaPromise=fetch('/assets/audio/music.json').then(r=>{if(!r.ok)throw Error('Ritim bilgisi açılamadı.');return r.json()});return this.metaPromise}
 async buffer(track){if(!this.buffers.has(track)){const promise=(async()=>{const meta=await this.metadata(),url=meta.tracks[track];if(!url)throw Error('Ritim seçimi geçersiz.');const response=await fetch(url);if(!response.ok)throw Error('Ritim dosyası açılamadı.');return this.ctx.decodeAudioData(await response.arrayBuffer())})();this.buffers.set(track,promise);promise.catch(()=>this.buffers.delete(track))}return this.buffers.get(track)}
 configure(settings){this.desired={...this.desired,...settings};this.setTempo(this.desired.bpm,this.desired.fast);if(this.gain)this.gain.gain.setTargetAtTime(this.desired.volume/100,this.ctx.currentTime,.035);return this.reconcile()}
 async reconcile(){const generation=++this.generation,d={...this.desired};
  if(!d.running||d.music==='off'){this.stopSource();this.statusChanged('off');return}
  try{
   this.ensureContext();this.gain.gain.setTargetAtTime(d.volume/100,this.ctx.currentTime,.035);
   if(this.source&&this.track===d.music){this.statusChanged(this.ctx.state==='running'?'playing':'blocked');return}
   this.statusChanged('loading');const [buffer,meta]=await Promise.all([this.buffer(d.music),this.metadata()]);if(generation!==this.generation)return;
   const position=this.source?this.position():0;this.stopSource(false);
   const source=this.ctx.createBufferSource();source.buffer=buffer;source.loop=true;source.loopStart=0;source.loopEnd=Math.min(meta.loop_seconds,buffer.duration);source.playbackRate.value=this.rate;source.connect(this.gain);
   this.source=source;this.track=d.music;this.offset=position;this.anchor=this.ctx.currentTime;source.start(this.anchor,position%source.loopEnd);
   if(this.ctx.state!=='running'){this.statusChanged('blocked');this.ctx.resume().catch(()=>{})}else this.statusChanged('playing');
  }catch(error){if(generation!==this.generation)return;this.stopSource();this.statusChanged('error',error.message)}
 }
 position(){return this.source&&this.ctx?this.offset+(this.ctx.currentTime-this.anchor)*this.rate:0}
 beats(){return this.source&&this.ctx?.state==='running'&&this.status==='playing'?this.position()*112/60:null}
 setTempo(bpm=112,fast=false){this.desired.bpm=bpm;this.desired.fast=fast;const rate=bpm/112*(fast?1.45:1);if(Math.abs(rate-this.rate)<1e-9)return;if(this.source){this.offset=this.position();this.anchor=this.ctx.currentTime;this.source.playbackRate.setValueAtTime(rate,this.anchor)}this.rate=rate}
 async unlock(){try{this.ensureContext();const resumed=this.ctx.resume();await resumed;await this.reconcile()}catch(error){this.statusChanged('error',error.message)}}
 stopSource(reset=true){if(this.source){try{this.source.stop();this.source.disconnect()}catch{}this.source=null}if(reset)this.offset=0;this.track=''}
 stop(){++this.generation;this.desired.running=false;this.stopSource();this.statusChanged('off')}
 diagnostics(){let rms=0;if(this.analyser){const samples=new Float32Array(this.analyser.fftSize);this.analyser.getFloatTimeDomainData(samples);rms=Math.sqrt(samples.reduce((sum,value)=>sum+value*value,0)/samples.length)}return {status:this.status,context:this.ctx?.state||'not-created',track:this.track,rate:this.rate,position:this.position(),beats:this.beats(),volume:this.desired.volume,rms,error:this.error}}
}
''',encoding='utf-8')
p=R/'engine.py';s=p.read_text(encoding='utf-8').replace("self.quality = 'balanced'", "self.quality = 'balanced'\n        self.music = 'halay'\n        self.volume = 45")
s=s.replace('old_layout,old_theme,old_quality=self.layout,self.theme,self.quality','old_layout,old_theme,old_quality=self.layout,self.theme,self.quality\n                old_music,old_volume=self.music,self.volume')
s=s.replace('self.layout,self.theme,self.quality=old_layout,old_theme,old_quality','self.layout,self.theme,self.quality=old_layout,old_theme,old_quality\n                self.music,self.volume=old_music,old_volume')
s=s.replace('quality=self.quality,','quality=self.quality,music=self.music,volume=self.volume,')
p.write_text(s,encoding='utf-8')
p=R/'server.py';s=p.read_text(encoding='utf-8').replace("    quality: Literal['balanced','high']='balanced'", "    quality: Literal['balanced','high']='balanced'\n    music: Literal['halay','drum','off']='halay'\n    volume: int=Field(default=45,ge=0,le=100)")
s=s.replace('            engine.quality=settings.quality','            engine.quality=settings.quality\n            engine.music=settings.music\n            engine.volume=settings.volume')
needle="CONFIG_PATH=ROOT/'config.json'"
s=s.replace(needle,'''class AudioSettings(BaseModel):
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

'''+needle)
p.write_text(s,encoding='utf-8')
p=R/'app/scene.js';s=p.read_text(encoding='utf-8').replace("import {connect} from './transport.js';", "import {connect} from './transport.js';\nimport {HalayMusic} from './music.js';")
old="if(!preview)connect(s=>{state=s;offset=s.server_time-Date.now()/1000;},ok=>{document.querySelector('#connection').textContent=ok?'':'Bağlantı bekleniyor…'});"
new="""const unlock=document.querySelector('#audio-unlock');
const music=preview?null:new HalayMusic((status,error)=>{unlock.hidden=status!=='blocked'&&status!=='error';unlock.textContent=status==='error'?'Ses açılamadı · yeniden dene':'♫ Sesi aç';unlock.title=error||'Tarayıcıda müziği başlat';});
unlock.onclick=()=>music?.unlock();window.halayAudioDiagnostics=()=>music?.diagnostics()||{status:'preview-muted'};
if(!preview)connect(s=>{state=s;offset=s.server_time-Date.now()/1000;music.configure({music:s.music||'halay',volume:s.volume??45,bpm:s.bpm||112,fast:s.speed_until>s.server_time,running:Boolean(s.session?.running)})},ok=>{document.querySelector('#connection').textContent=ok?'':'Bağlantı bekleniyor…';if(!ok)music.stop()});
"""
assert old in s;s=s.replace(old,new)
s=s.replace(" const dt=Math.min((ms-last)/1000,.05);", " const dt=last?Math.max(0,(ms-last)/1000):0;")
s=s.replace(' phaseTime+=dt*(state.speed_until>now?1.45:1);', " music?.setTempo(state.bpm||112,state.speed_until>now);\n const audioBeats=music?.beats();if(audioBeats!=null)phaseTime=audioBeats*60/(state.bpm||112);else phaseTime+=dt*(state.speed_until>now?1.45:1);")
s=s.replace('window.halayDiagnostics=()=>stage.diagnostics();', 'window.halayDiagnostics=()=>({...stage.diagnostics(),audio:music?.diagnostics()||null});')
p.write_text(s,encoding='utf-8')
p=R/'app/overlay.html';s=p.read_text(encoding='utf-8').replace('</style>', '#audio-unlock{position:fixed;bottom:12%;left:50%;transform:translateX(-50%);padding:12px 22px;border:1px solid #d8b36b;border-radius:22px;background:#201c16ed;color:#ffe3a2;font:600 16px system-ui;cursor:pointer;z-index:9}#audio-unlock[hidden]{display:none}</style>')
s=s.replace('<div id="connection"></div>', '<div id="connection"></div><button id="audio-unlock" type="button" hidden>♫ Sesi aç</button>').replace('scene.js?v=4','scene.js?v=5')
p.write_text(s,encoding='utf-8')
print('Local loop player and dance/audio clock integrated.')
