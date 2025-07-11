from pydantic import BaseModel, Field
from typing import Optional

class BatchParamChangePayload(BaseModel):
    reproduction_threshold: Optional[float] = Field(None, gt=0, description="Minimum energy level for an agent to reproduce.")
    energy_efficiency: Optional[float] = Field(None, gt=0, description="Efficiency of converting food to energy.")
    detection_range: Optional[float] = Field(None, gt=0, description="The range at which an agent can detect other entities.")
    vision_range: Optional[float] = Field(None, gt=0, description="The maximum range of an agent's vision.")
    size: Optional[float] = Field(None, gt=0, description="The size of the agent.")
    speed: Optional[float] = Field(None, gt=0, description="The movement speed of the agent.")
    aggression: Optional[float] = Field(None, ge=0, le=1, description="The aggression level of the agent (0-1).")
    mutation_rate: Optional[float] = Field(None, ge=0, le=1, description="The rate at which mutations occur (0-1).")
    energy_decay: Optional[float] = Field(None, gt=0, description="The rate at which energy decays over time.")

    class Config:
        extra = "forbid" 