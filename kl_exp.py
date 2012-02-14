import math
import sys
import numpy
import pylab
import main
import moran
import ternary
from math_helpers import normalize, normalize_dictionary, kl_divergence
from helpers import ensure_digits
from graph import Graph



    #m = [[0,1,-1],[1,0,-3],[-1,3,0]]
    #m = [[0,1,-1],[1,0,-2],[-1,2,0]]
    #m = [[0,0,-1],[0,0,-2],[-1,1,0]]
    #m = [[0,0,-2],[0,0,-1],[-1,1,0]]
    #m = [[0,0,1],[0,0,0],[1,1,0]]
    
def main(N=27):
    """Ternary Moran process."""
    a = 1.
    b = 0.
    #m = moran.rock_scissors_paper(a=a, b=b)
    #m = [[0,0,-1],[0,0,-2],[-1,1,0]]
    #m = [[0,1,-1],[1,0,-3],[-1,3,0]]
    m = [[0,1,1],[0,1,1],[1,0,0]]
    escort = None
    edges = moran.multivariate_moran_transitions(m, N=N, escort=escort, fermi=True, beta=1.)
    graph = Graph()
    graph.add_edges(edges)
    e_kl = dict()
    for source in graph.vertices():
        s = 0.
        if source[2] != 0:
            dist = normalize(list(source))
            #dist = normalize([N//3]*3)
            out_dict = graph.out_dict(source)
            for target, weight in out_dict.items():
                s += weight * kl_divergence(dist, normalize(list(target)))
        if s > 1e-10:
            s = math.pow(s, 1./2)
        e_kl[(source[0], source[1])] = s
    ternary.ternary_plot(e_kl, N)
    pylab.show()

def main_2(N, fitness_landscape):
    edges = moran.moran_simulation_transitions(N, fitness_landscape)
    graph = Graph()
    graph.add_edges(edges)
    e_kl = dict()
    for source in graph.vertices():
        s = 0.
        dist = normalize(list(source))
        #dist = normalize([N//3]*3)
        out_dict = graph.out_dict(source)
        for target, weight in out_dict.items():
            s += weight * kl_divergence(dist, normalize(list(target)))
        #if s > 1e-10:
            #s = math.pow(s, 1./2)
        e_kl[source] = s
    xs = []
    ys = []
    for k in range(2, N-1):
        xs.append(k)
        ys.append(e_kl[(k, N-k)])
    pylab.plot(xs, ys)

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
        
        
if __name__ == '__main__':
    N = int(sys.argv[1])
    #main(N)
    #main_2(N)
    #kl_movie(N)
    ## Prisoner's Dilemma
    m = [[0,1],[0,2]]
    ## Hawk-Dove
    #m = [[1,2],[2,1]]    
    # Coordination
    #m = [[2,1], [1,2]]
    fitness_landscape = moran.linear_fitness_landscape(m, beta=1.)
    #fitness_landscape = moran.fitness_static(r)
    main_2(N, fitness_landscape)
    pylab.show()
    