import math
import matplotlib
import matplotlib.pyplot as pylab

"""This is a matplotlib ternary heatmap plotting utility. Given a dictionary with keys as tuples (i,j) where i + j + k = N and values as color values, the heatmap function produces a density plot by coloring alternating equilateral triangles and averaging colors for the interior triangles. The triangles are individually drawn with matplotlib's polygon functions."""

## Constants

SQRT3OVER2 = math.sqrt(3) / 2

## Default colormap, other options here: http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps
DEFAULT_COLOR_MAP = pylab.get_cmap('jet')    
#DEFAULT_COLOR_MAP = pylab.get_cmap('gist_stern')

## Geometry functions
def triangle_coordinates(i, j, alt=False):
    """Returns the ordered coordinates of the triangle vertices for i + j + k = N. Alt refers to the averaged triangles; the ordinary triangles are those with base parallel to the axis on the lower end (rather than the upper end)"""
    # N = i + j + k
    if not alt:
        return [(i/2. + j, i * SQRT3OVER2), (i/2. + j + 1, i * SQRT3OVER2), (i/2. + j + 0.5, (i + 1) * SQRT3OVER2)]
    else:
        # Alt refers to the inner triangles not covered by the default case
        return [(i/2. + j + 1, i * SQRT3OVER2), (i/2. + j + 1.5, (i + 1) * SQRT3OVER2), (i/2. + j + 0.5, (i + 1) * SQRT3OVER2)]        
                
def unzip(l):
    return [x for (x,y) in l], [y for (x,y) in l]    


def colormapper(x, a=0, b=1, cmap=None):
    """Maps color values to [0,1] and obtains rgba from the given color map for triangle coloring."""
    rgba = cmap((x - a) / float(b - a))
    hex_ = matplotlib.colors.rgb2hex(rgba)
    return hex_
    
def heatmap(d, N, cmap_name=None):
    """d is a dictionary of (i,j) --> c pairs where N = i + j + k."""
    if not cmap_name:
        cmap = DEFAULT_COLOR_MAP
    else:
        cmap = pylab.get_cmap(cmap_name)
    # Colorbar hack -- make fake figure and through it away
    Z = [[0,0],[0,0]]
    levels = [v for v in d.values()]
    levels.sort()
    CS3 = pylab.contourf(Z, levels, cmap=cmap)
    # Plot polygons    
    pylab.clf()
    a = min(d.values())
    b = max(d.values())
    # Color data triangles.
    for k, v in d.items():
        i, j = k
        vertices = triangle_coordinates(i,j)
        x,y = unzip(vertices)
        color = colormapper(d[i,j],a,b,cmap=cmap)
        pylab.fill(x, y, facecolor=color, edgecolor=color)
    # Color smoothing triangles.
    for i in range(N+1):
        for j in range(N + 1 - i - 1):
            alt_color = (d[i,j] + d[i, j+1] + d[i+1, j])/3.
            color = colormapper(alt_color, a, b, cmap=cmap)
            vertices = triangle_coordinates(i,j, alt=True)
            x,y = unzip(vertices)
            pylab.fill(x, y, facecolor=color, edgecolor=color)
    #Colorbar hack continued.
    pylab.colorbar(CS3)

def state_counts_to_ternary(counts, N):
    """Converts state counts to ternary format for plotting."""
    d = dict()
    for i in range(0, N+1):
        for j in range(0, N+1-i):
            k = N - i - j
            try:
                d[(i,j)] = counts[(i,j,k)]
            except KeyError:
                d[(i,j)] = 0
    return d      

def ternary_plot(data, N, directory=None, filename_root=None, cmap_name=None, log=False):
    # Make and maybe save heatmap.
    pylab.clf()
    if log:
        for k, v in data.items():
            data[k] = -math.log(v)
    #data = normalize_distribution(data)
    heatmap(data, N, cmap_name=cmap_name)
    if directory:
        filename = os.path.join(directory, filename_root + '.png')
        pylab.savefig(filename)    

def load_data(filename):
    """Makes a dictionary of data with lines of the form 'i j color'."""
    handle = open(filename)
    d = dict()
    for line in handle:
        s = line.split(' ')
        d[(int(s[0]), int(s[1]))] = float(s[2])
    return d
    
if __name__ == '__main__':
    import sys
    from math_helpers import normalize_distribution
    filename = sys.argv[1]
    N = int(sys.argv[2])
    #d = normalize_distribution(load_data(filename))
    d = load_data(filename)
    # Take log for better heatmap for exponential values.
    for k, v in d.items():
        d[k] = math.log(1 + v)
    heatmap(d,N)
    pylab.show()
    
        
        