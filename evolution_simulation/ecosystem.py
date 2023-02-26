"""Module containing environment and related classes for evolution simulation."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import truncnorm

from evolution_simulation.organism import Organism, Pair
from evolution_simulation.utils import calculate_truncnorm_a_and_b, resolve_ecosystem_attribute_parameters, get_evolution_step_dataframe


class EcosystemAttribute():
    """Class representing any attribute of an ecosystem.
    """

    def __init__(self, parameters: dict[str, float], random_seed: int = None) -> None:

        mean, std, min_value, max_value, volatility = resolve_ecosystem_attribute_parameters(parameters)

        self.update_distribution(mean=mean, std=std, min_value=min_value, max_value=max_value)

        self.volatility = float(volatility)

        if self.volatility is None:
            self.volatility = self.std

        self.value_development = None
        self.current_value = None

        self.rng = np.random.default_rng(seed=random_seed)

    def update_distribution(self, mean: float, std: float, min_value: float = None, max_value: float = None) -> None:
        """Update the distribution of this attribute.

        The distribution is a truncated normal distribution implemented with `scipy.stats.truncnorm`. If
        min_value and max_value are not set, they default to three standard deviations in both directions
        from the mean.

        Args:
            mean (float): Mean value of the distribution.
            std (float): Standard deviation of the distribution.
            min_value (float, optional): Minimum value. Defaults to None.
            max_value (float, optional): Maximum value. Defaults to None.
        """
        self.mean = float(mean)
        self.std = float(std)
        self.min_value = float(min_value)
        self.max_value = float(max_value)

        if self.min_value is None:
            self.min_value = self.mean - 3.0 * self.std

        if self.max_value is None:
            self.max_value = self.mean + 3.0 * self.std

        a, b = calculate_truncnorm_a_and_b(mean=self.mean,
                                           std=self.std,
                                           min_value=self.min_value,
                                           max_value=self.max_value)

        self.distribution = truncnorm(a=a, b=b, loc=mean, scale=std)

    def initialize_random_values(self, n: int) -> None:
        """Initialize a list of values from a truncated normal distribution and corrects them so the
        step width is not larger than the attributes volatility.

        Args:
            n (int): Number of values.
        """
        generated_random_values = self.distribution.rvs(size=n, random_state=self.rng.integers(1000000))

        corrected_random_values = [generated_random_values[0]]

        for i in range(1, n):
            if abs(generated_random_values[i] - corrected_random_values[i - 1]) <= self.volatility:
                corrected_random_values.append(generated_random_values[i])
            elif generated_random_values[i] > corrected_random_values[i - 1]:
                corrected_random_values.append(corrected_random_values[i - 1] + self.volatility)
            else:
                corrected_random_values.append(corrected_random_values[i - 1] - self.volatility)

        self.value_development = corrected_random_values

    def iterate_value(self, i: int) -> None:
        """Set the current value to the value at a specific index in the value development.

        Args:
            i (int): Index (or iteration step).
        """
        self.current_value = self.value_development[i]


class Ecosystem():
    """Class representing an ecosystem.
    """

    def __init__(self, parameters: dict[str, dict[str, float]], random_seed: int = None) -> None:

        required_attributes = ['temperature', 'hazard_rate', 'food']

        for attribute in required_attributes:
            if attribute not in parameters.keys():
                raise ValueError(f'Required attribute {attribute} was not found in dictionary. Got {parameters.keys()}')

        self.rng = np.random.default_rng(seed=random_seed)

        self.temperature = EcosystemAttribute(parameters=parameters['temperature'],
                                              random_seed=self.rng.integers(1000000))

        self.hazard_rate = EcosystemAttribute(parameters=parameters['hazard_rate'],
                                              random_seed=self.rng.integers(1000000))

        self.food = EcosystemAttribute(parameters=parameters['food'], random_seed=self.rng.integers(1000000))

        self.utilized_food = 0

        self.organisms = None

    def initialize_attribute_values(self, n: int) -> None:
        self.temperature.initialize_random_values(n=n)
        self.hazard_rate.initialize_random_values(n=n)
        self.food.initialize_random_values(n=n)

    def iterate_attribute_values(self, i: int) -> None:
        self.temperature.iterate_value(i=i)
        self.hazard_rate.iterate_value(i=i)
        self.food.iterate_value(i=i)

    def initialize_organism_attribute_distribution_values(self, parameters: dict[str, float],
                                                          n: int) -> np.ndarray[float]:
        mean = float(parameters['mean'])
        std = float(parameters['std'])
        min_value = float(parameters['min_value'])
        max_value = float(parameters['max_value'])

        a, b = calculate_truncnorm_a_and_b(mean=mean, std=std, min_value=min_value, max_value=max_value)

        return truncnorm(a=a, b=b, loc=mean, scale=std).rvs(size=n, random_state=self.rng.integers(1000000))

    def initialize_organisms(self, parameters: dict[str, dict[str, float]], n: int) -> None:

        temperature_ideal_values = self.initialize_organism_attribute_distribution_values(
            parameters=parameters['temperature_ideal'], n=n)

        temperature_range_values = self.initialize_organism_attribute_distribution_values(
            parameters=parameters['temperature_range'], n=n)

        resilience_values = self.initialize_organism_attribute_distribution_values(parameters=parameters['resilience'],
                                                                                   n=n)

        fertility_values = self.initialize_organism_attribute_distribution_values(parameters=parameters['fertility'],
                                                                                  n=n)

        mutation_chance_values = self.initialize_organism_attribute_distribution_values(
            parameters=parameters['mutation_chance'], n=n)

        self.organisms = []

        for i in range(n):
            new_organism_parameters = {
                'temperature_ideal': temperature_ideal_values[i],
                'temperature_range': temperature_range_values[i],
                'resilience': resilience_values[i],
                'fertility': fertility_values[i],
                'mutation_chance': mutation_chance_values[i],
            }

            self.organisms.append(Organism(parameters=new_organism_parameters, random_seed=self.rng.integers(1000000)))

    def simulate_evolution(self, n: int) -> pd.DataFrame:
        if self.organisms is None:
            raise ValueError('No organisms have been initialized. Please call initialize_organisms first.')

        print(f'Initializing evolution simulation starting with {len(self.organisms)} organisms for {n} generations...')
        print()

        self.initialize_attribute_values(n=n)

        df = pd.DataFrame(columns=[
            'iteration',
            'temperature',
            'hazard_rate',
            'available_food',
            'number_organisms',
            'temperature_ideal_mean',
            'temperature_ideal_std',
            'temperature_range_mean',
            'temperature_range_std',
            'resilience_mean',
            'resilience_std',
            'fertility_mean',
            'fertility_std',
            'mutation_chance_mean',
            'mutation_chance_std',
            'food_requirement_mean',
            'food_requirement_std',
            'fitness_mean',
            'fitness_std',
        ])

        for i in range(n):
            next_generation = []

            self.iterate_attribute_values(i=i)

            for organism in self.organisms:
                organism.calculate_food_requirement(ecosystem=self)
                organism.calculate_fitness(ecosystem=self)

                if organism.fitness < self.rng.uniform():
                    organism.survives = False

            step_df = get_evolution_step_dataframe(ecosystem=self, organisms=self.organisms, i=i)
            df = pd.concat([df, step_df], ignore_index=True)

            surviving_organisms = [organism for organism in self.organisms if organism.survives]

            if len(surviving_organisms) < 2:
                print(
                    f'Stopping simulation early because the number of organisms is insufficient for reproduction after {i} years.'
                )
                break

            # not reversing (sorting descending) because pop returns last element
            surviving_organisms.sort(key=lambda x: x.fitness)

            reproducing_organisms = []

            while self.utilized_food < self.food.current_value and len(surviving_organisms) > 0:
                reproducing_organism = surviving_organisms.pop()
                self.utilized_food += reproducing_organism.food_requirement

                reproducing_organisms.append(reproducing_organism)

            self.rng.shuffle(reproducing_organisms)

            pairs = []

            while len(reproducing_organisms) > 1:
                organism_a = reproducing_organisms.pop()
                organism_b = reproducing_organisms.pop()

                pairs.append(Pair(organism_a=organism_a, organism_b=organism_b))

            for pair in pairs:
                next_generation.extend(pair.produce_offspring())

            self.organisms = next_generation
            self.utilized_food = 0
            print(f'Generation {i + 1} consists of {len(self.organisms)} organisms.')

        return df
