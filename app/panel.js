import {connect,send} from './transport.js';
const $=s=>document.querySelector(s),msg=$('#message');
async function emit(e){try{await send(e);msg.textContent='Sahne güncellendi.'}catch(err){msg.textContent=err.message}}
connect(s=>{
 $('#source').textContent=s.source;
 const joined=s.users.filter(u=>u.joined);$('#summary').textContent=`${joined.length}/${s.ring_capacity} dansçı · ${s.queued||0} sırada · ${s.scene==='halay'?'Halay meydanı':'Çember dansı'}`;$('#total').textContent=`${s.users.length} kişi`;
 $('#scene').value=s.scene;
 const selected=$('#gift').value;
 $('#gift').replaceChildren(...s.gift_names.map(name=>new Option(name,name)));if(s.gift_names.includes(selected))$('#gift').value=selected;
 $('#people').replaceChildren(...s.users.map(u=>{const chip=document.createElement('div');chip.className='person';const label=document.createElement('span');label.textContent=`${u.name} · ${u.points} puan${u.joined?'':u.queued?' · sırada':' · beğeni bekliyor'}`;const b=document.createElement('button');b.type='button';b.textContent='×';b.setAttribute('aria-label',u.name+' kişisini çıkar');b.onclick=()=>emit({type:'control',text:'remove',user_id:u.id});chip.append(label,b);return chip}));
 $('#log').replaceChildren(...s.events.slice().reverse().slice(0,15).map(e=>{const el=document.createElement('div');el.className='entry';const b=document.createElement('b');b.textContent=e.name;el.append(b,document.createTextNode(` · ${e.type} · ${e.text} ${e.count>1?'×'+e.count:''}`));return el}));
},ok=>{$('#connection').textContent=ok?'Bağlı · yerel':'Yeniden bağlanıyor…';$('#connection').style.color=ok?'#a6d7b0':'#e89a9a'});
$('#type').onchange=()=>{const type=$('#type').value;$('#commentrow').hidden=type!=='comment';$('#giftrow').hidden=type!=='gift';$('#countrow').hidden=type==='comment';$('#count').value=type==='like'?300:1};
$('#eventform').onsubmit=async e=>{e.preventDefault();const button=e.submitter;button.disabled=true;await emit({type:$('#type').value,user_id:$('#uid').value,name:$('#name').value,text:$('#comment').value,gift:$('#gift').value,count:Number($('#count').value),event_id:crypto.randomUUID()});button.disabled=false};
$('#demo').onclick=()=>emit({type:'control',text:'demo'});$('#speed').onclick=()=>emit({type:'control',text:'speed'});
$('#reset').onclick=()=>{if(confirm('Tüm katılımcılar ve puanlar silinsin mi?'))emit({type:'control',text:'reset'})};
$('#scene').onchange=()=>emit({type:'control',text:$('#scene').value});
