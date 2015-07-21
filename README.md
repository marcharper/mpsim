# mpsim

This is a python library for computing trajectories of Markov processes. Given
a list of states and transition probabilities, `mpsim` computes sample
sequences of states of either a fixed length or until an absorbing state is
reached.

The library was created to generate many such trajectories efficiently and has 
a number of features such as caching of frequently needed intermediate
computations, utilization of multiple processing cores, and callbacks for
on-the-fly processing of trajectories.

Basic Usage
------------

There are some examples [included with the library](/examples.py), To use the
library you need to supply a list of transitions in the following form:

```
[(source_state, target_state, transition_probability), ...]
```

The states of the process can be any hashable python object (integers, strings,
etc.). These are compiled into a graph object representing the directed graph
associated to the process.

For example:

    import mpsim
    edges = [('a', 'b', 0.5), ('a', 'a', 0.5), ('b', 'a', 0.8),
             ('b', 'b', 0.1), ('b', 'c', 0.1)]
    cache = mpsim.compile_edges(edges)
    random_seed, iterations, trajectory = mpsim.simulation(cache, initial_state='a')
    print "".join(trajectory)

This prints something like (depending on the random seed)

```
aaaaabababababaababababababaaaaaaabababaaaaaababaabc
```

The function `mpsim.simulation` accepts two additional keyword arguments:
- `random_seed` in case you want to specify the seed yourself, and
- `max_iterations`, in case you want to either limit the total iterations of the
process or if you want trajectories of a particular length (if there are no absorbing
states).

`mpsim` will detect absorbing states as those having no outbound edges or
transitions.

Larger Scale Usage
------------------

The library was originally created to generate many long trajectories. For this
usage case you likely want to take advantage of multiple processing cores and you
will want to process the data on the fly to prevent the trajectories from
accumulating in memory.

`mpsim` provides various helpers for this usage case in [generators](/mpsim/generators.py) and [callbacks](/mpsim/callbacks.py). Let's look at a
few of these in particular.

To limit memory usage, you can specify the number of trajectories to be
generated in each batch (before passing to a callback). To do so, use
`mpsim.generators.iterations_generator` as follows:

```
    mpsim.generators.iterations_generator(total, per_run=1000)
```

This will tell `mpsim` to generate `total` number of trajectories in
batches of `per_run`, split over the available processing cores.

You also need to specify the initial state to use. This can be the same state
every time, in which case you can use:

```
    initial_state_gen = mpsim.generators.constant_generator('a')
```

or a random state, in which case you could use:

```
    initial_state_gen = mpsim.generators.constant_generator(states)
```

Note that you must supply the states as a sequence, `mpsim` will not make any 
assumptions in this case as to what you may have wanted.

Finally you can specify a callback to process the trajectories in each batch.
For example, perhaps you are only interested in the total length of the
trajectories. The best way to do this is with a method of a class that keeps
track of the lengths (this is in `mpsim.callbacks`):

```
    class LengthRecorder(object):
        """
        Records only length of trajectories.
        """

        def __init__(self):
            self.lengths = []

        def add(self, results):
            for seed, length, history in results:
                self.lengths.append(length)
```

Then you would pass the `add` method of an instance as the callback, like so:

```
    callback_obj = mpsim.callbacks.RunLengthRecorder()
    callback = callback.add
```

`mpsim` will then pass the trajectories to the add function as each batch is
generated. Note that this is done syncronyously at the end of each batch, not
asynchronously as each trajectory is generated, so the callback does not need
to be thread-safe but the processing does not utilize multiple cores. If you
want to process on the fly with something thread-safe, you need to write a custom `sim_func` and pass it in as a keyword argument to `batched_simulations` (see
[simulations](/mpsim/simulation_.py) ).

Putting it all together:

```
    import mpsim
    from matplotlib import pyplot

    edges = [('a', 'b', 0.5), ('a', 'a', 0.5), ('b', 'a', 0.8),
                ('b', 'b', 0.1), ('b', 'c', 0.1)]
    cache = mpsim.compile_edges(edges)

    # Set up generators for batched processing
    initial_state_gen = mpsim.generators.constant_generator('a')
    parameter_gen = mpsim.generators.parameter_generator(cache, initial_state_gen)
    iters_gen = mpsim.generators.iterations_generator(100000)
    callback_obj = mpsim.callbacks.RunLengthRecorder()

    results = mpsim.batched_simulations(parameter_gen, iters_gen,
                                        callback=callback_obj.add)
    lengths = callback_obj.lengths

    # Plot the lengths as a histogram
    pyplot.hist(lengths, bins=30)
    pyplot.show()
```




