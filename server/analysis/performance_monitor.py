"""
NeoMag Performans Monitörü v1.0
Sistem kaynaklarını (CPU, GPU, Memory) izler ve loglar.
"""

import psutil
import time
import threading
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None

@dataclass 
class PerformanceMetrics:
    """Anlık performans metrikleri"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    gpu_memory_used_mb: Optional[float] = None
    gpu_memory_total_mb: Optional[float] = None
    gpu_utilization_percent: Optional[float] = None

class PerformanceMonitor:
    """
    Sistem kaynak kullanımını (CPU, Bellek) izlemek için bir yardımcı sınıf.
    """
    def __init__(self):
        self.process = psutil.Process()
        self.history: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def get_metrics(self) -> Dict[str, float]:
        """Anlık CPU ve Bellek kullanımını döndürür."""
        
        # get_cpu_percent() ilk çağrıldığında 0.0 döner, bu yüzden non-blocking çağrı gerekir.
        # Daha doğru sonuç için kısa bir aralıkla çağrılabilir: self.process.cpu_percent(interval=0.01)
        # Ancak bu, ana döngüyü yavaşlatabilir. Şimdilik temel kullanımı yeterli.
        cpu_percent = self.process.cpu_percent()
        
        # Bellek kullanımı (resident set size) megabyte olarak
        memory_mb = self.process.memory_info().rss / (1024 * 1024)
        
        return {
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb
        }

    def record_tick(self):
        """Metrikleri zaman damgasıyla birlikte kaydeder."""
        metrics = self.get_metrics()
        metrics["timestamp"] = time.time() - self.start_time
        self.history.append(metrics)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Kaydedilen tüm metrik geçmişini döndürür."""
        return self.history

    def get_average_metrics(self) -> Dict[str, float]:
        """Tüm çalışma süresi boyunca ortalama metrikleri hesaplar."""
        if not self.history:
            return {"avg_cpu_percent": 0.0, "avg_memory_mb": 0.0}
        
        avg_cpu = sum(m['cpu_percent'] for m in self.history) / len(self.history)
        avg_mem = sum(m['memory_mb'] for m in self.history) / len(self.history)
        
        return {
            "avg_cpu_percent": round(avg_cpu, 2),
            "avg_memory_mb": round(avg_mem, 2)
        }

if __name__ == '__main__':
    # Test için
    monitor = PerformanceMonitor()
    print("Performans izleyici başlatıldı. 5 saniye boyunca metrikler kaydedilecek...")
    for i in range(10):
        monitor.record_tick()
        print(f"Tick {i+1}: {monitor.get_metrics()}")
        time.sleep(0.5)
        
    print("\n--- Metrik Geçmişi ---")
    print(monitor.get_history())
    
    print("\n--- Ortalama Metrikler ---")
    print(monitor.get_average_metrics()) 