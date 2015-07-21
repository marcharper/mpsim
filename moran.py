import math

from math_helpers import normalize, dot_product, multiply_vectors

### Birth and death probability functions

def moran_death(N):
    def p(pop):
        s = sum(pop)
        if s == N + 1:
            return 1
        return 0
    return p

def moran_death_2(N):
    def p(pop):
        s = sum(pop)
        if s == N:
            return 1.
        if s == N - 1:
            return 0.5
        return 0.
    return p

def moran_cascade(N):
    def p(pop):
        s = sum(pop)
        return math.pow(2, s-N)
    return p

def discrete_sigmoid(t, k_1=0.1, k_2=-1.1):
    # Adapted from https://dinodini.wordpress.com/2010/04/05/normalized-tunable-sigmoid-functions/
    k_2 = -1 - k_1
    if t < 0:
        return 0
    if t <= 0.5:
        return k_1 * t / (k_1 - 2*t + 1)
    else:
        return 0.5 + 0.5*k_2 * (2*t - 1.) / (k_2 - (2* t - 1.) + 1)

def sigmoid_death(N):
    def p(pop):
        s = sum(pop)
        return discrete_sigmoid(float(s) / N)
    return p
        
def linear_death(N):
    def p(pop):
        s = sum(pop)
        if s == 1:
            return 0
        return float(s) / N
    return p

### Landscape Transforms

def fermi_transform(landscape, beta=1.0):
    """Exponentiates landscapes, useful if total fitness is zero to prevent divide by zero errors."""
    def f(x):
        fitness = list(map(lambda z: math.exp(beta*z), landscape(x)))
        return fitness
    return f  

def escort_transform(landscape, escort):
    def f(pop):
        pop = list(map(escort,pop))
    return landscape(pop)

## Sample escorts
#escort = lambda x: math.sqrt(abs(x))
#escort = lambda x: x**1.1
#escort = lambda x: x**0.02
#escort = lambda x: 1    # Projection Dynamic
    
### Fitness landscapes    

def fitness_static(r):
    def fitness(pop):
        return [1., float(r)]
    return fitness
    
def rock_scissors_paper(a=1, b=1):
    """Good and Bad RSP matrix."""
    return [[0,-b,a], [a, 0, -b], [-b, a, 0]]        
    
#def linear_fitness_landscape(m, beta=None):
    #"""Computes a fitness landscape for a three player game from a matrix given by m and a population vector (i,j,...,k) summing to N."""
    ## m = array of rows
    #def f(pop):
        #fitness = []
        ##if escort:
            ##pop = list(map(escort,pop))
        #for i in range(len(pop)):
            ## - m[i][i] because we assume that individuals do not interact with themselves.
            #f = dot_product(m[i], pop) - m[i][i] 
            #fitness.append(f)
        #return fitness
    #if beta:
        #f = fermi_transform(f, beta)
    #return f

def linear_fitness_landscape(m, beta=None, self_interaction=False):
    """Computes a fitness landscape from a game matrix given by m and a population vector (i,j) summing to N."""
    # m = array of rows
    def f(pop):
        N = sum(pop)
        if self_interaction:
            div = N
        else:
            div = N-1
        #pop = [x / float(div) for x in pop]
        fitness = []
        for i in range(len(pop)):
            # - m[i][i] if individuals do not interact with themselves.
            f = dot_product(m[i], pop)
            if not self_interaction:
                f -= m[i][i]
            fitness.append(f / float(div))
        return fitness
    if beta:
        f = fermi_transform(f, beta)
    return f  

#E.g in two-player games, this is equivalent to
#m = [[a,b],[c,d]]
#def fitness(pop):
    #i = pop[0]
    #f_a = ( a*(i - 1.) + b*(N - i) ) / (N - 1.)
    #f_b = ( c*i + d*(N - i - 1.) ) / (N - 1.)
    #return [f_a, f_b]
    
### Transition Probability Computers   
    
# 3d Moran process    
def multivariate_moran_transitions(N, fitness_landscape):
    """Computes transitions for dimension n=3 moran process given a game matrix."""
    edges = []
    for i in range(N+1):
        for j in range(N+1-i):
            k = N - i - j
            # There are zero to six possible transitions, depending on the values of i, j, k.
            # Case 1, absorbing states: one of i, j, or k == N
            if i==N or j==N or k==N:
                continue
            pop = [i, j, k]
            fitness = fitness_landscape(pop)
            total_fitness = float(dot_product(fitness, pop))
            #Case 2: One of i, j, or k is zero (both cannot be because of case 1).
            if i == 0:
                transitions = [(i, j+1, k-1), (i, j-1, k+1)]
            elif j == 0:
                transitions = [(i+1, j, k-1), (i-1, j, k+1)]
            elif k == 0:
                transitions = [(i+1, j-1, k), (i-1, j+1, k)]
            else:
                transitions = [(i, j+1, k-1), (i, j-1, k+1), (i+1, j, k-1), (i-1, j, k+1), (i+1, j-1, k), (i-1, j+1, k)]
            temp_edges = []
            s = 0
            for i2, j2, k2 in transitions:
                diffs = [i2 - i, j2 - j, k2 - k]
                # one of these is 0, one is -1, one is 1
                for x in range(len(diffs)):
                    if diffs[x] == 1:
                        plus_one_index = x
                    if diffs[x] == -1:
                        minus_one_index = x
                #t = pop[plus_one_index]*fitness[plus_one_index] / total_fitness * pop[minus_one_index] / N
                t = pop[plus_one_index]*fitness[plus_one_index] / total_fitness * pop[minus_one_index] / sum(pop)
                s += t
                temp_edges.append(((i,j,k), (i2, j2, k2), t))
            # Compute transition probability of staying put.
            temp_edges.append(((i,j,k), (i,j,k), 1-s))
            edges.extend(temp_edges)
    return edges

def moran_simulation_transitions(N, fitness_landscape=None, incentive=None):
    """Returns a graph of the Markov process corresponding to a generalized Moran process on the given fitness landscape."""
    edges = []
    # Possible states are (a, b) with 0 < a + b <= N where a is the number of A individuals and B is the number of B individuals.
    for a in range(1, N):
        b = float(N - a)
        if incentive:
            #birth = normalize(incentive(normalize([a,b])))
            birth = normalize(incentive([a,b]))
        else:
            birth = normalize(multiply_vectors([a, b], fitness_landscape([a,b])))
        up = birth[0] * b / (a + b)
        down = birth[1] * a / (a + b)
        even = 1 - up - down
        edges.append(((a, N-a), (a+1, N-a-1), up))
        edges.append(((a, N-a), (a-1, N-a+1), down))
        edges.append(((a, N-a), (a, N-a), even))
    return edges    
    
# 2d moran-like process separating birth and death processes
def generalized_moran_simulation_transitions(N, fitness_landscape, death_probabilities=None, incentive=None):
    """Returns a graph of the Markov process corresponding to a generalized Moran process, allowing for uncoupled birth and death processes."""
    if not death_probabilities:
        death_probabilities = moran_death(N)
    edges = []
    # Possible states are (a, b) with 0 < a + b <= N where a is the number of A individuals and B is the number of B individuals.
    for a in range(1, N + 2):
        for b in range(1, N + 2 - a):
            # Death events.
            if a + b == 0:
                continue
            if a + b < N:
                continue
            p = death_probabilities((a, b))
            if a > 0:
                q = p * float(a) / (a + b)
                if q > 0:
                    edges.append(((a, b), (a - 1, b), q))
            if b > 0:
                q = p * float(b) / (a + b)
                if q > 0:
                    edges.append(((a, b), (a, b - 1), q))
            # Birth events.
            if a + b >= N + 1:
                continue
            if incentive:
                birth_q = normalize(incentive([a,b]))
            else:
                birth_q = normalize(multiply_vectors([a, b], fitness_landscape([a,b])))
            if a <= N:
                q = (1. - p) * birth_q[0]
                if q > 0:
                    edges.append(((a, b), (a + 1, b), q))
            if b <= N:
                q = (1. - p) * birth_q[1]
                if q > 0:
                    edges.append(((a, b), (a, b + 1), q))
    return edges

# 2d moran-like process separating birth and death processes; same as fixed size other than a + b < N conditional.
def generalized_moran_simulation_transitions_variable_size(N, fitness_landscape, death_probabilities=None):
    """Returns a graph of the Markov process corresponding to a generalized Moran process, allowing for uncoupled birth and death processes."""
    if not death_probabilities:
        death_probabilities = moran_death(N)
    edges = []
    # Possible states are (a, b) with 0 < a + b <= N where a is the number of A individuals and B is the number of B individuals.
    for a in range(1, N + 2):
        for b in range(1, N + 2 - a):
            # Death events.
            if a + b == 0:
                continue
            p = death_probabilities((a, b))
            if a > 0:
                q = p * float(a) / (a + b)
                if q > 0:
                    edges.append(((a, b), (a - 1, b), q))
            if b > 0:
                q = p * float(b) / (a + b)
                if q > 0:
                    edges.append(((a, b), (a, b - 1), q))
            # Birth events.
            if a + b >= N + 1:
                continue
            birth_q = normalize(multiply_vectors([a, b], fitness_landscape([a,b])))
            if a <= N:
                q = (1. - p) * birth_q[0]
                if q > 0:
                    edges.append(((a, b), (a + 1, b), q))
            if b <= N:
                q = (1. - p) * birth_q[1]
                if q > 0:
                    edges.append(((a, b), (a, b + 1), q))
    return edges    
    
