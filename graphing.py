import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.animation as animation
import smoothing

from itertools import chain
from collections import namedtuple


def vert_pos(n, step, base):  # generate a list of vertical positions
    if (n % 2) == 0:
        start = base + step / 2 - (n / 2) * step
    else:
        start = base - (n / 2) * step
    return [start + i * step for i in range(n)]


def label_node_pos(reeb, crtval,dist):
    curnodes = [x for x in range(reeb.order()) if reeb.node[x]['f_val'] == crtval]
    step = 0.2 * dist
    n = len(curnodes)
    pos = vert_pos(n, step, 0)
    for i in range(n):
        reeb.node[curnodes[i]]['pos'] = pos[i]


def edge_path(reeb):  # with appropriate position labels
    oneCode = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, ]
    #height = 0.05  # could vary height based on number of nodes
    verts = []
    codes = []
    for l in reeb.nodes():
        for r in reeb.neighbors(l):
            if reeb.node[r]['f_val'] > reeb.node[l]['f_val']:
                dist = reeb.node[r]['f_val'] - reeb.node[l]['f_val']
                height = 0.05 * dist
                num_edges = len([k for x, y, k in reeb.edges(keys=True)
                                 if (x == l) and (y == r) or (x == r) and (y == l)])
                lval = reeb.node[l]['f_val']
                rval = reeb.node[r]['f_val']
                lpos = reeb.node[l]['pos']
                rpos = reeb.node[r]['pos']
                lrefval = lval + (rval - lval) / 5
                rrefval = rval - (rval - lval) / 5
                lrefpos = vert_pos(num_edges, height, lpos + (rpos - lpos) / 5)
                rrefpos = vert_pos(num_edges, height, rpos - (rpos - lpos) / 5)
                for i in range(num_edges):
                    verts.extend([(lval, lpos), (lrefval, lrefpos[i]),
                                  (rrefval, rrefpos[i]), (rval, rpos)])
                    codes.extend(oneCode)
    return Path(verts, codes)


def draw_reeb(reeb):  # reeb is a networkx MultiGraph
    crtvals = smoothing.get_critical_vals(reeb)
    for i in range(len(crtvals)):
        v = crtvals[i]
        if i == 0:
            dist = crtvals[i+1] - v
        else:
            dist = v - crtvals[i-1]
            if (i != len(crtvals) -1) and (crtvals[i+1] - v < dist):
                dist = crtvals[i+1] - v
        print dist
        label_node_pos(reeb, v, dist)
    patch = patches.PathPatch(edge_path(reeb), facecolor='none', lw=2)
    ax.add_patch(patch)
    ax.set_xlim(min(v for v in crtvals) - 1, max(v for v in crtvals) + 1)
    ax.set_ylim(-1, 1)
    plt.show()


def animate_reeb(n, reeb):
    ax.clear()
    reeb = smoothing.smooth(reeb, 0.01 * (n + 1))
    crtvals = smoothing.get_critical_vals(reeb)
    for i in range(len(crtvals)):
        v = crtvals[i]
        if i == 0:
            dist = crtvals[i+1] - v
        else:
            dist = v - crtvals[i-1]
            if (i != len(crtvals) -1) and (crtvals[i+1] - v < dist):
                dist = crtvals[i+1] - v
        label_node_pos(reeb, v, dist)
    patch = patches.PathPatch(edge_path(reeb), facecolor='none', lw=2)
    ax.add_patch(patch)
    ax.set_xlim(min(v for v in crtvals) - 1, max(v for v in crtvals) + 1)
    ax.set_ylim(-1, 1)


fig = plt.figure()
ax = fig.add_subplot(111)
reeb = nx.MultiGraph()
reeb.add_nodes_from([0, 1, 2, 3, 4])
reeb.node[0]['f_val'] = 0
reeb.node[1]['f_val'] = 1
reeb.node[2]['f_val'] = 3
reeb.node[3]['f_val'] = 3
reeb.node[4]['f_val'] = 1
reeb.add_edges_from([(0, 1), (0, 1), (1, 2), (1, 3),
                     (3, 4), (3, 4), (2, 4), (3, 4), (0, 1)])
# draw_reeb(reeb)


reeb = smoothing.smooth(reeb,0.1)

draw_reeb(reeb)


# ani = animation.FuncAnimation(fig, animate_reeb, 150, fargs=[reeb], interval=20)
plt.show()
