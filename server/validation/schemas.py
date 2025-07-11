from pydantic import BaseModel, Field, validator
from typing import List

# Değer aralıkları için sabitler
MIN_ENERGY_EFFICIENCY = 0.5
MAX_ENERGY_EFFICIENCY = 2.0
MIN_SPEED = 0.1 # Minimum hızı daha makul bir seviyeye çek
MAX_SPEED = 5.0 # Maksimum hızı da dengelemek için düşür
MIN_DETECTION_RANGE = 10.0 # Algılama aralığını da ayarla
MAX_DETECTION_RANGE = 150.0

class ValidatedAgentGenes(BaseModel):
    """Doğrulama kuralları içeren Ajan Genleri Şeması."""
    reproduction_threshold: float = Field(..., gt=50, le=150)
    energy_efficiency: float = Field(..., ge=MIN_ENERGY_EFFICIENCY, le=MAX_ENERGY_EFFICIENCY)
    detection_range: float = Field(..., ge=MIN_DETECTION_RANGE, le=MAX_DETECTION_RANGE)
    speed: float = Field(..., ge=MIN_SPEED, le=MAX_SPEED)
    aggression: float = Field(..., ge=0.0, le=1.0)
    mutation_rate: float = Field(..., ge=0.001, le=0.2)

class ValidatedAgentState(BaseModel):
    """Doğrulama kuralları içeren Ajan Durumu Şeması."""
    id: str
    x: float
    y: float
    vx: float
    vy: float
    energy: float = Field(..., ge=0) # Enerji negatif olamaz
    age: int = Field(..., ge=0)
    generation: int = Field(..., ge=0)
    offspring_count: int = Field(..., ge=0)
    genes: ValidatedAgentGenes

class WorldState(BaseModel):
    """Tüm dünya durumunu kapsayan ve doğrulayan ana şema."""
    agents: List[ValidatedAgentState]
    food: List # Şimdilik basit tutuyoruz
    world_info: dict

    @validator('agents')
    def check_agent_positions(cls, agents, values, **kwargs):
        # Bu validator, dünya boyutları gibi ek bilgilere ihtiyaç duyabilir.
        # Şimdilik basit bir kontrol yapıyoruz.
        # Örneğin, hiçbir ajanın pozisyonunun NaN olmaması gerektiğini kontrol edebiliriz.
        for agent in agents:
            if agent.x is None or agent.y is None:
                 raise ValueError(f"Ajan {agent.id} için pozisyon bilgisi eksik.")
        return agents 

class AnalysisRequest(BaseModel):
    """Asenkron analiz görevi için istek modeli."""
    simulation_data: dict
    real_world_data: dict

class ExportRequest(BaseModel):
    """Veri dışa aktarma isteği için model."""
    format_type: str = Field(..., pattern="^(csv|json|excel)$") # Sadece belirli formatlara izin ver 