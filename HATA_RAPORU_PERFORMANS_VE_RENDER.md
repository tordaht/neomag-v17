
# NeoMag Simülasyon Platformu - Performans ve Render Hatası Raporu

**Tarih:** 10 Temmuz 2025
**Raporu Hazırlayan:** Gemini AI
**Versiyon:** 1.0

## 1. Özet

Bu rapor, NeoMag simülasyon platformunda karşılaşılan iki kritik sorunu detaylandırmaktadır:

1.  **Aşırı Yükleme Süresi:** Uygulama arayüzünün kullanıcı tarafından kullanılabilir hale gelmesi 15 saniyeden uzun sürmektedir.
2.  **Render Başlatma Hatası:** `three.js` tabanlı 3D render motoru (`Renderer3D.js`), bir `TypeError` nedeniyle başlatılamamaktadır. Bu hata, simülasyonun 3D tuval üzerinde hiç görüntülenememesine neden olmaktadır.

Bu belge, sorunların analizini, ilgili kod parçacıklarını ve sorunun kök nedenini bulmaya yönelik soruları içermekte olup, konunun uzmanı tarafından incelenmek üzere hazırlanmıştır.

---

## 2. Gözlemlenen Sorunlar

### Sorun 1: Yüksek Başlatma Süresi (>15sn)

-   **Belirti:** Tarayıcıda sayfa yenilendikten sonra, arayüzün (kontrol butonları, grafik alanları ve 3D tuval) tamamen yüklenip etkileşime hazır hale gelmesi 15 saniyeden fazla sürmektedir. Bu durum, kullanıcı deneyimini ciddi şekilde olumsuz etkilemektedir.
-   **Olası Nedenler:**
    -   **Büyük Kütüphaneler:** `three.js` (v0.166.1) ve `Plotly.js` (v2.33.0) gibi büyük JavaScript kütüphanelerinin yüklenmesi ve "parse" edilmesi zaman alıyor olabilir.
    -   **Bloklayan İşlemler:** `AppController.js` içerisindeki `initializeApp` fonksiyonu, ana iş parçacığını (main thread) uzun süre meşgul eden senkron operasyonlar içeriyor olabilir.
    -   **Verimsiz Başlatma Sırası:** Kaynakların (render motoru, dashboard yöneticisi, WebSocket bağlantısı) yüklenme ve başlatılma sırası optimize edilmemiş olabilir.

### Sorun 2: Render Başlatma Hatası (Boş Tuval)

-   **Belirti:** 3D simülasyonu göstermesi gereken tuval tamamen boş kalıyor. Tarayıcının geliştirici konsolunda aşağıdaki kritik hata görülüyor:
    ```
    Uncaught TypeError: Cannot read properties of null (reading 'setUsage')
        at Renderer3D.init (Renderer3D.js:69:42)
        at new Renderer3D (Renderer3D.js:25:14)
        at AppController.initializeApp (AppController.js:42:29)
    ```
-   **Analiz:**
    -   Hata, `src/systems/Renderer3D.js` dosyasındaki `init()` metodu içinde, `this.instancedMesh.instanceColor.setUsage(THREE.DynamicDrawUsage);` satırında meydana gelmektedir.
    -   Bu hata, `this.instancedMesh.instanceColor` özelliğinin `null` olduğunu göstermektedir.
    -   `three.js` dokümantasyonuna göre, bir `InstancedMesh` nesnesi, materyalinin `vertexColors` özelliği `true` olarak ayarlandığında `instanceColor` tamponunu (bir `InstancedBufferAttribute`) otomatik olarak oluşturmalıdır.
    -   Kodumuzda materyal doğru bir şekilde `vertexColors: true` ile oluşturulmuştur. Bu durum, `three.js`'in beklenen davranışını sergilemediğini veya bizim API'yi hatalı kullandığımızı düşündürmektedir.
-   **Uygulanan Geçici Çözüm:**
    -   Hatanın oluştuğu `this.instancedMesh.instanceColor.setUsage(...)` satırı yorum satırı haline getirilerek uygulamanın başlangıçta çökmesi engellenmiştir.
    -   Ancak bu, kök nedeni çözmemektedir. Eğer `instanceColor` gerçekten `null` ise, render döngüsü içindeki `setColorAt()` çağrısı bir sonraki aşamada hata verecek ve ajanlar renklendirilemeyecektir.

---

## 3. Sistem Mimarisine Genel Bakış

-   **İstemci (`src/`):**
    -   `main.js`: Uygulamanın giriş noktası. `AppController` sınıfını başlatır.
    -   `core/AppController.js`: Merkezi kontrolcü. WebSocket bağlantısını, `Renderer3D` ve `DashboardManager` gibi ana bileşenleri ve kullanıcı etkileşimlerini yönetir.
    -   `systems/Renderer3D.js`: `three.js` sahnesini, kamerasını ve render döngüsünü yönetir. Performans için `InstancedMesh` kullanacak şekilde yeniden yazılmıştır ve mevcut hatanın kaynağıdır.
    -   `index.html`: Ana HTML dosyası. Bağımlılıkları (`three`, `plotly`) yüklemek için `importmap` kullanır.
-   **Sunucu (`server/`):**
    -   `main.py`: FastAPI tabanlı sunucu. WebSocket bağlantılarını yönetir ve simülasyon motoruyla istemci arasında bir köprü görevi görür.

---

## 4. İlgili Kod Parçacıkları

### `src/systems/Renderer3D.js` (Hatanın Kaynağı)
```javascript
// ...
// InstancedMesh Kurulumu
const geometry = new THREE.IcosahedronGeometry(5, 1);
const material = new THREE.MeshStandardMaterial({
    roughness: 0.4,
    metalness: 0.2,
    vertexColors: true // Bu özellik true olmasına rağmen instanceColor null oluyor.
});

this.instancedMesh = new THREE.InstancedMesh(geometry, material, MAX_AGENTS);
this.instancedMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);

// AŞAĞIDAKİ SATIR HATAYA NEDEN OLUYOR:
this.instancedMesh.instanceColor.setUsage(THREE.DynamicDrawUsage);

this.scene.add(this.instancedMesh);
// ...
```

### `src/core/AppController.js` (Başlatma Mantığı)
```javascript
// ...
initializeApp() {
    console.log("AppController v17.2 başlatılıyor...");
    
    const renderContainer = document.getElementById('simulation-container-3d');
    if (renderContainer) {
        // Hatanın tetiklendiği yer:
        this.renderer = new Renderer3D(renderContainer); 
    } else {
        console.error("3D render container 'simulation-container-3d' bulunamadı.");
        return;
    }

    this.dashboard = new DashboardManager();
    this.connectWebSocket();
    this.setupEventListeners();
    // ...
    this.animate();
}
// ...
```

### `index.html` (Bağımlılık Yükleme)
```html
<script async src="https://unpkg.com/es-module-shims@1.10.0/dist/es-module-shims.js"></script>
<script type="importmap">
{
    "imports": {
        "three": "https://unpkg.com/three@0.166.1/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.166.1/examples/jsm/"
    }
}
</script>
```

---

## 5. Uzmana Yönelik Sorular

### Render Hatası Hakkında:

1.  `three.js` v0.166.1'de, materyalde `vertexColors: true` olarak ayarlanmasına rağmen `InstancedMesh.instanceColor` özelliğinin `null` olmasının sebebi ne olabilir? Bu, kütüphanenin bilinen bir hatası mı, gözden kaçan bir API değişikliği mi, yoksa bizim tarafımızdan yanlış bir kullanım mı söz konusu?
2.  Kullandığımız `importmap` ile modül yükleme stratejisi, `three.js` modüllerinin veya özelliklerinin başlatılma şeklinde bir soruna yol açıyor olabilir mi?
3.  Örnek (instance) bazında renk ataması yapmak için bu `null` referans hatasını önleyecek daha güvenilir veya alternatif bir yöntem var mıdır? Örneğin, `instanceColor` tamponunu manuel olarak oluşturup `InstancedMesh`'e atamak bir çözüm olabilir mi?

### Performans Sorunları Hakkında:

1.  Böyle bir `three.js` uygulamasının başlatma (startup) sürecini profilleyerek darboğazları tespit etmek için en etkili yöntemler ve araçlar nelerdir?
2.  Uygulamanın `Plotly.js` ve `three.js` gibi büyük kütüphaneleri yüklemesi bariz bir yavaşlık kaynağıdır. Mevcut `importmap` yapısıyla "lazy loading" (tembel yükleme) veya "code splitting" (kod bölme) teknikleri nasıl uygulanabilir? Örneğin, `DashboardManager` ve `Plotly` bağımlılığının yüklenmesini, 3D sahne görünür hale geldikten sonraya erteleyebilir miyiz?
3.  `AppController.js` içerisindeki başlatma sırasında, ana iş parçacığını (main thread) farkında olmadan uzun süre bloklayan bariz bir anti-pattern veya hatalı bir mantık akışı var mı?

---

## 6. Önerilen Sonraki Adımlar

1.  **Uzman Değerlendirmesi:** Bu raporun incelenerek yapılan analizin doğrulanması.
2.  **Derinlemesine Profiling:** Tarayıcı geliştirici araçlarının "Performance" sekmesi kullanılarak, sayfanın yüklenmesinden uygulamanın tamamen hazır hale gelmesine kadar geçen tüm sürecin detaylı bir şekilde profillenmesi.
3.  **Sorunu İzolasyonu:** Projeden bağımsız, minimal bir kod örneği (örneğin CodePen veya JSFiddle üzerinde) oluşturarak sadece `three.js` v0.166.1 ile `InstancedMesh` ve `instanceColor` davranışının test edilmesi. Bu, sorunun kütüphaneye mi özgü yoksa proje entegrasyonuna mı bağlı olduğunu netleştirecektir. 