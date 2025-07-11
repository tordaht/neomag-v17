from celery import Celery

# Redis'in varsayılan olarak localhost:6379 üzerinde çalıştığını varsayıyoruz.
# Proje raporundaki "Production Scale" aşamasında bu konfigürasyonun
# daha sağlam hale getirilmesi (örn. environment variables) gerekecektir.
REDIS_URL = "redis://localhost:6379/0"

# Celery uygulamasını oluştur
celery_app = Celery(
    "neomag_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["server.analysis.statistical_analyzer"] # Analiz görevlerinin bulunduğu modül
)

# Görevlerin ve sonuçların serileştirilmesi için yapılandırma
# Bilimsel hesaplamada karmaşık Python nesneleri (numpy array, pandas df) için pickle gereklidir.
celery_app.conf.update(
    task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["pickle"],
    task_track_started=True,
)

if __name__ == "__main__":
    celery_app.start() 