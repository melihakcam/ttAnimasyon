import asyncio,json,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from websockets.asyncio.client import connect

async def main():
    report=[]
    delivery="qa-"+str(uuid.uuid4())
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8765',trust_env=False,timeout=8) as h:
        async def post(payload):
            r=await h.post('/api/event',json=payload);r.raise_for_status();return r.json()
        await post(dict(type='control',text='reset'))
        for path in ['/','/panel','/overlay','/assets/scene.js','/assets/panel.js']:
            r=await h.get(path);assert r.status_code==200,(path,r.status_code)
        report.append('HTTP panel/overlay/assets: PASS')
        async with connect('ws://127.0.0.1:8765/ws',origin='http://127.0.0.1:8765',proxy=None) as ws:
            first=json.loads(await ws.recv());assert first['type']=='state'
            await post(dict(type='comment',user_id='qa',name='<script>alert(1)</script>',text='qız'))
            s=json.loads(await asyncio.wait_for(ws.recv(),3));u=s['users'][0]
            assert u['joined'] and u['costume']=='kız'
            await post(dict(type='gift',user_id='qa',name='QA',gift='Rose',count=7,event_id=delivery))
            s=json.loads(await asyncio.wait_for(ws.recv(),3));assert s['users'][0]['points']==7
            duplicate=await post(dict(type='gift',user_id='qa',gift='Rose',count=7,event_id=delivery))
            assert duplicate['changed']==False
            report.append('WebSocket broadcast + comment/gift + duplicate delivery: PASS')
        async with connect('ws://127.0.0.1:8765/ws',origin='http://127.0.0.1:8765',proxy=None) as ws:
            assert json.loads(await ws.recv())['users'][0]['points']==7
            report.append('New/reconnected client gets current state: PASS')
        r=await h.post('/api/event',json=dict(type='gift',count=-2));assert r.status_code==422
        r=await h.post('/api/event',json=dict(type='control',text='reset'),headers={'Origin':'https://untrusted.example'});assert r.status_code==403
        try:
            async with connect('ws://127.0.0.1:8765/ws',origin='https://untrusted.example',proxy=None):
                raise AssertionError('Bad origin accepted')
        except __import__('websockets').exceptions.InvalidStatus: pass
        report.append('Invalid count + cross-origin HTTP/WebSocket rejected: PASS')
        # Use a fresh client event ID on every run, then restore an empty scene.
        await post(dict(type='control',text='reset'))
    output='\n'.join(report)+'\n'
    (Path(__file__).parents[1]/'runtime'/'integration.txt').write_text(output,encoding='utf-8')
    print(output)

if __name__=='__main__': asyncio.run(main())
