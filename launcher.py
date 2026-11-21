"""Start/reuse the local studio and keep browser data inside the project."""
import sys,os,json,time,subprocess
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError
ROOT=Path(__file__).resolve().parent
os.environ['TEMP']=str(ROOT/'work');os.environ['TMP']=str(ROOT/'work');os.environ['PYTHONDONTWRITEBYTECODE']='1'
(ROOT/'work').mkdir(exist_ok=True);(ROOT/'runtime').mkdir(exist_ok=True)
def health():
    try:
        with urlopen('http://127.0.0.1:8765/api/health',timeout=1) as response:
            data=json.load(response)
            return data if 'pid' in data else None
    except (OSError,ValueError): return None

def main():
    if '--stop' in sys.argv:
        if not health(): print('Stüdyo zaten kapalı.');return
        req=Request('http://127.0.0.1:8765/api/shutdown',data=b'{}',headers={'Content-Type':'application/json'})
        with urlopen(req,timeout=10) as response: response.read()
        print('Stüdyo ve TikTok dinleyicisi durduruldu.');return
    if not health():
        with (ROOT/'runtime/server.out.log').open('a',encoding='utf-8') as out,(ROOT/'runtime/server.err.log').open('a',encoding='utf-8') as err:
            child=subprocess.Popen([sys.executable,'-B',str(ROOT/'server.py')],cwd=ROOT,stdout=out,stderr=err,creationflags=0x08000000 if sys.platform=='win32' else 0)
        for _ in range(80):
            if health(): break
            if child.poll() is not None: raise RuntimeError('Stüdyo açılamadı. runtime/server.err.log dosyasına bakın.')
            time.sleep(.15)
        else: raise RuntimeError('Stüdyo başlatılamadı. 8765 bağlantı noktasını kontrol edin.')
    print('Stüdyo hazır: http://127.0.0.1:8765')
    if '--no-browser' in sys.argv: return
    candidates=[Path(os.environ.get('ProgramFiles(x86)',r'C:\Program Files (x86)'))/'Microsoft/Edge/Application/msedge.exe',Path(os.environ.get('ProgramFiles',r'C:\Program Files'))/'Google/Chrome/Application/chrome.exe']
    browser=next((path for path in candidates if path.is_file()),None)
    if browser:
        subprocess.Popen([str(browser),'--user-data-dir='+str(ROOT/'runtime/studio-browser'),'--disk-cache-dir='+str(ROOT/'runtime/studio-cache'),'--no-first-run','--disable-breakpad','--app=http://127.0.0.1:8765/'],cwd=ROOT)
    else: print('Tarayıcıda http://127.0.0.1:8765 adresini açın.')

if __name__=='__main__':
    try: main()
    except Exception as exc: print(str(exc));sys.exit(1)
