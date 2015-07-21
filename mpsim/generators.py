"""
Various generators useful for controlling simulations.
"""

import random

def random_seeds(a=1, b=99999999999):
    """
    Generates random seeds.
    """

    while True:
        yield random.randint(a, b)

def iterations_generator(total_iterations, per_run=10000):
    """
    Divides up the requested number of simulations into chunks so that
    results can be written to disk or processed. This avoids taking up huge
    amounts of RAM with the generated trajectories.
    """

    remaining = total_iterations
    while remaining > 0:
        iters = min(per_run, remaining)
        yield iters
        remaining -= per_run

def constant_generator(value):
    """
    Yields value indefinitely. Useful for specifying the same initial state
    repeatedly to simulations.
    """

    while True:
        yield value

def random_state_generator(states):
    """
    Yields random starting states (uniformly).
    """

    while True:
        yield random.choice(states)