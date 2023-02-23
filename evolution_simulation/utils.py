"""Module containing various helper function for evolution simulation.
"""


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
