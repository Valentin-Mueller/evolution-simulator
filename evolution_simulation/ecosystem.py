"""Module containing environment and related classes for evolution simulation."""
import numpy as np
from scipy.stats import truncnorm

from evolution_simulation.utils import calculate_truncnorm_a_and_b, resolve_ecosystem_attribute_parameters


class EcosystemAttribute():
    """Class representing any attribute of an ecosystem.
    """

    def __init__(
        self,
        parameters: dict[str, float],
        random_seed: int = None,
    ) -> None:
        mean, std, min_value, max_value, volatility = resolve_ecosystem_attribute_parameters(parameters)

        self.update_distribution(mean=mean, std=std, min_value=min_value, max_value=max_value)

        self.volatility = volatility

        if self.volatility is None:
            self.volatility = self.std

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
        self.mean = mean
        self.std = std
        self.min_value = min_value
        self.max_value = max_value

        if self.min_value is None:
            self.min_value = mean - 3.0 * std

        if self.max_value is None:
            self.max_value = mean + 3.0 * std
        else:
            self.max_value = max_value

        a, b = calculate_truncnorm_a_and_b(mean=self.mean,
                                           std=self.std,
                                           min_value=self.min_value,
                                           max_value=self.max_value)

        self.distribution = truncnorm(a=a, b=b, loc=mean, scale=std)

    def get_random_values(self, n: int) -> list[float]:
        """Sample values from a truncated normal distribution and corrects them so the step width is
        not larger than the attributes volatility.

        Args:
            n (int): Number of values.

        Returns:
            list[float]: List containing the values.
        """
        generated_random_values = self.distribution.rvs(size=n, random_state=self.rng.integers(10000))

        corrected_random_values = [generated_random_values[0]]

        for i in range(1, n):
            if abs(generated_random_values[i] - corrected_random_values[i - 1]) <= self.volatility:
                corrected_random_values.append(generated_random_values[i])
            elif generated_random_values[i] > corrected_random_values[i - 1]:
                corrected_random_values.append(corrected_random_values[i - 1] + self.volatility)
            else:
                corrected_random_values.append(corrected_random_values[i - 1] - self.volatility)

        return corrected_random_values


class Ecosystem():
    """Class representing an ecosystem.
    """

    def __init__(self, parameters: dict[str, dict[str, float]]) -> None:
        required_attributes = ['temperature', 'hazard_rate', 'food']

        for attribute in required_attributes:
            if attribute not in parameters.keys():
                raise ValueError(f'Required attribute {attribute} was not found in dictionary. Got {parameters.keys()}')

        self.temperature = EcosystemAttribute(parameters=parameters['temperature'])

        self.hazard_rate = EcosystemAttribute(parameters=parameters['hazard_rate'])

        self.food = EcosystemAttribute(parameters=parameters['food'])
