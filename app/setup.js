import {connect} from './transport.js';
import {HalayMusic} from './music.js';
const $=s=>document.querySelector(s);let running=false,initial=true,previewTimer;
let auditioning=false,audioTimer;
const audition=new HalayMusic((status,error)=>{if(status==='error'){$('#musicstatus').textContent=error;auditioning=false}$('#listenmusic').textContent=auditioning?'Dinlemeyi durdur':'Ritmi dinle'});
const names={circle:'Halka',arc:'Yay',wide:'Geniş yay',line:'Sıra'};
function settings(){return {mode:$('#mode').value,scene:document.querySelector('input[name="scene"]:checked').value,layout:document.querySelector('input[name="layout"]:checked').value,theme:$('#theme').value,quality:$('#quality').value,capacity:Number($('#capacity').value),username:$('#username').value,music:$('#music').value,volume:Number($('#volume').value)}}
function preview(){const s=settings();$('#previewcaption').textContent=`${names[s.layout]} · ${s.capacity} kişi`;document.querySelectorAll('[data-capacity]').forEach(b=>b.classList.toggle('active',Number(b.dataset.capacity)===s.capacity));clearTimeout(previewTimer);previewTimer=setTimeout(()=>{if(s.capacity>=4&&s.capacity<=120)$('#preview').src='/overlay?preview=1&'+new URLSearchParams({layout:s.layout,theme:s.theme,capacity:s.capacity,scene:s.scene,bpm:Number($('#bpm').value)||112})},250)}
function fill(s){for(const id of ['mode','username','capacity','theme','quality','music','volume'])if(s[id]!==undefined)$('#'+id).value=s[id];for(const key of ['scene','layout']){const radio=document.querySelector(`input[name="${key}"][value="${s[key]}"]`);if(radio)radio.checked=true}$('#mode').onchange();musicUI();preview()}
$('#mode').onchange=()=>{const live=$('#mode').value==='live';$('#userrow').hidden=!live;$('#liveinfo').hidden=!live;$('#username').required=live};
for(const input of document.querySelectorAll('[name="layout"],[name="scene"],#capacity,#theme'))input.addEventListener('input',preview);
for(const button of document.querySelectorAll('[data-capacity]'))button.onclick=()=>{$('#capacity').value=button.dataset.capacity;preview()};
async function call(path,payload){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await r.json();if(!r.ok)throw Error(typeof data.detail==='string'?data.detail:'Ayarları kontrol edin.');return data}

connect(s=>{const t=s.session||{};running=t.running;musicUI();$('#status').textContent=`${s.source} · ${s.users.filter(u=>u.joined).length}/${s.ring_capacity} kişi · ${s.queued||0} sırada`;$('#stop').hidden=!running;$('#start').textContent=running?'Yeni oturum başlat':'Başlat · sahneyi aç';if(initial&&running)fill(t);initial=false},ok=>{$('#connection').textContent=ok?'Yerel sunucu bağlı':'Yeniden bağlanıyor…'});
$('#setupform').onsubmit=async e=>{e.preventDefault();if(running&&!confirm('Yeni oturum mevcut katılımcıları ve puanları sıfırlasın mı?'))return;$('#start').disabled=true;audition.stop();auditioning=false;try{const s=settings(),rules=readRules();await call('/api/rules',rules);await call('/api/settings',s);await call('/api/session/start',s);location.href='/overlay'}catch(err){$('#status').textContent=err.message;$('#start').disabled=false}};
$('#stop').onclick=async()=>{try{await call('/api/session/stop',{});$('#status').textContent='Oturum durduruldu.'}catch(err){$('#status').textContent=err.message}};
$('#copyobs').onclick=async()=>{try{await navigator.clipboard.writeText($('#obsurl').value);$('#copyobs').textContent='Kopyalandı'}catch{$('#obsurl').focus();$('#obsurl').select();$('#copyobs').textContent='Ctrl+C ile kopyala'}};

let savedProfiles=[];
function ruleRow(rule={name:'',gift_id:0,action:'join',points:1}){
 const row=document.createElement('div');row.className='giftrule';
 const grid=document.createElement('div');grid.className='rulegrid';row.append(grid);
 for(const [field,label,type] of [['name','Hediye adı','text'],['gift_id','Hediye kimliği · isteğe bağlı','number'],['action','Ne yapsın?','select'],['points','Adet başına puan','number']]){
  const wrapper=document.createElement('label');wrapper.textContent=label;let input;
  if(type==='select'){input=document.createElement('select');for(const [value,title] of [['join','Halaya katıl'],['speed','Hızlandır'],['drummer','Nağaracı olsun'],['zurna','Zurnacı olsun'],['confetti','Konfeti göster']])input.add(new Option(title,value))}
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

function musicUI(){$('#volumevalue').textContent=$('#volume').value+'%';$('#listenmusic').disabled=running||$('#music').value==='off';if(running)$('#musicstatus').textContent='Yayında · ses değişiklikleri açık sahneye uygulanır.'}
function changedAudio(){musicUI();if(auditioning)audition.configure({music:$('#music').value,volume:Number($('#volume').value),bpm:Number($('#bpm').value)||112,running:true});clearTimeout(audioTimer);if(running)audioTimer=setTimeout(()=>call('/api/audio',{music:$('#music').value,volume:Number($('#volume').value)}).catch(error=>{$('#musicstatus').textContent=error.message}),180)}
$('#music').onchange=changedAudio;$('#volume').oninput=changedAudio;
$('#bpm').addEventListener('input',()=>{preview();if(auditioning)audition.setTempo(Number($('#bpm').value)||112,false)});
$('#listenmusic').onclick=async()=>{if(auditioning){audition.stop();auditioning=false;$('#listenmusic').textContent='Ritmi dinle';$('#musicstatus').textContent='Dinleme durduruldu.';return}auditioning=true;audition.configure({music:$('#music').value,volume:Number($('#volume').value),bpm:Number($('#bpm').value)||112,running:true,fast:false});await audition.unlock();$('#musicstatus').textContent='Dinleniyor · adımlara uygun davul-zurna ritmi.'};
window.addEventListener('pagehide',()=>audition.stop());window.studioAudioDiagnostics=()=>audition.diagnostics();
