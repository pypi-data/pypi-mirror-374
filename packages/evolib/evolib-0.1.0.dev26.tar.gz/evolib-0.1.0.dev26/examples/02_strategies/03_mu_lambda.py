"""
Example 2.2 - Mu Lambda

This example demonstrates the basic Mu Plus Lambda and Mu Comma Lambda evolution:
"""

from evolib import Indiv, Pop, mse_loss, simple_quadratic
from evolib.operators.strategy import evolve_mu_plus_lambda


# User-defined fitness function
def my_fitness(indiv: Indiv) -> None:
    """Simple fitness function using the quadratic benchmark and MSE loss."""
    expected = 0.0
    predicted = simple_quadratic(indiv.para["test-vector"].vector)
    indiv.fitness = mse_loss(expected, predicted)


def print_population(pop: Pop, title: str) -> None:
    print(f"{title}")
    for i, indiv in enumerate(pop.indivs):
        print(
            f"  Indiv {i}: Parameter = {indiv.para['test-vector'].vector},"
            f"Fitness = {indiv.fitness:.6f}"
        )


# Create and initializes the population.
pop = Pop("population.yaml")

# Set fitnessfuction
pop.set_functions(fitness_function=my_fitness)

# Evaluate fitness
pop.evaluate_fitness()

print_population(pop, "Initial Parents")

# Mu Plus Lambda
for gen in range(pop.max_generations):
    evolve_mu_plus_lambda(pop)
    pop.print_status()
