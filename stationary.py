import moran
import main
import sys
import pylab
from helpers import ensure_digits
from graph import Graph

"""Compute stationary distributions for Markov processes."""

class Cache(object):
    """Caches common calculations for a given graph for efficiency."""
    def __init__(self, graph):
        # Caches vertex enumeration, cumulative sums, absorbing state tests, and transition targets.
        self.enum = dict()
        self.inv_enum = []
        self.in_neighbors = []
        self.terminals = []
        vertices = graph.vertices()
        #Enumerate vertices
        for (index, vertex) in enumerate(vertices):
            self.enum[vertex] = index
            self.inv_enum.append(vertex)
            # Is node terminating?
            if len(graph.out_dict(vertex)) == 0:
                self.terminals.append(index)
        # Cache in_neighbors
        for vertex in vertices:
            in_dict = graph.in_dict(vertex)
            self.in_neighbors.append([(self.enum[k], v) for k,v in in_dict.items()])

def stationary_distribution_generator(cache, initial_state=None):
    """Generator for the stationary distribution of a Markov chain, produced by iteration of the transition matrix."""
    N = len(cache.inv_enum)
    if not initial_state:
        ranks = [1/float(N)]*N
    else:
        ranks = initial_state        
    while True:
        new_ranks = []
        for node in range(N):
            new_rank = 0.
            for i, v in cache.in_neighbors[node]:
                new_rank += v * ranks[i]
            new_ranks.append(new_rank)
        yield new_ranks
        ranks = new_ranks

def three_dim():    
    N = int(sys.argv[1])
    iterations = int(sys.argv[2])

    print "preparing computations"
    m = moran.rock_scissors_paper(a=1, b=3)
    #a = 2.8
    #b = 1
    #m = [[0,a,-b],[a,0,-b],[b,b,0]]  
    #m = [[0,0,1],[0,0,0],[1,1,0]]
    edges = moran.multivariate_moran_transitions(m=m, N=N)
    g = Graph()
    g.add_edges(edges)
    g.normalize_weights()
    cache = Cache(g)
    initial_state = [0]*(len(edges))
    initial_state[cache.enum[(N//3, N//3, N//3)]] = 1
    #initial_state = [1]*(len(edges))
    print "calculating convergents and saving images"
    gen = stationary_distribution_generator(cache, initial_state=initial_state)
    for i, ranks in enumerate(gen):
        if i == iterations:
            break
        d = dict()
        for j, r in enumerate(ranks):
            state = cache.inv_enum[j]
            d[(state[0], state[1])] = r
        main.ternary_plot(d, N, 'stat', ensure_digits(len(str(iterations)), str(i)), log=True)
        #print i, 

def two_dim(N=20, r=0, iterations=200):
    #fitness_landscape = moran.fitness_static(r)
    m = [[1,2], [2,1]]
    fitness_landscape = moran.linear_fitness_landscape(m, fermi=False)
    edges = moran.moran_simulation_transitions(N, fitness_landscape)
    g = Graph()
    g.add_edges(edges)
    g.normalize_weights()
    cache = Cache(g)
    initial_state = [0]*(len(edges))
    #initial_state[cache.enum[N//2]] = 1
    initial_state[cache.enum[1]] = 1
    #initial_state = [1]*(len(edges))
    #print "calculating convergents and saving images"
    gen = stationary_distribution_generator(cache, initial_state=initial_state)
    d = dict()
    for i, ranks in enumerate(gen):       
        if i == iterations:
            break
        #if i != iterations - 1:
            #continue
        print i
        d = dict()
        for j, r in enumerate(ranks):
            state = cache.inv_enum[j]
            d[state] = r
        xs = range(N+1)
        ys = []
        for k in xs:
            ys.append(d[(k, N-k)])
        pylab.clf()
        pylab.plot(xs, ys)
        #pylab.show()
        pylab.savefig('static_2/' + ensure_digits(len(str(iterations)), str(i)) + ".png", dpi=160)

if __name__ == '__main__':
    two_dim()