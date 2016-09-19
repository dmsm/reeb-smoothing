# Visualization of All-scale Smoothing for Reeb Graphs

## The `.reeb` file format

This script takes as input a Reeb graph incoded in a `.reeb` file. A `.reeb` file must contain two lines. The first line should consist of a comma-delimited list of function values for each vertex in the graph. The second line should consist of a comma-delimited list of tuples corresponding edges between vertices. An Reeb graph with five vertices and nine edges might look as follows:

```
0,1,3,3,1
(0,1),(0,1),(1,2),(1,3),(3,4),(3,4),(2,4),(3,4),(0,1)
```

We include four sample `.reeb` files.

## Running the visualization script

To visualize the smoothing of a Reeb graph stored in `graph.reeb`, make sure you have installed all the dependencies, and run `python graph_reeb.py graph.reeb`. By default, our tool displays an animation demonstrating how the graph changes as the smoothing radius increases. Additionally, the following flags are available:

- `--epsilon r` allows you to specify a value `r` in order to display the Reeb graph smoothed by radius `r`
- `--multiplot` displays a multiplot containing snapshots of the Reeb graph for multiple increasing smoothing radii
