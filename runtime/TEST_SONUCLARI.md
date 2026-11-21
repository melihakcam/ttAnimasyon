# Doğrulama sonucu

- 13 kural/uyumluluk/oturum testi: GEÇTİ.
- HTTP panel, overlay ve tarayıcı kaynakları: GEÇTİ.
- WebSocket olay aktarımı, tekrar teslimat ve yeniden bağlantıda tam durum: GEÇTİ.
- Geçersiz adet ve farklı kaynaklı HTTP/WebSocket isteğinin reddi: GEÇTİ.
- Microsoft Edge ile panelden demo, yorum, hediye, 300 beğeni, animasyon değişimi ve hız kontrolü: GEÇTİ.
- Mobil yatay taşma, hareket eden Canvas ve saydam arka plan: GEÇTİ.
- Tarayıcı JavaScript hatası: 0.
- TikTokLive 7.0.1 gerçek GiftEvent nesnesinde ara seri olayını atlama ve son toplamı sayma: GEÇTİ.
- Gerçek TikTok yayınına bağlantı: DENENMEDİ; hesap kullanıcı adı verilmedi.
- OBS uygulamasında yayın açma: DENENMEDİ; Browser Source URL'si tarayıcıda doğrulandı.

Test sunucusu doğrulama sonunda kapatıldı. BASLAT.cmd ile tekrar açılabilir.

Ekran görüntüleri: work/panel-preview.png, work/panel-mobile.png, work/overlay-preview.png.
Detaylar: integration.txt ve browser-qa.json.

Yeni başlangıç ekranında sahne ve kişi sayısı seçimi, tek düğmeyle otomatik demo, kapasite dolunca sıraya alma, katılımcı çıkınca sıradakini alma ve oturumu durdurma doğrulandı. Gerçek TikTok dinleyicisinin otomatik başlatılması dış bağlantı kurmayan işlem taklidiyle test edildi; canlı yayına uçtan uca bağlantı halen denenmedi.

3B güncelleme: 4/12/24/60 kişide dörder hareket anında ortak el hedefleri ölçüldü, en büyük komşu el farkı 0.000001 dünya biriminin altında. Aynı genel yöne bakış, WebGL çizimi, hareketli görüntü ve saydam görünüm geçti. Ayrıntılı sayısal sonuçlar halay-chain-qa.json içinde.

Genel stüdyo sürümü: 19 kural/oturum/profil testi geçti. Tarayıcıda profil oluşturma, seçip geri yükleme, silme ve hediye düzenleyici doğrulandı. Üç halka biçimi, dört kalabalık ve dört hareket anı için 48 el bağlantısı ölçümü geçti.

Müzikli sürüm: 21 kural/oturum/profil/ses dosyası testi geçti. Gerçek tarayıcıda dinleme, davula geçiş, autoplay düğmesi, ses seviyesi, sessiz, ses saatiyle dans konumu ve 1.45x hediye hızlandırması doğrulandı. Ses sinyali rms değeri sıfırın üzerinde ölçüldü. Rapor: audio-qa.json. OBS/TikTok yayın sesi testi yapılmadı.
