from __future__ import division
import math
import itertools as it
from decimal import Decimal, getcontext

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec

import smoothing


getcontext().prec = 3


def vert_pos(n, step, base):  # generate a list of vertical positions
    if n % 2 == 0:
        start = base + step / 2 - (n // 2) * step
    else:
        start = base - (n // 2) * step
    return [start + i * step for i in range(n)]


def label_node_pos(reeb, crtval, dist):
    curnodes = [x for x in reeb.nodes_iter() if reeb.node[x]['f_val'] == crtval]
    step = Decimal('0.2') * dist
    n = len(curnodes)
    pos = vert_pos(n, step, 0)
    for i in range(n):
        reeb.node[curnodes[i]]['pos'] = pos[i]


def edge_path(reeb):  # with appropriate position labels
    one_code = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    verts = []
    codes = []
    for l in reeb.nodes():
        for r in reeb.neighbors(l):
            if reeb.node[r]['f_val'] > reeb.node[l]['f_val']:
                dist = reeb.node[r]['f_val'] - reeb.node[l]['f_val']
                height = Decimal('0.15') * dist
                num_edges = len([1 for x, y in reeb.edges()
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
                    codes.extend(one_code)
    return Path(verts, codes)


def draw_reeb(reeb, ax):  # reeb is a networkx MultiGraph
    crtvals = smoothing.get_critical_vals(reeb)
    for i in range(len(crtvals)):
        c = crtvals[i]
        if i == 0:
            dist = crtvals[i + 1] - c
        else:
            x = [x for x in reeb.nodes_iter() if reeb.node[x]['f_val'] == c][0]
            if 'side' not in reeb.node[x]:
                dist = c - crtvals[i - 1]
                if (i != len(crtvals) - 1) and (crtvals[i + 1] - c < dist):
                    dist = crtvals[i + 1] - c
            elif reeb.node[x]['side'] == 'l':
                dist = c - crtvals[i - 1]
            else:
                dist = crtvals[i + 1] - c
        label_node_pos(reeb, c, dist)
    patch = patches.PathPatch(edge_path(reeb), facecolor='none', lw=1)
    ax.add_patch(patch)
    ax.set_xlim(min(float(c) for c in crtvals) - 1, max(float(c) for c in crtvals) + 1)
    ax.set_ylim(-1, 1)


def animate_reeb(n, reeb, ax, delta):
    print delta * n
    ax.clear()
    reeb = smoothing.smooth(reeb, delta * n)
    draw_reeb(reeb, ax)



def show_animation(reeb):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ani = animation.FuncAnimation(fig, animate_reeb, 150, fargs=[reeb, ax, 0.01], interval=20)
    plt.show()


def show_plot(reeb, epsilon):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    reeb = smoothing.smooth(reeb, epsilon)
    draw_reeb(reeb, ax)
    plt.show()

def show_multiplots(reeb):
    fig = plt.figure()
    num_plots = 12
    cols = int(math.sqrt(num_plots))
    rows = (num_plots - 1) // cols + 1
    crit_vals = smoothing.get_critical_vals(reeb)
    interval = (crit_vals[-1] - crit_vals[0]) / 2
    gs = gridspec.GridSpec(rows, cols)

    plots = []
    for i in range(num_plots):
        row = i // cols
        col = i % cols
        plots.append(fig.add_subplot(gs[row, col]))
        epsilon = interval * i / (num_plots - 1)
        new_reeb = smoothing.smooth(reeb, epsilon)
        plots[-1].set_title("epsilon = {:.2f}".format(epsilon))
        draw_reeb(new_reeb, plots[-1])
    fig.tight_layout()
    plt.show()


reeb1 = nx.MultiGraph()
reeb1.add_nodes_from([0, 1, 2, 3, 4])
reeb1.node[0]['f_val'] = 0
reeb1.node[1]['f_val'] = 1
reeb1.node[2]['f_val'] = 3
reeb1.node[3]['f_val'] = 3
reeb1.node[4]['f_val'] = 1
reeb1.add_edges_from([(0, 1), (0, 1), (1, 2), (1, 3),
                     (3, 4), (3, 4), (2, 4), (3, 4), (0, 1)])


reeb2 = nx.MultiGraph()
reeb2.add_nodes_from([0,1,2,3,4,5])
fvals2 = [0,1,2,3,4,5]
for i in range(6):
    reeb2.node[i]['f_val'] = fvals2[i]
reeb2.add_edges_from([(0,3),(0,2),(1,2),(1,3),(3,4),(3,4),(4,5)])

reeb3 = nx.MultiGraph()
reeb3.add_nodes_from([0,1,2,3,4,5,6,7,8,9,10])
fvals3 = [0,1,1,1.5,1.7,1.7,1.7,2,2,2,3]
for i in range(11):
    reeb3.node[i]['f_val'] = fvals3[i]
reeb3.add_edges_from([(0,1),(1,5), (1,5),(1,6),(2,5),(3,6), (3,6),
    (4,7),(5,8),(6,8),(6,7),(6,9),(7,10),(8,10)])


reeb4 = nx.MultiGraph()
reeb4.add_nodes_from([0,1,2])
fvals4 = [0,0.5,0.7]
for i in range(3):
    reeb4.node[i]['f_val'] = fvals4[i]
reeb4.add_edges_from([(0,2),(0,2),(1,2),(1,2)])


show_animation(reeb3)
# show_plot(reeb3, 0.1)
# show_multiplots(reeb3)
