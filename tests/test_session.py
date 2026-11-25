import unittest,time
from unittest.mock import AsyncMock,patch
from types import SimpleNamespace
from fastapi.testclient import TestClient
from server import app
from engine import Engine

class SessionFlow(unittest.TestCase):
    def test_automatic_demo_start_stop_and_capacity(self):
        with TestClient(app,base_url='http://127.0.0.1:8765') as client:
            r=client.post('/api/session/start',json={'mode':'demo','scene':'orbit','capacity':4})
            self.assertEqual(r.status_code,200)
            for _ in range(30):
                s=client.get('/api/state').json()
                if s['users']: break
                time.sleep(.02)
            self.assertTrue(s['session']['running'])
            self.assertEqual(s['scene'],'orbit')
            self.assertEqual(s['ring_capacity'],4)
            self.assertTrue(s['users'],'Automatic demo must generate an event without operator input')
            for i in range(8):
                r=client.post('/api/event',json={'type':'comment','user_id':'test'+str(i),'name':str(i),'text':'halay'})
                self.assertEqual(r.status_code,200)
            s=client.get('/api/state').json()
            self.assertEqual(sum(u['joined'] for u in s['users']),4)
            self.assertEqual(s['queued'],len(s['users'])-4)
            client.post('/api/event',json={'type':'control','text':'remove','user_id':s['users'][0]['id']})
            s=client.get('/api/state').json()
            self.assertEqual(sum(u['joined'] for u in s['users']),4)
            self.assertEqual(s['queued'],len(s['users'])-4)
            client.post('/api/event',json={'type':'control','text':'reset'})
            s=client.get('/api/state').json()
            self.assertEqual(s['ring_capacity'],4)
            self.assertEqual(s['scene'],'orbit')
            self.assertEqual(client.post('/api/session/stop',json={}).status_code,200)
            self.assertFalse(client.get('/api/state').json()['session']['running'])
    def test_live_launches_owned_listener_without_external_network_in_test(self):
        child=SimpleNamespace(returncode=0)
        with TestClient(app,base_url='http://127.0.0.1:8765') as client:
            with patch('server.asyncio.create_subprocess_exec',new_callable=AsyncMock,return_value=child) as spawn:
                r=client.post('/api/session/start',json={'mode':'live','scene':'halay','capacity':12,'username':'@example'})
                self.assertEqual(r.status_code,200,r.text)
                self.assertEqual(r.json()['session']['username'],'example')
                spawn.assert_awaited_once()
                args,kw=spawn.call_args
                self.assertEqual(args[-1],'example')
                self.assertTrue(kw['env']['TEMP'].startswith('D:'))
                self.assertEqual(client.post('/api/session/stop',json={}).status_code,200)
    def test_rejects_missing_username_and_bad_settings(self):
        with TestClient(app,base_url='http://127.0.0.1:8765') as client:
            for settings in [{'mode':'live','capacity':12}, {'mode':'demo','capacity':2}, {'mode':'demo','capacity':121}, {'mode':'live','username':'bad name'}, {'scene':'cenaze'}]:
                self.assertEqual(client.post('/api/session/start',json=settings).status_code,422)
            self.assertEqual(client.post('/api/session/start',json={'mode':'demo'},headers={'Origin':'https://untrusted.example'}).status_code,403)

class SceneOptions(unittest.TestCase):
    def test_layout_theme_and_quality_follow_session(self):
        with TestClient(app,base_url='http://127.0.0.1:8765') as client:
            for layout in ['circle','arc','wide','line']:
                r=client.post('/api/session/start',json={'mode':'demo','capacity':12,'layout':layout,'theme':'sunset','quality':'high'})
                self.assertEqual(r.status_code,200,r.text)
                state=client.get('/api/state').json()
                self.assertEqual((state['layout'],state['theme'],state['quality']),(layout,'sunset','high'))
                client.post('/api/session/stop',json={})
            for setting in [{'layout':'spiral'},{'theme':'bad'},{'quality':'ultra'}]:
                self.assertEqual(client.post('/api/session/start',json=setting).status_code,422)
    def test_saved_settings_survive_a_fresh_read(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from server import ROOT
        with TemporaryDirectory(dir=ROOT/'work') as directory:
            with patch('server.SETTINGS_PATH',Path(directory)/'settings.json'):
                with TestClient(app,base_url='http://127.0.0.1:8765') as client:
                    selected={'mode':'demo','capacity':36,'layout':'wide','theme':'sunset','quality':'high'}
                    self.assertEqual(client.post('/api/settings',json=selected).status_code,200)
                with TestClient(app,base_url='http://127.0.0.1:8765') as client:
                    saved=client.get('/api/settings').json()
                    self.assertTrue(all(saved[k]==v for k,v in selected.items()))
                    self.assertEqual(client.post('/api/settings',json={'capacity':999}).status_code,422)
