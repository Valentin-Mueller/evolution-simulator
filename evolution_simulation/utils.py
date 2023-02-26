"""Module containing various helper function for evolution simulation.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from evolution_simulation.ecosystem import Ecosystem
    from evolution_simulation.organism import Organism


def calculate_truncnorm_a_and_b(mean: float, std: float, min_value: float, max_value: float) -> tuple[float, float]:
    """Calculate a and b as required by `scipy.stats.truncnorm`.

    Args:
        mean (float): Mean of the distribution.
        std (float): Standard deviation of the distribution.
        min_value (float): Min value for truncation.
        max_value (float): Max value for truncation.

    Returns:
        tuple[float, float]: a and b as needed for `scipy.stats.truncnorm`.
    """
    a = (min_value - mean) / std
    b = (max_value - mean) / std
    return a, b


def resolve_ecosystem_attribute_parameters(
        parameters: dict[str, float]) -> tuple[float, float, float | None, float | None, float | None]:
    """Resolve the parameters for an ecosystem attribute from the parameter dictionary.

    Resolves min_value, max_value and volatility being optional.

    Args:
        parameters (dict[str, dict[str, float]]): Dictionary containing the attributes and their parameters.

    Returns:
        tuple[float, float, float | None, float | None, float | None]: Mean, std, min_value, max_value and volatility.
    """
    mean = parameters['mean']
    std = parameters['std']

    try:
        min_value = parameters['min_value']
    except KeyError:
        min_value = None

    try:
        max_value = parameters['max_value']
    except KeyError:
        max_value = None

    try:
        volatility = parameters['volatility']
    except KeyError:
        volatility = None

    return mean, std, min_value, max_value, volatility


def get_evolution_step_dataframe(ecosystem: Ecosystem, organisms: list[Organism]) -> pd.DataFrame:
    data = {}

    data['temperature'] = ecosystem.temperature.current_value
    data['hazard_rate'] = ecosystem.hazard_rate.current_value
    data['food'] = ecosystem.hazard_rate.current_value

    temperature_ideal_values = [organism.temperature_ideal for organism in organisms]
    temperature_range_values = [organism.temperature_range for organism in organisms]
    resilience_values = [organism.resilience for organism in organisms]
    fertility_values = [organism.fertility for organism in organisms]
    mutation_chance_values = [organism.mutation_chance for organism in organisms]
    food_requirement_values = [organism.food_requirement for organism in organisms]
    fitness_values = [organism.fitness for organism in organisms]

    data['temperature_ideal_mean'] = np.mean(temperature_ideal_values)
    data['temperature_ideal_std'] = np.std(temperature_ideal_values)

    data['temperature_range_mean'] = np.mean(temperature_range_values)
    data['temperature_range_std'] = np.std(temperature_range_values)

    data['resilience_mean'] = np.mean(resilience_values)
    data['resilience_std'] = np.std(resilience_values)

    data['fertility_mean'] = np.mean(fertility_values)
    data['fertility_std'] = np.std(fertility_values)

    data['mutation_chance_mean'] = np.mean(mutation_chance_values)
    data['mutation_chance_std'] = np.std(mutation_chance_values)

    data['food_requirement_mean'] = np.mean(food_requirement_values)
    data['food_requirement_std'] = np.std(food_requirement_values)

    data['fitness_mean'] = np.mean(fitness_values)
    data['fitness_std'] = np.std(fitness_values)

    return pd.DataFrame.from_dict(data=[data])
