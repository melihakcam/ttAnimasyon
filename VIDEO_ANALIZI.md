# Referans video incelemesi

Kaynak: `Kayıt 2026-11-18 221212.mp4`, 576×960, 30 FPS, 16.47 saniye, ses kanallı. Görsel inceleme 0–14 saniye arasına yayılmış sekiz kare ve 5. saniye tam çözünürlüklü kare üzerinden yapıldı. Konuşmanın tam geçmişi için araç erişimi yoktu; dosya doğrudan D: klasöründen okundu.

## Görüntüde doğrulananlar

- Dikey yayın, kahverengi taş döşeli açık meydan, arkada karanlık alan ve küçük ışıklar.
- Çok sayıda karakter halka/oval halay düzeninde, ortada boşluk. Geleneksel kıyafetler, hareket eden kollar/bacaklar, perspektifle küçülen arka sıra.
- Başların üzerinde beyaz çerçeveli yuvarlak profil fotoğrafları; üzerlerinde kullanıcı isimleri. Bazı kullanıcıların beyaz konuşma balonları var.
- Sol üstte “En iyi dansçılar” başlığı ve beş kişilik sıralama.
- Sağ üstte sarı yay biçiminde gösterge, nota simgesi, “Hızlı” / “Orta” yazıları ve 250 sayısı. 250'nin hız mı, hediye eşiği mi olduğu doğrulanamıyor.
- Ön planda kırmızı döşek/halı alanları ve kırmızı yükselti. Sağ önde “Nağaracı” etiketi ve isimli karakter, solda “Zurnacı” yazısı.
- Alttaki yönerge oyuncak, ahşap, köşeli, ayı, tilki, kedi, tavşan, koyun, penguen seçeneklerinden bahsediyor.
- Alt yazıda “kız / qız / erkek / oğlan” yazınca kıyafetin değişeceği belirtiliyor. “Yorum yaz, yallıya katıl! · ya da 300 beğeni” katılım çağrısı var.

## Kaydın doğrulamadığı, prototipte seçilen davranışlar

- Hediye → karakter/rol/hız/puan eşleşmeleri ve süreleri görülmüyor; config.json içindeki kurallar varsayım.
- Sıralamanın puan hesabı bilinmiyor; prototipte hediye tabanlı oyun puanı.
- 300 beğeni çağrısı görülüyor; bunun kişi başı mı toplam mı olduğu belirsiz. Prototip kişi başı sayar.
- Yorumla katılım çağrısı görülüyor; hangi yorumların kabul edildiği belirsiz. Prototip her yorumu katılım sayar.
- Ayrılma, sıra sınırı, kaybolma süresi, hızın BPM değeri bilinmiyor; prototipte 60 kullanıcı, elle çıkarma, normal 112 BPM ve süreli hızlandırma seçildi.
- Görünen avatarlar gerçek kullanıcı görselleri; prototip varsayılan olarak baş harf kullanır.

## Benzerlik ve kalan farklar

Dikey kompozisyon, oval dans halkası, profil çerçeveleri/isimler, konuşma balonları, ilk beş listesi, hız göstergesi, kırmızı dekor ve önde davulcu alanı yeniden çizildi. Karakterler 2B Canvas ile perspektif ve ritmik hareket kullanıyor; videodaki 3B modellerin kopyası değil. Zurnacı için ayrı oynanabilir rol ve özgün müzik bu sürümde yok. Hayvan kıyafetleri temsili simgeler. Kamera, gerçek fotoğraf/model varlıkları ve ayrıntılı animasyonlar ileride aynı olay yapısına eklenebilir.

Çerçeveler `work/sequence.jpg` ve `work/frame05.png` dosyalarında. Kaynak video değiştirilmedi. Kaydın sesinin müzikal/konuşma analizi yapılmadı, ses projeye eklenmedi.

## Sonradan açıklanan başlangıç akışı

Kullanıcı, gördüğü sistemde girişte sahne ve halka kişi sayısı seçilip Başlat denildikten sonra katılımcıların otomatik geldiğini açıkladı. Bu bilgi kullanıcı anlatımına dayanır; kısa kayıt giriş ekranını göstermiyor. Prototipe sahne/kapasite/mod/hesap seçimi, tek düğmeyle dinleyici başlatma ve tam sahneye geçiş eklendi. Kapasite dolunca sıraya alma davranışı varsayımdır. Sadece canlı yayına giriş yapan herkesi otomatik katılımcı yapma eklenmedi; yorum, hediye veya beğeni eşiğiyle katılım devam eder.

## El ele halay düzeltmesi

Kullanıcı, el ele tutuşulması ve ilk görselin gerçekçilik düzeyinin düşük olması konusunda düzeltme yaptı. Önceki 2B çizim kaldırıldı; üç boyutlu, aynı yöne dönük açık yay zinciri eklendi. Komşu elleri ortak hedefte buluşuyor. Bu, referansın özgün karakter varlıklarının çıkarıldığı anlamına gelmiyor; yeni modeller stilize ve prosedüreldir. Önceki 2B benzerlik notu eski sürümü anlatır.
