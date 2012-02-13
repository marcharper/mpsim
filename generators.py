### Generators for simulations
import random

# This generator divides up the requested number of simulations into chunks so that results can be written to disk or processed so as to not fill memory.
# batches
def iterations_generator(total_iterations, per_run=10000):
    remaining = total_iterations
    while remaining > 0:
        iters = min(per_run, remaining)
        yield iters
        remaining -= per_run

# Each simulation requires a random seed.
def random_seeds(a=1, b=99999999999):
    while True:
        yield random.randint(a, b)

### Initial State Generator helpers        
        
# Useful for specifying a constant initial state, for instance.
def constant_generator(value):
    while True:
        yield value

# E.g. Can specify the barycenter:
# initial_state_generator = constant_generator([N//3, N//3, N//3])
# Or a single invading mutant:
# initial_state_generator = constant_generator([N-1, 1])
    
## Random initial state generator        
def random_vector(n, N, minimum=1):
    """Returns a random integer vector of length n that sums to N. To avoid the boundary, set minimum = 1."""
    r = []
    s = N
    for i in range(n-1):
        try:
            t = random.randint(minimum, s - minimum)
        except ValueError:
            t = minimum
        s -= t
        r.append(t)
    r.append(s)
    return tuple(r)

def random_state_generator(n,N):
    """Random state generator for use as an initial_state_generator."""
    while True:
        yield random_vector(n, N)
