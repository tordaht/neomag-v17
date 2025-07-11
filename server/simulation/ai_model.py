import torch
import torch.nn as nn

class AgentBrain(nn.Module):
    """
    Ajanların karar mekanizmasını temsil eden basit bir ileri beslemeli sinir ağı.
    Çevresel girdileri alır ve hareket vektörünü (vx, vy) çıktı olarak verir.
    """
    def __init__(self, input_size: int, output_size: int, hidden_size: int = 16):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Tanh()  # Çıktıları -1 ve 1 aralığında sınırlamak için Tanh aktivasyonu
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x) 