from pathlib import Path
r=Path(r'D:\tiktokAnimasyon')
p=r/'server.py';s=p.read_text(encoding='utf-8').replace('    return await call_next(request)', "    response=await call_next(request)\n    response.headers['Cache-Control']='no-store'\n    return response");p.write_text(s,encoding='utf-8')
for name in ['index.html','overlay.html','setup.html']:
 p=r/'app'/name;s=p.read_text(encoding='utf-8')
 for asset in ['panel.js','scene.js','setup.js','panel.css']:s=s.replace('/assets/'+asset+'"','/assets/'+asset+'?v=2"')
 p.write_text(s,encoding='utf-8')
p=r/'tests/browser_qa.py';s=p.read_text(encoding='utf-8').replace("headless=True,viewport=", "extra_http_headers={'Cache-Control':'no-cache'},headless=True,viewport=");p.write_text(s,encoding='utf-8')
print('Browser cache invalidation fixed.')
