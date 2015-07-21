### Simulation Callbacks

from collections import Counter

def print_results(results, filename=None):
    for result in results:
        print result


class LengthRecorder(object):
    """
    Records only length of trajectories.
    """

    def __init__(self):
        self.lengths = []

    def add(self, results):
        for seed, length, history in results:
            self.lengths.append(length)


class StateCounter(object):
    """
    Aggregates states over runs to measure incidence rates.
    """

    def __init__(self):
        self.counts = Counter()

    def add(self, results):
        for seed, length, history in results:
            self.counts.update(history)


class ResultsWriter(object):
    """
    Convenience callback to save data in CSV format to disk on-the-fly.
    """

    def __init__(self, filename):
        self.handle = open(filename, 'w')
        self.writer = csv.writer(self.handle)

    def write(self, results):
        for seed, length, history in results:
            row = [seed, length]
            row.extend(history)
            self.writer.write(row)

