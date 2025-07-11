# NeoMag Dağıtım Kılavuzu v17.1

Bu doküman, NeoMag platformunun bir sunucuya manuel veya Docker ile nasıl dağıtılacağını adım adım açıklamaktadır.

## 1. Manuel Dağıtım

### Adım 1: Ön Gereksinimler
-   **Python:** Sunucuda Python 3.10 veya üzeri bir sürümün yüklü olması gerekmektedir.
-   **Git:** Proje dosyalarını sunucuya çekmek için Git gereklidir.

### Adım 2: Projeyi Sunucuya Klonlama
```bash
git clone <proje_repo_adresi>
cd neomag
```

### Adım 3: Başlatma Betiğini Çalıştırma
Proje, sunucuyu ve bağımlılıkları otomatik olarak kurup başlatan betikler içermektedir.

**Windows için:**
```batch
.\\start_server.bat
```

**Linux/macOS için:** (Önce betiği çalıştırılabilir yapın)
```bash
chmod +x start_server.sh
./start_server.sh
```
Bu betikler, gerekli Python sanal ortamını (`venv`) oluşturur, `server/requirements.txt` dosyasındaki bağımlılıkları kurar ve uygulamayı `uvicorn` ile başlatır.

### Adım 4: Süreci Arka Planda Çalıştırma (Production)
Sunucuyu terminal kapatıldığında bile çalışır durumda tutmak için `systemd` gibi bir süreç yöneticisi kullanılması tavsiye edilir.

1.  `/etc/systemd/system/neomag.service` adında bir servis dosyası oluşturun:
    ```ini
    [Unit]
    Description=NeoMag Simulation Server
    After=network.target

    [Service]
    User=<kullanici_adiniz>
    Group=<kullanici_grubunuz>
    WorkingDirectory=/path/to/your/project/neomag
    # Betik zaten sanal ortamı aktive edip uvicorn'u çalıştıracaktır
    ExecStart=/path/to/your/project/neomag/start_server.sh
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
2.  Servisi etkinleştirin ve başlatın:
    ```bash
    sudo systemctl enable neomag
    sudo systemctl start neomag
    ```

---

## 2. Docker ile Dağıtım (Tavsiye Edilen)

Docker, projenin tüm bağımlılıklarını bir konteyner içinde paketleyerek dağıtımı basitleştirir.

### Adım 1: `docker-compose.yml` Oluşturma
Projenin kök dizinine aşağıdaki içerikle bir `docker-compose.yml` dosyası oluşturun:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: neomag_backend
    ports:
      - "8080:8080"
    volumes:
      - ./server:/app/server
      - ./exports:/app/exports
    command: uvicorn server.main:app --host 0.0.0.0 --port 8080 --reload
    restart: unless-stopped

# Not: Frontend statik dosyaları artık doğrudan FastAPI üzerinden sunuluyor.
# Ayrı bir frontend servisine (örn: Nginx) şimdilik gerek yoktur.
```

### Adım 2: `Dockerfile` Oluşturma
Projenin kök dizinine aşağıdaki içerikle bir `Dockerfile` oluşturun:

```Dockerfile
# Python 3.12 slim versiyonunu temel al
FROM python:3.12-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Önce gereksinimleri kopyala ve yükle (cache'leme için)
COPY ./server/requirements.txt /app/server/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/server/requirements.txt

# Proje dosyalarını kopyala
COPY . /app

# Uvicorn portunu dışarı aç
EXPOSE 8080

# Başlatma komutu docker-compose'da belirtildi
```

### Adım 3: Uygulamayı Başlatma
```bash
docker-compose up --build
```
Uygulama artık `http://<sunucu_ip>:8080` adresinden erişilebilir olacaktır. Arka planda çalıştırmak için `docker-compose up -d --build` komutunu kullanın.

---

## 3. Örnek CI/CD Akışı (GitHub Actions)

Aşağıdaki workflow, `main` branch'ine yapılan her `push` işleminde manuel dağıtım ortamını günceller.

`.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production (Manual Setup)

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: SSH and Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USERNAME }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /path/to/your/project/neomag
            git pull origin main
            # Sanal ortamı aktive et ve bağımlılıkları güncelle
            source server/venv/bin/activate
            pip install -r server/requirements.txt
            # systemd servisini yeniden başlatarak uygulamayı güncelle
            sudo systemctl restart neomag
```
Bu workflow, sunucudaki kodu günceller, bağımlılıkları standart `pip` komutu ile senkronize eder ve `systemd` servisini yeniden başlatarak değişikliklerin canlıya alınmasını sağlar. 