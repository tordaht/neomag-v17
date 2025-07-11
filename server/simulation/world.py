import logging
from typing import Dict, Any

from .managers.entity_manager import EntityManager
from .managers.clock_manager import SimulationClock
from .managers.interaction_manager import InteractionManager
from .managers.evolution_manager import EvolutionManager
from .managers.statistics_manager import StatisticsManager
from .managers.state_manager import StateManager

logger = logging.getLogger(__name__)

class ProductionWorld:
    """
    Refactored Production-ready bilimsel simülasyon dünyası.
    Sorumlulukları yönetici sınıflarına delege eder.
    """
    
    def __init__(self, width: int, height: int, initial_population: int, num_islands: int = 4):
        self.width = width
        self.height = height
        self._initial_population_count = initial_population
        self.version = "18.0.0"

        # Yöneticileri Başlat
        self.clock = SimulationClock()
        self.entities = EntityManager(width, height, num_islands)
        self.interaction = InteractionManager(self.entities)
        self.evolution = EvolutionManager(self.entities, initial_population)
        
        world_info = {
            "width": self.width, "height": self.height, 
            "version": self.version, "start_time": self.clock.start_time
        }
        self.stats = StatisticsManager(self.entities)
        self.state = StateManager(self.entities, self.stats, world_info)

        # Başlangıç popülasyonunu oluştur
        self.entities.spawn_initial_population(self._initial_population_count)
        
        logger.info(f"NeoMag Refactored World v{self.version} başlatıldı. Session: {self.state.session_id}")
        logger.info(f"İlk popülasyon: {initial_population} ajan, {num_islands} adaya bölündü.")

    def update(self, delta_time: float = 0.016):
        """Ana güncelleme döngüsü. Simülasyonun bir adımını ilerletir."""
        if self.clock.is_paused:
            return

        self.stats.perf_monitor.record_tick()
        
        # 1. Quadtree'yi yeniden oluştur
        self.entities.rebuild_quadtree()
        
        # 2. Ajan durumlarını, etkileşimleri, yaşlanmayı ve ölümü yönet
        self.interaction.update_interactions(delta_time)
        
        # 3. Üreme ve evrimi yönet
        if self.clock.ticks > 0 and self.clock.ticks % 100 == 0:
             self.evolution.handle_reproduction_and_evolution(self.clock.generation)
        
        # 4. Jenerasyonun sonu mu kontrol et
        if self.clock.ticks > 0 and self.clock.ticks % 2000 == 0:
            self.stats.record_generation_metrics(self.clock.generation, self.evolution.extinction_events)
            self.clock.next_generation()
            self.state.save_snapshot(self.clock.ticks, self.clock.generation)

        # Tick'i ilerlet
        self.clock.tick()

    def get_state_for_client(self) -> Dict[str, Any]:
        """İstemci için hafifletilmiş durumu döndürür."""
        return self.state.get_state_for_client(self.clock.ticks, self.clock.generation)

    def get_statistics(self) -> Dict[str, Any]:
        """Detaylı istatistikleri döndürür."""
        return self.stats.get_current_statistics(self.clock.ticks, self.clock.generation)

    def update_parameters(self, params: Dict[str, Any]):
        """Ajanların parametrelerini günceller."""
        self.interaction.update_agent_parameters(params)
        logger.info(f"Toplu parametreler güncellendi: {list(params.keys())}")

    def set_pause(self, is_paused: bool):
        """Simülasyonu duraklatır veya devam ettirir."""
        self.clock.set_pause(is_paused)

    def reset(self):
        """Tüm simülasyonu başlangıç durumuna sıfırlar."""
        logger.info("Simülasyon sıfırlanıyor...")
        self.clock.reset()
        self.entities.reset(self._initial_population_count)
        self.stats.reset()
        self.evolution.extinction_events = 0
        logger.info("Simülasyon başarıyla sıfırlandı.")