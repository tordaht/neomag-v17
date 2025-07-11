import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

from .entity_manager import EntityManager
from ..analysis.performance_monitor import PerformanceMonitor
from ..utils import deep_convert_to_native_types # Helper fonksiyonu için bir utils dosyası oluşturalım

@dataclass
class EvolutionMetrics:
    """Evrim metrikleri"""
    generation: int
    population_size: int
    avg_fitness: float
    max_fitness: float
    genetic_diversity: float
    avg_age: float
    extinction_events: int

class StatisticsManager:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.perf_monitor = PerformanceMonitor()
        self.metrics_history: List[EvolutionMetrics] = []

    def reset(self):
        """İstatistikleri ve performans izleyiciyi sıfırlar."""
        self.perf_monitor = PerformanceMonitor()
        self.metrics_history = []

    def record_generation_metrics(self, generation: int, extinction_events: int):
        """Bir jenerasyonun sonundaki metrikleri kaydeder."""
        agents = self.entity_manager.agents
        if not agents:
            return

        avg_fitness = float(np.mean([a.state.energy for a in agents]))
        max_fitness = float(np.max([a.state.energy for a in agents]))
        genetic_diversity = float(np.std([a.state.genes.speed for a in agents]))
        avg_age = float(np.mean([a.state.age for a in agents]))

        metrics = EvolutionMetrics(
            generation=generation,
            population_size=len(agents),
            avg_fitness=avg_fitness,
            max_fitness=max_fitness,
            genetic_diversity=genetic_diversity,
            avg_age=avg_age,
            extinction_events=extinction_events
        )
        self.metrics_history.append(metrics)

    def get_current_statistics(self, generation: int, ticks: int) -> Dict[str, Any]:
        """Simülasyonun anlık ve geçmişe dönük istatistiklerini döndürür."""
        agents = self.entity_manager.agents
        if not agents:
            return {"message": "No agents available."}
        
        agent_data = [asdict(a.state.genes) for a in agents]
        df_genes = pd.DataFrame(agent_data)
        
        current_perf = self.perf_monitor.get_metrics()
        avg_perf = self.perf_monitor.get_average_metrics()
        
        stats = {
            "tick": ticks,
            "generation": generation,
            "population_size": len(agents),
            "island_distribution": [len(island) for island in self.entity_manager.islands],
            "total_food_sources": len(self.entity_manager.food),
            "performance": {
                "current_cpu_percent": current_perf.get("cpu_percent"),
                "current_memory_mb": current_perf.get("memory_mb"),
                "average_cpu_percent": avg_perf.get("avg_cpu_percent"),
                "average_memory_mb": avg_perf.get("avg_memory_mb"),
            },
            "genetic_summary": {
                "mean": deep_convert_to_native_types(df_genes.mean().to_dict()),
                "std_dev": deep_convert_to_native_types(df_genes.std().to_dict()),
                "min": deep_convert_to_native_types(df_genes.min().to_dict()),
                "max": deep_convert_to_native_types(df_genes.max().to_dict()),
            },
            "evolution_history": [asdict(m) for m in self.metrics_history]
        }
        return stats

    def get_average_fitness(self) -> float:
        """Ajanların ortalama fitness değerini hesaplar."""
        agents = self.entity_manager.agents
        if not agents:
            return 0.0
        return float(np.mean([agent.state.energy for agent in agents]))

    def get_genetic_diversity(self) -> float:
        """Popülasyonun genetik çeşitliliğini (hız geninin std sapması) hesaplar."""
        agents = self.entity_manager.agents
        if not agents:
            return 0.0
        return float(np.std([a.state.genes.speed for a in agents])) 