### Simulation Callbacks

from multiset import Multiset

# The following class and function look at the simulations and estimate absorption probabilities for the Moran Process.

class ConvergentsCounter(object):
    """Counts final states of runs. Useful for testing for known convergence rates."""
    def __init__(self):
        self.counts = Multiset()

    def add(self, results):
        for seed, length, history in results:
            self.counts.add(history[-1])

def analyze_fixations(counts):
    d = {'A': 0, 'B': 0}
    for k,v in counts.items():
        if k[0] == 0:
            d['A'] += v
        else:
            d['B'] += v
    print normalize_distribution(d)

## Example Usage
#counter = ConvergentsCounter()
#call_backs = [counter.add]

#print normalize_distribution(counter.counts)
#analyze_fixations(counter.counts)    
    
class RunLengthRecorder(object):
    """Records only length of run."""
    def __init__(self):
        self.lengths = []

    def add(self, results):
        for seed, length, history in results:
            # the seed is the first result; don't count that.
            self.lengths.append(length)    
    
class StateCounter(object):
    """Aggregates states over runs to measure occupation times."""
    def __init__(self):
        self.counts = Multiset()
    
    def add(self, results):
        for seed, length, history in results:
            self.counts.add_many(history)
    
### The following code caches full run results - use writer.write as the call_back on a ResultsWriter object.

def print_results(results, filename=None):
    for result in results:
        print result

class ResultsWriter(object):
    """Convenience callback to save data to disk."""
    def __init__(self, filename):
        self.handle = open(filename, 'w')
        self.writer = csv.writer(self.handle)
    
    def write(self, results):
        for seed, length, history in results:
            row = [seed, length]
            row.extend(history)
            self.writer.write(row)

## Callbacks to cache to disk
#writer = ResultsWriter(filename="results.csv")
#call_backs = [writer.write]
            