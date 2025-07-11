import time
from dataclasses import dataclass, field

@dataclass
class TrafficReport:
    """Ağ trafiği raporu için veri sınıfı."""
    bytes_sent_total: int = 0
    bytes_received_total: int = 0
    messages_sent_total: int = 0
    messages_received_total: int = 0
    monitoring_duration_seconds: float = 0.0
    avg_bytes_sent_per_second: float = 0.0
    avg_bytes_received_per_second: float = 0.0

class TrafficMonitor:
    """
    WebSocket sunucusunun ağ trafiğini izlemek için basit bir monitör.
    """
    def __init__(self):
        self._bytes_sent = 0
        self._bytes_received = 0
        self._messages_sent = 0
        self._messages_received = 0
        self._start_time = time.monotonic()

    def record_sent(self, size_bytes: int):
        """Gönderilen bir mesajı kaydeder."""
        self._bytes_sent += size_bytes
        self._messages_sent += 1

    def record_received(self, size_bytes: int):
        """Alınan bir mesajı kaydeder."""
        self._bytes_received += size_bytes
        self._messages_received += 1
    
    def get_report(self) -> TrafficReport:
        """İzleme periyodu için bir trafik raporu oluşturur."""
        duration = time.monotonic() - self._start_time
        
        avg_sent_bps = (self._bytes_sent / duration) if duration > 0 else 0
        avg_received_bps = (self._bytes_received / duration) if duration > 0 else 0

        return TrafficReport(
            bytes_sent_total=self._bytes_sent,
            bytes_received_total=self._bytes_received,
            messages_sent_total=self._messages_sent,
            messages_received_total=self._messages_received,
            monitoring_duration_seconds=round(duration, 2),
            avg_bytes_sent_per_second=round(avg_sent_bps, 2),
            avg_bytes_received_per_second=round(avg_received_bps, 2)
        )

    def reset(self):
        """Sayaçları sıfırlar."""
        self._bytes_sent = 0
        self._bytes_received = 0
        self._messages_sent = 0
        self._messages_received = 0
        self._start_time = time.monotonic()

# Global olarak erişilebilecek tek bir instance oluşturuyoruz.
traffic_monitor = TrafficMonitor() 