# How to create a network topology in Python
## Python-iGraph
Reference: [python-igraph](https://igraph.org/python/)
- If you use `pip install`, we use the package of python-igraph by installed with `pip3` as following: </br>
  - $`pip3 install python-igraph`
- If you use `conda`, we install python-igraph by </br>
  - $`conda install -c conda-forge python-igraph`
- If you have a problem with plotting a graph, you may need to install [cairograph](https://www.cairographics.org/download/)
  
## NetworkX
Reference : [NetworkX](https://networkx.org/documentation/latest/tutorial.html)
- If you use `pip` or `pip3` for installation , you can use command :
  - $`pip3 install networkx`
- Use [Dijkstra algorithm](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.dijkstra_path.html) 
  - [Tutorial](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/Python_Graph/Simple_edge_topology.ipynb)
- Examples of creating a simple graph with networkx
  - [Create a simple graph](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/Python_Graph/Simple_edge_topology.ipynb)
  - [How to find a shortest path with Dijkstra's algorithm](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/Python_Graph/Simple_Graph_with_multiple_edge_attributes.ipynb)
  - [How to run the optimum-pruning-based routing algorithm](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/Python_Graph/A%20simple%20graph%20with%20optimal%20pruning%20based%20routing.ipynb)