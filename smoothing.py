from __future__ import division
from decimal import Decimal, getcontext

import networkx as nx


getcontext().prec = 3


def get_critical_vals(reeb):
    return sorted(list(set(d['f_val'] for _, d in reeb.nodes_iter(data=True))))


def preprocess(reeb):
    reeb = nx.convert_node_labels_to_integers(reeb)
    for x in reeb.node:
        reeb.node[x]['f_val'] = Decimal(str(reeb.node[x]['f_val']))
    critical_vals = get_critical_vals(reeb)
    for u, v, k in reeb.edges(keys=True):
        intersections = [c for c in critical_vals if
                         (c > reeb.node[u]['f_val'] and c < reeb.node[v]['f_val']) or
                         (c < reeb.node[u]['f_val'] and c > reeb.node[v]['f_val'])]
        if intersections:
            reeb.remove_edge(u, v, k)
            l, r = sorted((u, v), key=lambda x: reeb.node[x]['f_val'])
            x = l
            for intersection in intersections:
                x_prev = x
                x = reeb.number_of_nodes()
                reeb.add_node(x, f_val=intersection)
                reeb.add_edge(x_prev, x)
            reeb.add_edge(x, r)
    return nx.convert_node_labels_to_integers(reeb)


def label_edges(reeb):
    for u, v, k in reeb.edges(keys=True):
        reeb[u][v][k]['weight'] = abs(reeb.node[u]['f_val'] - reeb.node[v]['f_val'])


def get_smallest_int_length(reeb):
    return min(d['weight'] for _, _, d in reeb.edges(data=True))


def remove_redundant_nodes(reeb):
    nodes = [x for x, d in reeb.degree().items() if d == 2 and len(reeb[x]) == 2]
    for x in nodes:
        f_val = reeb.node[x]['f_val']
        adj1, adj2 = reeb[x].keys()
        if (reeb.node[adj1]['f_val'] - f_val) * (reeb.node[adj2]['f_val'] - f_val) < 0:
            reeb.add_edge(adj1, adj2)
            reeb.remove_node(x)
    return nx.convert_node_labels_to_integers(reeb)


def shrink_ints(reeb, epsilon, critical_vals):
    for i in range(len(critical_vals) - 1):
        l, r = critical_vals[i], critical_vals[i + 1]
        if r - l > 2 * epsilon:
            n = max(reeb.node) + 1
            left_nodes = [x for x in reeb.nodes() if reeb.node[x]['f_val'] == l]
            right_nodes = [x for x in reeb.nodes() if reeb.node[x]['f_val'] == r]
            left_new_nodes = [x + n for x in left_nodes]
            right_new_nodes = [x + n for x in right_nodes]
            reeb.add_nodes_from(zip(left_new_nodes, [{'side': 'r'}] * len(left_new_nodes))
                                + zip(right_new_nodes, [{'side': 'l'}] * len(right_new_nodes)))
            for x in left_new_nodes:
                reeb.node[x]['f_val'] = l + epsilon
            for x in right_new_nodes:
                reeb.node[x]['f_val'] = r - epsilon
            reeb.add_edges_from(zip(left_nodes, left_new_nodes))
            reeb.add_edges_from(zip(right_nodes, right_new_nodes))
            sub_edges = reeb.subgraph(left_nodes + right_nodes).edges()
            for u, v in sub_edges:
                reeb.add_edge(u + n, v + n)
            reeb.remove_edges_from(sub_edges)
        elif r - l == 2 * epsilon:
            left_nodes = [x for x in reeb.nodes() if reeb.node[x]['f_val'] == l]
            right_nodes = [x for x in reeb.nodes() if reeb.node[x]['f_val'] == r]
            sub_reeb = reeb.subgraph(left_nodes + right_nodes)
            for component in nx.connected_component_subgraphs(sub_reeb):
                reeb.remove_edges_from(component.edges())
                component_node = max(reeb.node) + 1
                for x in component.nodes():
                    reeb.add_edge(x, component_node)
                reeb.node[component_node]['f_val'] = (l + r) / 2
    return reeb


def add_at_two_ends(reeb, epsilon, critical_vals):
    # add nodes at the two ends of the reeb graph
    n = max(reeb.node) + 1
    l = critical_vals[0]
    r = critical_vals[-1]
    left_end_nodes = [x for x in reeb.nodes() if reeb.node[x]['f_val'] == l]
    right_end_nodes = [x for x in reeb.nodes() if reeb.node[x]['f_val'] == r]
    left_new_end_nodes = [i + n for i in left_end_nodes]
    right_new_end_nodes = [i + n for i in right_end_nodes]
    reeb.add_nodes_from(left_new_end_nodes + right_new_end_nodes)
    for i in left_new_end_nodes:
        reeb.node[i]['f_val'] = l - epsilon
    for i in right_new_end_nodes:
        reeb.node[i]['f_val'] = r + epsilon
    reeb.add_edges_from(zip(left_end_nodes, left_new_end_nodes))
    reeb.add_edges_from(zip(right_end_nodes, right_new_end_nodes))
    return reeb


def smooth(reeb, epsilon):
    epsilon = Decimal(str(epsilon))
    reeb = preprocess(reeb)
    if epsilon <= 0:
        return reeb
    label_edges(reeb)
    critical_vals = get_critical_vals(reeb)
    crt_epsilon = get_smallest_int_length(reeb) / 2
    if epsilon >= crt_epsilon:
        reeb = shrink_ints(reeb, crt_epsilon, critical_vals)
        reeb = add_at_two_ends(reeb, crt_epsilon, critical_vals)
        reeb = remove_redundant_nodes(reeb)
        reeb = smooth(reeb, epsilon - crt_epsilon)
    else:
        reeb = shrink_ints(reeb, epsilon, critical_vals)
        reeb = add_at_two_ends(reeb, epsilon, critical_vals)
        reeb = remove_redundant_nodes(reeb)
    label_edges(reeb)
    return nx.convert_node_labels_to_integers(preprocess(reeb))
