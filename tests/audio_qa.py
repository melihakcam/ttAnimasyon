import asyncio,json,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
os.environ['TEMP']=str(ROOT/'work');os.environ['TMP']=str(ROOT/'work')
async def main():
 errors=[];report={}
 async with async_playwright() as p:
  context=await p.chromium.launch_persistent_context(str(ROOT/'work/audio-browser-profile'),executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True,viewport={'width':540,'height':960},extra_http_headers={'Cache-Control':'no-cache'},args=['--disable-breakpad','--disable-crash-reporter','--no-first-run','--enable-unsafe-swiftshader','--mute-audio','--autoplay-policy=user-gesture-required'])
  page=context.pages[0];page.on('pageerror',lambda err:errors.append(str(err)))
  async def post(path,data):
   return await page.evaluate("async ({path,data})=>{const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!response.ok)throw Error(await response.text());return response.json()}",dict(path=path,data=data))
  original=None
  try:
   await page.goto('http://127.0.0.1:8765/')
   original=await page.evaluate("fetch('/api/settings').then(r=>r.json())")
   await post('/api/session/stop',{})
   await page.wait_for_function("document.querySelector('#giftrules').children.length>0")
   await page.locator('#music').select_option('halay')
   await page.locator('#volume').fill('20')
   await page.get_by_role('button',name='Ritmi dinle',exact=True).click()
   await page.wait_for_function("window.studioAudioDiagnostics?.().status==='playing'&&window.studioAudioDiagnostics().rms>.001")
   report['audition']=await page.evaluate('window.studioAudioDiagnostics()')
   await page.locator('#music').select_option('drum')
   await page.wait_for_function("window.studioAudioDiagnostics?.().track==='drum'&&window.studioAudioDiagnostics().status==='playing'")
   await page.get_by_role('button',name='Dinlemeyi durdur',exact=True).click()
   assert (await page.evaluate('window.studioAudioDiagnostics().status'))=='off'
   await post('/api/session/start',{'mode':'demo','capacity':8,'music':'halay','volume':20})
   await page.goto('http://127.0.0.1:8765/overlay')
   await page.wait_for_function("['blocked','playing'].includes(window.halayAudioDiagnostics?.().status)")
   if await page.locator('#audio-unlock').is_visible():await page.locator('#audio-unlock').click()
   await page.wait_for_function("window.halayAudioDiagnostics?.().status==='playing'&&window.halayAudioDiagnostics().rms>.001")
   before=await page.evaluate('window.halayAudioDiagnostics().beats')
   await page.wait_for_timeout(350)
   after=await page.evaluate('window.halayAudioDiagnostics().beats');assert after>before
   await post('/api/event',{'type':'control','text':'speed'})
   await page.wait_for_function("Math.abs(window.halayAudioDiagnostics?.().rate-1.45)<.001")
   await page.wait_for_function("window.halayDiagnostics?.().chainCount>0")
   d=await page.evaluate('window.halayDiagnostics()')
   assert abs(d['phase']*112/60-d['audio']['beats'])<.6,d
   report['synchronized_speed']=d['audio']
   await post('/api/audio',{'music':'drum','volume':12})
   await page.wait_for_function("window.halayAudioDiagnostics?.().track==='drum'&&window.halayAudioDiagnostics().volume===12")
   report['live_controls']=await page.evaluate('window.halayAudioDiagnostics()')
   await post('/api/audio',{'music':'off','volume':0})
   await page.wait_for_function("window.halayAudioDiagnostics?.().status==='off'")
   await post('/api/session/stop',{})
   await page.goto('http://127.0.0.1:8765/overlay?preview=1&capacity=8')
   await page.wait_for_function("window.halayAudioDiagnostics?.().status==='preview-muted'")
   assert not errors,errors
   report.update(result='PASS',checks=['non-silent decoded audio','audition start/stop','drums-only selection','autoplay unlock','audio clock progresses','dance follows audio beat','1.45x gift speed','live track/volume','mute','silent embedded preview'],javascript_errors=errors)
  finally:
   if original:
    try:await post('/api/session/stop',{});await post('/api/settings',original)
    except Exception:pass
   await context.close()
 (ROOT/'runtime/audio-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
