from pathlib import Path
r=Path(r'D:\tiktokAnimasyon')
(r/'tests/test_studio.py').write_text(r'''import unittest,json,copy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from fastapi.testclient import TestClient
import server

class StudioPreparation(unittest.TestCase):
    def setUp(self):
        self.directory=TemporaryDirectory(dir=server.ROOT/'work')
        self.original=copy.deepcopy(server.engine.config)
        self.patches=[patch('server.CONFIG_PATH',Path(self.directory.name)/'config.json'),patch('server.PROFILES_PATH',Path(self.directory.name)/'profiles.json')]
        for p in self.patches:p.start()
        self.client=TestClient(server.app,base_url='http://127.0.0.1:8765');self.client.__enter__()
    def tearDown(self):
        self.client.__exit__(None,None,None)
        server.engine.config.clear();server.engine.config.update(self.original)
        for p in reversed(self.patches):p.stop()
        self.directory.cleanup()
    def rules(self):return {'bpm':130,'like_threshold':42,'gifts':[{'name':'Flower','gift_id':11,'action':'speed','points':8}]}
    def test_rules_are_persisted_and_drive_gift_events(self):
        self.assertEqual(self.client.post('/api/rules',json=self.rules()).status_code,200)
        self.assertEqual(json.loads(server.CONFIG_PATH.read_text())['base_bpm'],130)
        self.assertEqual(self.client.get('/api/rules').json()['like_threshold'],42)
        self.client.post('/api/event',json={'type':'comment','user_id':'rules-qa','name':'QA','text':'halay'})
        self.client.post('/api/event',json={'type':'gift','user_id':'rules-qa','name':'QA','gift_id':11,'count':2})
        self.assertEqual(server.engine.users['rules-qa']['points'],16)
        self.assertGreater(server.engine.speed_until,0)
    def test_invalid_or_duplicate_rules_are_rejected(self):
        for rules in [{'bpm':999,'gifts':[{'name':'A'}]}, {'gifts':[]}, {'gifts':[{'name':'A','points':-1}]}, {'gifts':[{'name':'A'},{'name':'A'}]}, {'gifts':[{'name':'A','gift_id':1},{'name':'B','gift_id':1}]}]:
            self.assertEqual(self.client.post('/api/rules',json=rules).status_code,422)
        self.assertFalse(server.CONFIG_PATH.exists())
    def test_profile_create_update_reload_delete(self):
        body={'name':'Akşam halayı','settings':{'capacity':36,'layout':'wide','theme':'sunset'},'rules':self.rules()}
        result=self.client.post('/api/profiles',json=body)
        self.assertEqual(result.status_code,200,result.text)
        value=result.json();self.assertTrue(value['id'])
        self.assertEqual(self.client.get('/api/profiles').json()[0]['settings']['capacity'],36)
        value['name']='Gece halayı';value['settings']['layout']='line'
        self.assertEqual(self.client.post('/api/profiles',json=value).status_code,200)
        saved=json.loads(server.PROFILES_PATH.read_text())
        self.assertEqual(len(saved),1);self.assertEqual(saved[0]['settings']['layout'],'line')
        self.assertEqual(self.client.delete('/api/profiles/'+value['id']).status_code,200)
        self.assertEqual(self.client.get('/api/profiles').json(),[])
    def test_profile_mutations_reject_foreign_origin(self):
        self.assertEqual(self.client.post('/api/profiles',json={'name':'Test','settings':{}},headers={'Origin':'https://example.com'}).status_code,403)
        self.assertEqual(self.client.delete('/api/profiles/missing',headers={'Origin':'https://example.com'}).status_code,403)
''',encoding='utf-8')
p=r/'tests/browser_qa.py';s=p.read_text(encoding='utf-8')
s=s.replace("        await page.wait_for_function(\"document.querySelector('#connection').textContent.includes('Bağlı')\")", "        await page.wait_for_function(\"document.querySelector('#connection').textContent.includes('Bağlı')\")\n        originalRules=await page.evaluate(\"fetch('/api/rules').then(r=>r.json())\")")
s=s.replace("        await page.locator('#capacity').fill('8')", """        await page.locator('#profilename').fill('Tarayıcı test hazırlığı')
        await page.get_by_role('button',name='Profili kaydet',exact=True).click()
        await page.wait_for_function("document.querySelector('#profilestatus').textContent==='Profil kaydedildi.'")
        savedProfile=await page.locator('#profiles').input_value()
        await page.locator('#profiles').select_option('')
        await page.locator('#theme').select_option('night')
        await page.locator('#profiles').select_option(savedProfile)
        assert await page.locator('#theme').input_value()=='sunset'
        assert await page.locator('#capacity').input_value()=='12'
        await page.locator('#capacity').fill('8')""")
s=s.replace("        assert not errors,errors\n        await context.close()", """        await page.locator('#mode').select_option('demo')
        await page.locator('#profiles').select_option(savedProfile)
        page.once('dialog',lambda dialog:dialog.accept())
        await page.get_by_role('button',name='Profili sil',exact=True).click()
        await page.wait_for_function("document.querySelector('#profilestatus').textContent==='Profil silindi.'")
        await page.evaluate("rules=>fetch('/api/rules',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(rules)})",originalRules)
        desktop=await context.new_page();desktop.on('pageerror',lambda err:errors.append(str(err)))
        await desktop.set_viewport_size({'width':1440,'height':1100})
        await desktop.goto('http://127.0.0.1:8765/')
        await desktop.wait_for_function("document.querySelector('#giftrules').children.length>0")
        await desktop.screenshot(path=str(ROOT/'work/studio-desktop.png'),full_page=True)
        assert not errors,errors
        await context.close()""")
s=s.replace("'layout/theme preview'", "'layout/theme preview','profile create/load/delete in browser','gift editor loads'")
p.write_text(s,encoding='utf-8')
print('General studio tests ready.')
