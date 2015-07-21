"""
Various generators useful for controlling simulations.
"""

import itertools
import random

def random_seed(a=1, b=99999999999):
    """
    Returns a random seed.
    """

    return random.randint(a, b)

def random_seed_generator(a=1, b=99999999999):
    """
    Generates random seeds.
    """

    while True:
        yield random_seed(a=a, b=b)

### Generators for simulations

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

def iterations_generator(total_iterations, per_run=1000):
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

def parameter_generator(cache, initial_state_gen, seed_gen=None,
                        max_steps=10000):
    """
    Combines generators to yield parameters for simulations as needed for
    multiprocessing.
    """

    cache_gen = constant_generator(cache)
    max_steps_gen = constant_generator(max_steps)
    if not seed_gen:
        seed_gen = random_seed_generator()
    return itertools.izip(cache_gen, initial_state_gen, seed_gen, max_steps_gen)
