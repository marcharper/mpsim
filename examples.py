# -*- coding: utf-8 -*-

import mpsim
from matplotlib import pyplot

def example_1():
    """
    Runs a basic simulation.
    """

    edges = [('a', 'b', 0.5), ('a', 'a', 0.5), ('b', 'a', 0.8),
             ('b', 'b', 0.1), ('b', 'c', 0.1)]
    cache = mpsim.compile_edges(edges)
    random_seed, iterations, trajectory = mpsim.simulation(cache, initial_state='a')
    print "".join(trajectory)

def example_2():
    """
    Runs many batched simulations.
    """

    edges = [('a', 'b', 0.5), ('a', 'a', 0.5), ('b', 'a', 0.8),
             ('b', 'b', 0.1), ('b', 'c', 0.1)]
    cache = mpsim.compile_edges(edges)

    # Set up generators for batched processing
    initial_state_gen = mpsim.generators.constant_generator('a')
    parameter_gen = mpsim.generators.parameter_generator(cache, initial_state_gen)
    iters_gen = mpsim.generators.iterations_generator(100000)
    results = mpsim.batched_simulations(parameter_gen, iters_gen)

    # Plot the results
    lengths = [len(trajectory) for (_, _, trajectory) in results]
    pyplot.hist(lengths, bins=30)
    pyplot.show()

def example_3():
    """
    Runs many batched simulations, processing trajectories using a callback
    to reduce memory overhead.
    """

    edges = [('a', 'b', 0.5), ('a', 'a', 0.5), ('b', 'a', 0.8),
             ('b', 'b', 0.1), ('b', 'c', 0.1)]
    cache = mpsim.compile_edges(edges)

    # Set up generators for batched processing
    initial_state_gen = mpsim.generators.constant_generator('a')
    parameter_gen = mpsim.generators.parameter_generator(cache, initial_state_gen)
    iters_gen = mpsim.generators.iterations_generator(100000)
    callback_obj = mpsim.callbacks.RunLengthRecorder()
    
    results = mpsim.batched_simulations(parameter_gen, iters_gen,
                                        callback=callback_obj.add)
    lengths = callback_obj.lengths
    pyplot.hist(lengths, bins=30)
    pyplot.show()

if __name__ == '__main__':
    example_1()
    example_2()
    example_3()
