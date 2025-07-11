import numpy as np
import copy
from typing import List, Tuple
from .agent import Agent, AgentGenes
import uuid

def _crossover_genes(genes1: AgentGenes, genes2: AgentGenes) -> AgentGenes:
    """İki ebeveynin genlerini birleştirerek yeni bir gen seti oluşturur."""
    
    # Beyin ağırlıkları için tek noktalı çaprazlama
    weights1 = np.array(genes1.brain_weights)
    weights2 = np.array(genes2.brain_weights)
    child_weights = weights1 # Başlangıç olarak ilk ebeveyni al
    if len(weights1) > 1 and len(weights2) > 1:
        crossover_point = np.random.randint(1, len(weights1) - 1)
        child_weights = np.concatenate([weights1[:crossover_point], weights2[crossover_point:]])

    return AgentGenes(
        reproduction_threshold=(genes1.reproduction_threshold + genes2.reproduction_threshold) / 2,
        energy_efficiency=(genes1.energy_efficiency + genes2.energy_efficiency) / 2,
        detection_range=(genes1.detection_range + genes2.detection_range) / 2,
        speed=(genes1.speed + genes2.speed) / 2,
        aggression=(genes1.aggression + genes2.aggression) / 2,
        mutation_rate=(genes1.mutation_rate + genes2.mutation_rate) / 2,
        energy_decay=(genes1.energy_decay + genes2.energy_decay) / 2,
        vision_range=(genes1.vision_range + genes2.vision_range) / 2, # Eksik parametre eklendi
        size=(genes1.size + genes2.size) / 2, # Eksik parametre eklendi
        brain_weights=list(child_weights)
    )

def _mutate_genes(genes: AgentGenes, mutation_strength: float) -> AgentGenes:
    """Bir ajanın genlerini, kendi mutasyon oranına göre değiştirir."""
    new_genes = copy.deepcopy(genes)
    mutation_rate = new_genes.mutation_rate
    
    if np.random.rand() < mutation_rate:
        # Standart genleri mutasyona uğrat
        new_genes.reproduction_threshold += np.random.normal(0, 0.1) * mutation_strength * 5
        new_genes.energy_efficiency += np.random.normal(0, 0.1) * mutation_strength * 0.1
        new_genes.detection_range += np.random.normal(0, 0.1) * mutation_strength * 10
        new_genes.speed += np.random.normal(0, 0.1) * mutation_strength * 5
        new_genes.aggression = np.clip(new_genes.aggression + np.random.normal(0, 0.1) * mutation_strength, 0, 1)
    
    # Beyin ağırlıklarını mutasyona uğrat
    brain_weights = np.array(new_genes.brain_weights)
    mutation_mask = np.random.rand(*brain_weights.shape) < mutation_rate
    mutations = np.random.normal(0, mutation_strength, brain_weights.shape) * mutation_mask
    new_genes.brain_weights = list(brain_weights + mutations)

    return new_genes

def evolve_population(
    population: List[Agent], 
    num_offspring: int,
    mutation_strength: float
) -> List[Agent]:
    """
    Verilen bir popülasyonu evrimleştirir: Elitizm, Çaprazlama ve Mutasyon.
    """
    if not population:
        return []

    # Fitness'a göre sırala (daha yüksek enerji, yaş ve yavru sayısı daha iyi)
    sorted_population = sorted(population, key=lambda agent: agent.state.energy + agent.state.offspring_count * 10, reverse=True)
    
    # 1. Elitizm: En iyi %10'u doğrudan bir sonraki jenerasyona taşı
    elite_count = max(1, len(sorted_population) // 10)
    elites = sorted_population[:elite_count]
    
    # 2. Çaprazlama (Crossover)
    offspring = []
    parent_pool = elites if elites else sorted_population # Elit yoksa tüm popülasyonu kullan
    
    for _ in range(num_offspring):
        if len(parent_pool) < 2:
            parent1 = parent_pool[0]
            parent2 = parent_pool[0]
        else:
            parent_array = np.array(parent_pool)
            parent1, parent2 = np.random.choice(parent_array, 2, replace=False)
        
        # Genleri çaprazla ve mutasyona uğrat
        child_genes = _crossover_genes(parent1.state.genes, parent2.state.genes)
        child_genes = _mutate_genes(child_genes, mutation_strength)
        
        # Yeni yavruyu oluştur
        child = Agent(
            x=parent1.state.x + np.random.uniform(-20, 20),
            y=parent1.state.y + np.random.uniform(-20, 20),
            generation=parent1.state.generation + 1,
            genes=child_genes
        )
        offspring.append(child)
        
    next_generation: List[Agent] = []
    for agent in elites:
        # Elitlerin durumunu sıfırla (enerji, yaş vb.)
        agent.state.energy = 100.0
        agent.state.age = 0
        agent.state.offspring_count = 0
        next_generation.append(agent)

    return next_generation + offspring 