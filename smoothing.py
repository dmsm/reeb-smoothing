from __future__ import division
from itertools import chain
from collections import namedtuple
import networkx as nx
import itertools


def get_critical_vals(reeb):
    return sorted(list(set(d['f_val'] for _, d in reeb.nodes_iter(data=True))))


def preprocess(reeb):
    reeb = nx.convert_node_labels_to_integers(reeb)
    critical_vals = get_critical_vals(reeb)
    for l, r, k in reeb.edges(keys=True):
        intersections = [v for v in critical_vals if
                         (v > reeb.node[l]['f_val'] and
                          v < reeb.node[r]['f_val']) or
                         (v < reeb.node[l]['f_val'] and
                          v > reeb.node[r]['f_val'])]
        if intersections:
            reeb.remove_edge(l, r, k)
            l, r = sorted((l, r), key=lambda n: reeb.node[n]['f_val'])
            n = l
            for intersection in intersections:
                n_prev = n
                n = reeb.number_of_nodes()
                reeb.add_node(n, f_val=intersection)
                reeb.add_edge(n_prev, n)
            reeb.add_edge(n, r)
    return nx.convert_node_labels_to_integers(reeb)


def label_edges(reeb):
    for l, r, k in reeb.edges(keys=True):
        reeb[l][r][k]['weight'] = abs(
            reeb.node[r]['f_val'] - reeb.node[l]['f_val'])


def get_smallest_int(reeb):
    min_weight = min(d['weight'] for _, _, d in reeb.edges(data=True))
    return [(l, r, k, d) for l, r, k, d in reeb.edges(data=True, keys=True) if d['weight'] == min_weight]


def smooth_int(reeb, edges):
    G_temp = nx.MultiGraph()
    G_temp.add_edges_from(edges)
    for subgraph in nx.connected_component_subgraphs(G_temp):   #
        reeb.remove_edges_from(subgraph.edges())
        component_node = reeb.number_of_nodes()  # G -> reeb
        for node in subgraph.nodes():
            reeb.add_edge(node, component_node)  # add_node -> add_edge
        u, v = subgraph.edges_iter().next()
        reeb.node[component_node]['f_val'] = (
            reeb.node[u]['f_val'] + reeb.node[v]['f_val']) / 2


def remove_redundant_nodes(reeb):
    nodes = [n for n, d in reeb.degree().items() if d == 2]
    for node in nodes:
        f_val = reeb.node[node]['f_val']
        adj1, adj2 = reeb[node].keys()  # G -> reeb
        if (reeb.node[adj1]['f_val'] - f_val) * (reeb.node[adj2]['f_val'] - f_val) < 0:
            reeb.add_edge(adj1, adj2)
            reeb.remove_node(node)
    return nx.convert_node_labels_to_integers(reeb)


def shrink_ints(reeb, epsilon, critical_vals):
    for i in range(len(critical_vals) - 1):
        l, r = critical_vals[i], critical_vals[i + 1]
        if r - l > 2 * epsilon:
            n = max(reeb.node) + 1
            leftNodes = [x for x in reeb.nodes() if reeb.node[x]['f_val'] == l]
            rightNodes = [x for x in reeb.nodes() if reeb.node[
                x]['f_val'] == r]
            leftNewNodes = [i + n for i in leftNodes]
            rightNewNodes = [i + n for i in rightNodes]
            reeb.add_nodes_from(leftNewNodes + rightNewNodes)
            for i in leftNewNodes:
                reeb.node[i]['f_val'] = l + epsilon
            for i in rightNewNodes:
                reeb.node[i]['f_val'] = r - epsilon
            reeb.add_edges_from(zip(leftNodes, leftNewNodes))
            reeb.add_edges_from(zip(rightNodes, rightNewNodes))
            sub_edges = reeb.subgraph(leftNodes + rightNodes).edges()
            for u, v in sub_edges:
                reeb.add_edge(u + n, v + n)
            reeb.remove_edges_from(sub_edges)
    return remove_redundant_nodes(reeb)


def smooth(reeb, epsilon):
    reeb = preprocess(reeb)
    label_edges(reeb)
    critical_vals = get_critical_vals(reeb)
    smallest_edges = get_smallest_int(reeb)
    if smallest_edges:
        l, r, k, d = smallest_edges[0]
        crt_epsilon = d['weight'] / 2
        if epsilon >= crt_epsilon:
            smooth_int(reeb, smallest_edges)
            reeb = shrink_ints(reeb, crt_epsilon, critical_vals)
            if epsilon > crt_epsilon:
                reeb = smooth(reeb, epsilon - crt_epsilon)
        else:
            reeb = shrink_ints(reeb, epsilon, critical_vals)
    return nx.convert_node_labels_to_integers(remove_redundant_nodes(reeb))
