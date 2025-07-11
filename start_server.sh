#!/bin/bash
# NeoMag Sunucusunu Başlatma Betiği (Linux/macOS)

echo "=========================================="
echo "  NeoMag Sunucusu Başlatılıyor (v17.1)  "
echo "=========================================="

# Sanal ortam dizini
VENV_DIR="server/venv"

# Python sürümünü kontrol et (örneğin 3.10+)
# python --version

# Sanal ortamın var olup olmadığını kontrol et
if [ ! -d "$VENV_DIR" ]; then
    echo "Sanal ortam bulunamadı. Oluşturuluyor: $VENV_DIR"
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "HATA: Sanal ortam oluşturulamadı. Lütfen Python3 ve venv modülünün kurulu olduğundan emin olun."
        exit 1
    fi
fi

# Sanal ortamı aktive et
echo "Sanal ortam aktive ediliyor..."
source $VENV_DIR/bin/activate

# Bağımlılıkların kurulu olup olmadığını kontrol etmek için bir işaretçi dosyası
PACKAGES_INSTALLED_FLAG="$VENV_DIR/.packages_installed"

# Bağımlılıkların güncel olup olmadığını kontrol et
if [ "server/requirements.txt" -nt "$PACKAGES_INSTALLED_FLAG" ]; then
    echo "Yeni veya güncellenmiş bağımlılıklar bulundu. Yükleniyor..."
    pip install --upgrade pip
    pip install -r server/requirements.txt
    if [ $? -ne 0 ]; then
        echo "HATA: Bağımlılıklar yüklenemedi. Lütfen 'server/requirements.txt' dosyasını ve internet bağlantınızı kontrol edin."
        exit 1
    fi
    # Yükleme başarılı olduysa, işaretçi dosyasını güncelle
    touch "$PACKAGES_INSTALLED_FLAG"
else
    echo "Bağımlılıklar güncel."
fi

# Sunucuyu Uvicorn ile başlat
echo "Uvicorn sunucusu başlatılıyor: http://127.0.0.1:8080"
echo "Uygulamayı kapatmak için CTRL+C tuşlarına basın."
echo "=========================================="

# Proje kök dizininden çalıştırıldığını varsayarak
uvicorn server.main:app --host 127.0.0.1 --port 8080 --reload

# Sanal ortamı devre dışı bırak
deactivate
echo "Sunucu kapatıldı. Sanal ortam devre dışı bırakıldı." 