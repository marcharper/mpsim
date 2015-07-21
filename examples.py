# -*- coding: utf-8 -*-
import csv
import math
import os
import random
import sys

import numpy
import pylab

import callbacks
import generators
import graph
import simulation
import moran
import ternary
from math_helpers import normalize, normalize_dictionary, shannon_entropy
from helpers import ensure_digits, ensure_directory

def basic_simulation_run(cache, iteration_gen, initial_state_generator, call_backs=None, max_steps=None, short_report=False):
    param_gen = simulation.parameter_generator(cache, initial_state_generator, max_steps=max_steps, short_report=short_report)
    all_results = simulation.run_simulations(param_gen, iteration_gen, call_backs=call_backs)
    return all_results

#edge_function = generalized_moran_simulation_transitions
def two_type_moran_process_simulations(N=40, fitness_landscape=None, initial_state_generator=None, edge_function=None, iterations=10000, per_run=100000, verbose=False, call_backs=None, death_probabilities=None):
    if not fitness_landscape:
        fitness_landscape = moran.fitness_static(2.)
    if not edge_function:
        edge_function = moran.moran_simulation_transition
    if not initial_state_generator:
        initial_state_generator = generators.random_state_generator(2,N)
    # Not all edge functions accept death probabilities (in particular, pure moran doesn't).
    if death_probabilities:
        edges = edge_function(N, fitness_landscape, death_probabilities=death_probabilities)
    else:
        edges = edge_function(N, fitness_landscape)
    cache = simulation.compile_edges(edges, verbose=False)
    igen = generators.iterations_generator(iterations, per_run)
    param_gen = simulation.parameter_generator(cache, initial_state_generator, max_steps=100000)
    runs = basic_simulation_run(cache, igen, initial_state_generator, call_backs=None, max_steps=None, short_report=False)
    return runs 

## Run length estimators ##

def run_lengths(cache, iteration_gen, initial_state_generator, max_steps=1000000):
    rlc = callbacks.RunLengthRecorder()
    call_backs = [rlc.add]
    basic_simulation_run(cache, igen, initial_state_generator, call_backs=call_backs, max_steps=max_steps, short_report=True)
    return rlc.lengths

def run_length_batches(Ns=range(6, 60, 3), brange=numpy.arange(0,5.01, 0.1), a=1, iterations=16000, per_run=800, output_directory="rsp_run_lengths"):
    """Cache data for RSP games for later analysis."""
    import gc
    ensure_directory(output_directory)
    run_params = []
    for N in Ns:
        for b in brange:
            gc.collect()
            print N, b
            m = moran.rock_scissors_paper(a=a, b=b)
            fitness_landscape = moran.linear_fitness_landscape(m)
            igen = generators.iterations_generator(iterations, per_run)
            initial_state_generator = generators.constant_generator((N//3,N//3,N//3))
            cache = simulation.compile_edges(edges)
            lengths = run_lengths(cache, igen, initial_state_generator)
            # Write run_lengths to disk.            
            handle = open(os.path.join(output_directory, "%s_%s.csv" % (str(N), str(b),)), 'w')
            print len(lengths)
            for l in lengths:
                print >> handle, l

## Relative state occupancies ##

def state_occurances(N, fitness_landscape, iteration_gen, initial_state_generator, verbose=True):
    # Callbacks
    counter = callbacks.StateCounter()
    call_backs = [counter.add]   
    # Compile graph
    #edges = moran.multivariate_moran_transitions(N, fitness_landscape)
    edges = moran.moran_simulation_transitions(N, fitness_landscape)
    cache = simulation.compile_edges(edges)
    if verbose:
        markov_process_details(edges)
    # Run Simulations
    basic_simulation_run(cache, iteration_gen, initial_state_generator, call_backs=call_backs, max_steps=None)
    return counter.counts

## This test produces single images for given matrices for a 3D Moran process.        
def three_player_state_occurances_plot(N, iterations, per_run):
    igen = generators.iterations_generator(iterations, per_run)
    #initial_state_generator = generators.constant_generator((N//3,N//3,N//3))
    initial_state_generator = generators.random_state_generator(3, N)
    # Process data; in this case prep data for a ternary plot.
    counts = state_occurances(N, fitness_landscape, igen, initial_state_generator)
    ternary_dict = ternary.state_counts_to_ternary(counts, N)
    ternary.heatmap(ternary_dict, N, cmap_name="BrBG")
    #pylab.savefig(str(i) + ".png")

def two_player_state_occurances(N, fitness_landscape, iterations=1000, per_run=100):
    igen = generators.iterations_generator(iterations, per_run)
    #initial_state_generator = generators.constant_generator((N//2,N//2))
    initial_state_generator = generators.random_state_generator(2, N)
    #initial_state_generator = generators.constant_generator((N-4,4))
    # Process data; in this case prep data for a ternary plot.
    counts = state_occurances(N, fitness_landscape, igen, initial_state_generator)
    pylab.clf()
    xs = range(1, N)
    ys = []
    for i in xs:
        try:
            ys.append(counts[(i, N-i)])
        except KeyError:
            ys.append(0)
    ys = normalize(ys)
    pylab.plot(xs, ys)

#2d
def transition_entropy(N, fitness_landscape):
    edges = moran.moran_simulation_transitions(N, fitness_landscape)
    g = graph.Graph()
    g.add_edges(edges)
    d = dict()
    for vertex in g.vertices():
        transitions = g.out_dict(vertex).values()
        d[vertex] = shannon_entropy(transitions)
        #try:
            #p = g.out_dict(vertex)[vertex]
            #d[vertex] += p * math.log(p)
        #except KeyError:
            #continue
    pylab.clf()
    xs = range(1, N)
    ys = []
    for i in xs:
        try:
            ys.append(d[(i, N-i)])
        except KeyError:
            ys.append(0)
    pylab.plot(xs, ys)
    

def example_1():
    """
    Runs a basic simulation.
    """
    
    edges = [('a', 'b', 0.5), ('a', 'a', 0.5), ('b', 'a', 0.8),
             ('b', 'b', 0.1), ('b', 'c', 0.1)]
    cache = mpsim.compile_edges(edges)
    trajectory = mpsim.simulation(cache, initial_state='a')
    print trajectory

    
    
if __name__ == '__main__':
    example_1()
