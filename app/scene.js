import {connect} from './transport.js';
import {HalayMusic} from './music.js';
import {createHalayStage} from './halay3d.js?v=10';
const canvas=document.querySelector('#stage'),c=canvas.getContext('2d');
let state={users:[],events:[],bpm:112,scene:'halay'},offset=0;
const params=new URLSearchParams(location.search),transparent=params.has('transparent'),preview=params.has('preview');
if(preview){state={...state,bpm:Number(params.get('bpm'))||112,scene:params.get('scene')||'halay',layout:params.get('layout')||'circle',theme:params.get('theme')||'night',quality:'balanced',users:Array.from({length:Math.min(60,Math.max(4,Number(params.get('capacity'))||48))},(_,i)=>({id:'preview'+i,name:['Elif','Melih','Dilan','Can','Nehir','Baran'][i%6],joined:true,points:0,color:['#7a1e2c','#1f1a1f','#154e40','#5a1b2a','#172d50'][i%5],costume:i%7?'kız':'erkek',role:i===0?'drummer':i===1?'zurnaci':'',bubble:''}))}}

let stage;
try{stage=createHalayStage(document.querySelector('#world'),{transparent})}
catch(err){document.querySelector('#connection').textContent='3B sahne açılamadı. Tarayıcıda grafik hızlandırmayı kontrol edin.';throw err}
const unlock=document.querySelector('#audio-unlock');
const music=preview?null:new HalayMusic((status,error)=>{unlock.hidden=status!=='blocked'&&status!=='error';unlock.textContent=status==='error'?'Ses açılamadı · yeniden dene':'♫ Sesi aç';unlock.title=error||'Tarayıcıda müziği başlat';});
unlock.onclick=()=>music?.unlock();window.halayAudioDiagnostics=()=>music?.diagnostics()||{status:'preview-muted'};
if(!preview)connect(s=>{state=s;offset=s.server_time-Date.now()/1000;music.configure({music:s.music||'halay',volume:s.volume??45,bpm:s.bpm||112,fast:s.speed_until>s.server_time,running:Boolean(s.session?.running)})},ok=>{document.querySelector('#connection').textContent=ok?'':'Bağlantı bekleniyor…';if(!ok)music.stop()});

const avatars=new Map();
function rounded(x,y,w,h,r,fill){c.fillStyle=fill;c.beginPath();c.roundRect(x,y,w,h,r);c.fill()}
function text(s,x,y,size=16,color='#fff',align='center',weight=700){c.fillStyle=color;c.font=`${weight} ${size}px "Segoe UI",sans-serif`;c.textAlign=align;c.fillText(s,x,y)}
function ellipse(x,y,rx,ry,color){c.fillStyle=color;c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fill()}
function line(points,color,width){c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.stroke()}
function polygon(points,color){c.fillStyle=color;c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fill()}
function portrait(u,x,y,r){
 ellipse(x,y,r+2.5,r+2.5,'#ffffff');ellipse(x,y,r,r,u.color);
 let img=avatars.get(u.avatar);
 if(u.avatar&&!img){img=new Image();img.referrerPolicy='no-referrer';img.src=u.avatar;avatars.set(u.avatar,img);if(avatars.size>100)avatars.delete(avatars.keys().next().value)}
 if(img?.complete&&img.naturalWidth){c.save();c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.clip();c.drawImage(img,x-r,y-r,r*2,r*2);c.restore()}
 else text(u.name.slice(0,2).toLocaleUpperCase('tr'),x,y+r*.31,r*.75);
}
function shadowText(s,x,y,size,color='#fff',align='center',weight=700){c.save();c.shadowColor='#000c';c.shadowBlur=4;c.shadowOffsetY=1;text(s,x,y,size,color,align,weight);c.restore()}
function bubble(msg,x,y){
 // Beyaz konuşma balonu, altında kuyruk.
 c.font='700 12px "Segoe UI",sans-serif';const w=Math.max(34,c.measureText(msg).width+18),h=24,bx=Math.max(4,Math.min(536-w,x-w/2));
 c.save();c.shadowColor='#0006';c.shadowBlur=6;rounded(bx,y-h,w,h,12,'#fffdf8');polygon([[x-6,y-1],[x+6,y-1],[x,y+7]],'#fffdf8');c.restore();text(msg,bx+w/2,y-8,12,'#20181c');
}
function hud(t,users){
 rounded(12,12,262,168,14,'#0d120fd9');text('🏆 En iyi dansçılar',26,40,18,'#f7d66f','left');
 [...users].sort((a,b)=>b.points-a.points).slice(0,5).forEach((u,i)=>{const y=66+i*24;if(i===0)text('👑',26,y+5,13,'#ffd76a','left');else text(String(i+1),30,y+5,12,'#cfd3c8','left');portrait(u,58,y,10);text(u.name.slice(0,16),76,y+5,13,'#fff','left');text(String(u.points),262,y+5,12,'#ead28b','right')});
 const fast=state.speed_until>t,bpm=fast?Math.round(state.bpm*1.45):state.bpm,arc=fast?'#f8da5c':'#8fdc6a';
 c.strokeStyle='#ffffff22';c.lineWidth=9;c.beginPath();c.arc(484,64,42,.7,Math.PI*2.3);c.stroke();c.strokeStyle=arc;c.beginPath();c.arc(484,64,42,.7,fast?Math.PI*2.3:3.6);c.stroke();
 shadowText('♪',484,52,22,arc);shadowText(fast?'Hızlı':'Orta',484,76,14);shadowText('♫ '+bpm,484,97,12,'#ecdca0');
 shadowText('Dansçını seç: oyuncak · ahşap · köşeli · ayı · tilki · kedi · tavşan · koyun · penguen yaz',270,862,11,'#f1e6c8');
 shadowText('“kız / qız” / “erkek / oğlan” yazınca kıyafet değişir',270,882,13,'#fff');
 const threshold=state.like_threshold||300,label=`💬 Yorum yaz, halaya katıl! · ya da ${threshold} beğeni`;
 c.font='700 17px "Segoe UI",sans-serif';const w=c.measureText(label).width+36;rounded(270-w/2,896,w,38,19,'#121512e6');text(label,270,921,17,'#f4d978');
 if(!users.length){rounded(72,347,396,116,20,'#18151ce8');text('Meydan seni bekliyor',270,393,25,'#ffe4a1');text('Yorumlarla halaya otomatik katıl.',270,426,15,'#e5d7cd')}
 if(state.effect_until>t){for(let i=0;i<100;i++){c.fillStyle=['#ffd36a','#ff5386','#8bd7c3'][i%3];c.fillRect((i*71+t*40)%540,((t*140+i*47)%1000)-40,5,10)}}
}

let last=0,phaseTime=0;
window.halayDiagnostics=()=>({...stage.diagnostics(),audio:music?.diagnostics()||null});
function frame(ms){
 const dt=last?Math.max(0,(ms-last)/1000):0;last=ms;const now=Date.now()/1000+offset;
 music?.setTempo(state.bpm||112,state.speed_until>now);
 const audioBeats=music?.beats();if(audioBeats!=null)phaseTime=audioBeats*60/(state.bpm||112);else phaseTime+=dt*(state.speed_until>now?1.45:1);
 const ratio=Math.min(devicePixelRatio||1,1.5),w=canvas.clientWidth,h=canvas.clientHeight;
 if(canvas.width!==Math.round(w*ratio)||canvas.height!==Math.round(h*ratio)){canvas.width=Math.round(w*ratio);canvas.height=Math.round(h*ratio)}
 c.setTransform(1,0,0,1,0,0);c.clearRect(0,0,canvas.width,canvas.height);
 const s=Math.min(canvas.width/540,canvas.height/960);c.setTransform(s,0,0,s,(canvas.width-540*s)/2,(canvas.height-960*s)/2);
 const users=state.users.filter(u=>u.joined),labels=stage.render(users,phaseTime,state.bpm,state.scene,{layout:state.layout,theme:state.theme,quality:state.quality});
 const spots=labels.spots;
 // Boş rol yerleri kürsünün üstünde yazılır; dolu olanlar kişinin isim etiketinin üstünde.
 if(spots){if(!spots.zurnaTaken)shadowText('🎺 Zurnacı',spots.zurna.x,spots.zurna.y,15,'#ffe9b0');if(!spots.drumTaken)shadowText('🥁 Nağaracı',spots.drum.x,spots.drum.y,15,'#ffe9b0')}
 const crowded=labels.length>16;
 for(const p of labels){
  const u=p.user,role=u.role==='drummer'||u.role==='zurnaci',r=role?24:Math.max(9,Math.round(15*p.scale)),size=role?14:Math.max(9,Math.round(11*p.scale));
  portrait(u,p.x,p.y,r);
  const limit=crowded&&!role?11:16,label=u.name.length>limit?u.name.slice(0,limit-1)+'…':u.name;
  if(role){c.font='700 14px "Segoe UI",sans-serif';const w=c.measureText(label).width+24;rounded(p.x-w/2,p.y-r-30,w,22,11,u.role==='drummer'?'#c0263f':'#8a5a17');text(label,p.x,p.y-r-14,14);shadowText(u.role==='drummer'?'🥁 Nağaracı':'🎺 Zurnacı',p.x,p.y-r-38,15,'#ffe9b0')}
  else shadowText(label,p.x,p.y-r-5,size);
  if(u.bubble&&u.bubble_until>now){const msg=u.bubble.length>20?u.bubble.slice(0,19)+'…':u.bubble;bubble(msg,p.x,p.y-r-(role?58:20)-size)}
 }
 hud(now,users);if(preview){rounded(170,823,200,30,12,'#171b24dc');text('ÖNİZLEME · örnek katılımcılar',270,843,12,'#ead28b')}requestAnimationFrame(frame);
}requestAnimationFrame(frame);
