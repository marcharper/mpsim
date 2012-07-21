
class Memoize(object):
    """Memoizes a function."""
    def __init__(self, f, kwargs=None):
        self.f = f
        self.store = dict()
        self.kwargs = kwargs
    def __call__(self, *args):
        try:
            return self.store[args]
        except KeyError:
            if self.kwargs:
                self.store[args] = self.f(*args, **self.kwargs)
            else:
                self.store[args] = self.f(*args)
            return self.store[args]
            