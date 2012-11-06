import cPickle as pickle
import datetime
import gc
import itertools
import multiprocessing
import random

import numpy

import generators
from math_helpers import normalize
from graph import Graph

def cumsum(l):
    "Cumulative summation."""
    a = numpy.array(l)
    return a.cumsum()

def load_cache(filename):
    """Unpickle a precompiled cache."""
    f = open(filename)
    cache = pickle.load(f)
    return cache

### Generators for simulations

# Each simulation requires a tuple of arguments for multiprocessing.        
def parameter_generator(cache, initial_state_gen, seed_gen=None, short_report=False, max_steps=10000, reverse_enumeration=True):
    """Yields parameters for simulations as needed for multiprocessing."""
    cache_gen = generators.constant_generator(cache)
    report_gen = generators.constant_generator(short_report)
    max_steps_gen = generators.constant_generator(max_steps)
    reverse_enumeration_gen = generators.constant_generator(reverse_enumeration)
    if not seed_gen:
        seed_gen = generators.random_seeds()
    return itertools.izip(cache_gen, initial_state_gen, seed_gen, report_gen, max_steps_gen, reverse_enumeration_gen)
        
### Cache and compilation. For efficiency, repeatedly needed calculations are cached.
            
def compile_edges(edges, verbose=True, cache_to_disk=False, filename=None):
    """This function takes a lists of edges and returns a compiled SimulationCache object to improve efficiency for batches of simulations."""
    if verbose:
        print "Building graph..."
    g = Graph()
    g.add_edges(edges)
    if verbose:
        print "Compiling graph..."
    cache = SimulationCache(g, verbose=verbose)
    if cache_to_disk:
        if not filename:
            now = datetime.datetime.now()
            filename = now.isoformat() + ".pickle"
        f = open(filename, 'w')
        if verbose:
            print "Pickling cache for future simulations."
        pickle.dump(cache, f)
    return cache

class SimulationCache(object):
    """Caches common calculations for a given graph to speed up repeated simulations."""
    def __init__(self, graph, verbose=True):
        # Caches vertex enumeration, cumulative sums, absorbing state tests, and transition targets.
        self.enum = dict()
        self.inv_enum = []
        self.csums = []
        self.out_neighbors = []
        self.absorbing = []
        vertices = graph.vertices()
        if verbose:
            print "  Enumerating States..."
        for (index, vertex) in enumerate(vertices):
            self.enum[vertex] = index
            self.inv_enum.append(vertex)
        if verbose:
            print "  Computing cumulative sums of outbound transition probabilities, detecting absorbing states, etc..."
        for vertex in vertices:
            out_dict = graph.out_dict(vertex)
            items = out_dict.items()
            self.csums.append(cumsum(normalize([v for k,v in items])))
            self.out_neighbors.append([self.enum[k] for k,v in items])
            self.absorbing.append(not out_dict)

# This function is used to select a neighboring state.
def fitness_proportionate_selection(csums, r):
    """Selects next transition from an array of cumulatively summed values and a random value r in [0,1)"""
    for j, x in enumerate(csums):
        if x >= r:
            return j

# This function is called by run_simulations and actually carries out the simulation.
def simulation(args):
    cache, initial_state, seed, short_report, max_steps, reverse_enumeration = args
    if not max_steps:
        max_steps = float("inf")
    # Generate a new random seed and begin history with it.
    srandom = random.Random()
    srandom.seed(seed)
    state = cache.enum[initial_state]
    history = [state]
    out_neighbors = cache.out_neighbors
    for iteration in itertools.count(1):
        # Exit conditions...
        if iteration >= max_steps:
            break
        # Is state absorbing?
        if cache.absorbing[state]:
            break
        # Choose next state.
        next_index = fitness_proportionate_selection(cache.csums[state], srandom.random())
        state = out_neighbors[state][next_index]
        if not short_report:
            history.append(state)
    if short_report:
        # Append the final state
        history.append(state)
    # report state sequence
    if reverse_enumeration:
        history = list(map(lambda x: cache.inv_enum[x], history))
    return (seed, iteration, history)

def run_simulations(param_gen, iters_gen, processes=None, call_backs=None, verbose=False, gc_aggressively=False):
    """Runs simulations on multiple processing cores in batch sizes dictated by iters_gen, posting data to callbacks to reduce memory footprint."""
    if not processes:
        processes = multiprocessing.cpu_count()
    total = 0
    all_results = []
    for iters in iters_gen:
        total += iters
        if verbose:
            print total,
        params = itertools.islice(param_gen, 0, iters)
        #print list(itertools.islice(params,0,1))
        pool = multiprocessing.Pool(processes=processes)
        try:
            results = pool.map(simulation, params)
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            print 'Control-C received. Exiting.'
            pool.terminate()
            exit()
        if call_backs:
            for call_back in call_backs:
                call_back(results)
        else:
            all_results.extend(results)
        # If simulations take up a large amount of memory, invoking the garbage collector more often can lower the footprint.
        if gc_aggressively:
            del results
            gc.collect()
    if verbose:
        print ""
    if not call_backs:
        return all_results
