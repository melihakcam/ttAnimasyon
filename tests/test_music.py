import unittest,json,wave,array,math
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from server import app,ROOT

class MusicSettings(unittest.TestCase):
    def test_music_controls_follow_session_and_persist(self):
        with TemporaryDirectory(dir=ROOT/'work') as directory,patch('server.SETTINGS_PATH',Path(directory)/'settings.json'):
            with TestClient(app,base_url='http://127.0.0.1:8765') as client:
                result=client.post('/api/session/start',json={'mode':'demo','capacity':8,'music':'drum','volume':22})
                self.assertEqual(result.status_code,200)
                state=client.get('/api/state').json()
                self.assertEqual((state['music'],state['volume']),('drum',22))
                self.assertEqual(client.post('/api/audio',json={'music':'off','volume':0}).status_code,200)
                state=client.get('/api/state').json();self.assertEqual((state['music'],state['volume']),('off',0))
                saved=client.get('/api/settings').json();self.assertEqual((saved['music'],saved['volume']),('off',0))
                for settings in [{'music':'bad'},{'volume':101},{'volume':-1}]:
                    self.assertEqual(client.post('/api/audio',json=settings).status_code,422)
                self.assertEqual(client.post('/api/audio',json={'volume':50},headers={'Origin':'https://example.com'}).status_code,403)
                client.post('/api/session/stop',json={})
    def test_generated_loops_are_non_silent_and_match_beats(self):
        metadata=json.loads((ROOT/'app/audio/music.json').read_text(encoding='utf-8'))
        target=metadata['beats']*60/metadata['bpm']
        for name in ['meydan-halay-112.wav','davul-112.wav']:
            with wave.open(str(ROOT/'app/audio'/name),'rb') as audio:
                self.assertEqual((audio.getnchannels(),audio.getsampwidth(),audio.getframerate()),(2,2,44100))
                self.assertAlmostEqual(audio.getnframes()/audio.getframerate(),target,places=5)
                samples=array.array('h',audio.readframes(audio.getnframes()))[::97]
            self.assertLess(max(abs(value) for value in samples),32767)
            self.assertGreater(math.sqrt(sum(value*value for value in samples)/len(samples)),500)
