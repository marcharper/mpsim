import math

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

def kl_divergence(p, q):
    s = 0.
    for i in range(len(p)):
        if q[i] > 1e-10:
            s += p[i] * math.log(p[i] / q[i])
    return s