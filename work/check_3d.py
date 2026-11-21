import asyncio,os,json
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(r'D:\tiktokAnimasyon')
os.environ['TEMP']=str(R/'work');os.environ['TMP']=str(R/'work')
async def main():
 errors=[]
 async with async_playwright() as p:
  ctx=await p.chromium.launch_persistent_context(str(R/'work/3d-browser-profile'),executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True,viewport={'width':540,'height':960},extra_http_headers={'Cache-Control':'no-cache'},args=['--disable-breakpad','--disable-crash-reporter','--no-first-run','--enable-unsafe-swiftshader'])
  page=ctx.pages[0];page.on('pageerror',lambda e:errors.append(str(e)))
  try:
   await page.goto('http://127.0.0.1:8765/overlay')
   await page.evaluate("fetch('/api/session/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})")
   for cmd in ['reset','demo']:
    await page.evaluate("cmd=>fetch('/api/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'control',text:cmd})})",cmd)
   await page.wait_for_function("window.halayDiagnostics?.().chainCount===17",timeout=60000)
   await page.wait_for_timeout(1000)
   print(await page.evaluate('window.halayDiagnostics()'))
   assert (await page.evaluate('window.halayDiagnostics().maxHandGap'))<1e-6
   await page.screenshot(path=str(R/'work/halay-3d-preview.png'))
   assert not errors,errors
  finally: await ctx.close()
asyncio.run(main())
