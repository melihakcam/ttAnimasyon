from pathlib import Path
r=Path(r'D:\tiktokAnimasyon')
p=r/'engine.py';s=p.read_text(encoding='utf-8').replace("if action == 'reset':\n                self.reset()", "if action == 'reset':\n                old_scene,old_capacity,old_source=self.scene,self.ring_capacity,self.source\n                self.reset()\n                self.scene,self.ring_capacity,self.source=old_scene,old_capacity,old_source");p.write_text(s,encoding='utf-8')
(r/'tests/test_session.py').write_text(r'''import unittest,time
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
            for settings in [{'mode':'live','capacity':12}, {'mode':'demo','capacity':2}, {'mode':'demo','capacity':61}, {'mode':'live','username':'bad name'}, {'scene':'cenaze'}]:
                self.assertEqual(client.post('/api/session/start',json=settings).status_code,422)
            self.assertEqual(client.post('/api/session/start',json={'mode':'demo'},headers={'Origin':'https://untrusted.example'}).status_code,403)
''',encoding='utf-8')
# Extend visual checks with the one-click launch workflow. Keep a full-screen screenshot after automatic arrivals.
p=r/'tests/browser_qa.py';s=p.read_text(encoding='utf-8').replace("        await context.close()", """        await page.goto('http://127.0.0.1:8765/')
        await page.locator('#capacity').fill('8')
        await page.get_by_role('button',name='Başlat · sahneyi aç').click()
        await page.wait_for_url('**/overlay')
        await page.wait_for_function(\"fetch('/api/state').then(r=>r.json()).then(s=>s.users.length>0&&s.ring_capacity===8&&s.session.running)\")
        await page.goto('http://127.0.0.1:8765/')
        await page.wait_for_function(\"!document.querySelector('#stop').hidden\")
        await page.screenshot(path=str(ROOT/'work'/'setup-preview.png'),full_page=True)
        await page.get_by_role('button',name='Oturumu durdur').click()
        await page.wait_for_function(\"document.querySelector('#stop').hidden\")
        await page.locator('#mode').select_option('live')
        assert await page.locator('#username').is_visible()
        assert await page.locator('#username').get_attribute('required') is not None
        assert not errors,errors
        await context.close()""")
s=s.replace("'no JavaScript errors'", "'no JavaScript errors','startup scene/capacity selection','one click automatic demo','stop session','live username field'")
p.write_text(s,encoding='utf-8')
# Document the new primary flow; preserve original optional manual listener steps for debugging.
p=r/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('3. **Demo katılımcıları** düğmesine bas: 18 isimli karakter, sıralama ve davulcu görünür.', '3. Girişte **Halay meydanı** veya **Çember dansı** seç; halkadaki kişi sayısını 4–60 arasında ayarla.\n4. **Otomatik demo** seçip **Başlat** düğmesine bas: örnek katılımcılar iki saniyede bir kendiliğinden gelir. Ekran doğrudan tam yayın sahnesine geçer.\n5. Gerçek yayın için girişte **Gerçek TikTok yayını** seç, kullanıcı adını yaz, **Başlat** de. Dinleyici otomatik açılır; yorum/hediye/beğeni olayları katılımcıları getirir. Gerçek yayının açık olması gerekir.\n6. Oturumu durdurmak veya değiştirmek için http://127.0.0.1:8765 adresine dön. Yeni oturum mevcut katılımcıları ve puanları sıfırlar.\n\nAyrıntılı test paneli artık **http://127.0.0.1:8765/panel** adresindedir. İstersen orada **Demo katılımcıları** ile 18 örneği tek seferde ekleyebilirsin.\n\nTest panelindeki seçenekler:')
s=s.replace('4. Yorum gönder:', '- Yorum gönder:').replace('5. `kız`','- `kız`').replace('6. Hediye veya beğeni','- Hediye veya beğeni').replace('7. Animasyon modülünü','- Animasyon modülünü')
s=s.replace('## Gerçek TikTok bağlantısı — isteğe bağlı', '''## Halka kapasitesi ve otomatik akış

Seçilen sayı aktif sahne katılımcısı sınırıdır; kullanıcılar gelmeden sahte canlı katılımcı üretilmez. Sınır dolunca yeni katılanlar sıraya alınır. Aktif biri test panelinden çıkarılınca sıradaki kişi otomatik alınır. Şu anda otomatik süre dolması/katılımcı çıkarma yoktur; dolu halka kendiliğinden dönüştürülmez. Toplam kayıt sınırı config.json içindeki max_users (varsayılan 60), görünür katılımcı sınırından ayrıdır. Aktif+sıradaki kayıtlar bu üst sınıra ulaşırsa yeni kimlikler alınamaz; mevcut kullanıcıların olayları işlemeye devam eder. Bu doluluk davranışı, kullanıcının anlattığı başlangıç akışını tamamlamak için seçilen varsayımdır; referans videoda doğrulanmadı.

İlk girişte seçim yapılır; Başlat sonrasında test paneline dokunmak gerekmez. Demo kendiliğinden örnek olay üretir, canlı mod yalnızca gerçek TikTok olaylarını kullanır. TikTok dinleyicisini bu sürümde başlangıç ekranı yönetir; aynı anda TIKTOK_BAGLAN.cmd açma, çift dinleyici olayları tekrarlayabilir. Kontrol ekranındaki yerel bağlantı durumu TikTok'a bağlanıldığı anlamına gelmez; TikTok bağlı durumunu ayrıca kontrol et.

Cenaze sahnesi bu sürümde yoktur. Menüde yalnızca çalışan iki dans modülü vardır. Ses henüz eklenmemiştir.\n
## Gerçek TikTok bağlantısı — isteğe bağlı''')
s=s.replace('2. **TIKTOK_BAGLAN.cmd** aç ve yayında olan hesabın kullanıcı adını gir. Şifre istemez.', '2. Giriş ekranında **Gerçek TikTok yayını** seç, kullanıcı adını yazıp Başlat de. Şifre istemez. Alternatif manuel hata ayıklama yolu olarak TIKTOK_BAGLAN.cmd kullanılabilir; otomatik oturumla eşzamanlı çalıştırma.')
p.write_text(s,encoding='utf-8')
p=r/'VIDEO_ANALIZI.md';s=p.read_text(encoding='utf-8')+'''\n## Sonradan açıklanan başlangıç akışı\n\nKullanıcı, gördüğü sistemde girişte sahne ve halka kişi sayısı seçilip Başlat denildikten sonra katılımcıların otomatik geldiğini açıkladı. Bu bilgi kullanıcı anlatımına dayanır; kısa kayıt giriş ekranını göstermiyor. Prototipe sahne/kapasite/mod/hesap seçimi, tek düğmeyle dinleyici başlatma ve tam sahneye geçiş eklendi. Kapasite dolunca sıraya alma davranışı varsayımdır. Sadece canlı yayına giriş yapan herkesi otomatik katılımcı yapma eklenmedi; yorum, hediye veya beğeni eşiğiyle katılım devam eder.\n''';p.write_text(s,encoding='utf-8')
print('Session checks and instructions updated.')
