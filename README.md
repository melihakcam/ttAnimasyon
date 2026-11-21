# Halay Stüdyo

Yerel bilgisayarda çalışan, hazırlık yapıp profil seçerek başlatabileceğin TikTok etkileşim stüdyosu. Bütün proje, bağımlılıklar, geçici dosyalar, profiller ve stüdyo tarayıcı verileri D:\tiktokAnimasyon içindedir. Mevcut Python/Edge/Chrome uygulamaları kurulu yerlerinden okunur; Windows ve OBS kendi kayıtlarını kendi ayarlarına göre tutar.

## Aç ve hazırla

1. **BASLAT.cmd** dosyasını çift tıkla. Sunucu açılır ve hazırlık ekranı ayrı bir stüdyo penceresinde gelir. Tekrar açarsan aynı sunucu kullanılır. Pencereyi kapatmak sunucuyu durdurmaz.
2. **Kayıtlı hazırlıklarım** bölümünden bir profil seç veya yeni hazırlık yap.
3. Sahne modülünü seç: **Halay meydanı** veya **Ritmik halay**.
4. Düzeni seç: **Halka** (varsayılan, referans videodaki gibi), **Yay**, **Geniş yay**, **Sıra**. Hepsi el ele ve ortak ritimdedir. Halkada herkes ortaya dönük, kollar yukarıda; az kişide halka arkadan dolmaya başlar, yeterli kişi gelince kapanır ve yavaşça döner. Kamera halkanın ön kenarının üstündedir; ortada minder, solda Zurnacı, sağda Nağaracı kürsüsü vardır.
   - **Zurnacı**: "Zurnacı olsun" davranışlı hediye (varsayılan: Zurna, Finger Heart). **Nağaracı**: "Nağaracı olsun" davranışlı hediye (Drum, Davul). Rol sahipleri halka doluyken de sahneye alınır.
5. Kişi sayısını **4–60** arasında seç. Sağdaki örnek önizleme, gerçek oturumdan bağımsızdır.
6. **Gece / Gün batımı** ışığını ve **Dengeli / Yüksek** kaliteyi seç. Zayıf ekran kartında dengeli kullan.
7. **Hediye ve katılım kuralları** bölümünde dans hızını (60–220 BPM), katılım beğeni eşiğini, hediye adı/kimliği → davranış/puan eşleşmelerini düzenle. Hediye davranışları: katıl, hızlandır, davulcu, konfeti. En fazla 40 kural; tanınmayan hediye varsayılan 1 puanla katılım sağlar.
8. Hazırlığına isim verip **Profili kaydet** de. En fazla 20 profil tutulur. Seçili profili tekrar kaydetmek onu günceller. Yeni bir kopya için listeden Yeni hazırlık seçip yeni isimle kaydet. Profil yüklemek canlı sahneyi değiştirmez; **Başlat** ayarları uygular.
9. Hesapsız denemek için **Otomatik demo** seç. Gerçek TikTok için canlı yayının açıkken **Gerçek TikTok yayını** seçip kullanıcı adını gir.
10. **Başlat** ile sahne açılır; kişiler olaylarla otomatik gelir. Demo iki saniyede bir örnek olay üretir. Gerçek modda örnek kişi üretilmez.

Hazırlık adresi: http://127.0.0.1:8765
Ayrıntılı test paneli: http://127.0.0.1:8765/panel
Yayın sahnesi: http://127.0.0.1:8765/overlay

**Oturumu durdur**, demo veya TikTok olay akışını durdurur; son sahne ve sunucu açık kalır. **DURDUR.cmd**, sunucuyu ve sahip olduğu TikTok dinleyicisini kapatır.

## Ne saklanır?

- Son başlangıç ayarları: runtime/settings.json.
- İsimli profiller: runtime/profiles.json. Sahne/düzen/kapasite/ışık/kalite/hesap ve hediye kuralları birlikte saklanır.
- Uygulanan hediye, hız ve beğeni kuralları: config.json.
- Aktif katılımcı/puan/sıra: bellekte. Yeni oturum veya sunucunun kapanması bunları sıfırlar.
- Yerel sunucu ve TikTok günlükleri: runtime/ altında.

Başlangıç örnekleri: Halay 12 kişi, Halay 24 kişi, Sıra 16 kişi. Bunları değiştirebilir veya kendi profillerini kaydedebilirsin. Günlük kullanım için kod düzenlemen gerekmez.

## Katılım ve halka doluluğu

Yorum yapan, hediye gönderen veya kişi başına beğeni eşiğine ulaşan kullanıcı katılır. Aynı kullanıcı kimliği aynı kişiyi günceller; görünen ad kimlik yerine geçmez. “kız / qız / erkek / oğlan” kıyafeti değiştirir. Ayrıntılı hayvan modelleri bu 3B sürümde hazır değildir.

Seçilen kişi sayısı aktif katılımcı üst sınırıdır; davulcu da buna dahildir. Halka dolunca yeni katılanlar sıraya alınır. Test panelinden aktif biri çıkarılınca sıradaki otomatik alınır. Süre dolmasıyla otomatik çıkarma yapılmaz. Toplam izlenen kimlik sınırı config.json içindeki max_users (varsayılan 60); aktif ve sıradakilerin toplamı bu sınıra ulaşınca yeni kimlikler kabul edilmez. Mevcut kişilerin olayları işlemeye devam eder.

## Gerçek TikTok

Bağımlılık kurulu. Başka bilgisayarda önce KUR.cmd, isteğe bağlı canlı bağlantı için TIKTOK_KUR.cmd çalıştırılır. Python 3.10+ gerekir. Hazırlık ekranında kullanıcı adı girilip Başlat denince dinleyici otomatik açılır. Hesabın yayında olması gerekir. Şifre istemez. Aynı anda TIKTOK_BAGLAN.cmd açma; bu dosya yalnızca manuel hata ayıklama içindir.

TikTokLive 7.0.1 üçüncü taraf kütüphanedir. Gerçek hesapta uçtan uca bağlantı henüz denenmedi. TikTok değişiklikleri, erişim/imza servisleri veya bölgesel kısıtlar bağlantıyı etkileyebilir. Yerel demo internet gerektirmez; canlı bağlantı internet gerektirir. Kaynak durumu TikTok bağlı demeden yalnızca yerel sunucunun bağlı olması yeterli değildir. Hatalar runtime/tiktok.log içindedir. Dinleyici kapanırsa hazırlık ekranındaki durum güncellenir.

Hediye serilerinde ara mesajlar atlanır, son repeat_count toplamı sayılır. order_id varsa tekrar teslimat önlenir; son 4000 kimlik bellekte tutulur. Dinleyici kuyruğu 1000 olayla sınırlı; gönderilemeyen olaylar loga yazılır, diske kaydedilip yeniden oynatılmaz. Oyun puanları gerçek para/ödül muhasebesi değildir. Dinleyici TikTok profil fotoğrafını (HTTPS) aktarır; fotoğraf gelmezse baş harfler gösterilir.

Kaynaklar:
- https://github.com/isaackogan/TikTokLive
- https://ttl.docs.isaackogan.com/guides/gifts/

## OBS

1. Kaynaklar → + → **Tarayıcı**. Yerel dosya kapalı.
2. URL: **http://127.0.0.1:8765/overlay**. Genişlik 1080, yükseklik 1920, 30 FPS.
3. Kontrol ekranını değil yalnızca bu sahneyi yayına ekle. URL hazırlık ekranında kopyalanabilir.
4. İstenirse saydam zemin: http://127.0.0.1:8765/overlay?transparent=1
5. Kaynak görünür olmadığında kapatma seçeneğini kapalı tut. Yenilemede güncel durum WebSocket ile tekrar gelir.

Bu sürümde özgün sentetik davul-zurna müziği ve yalnız davul seçeneği bulunur. Müzik doğrudan tarayıcı kaynağından çalar; ayrıca Medya Kaynağı eklemek gerekmez. Görüntüyü TikTok'a göndermek için hesabında kullanılabilen OBS/LIVE Studio yayın yöntemi ayrıca kurulmalıdır; dinleyici görüntüyü yayınlamaz.

OBS kaynakları: https://obsproject.com/kb/browser-source ve https://obsproject.com/kb/media-sources

## Görseller ve genişletme

Karakterler prosedürel 3B; ince-uzun oranlar, yere kadar uzun elbiseler, uzun saç, sikke alınlık, loş fener ışığı, geleneksel kıyafet işlemeleri, halay başının mendili, davul, halı, minder, fener, taş meydan, sıcak/soğuk ışık ve gölgeler var. Ortak el hedefleri ve eşzamanlı adımlar zinciri korur. Stilize modellerdir; referans videodaki özgün varlıkların kopyası değildir.

Çalışan iki halay hareket modülü vardır. Cenaze gibi başka temalı karakter/sahne modülleri henüz eklenmedi. Yeni profil kaydetmek yeni karakter modeli üretmez. Yeni animasyonlar aynı olay ve profil yapısına kod/varlık eklenerek genişletilebilir.

- engine.py: kullanıcılar, puanlar, sıra ve hediye kuralları.
- server.py: yerel HTTP/WebSocket, profil/ayar yönetimi ve dinleyici yaşam döngüsü.
- app/halay3d.js: Three.js karakterler, yerleşim ve hareket.
- app/scene.js: isimler, profil halkaları ve yayın göstergeleri.
- app/setup.*: genel hazırlık stüdyosu.
- tiktok_listener.py: isteğe bağlı gerçek olay köprüsü.
- launcher.py: tek tıkla başlat/durdur.

Three.js 0.170.0, app/vendor altında yerel olarak bulunur; MIT lisansı aynı klasörde. Yayın sırasında CDN gerekmez. WebGL 2 destekli tarayıcı ve grafik hızlandırması gerekir. Ekran kartına bağlı olarak 60 kişi ve yüksek kalite ağır gelebilir.

## Doğrulama

DURDUR.cmd sonrasında TEST.cmd çalıştır. Başka makinede test araçları requirements-dev.txt ile kurulmalı ve Microsoft Edge bulunmalıdır. Test profili/ekran görüntüleri work/, raporlar runtime/ altındadır.

21 kural/oturum/profil/müzik testi, HTTP/WebSocket, kayıtlı hazırlık yükleme/silme, hediye düzenleyici, önizleme, mobil görünüm ve 3 halka düzeni tarayıcıda doğrulandı. 4/12/24/60 kişide dörder hareket anında el bağlantıları ölçüldü. Canlı TikTok hesabına ve OBS'den gerçek yayına uçtan uca test yapılmadı.

API: /api/audio, /api/state, /api/event, /api/settings, /api/rules, /api/profiles, /api/session/start, /api/session/stop. WebSocket: /ws. Sunucu sadece 127.0.0.1:8765 dinler. Giriş sistemi yoktur; yerel portu internete açma.

## Müzik ve dans

Hazırlık ekranında Müzik bölümünden **Meydan Halayı · davul ve zurna**, **Yalnız davul** veya **Sessiz** seç. **Ritmi dinle** ile oturum açmadan deneyebilirsin; tekrar basınca durur. Ses seviyesi yüzdeyle ayarlanır. Müzik seçimi ve seviye hazırlık profiline kaydedilir; açık oturumda bu iki alan değişince yayın sahnesine hemen uygulanır. Yerleşik görsel önizleme daima sessizdir.

Meydan Halayı bu proje için sıfırdan sentezlendi. Hicaz renkli özgün kısa ezgiler, 2/4 halay yürüyüşüne uygun davul vurguları ve küçük geçişler içerir. Gerçek bir müzisyenin kaydı değildir; dış şarkı, kayıt veya sample kullanılmadı. Temel hız **112 BPM**, 128 vuruşluk döngü yaklaşık **68.57 saniye**. Aynı uzunlukta davul sürümü de vardır. Yerel WAV dosyaları app/audio/ altında; kaynak bilgisi music.json içindedir. Çalışırken internet veya ücretli müzik servisi gerekmez.

Dansın ritim konumu doğrudan çalan sesin saatinden alınır; yavaş çizilen kareler müzikten geri kalmaz. Dans hızı değiştirilirse müzik de aynı oranda değişir. Hızlandırma hediyesi ikisini 1.45 kat hızlandırır. Bu yöntemle sesin perdesi de hızla birlikte değişir; perdeyi sabit tutan zaman esnetme kullanılmaz. Seçim veya sessizden dönüşte döngü yeniden başlayabilir.

Oturum başlayınca müzik çalar; oturum durunca veya yerel bağlantı kesilince durur. Tarayıcı otomatik sesi engellerse sahnede **Sesi aç** düğmesi görünür; bir kez tıkla. OBS'de gerekiyorsa kaynakla Etkileşim/Interact penceresinden aynı düğmeye tıkla. Tarayıcı kaynağı özelliklerindeki **Control audio via OBS / Sesi OBS ile kontrol et** seçeneğiyle sesi OBS mikserine yönlendir, kanalın sessizde olmadığını ve ses göstergesinin hareket ettiğini kontrol et. Kulaklıkla dinleme seçeneği OBS sürümüne göre ayrıca açılır. Aynı sahneyi OBS'de ve ayrı tarayıcı penceresinde aynı anda sesli çalıştırma; çift ses oluşur. OBS Sanal Kamera ile LIVE Studio kullanılırsa sesin ayrıca LIVE Studio'ya aktarılması gerekir.

Ses sinyali, otomatik ses açma düğmesi, dinleme başlat/durdur, müzik/davul geçişi, canlı ses seviyesi, sessiz seçim ve hediye hızlandırması Edge üzerinde ölçülerek doğrulandı. Ses testleri hoparlörden yüksek ses çıkarmamak için test tarayıcısında sessiz çıkışla yürütülür; gerçek ses sinyali Web Audio analizöründen ölçülür. OBS/TikTok'tan gerçek yayın sesi testi halen yapılmadı.

OBS yönlendirme kaynağı: https://github.com/obsproject/obs-studio/issues/7878
