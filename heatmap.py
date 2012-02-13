import csv
import sys
import numpy
from multiset import Multiset

"""Ordinary 2d heatmap."""

N = sys.argv[1]

handle = open("results.csv")
reader = csv.reader(handle)
states = Multiset()
for i, row in enumerate(reader):
    print i, row[0]
    states.add_many(map(eval, row[1:]))

c = numpy.zeros((N+1,N+1))
for i in range(0, N+1):
    for j in range(0, N+1-i):
        k = N - i - j
        try:
            c[i,j] = states[(i,j,k)]
        except KeyError:
            pass

x = numpy.array(range(N+1))
y = numpy.array(range(N+1))

pylab.clf()
pylab.pcolor(x,y,c)
pylab.show()
