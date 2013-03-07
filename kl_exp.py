import math
import numpy
import sys

from matplotlib import pyplot

import main
import moran
import ternary
from math_helpers import normalize, normalize_dictionary, kl_divergence, multiply_vectors
from helpers import ensure_digits
from graph import Graph

from incentives import *

## This module contains functions to compute the expected KL divergence for each state of a Markov process.

def main_3d(N, fitness_landscape):
    """Ternary Moran process."""
    edges = moran.multivariate_moran_transitions(N, fitness_landscape)
    graph = Graph()
    graph.add_edges(edges)
    e_kl = dict()
    for source in graph.vertices():
        s = 0.
        if all(source):
            dist = normalize(list(source))
            #dist = normalize([N//3]*3)
            out_dict = graph.out_dict(source)
            for target, weight in out_dict.items():
                #s += weight * kl_divergence(dist, normalize(list(target)))
                s += weight * kl_divergence(normalize(list(target)), dist)
        #if s > 1e-10:
            #s = math.pow(s, 1./2)
            e_kl[(source[0], source[1])] = s
    ternary.heatmap(e_kl, N)
    
def main_2d(N, incentive):
    #print normalize(incentive(normalize(x)))
    edges = moran.moran_simulation_transitions(N, fitness_landscape, incentive=incentive)
    graph = Graph()
    graph.add_edges(edges)
    e_kl = dict()
    for source in graph.vertices():
        s = 0.
        dist = normalize(list(source))
        #dist = normalize([N//3]*3)
        out_dict = graph.out_dict(source)
        for target, weight in out_dict.items():
            if target[0] == 0 or target[0] == N:
                continue
            #s += weight * kl_divergence(dist, normalize(list(target)))
            s += weight * kl_divergence(normalize(list(target)), dist)
        #if s > 1e-10:
            #s = math.pow(s, 1./2)
        e_kl[source] = s
    xs = []
    ys = []
    for k in range(2, N-1):
        xs.append(k)
        ys.append(e_kl[(k, N-k)])
    #print ys
    pyplot.plot(xs, ys)

def kl_movie_2(N=20):
    rs = list(numpy.arange(0.0, 0.1, 0.001))
    rs.extend(list(numpy.arange(0.1, 2, 0.01)))
    rs.extend(list(numpy.arange(2, 3, 0.1)))
    rs.extend(range(4, 101, 1))
    digits = len(str(len(rs)))
    for i, r in enumerate(rs):
        print i, r
        pylab.clf()
        main_2(N, r)
        pylab.ylim(0, 0.0045)
        pylab.title("r=%s" % (str(r),))
        pylab.savefig('kl_static/' + str(ensure_digits(digits, str(i))) + ".png", dpi=160, pad_inches=0.5)

##def kl_movie(N=20):
    ##rs = list(numpy.arange(0.0, 0.1, 0.001))
    ##rs.extend(list(numpy.arange(0.1, 2, 0.01)))
    ##rs.extend(list(numpy.arange(2, 3, 0.1)))
    ##rs.extend(range(4, 101, 1))
    ##digits = len(str(len(rs)))
    ##for i, r in enumerate(rs):
        ##print i, r
        ##pylab.clf()
        ##main_2(N, r)
        ##pylab.ylim(0, 0.0045)
        ##pylab.title("r=%s" % (str(r),))
        ##pylab.savefig('kl_matrix/' + str(ensure_digits(digits, str(i))) + ".png", dpi=160, pad_inches=0.5)        
    
def ess(m, N):
    a = m[0][0]
    b = m[0][1]
    c = m[1][0]
    d = m[1][1]
    x = float(d - b + float(a - d) / N) / ((d - b) + (a - c))
    return numpy.array([x, 1.-x])
    
if __name__ == '__main__':
    N = int(sys.argv[1])
    #kl_movie(N)
    
    ## Sample Landscapes, 2D ##
    ## Static Landscape
    r = .1
    fitness_landscape = moran.fitness_static(r)
    ## Prisoner's Dilemma
    #m = [[0,1],[0,2]]
    # Hawk-Dove
    #m = [[1,2],[2,1]]
    # Coordination
    #m = [[2,1], [1,2]]
    #m = [[20,0], [17,1]]
    #m = [[1,2],[5,1]]
    #fitness_landscape = moran.linear_fitness_landscape(m)
    #x = ess(m, N)
    #print x, N * x 

    incentive=replicator_incentive_power(fitness_landscape, 0.)
    main_2d(N, incentive)    
    incentive=replicator_incentive(fitness_landscape)
    main_2d(N, incentive)
    incentive = fermi_incentive(fitness_landscape, 1)
    main_2d(N, incentive)    
    incentive = logit_incentive(fitness_landscape, 1)
    main_2d(N, incentive)
    #incentive = logit_incentive(fitness_landscape, 10)
    #main_2d(N, incentive)
    incentive=best_reply_incentive(fitness_landscape)
    main_2d(N, incentive)    

    #incentive=replicator_incentive_power(fitness_landscape, 0.6)
    #main_2d(N, incentive)
    #incentive=replicator_incentive_power(fitness_landscape, 0.75)
    #main_2d(N, incentive)    
    #incentive=replicator_incentive_power(fitness_landscape, 1)
    #main_2d(N, incentive)
    #incentive=replicator_incentive_power(fitness_landscape, 1.2)
    #main_2d(N, incentive)
    #incentive=replicator_incentive_power(fitness_landscape, 1.25)
    #main_2d(N, incentive)
    #incentive=replicator_incentive_power(fitness_landscape, 3)
    #main_2d(N, incentive)      

    pyplot.show()

    ## Sample Landscapes, 3D ##
    #m = [[0,1,-1],[1,0,-3],[-1,3,0]]
    #m = [[0,1,-1],[1,0,-2],[-1,2,0]]
    ##m = [[0,0,-1],[0,0,-2],[-1,1,0]]
    #m = [[0,0,-2],[0,0,-1],[-1,1,0]]
    #m = [[0,0,1],[0,0,0],[1,1,0]]    
    #m = [[0,0,-1],[0,0,-2],[-1,1,0]]
    #m = [[0,1,1],[0,1,1],[1,0,0]]
    #a = 1.
    #b = -1.
    #m = moran.rock_scissors_paper(a=a, b=b)
 
    #fitness_landscape = moran.linear_fitness_landscape(m, beta=1.)
    #main_3d(N, fitness_landscape)
    