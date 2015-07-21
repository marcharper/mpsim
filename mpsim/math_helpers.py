import numpy

def cumsum(l):
    """
    Cumulative summation of a list.
    """

    a = numpy.array(l)
    return a.cumsum()

# Vector / numpy.array
def normalize(x):
    s = float(sum(x))
    for j in range(len(x)):
        x[j] /= s
    return x

# Dictionary
def normalize_dictionary(x):
    s = float(sum(x.values()))
    for k in x.keys():
        x[k] /= s
    return x

