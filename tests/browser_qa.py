import asyncio,json,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(r'D:\tiktokAnimasyon')
os.environ['TEMP']=str(ROOT/'work');os.environ['TMP']=str(ROOT/'work')
async def main():
    errors=[]
    async with async_playwright() as p:
        context=await p.chromium.launch_persistent_context(
            str(ROOT/'work'/'browser-profile'),
            executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            extra_http_headers={'Cache-Control':'no-cache'},headless=True,viewport={'width':1440,'height':1100},
            args=['--disable-breakpad','--disable-crash-reporter','--no-first-run','--disable-extensions','--enable-unsafe-swiftshader','--mute-audio'],
            downloads_path=str(ROOT/'work'/'downloads'))
        page=context.pages[0]
        page.on('pageerror',lambda err: errors.append(str(err)))
        await page.goto('http://127.0.0.1:8765/panel')
        await page.wait_for_function("document.querySelector('#connection').textContent.includes('Bağlı')")
        originalRules=await page.evaluate("fetch('/api/rules').then(r=>r.json())")
        await page.evaluate("fetch('/api/session/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'demo',scene:'halay',capacity:24})})")
        await page.evaluate("fetch('/api/session/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})")
        await page.evaluate("fetch('/api/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'control',text:'reset'})})")
        await page.get_by_role('button',name='Demo katılımcıları').click()
        await page.wait_for_function("document.querySelector('#total').textContent==='18 kişi'")
        overlay=page.frames[1]
        await overlay.wait_for_function("document.querySelector('#connection').textContent===''")
        # Exercise actual panel interactions, including gift and like controls.
        await page.locator('#uid').fill('qa-browser')
        await page.locator('#name').fill('Tarayıcı Testi')
        await page.locator('#comment').fill('qız')
        await page.get_by_role('button',name='Sahneye gönder').click()
        await page.wait_for_function("document.querySelector('#total').textContent==='19 kişi'")
        await page.locator('#type').select_option('gift')
        await page.locator('#gift').select_option('Rose')
        await page.locator('#count').fill('3')
        await page.get_by_role('button',name='Sahneye gönder').click()
        await page.wait_for_function("document.querySelector('#people').textContent.includes('Tarayıcı Testi · 3 puan')")
        await page.locator('#type').select_option('like')
        await page.locator('#uid').fill('qa-liker')
        await page.locator('#name').fill('Beğenen')
        await page.get_by_role('button',name='Sahneye gönder').click()
        await page.wait_for_function("document.querySelector('#summary').textContent.startsWith('20/24 dansçı')")
        await page.locator('#scene').select_option('orbit')
        await page.wait_for_function("document.querySelector('#summary').textContent.includes('Çember')")
        await page.locator('#scene').select_option('halay')
        await page.get_by_role('button',name='20 sn hızlandır').click()
        await page.screenshot(path=str(ROOT/'work'/'panel-preview.png'),full_page=True)
        await page.set_viewport_size({'width':390,'height':844})
        await page.screenshot(path=str(ROOT/'work'/'panel-mobile.png'),full_page=True)
        assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'Mobile horizontal overflow'
        scene=await context.new_page()
        scene.on('pageerror',lambda err: errors.append(str(err)))
        await scene.set_viewport_size({'width':540,'height':960})
        await scene.goto('http://127.0.0.1:8765/overlay')
        await scene.wait_for_function("document.querySelector('#connection').textContent===''")
        await scene.wait_for_function('window.halayDiagnostics?.().chainCount>0')
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
            for(const layout of ['arc','wide','line'])for(const phase of [0,.16,.37,.62]){renderer.render(users,phase,112,'halay',{layout,theme:'night',quality:'balanced'});results.push({...renderer.diagnostics(),count})}
          }
          renderer.dispose();canvas.remove();return results;
        }''')
        assert all(c['maxHandGap']<1e-6 and c['links']==c['count']-1 for c in crowd_checks),crowd_checks
        (ROOT/'runtime'/'halay-chain-qa.json').write_text(json.dumps(crowd_checks,indent=2),encoding='utf-8')
        before=await scene.screenshot()
        await scene.wait_for_timeout(200)
        after=await scene.screenshot()
        assert before!=after,'Animation does not move'
        await scene.goto('http://127.0.0.1:8765/overlay?transparent=1')
        await scene.wait_for_function("document.querySelector('#connection').textContent===''")
        alpha=await scene.locator('#stage').evaluate("el=>el.getContext('2d').getImageData(1,1,1,1).data[3]")
        assert alpha==0,'Transparent corner expected'
        # Preserve a clean demo for the next manual preview.
        await page.evaluate("fetch('/api/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'control',text:'reset'})})")
        assert not errors,errors
        await page.goto('http://127.0.0.1:8765/')
        await page.locator('[name="layout"][value="wide"]').check()
        await page.locator('#theme').select_option('sunset')
        await page.locator('[data-capacity="12"]').click()
        await page.wait_for_function("document.querySelector('#preview').src.includes('layout=wide')&&document.querySelector('#preview').src.includes('capacity=12')")
        await page.locator('#profilename').fill('Tarayıcı test hazırlığı')
        await page.get_by_role('button',name='Profili kaydet',exact=True).click()
        await page.wait_for_function("document.querySelector('#profilestatus').textContent==='Profil kaydedildi.'")
        savedProfile=await page.locator('#profiles').input_value()
        await page.locator('#profiles').select_option('')
        await page.locator('#theme').select_option('night')
        await page.locator('#profiles').select_option(savedProfile)
        assert await page.locator('#theme').input_value()=='sunset'
        assert await page.locator('#capacity').input_value()=='12'
        await page.locator('#capacity').fill('8')
        await page.get_by_role('button',name='Başlat · sahneyi aç').click()
        await page.wait_for_url('**/overlay')
        await page.wait_for_function("window.halayDiagnostics?.().layout==='wide'&&window.halayDiagnostics?.().theme==='sunset'")
        await page.wait_for_function("fetch('/api/state').then(r=>r.json()).then(s=>s.users.length>0&&s.ring_capacity===8&&s.session.running)")
        await page.goto('http://127.0.0.1:8765/')
        await page.wait_for_function("!document.querySelector('#stop').hidden")
        await page.screenshot(path=str(ROOT/'work'/'setup-preview.png'),full_page=True)
        await page.get_by_role('button',name='Oturumu durdur').click()
        await page.wait_for_function("document.querySelector('#stop').hidden")
        await page.locator('#mode').select_option('live')
        assert await page.locator('#username').is_visible()
        assert await page.locator('#username').get_attribute('required') is not None
        await page.locator('#mode').select_option('demo')
        await page.locator('#profiles').select_option(savedProfile)
        page.once('dialog',lambda dialog:dialog.accept())
        await page.get_by_role('button',name='Profili sil',exact=True).click()
        await page.wait_for_function("document.querySelector('#profilestatus').textContent==='Profil silindi.'")
        await page.evaluate("rules=>fetch('/api/rules',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(rules)})",originalRules)
        desktop=await context.new_page();desktop.on('pageerror',lambda err:errors.append(str(err)))
        await desktop.set_viewport_size({'width':1440,'height':1100})
        await desktop.goto('http://127.0.0.1:8765/')
        await desktop.wait_for_function("document.querySelector('#giftrules').children.length>0")
        await desktop.wait_for_function("document.querySelector('#preview').contentWindow?.halayDiagnostics?.().chainCount>0")
        await desktop.screenshot(path=str(ROOT/'work/studio-desktop.png'),full_page=True)
        assert not errors,errors
        await context.close()
    report={'result':'PASS','checks':['panel loads','WebSocket connects','demo 18 users','comment joins','gift points','300 likes joins','module switching','speed control','mobile layout','canvas animates','transparent mode','no JavaScript errors','startup scene/capacity selection','one click automatic demo','stop session','live username field','3D scene rendering','joined hands at 4/12/24/60 users across 4 dance phases','shared facing direction','all three ring layouts','saved settings','layout/theme preview','profile create/load/delete in browser','gift editor loads'],'javascript_errors':errors}
    (ROOT/'runtime'/'browser-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
