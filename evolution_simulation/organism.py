import numpy as np

from evolution_simulation.ecosystem import Ecosystem


class Organism():
    """Class representing an organism in an ecosystem.
    """

    def __init__(
        self,
        parameters: dict[str, float],
        random_seed: int = None,
    ) -> None:
        self.temperature_ideal = parameters['temperature_ideal']
        self.temperature_range = parameters['temperature_range']
        self.resistance = parameters['resistance']
        self.fertility = parameters['fertility']
        self.mutation_chance = parameters['mutation_chance']

        self.food_requirement = None
        self.mortality = None

        self.rng = np.random.default_rng(seed=random_seed)

    def calculate_food_requirement(self, ecosystem: Ecosystem) -> float:
        pass

    def calculate_fitness(self, ecosystem: Ecosystem) -> float:
        pass


class Pair():
    """Class representing a pair of Organisms that produces offspring.
    """

    def __init__(self, organism_a: Organism, organism_b: Organism) -> None:
        self.parent_a = organism_a
        self.parent_b = organism_b

        self.fertility = np.rint((self.parent_a.fertility + self.parent_b.fertility) / 2.0)

        self.mutation_chance = (self.parent_a.mutation_chance + self.parent_b.mutation_chance) / 2.0

        random_seed = (self.parent_a.rng.integers(1000000) + self.parent_b.rng.integers(1000000)) // 2
        self.rng = np.random.default_rng(seed=random_seed)

    def crossover_attribute(self, attribute_a: float, attribute_b: float, mutation_range: float = 0.1) -> float:
        crossover_weight = self.rng.uniform(endpoint=True)

        child_attribute = attribute_a * crossover_weight + attribute_b * (1 - crossover_weight)

        if self.rng.uniform() < self.mutation_chance:
            child_attribute *= self.rng.uniform(low=1 - mutation_range, high=1 + mutation_range, endpoint=True)

        return child_attribute

    def crossover(self, mutation_range: float = 0.1) -> Organism:

        child_parameters = {}

        child_parameters['temperature_ideal'] = self.crossover_attribute(self.parent_a.temperature_ideal,
                                                                         self.parent_b.temperature_ideal,
                                                                         mutation_range=mutation_range)

        child_parameters['temperature_range'] = self.crossover_attribute(self.parent_a.temperature_range,
                                                                         self.parent_b.temperature_range,
                                                                         mutation_range=mutation_range)

        child_parameters['resistance'] = self.crossover_attribute(self.parent_a.resistance,
                                                                  self.parent_b.resistance,
                                                                  mutation_range=mutation_range)

        child_parameters['fertility'] = self.crossover_attribute(self.parent_a.fertility,
                                                                 self.parent_b.fertility,
                                                                 mutation_range=mutation_range)

        child_parameters['mutation_chance'] = self.crossover_attribute(self.parent_a.mutation_chance,
                                                                       self.parent_b.mutation_chance,
                                                                       mutation_range=mutation_range)

        child_random_seed = self.rng.integers(1000000)

        return Organism(parameters=child_parameters, random_seed=child_random_seed)

    def produce_offspring(self) -> list[Organism]:
        offspring = []

        for _ in range(self.fertility):
            offspring.append(self.crossover())

        return offspring
