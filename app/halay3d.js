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
function dressSkirt(){
 // Belden yere kadar inen, kıvrımlı uzun etek.
 return geo('longskirt',()=>{const points=[];for(let i=0;i<=12;i++){const q=i/12;points.push(new T.Vector2(.125+Math.pow(q,1.35)*.21,1.05-q*1.03))}const g=new T.LatheGeometry(points,56);const pos=g.attributes.position;for(let i=0;i<pos.count;i++){const y=pos.getY(i),a=Math.atan2(pos.getX(i),pos.getZ(i)),depth=(1.05-y)/1.03,fold=1+Math.sin(a*14)*.06*depth+Math.sin(a*5+1)*.02*depth;pos.setX(i,pos.getX(i)*fold);pos.setZ(i,pos.getZ(i)*fold)}g.computeVertexNormals();return g});
}
function dressFabric(color){
 const key='dress:'+color;if(materials.has(key))return materials.get(key);
 const cn=document.createElement('canvas');cn.width=cn.height=256;const ctx=cn.getContext('2d');
 ctx.fillStyle=color;ctx.fillRect(0,0,256,256);
 // Yumuşak kumaş dokusu ve önde ince işleme şeridi.
 for(let x=0;x<256;x++){const shade=Math.sin(x/256*Math.PI*28)*.5+.5;ctx.fillStyle=`rgba(0,0,0,${.05+shade*.12})`;ctx.fillRect(x,0,1,256)}
 for(let y=0;y<256;y+=3){ctx.fillStyle=y%6?'#ffffff05':'#00000008';ctx.fillRect(0,y,256,1)}
 ctx.strokeStyle='#c9a55a99';ctx.lineWidth=2;for(const x of [120,136]){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,256);ctx.stroke()}
 for(let y=10;y<256;y+=22){ctx.fillStyle='#d8b867aa';ctx.beginPath();ctx.moveTo(128,y-5);ctx.lineTo(132,y);ctx.lineTo(128,y+5);ctx.lineTo(124,y);ctx.fill()}
 const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;const material=new T.MeshStandardMaterial({map:tex,roughness:.92,metalness:.02,side:T.DoubleSide});materials.set(key,material);return material;
}
// "Dansçını seç" kostümleri: hayvan maskotları ve malzeme stilleri.
const ANIMALS={
 'ayı':{fur:'#6b4630',muzzle:'#c49a72',ears:'round'},
 'tilki':{fur:'#c8622a',muzzle:'#f3e7d8',ears:'pointy',tip:'#2b1d17',tail:'#c8622a'},
 'kedi':{fur:'#8d8a86',muzzle:'#efe8de',ears:'cat',whiskers:true},
 'tavşan':{fur:'#ece6de',muzzle:'#fbf6f0',ears:'long',inner:'#e9a7b2',tail:'#ffffff'},
 'koyun':{fur:'#f1ece2',face:'#2b2522',muzzle:'#3a312c',ears:'side',wool:true},
 'penguen':{fur:'#1b1c22',muzzle:'#f2f0ea',ears:'none',beak:'#f0a232',belly:'#f4f1ea'}
};
const STYLES=new Set(['oyuncak','ahşap','köşeli']);
function woodMaterial(dark){
 const key='wood:'+dark;if(materials.has(key))return materials.get(key);
 const cn=document.createElement('canvas');cn.width=cn.height=256;const ctx=cn.getContext('2d');
 ctx.fillStyle=dark?'#6b4428':'#b07a48';ctx.fillRect(0,0,256,256);
 for(let i=0;i<70;i++){ctx.strokeStyle=i%3?'#00000018':'#ffffff14';ctx.lineWidth=1+i%3;ctx.beginPath();const y=i*3.7;ctx.moveTo(0,y);for(let x=0;x<=256;x+=16)ctx.lineTo(x,y+Math.sin(x*.05+i)*4);ctx.stroke()}
 const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;const m=new T.MeshStandardMaterial({map:tex,roughness:.7});materials.set(key,m);return m;
}
function toyMaterial(source,hash){
 // Parlak plastik: dokuyu bırakır, rengi doygunlaştırır.
 const base=new T.Color(source.color);if(source.map)base.set(['#e63946','#2a9d8f','#457bdc','#f4a261','#9b5de5'][hash%5]);
 const hsl={};base.getHSL(hsl);const key='toy:'+base.getHexString();if(materials.has(key))return materials.get(key);
 const m=new T.MeshStandardMaterial({color:new T.Color().setHSL(hsl.h,Math.min(1,hsl.s*1.4+.15),Math.min(.62,Math.max(.3,hsl.l*1.15))),roughness:.28,metalness:.05});materials.set(key,m);return m;
}
function animalHead(body,kind,a){
 const fur=mat(a.fur,.85),face=mat(a.face||a.fur,.85),muzzle=mat(a.muzzle,.8),dark=mat('#120f10',.4);
 ell(body,face,0,1.6,0,.095,.1,.095);
 if(kind==='penguen'){for(const x of [-.035,.035])ell(body,mat('#f2f0ea',.8),x,1.62,.06,.035,.045,.03);const beak=mesh(geo('beak',()=>new T.ConeGeometry(.025,.08,10)),mat(a.beak,.5),body,0,1.585,.11);beak.rotation.x=Math.PI/2;ell(body,mat(a.belly,.85),0,1.15,.07,.12,.26,.07)}
 else{ell(body,muzzle,0,1.575,.07,.05,.04,.045);ell(body,dark,0,1.59,.11,.016,.012,.01)}
 for(const x of [-.034,.034])ell(body,dark,x,1.63,.08,.012,.014,.006);
 const ears=[];
 if(a.ears==='round')for(const s of [-1,1])ears.push(ell(body,fur,s*.07,1.69,-.005,.035,.035,.02));
 if(a.ears==='pointy'||a.ears==='cat')for(const s of [-1,1]){const h=a.ears==='cat'?.07:.1,e=mesh(geo('ear'+h,()=>new T.ConeGeometry(.04,h,4)),fur,body,s*.06,1.7+h*.3,-.01);e.rotation.z=-s*.25;if(a.tip)mesh(geo('eartip',()=>new T.ConeGeometry(.018,.035,4)),mat(a.tip),body,s*.06+(-s*.25)*-.035,1.7+h*.3+h*.38,-.01).rotation.z=-s*.25}
 if(a.ears==='long')for(const s of [-1,1]){const e=ell(body,fur,s*.04,1.78,-.01,.028,.13,.016);e.rotation.z=-s*.12;const inner=ell(body,mat(a.inner,.8),s*.04,1.78,.004,.015,.1,.008);inner.rotation.z=-s*.12}
 if(a.ears==='side')for(const s of [-1,1]){const e=ell(body,face,s*.1,1.62,0,.06,.02,.025);e.rotation.z=s*.3}
 if(a.wool){const wool=mat(a.fur,1);for(let i=0;i<7;i++){const ang=i/7*Math.PI*2;ell(body,wool,Math.sin(ang)*.06,1.68+Math.cos(ang*2)*.01,Math.cos(ang)*.05-.01,.045,.04,.045)}}
 if(a.whiskers)for(const s of [-1,1])for(const dy of [-.008,.008]){const w=bone(body,mat('#f5f5f0'),.0025);segment(w,v(s*.03,1.575+dy,.1),v(s*.12,1.57+dy*2,.09))}
 if(a.tail){const t=ell(body,mat(a.tail,.85),0,.85,-.3,kind==='tavşan'?.06:.07,kind==='tavşan'?.06:.07,kind==='tavşan'?.06:.22);t.rotation.x=kind==='tavşan'?0:-.6}
 return ears;
}
function applyStyle(root,kind,hash){
 if(!STYLES.has(kind))return;
 const lowSphere=geo('lowsphere',()=>new T.IcosahedronGeometry(1,0)),lowSkirt=geo('lowskirt',()=>new T.CylinderGeometry(.13,.34,1.03,7));
 root.traverse(o=>{
  if(!o.isMesh)return;const m=o.material;
  if(kind==='ahşap')o.material=woodMaterial(m.metalness>.2);
  else if(kind==='oyuncak')o.material=toyMaterial(m,hash+(m.metalness>.2?2:0));
  else{const key='flat:'+m.uuid;if(!materials.has(key)){const f=m.clone();f.flatShading=true;f.needsUpdate=true;materials.set(key,f)}o.material=materials.get(key);if(o.geometry===sphere)o.geometry=lowSphere;if(o.geometry===geometries.get('longskirt')){o.geometry=lowSkirt;o.position.y=.535}}
 });
}
// --- İskeletli 3B karakterler (Quaternius Universal Base Characters, CC0; tools/model_build.py ile hazırlanır) ---
let MODELS=null;
const HUMAN_COSTUMES=new Set(['','kız','qız','erkek','oğlan']);
async function loadModels(){
 const loader=new T.TextureLoader();
 const tex=(name,srgb=true)=>{const t=loader.load('/assets/models/'+name);t.flipY=false;if(srgb)t.colorSpace=T.SRGBColorSpace;t.anisotropy=4;return t};
 async function one(name){
  const [meta,bin]=await Promise.all([fetch(`/assets/models/${name}.json`).then(r=>{if(!r.ok)throw new Error(name);return r.json()}),fetch(`/assets/models/${name}.bin`).then(r=>r.arrayBuffer())]);
  const ibmArray=new Float32Array(bin,meta.ibm,meta.joints.length*16),ibm=meta.joints.map((_,i)=>new T.Matrix4().fromArray(ibmArray,i*16));
  const geoms={};
  for(const m of meta.meshes){
   const g=new T.BufferGeometry();
   g.setAttribute('position',new T.BufferAttribute(new Float32Array(bin,m.position,m.count*3),3));
   g.setAttribute('normal',new T.BufferAttribute(new Float32Array(bin,m.normal,m.count*3),3));
   g.setAttribute('uv',new T.BufferAttribute(new Float32Array(bin,m.uv,m.count*2),2));
   g.setAttribute('skinIndex',new T.BufferAttribute(new Uint8Array(bin,m.joints,m.count*4),4));
   g.setAttribute('skinWeight',new T.BufferAttribute(new Float32Array(bin,m.weights,m.count*4),4));
   g.setAttribute('region',new T.BufferAttribute(new Float32Array(bin,m.region,m.count),1));
   g.setIndex(new T.BufferAttribute(m.indexType==='u32'?new Uint32Array(bin,m.index,m.indexCount):new Uint16Array(bin,m.index,m.indexCount),1));
   geoms[m.name]=g;
  }
  return {meta,ibm,geoms};
 }
 const [kadin,erkek]=await Promise.all([one('kadin'),one('erkek')]);
 kadin.skins=[tex('kadin-ten-acik.jpg'),tex('kadin-ten-koyu.jpg')];kadin.normal=tex('kadin-normal.jpg',false);
 erkek.skins=[tex('erkek-ten-acik.jpg'),tex('erkek-ten-koyu.jpg')];erkek.normal=tex('erkek-normal.jpg',false);
 const hair=tex('sac.jpg'),eye=tex('goz.jpg');
 return {kadin,erkek,hair,eye};
}
function clothedMaterial(lib,skinIndex,garment,legs,shoes){
 // Gövde dokusu ten için kullanılır; "region" değeri olan bölgeler kıyafet rengiyle boyanır.
 const key=['clothed',lib===MODELS.kadin?'k':'e',skinIndex,garment,legs,shoes].join(':');if(materials.has(key))return materials.get(key);
 const m=new T.MeshStandardMaterial({map:lib.skins[skinIndex],normalMap:lib.normal,roughness:.78,metalness:0});
 const uniforms={uGarment:{value:new T.Color(garment)},uLegs:{value:new T.Color(legs)},uShoes:{value:new T.Color(shoes)}};
 m.onBeforeCompile=shader=>{
  Object.assign(shader.uniforms,uniforms);
  shader.vertexShader='attribute float region;\nvarying float vRegion;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvRegion=region;');
  shader.fragmentShader='uniform vec3 uGarment;\nuniform vec3 uLegs;\nuniform vec3 uShoes;\nvarying float vRegion;\n'+shader.fragmentShader.replace('#include <map_fragment>',`#include <map_fragment>
  if(vRegion>.5){
   vec3 cloth=vRegion<1.5?uGarment:(vRegion<2.5?uLegs:uShoes);
   float weave=.94+.06*sin(vMapUv.x*900.)*sin(vMapUv.y*900.);
   diffuseColor.rgb=cloth*weave;
  }`).replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\n if(vRegion>.5)roughnessFactor=.92;');
 };
 m.customProgramCacheKey=()=>'clothed-region';
 materials.set(key,m);return m;
}
function plainModelMaterial(name,map,color,roughness=.6){const key='modelmat:'+name+color;if(!materials.has(key))materials.set(key,new T.MeshStandardMaterial({map,color,roughness}));return materials.get(key)}
function makeModelActor(user){
 const hash=[...user.id].reduce((a,ch)=>a+ch.charCodeAt(0),0),female=user.costume!=='erkek'&&user.costume!=='oğlan',lib=female?MODELS.kadin:MODELS.erkek;
 const root=new T.Group(),body=new T.Group();root.add(body);
 // İskeleti her karakter için yeniden kur; geometriler ve dokular paylaşılır.
 const joints=lib.meta.joints,bones=joints.map(j=>{const b=new T.Bone();b.name=j.name;b.position.fromArray(j.t);b.quaternion.fromArray(j.r);b.scale.fromArray(j.s);return b});
 joints.forEach((j,i)=>{if(j.parent>=0)bones[j.parent].add(bones[i]);else body.add(bones[i])});
 const skeleton=new T.Skeleton(bones,lib.ibm),B=Object.fromEntries(bones.map(b=>[b.name,b]));
 root.updateMatrixWorld(true);
 const color=user.color||'#7a1e2c',skinIndex=hash%4===3?1:0,hairColor=['#2a1a12','#1b1210','#3d2516','#120d0c'][hash%4];
 const bodyMat=female?clothedMaterial(lib,skinIndex,color,'#151316','#141216'):clothedMaterial(lib,skinIndex,'#e4dccd','#1d1b22','#141216');
 const hairMat=plainModelMaterial('hair'+hairColor,MODELS.hair,hairColor,.55),eyeMat=plainModelMaterial('eye',MODELS.eye,'#ffffff',.2);
 const parts=[['body',bodyMat],['eyes',eyeMat],['brows',hairMat]];
 if(female)parts.push([hash%3===1?'Hair_Buns':'Hair_Long',hairMat]);else{parts.push(['Hair_SimpleParted',hairMat]);if(hash%3===0)parts.push(['Hair_Beard',hairMat])}
 for(const [name,material] of parts){const sm=new T.SkinnedMesh(lib.geoms[name],material);sm.bind(skeleton,new T.Matrix4());sm.castShadow=true;sm.receiveShadow=true;sm.frustumCulled=false;body.add(sm)}
 // Kıyafet aksesuarları dinlenme pozunda kurulur ve ilgili kemiğe bağlanır.
 const gold=mat('#b89244',.4,.45),add=(boneName,object)=>{body.add(object);object.updateMatrixWorld(true);B[boneName].attach(object);return object};
 if(female){
  const skirt=new T.Mesh(dressSkirt(),dressFabric(color));skirt.scale.set(1.32,1,1.18);skirt.position.y=-.02;skirt.castShadow=skirt.receiveShadow=true;add('pelvis',skirt);
  const hem=new T.Mesh(geo('hemband',()=>new T.CylinderGeometry(.342,.35,.035,56,1,true)),mat('#8f6d32',.5,.4));hem.scale.set(1.32,1,1.18);hem.position.y=.03;add('pelvis',hem);
  const belt=new T.Mesh(geo('modelbelt',()=>new T.CylinderGeometry(.15,.16,.06,28)),gold);belt.scale.set(1,1,.82);belt.position.set(0,1.02,-.02);add('pelvis',belt);
  const band=new T.Mesh(geo('modelband',()=>new T.TorusGeometry(.098,.007,6,36)),gold);band.rotation.x=Math.PI/2.1;band.position.set(0,1.69,.005);add('Head',band);
  for(let i=-4;i<=4;i++){const coin=ell(body,gold,Math.sin(i*.24)*.1,1.675,Math.cos(i*.24)*.1+.003,.011,.014,.004);B.Head.attach(coin)}
 }else{
  for(const s of [-1,1]){const vest=block(body,dressFabric(color),s*.085,1.25,.1,.13,.38,.04);B.spine_02.attach(vest)}
  const sash=new T.Mesh(geo('sash',()=>new T.CylinderGeometry(.16,.165,.08,28)),mat('#7d1d28',.8));sash.scale.set(1,1,.8);sash.position.set(0,1.0,-.02);add('pelvis',sash);
  const hat=new T.Mesh(geo('modelkalpak',()=>new T.CylinderGeometry(.088,.098,.1,22)),mat('#141216',.7));hat.position.set(0,1.79,-.01);add('Head',hat);
 }
 let drum=null,zurna=null;
 if(user.role==='drummer'){
  drum=new T.Group();drum.position.set(0,.95,.36);drum.rotation.x=Math.PI*.09;body.add(drum);
  mesh(geo('drum',()=>new T.CylinderGeometry(.27,.27,.31,32)),mat('#5a1820',.8),drum,0,0,0);
  for(const h of [-.16,.16])mesh(geo('drumskin',()=>new T.CylinderGeometry(.285,.285,.025,32)),mat('#d8c49e'),drum,0,h,0);
  for(let k=0;k<Math.PI*2;k+=Math.PI/6){const cord=bone(drum,gold,.008);segment(cord,v(Math.cos(k)*.277,-.15,Math.sin(k)*.277),v(Math.cos(k+.26)*.277,.15,Math.sin(k+.26)*.277))}
  drum.updateMatrixWorld(true);B.spine_01.attach(drum);
 }
 if(user.role==='zurnaci'){
  zurna={mouth:v(0,1.57,.11),bell:v(0,1.24,.5)};
  const pipe=mesh(geo('zurna',()=>new T.CylinderGeometry(.014,.048,1,14)),mat('#7a4a25',.55),body,0,0,0);segment(pipe,zurna.bell,zurna.mouth);pipe.updateMatrixWorld(true);B.Head.attach(pipe);
 }
 const flag=new T.Mesh(new T.PlaneGeometry(.22,.28,6,8),new T.MeshStandardMaterial({color:'#b82536',roughness:1,side:T.DoubleSide}));flag.visible=false;body.add(flag);
 const rest=new Map(bones.map(b=>[b,b.quaternion.clone()]));
 const arms=[-1,1].map(side=>{const s=side===1?'l':'r';return {side,upper:B['upperarm_'+s],lower:B['lowerarm_'+s],handBone:B['hand_'+s],hand:new T.Object3D()}});
 return {root,body,user,legs:[],arms,drum,zurna,flag,phase:hash*.001,model:{bone:B,rest,female}};
}
const _q=new T.Quaternion(),_q2=new T.Quaternion(),_v=new T.Vector3(),_v2=new T.Vector3(),_axis=new T.Vector3();
function rotateBone(bone,axisRoot,angle,root){
 // Karakterin kendi eksenine göre (ileri/yan) döndür; kemiğin yerel eksenleri farklı olabilir.
 _axis.copy(axisRoot).applyQuaternion(root.quaternion);bone.parent.getWorldQuaternion(_q).invert();_axis.applyQuaternion(_q).normalize();
 bone.quaternion.premultiply(_q2.setFromAxisAngle(_axis,angle));
}
function animateModel(a,time,bpm){
 const {bone,rest}=a.model,cycle=time*bpm/60*Math.PI*2;
 for(const [b,q] of rest)b.quaternion.copy(q);
 a.body.position.y=Math.max(0,Math.sin(cycle*2))*.03;a.body.rotation.z=Math.sin(cycle)*.02;
 a.root.updateMatrixWorld(true);
 const X=v(1,0,0),Z=v(0,0,1);
 for(const [s,phase] of [['l',0],['r',Math.PI]]){
  const step=Math.sin(cycle+phase);
  rotateBone(bone['thigh_'+s],X,-step*.22-.04,a.root);
  bone['thigh_'+s].updateMatrixWorld(true);
  rotateBone(bone['calf_'+s],X,Math.max(0,Math.sin(cycle+phase))*.38,a.root);
 }
 rotateBone(bone.spine_02,Z,Math.sin(cycle)*.04,a.root);
 rotateBone(bone.Head,X,Math.sin(cycle*2)*.04,a.root);
 a.root.updateMatrixWorld(true);
}
function aimBone(b,childLocal,target){
 b.updateWorldMatrix(true,false);b.getWorldPosition(_v);b.getWorldQuaternion(_q);
 _v2.copy(childLocal).normalize().applyQuaternion(_q);
 const want=target.clone().sub(_v).normalize();
 _q2.setFromUnitVectors(_v2,want).multiply(_q);
 b.parent.getWorldQuaternion(_q).invert();b.quaternion.copy(_q.multiply(_q2));b.updateMatrixWorld(true);
}
function modelArm(a,arm,target){
 // İki kemikli ters kinematik: omuz -> dirsek -> bilek. Dirsek aşağı ve dışa bakar.
 arm.upper.updateWorldMatrix(true,true);
 const shoulder=arm.upper.getWorldPosition(new T.Vector3()),elbow0=arm.lower.getWorldPosition(new T.Vector3()),wrist0=arm.handBone.getWorldPosition(new T.Vector3());
 const L1=shoulder.distanceTo(elbow0),L2=elbow0.distanceTo(wrist0);
 const d=target.clone().sub(shoulder),dist=Math.min(Math.max(d.length(),.05),(L1+L2)*.999),dir=d.normalize();
 const pole=v(arm.side*.7,-1,-.25).applyQuaternion(a.root.quaternion),ortho=pole.sub(dir.clone().multiplyScalar(pole.dot(dir))).normalize();
 const along=(L1*L1-L2*L2+dist*dist)/(2*dist),height=Math.sqrt(Math.max(0,L1*L1-along*along));
 const elbow=shoulder.clone().addScaledVector(dir,along).addScaledVector(ortho,height),wrist=shoulder.clone().addScaledVector(dir,dist);
 aimBone(arm.upper,arm.lower.position,elbow);aimBone(arm.lower,arm.handBone.position,wrist);
 // Parmaklar komşunun eline doğru, hafif aşağı baksın: el ele tutuşma görüntüsü.
 const finger=arm.handBone.children.find(c=>c.name.startsWith('middle_01'));
 if(finger){const reach=v(arm.side,0,0).applyQuaternion(a.root.quaternion).multiplyScalar(.6).add(dir).setY(-.25).normalize();aimBone(arm.handBone,finger.position,wrist.clone().add(reach))}
 arm.handBone.getWorldPosition(_v);arm.hand.position.copy(a.body.worldToLocal(_v.clone()));
}
function makeActor(user){
 if(MODELS&&HUMAN_COSTUMES.has(user.costume||''))return makeModelActor(user);
 const root=new T.Group(),body=new T.Group();root.add(body);
 const kind=user.costume,animal=ANIMALS[kind];
 const hash=[...user.id].reduce((a,ch)=>a+ch.charCodeAt(0),0),skin=animal?mat(animal.fur,.85):mat(['#c99b78','#d9b08e','#b88763','#e2bc9c'][hash%4],.6),cloth=animal?mat(animal.fur,.95):dressFabric(user.color||'#6d2333'),plain=animal?mat(animal.fur,.9):mat(user.color||'#6d2333',.9),gold=mat('#b89244',.4,.45),dark=mat('#141216',.7),hair=mat(['#1d1411','#33201a','#141215','#4a2c1d'][hash%4],.55);
 const female=user.costume!=='erkek';
 // Gövde: ince bel, dar omuz; boy yaklaşık 1.75.
 if(female){
  mesh(geo('bodice',()=>new T.CylinderGeometry(.16,.125,.4,24)),cloth,body,0,1.22,0,1,1,.72);
  ell(body,plain,0,1.41,0,.175,.07,.11);
  mesh(dressSkirt(),cloth,body,0,0,0);
  mesh(geo('hemband',()=>new T.CylinderGeometry(.342,.35,.035,56,1,true)),mat('#8f6d32',.5,.4),body,0,.05,0);
  mesh(geo('belt2',()=>new T.CylinderGeometry(.128,.128,.05,24)),gold,body,0,1.04,0,1,1,.74);
  for(let i=0;i<5;i++)ell(body,gold,0,1.12+i*.055,.092,.012,.016,.006);
 }else{
  const shirt=mat('#e6dccb',.85),trousers=mat('#1d1b22',.9);
  mesh(geo('shirt',()=>new T.CylinderGeometry(.165,.14,.42,24)),shirt,body,0,1.2,0,1,1,.72);
  ell(body,shirt,0,1.4,0,.18,.07,.115);
  block(body,cloth,-.085,1.21,.06,.12,.4,.05);block(body,cloth,.085,1.21,.06,.12,.4,.05);
  mesh(geo('hips2',()=>new T.CylinderGeometry(.14,.135,.16,20)),trousers,body,0,.95,0,1,1,.75);
  mesh(geo('belt2m',()=>new T.CylinderGeometry(.142,.142,.06,24)),mat('#7d1d28',.8),body,0,1.02,0,1,1,.76);
 }
 // Boyun ve oranlı baş; küçük yüz ayrıntıları.
 ell(body,skin,0,1.48,0,.045,.06,.045);
 if(animal)animalHead(body,kind,animal);
 else{
 ell(body,skin,0,1.6,0,.078,.1,.085);
 ell(body,skin,0,1.575,.075,.013,.02,.016);
 for(const x of [-.028,.028])ell(body,dark,x,1.615,.072,.009,.006,.004);
 for(const x of [-.03,.03])ell(body,hair,x,1.637,.074,.016,.003,.004);
 ell(body,mat('#8c4f45',.6),0,1.548,.072,.02,.005,.005);
 if(female){
  ell(body,hair,0,1.645,-.012,.084,.078,.088);
  ell(body,hair,0,1.5,-.06,.085,.17,.05);
  mesh(geo('coinband',()=>new T.TorusGeometry(.083,.008,6,32)),gold,body,0,1.655,.004).rotation.x=Math.PI/2.15;
  for(let i=-3;i<=3;i++)ell(body,gold,Math.sin(i*.28)*.083,1.64,Math.cos(i*.28)*.083,.009,.012,.004);
 }else{
  ell(body,hair,0,1.65,-.01,.08,.06,.085);
  mesh(geo('kalpak',()=>new T.CylinderGeometry(.075,.085,.085,20)),dark,body,0,1.71,-.005);
  ell(body,hair,0,1.555,.07,.045,.012,.012);
 }
 }
 const legs=[];for(const side of [-1,1]){
  const upper=bone(body,female?dark:mat('#1d1b22',.9),female?.045:.06),lower=bone(body,female?dark:mat('#1d1b22',.9),.045),shoe=ell(body,kind==='penguen'?mat('#f0a232',.5):dark,side*.11,.065,.065,.06,.05,.13);
  legs.push({side,upper,lower,shoe});
 }
 const sleeve=female?cloth:mat('#e6dccb',.85),cuff=female?gold:sleeve;
 const arms=[];for(const side of [-1,1]){
  const upper=bone(body,sleeve,.05),lower=bone(body,sleeve,.043),elbow=ell(body,sleeve,0,0,0,.05,.05,.05),hand=ell(body,skin,0,0,0,.04,.045,.03);
  ell(body,plain,side*.165,1.39,0,.065,.06,.065);
  arms.push({side,upper,lower,elbow,hand,cuff:cuff===gold?mesh(geo('cuff',()=>new T.CylinderGeometry(.046,.046,.03,12)),gold,body,0,0,0):null});
 }
 let drum=null;
 if(user.role==='drummer'){
  drum=new T.Group();body.add(drum);drum.position.set(0,.88,.32);drum.rotation.x=Math.PI*.09;
  mesh(geo('drum',()=>new T.CylinderGeometry(.27,.27,.31,32)),mat('#5a1820',.8),drum,0,0,0);
  for(const h of [-.16,.16])mesh(geo('drumskin',()=>new T.CylinderGeometry(.285,.285,.025,32)),mat('#d8c49e'),drum,0,h,0);
  for(let a=0;a<Math.PI*2;a+=Math.PI/6){const cord=bone(drum,gold,.008);segment(cord,v(Math.cos(a)*.277,-.15,Math.sin(a)*.277),v(Math.cos(a+.26)*.277,.15,Math.sin(a+.26)*.277))}
 }
 let zurna=null;
 if(user.role==='zurnaci'){
  // Zurna: ağızdan öne-aşağı uzanan, ucu genişleyen nefesli çalgı.
  zurna={mouth:v(0,1.55,.09),bell:v(0,1.2,.46)};
  const pipe=mesh(geo('zurna',()=>new T.CylinderGeometry(.014,.048,1,14)),mat('#7a4a25',.55),body,0,0,0);segment(pipe,zurna.bell,zurna.mouth);
  const lip=mesh(geo('zurnalip',()=>new T.TorusGeometry(.05,.009,6,20)),gold,body,0,0,0);lip.position.copy(zurna.bell);lip.quaternion.copy(pipe.quaternion);lip.rotateX(Math.PI/2);
 }
 const flag=new T.Mesh(new T.PlaneGeometry(.22,.28,6,8),new T.MeshStandardMaterial({color:'#b82536',roughness:1,side:T.DoubleSide}));flag.visible=false;body.add(flag);
 applyStyle(root,kind,hash);
 return {root,body,user,legs,arms,drum,zurna,flag,phase:hash*.001};
}
function updateLegs(a,time,beat,scale){
 if(a.model)return animateModel(a,time,beat);
 const cycle=time*beat/60*Math.PI*2,step=Math.sin(cycle),lift=Math.max(0,Math.sin(cycle*2))*.035;
 a.body.position.y=lift;
 a.body.rotation.z=Math.sin(cycle)*.025;
 for(const leg of a.legs){const s=leg.side,phase=cycle+(s===1?Math.PI:0);const ankle=v(s*.105+Math.sin(phase)*.04,.09+Math.max(0,Math.sin(phase))*.065,Math.cos(phase)*.065),hip=v(s*.105,.92,0),knee=hip.clone().lerp(ankle,.52);knee.z+=.055+Math.max(0,Math.sin(phase))*.07;segment(leg.upper,hip,knee);segment(leg.lower,knee,ankle);leg.shoe.position.copy(ankle).add(v(0,-.025,.055));leg.shoe.rotation.x=-Math.max(0,Math.sin(phase))*.14}
 a.root.updateMatrixWorld(true);
}
function solveArm(a,arm,target,time,bpm){
 if(a.model)return modelArm(a,arm,target);
 // The target is shared by adjacent dancers: the two wrist endpoints are identical.
 const shoulder=v(arm.side*.17,1.38,0),hand=a.body.worldToLocal(target.clone());
 const mid=shoulder.clone().lerp(hand,.5),distance=shoulder.distanceTo(hand),length=.3;
 const bend=Math.sqrt(Math.max(.001,length*length-distance*distance*.25));
 mid.y-=bend*.8;mid.x+=arm.side*bend*.45;mid.z-=.02;
 segment(arm.upper,shoulder,mid);segment(arm.lower,mid,hand);arm.elbow.position.copy(mid);arm.hand.position.copy(hand);
 if(arm.cuff){arm.cuff.position.copy(mid).lerp(hand,.86);arm.cuff.quaternion.copy(arm.lower.quaternion)}
}
function floorTexture(){const cn=document.createElement('canvas');cn.width=cn.height=1024;const ctx=cn.getContext('2d');ctx.fillStyle='#4a392e';ctx.fillRect(0,0,1024,1024);for(let row=0;row<8;row++)for(let col=-1;col<8;col++){let x=col*150+(row%2)*75,y=row*130;ctx.fillStyle=`hsl(22 18% ${21+((row*71+col*13)%4)}%)`;ctx.fillRect(x+2,y+2,146,126);ctx.strokeStyle='#3a2c24';ctx.lineWidth=1.5;ctx.strokeRect(x,y,150,130);for(let i=0;i<80;i++){ctx.fillStyle=i%2?'#ffffff08':'#0000000c';ctx.fillRect(x+(i*37)%148,y+(i*53)%127,2,1)}}const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(3,3);return tex}
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
 const hemi=new T.HemisphereLight('#e4d5be','#4d3029',2);scene.add(hemi);
 // Fenerlerden gelen sıcak ışık halkayı loş bir gece meydanı gibi aydınlatır.
 const warm=[];for(const [x,z] of [[-4,-2],[4,-2],[0,3]]){const l=new T.PointLight('#ffb466',0,16,1.6);l.position.set(x,3.2,z);scene.add(l);warm.push(l)}
 const key=new T.DirectionalLight('#ffe1ae',3.1);key.position.set(-3,8,5);key.castShadow=true;key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-9,right:9,top:9,bottom:-9,near:.5,far:30});key.shadow.normalBias=.025;key.shadow.bias=-.0003;scene.add(key);scene.add(key.target);
 const rim=new T.DirectionalLight('#b8c3ee',1.5);rim.position.set(3,4,-6);scene.add(rim);
 const decor=new T.Group();scene.add(decor);decor.visible=!transparent;
 const floor=floorTexture();floor.repeat.set(5,5);
 const ground=new T.Mesh(new T.PlaneGeometry(60,60),new T.MeshStandardMaterial({map:floor,roughness:.98}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;decor.add(ground);
 // Dikdörtgen kilimler yay/sıra düzenlerinde, yuvarlak kürsüler halka düzeninde kullanılır.
 const rugmat=new T.MeshStandardMaterial({map:rugTexture(),roughness:1,color:'#b9a9a6'}),squareRugs=new T.Group();decor.add(squareRugs);
 for(const [x,z,w,h] of [[-1.7,2.9,1.6,1.2],[1.4,3.7,2,1.5]]){const rug=new T.Mesh(new T.PlaneGeometry(w,h),rugmat);rug.rotation.x=-Math.PI/2;rug.position.set(x,.018,z);rug.receiveShadow=true;squareRugs.add(rug)}
 const roundmat=new T.MeshStandardMaterial({map:roundRugTexture(),roughness:1,color:'#b9a9a6'}),roundRugs={};
 for(const name of ['zurna','drum']){const g=new T.Group();decor.add(g);mesh(geo('dais',()=>new T.CylinderGeometry(.98,1.04,.1,48)),mat('#4a1119'),g,0,.05,0);const top=new T.Mesh(geo('daistop',()=>new T.CircleGeometry(.96,48)),roundmat);top.rotation.x=-Math.PI/2;top.position.y=.102;top.receiveShadow=true;g.add(top);roundRugs[name]=g}
 const bench=new T.Group();decor.add(bench);
 const benchmat=mat('#5e1722');block(bench,benchmat,0,.27,0,2.5,.21,.8);block(bench,mat('#c39a51',.45,.2),0,.16,0,2.54,.035,.84);for(const x of [-1.05,1.05])for(const z of [-.28,.28])block(bench,mat('#472f22'),x,.09,z,.07,.2,.07);
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
 const actors=new Map();
 loadModels().then(lib=>{MODELS=lib;for(const a of actors.values())scene.remove(a.root);actors.clear()}).catch(err=>console.warn('3B karakter modelleri yüklenemedi, basit karakterler kullanılıyor.',err));let lastSize='',lastLook='',diagnostics={};
 function applyLook(options){
  const theme=options.theme||'night',quality=options.quality||'balanced',signature=theme+quality;if(signature===lastLook)return;lastLook=signature;
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,quality==='high'?2:1.25));key.shadow.mapSize.set(quality==='high'?2048:1024,quality==='high'?2048:1024);if(key.shadow.map){key.shadow.map.dispose();key.shadow.map=null}
  renderer.toneMappingExposure=theme==='sunset'?1.0:.78;hemi.intensity=theme==='sunset'?1.8:.85;for(const l of warm)l.intensity=theme==='sunset'?6:16;
  key.color.set(theme==='sunset'?'#ffce91':'#ffe3b5');key.intensity=theme==='sunset'?2.6:1.35;rim.color.set(theme==='sunset'?'#ffc889':'#839ad1');rim.intensity=theme==='sunset'?.7:1.2;
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
   const spacing=.54,minRadius=2.7,need=n*spacing;
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
   zurnaSpot=v(-R*.4,0,R*.3);drumSpot=v(R*.3,0,R*.5);
   backdrop.position.z=-R-1.6+5.3;
   warm[0].position.set(-R*.95,3.4,-R*.35);warm[1].position.set(R*.95,3.4,-R*.35);warm[2].position.set(0,3.2,R*.45);
   camPos=v(0,3.9+R*1.05,R+2.9);camLook=v(0,.3,-R*.4);
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
  const joinHeight=circle?1.6:1.17,joins=[];
  const links=closed?rows.length:Math.max(0,rows.length-1);
  for(let i=0;i<links;i++){
   const left=rows[i],right=rows[(i+1)%rows.length],s=left.root.scale.x,p=left.root.localToWorld(v(.205,joinHeight,circle?.09:0)),q=right.root.localToWorld(v(-.205,joinHeight,circle?.09:0)),t=p.add(q).multiplyScalar(.5);
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
