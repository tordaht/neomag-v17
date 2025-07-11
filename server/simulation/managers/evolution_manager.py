import numpy as np
import logging
from typing import List

from .entity_manager import EntityManager
from ..agent import Agent
from ..evolution import evolve_population

logger = logging.getLogger(__name__)

class EvolutionManager:
    def __init__(self, entity_manager: EntityManager, initial_population_count: int):
        self.entity_manager = entity_manager
        self._initial_population_count = initial_population_count
        self.extinction_events = 0

    def handle_reproduction_and_evolution(self, generation: int):
        """Üreme, jenerasyon değerlendirmesi ve evrimi yönetir."""
        self._handle_reproduction()
        
        # Jenerasyon değerlendirmesi
        # Bu, belirli aralıklarla (örneğin 2000 tick) çağrılmalıdır.
        self._evaluate_generation(generation)
        
        # Popülasyonu kontrol et ve gerekirse acil durum prosedürünü uygula
        if len(self.entity_manager.agents) < self._initial_population_count / 4:
            self._emergency_repopulation(generation)


    def _handle_reproduction(self):
        """Üreme koşullarını kontrol eder ve yeni yavrular oluşturur."""
        for i, island in enumerate(self.entity_manager.islands):
            reproducing_agents = [agent for agent in island if agent.state.energy >= agent.state.genes.reproduction_threshold]
            if len(reproducing_agents) >= 2:
                # Yavru oluşturma işlemini `evolve_population` fonksiyonuna devret.
                # `_create_offspring` artık doğrudan kullanılmıyor.
                new_offspring = evolve_population(reproducing_agents, 1, 0.1) # 1 yavru, düşük mutasyon
                
                if new_offspring:
                    self.entity_manager.add_offspring(new_offspring)
                    
                    # Ebeveynlerin enerjisini düşür
                    for parent in reproducing_agents[:2]:
                        parent.state.energy -= 50
                        parent.state.offspring_count += len(new_offspring)


    def _evaluate_generation(self, current_generation: int):
        """Tüm popülasyon için jenerasyon değerlendirmesi yapar."""
        logger.info(f"Jenerasyon {current_generation} değerlendiriliyor...")
        
        all_agents_flat = self.entity_manager.agents
        if not all_agents_flat:
            logger.warning("Değerlendirilecek ajan bulunamadı, jenerasyon atlanıyor.")
            return

        # Elitleri seç ve geri kalanları yeni jenerasyonla değiştir
        new_islands = []
        for island_population in self.entity_manager.islands:
            if not island_population:
                new_islands.append([])
                continue
            
            # Popülasyonu sabit tutmak için yavru sayısını ada boyutuna göre ayarla
            num_offspring = len(island_population)
            next_gen_island = evolve_population(
                population=island_population,
                num_offspring=num_offspring,
                mutation_strength=np.mean([p.state.genes.mutation_rate for p in island_population])
            )
            new_islands.append(next_gen_island)
        
        self.entity_manager.islands = new_islands
        
        # Yeni jenerasyon için yiyecekleri yeniden doldur
        self.entity_manager.spawn_food(300)
        
        logger.info(f"Yeni jenerasyon {current_generation + 1} başlatıldı. Popülasyon: {len(self.entity_manager.agents)}")


    def _emergency_repopulation(self, current_generation: int):
        """Popülasyon kritik seviyenin altına düşerse, hayatta kalanları klonlar."""
        logger.warning("Acil durum yeniden popülasyon prosedürü aktive edildi!")
        survivors = sorted(self.entity_manager.agents, key=lambda a: a.state.energy, reverse=True)
        
        if not survivors:
            self.entity_manager.spawn_initial_population(self._initial_population_count // 2)
            return

        num_to_repopulate = self._initial_population_count - len(self.entity_manager.agents)
        for _ in range(num_to_repopulate):
            parent = np.random.choice(survivors)
            self.entity_manager.add_agent(
                x=np.random.uniform(0, self.entity_manager.width),
                y=np.random.uniform(0, self.entity_manager.height),
                generation=current_generation,
                genes=parent.state.genes
            )
        logger.info(f"{num_to_repopulate} yeni ajan acil durum prosedürüyle oluşturuldu.") 