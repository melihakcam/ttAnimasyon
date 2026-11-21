import subprocess,sys,time,os
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(r'D:\tiktokAnimasyon')
os.environ['TEMP']=str(ROOT/'work');os.environ['TMP']=str(ROOT/'work');os.environ['PYTHONDONTWRITEBYTECODE']='1'
with (ROOT/'runtime'/'qa-server.log').open('w',encoding='utf-8') as log:
    server=subprocess.Popen([sys.executable,'-B','server.py'],cwd=ROOT,stdout=log,stderr=log)
    try:
        for i in range(60):
            if server.poll() is not None: raise RuntimeError('Server stopped; see qa-server.log')
            try:
                with urlopen('http://127.0.0.1:8765/api/state',timeout=1) as response:
                    if response.status==200: break
            except OSError: time.sleep(.2)
        else: raise RuntimeError('Server not ready')
        for args in [['-m','unittest','discover','-s','tests','-v'],['tests/integration.py'],['work/browser_qa.py']]:
            subprocess.run([sys.executable,'-B',*args],cwd=ROOT,check=True)
    finally:
        server.terminate()
        try: server.wait(timeout=5)
        except subprocess.TimeoutExpired: server.kill()
