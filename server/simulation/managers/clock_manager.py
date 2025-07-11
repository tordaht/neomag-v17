import time

class SimulationClock:
    def __init__(self):
        self.ticks: int = 0
        self.generation: int = 0
        self.is_paused: bool = True
        self.start_time: float = time.time()
        self.last_update_time: float = time.time()
        self._update_call_times = []

    def tick(self):
        """Simülasyon tick'ini bir artırır."""
        self.ticks += 1
        self.last_update_time = time.time()
        self._update_call_times.append(self.last_update_time)

    def next_generation(self):
        """Yeni bir jenerasyona geçer."""
        self.generation += 1

    def set_pause(self, is_paused: bool):
        """Simülasyonu duraklatır veya devam ettirir."""
        self.is_paused = is_paused

    def reset(self):
        """Saati başlangıç durumuna sıfırlar."""
        self.ticks = 0
        self.generation = 0
        self.is_paused = False
        self.start_time = time.time()
        self._update_call_times = []

    def get_ups(self) -> float:
        """Son 10 saniye içindeki ortalama Güncelleme/Saniye (UPS) değerini döndürür."""
        now = time.time()
        # Son 10 saniyeden eski kayıtları temizle
        self._update_call_times = [t for t in self._update_call_times if now - t <= 10]
        if not self._update_call_times:
            return 0.0
        # 10 saniyeden daha az süre geçtiyse bile, geçen süreye böl
        elapsed = now - self.start_time
        if elapsed < 10 and elapsed > 0:
             return len(self._update_call_times) / elapsed
        return len(self._update_call_times) / 10.0 