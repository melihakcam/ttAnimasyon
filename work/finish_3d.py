from pathlib import Path
r=Path(r'D:\tiktokAnimasyon')
p=r/'app/halay3d.js';s=p.read_text(encoding='utf-8').replace('new T.PerspectiveCamera(45','new T.PerspectiveCamera(49');s=s.replace("maxHandGap:maxGap,phase:time", "maxHandGap:maxGap,maxFacingAngle:Math.max(0,...rows.map(a=>Math.abs(a.root.rotation.y))),phase:time");p.write_text(s,encoding='utf-8')
p=r/'tests/browser_qa.py';s=p.read_text(encoding='utf-8').replace("'--disable-extensions'", "'--disable-extensions','--enable-unsafe-swiftshader'")
s=s.replace("before=await scene.locator('canvas').evaluate(\"el=>el.toDataURL()\")", "before=await scene.screenshot()")
s=s.replace("after=await scene.locator('canvas').evaluate(\"el=>el.toDataURL()\")", "after=await scene.screenshot()")
s=s.replace("scene.locator('canvas').evaluate", "scene.locator('#stage').evaluate")
s=s.replace("        await scene.screenshot(path=str(ROOT/'work'/'overlay-preview.png'))", """        await scene.wait_for_function('window.halayDiagnostics?.().chainCount>0')
        await scene.screenshot(path=str(ROOT/'work'/'overlay-preview.png'))
        diagnostics=await scene.evaluate('window.halayDiagnostics()')
        assert diagnostics['maxHandGap']<1e-6,diagnostics
        assert diagnostics['links']==diagnostics['chainCount']-1,diagnostics
        assert diagnostics['maxFacingAngle']<1.05,diagnostics
        # Exercise the same renderer at different crowd sizes and multiple movement phases.
        crowd_checks=await scene.evaluate('''async()=>{
          const {createHalayStage}=await import('/assets/halay3d.js');
          const canvas=document.createElement('canvas');canvas.style.cssText='position:fixed;width:540px;height:960px;inset:0';document.body.append(canvas);
          const renderer=createHalayStage(canvas,{transparent:true}),results=[];
          for(const count of [4,12,24,60]){
            const users=Array.from({length:count},(_,i)=>({id:'qa'+i,name:'QA '+i,color:'#73283b',costume:i%2?'kız':'erkek',role:''}));
            for(const phase of [0,.16,.37,.62]){renderer.render(users,phase,112,'halay');results.push({...renderer.diagnostics(),count})}
          }
          renderer.dispose();canvas.remove();return results;
        }''')
        assert all(c['maxHandGap']<1e-6 and c['links']==c['count']-1 for c in crowd_checks),crowd_checks
        (ROOT/'runtime'/'halay-chain-qa.json').write_text(json.dumps(crowd_checks,indent=2),encoding='utf-8')""")
s=s.replace("'live username field'", "'live username field','3D scene rendering','joined hands at 4/12/24/60 users across 4 dance phases','shared facing direction'")
p.write_text(s,encoding='utf-8')
# Current source documentation must describe the upgraded renderer accurately.
p=r/'README.md';s=p.read_text(encoding='utf-8').replace('app/scene.js`: Canvas çizimi;', 'app/scene.js`: yayın göstergeleri ve isimler; app/halay3d.js: yerel Three.js ile üç boyutlu karakterler, ışık/gölge, ortak el hedefleri ve eşzamanlı adımlar.').replace("`registerScene('isim', (users, time) => {...})` ile yeni çizici eklenir.", 'Yeni sahneler halay3d.js render yönlendirmesine eklenir.')
s+='''\n## Üç boyutlu halay güncellemesi\n\nHalay artık karşılıklı bağımsız karakterlerden oluşmaz. Aynı genel yöne bakan tek açık yay zinciri, komşular için aynı dünya koordinatındaki el hedeflerini kullanır. İki kol hedefe göre bükülür; yanal adım ve diz hareketleri tüm zincirde aynı ritimdedir. 4, 12, 24 ve 60 kişide dört farklı hareket anında el aralığı tarayıcı testinde ölçülür.\n\nKarakterler prosedürel 3B modellerdir; hacimli geleneksel kıyafet, başlık, yüz ayrıntıları, davul ve gölgeler vardır. Fotogerçekçi insan taraması veya videodaki özgün modeller değildir. Alternatif çember modülü de aynı el bağlantısını korur. Ses halen eklenmemiştir.\n\nThree.js 0.170.0 yerel app/vendor altında ve MIT lisansı THREE-LICENSE.txt içinde. Yayın sırasında CDN bağlantısı gerekmez. 3B görüntü WebGL 2 destekli ve grafik hızlandırması açık bir tarayıcı/OBS gerektirir; performans bilgisayarın ekran kartına ve katılımcı sayısına bağlıdır.\n'''
p.write_text(s,encoding='utf-8')
p=r/'VIDEO_ANALIZI.md';s=p.read_text(encoding='utf-8');s+='''\n## El ele halay düzeltmesi\n\nKullanıcı, el ele tutuşulması ve ilk görselin gerçekçilik düzeyinin düşük olması konusunda düzeltme yaptı. Önceki 2B çizim kaldırıldı; üç boyutlu, aynı yöne dönük açık yay zinciri eklendi. Komşu elleri ortak hedefte buluşuyor. Bu, referansın özgün karakter varlıklarının çıkarıldığı anlamına gelmiyor; yeni modeller stilize ve prosedüreldir. Önceki 2B benzerlik notu eski sürümü anlatır.\n''';p.write_text(s,encoding='utf-8')
print('3D tests and documentation updated.')
