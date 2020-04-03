import matplotlib.pyplot as plt
import numpy as np

def zipf(counter):
    counts = np.array(tuple(counter.values()))
    tokens = np.array(tuple(counter.keys()))
    ranks = np.arange(1, counts.size + 1)
    indices = counts.argsort()[::-1][:]
    frequencies = counts[indices]
    plot = plt.loglog(ranks, frequencies, marker=".")[0]
    for n in list(np.logspace(-0.5, np.log10(len(counts)), 20).astype(int)):
        dummy = plt.text(
            ranks[n], frequencies[n], " " + tokens[indices[n]],
            verticalalignment='bottom',
            horizontalalignment='left'
        )
    return plot