from math import log

def cumsum(l):
    """
    Cumulative summation of a list.
    """

    a = numpy.array(l)
    return a.cumsum()

def arange(a, b, steps=100):
    """Similar to numpy.arange"""
    delta = (b - a) / float(steps)
    xs = []
    for i in range(steps):
        x = a + delta * i
        xs.append(x)
    return xs

## Vectors

def multiply_vectors(a, b):
    c = []
    for i in range(len(a)):
        c.append(a[i]*b[i])
    return c

def dot_product(a, b):
    c = 0
    for i in range(len(a)):
        c += a[i] * b[i]
    return c

#vector
def normalize(x):
    s = float(sum(x))
    for j in range(len(x)):
        x[j] /= s
    return x

#dictionary
def normalize_dictionary(x):
    s = float(sum(x.values()))
    for k in x.keys():
        x[k] /= s
    return x

## Information Theoretic Functions

def kl_divergence(p, q):
    s = 0.
    for i in range(len(p)):
        try:
            s += p[i] * log(p[i] / q[i])
        except ValueError:
            continue
    return s

def shannon_entropy(p):
    s = 0.
    for i in range(len(p)):
        try:
            s += p[i] * log(p[i])
        except ValueError:
            continue
    return -1.*s

def binary_entropy(p):
    return -p*log(p) - (1-p) * log(1-p)

