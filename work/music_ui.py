from pathlib import Path
R=Path(r'D:\tiktokAnimasyon')
p=R/'app/setup.html';s=p.read_text(encoding='utf-8')
needle='<div class="divider"></div><details class="ruleeditor">'
s=s.replace(needle,'''<div class="divider"></div><section class="musicbox"><h2>Müzik</h2><label>Halay ritmi<select id="music"><option value="halay">Meydan Halayı · davul ve zurna</option><option value="drum">Yalnız davul</option><option value="off">Sessiz</option></select></label><label>Ses seviyesi <output id="volumevalue">45%</output><input id="volume" type="range" min="0" max="100" value="45"></label><button type="button" id="listenmusic">Ritmi dinle</button><p id="musicstatus" class="note" role="status">112 BPM’de hazırlanan özgün sentetik davul-zurna ezgisi. Dans hızı değiştiğinde ritim de birlikte değişir.</p><small>Açık oturumda ritim ve ses seviyesi değişiklikleri anında uygulanır. Önizleme penceresi sessizdir.</small></section><div class="divider"></div><details class="ruleeditor">''')
s=s.replace('Bu sürüm sessizdir; müziğini OBS’de ayrı Medya Kaynağı olarak ekleyebilirsin.', 'Müzik bu tarayıcı kaynağından gelir. Çift ses olmaması için ayrı test penceresinde müziği durdur; sesi yalnızca yayın kaynağından al.')
s=s.replace('setup.js?v=4','setup.js?v=5').replace('setup.css?v=4','setup.css?v=5')
p.write_text(s,encoding='utf-8')
p=R/'app/setup.css';s=p.read_text(encoding='utf-8')+'''\n.musicbox h2{margin-bottom:18px}.musicbox input[type=range]{padding:0;height:30px;accent-color:#e7c174;background:transparent;border:0}.musicbox output{float:right;color:#e6c47e;font-weight:700}.musicbox #listenmusic{min-width:150px}.musicbox #musicstatus{min-height:38px;line-height:1.7}.musicbox>small{line-height:1.7;margin-bottom:15px}\n''';p.write_text(s,encoding='utf-8')
p=R/'app/setup.js';s=p.read_text(encoding='utf-8').replace("import {connect} from './transport.js';", "import {connect} from './transport.js';\nimport {HalayMusic} from './music.js';")
s=s.replace("const names={arc:", "let auditioning=false,audioTimer;\nconst audition=new HalayMusic((status,error)=>{if(status==='error'){$('#musicstatus').textContent=error;auditioning=false}$('#listenmusic').textContent=auditioning?'Dinlemeyi durdur':'Ritmi dinle'});\nconst names={arc:")
s=s.replace("username:$('#username').value}", "username:$('#username').value,music:$('#music').value,volume:Number($('#volume').value)}")
s=s.replace("['mode','username','capacity','theme','quality']", "['mode','username','capacity','theme','quality','music','volume']")
s=s.replace("$('#mode').onchange();preview()", "$('#mode').onchange();musicUI();preview()")
s=s.replace("scene:s.scene})", "scene:s.scene,bpm:Number($('#bpm').value)||112})")
s=s.replace("running=t.running;$('#status')", "running=t.running;musicUI();$('#status')")
s=s.replace("$('#start').disabled=true;try{", "$('#start').disabled=true;audition.stop();auditioning=false;try{")
s+=r'''
function musicUI(){$('#volumevalue').textContent=$('#volume').value+'%';$('#listenmusic').disabled=running||$('#music').value==='off';if(running)$('#musicstatus').textContent='Yayında · ses değişiklikleri açık sahneye uygulanır.'}
function changedAudio(){musicUI();if(auditioning)audition.configure({music:$('#music').value,volume:Number($('#volume').value),bpm:Number($('#bpm').value)||112,running:true});clearTimeout(audioTimer);if(running)audioTimer=setTimeout(()=>call('/api/audio',{music:$('#music').value,volume:Number($('#volume').value)}).catch(error=>{$('#musicstatus').textContent=error.message}),180)}
$('#music').onchange=changedAudio;$('#volume').oninput=changedAudio;
$('#bpm').addEventListener('input',()=>{preview();if(auditioning)audition.setTempo(Number($('#bpm').value)||112,false)});
$('#listenmusic').onclick=async()=>{if(auditioning){audition.stop();auditioning=false;$('#listenmusic').textContent='Ritmi dinle';$('#musicstatus').textContent='Dinleme durduruldu.';return}auditioning=true;audition.configure({music:$('#music').value,volume:Number($('#volume').value),bpm:Number($('#bpm').value)||112,running:true,fast:false});await audition.unlock();$('#musicstatus').textContent='Dinleniyor · adımlara uygun davul-zurna ritmi.'};
window.addEventListener('pagehide',()=>audition.stop());window.studioAudioDiagnostics=()=>audition.diagnostics();
'''
p.write_text(s,encoding='utf-8')
p=R/'app/scene.js';s=p.read_text(encoding='utf-8').replace("state={...state,scene:params.get('scene')", "state={...state,bpm:Number(params.get('bpm'))||112,scene:params.get('scene')")
p.write_text(s,encoding='utf-8')
print('Music selection, audition and live volume controls added.')
