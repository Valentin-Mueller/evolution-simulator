# Evolution Simulator

Exploring the problem of evolution with genetic algorithms.

This project was initially created as an assignment in the course AI at DHBW Mannheim, but further development is possible.

## Requirements

This project utilizes `python>=3.10`.

All requrements are included in the file [requirements.txt](requirements.txt) and can be installed with the following command:

```
pip install -r requirements.txt
```

## Functionality

This repository explores the use of genetic algorithms in a vastly simplified simulation of evolution. An ecosystem serves as simulation environment, while organisms are improved with a genertic algorithm with the goal of survival. Fitness serves as a reverse loss function that needs to be optimized, while the available food limits both the total number of organisms and their parameters, since bigger ranges or higher values lead to higher food requirements.

Currently, only natural selection affects the outcome. Sexual selection is not yet taken into consideration.

All logic is implemented in the package [evolution_simulation](evolution_simulation/) and the respective classes. The notebook [Simulate_Evolution.ipynb](Simulate_Evolution.ipynb) contains an demo for the usage that can be adjusted as desired.

## Ideas for Simulation Parameter Tweaks

- Reduce the mutation chance to show its influence on fitness and thus importance in evolution
- Reduce fertility to require more specialized offspring
- Increase volatility and/or standard deviations
- Make generation 0 organisms more/less variable

## Ideas for Improvement or Expansion

- Tweak/optimize parameters for food requirement and fitness
- Include sexual selection on top of natural selection
- Allow simulation for multiple competing organisms
- ...
