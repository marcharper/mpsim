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
import simulation
import moran
import ternary
from math_helpers import normalize, normalize_dictionary
from helpers import ensure_digits, ensure_directory

### Cache loaders.

#def edges_to_csv(edges, filename):
    #handle = open(filename, 'w')
    #writer = csv.writer(handle)
    #for x, y, z in edges:
        #row = [x, y, z]
        #writer.writerow(row)

#def csv_to_edges(filename):
    #handle = open(filename)
    #reader = csv.reader(handle)
    #edges = []
    #for row in reader:
        #edges.append(tuple(map(eval, row)))
    #return edges

### Helpers and plotters

def parse_args(argv):
    N = int(argv[1])
    iterations = int(argv[2])
    try:
        per_run = int(argv[3])
    except:
        per_run = iterations // 10
    return (N, iterations, per_run)

def arange(a, b, steps=100):
    """Similar to numpy.arange"""
    delta = (b - a) / float(steps)
    xs = []
    for i in range(steps):
        x = a + delta * i
        xs.append(x)
    return xs

def markov_process_details(edges):
    """Basic details about a set of edges for a Markov process."""
    s = set()
    for x, _, _ in edges:
        s.add(x)
    print "Vertices:", len(s)
    print "Edges:", len(edges)

### Convenience functions for ternary plot generation.    
    
def write_ternary_data(data, directory, filename_root):
    """ Writes weighted ternary data to disk."""
    filename = os.path.join(directory, filename_root +'.csv')
    handle = open(filename, 'w')
    writer = csv.writer(handle)
    for k, v in data.items():
        writer.writerow([k[0], k[1], v])

def ternary_plot(data, N, directory=None, filename_root=None, cmap_name=None, log=True, ):
    """Generates a ternary plot using functions from the ternary module."""
    pylab.clf()
    if log:
        for k, v in data.items():
            data[k] = (math.log(1 + v))
    data = normalize_dictionary(data)
    ternary.heatmap(data, N, cmap_name=cmap_name)
    if directory:
        filename = os.path.join(directory, filename_root + '.png')
        pylab.savefig(filename)
        
### Movie creation.
def make_movie_images(N, iterations, data_directory="movies/"):
    """Generates images for stitching into a video."""
    a = 1.   
    run_params = []
    run_params.append((40000, 20000, arange(-2, 2, 100)))
    run_params.append((80000, 20000, arange(2, 4, 50)))
    run_params.append((120000, 40000, arange(4, 34, 300)))
    total = sum(len(l) for i, p, l in run_params)
    digits = len(str(total))
    pre = 0
    for iterations, per_run, l in run_params:
        for i in range(len(l)):
            b = l[i]
            print i, ensure_digits(digits, str(pre + i)), b, iterations, per_run
            m = moran.rock_scissors_paper(a=a, b=b)    
            fitness_landscape = moran.linear_fitness_landscape(m, beta=2.0)
            igen = generators.iterations_generator(iterations, per_run)
            #initial_state_generator = generators.constant_generator((N//3,N//3,N//3))
            initial_state_generator = generators.random_state_generator(3, N)
            # Process data; in this case prep data for a ternary plot.
            counts = state_occurances(N, fitness_landscape, igen, initial_state_generator)
            d = state_counts_to_ternary(counts, N)
            #write_ternary_data(d, "movies", ensure_digits(digits, str(pre + i)))
            ternary.ternary_plot(d, N, "movies", ensure_digits(digits, str(pre + i)))
        pre += len(l)

### Examples and Tests    

def basic_simulation_run(cache, iteration_gen, initial_state_generator, call_backs=None, max_steps=None, short_report=False):
    param_gen = simulation.parameter_generator(cache, initial_state_generator, max_steps=max_steps, short_report=short_report)
    all_results = simulation.run_simulations(param_gen, iteration_gen, call_backs=call_backs)
    return all_results

def two_type_moran_process_simulations(N=40, fitness_landscape=moran.fitness_static(2.), iterations=10000, per_run=100000, verbose=False, call_backs=None, initial_state_generator=None):
    if not initial_state_generator:
        initial_state_generator = generators.random_state_generator(2,N)
    igen = generators.iterations_generator(iterations, per_run)
    edges = moran.moran_simulation_transitions(N, fitness_landscape)
    cache = simulation.compile_edges(edges, verbose=False)
    param_gen = simulation.parameter_generator(cache, initial_state_generator, max_steps=100000)
    runs = basic_simulation_run(cache, igen, initial_state_generator, call_backs=None, max_steps=None, short_report=False)
    return runs

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
    basic_simulation_run(cache, iteration_gen, initial_state_generator, call_backs=call_backs, max_steps=10*N)
    return counter.counts
    
# formerly "main"
## This test produces single images for given matrices for a 3D Moran process.        
def three_player_state_occurances_plot(N, iterations, per_run):
    igen = generators.iterations_generator(iterations, per_run)
    #initial_state_generator = generators.constant_generator((N//3,N//3,N//3))
    initial_state_generator = generators.random_state_generator(3, N)
    # Process data; in this case prep data for a ternary plot.
    counts = state_occurances(N, fitness_landscape, igen, initial_state_generator)
    ternary_dict = ternary.state_counts_to_ternary(counts, N)
    ternary.ternary_plot(ternary_dict, N, cmap_name="BrBG")
    #pylab.savefig(str(i) + ".png")
        
def two_player_state_occurances(N=20, fitness_landscape, iterations=1000, per_run=100):
    igen = generators.iterations_generator(iterations, per_run)
    #initial_state_generator = generators.constant_generator((N//2,N//2))
    initial_state_generator = generators.random_state_generator(2, N)
    # Process data; in this case prep data for a ternary plot.
    counts = state_occurances(N, fitness_landscape, igen, initial_state_generator)
    pylab.clf()
    xs = range(1, N)
    ys = []
    for i in xs:
        try:
            ys.append(1./counts[(i, N-i)])
        except KeyError:
            ys.append(0)
    pylab.plot(xs, ys)

if __name__ == '__main__':
    # 3 player state occupation plots
    N, iterations, per_run = parse_args(sys.argv)
    #m = [[0,-2,2],[0,0,1],[0,1,0]]
    #a = 2.8
    #b = 1
    #m = [[0,a,-b],[a,0,-b],[b,b,0]]  
    #m = [[0,1,-1],[1,0,-3],[-1,3,0]]
    #m = [[0,1,-1],[1,0,-2],[-1,2,0]]
    #m = [[0,0,-1],[0,0,-2],[-1,1,0]]
    #m = [[0,0,-2],[0,0,-1],[-1,1,0]]
    #m = [[0,0,1],[0,0,0],[1,1,0]]
    matrices = [[[0,1,-1],[1,0,-3],[-1,3,0]],[[0,1,-1],[1,0,-2],[-1,2,0]],[[0,0,-1],[0,0,-2],[-1,1,0]],[[0,0,-2],[0,0,-1],[-1,1,0]], [[0,0,1],[0,0,0],[1,1,0]]]
    for i, m in enumerate(matrices):
        fitness_landscape = moran.linear_fitness_landscape(m, beta=2.0)
        three_player_state_occurances_plot(N, iterations, per_run)
        pylab.show()    

    # 2 player state plots
    #fitness_landscape = moran.fitness_static(r)
    m = [[0,1],[0,2]]
    #m = [[1,2], [2,1]]
    #m = [[2,1], [1,2]]
    fitness_landscape = moran.linear_fitness_landscape(m)      
    two_player_state_occurances(N, iterations, per_run)
    pylab.show()    

    
    
    
    #run_lengths()
    #simulation_test(sys.argv[1:])
    #for b in range(0, 400, 4):
        #multivariate_test(sys.argv, a=1, b=1+b/100.)
    #multivariate_test(sys.argv, a=1, b=8)
    #make_movie_images(sys.argv)
    # ffmpeg -qscale 2 -r 15 -b 9600 -i %03d.png movie.mp4
        