from typing import List
from .entity_manager import EntityManager, Food
from ..agent import Agent
from ..Quadtree import Rectangle

class InteractionManager:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def update_interactions(self, delta_time: float):
        """Ajanların çevreleriyle olan tüm etkileşimlerini yönetir."""
        
        # 1. Ajanların 'update' metodunu çağır (karar verme, hareket)
        self._update_agents_state(delta_time)
        
        # 2. Yiyecek tüketimini yönet
        self._handle_food_consumption()
        
        # 3. Yaşlanma ve ölümü yönet
        dead_agents = self._handle_aging_and_death()
        
        # Ölen ajanları Entity Manager'dan kaldır
        if dead_agents:
            extinction_events = self.entity_manager.remove_agents(dead_agents)
            # Soy tükenmesi olaylarını burada loglayabilir veya başka bir yöneticiye bildirebiliriz.
            # Örneğin: self.stats_manager.record_extinctions(extinction_events)
        
    def _update_agents_state(self, delta_time: float):
        """Her ajanın kendi iç durumunu ve hareketini güncellemesini tetikler."""
        qtree = self.entity_manager.qtree
        for agent in self.entity_manager.agents:
            # Quadtree kullanarak yakındaki nesneleri bul
            vision_range = Rectangle(agent.state.x, agent.state.y, agent.state.genes.vision_range * 2, agent.state.genes.vision_range * 2)
            nearby_entities = qtree.query(vision_range)
            
            nearby_agents = [e[2] for e in nearby_entities if isinstance(e[2], Agent) and e[2].state.id != agent.state.id]
            nearby_food = [e[2] for e in nearby_entities if isinstance(e[2], Food)]
            
            # Ajanın karar verme ve hareket mantığını çalıştır
            agent.update(delta_time, nearby_agents, nearby_food)

    def _handle_food_consumption(self):
        """Ajanların yiyecek tüketmesini sağlar."""
        consumed_food_ids = set()
        for agent in self.entity_manager.agents:
            if agent.state.energy >= 100: continue

            eating_range = Rectangle(agent.state.x, agent.state.y, 10, 10)
            nearby_food = [e[2] for e in self.entity_manager.qtree.query(eating_range) if isinstance(e[2], Food)]

            for food in nearby_food:
                if food.id not in consumed_food_ids:
                    # Ajan ve yiyecek arasındaki mesafeyi kontrol etmeye gerek yok,
                    # çünkü Quadtree zaten yakındakileri buldu.
                    # Ancak daha hassas bir kontrol istenirse mesafe hesaplanabilir.
                    agent.state.energy += food.energy_value
                    consumed_food_ids.add(food.id)
                    break 
        
        if consumed_food_ids:
            self.entity_manager.consume_food(consumed_food_ids)

    def _handle_aging_and_death(self) -> List[Agent]:
        """Ajanların yaşlanmasını ve ölmesini yönetir, ölenlerin listesini döndürür."""
        dead_agents = []
        for agent in self.entity_manager.agents:
            agent.state.age += 1
            agent.state.energy -= agent.state.genes.energy_decay # Yaşlanma maliyeti
            if agent.state.energy <= 0:
                dead_agents.append(agent)
        return dead_agents

    def update_agent_parameters(self, params: dict):
        """Ajanların genetik parametrelerini günceller."""
        for agent in self.entity_manager.agents:
            for key, value in params.items():
                if hasattr(agent.state.genes, key):
                    setattr(agent.state.genes, key, value) 