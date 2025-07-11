import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import uuid
import torch

from .ai_model import AgentBrain

# Sabitler
BRAIN_INPUT_SIZE = 5  # energy, food_dx, food_dy, agent_dx, agent_dy
BRAIN_OUTPUT_SIZE = 2 # vx, vy
BRAIN_HIDDEN_SIZE = 16

@dataclass
class AgentGenes:
    """Bir ajanın genetik yapısını tanımlar. Artık beyin ağırlıklarını da içeriyor."""
    reproduction_threshold: float
    energy_efficiency: float
    detection_range: float
    vision_range: float # Eklendi
    size: float # Eklendi
    speed: float
    aggression: float
    mutation_rate: float
    energy_decay: float
    brain_weights: List[float] # Düzleştirilmiş beyin ağırlıkları

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AgentState:
    """Bir ajanın anlık durumunu temsil eder."""
    id: str
    x: float
    y: float
    vx: float
    vy: float
    energy: float
    age: int
    generation: int
    offspring_count: int
    genes: AgentGenes # AgentGenes artık beyin ağırlıklarını içeriyor
    last_updated_tick: int = 0 # Delta güncellemeleri için eklendi

    def to_dict(self) -> Dict[str, Any]:
        """Ajan durumunu sözlük formatına çevirir."""
        data = asdict(self)
        # AgentGenes'in de sözlüğe çevrildiğinden emin ol
        data['genes'] = self.genes.to_dict()
        return data

def get_brain_flat_weight_count() -> int:
    """Ağdaki toplam ağırlık ve bias sayısını hesaplar."""
    temp_brain = AgentBrain(BRAIN_INPUT_SIZE, BRAIN_OUTPUT_SIZE, BRAIN_HIDDEN_SIZE)
    return sum(p.numel() for p in temp_brain.parameters())

def create_random_genes() -> AgentGenes:
    """Rastgele genetik değerlere ve beyin ağırlıklarına sahip bir AgentGenes nesnesi oluşturur."""
    num_weights = get_brain_flat_weight_count()
    return AgentGenes(
        reproduction_threshold=np.random.uniform(70, 95),
        energy_efficiency=np.random.uniform(0.7, 1.3),
        detection_range=np.random.uniform(50, 150),
        vision_range=np.random.uniform(100, 200), # Eklendi
        size=np.random.uniform(5, 15), # Eklendi
        speed=np.random.uniform(0.5, 5.0),
        aggression=np.random.uniform(0, 1),
        mutation_rate=np.random.uniform(0.01, 0.1),
        energy_decay=np.random.uniform(0.05, 0.2),
        brain_weights=list(np.random.randn(num_weights).astype(np.float32))
    )

class Agent:
    def __init__(self, x: float, y: float, generation: int, genes: Optional[AgentGenes] = None):
        self.state = AgentState(
            id=str(uuid.uuid4()),
            x=x,
            y=y,
            vx=0.0,
            vy=0.0,
            energy=100.0,
            age=0,
            generation=generation,
            offspring_count=0,
            genes=genes if genes else create_random_genes(),
            last_updated_tick=0 # Başlangıçta 0 olmalı
        )
        
        # Ajanın beynini oluştur ve genlerden gelen ağırlıkları yükle
        self.brain = AgentBrain(BRAIN_INPUT_SIZE, BRAIN_OUTPUT_SIZE, BRAIN_HIDDEN_SIZE)
        self.load_weights_from_genes()

    @property
    def id(self): return self.state.id
    @property
    def x(self): return self.state.x
    @property
    def y(self): return self.state.y
    @property
    def energy(self): return self.state.energy
    @property
    def age(self): return self.state.age
    @property
    def genes(self): return self.state.genes

    def load_weights_from_genes(self):
        """Genlerdeki düzleştirilmiş ağırlıkları beyin modeline yükler."""
        weights_flat = torch.tensor(self.state.genes.brain_weights, dtype=torch.float32)
        start = 0
        for param in self.brain.parameters():
            end = start + param.numel()
            param.data = weights_flat[start:end].view(param.shape)
            start = end

    def update(self, delta_time: float, nearby_agents: List['Agent'], nearby_food: List[Any]):
        """Ajanın karar verme ve durum güncelleme mantığını birleştirir."""
        # 1. En yakın yiyeceği ve ajanı bul (yakın listeden)
        nearest_food = min(nearby_food, key=lambda f: np.sqrt((self.state.x - f.x)**2 + (self.state.y - f.y)**2)) if nearby_food else None
        nearest_agent = min(nearby_agents, key=lambda a: np.sqrt((self.state.x - a.state.x)**2 + (self.state.y - a.state.y)**2)) if nearby_agents else None

        # 2. Girdileri hazırla ve karar ver
        energy_input = self.state.energy / 100.0
        
        food_dx, food_dy = 0.0, 0.0
        if nearest_food:
            food_dx = (nearest_food.x - self.state.x) / self.state.genes.vision_range
            food_dy = (nearest_food.y - self.state.y) / self.state.genes.vision_range
        
        agent_dx, agent_dy = 0.0, 0.0
        if nearest_agent:
            agent_dx = (nearest_agent.state.x - self.state.x) / self.state.genes.vision_range
            agent_dy = (nearest_agent.state.y - self.state.y) / self.state.genes.vision_range
            
        input_tensor = torch.tensor([
            energy_input, 
            np.clip(food_dx, -1, 1), np.clip(food_dy, -1, 1), 
            np.clip(agent_dx, -1, 1), np.clip(agent_dy, -1, 1)
        ], dtype=torch.float32)
        
        with torch.no_grad():
            output = self.brain(input_tensor)
        
        self.state.vx, self.state.vy = output[0].item(), output[1].item()

        # 3. Pozisyonu güncelle ve enerjiyi ayarla
        speed = self.state.genes.speed
        self.state.x += self.state.vx * speed * delta_time
        self.state.y += self.state.vy * speed * delta_time
        
        self.state.energy -= self.state.genes.energy_decay * delta_time
        self.state.age += 1
        self.state.last_updated_tick += 1 # Basit bir artış, world tick'i daha iyi olabilir
    
    def to_dict(self) -> Dict[str, Any]:
        """Ajan durumunu istemciye göndermek için sözlüğe çevirir."""
        return self.state.to_dict() 