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