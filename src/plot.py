import sys
from pylab import loadtxt, plot, show

try:

    data = loadtxt(sys.stdin)

    if len(data.shape) == 1:
        plot(data)
    else:
        data = zip(*data)
        plot(*data)

    show()

except (IOError, ValueError):
    print >> sys.stderr, 'Input must contain 1 or 2 values per line'
