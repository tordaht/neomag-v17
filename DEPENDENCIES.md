# NeoMag Proje Bağımlılıkları ve Sistem Mimarisi

**Versiyon:** 17.1.0  
**Güncelleme Tarihi:** 2025-07-28
**Seri No:** NEOMAG-DEP-002

## 📋 Sistem Gereksinimleri

- **Python:** 3.10+ (önerilen: 3.12)
- **İşletim Sistemi:** Windows (start_server.bat için), Linux/macOS (uyarlanabilir)
- **RAM:** 4GB (önerilen: 8GB+)
- **GPU:** CUDA destekli NVIDIA kartı (CuPy için opsiyonel)

## 🐍 Sunucu Tarafı Bağımlılıklar (Python)

Tüm sunucu tarafı bağımlılıklar `server/requirements.txt` dosyasında yönetilmektedir. Script'imiz bu dosyayı otomatik olarak kullanır.

### Ana Framework ve API
```
fastapi==0.111.1
uvicorn==0.30.3
pydantic==2.8.2
websockets==12.0
```

### Veri İşleme ve Bilimsel Hesaplama
```
numpy==1.26.4
pandas==2.2.2
scipy==1.14.1
torch==2.5.0
cupy-cuda12x==13.2.0
```

### Asenkron Görevler
```
celery==5.4.0
redis==5.0.7
```

## 🌐 İstemci Tarafı Bağımlılıklar (JavaScript)

İstemci tarafı bağımlılıkları `index.html` içinde CDN (Content Delivery Network) üzerinden doğrudan çekilmektedir. `npm` veya `package.json` kullanımı kaldırılmıştır.

- **Three.js (`0.165.0`):** 3D render motoru.
- **Plotly.js (`latest`):** İnteraktif bilimsel grafikler için kullanılır.

## 🏗️ Sistem Mimarisi

Detaylı ve güncel mimari açıklamaları için lütfen `SISTEM_MIMARISI.md` dosyasına başvurun.

### Temel Yapı
- **Backend:** `server` klasöründe yer alan, FastAPI tabanlı asenkron bir sunucudur.
- **Frontend:** `src` klasöründe yer alan, modern JavaScript (ES6 Modules) ile yazılmış, `three.js` ve `plotly.js` kullanan bir arayüzdür.
- **İletişim:** Backend ve frontend arasında `WebSocket` üzerinden gerçek zamanlı iletişim kurulur.

## 🔧 Kurulum ve Çalıştırma

Projenin kurulumu ve çalıştırılması, tüm adımları otomatize eden `start_server.bat` script'i ile basitleştirilmiştir.

### Tek Adımda Çalıştırma
Projenin ana dizinindeyken aşağıdaki komutu çalıştırmanız yeterlidir:
```batch
.\start_server.bat
```
Bu script, sanal ortamı kuracak, Python bağımlılıklarını yükleyecek ve sunucuyu başlatacaktır.

## 📊 Versiyon Uyumluluğu

- **CuPy:** Opsiyoneldir, ancak kullanılıyorsa CUDA 12.x sürümü gereklidir.
- **Tarayıcı:** Three.js ve ES6 modül desteği olan modern bir tarayıcı (Chrome, Firefox, Edge güncel sürümleri). 