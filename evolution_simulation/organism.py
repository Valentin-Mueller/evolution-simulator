"""Module containing organisms and related classes for evolution simulation."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from evolution_simulation.ecosystem import Ecosystem


class Organism():
    """Class representing an organism in an ecosystem.
    """

    def __init__(self, parameters: dict[str, float], random_seed: int = None) -> None:

        self.temperature_ideal = float(parameters['temperature_ideal'])
        self.temperature_range = float(parameters['temperature_range'])
        self.resilience = float(parameters['resilience'])
        self.fertility = float(parameters['fertility'])
        self.mutation_chance = float(parameters['mutation_chance'])

        self.survives = True

        self.food_requirement = None
        self.fitness = None

        self.rng = np.random.default_rng(seed=random_seed)

    def calculate_food_requirement(self, ecosystem: Ecosystem) -> None:
        temperature_range_ecosystem = ecosystem.temperature.max_value - ecosystem.temperature.min_value
        temperature_range_organism = self.temperature_range * 2

        temperature_tolerance_coefficient = temperature_range_organism / temperature_range_ecosystem

        food_requirement = 1
        food_requirement *= temperature_tolerance_coefficient * 3
        food_requirement *= 0.5 + self.resilience
        food_requirement *= self.fertility / 2.0

        self.food_requirement = food_requirement

    def calculate_fitness(self, ecosystem: Ecosystem) -> None:

        if (ecosystem.temperature.current_value >= self.temperature_ideal - self.temperature_range) and (
                ecosystem.temperature.current_value <= self.temperature_ideal + self.temperature_range):
            base_value = 0.75
        else:
            base_value = 0.25

        fitness = base_value + min([max([self.resilience - ecosystem.hazard_rate.current_value, 0.0]), 0.25])
        self.fitness = fitness


class Pair():
    """Class representing a pair of organisms that produces offspring.
    """

    def __init__(self, organism_a: Organism, organism_b: Organism) -> None:

        self.parent_a = organism_a
        self.parent_b = organism_b

        self.fertility = int(np.rint((self.parent_a.fertility + self.parent_b.fertility) / 2.0))

        self.mutation_chance = (self.parent_a.mutation_chance + self.parent_b.mutation_chance) / 2.0

        random_seed = (self.parent_a.rng.integers(1000000) + self.parent_b.rng.integers(1000000)) // 2
        self.rng = np.random.default_rng(seed=random_seed)

    def calculate_crossover_attribute(self,
                                      attribute_a: float,
                                      attribute_b: float,
                                      mutation_range: float = 0.1) -> float:

        crossover_weight = self.rng.uniform()

        child_attribute = attribute_a * crossover_weight + attribute_b * (1 - crossover_weight)

        if self.rng.uniform() < self.mutation_chance:
            child_attribute *= self.rng.uniform(low=1 - mutation_range, high=1 + mutation_range)

        return child_attribute

    def crossover(self, mutation_range: float = 0.1) -> Organism:

        child_parameters = {}

        child_parameters['temperature_ideal'] = self.calculate_crossover_attribute(self.parent_a.temperature_ideal,
                                                                                   self.parent_b.temperature_ideal,
                                                                                   mutation_range=mutation_range)

        child_parameters['temperature_range'] = self.calculate_crossover_attribute(self.parent_a.temperature_range,
                                                                                   self.parent_b.temperature_range,
                                                                                   mutation_range=mutation_range)

        child_parameters['resilience'] = self.calculate_crossover_attribute(self.parent_a.resilience,
                                                                            self.parent_b.resilience,
                                                                            mutation_range=mutation_range)

        child_parameters['fertility'] = self.calculate_crossover_attribute(self.parent_a.fertility,
                                                                           self.parent_b.fertility,
                                                                           mutation_range=mutation_range)

        child_parameters['mutation_chance'] = self.calculate_crossover_attribute(self.parent_a.mutation_chance,
                                                                                 self.parent_b.mutation_chance,
                                                                                 mutation_range=mutation_range)

        child_random_seed = self.rng.integers(1000000)

        return Organism(parameters=child_parameters, random_seed=child_random_seed)

    def produce_offspring(self) -> list[Organism]:
        """Produce offspring.

        The number produced depends on the fertility of the pair, which depends on both parents.

        Returns:
            list[Organism]: The offspring organisms as a list.
        """
        offspring = []

        for _ in range(self.fertility):
            offspring.append(self.crossover())

        return offspring
