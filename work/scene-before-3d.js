import {connect} from './transport.js';
const canvas=document.querySelector('canvas'),c=canvas.getContext('2d');
let state={users:[],events:[],bpm:112,scene:'halay'},offset=0;
const transparent=new URLSearchParams(location.search).has('transparent');
connect(s=>{state=s;offset=s.server_time-Date.now()/1000;},ok=>{document.querySelector('#connection').textContent=ok?'':'Bağlantı bekleniyor…'});
const registry=new Map();
export function registerScene(name,renderer){registry.set(name,renderer)}
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
function rug(x,y,rx,ry){
 ellipse(x,y,rx+6,ry+6,'#351d25');ellipse(x,y,rx,ry,'#982b37');
 c.save();c.translate(x,y);c.scale(1,ry/rx);for(let a=0;a<Math.PI*2;a+=Math.PI/5){c.save();c.rotate(a);polygon([[rx*.78,-6],[rx*.86,0],[rx*.78,6],[rx*.70,0]],'#e6bc60');c.restore()}c.restore();
 ellipse(x,y,rx*.19,ry*.19,'#ead4a6');ellipse(x,y,rx*.12,ry*.12,'#412b34');
}
function dancer(u,x,y,scale,t,phase,drummer=false){
 c.save();c.translate(x,y);c.scale(scale,scale);
 const beat=t*state.bpm/60*Math.PI*2,hop=Math.sin(beat+phase)*4,step=Math.sin(beat+phase)*7;
 ellipse(0,4,25,7,'#0005');c.translate(step*.4,hop);
 const girl=u.costume==='kız',animal=!['kız','erkek','oyuncak','ahşap','köşeli'].includes(u.costume);
 line([[-10,-10],[-11+step*.55,5]],'#19171d',9);line([[10,-10],[12-step*.55,5]],'#19171d',9);
 if(girl){polygon([[-13,-64],[13,-64],[27,-8],[-27,-8]],u.color);polygon([[-7,-61],[2,-61],[9,-12],[-4,-12]],'#ffffff0b');line([[-14,-38],[14,-38]],'#d5a743',4)}
 else {polygon([[-18,-65],[18,-65],[14,-25],[-14,-25]],'#c5a076');polygon([[-18,-66],[-5,-63],[-6,-32],[-16,-29]],u.color);polygon([[18,-66],[5,-63],[6,-32],[16,-29]],u.color);line([[-14,-29],[14,-29]],'#b89735',5)}
 const lift=Math.sin(beat+phase)*5;
 line([[-15,-61],[-28,-45+lift],[-39,-65+lift]],'#c59b72',6);
 line([[15,-61],[28,-45-lift],[39,-65-lift]],'#c59b72',6);
 ellipse(0,-76,12,15,'#caa17f');
 if(girl){polygon([[-13,-89],[10,-90],[17,-51],[5,-56],[4,-81],[-8,-81],[-9,-52],[-19,-47]],'#e1bd80');ellipse(0,-91,13,4,u.color)}
 else rounded(-13,-94,26,11,4,u.color);
 if(animal){text(({kedi:'🐱',tilki:'🦊',tavşan:'🐰',koyun:'🐑',penguen:'🐧',ayı:'🐻',ayi:'🐻'})[u.costume]||'🧸',0,-64,32)}
 if(drummer){ellipse(9,-34,23,15,'#e8c48b');rounded(-14,-34,46,26,3,'#8c2539');ellipse(9,-10,23,10,'#4b2430');line([[24,-50],[11+step,-34]],'#e9c889',4)}
 portrait(u,0,-113,19);
 const label=u.name.length>15?u.name.slice(0,14)+'…':u.name;
 rounded(-Math.max(35,label.length*3.9),-158,Math.max(70,label.length*7.8),23,10,drummer?'#be2446':'#14171bd9');
 text(label,0,-142,13);
 if(u.bubble&&u.bubble_until>t){const msg=u.bubble.length>22?u.bubble.slice(0,21)+'…':u.bubble;rounded(-91,-199,182,30,12,'#fff5e7');text(msg,0,-179,12,'#32232c')}
 c.restore();
}
function floor(t){
 if(transparent)return;
 const g=c.createLinearGradient(0,0,0,960);g.addColorStop(0,'#12111d');g.addColorStop(.35,'#614534');g.addColorStop(1,'#846149');c.fillStyle=g;c.fillRect(0,0,540,960);
 c.save();c.strokeStyle='#36271e45';c.lineWidth=1;
 for(let i=-7;i<10;i++){c.beginPath();c.moveTo(270+i*35,230);c.lineTo(270+i*210,960);c.stroke()}
 for(let y=270;y<960;y+=Math.max(14,(y-200)*.14)){c.beginPath();c.moveTo(0,y);c.lineTo(540,y);c.stroke()}c.restore();
 for(let i=0;i<15;i++){const x=(i*89+20)%540,y=35+(i*47)%220;ellipse(x,y,1.5,2,'#eac76b');}
 rug(80,730,95,52);rug(400,840,116,65);
 polygon([[175,610],[410,683],[352,725],[128,651]],'#6e1b2a');polygon([[128,651],[352,725],[352,739],[128,665]],'#b58b43');
 line([[145,664],[145,699]],'#4a2b20',7);line([[342,732],[342,765]],'#4a2b20',7);
}
registerScene('halay',(users,t)=>{
 const dancers=users.filter(u=>u.role!=='drummer');
 const items=dancers.map((u,i)=>{const a=i/Math.max(dancers.length,1)*Math.PI*2+t*.035;return {u,x:270+285*Math.cos(a),y:420+154*Math.sin(a),s:.72+.25*(Math.sin(a)+1),a}}).sort((a,b)=>a.y-b.y);
 for(const v of items)dancer(v.u,v.x,v.y,v.s,t,0);
 const drummer=users.find(u=>u.role==='drummer');if(drummer){text('🥁 Nağaracı',403,584,17,'#ffe38e');dancer(drummer,403,817,1.35,t,0,true)}
});
registerScene('orbit',(users,t)=>{users.forEach((u,i)=>{let a=i/users.length*Math.PI*2+t*.35;dancer(u,270+175*Math.cos(a),510+150*Math.sin(a),.85,t,i*.2)})});
function hud(t,users){
 rounded(14,15,286,180,14,'#101711e8');text('🏆 En iyi dansçılar',29,43,19,'#f7d66f','left');
 [...users].sort((a,b)=>b.points-a.points).slice(0,5).forEach((u,i)=>{text(String(i+1),29,72+i*25,12,'#b7bfb4','left');portrait(u,61,67+i*25,10);text(u.name.slice(0,17),80,72+i*25,13,'#fff','left');text(String(u.points),283,72+i*25,12,'#ead28b','right')});
 const fast=state.speed_until>t;
 c.strokeStyle='#ffffff20';c.lineWidth=9;c.beginPath();c.arc(482,67,43,.7,Math.PI*2.3);c.stroke();c.strokeStyle='#f8da5c';c.beginPath();c.arc(482,67,43,.7,fast?Math.PI*2.3:4.9);c.stroke();text('♪',482,56,24,'#f8da5c');text(fast?'Hızlı':'Normal',482,80,14);text(String(fast?Math.round(state.bpm*1.45):state.bpm)+' BPM',482,101,11,'#ecdca0');
 rounded(17,875,506,70,15,'#101610ed');text('Yorum yaz, halaya katıl!',270,901,21,'#f4d978');text(`“kız / erkek” ile kıyafet değiştir • ${state.like_threshold||300} beğeni ile katıl`,270,926,12,'#e3e4d1');
 if(!users.length){rounded(72,347,396,116,20,'#18151ce8');text('Meydan seni bekliyor',270,393,25,'#ffe4a1');text('Test panelinden demo katılımcıları ekle.',270,426,15,'#e5d7cd')}
 if(state.effect_until>t){for(let i=0;i<100;i++){c.fillStyle=['#ffd36a','#ff5386','#8bd7c3'][i%3];c.fillRect((i*71+t*40)%540,((t*140+i*47)%1000)-40,5,10)}}
}
let last=0,phaseTime=0;
function frame(ms){
 const dt=Math.min((ms-last)/1000,.05);last=ms;const now=Date.now()/1000+offset;
 phaseTime+=dt*(state.speed_until>now?1.45:1);
 const ratio=devicePixelRatio||1,w=canvas.clientWidth,h=canvas.clientHeight;
 if(canvas.width!==Math.round(w*ratio)||canvas.height!==Math.round(h*ratio)){canvas.width=Math.round(w*ratio);canvas.height=Math.round(h*ratio)}
 c.setTransform(1,0,0,1,0,0);c.clearRect(0,0,canvas.width,canvas.height);
 const s=Math.min(canvas.width/540,canvas.height/960);c.setTransform(s,0,0,s,(canvas.width-540*s)/2,(canvas.height-960*s)/2);
 const users=state.users.filter(u=>u.joined);floor(now);
 // Dance phase is accelerated independently from real-time bubble expiry.
 const visible=users.map(u=>({...u,bubble_until:u.bubble_until>now?phaseTime+1:0}));
 (registry.get(state.scene)||registry.get('halay'))(visible,phaseTime);hud(now,users);requestAnimationFrame(frame);
}requestAnimationFrame(frame);
