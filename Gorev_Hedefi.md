# Görev Hedefi ve Yol Haritası (v2.0)

Bu doküman, NeoMag projesinin mevcut durumunu ve gelecekteki geliştirme hedeflerini tanımlar.

## Mevcut Durum

Proje, temel işlevselliği çalışan, kararlı bir yapıya kavuşturulmuştur:
- Sunucu, `start_server.bat` script'i ile tek adımda, bağımlılıkları otomatik yöneterek başlatılabilmektedir.
- Frontend ve backend arasındaki veri akışı sağlanmış, 3D simülasyon ve temel metrikler arayüzde gösterilmektedir.
- Kimlik doğrulama gibi karmaşık katmanlar kaldırılarak sistem basitleştirilmiştir.

## Gelecek Hedefler

### 1. Kod Kalitesi ve Tutarlılık
- **Görev:** Projeye ESLint (JavaScript) ve flake8 (Python) gibi linter araçlarını entegre etmek.
- **Amaç:** Kodlama hatalarını ve stil tutarsızlıklarını daha yazım aşamasındayken yakalayarak "reaktif" hata ayıklama ihtiyacını azaltmak ve kodun okunabilirliğini artırmak.

### 2. Test Otomasyonu
- **Görev:** `pytest` kullanarak backend'deki kritik iş mantığı (evrim, quadtree, ajan davranışları) için birim (unit) testleri yazmak.
- **Amaç:** Yeni geliştirmelerin mevcut sistemi bozmamasını garanti altına almak ve regresyon hatalarını önlemek.

### 3. Kullanıcı Deneyimi (UX) ve Arayüz (UI) Geliştirmeleri
- **Görev:** İnteraktif grafikleri daha detaylı hale getirmek ve kullanıcıya simülasyonu daha iyi kontrol etme imkanı sunacak yeni arayüz elemanları eklemek.
- **Amaç:** Platformun bilimsel değerini ve kullanılabilirliğini artırmak.

### 4. Dokümantasyon
- **Görev:** Proje dokümantasyonunu (`.md` dosyaları) kodda yapılan her önemli değişiklikle birlikte senkronize ve güncel tutmak.
- **Amaç:** Projenin anlaşılırlığını ve bakımının kolaylığını sağlamak. 