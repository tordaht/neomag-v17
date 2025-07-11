import os
import uuid
import json
import time
from typing import Dict, Any, Optional

from .entity_manager import EntityManager
from .statistics_manager import StatisticsManager
from ..utils import deep_convert_to_native_types
from ..validation.schemas import WorldState as ValidatedWorldState
from pydantic import ValidationError

class StateManager:
    def __init__(self, entity_manager: EntityManager, stats_manager: StatisticsManager, world_info: Dict[str, Any]):
        self.entity_manager = entity_manager
        self.stats_manager = stats_manager
        self.world_info = world_info # width, height, version etc.
        self.session_id = str(uuid.uuid4())
        self.snapshot_dir = os.path.join("server", "sim_snapshots", self.session_id)
        os.makedirs(self.snapshot_dir, exist_ok=True)
        
        self.last_client_update_ticks: Dict[str, int] = {}

    def get_state_for_client(self, ticks: int, generation: int) -> Dict[str, Any]:
        """İstemci için sadece değişen ajanları ve genel durumu içeren hafif bir state döndürür."""
        agents = self.entity_manager.agents
        
        changed_agents = []
        for agent in agents:
            if agent.state.id not in self.last_client_update_ticks or self.last_client_update_ticks[agent.state.id] < agent.state.last_updated_tick:
                changed_agents.append(agent.to_dict())
                self.last_client_update_ticks[agent.state.id] = ticks

        current_agent_ids = {a.state.id for a in agents}
        dead_agent_ids = [agent_id for agent_id in self.last_client_update_ticks if agent_id not in current_agent_ids]
        for agent_id in dead_agent_ids:
            del self.last_client_update_ticks[agent_id]
            
        food_list = [{"id": f.id, "x": f.x, "y": f.y} for f in self.entity_manager.food]

        state = {
            "version": self.world_info.get("version", "N/A"),
            "type": "world_update",
            "payload": {
                "world_dimensions": { "width": self.world_info.get("width"), "height": self.world_info.get("height") },
                "ticks": ticks,
                "generation": generation,
                "population": len(agents),
                "avg_fitness": self.stats_manager.get_average_fitness(),
                "genetic_diversity": self.stats_manager.get_genetic_diversity(),
                "agents": changed_agents,
                "dead_agent_ids": dead_agent_ids,
                "food_sources": food_list
            }
        }
        return state

    def save_snapshot(self, ticks: int, generation: int):
        """Simülasyonun tam durumunu bir JSON dosyasına kaydeder."""
        if ticks % 2000 != 0 or ticks == 0:
            return
        
        full_state = self._get_full_state(ticks, generation)
        if not full_state:
            print("Kaydedilecek geçerli durum yok.")
            return

        gen_str = f"{generation:04d}"
        tick_str = f"{ticks:07d}"
        filename = f"gen_{gen_str}_tick_{tick_str}.json"
        filepath = os.path.join(self.snapshot_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(full_state, f, indent=2)
            print(f"Snapshot kaydedildi: {filepath}")
        except (IOError, TypeError) as e:
            print(f"ERROR: Snapshot kaydedilemedi: {e}")


    def _get_full_state(self, ticks: int, generation: int) -> Optional[Dict[str, Any]]:
        """Doğrulama ve snapshot için dünyanın tam ve detaylı durumunu döndürür."""
        agent_states_list = [a.state.to_dict() for a in self.entity_manager.agents]
        food_list = [{"id": f.id, "x": f.x, "y": f.y, "energy_value": f.energy_value} for f in self.entity_manager.food]

        state_data = {
            "agents": agent_states_list,
            "food": food_list,
            "world_info": {
                "version": self.world_info.get("version"),
                "session_id": self.session_id,
                "simulation_time_seconds": time.time() - self.world_info.get("start_time", time.time()),
                "ticks": ticks,
                "generation": generation,
                "population": len(agent_states_list),
            }
        }
        
        try:
            ValidatedWorldState.parse_obj(state_data)
            return deep_convert_to_native_types(state_data)
        except ValidationError as e:
            print(f"CRITICAL: Bilimsel veri doğrulama hatası! {e}")
            return None 