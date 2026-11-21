import {connect} from './transport.js';
import {HalayMusic} from './music.js';
import {createHalayStage} from './halay3d.js';
const canvas=document.querySelector('#stage'),c=canvas.getContext('2d');
let state={users:[],events:[],bpm:112,scene:'halay'},offset=0;
const params=new URLSearchParams(location.search),transparent=params.has('transparent'),preview=params.has('preview');
if(preview){state={...state,bpm:Number(params.get('bpm'))||112,scene:params.get('scene')||'halay',layout:params.get('layout')||'arc',theme:params.get('theme')||'night',quality:'balanced',users:Array.from({length:Math.min(60,Math.max(4,Number(params.get('capacity'))||12))},(_,i)=>({id:'preview'+i,name:['Elif','Melih','Dilan','Can','Nehir','Baran'][i%6],joined:true,points:0,color:['#6f1e35','#214d3c','#202d4b'][i%3],costume:i%3?'kız':'erkek',role:i===0?'drummer':'',bubble:''}))}}

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
 ellipse(x,y,r+2,r+2,'#f6eed6');ellipse(x,y,r,r,u.color);
 let img=avatars.get(u.avatar);
 if(u.avatar&&!img){img=new Image();img.referrerPolicy='no-referrer';img.src=u.avatar;avatars.set(u.avatar,img);if(avatars.size>100)avatars.delete(avatars.keys().next().value)}
 if(img?.complete&&img.naturalWidth){c.save();c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.clip();c.drawImage(img,x-r,y-r,r*2,r*2);c.restore()}
 else text(u.name.slice(0,2).toLocaleUpperCase('tr'),x,y+r*.31,r*.75);
}
function hud(t,users){
 rounded(14,15,286,180,14,'#101711e8');text('🏆 En iyi dansçılar',29,43,19,'#f7d66f','left');
 [...users].sort((a,b)=>b.points-a.points).slice(0,5).forEach((u,i)=>{text(String(i+1),29,72+i*25,12,'#b7bfb4','left');portrait(u,61,67+i*25,10);text(u.name.slice(0,17),80,72+i*25,13,'#fff','left');text(String(u.points),283,72+i*25,12,'#ead28b','right')});
 const fast=state.speed_until>t;
 c.strokeStyle='#ffffff20';c.lineWidth=9;c.beginPath();c.arc(482,67,43,.7,Math.PI*2.3);c.stroke();c.strokeStyle='#f8da5c';c.beginPath();c.arc(482,67,43,.7,fast?Math.PI*2.3:4.9);c.stroke();text('♪',482,56,24,'#f8da5c');text(fast?'Hızlı':'Normal',482,80,14);text(String(fast?Math.round(state.bpm*1.45):state.bpm)+' BPM',482,101,11,'#ecdca0');
 rounded(17,875,506,70,15,'#101610ed');text('Yorum yaz, halaya katıl!',270,901,21,'#f4d978');text(`“kız / erkek” ile kıyafet değiştir • ${state.like_threshold||300} beğeni ile katıl`,270,926,12,'#e3e4d1');
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
 const crowded=labels.length>14;let labelIndex=0;
 for(const p of labels){
  const u=p.user,r=Math.max(10,19*p.scale),drummer=u.role==='drummer';
  if(drummer)text('🥁 Nağaracı',p.x,p.y-59,16,'#ffe38e');
  portrait(u,p.x,p.y,r);
  const limit=crowded?9:15,label=u.name.length>limit?u.name.slice(0,limit-1)+'…':u.name,width=Math.max(crowded?40:54,label.length*(crowded?6:7)),labelX=Math.max(width*.5+4,Math.min(536-width*.5,p.x)),labelY=p.y-r-26-(crowded&&!drummer?(labelIndex++%2)*20:0);
  rounded(labelX-width/2,labelY,width,20,9,drummer?'#b52542':'#111319e8');text(label,labelX,labelY+14,crowded?10:12);
  if(u.bubble&&u.bubble_until>now){const msg=u.bubble.length>22?u.bubble.slice(0,21)+'…':u.bubble;rounded(p.x-84,p.y-r-61,168,27,10,'#fff4e5');text(msg,p.x,p.y-r-43,12,'#30212a')}
 }
 hud(now,users);if(preview){rounded(170,823,200,30,12,'#171b24dc');text('ÖNİZLEME · örnek katılımcılar',270,843,12,'#ead28b')}requestAnimationFrame(frame);
}requestAnimationFrame(frame);
