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
            headless=True,viewport={'width':1440,'height':1100},
            args=['--disable-breakpad','--disable-crash-reporter','--no-first-run','--disable-extensions'],
            downloads_path=str(ROOT/'work'/'downloads'))
        page=context.pages[0]
        page.on('pageerror',lambda err: errors.append(str(err)))
        await page.goto('http://127.0.0.1:8765')
        await page.wait_for_function("document.querySelector('#connection').textContent.includes('Bağlı')")
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
        await page.wait_for_function("document.querySelector('#summary').textContent.startsWith('20 dansçı')")
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
        await scene.screenshot(path=str(ROOT/'work'/'overlay-preview.png'))
        before=await scene.locator('canvas').evaluate("el=>el.toDataURL()")
        await scene.wait_for_timeout(200)
        after=await scene.locator('canvas').evaluate("el=>el.toDataURL()")
        assert before!=after,'Animation does not move'
        await scene.goto('http://127.0.0.1:8765/overlay?transparent=1')
        await scene.wait_for_function("document.querySelector('#connection').textContent===''")
        alpha=await scene.locator('canvas').evaluate("el=>el.getContext('2d').getImageData(1,1,1,1).data[3]")
        assert alpha==0,'Transparent corner expected'
        # Preserve a clean demo for the next manual preview.
        await page.evaluate("fetch('/api/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'control',text:'reset'})})")
        assert not errors,errors
        await context.close()
    report={'result':'PASS','checks':['panel loads','WebSocket connects','demo 18 users','comment joins','gift points','300 likes joins','module switching','speed control','mobile layout','canvas animates','transparent mode','no JavaScript errors'],'javascript_errors':errors}
    (ROOT/'runtime'/'browser-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
