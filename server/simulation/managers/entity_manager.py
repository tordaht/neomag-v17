import numpy as np
import uuid
from typing import List, Optional

from ..agent import Agent, AgentGenes
from ..Quadtree import Rectangle, Quadtree

class Food:
    """Besin öğesi"""
    def __init__(self, x: float, y: float, energy_value: float = 25.0):
        self.x = x
        self.y = y
        self.energy_value = energy_value
        self.id = str(uuid.uuid4())[:8]

class EntityManager:
    def __init__(self, width: int, height: int, num_islands: int = 4):
        self.width = width
        self.height = height
        self.num_islands = num_islands
        self.islands: List[List[Agent]] = [[] for _ in range(num_islands)]
        self.food: List[Food] = []
        self.qtree = Quadtree(Rectangle(width / 2, height / 2, width, height), 4)

    @property
    def agents(self) -> List[Agent]:
        """Tüm adalardaki ajanları tek bir liste olarak döndürür."""
        return [agent for island in self.islands for agent in island]

    def reset(self, initial_population_count: int):
        """Varlıkları başlangıç durumuna sıfırlar."""
        self.islands = [[] for _ in range(self.num_islands)]
        self.food = []
        self.spawn_initial_population(initial_population_count)

    def spawn_initial_population(self, count: int):
        """Başlangıç popülasyonunu ve yiyecekleri oluşturur, adalara dağıtır."""
        agents = [Agent(x=np.random.uniform(0, self.width), y=np.random.uniform(0, self.height), generation=0) for _ in range(count)]
        for i, agent in enumerate(agents):
            island_index = i % self.num_islands
            self.islands[island_index].append(agent)
        self.spawn_food(300)

    def add_agent(self, x: float, y: float, generation: int = 0, genes: Optional[AgentGenes] = None):
        """Belirtilen koordinata yeni bir ajan ekler."""
        new_agent = Agent(x=x, y=y, genes=genes, generation=generation)
        island_sizes = [len(island) for island in self.islands]
        target_island_index = np.argmin(island_sizes) if island_sizes else 0
        self.islands[target_island_index].append(new_agent)

    def remove_agents(self, agents_to_remove: List[Agent]):
        """Verilen ajan listesini adalardan kaldırır."""
        if not agents_to_remove:
            return
            
        agents_to_remove_ids = {a.state.id for a in agents_to_remove}
        extinction_islands = set()

        for i, island in enumerate(self.islands):
            original_count = len(island)
            self.islands[i] = [agent for agent in island if agent.state.id not in agents_to_remove_ids]
            if len(self.islands[i]) == 0 and original_count > 0:
                extinction_islands.add(i)
        
        return extinction_islands


    def add_offspring(self, offspring: List[Agent]):
        """Yeni yavruları adalara ekler."""
        for child in offspring:
            # Yavruyu en az nüfuslu adaya ekle
            island_sizes = [len(island) for island in self.islands]
            target_island_index = np.argmin(island_sizes) if island_sizes else 0
            self.islands[target_island_index].append(child)

    def spawn_food(self, count: int):
        """Belirtilen sayıda yiyecek oluşturur."""
        for _ in range(count):
            food_item = Food(
                x=np.random.uniform(0, self.width),
                y=np.random.uniform(0, self.height),
                energy_value=np.random.uniform(50, 100)
            )
            self.food.append(food_item)

    def consume_food(self, food_ids: set):
        """Verilen ID'lere sahip yiyecekleri tüketir ve yenilerini oluşturur."""
        if not food_ids:
            return
        self.food = [f for f in self.food if f.id not in food_ids]
        self.spawn_food(len(food_ids))

    def rebuild_quadtree(self):
        """Quadtree'yi mevcut varlık konumlarıyla yeniden oluşturur."""
        self.qtree = Quadtree(Rectangle(self.width / 2, self.height / 2, self.width, self.height), 4)
        for agent in self.agents:
            self.qtree.insert((agent.state.x, agent.state.y, agent))
        for food_item in self.food:
            self.qtree.insert((food_item.x, food_item.y, food_item)) 