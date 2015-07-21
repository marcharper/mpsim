import cPickle as pickle
import datetime
import itertools
import multiprocessing
import random

import generators
from math_helpers import normalize, cumsum
from graph import Graph

def load_cache(filename):
    """
    Unpickle a precompiled cache.
    """

    f = open(filename)
    cache = pickle.load(f)
    return cache

### Generators for simulations

# Each simulation requires a tuple of arguments for use with multiprocessing.
def parameter_generator(cache, initial_state_gen, seed_gen=None,
                        max_steps=10000):
    """
    Combines generators to yield parameters for simulations as needed for
    multiprocessing.
    """

    cache_gen = generators.constant_generator(cache)
    max_steps_gen = generators.constant_generator(max_steps)
    if not seed_gen:
        seed_gen = generators.random_seeds()
    return itertools.izip(cache_gen, initial_state_gen, seed_gen, max_steps_gen)

### Cache and compilation. For efficiency, repeatedly needed calculations are cached.

def compile_edges(edges, cache_to_disk=False, filename=None):
    """
    Compiles lists of edges into an SimuulationCache object that caches common
    computations needed for producing many sample sequences.
    """

    g = Graph()
    g.add_edges(edges)
    cache = SimulationCache(g, verbose=verbose)
    if cache_to_disk:
        if not filename:
            now = datetime.datetime.now()
            filename = now.isoformat() + ".pickle"
        f = open(filename, 'w')
        pickle.dump(cache, f)
    return cache


class SimulationCache(object):
    """
    Caches common calculations for a given graph to speed up repeated
    simulations.
    """

    def __init__(self, graph):
        # Caches vertex enumeration, cumulative sums, absorbing state tests, and transition targets.
        self.enum = dict()
        self.inv_enum = []
        self.csums = []
        self.out_neighbors = []
        self.absorbing = []
        vertices = graph.vertices()

        # Enumerate states amd save the reverse enumeration
        for (index, vertex) in enumerate(vertices):
            self.enum[vertex] = index
            self.inv_enum.append(vertex)

        # Cache various computations -- cumulative sums, out_neighbors
        # Also detect absorbing states
        for vertex in vertices:
            out_dict = graph.out_dict(vertex)
            items = out_dict.items()
            self.csums.append(cumsum(normalize([v for k,v in items])))
            self.out_neighbors.append([self.enum[k] for k,v in items])
            self.absorbing.append(not out_dict)

def fitness_proportionate_selection(csums, r=None):
    """
    Selects next transition from an array of cumulatively summed values
    and a random value r in [0,1). Used to select the next state in the
    generation of Markov trajectories.
    """

    if not r:
        r = random.random()

    # Iterate through the cumulative sums (<= 1) to select a random value from
    # the original list (that was cumulatively-summed)
    for j, x in enumerate(csums):
        if x >= r:
            return j

# This function is called by run_simulations and actually carries out the simulation.
def simulation(cache, initial_state, random_seed=None, max_steps=None):
    """
    Generates simulated trajectories for the Markov process that produced
    the simulation cache object.
    """

    if not max_steps:
        max_steps = float("inf")
    if not random_seed:
        random_seed = random.randint(0, 100000000000)
    # Generate a new random value source (for reproducibility)
    srandom = random.Random()
    srandom.seed(random_seed)
    # Start the trajectory with the initial state
    state = cache.enum[initial_state]
    history = [state]
    # Start simulating
    out_neighbors = cache.out_neighbors
    for iteration in itertools.count(1):
        ## Check exit conditions
        # Did we exceed the maximum number of states
        if iteration >= max_steps:
            break
        # Have we reached an absorbing state?
        if cache.absorbing[state]:
            break
        # Choose next state.
        r = srandom.random()
        csums = cache.csums[state]
        next_index = fitness_proportionate_selection(csums, r)
        state = out_neighbors[state][next_index]
        history.append(state)
    # Reverse the enumeration of states before returning to the user
    inv_history = list(map(lambda x: cache.inv_enum[x], history))
    return (random_seed, iteration, inv_history)

def batched_simulations(param_gen, iters_gen, processes=None, call_backs=None):
    """
    Computes simulated trajectories using multiple processors, if available, in
    batches using multiprocessing.
    """

    if not processes:
        processes = multiprocessing.cpu_count()
    total = 0
    all_results = []
    for iters in iters_gen:
        total += iters
        params = itertools.islice(param_gen, 0, iters)
        pool = multiprocessing.Pool(processes=processes)
        try:
            results = pool.map(simulation, params)
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            print 'Control-C received. Exiting.'
            pool.terminate()
            exit()
        # Pass generated sequences to callbacks or append to history
        if call_backs:
            for call_back in call_backs:
                call_back(results)
        else:
            all_results.extend(results)
    if not call_backs:
        return all_results
