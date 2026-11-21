import * as T from './vendor/three.module.min.js';
const Y=new T.Vector3(0,1,0),v=(x=0,y=0,z=0)=>new T.Vector3(x,y,z);
const geometries=new Map(),materials=new Map();
function geo(key,make){if(!geometries.has(key))geometries.set(key,make());return geometries.get(key)}
function mat(color,roughness=.8,metalness=0){const key=color+':'+roughness+':'+metalness;if(!materials.has(key))materials.set(key,new T.MeshStandardMaterial({color,roughness,metalness}));return materials.get(key)}
const sphere=geo('sphere',()=>new T.SphereGeometry(1,16,12)),cylinder=geo('cylinder',()=>new T.CylinderGeometry(1,1,1,12)),box=geo('box',()=>new T.BoxGeometry(1,1,1));
function mesh(g,m,parent,x,y,z,sx=1,sy=sx,sz=sx){const o=new T.Mesh(g,m);o.position.set(x,y,z);o.scale.set(sx,sy,sz);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
function ell(parent,m,x,y,z,sx,sy,sz){return mesh(sphere,m,parent,x,y,z,sx,sy,sz)}
function block(parent,m,x,y,z,sx,sy,sz){return mesh(box,m,parent,x,y,z,sx,sy,sz)}
function bone(parent,m,radius){const o=mesh(cylinder,m,parent,0,0,0,radius,1,radius);o.userData.radius=radius;return o}
function segment(o,a,b){o.position.copy(a).add(b).multiplyScalar(.5);o.scale.y=a.distanceTo(b);o.quaternion.setFromUnitVectors(Y,b.clone().sub(a).normalize())}
function pleatedSkirt(){
 return geo('skirt',()=>{const points=[];for(let i=0;i<8;i++){const q=i/7;points.push(new T.Vector2(.16+q*.18,.94-q*.78))}const g=new T.LatheGeometry(points.reverse(),48);const pos=g.attributes.position;for(let i=0;i<pos.count;i++){const y=pos.getY(i),a=Math.atan2(pos.getX(i),pos.getZ(i)),fold=1+Math.sin(a*16)*.055*(1-y);pos.setX(i,pos.getX(i)*fold);pos.setZ(i,pos.getZ(i)*fold)}g.computeVertexNormals();return g});
}
function fabric(color){
 const key='fabric:'+color;if(materials.has(key))return materials.get(key);
 const cn=document.createElement('canvas');cn.width=cn.height=256;const ctx=cn.getContext('2d');
 ctx.fillStyle=color;ctx.fillRect(0,0,256,256);
 for(let x=0;x<256;x+=2){ctx.fillStyle=x%4?'#ffffff06':'#0000000c';ctx.fillRect(x,0,1,256)}
 for(const x of [18,36,220,238]){ctx.strokeStyle='#d6b467';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,256);ctx.stroke()}
 for(let y=15;y<256;y+=32)for(const x of [27,229]){ctx.strokeStyle='#e6c884';ctx.beginPath();ctx.moveTo(x,y-6);ctx.lineTo(x+5,y);ctx.lineTo(x,y+6);ctx.lineTo(x-5,y);ctx.closePath();ctx.stroke()}
 const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;const material=new T.MeshStandardMaterial({map:tex,roughness:.95});materials.set(key,material);return material;
}
function makeActor(user){
 const root=new T.Group(),body=new T.Group();root.add(body);
 const hash=[...user.id].reduce((a,ch)=>a+ch.charCodeAt(0),0),skin=mat(['#c69a77','#d7af8c','#b78564','#e0b99a'][hash%4]),cloth=fabric(user.color||'#6d2333'),cream=mat('#d8c49e'),gold=mat('#b79040',.45,.3),dark=mat('#18171a'),hair=mat(['#211814','#3c251b','#171518'][hash%3]);
 const female=user.costume!=='erkek',shirt=mat(female?'#a98661':'#cfb998');
 // Rounded torso and fitted folk waistcoat, with metallic belt and embroidery.
 mesh(geo('torso',()=>new T.CylinderGeometry(.21,.16,.48,20)),shirt,body,0,1.20,0,1,1,.66);
 ell(body,shirt,0,1.42,0,.225,.10,.135);
 if(female){mesh(pleatedSkirt(),cloth,body,0,0,0);mesh(geo('hem',()=>new T.CylinderGeometry(.328,.338,.025,48)),gold,body,0,.185,0);block(body,cloth,-.105,1.25,.104,.14,.39,.045);block(body,cloth,.105,1.25,.104,.14,.39,.045)}
 else {mesh(geo('hips',()=>new T.SphereGeometry(1,16,10)),cloth,body,0,.92,0,.21,.20,.13);block(body,cloth,-.12,1.24,.11,.15,.41,.055);block(body,cloth,.12,1.24,.11,.15,.41,.055)}
 mesh(geo('belt',()=>new T.CylinderGeometry(.181,.184,.065,24)),gold,body,0,.99,0,1,1,.78);
 for(let i=0;i<6;i++){ell(body,gold,-.055,1.08+i*.055,.145,.009,.013,.006);ell(body,gold,.055,1.08+i*.055,.145,.009,.013,.006)}
 // Neck, head and facial detail remain visible beneath the floating profile ring.
 ell(body,skin,0,1.51,0,.064,.085,.061);ell(body,skin,0,1.67,0,.104,.142,.096);
 ell(body,skin,-.105,1.67,0,.025,.042,.02);ell(body,skin,.105,1.67,0,.025,.042,.02);
 ell(body,hair,0,1.74,-.018,.109,.088,.091);
 ell(body,skin,0,1.656,.098,.024,.034,.035);
 for(const x of [-.039,.039]){ell(body,mat('#f1e7d9'),x,1.694,.085,.022,.012,.012);ell(body,dark,x,1.694,.096,.008,.009,.005)}
 ell(body,mat('#8a5547'),0,1.61,.085,.028,.007,.008);
 if(female){
   mesh(geo('cap',()=>new T.SphereGeometry(.115,20,12,0,Math.PI*2,0,Math.PI*.53)),cloth,body,0,1.72,-.006);
   mesh(geo('headband',()=>new T.TorusGeometry(.108,.012,6,32)),gold,body,0,1.741,-.006).rotation.x=Math.PI/2;
   const veil=mesh(geo('veil',()=>new T.CylinderGeometry(.085,.145,.37,18,1,true,0,Math.PI)),cream,body,0,1.54,-.06);veil.rotation.y=Math.PI/2;
   ell(body,gold,-.105,1.615,.01,.014,.026,.012);ell(body,gold,.105,1.615,.01,.014,.026,.012);
 }else{mesh(geo('hat',()=>new T.CylinderGeometry(.111,.113,.09,20)),cloth,body,0,1.805,-.005);mesh(geo('hatband',()=>new T.CylinderGeometry(.115,.115,.019,20)),dark,body,0,1.77,-.005)}
 const legs=[];for(const side of [-1,1]){
  const upper=bone(body,female?skin:cloth,female?.053:.08),lower=bone(body,female?skin:cloth,.052),shoe=ell(body,dark,side*.11,.065,.065,.073,.058,.147);
  legs.push({side,upper,lower,shoe});
 }
 const arms=[];for(const side of [-1,1]){
  const upper=bone(body,cream,.063),lower=bone(body,skin,.047),elbow=ell(body,cream,0,0,0,.064,.064,.064),hand=ell(body,skin,0,0,0,.055,.046,.04);
  arms.push({side,upper,lower,elbow,hand});
 }
 let drum=null;
 if(user.role==='drummer'){
  drum=new T.Group();body.add(drum);drum.position.set(0,.88,.34);drum.rotation.x=Math.PI*.09;
  mesh(geo('drum',()=>new T.CylinderGeometry(.27,.27,.31,32)),cloth,drum,0,0,0);
  for(const h of [-.16,.16])mesh(geo('drumskin',()=>new T.CylinderGeometry(.285,.285,.025,32)),cream,drum,0,h,0);
  for(let a=0;a<Math.PI*2;a+=Math.PI/6){const cord=bone(drum,gold,.008);segment(cord,v(Math.cos(a)*.277,-.15,Math.sin(a)*.277),v(Math.cos(a+.26)*.277,.15,Math.sin(a+.26)*.277))}
 }
 let zurna=null;
 if(user.role==='zurnaci'){
  // Zurna: ağızdan öne-aşağı uzanan, ucu genişleyen nefesli çalgı.
  zurna={mouth:v(0,1.62,.12),bell:v(0,1.24,.5)};
  const pipe=mesh(geo('zurna',()=>new T.CylinderGeometry(.016,.05,1,14)),mat('#7a4a25',.55),body,0,0,0);segment(pipe,zurna.bell,zurna.mouth);
  const lip=mesh(geo('zurnalip',()=>new T.TorusGeometry(.052,.01,6,20)),gold,body,0,0,0);lip.position.copy(zurna.bell);lip.quaternion.copy(pipe.quaternion);lip.rotateX(Math.PI/2);
 }
 const flag=new T.Mesh(new T.PlaneGeometry(.22,.28,6,8),new T.MeshStandardMaterial({color:'#b82536',roughness:1,side:T.DoubleSide}));flag.visible=false;body.add(flag);
 return {root,body,user,legs,arms,drum,zurna,flag,phase:hash*.001};
}
function updateLegs(a,time,beat,scale){
 const cycle=time*beat/60*Math.PI*2,step=Math.sin(cycle),lift=Math.max(0,Math.sin(cycle*2))*.035;
 a.body.position.y=lift;
 a.body.rotation.z=Math.sin(cycle)*.025;
 for(const leg of a.legs){const s=leg.side,phase=cycle+(s===1?Math.PI:0);const ankle=v(s*.105+Math.sin(phase)*.04,.09+Math.max(0,Math.sin(phase))*.065,Math.cos(phase)*.065),hip=v(s*.105,.92,0),knee=hip.clone().lerp(ankle,.52);knee.z+=.055+Math.max(0,Math.sin(phase))*.07;segment(leg.upper,hip,knee);segment(leg.lower,knee,ankle);leg.shoe.position.copy(ankle).add(v(0,-.025,.055));leg.shoe.rotation.x=-Math.max(0,Math.sin(phase))*.14}
 a.root.updateMatrixWorld(true);
}
function solveArm(a,arm,target,time,bpm){
 // The target is shared by adjacent dancers: the two wrist endpoints are identical.
 const shoulder=v(arm.side*.205,1.41,0),hand=a.body.worldToLocal(target.clone());
 const mid=shoulder.clone().lerp(hand,.5),distance=shoulder.distanceTo(hand),length=.32;
 const bend=Math.sqrt(Math.max(.001,length*length-distance*distance*.25));
 mid.y-=bend;mid.z+=.045;
 segment(arm.upper,shoulder,mid);segment(arm.lower,mid,hand);arm.elbow.position.copy(mid);arm.hand.position.copy(hand);
}
function floorTexture(){const cn=document.createElement('canvas');cn.width=cn.height=1024;const ctx=cn.getContext('2d');ctx.fillStyle='#715844';ctx.fillRect(0,0,1024,1024);for(let row=0;row<8;row++)for(let col=-1;col<8;col++){let x=col*150+(row%2)*75,y=row*130;ctx.fillStyle=`hsl(28 22% ${33+((row*71+col*13)%9)}%)`;ctx.fillRect(x+2,y+2,146,126);ctx.strokeStyle='#503d30';ctx.strokeRect(x,y,150,130);for(let i=0;i<80;i++){ctx.fillStyle=i%2?'#ffffff08':'#0000000c';ctx.fillRect(x+(i*37)%148,y+(i*53)%127,2,1)}}const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(3,3);return tex}
function rugTexture(){const cn=document.createElement('canvas');cn.width=cn.height=512;const ctx=cn.getContext('2d');ctx.fillStyle='#6d1527';ctx.fillRect(0,0,512,512);for(let i=0;i<12;i++){ctx.strokeStyle=i%2?'#c49b50':'#291c2c';ctx.lineWidth=3;ctx.strokeRect(8+i*3,8+i*3,496-i*6,496-i*6)}for(let x=85;x<500;x+=85)for(let y=85;y<500;y+=85){ctx.fillStyle=(x+y)%2?'#c6a05f':'#e5c78d';ctx.beginPath();ctx.moveTo(x,y-22);ctx.lineTo(x+22,y);ctx.lineTo(x,y+22);ctx.lineTo(x-22,y);ctx.fill();ctx.fillStyle='#1b2232';ctx.fillRect(x-5,y-5,10,10)}const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;return tex}
function roundRugTexture(){
 // Yuvarlak kilim: lacivert kenar şeridi, altın motifler ve ortada üç halka.
 const cn=document.createElement('canvas');cn.width=cn.height=512;const ctx=cn.getContext('2d'),c=256;
 ctx.fillStyle='#8f1b27';ctx.fillRect(0,0,512,512);
 ctx.fillStyle='#1c1a2b';ctx.beginPath();ctx.arc(c,c,256,0,Math.PI*2);ctx.arc(c,c,196,0,Math.PI*2,true);ctx.fill();
 for(let i=0;i<28;i++){const a=i/28*Math.PI*2,x=c+Math.cos(a)*226,y=c+Math.sin(a)*226;ctx.save();ctx.translate(x,y);ctx.rotate(a+Math.PI/4);ctx.fillStyle=i%2?'#d9b45c':'#9b2130';ctx.fillRect(-11,-11,22,22);ctx.restore()}
 ctx.strokeStyle='#d6ae58';ctx.lineWidth=6;ctx.beginPath();ctx.arc(c,c,192,0,Math.PI*2);ctx.stroke();
 ctx.fillStyle='#a3212f';ctx.beginPath();ctx.arc(c,c,186,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle='#5c0f1a';ctx.lineWidth=2;for(let r=40;r<186;r+=24){ctx.beginPath();ctx.arc(c,c,r,0,Math.PI*2);ctx.stroke()}
 ctx.lineWidth=13;for(const [dx,color] of [[-78,'#d9b45c'],[0,'#f0ece2'],[78,'#d9b45c']]){ctx.strokeStyle=color;ctx.beginPath();ctx.arc(c+dx,c,27,0,Math.PI*2);ctx.stroke()}
 const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;return tex;
}
export function createHalayStage(canvas,{transparent=false}={}){
 const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance',preserveDrawingBuffer:true});
 renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
 const scene=new T.Scene();if(!transparent){scene.background=new T.Color('#13101a');scene.fog=new T.Fog('#13101a',17,38)}
 const camera=new T.PerspectiveCamera(49,540/960,.1,80);camera.position.set(0,7.9,12.7);camera.lookAt(0,.25,0);
 scene.add(new T.HemisphereLight('#e4d5be','#4d3029',2));
 const key=new T.DirectionalLight('#ffe1ae',3.1);key.position.set(-3,8,5);key.castShadow=true;key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-9,right:9,top:9,bottom:-9,near:.5,far:30});key.shadow.normalBias=.025;key.shadow.bias=-.0003;scene.add(key);scene.add(key.target);
 const rim=new T.DirectionalLight('#b8c3ee',1.5);rim.position.set(3,4,-6);scene.add(rim);
 const decor=new T.Group();scene.add(decor);decor.visible=!transparent;
 const floor=floorTexture();floor.repeat.set(5,5);
 const ground=new T.Mesh(new T.PlaneGeometry(60,60),new T.MeshStandardMaterial({map:floor,roughness:.98}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;decor.add(ground);
 // Dikdörtgen kilimler yay/sıra düzenlerinde, yuvarlak kürsüler halka düzeninde kullanılır.
 const rugmat=new T.MeshStandardMaterial({map:rugTexture(),roughness:1}),squareRugs=new T.Group();decor.add(squareRugs);
 for(const [x,z,w,h] of [[-1.7,2.9,1.6,1.2],[1.4,3.7,2,1.5]]){const rug=new T.Mesh(new T.PlaneGeometry(w,h),rugmat);rug.rotation.x=-Math.PI/2;rug.position.set(x,.018,z);rug.receiveShadow=true;squareRugs.add(rug)}
 const roundmat=new T.MeshStandardMaterial({map:roundRugTexture(),roughness:1}),roundRugs={};
 for(const name of ['zurna','drum']){const g=new T.Group();decor.add(g);mesh(geo('dais',()=>new T.CylinderGeometry(.98,1.04,.1,48)),mat('#4a1119'),g,0,.05,0);const top=new T.Mesh(geo('daistop',()=>new T.CircleGeometry(.96,48)),roundmat);top.rotation.x=-Math.PI/2;top.position.y=.102;top.receiveShadow=true;g.add(top);roundRugs[name]=g}
 const bench=new T.Group();decor.add(bench);
 const benchmat=mat('#711c2a');block(bench,benchmat,0,.27,0,2.5,.21,.8);block(bench,mat('#c39a51',.45,.2),0,.16,0,2.54,.035,.84);for(const x of [-1.05,1.05])for(const z of [-.28,.28])block(bench,mat('#472f22'),x,.09,z,.07,.2,.07);
 for(let i=0;i<5;i++){const cushion=block(bench,fabric('#792537'),-.98+i*.49,.40,0,.46,.10,.7);cushion.rotation.z=(i%2?1:-1)*.025}

 // Köy meydanı arka planı, fenerler ve ip ışıkları; halka büyüdükçe geriye kayar.
 const backdrop=new T.Group();decor.add(backdrop);
 for(let i=0;i<23;i++){const bulb=new T.Mesh(sphere,new T.MeshBasicMaterial({color:'#ffdaa1'}));bulb.scale.setScalar(.03);bulb.position.set((i-11)*.75,3.3+Math.cos(i*.5)*.18,-4.6);backdrop.add(bulb)}
 const stone=mat('#3f3933');block(backdrop,stone,0,.48,-5.3,22,.96,.35);
 for(const x of [-7.3,-5.5,-3.7,3.7,5.5,7.3]){block(backdrop,mat('#5b4b3c'),x,1.4,-5.2,.34,2.8,.44);block(backdrop,mat('#a38459'),x,2.82,-5.2,.52,.12,.58)}
 const glowCanvas=document.createElement('canvas');glowCanvas.width=glowCanvas.height=64;const glowCtx=glowCanvas.getContext('2d'),gradient=glowCtx.createRadialGradient(32,32,0,32,32,32);gradient.addColorStop(0,'#ffe2a9dd');gradient.addColorStop(.25,'#f6bb6266');gradient.addColorStop(1,'#ffa84900');glowCtx.fillStyle=gradient;glowCtx.fillRect(0,0,64,64);const glowTexture=new T.CanvasTexture(glowCanvas);
 for(const x of [-3.7,3.7]){
  block(backdrop,mat('#27221d'),x,1.5,-3.9,.06,3,.06);block(backdrop,mat('#27221d'),x,2.95,-3.9,.3,.05,.3);
  block(backdrop,new T.MeshStandardMaterial({color:'#f2c777',emissive:'#ffb350',emissiveIntensity:1.8}),x,2.75,-3.9,.18,.3,.18);
  const glow=new T.Sprite(new T.SpriteMaterial({map:glowTexture,transparent:true,depthWrite:false}));glow.position.set(x,2.78,-3.85);glow.scale.set(.9,.9,1);backdrop.add(glow);
 }
 const actors=new Map();let lastSize='',lastLook='',diagnostics={};
 function applyLook(options){
  const theme=options.theme||'night',quality=options.quality||'balanced',signature=theme+quality;if(signature===lastLook)return;lastLook=signature;
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,quality==='high'?2:1.25));key.shadow.mapSize.set(quality==='high'?2048:1024,quality==='high'?2048:1024);if(key.shadow.map){key.shadow.map.dispose();key.shadow.map=null}
  renderer.toneMappingExposure=theme==='sunset'?1.05:.83;
  key.color.set(theme==='sunset'?'#ffce91':'#ffe3b5');key.intensity=theme==='sunset'?2.8:2.0;rim.color.set(theme==='sunset'?'#ffc889':'#839ad1');rim.intensity=theme==='sunset'?.7:1.2;
  if(!transparent){scene.background.set(theme==='sunset'?'#554039':'#10121e');scene.fog.color.copy(scene.background)}
 }
 const project=p=>{const q=p.clone().project(camera);return {x:(q.x*.5+.5)*540,y:(-.5*q.y+.5)*960}};

 function render(users,time,bpm,mode='halay',options={}){
  applyLook(options);
  const ids=new Set(users.map(u=>u.id));for(const [id,a] of actors){if(!ids.has(id)){scene.remove(a.root);actors.delete(id)}}
  for(const u of users){let a=actors.get(u.id);const signature=u.costume+u.color+u.role;if(!a||a.signature!==signature){if(a)scene.remove(a.root);a=makeActor(u);a.signature=signature;actors.set(u.id,a);scene.add(a.root)}a.user=u}
  const dancers=users.filter(u=>u.role!=='drummer'&&u.role!=='zurnaci'),n=dancers.length;
  const layout=options.layout||'circle',circle=layout==='circle';
  const beat=time*bpm/60*Math.PI*2;
  const rows=[];let closed=false,radius=0,drumSpot,zurnaSpot,camPos,camLook;
  if(circle){
   // Videodaki gibi: herkes ortaya dönük, el ele tek halka. Az kişide halka arkadan dolmaya başlar.
   const spacing=.6,minRadius=3,need=n*spacing;
   closed=n>2&&need>=Math.PI*2*minRadius;radius=closed?need/(Math.PI*2):minRadius;
   const step=spacing/radius,first=closed?Math.PI-time*.035:Math.PI+(n-1)*step/2;
   for(let i=0;i<n;i++){
    const a=actors.get(dancers[i].id),angle=first-i*step,stepSide=Math.sin(beat)*.05;
    a.root.position.set(Math.sin(angle)*radius+Math.cos(angle)*stepSide,0,Math.cos(angle)*radius-Math.sin(angle)*stepSide);
    a.root.rotation.y=angle+Math.PI;a.root.scale.setScalar(1);
    if(mode==='orbit'){const r=1+Math.sin(beat*.5)*.03;a.root.position.x*=r;a.root.position.z*=r}
    updateLegs(a,time,bpm,1);rows.push(a);
   }
   const R=radius;
   // Kamera halkanın ön kenarının üstünde: öndeki dansçılar kadraj altında kalır, ortadaki kürsüler görünür.
   bench.position.set(.1,0,R*.12);bench.rotation.y=-.42;
   zurnaSpot=v(-R*.46,0,R*.3);drumSpot=v(R*.3,0,R*.5);
   backdrop.position.z=-R-1.6+5.3;
   camPos=v(0,4.4+R*1.15,R+3.3);camLook=v(0,0,-R*.42);
  }else{
   const span=Math.max(.65,Math.min(6.3,(n-1)*.65));
   const depth=layout==='line'?0:Math.min(layout==='wide'?1.3:2.6,span*(layout==='wide'?.23:.42));
   const path=[];let arcLength=0;
   for(let j=0;j<=160;j++){const q=j/80-1,p=v(q*span*.5,0,-.5-depth+depth*q*q);if(path.length)arcLength+=p.distanceTo(path[path.length-1].p);path.push({p,d:arcLength,q})}
   const scale=n>1?Math.min(1,arcLength/(n-1)/.77):1;
   const along=distance=>{let k=1;while(k<path.length-1&&path[k].d<distance)k++;const a=path[k-1],b=path[k],mix=(distance-a.d)/(b.d-a.d||1);return {p:a.p.clone().lerp(b.p,mix),q:a.q+(b.q-a.q)*mix}};
   const sideStep=Math.sin(beat)*.065*scale;
   for(let i=0;i<n;i++){
    const a=actors.get(dancers[i].id),location=along(n===1?arcLength*.5:i/(n-1)*arcLength),q=location.q;
    a.root.position.set(location.p.x+sideStep,0,location.p.z+Math.cos(beat)*.025*scale);a.root.scale.setScalar(scale);a.root.rotation.y=layout==='line'?0:-Math.atan(q*(layout==='wide'?.7:1.4))*.55;
    if(mode==='orbit'){a.root.position.z+=Math.sin(time*.35)*.15}
    updateLegs(a,time,bpm,scale);rows.push(a);
   }
   bench.position.set(0,0,2.1);bench.rotation.y=0;zurnaSpot=v(-1.7,0,2.9);drumSpot=v(1.4,0,3.55);backdrop.position.z=0;
   camPos=v(0,7.9,12.7);camLook=v(0,.25,0);
  }
  squareRugs.visible=!circle;roundRugs.zurna.visible=roundRugs.drum.visible=circle;
  roundRugs.zurna.position.copy(zurnaSpot);roundRugs.drum.position.copy(drumSpot);
  camera.position.copy(camPos);if(circle)camera.position.x+=Math.sin(time*.11)*.35;camera.lookAt(camLook);
  key.target.position.copy(camLook);key.position.set(camLook.x-3,8+radius,camLook.z+5);
  const joinHeight=circle?1.5:1.17,joins=[];
  const links=closed?rows.length:Math.max(0,rows.length-1);
  for(let i=0;i<links;i++){
   const left=rows[i],right=rows[(i+1)%rows.length],s=left.root.scale.x,p=left.root.localToWorld(v(.205,joinHeight,0)),q=right.root.localToWorld(v(-.205,joinHeight,0)),t=p.add(q).multiplyScalar(.5);
   t.y+=Math.sin(beat)*.065*s;joins.push(t);
  }
  for(let i=0;i<rows.length;i++){
   const a=rows[i];
   for(const arm of a.arms){const neighbor=arm.side===-1?(closed?joins[(i-1+rows.length)%rows.length]:joins[i-1]):joins[i];const target=neighbor||a.root.localToWorld(v(arm.side*.43,(circle?1.45:1.18)+Math.sin(beat)*.08,.06));solveArm(a,arm,target,time,bpm)}
  }
  for(let i=0;i<rows.length;i++){
   const a=rows[i];a.flag.visible=i===0&&!closed;
   if(a.flag.visible){a.flag.position.copy(a.arms[0].hand.position).add(v(-.065,-.13,0));a.flag.rotation.z=.2+Math.sin(beat)*.3;const positions=a.flag.geometry.attributes.position;for(let j=0;j<positions.count;j++)positions.setZ(j,Math.sin(positions.getY(j)*19+time*9)*.023);positions.needsUpdate=true}
  }
  let maxGap=0;
  for(let i=0;i<links;i++){
   const next=rows[(i+1)%rows.length],p=rows[i].body.localToWorld(rows[i].arms[1].hand.position.clone()),q=next.body.localToWorld(next.arms[0].hand.position.clone());maxGap=Math.max(maxGap,p.distanceTo(q));
  }
  const lift=circle?.1:.015,faceCamera=spot=>Math.atan2(camPos.x-spot.x,camPos.z-spot.z);
  const drummer=users.find(u=>u.role==='drummer');
  if(drummer){const a=actors.get(drummer.id);a.root.position.copy(drumSpot).setY(lift);a.root.scale.setScalar(1);a.root.rotation.y=circle?faceCamera(drumSpot)-.35:-.22;updateLegs(a,time,bpm,1);for(const arm of a.arms){solveArm(a,arm,a.root.localToWorld(v(arm.side*.18,1.0+Math.sin(beat+arm.side)*.08,.38)),time,bpm)}}
  const zurnaci=users.find(u=>u.role==='zurnaci');
  if(zurnaci){const a=actors.get(zurnaci.id);a.root.position.copy(zurnaSpot).setY(lift);a.root.scale.setScalar(1);a.root.rotation.y=circle?faceCamera(zurnaSpot)+.45:.3;updateLegs(a,time,bpm,1);a.body.rotation.x=-.04+Math.sin(beat*.5)*.03;a.root.updateMatrixWorld(true);const z=a.zurna;for(const arm of a.arms){const local=z.mouth.clone().lerp(z.bell,arm.side===-1?.62:.34);local.x+=arm.side*.03;solveArm(a,arm,a.body.localToWorld(local),time,bpm)}}
  const w=canvas.clientWidth,h=canvas.clientHeight,size=w+'x'+h;if(size!==lastSize){renderer.setSize(w,h,false);camera.aspect=w/h;lastSize=size}
  camera.updateProjectionMatrix();camera.updateMatrixWorld();
  renderer.render(scene,camera);
  const labels=users.map(u=>{const a=actors.get(u.id),head=a.root.localToWorld(v(0,2.12,0)),p=head.clone().project(camera),near=circle?Math.max(.62,Math.min(1.3,7.5/head.distanceTo(camera.position))):a.root.scale.x;return {user:u,x:(p.x*.5+.5)*540,y:(-.5*p.y+.5)*960,scale:near,depth:p.z}}).sort((a,b)=>b.depth-a.depth);
  labels.spots={drum:project(drumSpot.clone().setY(drummer?2.75:1.2)),zurna:project(zurnaSpot.clone().setY(zurnaci?2.75:1.2)),drumTaken:Boolean(drummer),zurnaTaken:Boolean(zurnaci)};
  diagnostics={renderer:'threejs-webgl',chainCount:n,links,closed,radius,maxHandGap:maxGap,maxFacingAngle:circle?0:Math.max(0,...rows.map(a=>Math.abs(a.root.rotation.y))),phase:time,layout,theme:options.theme||'night',quality:options.quality||'balanced',transparent,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles};
  return labels;
 }
 return {render,diagnostics:()=>diagnostics,dispose:()=>renderer.dispose()};
}
