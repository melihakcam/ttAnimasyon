from pathlib import Path
r=Path(r'D:\tiktokAnimasyon')
p=r/'engine.py';s=p.read_text(encoding='utf-8').replace("self.scene = 'halay'", "self.scene = 'halay'\n        self.layout = 'arc'\n        self.theme = 'night'\n        self.quality = 'balanced'")
s=s.replace("old_scene,old_capacity,old_source=self.scene,self.ring_capacity,self.source", "old_scene,old_capacity,old_source=self.scene,self.ring_capacity,self.source\n                old_layout,old_theme,old_quality=self.layout,self.theme,self.quality")
s=s.replace("self.scene,self.ring_capacity,self.source=old_scene,old_capacity,old_source", "self.scene,self.ring_capacity,self.source=old_scene,old_capacity,old_source\n                self.layout,self.theme,self.quality=old_layout,old_theme,old_quality")
s=s.replace("events=self.events,scene=self.scene,", "events=self.events,scene=self.scene,layout=self.layout,theme=self.theme,quality=self.quality,")
p.write_text(s,encoding='utf-8')
p=r/'server.py';s=p.read_text(encoding='utf-8').replace("    username: str=Field(default='',max_length=32)", "    username: str=Field(default='',max_length=32)\n    layout: Literal['arc','wide','line']='arc'\n    theme: Literal['night','sunset']='night'\n    quality: Literal['balanced','high']='balanced'")
s=s.replace("            engine.scene=settings.scene", "            engine.scene=settings.scene\n            engine.layout=settings.layout\n            engine.theme=settings.theme\n            engine.quality=settings.quality")
needle='async def stop_session():'
s=s.replace(needle,'''SETTINGS_PATH=ROOT/'runtime'/'settings.json'

def saved_settings():
    try: return SessionSettings.model_validate_json(SETTINGS_PATH.read_text(encoding='utf-8')).model_dump()
    except (OSError,ValueError): return SessionSettings().model_dump()

@app.get('/api/settings')
async def get_settings(): return saved_settings()

@app.post('/api/settings')
async def save_settings(settings:SessionSettings):
    async with session_lock:
        SETTINGS_PATH.parent.mkdir(exist_ok=True)
        temporary=SETTINGS_PATH.with_suffix('.tmp')
        temporary.write_text(settings.model_dump_json(indent=2),encoding='utf-8')
        temporary.replace(SETTINGS_PATH)
    return {'ok':True}

'''+needle)
p.write_text(s,encoding='utf-8')
# Visual upgrades and geometric layout options.
p=r/'app/halay3d.js';s=p.read_text(encoding='utf-8')
s=s.replace('function makeActor(user){',r'''function fabric(color){
 const key='fabric:'+color;if(materials.has(key))return materials.get(key);
 const cn=document.createElement('canvas');cn.width=cn.height=256;const ctx=cn.getContext('2d');
 ctx.fillStyle=color;ctx.fillRect(0,0,256,256);
 for(let x=0;x<256;x+=2){ctx.fillStyle=x%4?'#ffffff06':'#0000000c';ctx.fillRect(x,0,1,256)}
 for(const x of [18,36,220,238]){ctx.strokeStyle='#d6b467';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,256);ctx.stroke()}
 for(let y=15;y<256;y+=32)for(const x of [27,229]){ctx.strokeStyle='#e6c884';ctx.beginPath();ctx.moveTo(x,y-6);ctx.lineTo(x+5,y);ctx.lineTo(x,y+6);ctx.lineTo(x-5,y);ctx.closePath();ctx.stroke()}
 const tex=new T.CanvasTexture(cn);tex.colorSpace=T.SRGBColorSpace;const material=new T.MeshStandardMaterial({map:tex,roughness:.95});materials.set(key,material);return material;
}
function makeActor(user){''')
s=s.replace("cloth=mat(user.color||'#6d2333')", "cloth=fabric(user.color||'#6d2333')")
s=s.replace(" return {root,body,user,legs,arms,drum,phase:hash*.001};", """ const flag=new T.Mesh(new T.PlaneGeometry(.22,.28,6,8),new T.MeshStandardMaterial({color:'#b82536',roughness:1,side:T.DoubleSide}));flag.visible=false;body.add(flag);
 return {root,body,user,legs,arms,drum,flag,phase:hash*.001};""")
s=s.replace(" const actors=new Map();let lastSize='',diagnostics={};", r'''
 // Village courtyard backdrop, warm lanterns and fabric-covered seating.
 const stone=mat('#3f3933');block(decor,stone,0,.48,-5.3,13,.96,.35);
 for(const x of [-5.5,-3.7,3.7,5.5]){block(decor,mat('#5b4b3c'),x,1.4,-5.2,.34,2.8,.44);block(decor,mat('#a38459'),x,2.82,-5.2,.52,.12,.58)}
 const glowCanvas=document.createElement('canvas');glowCanvas.width=glowCanvas.height=64;const glowCtx=glowCanvas.getContext('2d'),gradient=glowCtx.createRadialGradient(32,32,0,32,32,32);gradient.addColorStop(0,'#ffe2a9dd');gradient.addColorStop(.25,'#f6bb6266');gradient.addColorStop(1,'#ffa84900');glowCtx.fillStyle=gradient;glowCtx.fillRect(0,0,64,64);const glowTexture=new T.CanvasTexture(glowCanvas);
 for(const x of [-3.7,3.7]){
  block(decor,mat('#27221d'),x,1.5,-3.9,.06,3,.06);block(decor,mat('#27221d'),x,2.95,-3.9,.3,.05,.3);
  const lamp=block(decor,new T.MeshStandardMaterial({color:'#f2c777',emissive:'#ffb350',emissiveIntensity:1.8}),x,2.75,-3.9,.18,.3,.18);
  const glow=new T.Sprite(new T.SpriteMaterial({map:glowTexture,transparent:true,depthWrite:false}));glow.position.set(x,2.78,-3.85);glow.scale.set(.9,.9,1);decor.add(glow);
 }
 for(let i=0;i<5;i++){const cushion=block(decor,fabric('#792537'),-.98+i*.49,.40,2.1,.46,.10,.7);cushion.rotation.z=(i%2?1:-1)*.025}
 const actors=new Map();let lastSize='',lastLook='',diagnostics={};
 function applyLook(options){
  const theme=options.theme||'night',quality=options.quality||'balanced',signature=theme+quality;if(signature===lastLook)return;lastLook=signature;
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,quality==='high'?2:1.25));key.shadow.mapSize.set(quality==='high'?2048:1024,quality==='high'?2048:1024);if(key.shadow.map){key.shadow.map.dispose();key.shadow.map=null}
  renderer.toneMappingExposure=theme==='sunset'?1.05:.83;
  key.color.set(theme==='sunset'?'#ffce91':'#ffe3b5');key.intensity=theme==='sunset'?2.8:2.0;rim.color.set(theme==='sunset'?'#ffc889':'#839ad1');rim.intensity=theme==='sunset'?.7:1.2;
  if(!transparent){scene.background.set(theme==='sunset'?'#554039':'#10121e');scene.fog.color.copy(scene.background)}
 }
''')
s=s.replace("function render(users,time,bpm,mode='halay'){", "function render(users,time,bpm,mode='halay',options={}){\n  applyLook(options);")
s=s.replace("const depth=Math.min(2.6,span*.42);", "const layout=options.layout||'arc';\n  const depth=layout==='line'?0:Math.min(layout==='wide'?1.3:2.6,span*(layout==='wide'?.23:.42));")
s=s.replace("a.root.rotation.y=-Math.atan(q*1.4)*.55;", "a.root.rotation.y=layout==='line'?0:-Math.atan(q*(layout==='wide'?.7:1.4))*.55;")
s=s.replace("  for(let i=0;i<rows.length-1;i++){\n   const p=rows[i].body.localToWorld", """  for(let i=0;i<rows.length;i++){
   const a=rows[i];a.flag.visible=i===0;
   if(i===0){a.flag.position.copy(a.arms[0].hand.position).add(v(-.065,-.13,0));a.flag.rotation.z=.2+Math.sin(beat)*.3;const positions=a.flag.geometry.attributes.position;for(let j=0;j<positions.count;j++)positions.setZ(j,Math.sin(positions.getY(j)*19+time*9)*.023);positions.needsUpdate=true}
  }
  for(let i=0;i<rows.length-1;i++){
   const p=rows[i].body.localToWorld""")
s=s.replace("phase:time,transparent,", "phase:time,layout,theme:options.theme||'night',quality:options.quality||'balanced',transparent,")
p.write_text(s,encoding='utf-8')
p=r/'app/scene.js';s=p.read_text(encoding='utf-8').replace("const transparent=new URLSearchParams(location.search).has('transparent');", """const params=new URLSearchParams(location.search),transparent=params.has('transparent'),preview=params.has('preview');
if(preview){state={...state,layout:params.get('layout')||'arc',theme:params.get('theme')||'night',quality:'balanced',users:Array.from({length:Math.min(24,Math.max(4,Number(params.get('capacity'))||12))},(_,i)=>({id:'preview'+i,name:['Elif','Melih','Dilan','Can','Nehir','Baran'][i%6],joined:true,points:0,color:['#6f1e35','#214d3c','#202d4b'][i%3],costume:i%3?'kız':'erkek',role:i===0?'drummer':'',bubble:''}))}}
""")
s=s.replace("connect(s=>{state=s;", "if(!preview)connect(s=>{state=s;")
s=s.replace("stage.render(users,phaseTime,state.bpm,state.scene)", "stage.render(users,phaseTime,state.bpm,state.scene,{layout:state.layout,theme:state.theme,quality:state.quality})")
s=s.replace(" hud(now,users);requestAnimationFrame(frame);", " hud(now,users);if(preview){rounded(170,823,200,30,12,'#171b24dc');text('ÖNİZLEME · örnek katılımcılar',270,843,12,'#ead28b')}requestAnimationFrame(frame);")
p.write_text(s,encoding='utf-8')
print('Layout options, saved settings and visual details added.')
