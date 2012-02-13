# -*- coding: utf-8 -*-

class Multiset(object):
    """Basic multiset for counts."""
    def __init__(self, seq=None):
        self.mset = dict()
        if seq:
            self.add(seq)

    def __getitem__(self, key):
        return self.mset[key]

    def __setitem__(self, key, value):
        self.mset[key] = value

    def add_many(self, seq):
        for elem in seq:
            try:
                self.mset[elem] += 1
            except KeyError:
                self.mset[elem] = 1

    def add(self, elem):
        try:
            self.mset[elem] += 1
        except KeyError:
            self.mset[elem] = 1

    def values(self):
        return self.mset.values()

    def keys(self):
        return self.mset.keys()

    def items(self):
        return self.mset.items()

    def __repr__(self):
        return str(self.mset)
