import igraph as ig
import matplotlib.pyplot as plt
import numpy as np
import os, sys
from copy import copy
if __name__ == "__main__" and __package__ is None:
    # Go up one level to the package root
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    __package__ = "tempnetviz"
from .read_graph import *

def get_metric(data, metric, default_node_size, **kwargs):
        if isSymmetric(data):
            g = ig.Graph.Weighted_Adjacency(data, mode='undirected')
        else:
            g = ig.Graph.Weighted_Adjacency(data, mode='directed')    
    
        if metric == "betweenness":
            edge_betweenness = g.betweenness(weights = [1/e['weight'] for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
            edge_betweenness = ig.rescale(edge_betweenness)
            node_size = [(1+e)*default_node_size for e in edge_betweenness]
        elif metric == "strength":
            edge_strength = g.strength(weights = [e['weight'] for e in g.es()])
            edge_strength = ig.rescale(edge_strength)
            node_size = [(1+e)*default_node_size for e in edge_strength]
        elif metric == "closeness":
            edge_closeness = g.closeness(weights = [1/e['weight'] for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
            edge_closeness = ig.rescale(edge_closeness)
            node_size = [(1+e)*default_node_size for e in edge_closeness]
        elif metric == "hub score":
            edge_hub = g.hub_score(weights = [e['weight'] for e in g.es()])
            edge_hub = ig.rescale(edge_hub)
            node_size = [(1+e)*default_node_size for e in edge_hub]
        elif metric == "authority score":
            edge_authority = g.authority_score(weights = [e['weight'] for e in g.es()])
            edge_authority = ig.rescale(edge_authority)
            node_size = [(1+e)*default_node_size for e in edge_authority]
        elif metric  == "eigenvector centrality":
            random.seed(1)
            edge_evc = g.eigenvector_centrality(weights = [e['weight'] for e in g.es()])
            edge_evc = ig.rescale(edge_evc)
            node_size = [(1+e)*default_node_size for e in edge_evc]
        elif metric  == "page rank":
            edge_pagerank = g.personalized_pagerank(weights = [e['weight'] for e in g.es()])
            edge_pagerank = ig.rescale(edge_pagerank)
            node_size = [(1+e)*default_node_size for e in edge_pagerank]
        elif metric  == "rich-club":
            k_degree = kwargs["deg"]
            node_size = rich_club_weights(g, k_degree, 0.3)
            node_size = [n*default_node_size for n in node_size]
        elif metric == "k-core":
            k_degree = kwargs["deg"]
            node_size = k_core_weights(data, k_degree, 0.5)
            node_size = [n*default_node_size for n in node_size]
        else: # in case no metric is given
            node_size = [default_node_size]*data.shape[0]
            
        return node_size
    
def get_ordering_indices(g):
    """
    orders the nodes in input graph g according to detected communities, and within each
    community according to increasing strength. This is to minimize edge overlap in final plot.
    """
    communities = g.community_optimal_modularity(weights=[1/e['weight'] for e in g.es()]) 
    idx = [i for i in range(len(communities))]
    strengths = np.array(g.strength())
    ordered_indices = [0 for i in range(g.vcount())]
    for i in range(len(communities)):
        for j in communities[i]:
            ordered_indices[j] = i
    counter = 0
    communities = np.array(copy(ordered_indices))
    final_sorting = np.zeros(g.vcount())
    for value in np.unique(communities):
        where_value = np.where(communities == value)[0]
        sorting_str_idx = where_value[np.argsort(strengths[where_value])]
        for idx, pos in enumerate(sorting_str_idx):
            final_sorting[pos] += idx + counter 
        counter += np.sum(communities == value)
    return final_sorting

def plot_temporal_layout(path_to_file, ax=None, percentage_threshold = 0.0, mnn = None, avg_graph = False,
                  affinity = True, rm_fb_loops = True, mutual = True, rm_index = True, **kwargs):
    #loading data
    layers = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, mutual = mutual, \
                      avg_graph = avg_graph, affinity = affinity, rm_fb_loops = rm_fb_loops, rm_index = rm_index, return_ig=True)
    data = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, mutual = mutual, \
                      avg_graph = avg_graph, affinity = affinity, rm_fb_loops = rm_fb_loops, rm_index = rm_index)
    node_number = data[0].shape[0]
    timesteps = len(layers)

    # getting node ordering for plotting layout
    avg_graph = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, mutual = mutual, \
                      avg_graph = True, affinity = affinity, rm_fb_loops = rm_fb_loops, rm_index = rm_index, 
                      return_ig = True)[0]
    order_y = get_ordering_indices(avg_graph)
    # order_y = range(node_number)
    
    # parameters for graph plotting
    if rm_index == False and ("node_labels" in kwargs and kwargs["node_labels"]):
        node_labels = [str(i) for i in range(len(read_labels(path_to_file)))] 
    elif ("node_labels" in kwargs and kwargs["node_labels"]):
        node_labels = read_labels(path_to_file) 
    else:
        node_labels = None
    default_node_size = kwargs["node_size"] if "node_size" in kwargs else 15
    default_edge_width = kwargs["edge_width"] if "edge_width" in kwargs else 5
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        
    # Plot each time point
    for time_idx in range(timesteps):
        layout = []
        for i in range(node_number):  
            layout.append((time_idx, order_y[i]))  # Position nodes vertically (y-axis)
        
        if isSymmetric(data[time_idx]):
            directed = False
        else:
            directed = True
        mode = 'directed' if directed else 'undirected'
        subgraph = ig.Graph.Weighted_Adjacency(data[time_idx],  mode = mode)
        if rm_fb_loops:
            subgraph.delete_edges([edge for edge in subgraph.es if edge.source == edge.target])

        # Visual styling
        visual_style = {}
        # visual_style["vertex_label"] = g.vs["name"]
        node_size = get_metric(data[time_idx], kwargs["node_metric"], default_node_size, deg = kwargs["deg"])
        visual_style["vertex_size"] = node_size
        visual_style["vertex_color"] = [kwargs["node_cmap"](s) for s in rescale(node_size, 1) - 0.01] if kwargs["node_cmap"] != "none" else "black"

        visual_style["vertex_label_size"] = node_size
        visual_style["edge_width"] = 2
        visual_style["edge_color"] = "gray"
        visual_style["edge_curved"] = 0.2
        visual_style["edge_arrow_width"] = 10 if directed else 0
        if "edge_cmap" in kwargs:
            edge_cmap = kwargs["edge_cmap"]
        else:
            edge_cmap = get_cmap('Greys')
        
        if "scale_edge_width" in kwargs and type(kwargs["scale_edge_width"]) == bool:
            if kwargs["scale_edge_width"]: #if true, adapt edge_thickness to edge value, else all edges are shown with same width.
                display_edge_width = rescale(np.array([w['weight'] for w in layers[time_idx].es]), default_edge_width)
                edge_color = [edge_cmap(edge) for edge in rescale(np.array([w['weight'] for w in layers[time_idx].es])) - 0.01]
            else:
                display_edge_width = np.array([0.99 if w['weight'] > 0.01 else 0 for w in layers[time_idx].es])*default_edge_width
                edge_color = [edge_cmap(edge) for edge in rescale(np.array([w['weight'] for w in layers[time_idx].es])) - 0.01]
        else:
            display_edge_width = rescale(np.array([w['weight'] for w in layers[time_idx].es]), default_edge_width)
            edge_color = [edge_cmap(edge) for edge in rescale(np.array([w['weight'] for w in layers[time_idx].es])) - 0.01]

        visual_style["edge_width"] = display_edge_width
        visual_style["edge_color"] = edge_color
        ig.plot(subgraph, target=ax, layout=layout, **visual_style)
        
    ax.set_yticks(range(node_number))
    ax.set_yticklabels(node_labels)  # Label each tick
    ax.set_xticks(range(timesteps))  # Set ticks at each time step position
    ax.set_xticklabels([f'{i+1}' for i in range(timesteps)])  # Label each tick
    ax.set_xlabel('Timesteps')
    ax.grid(alpha = 0.5)
    
if __name__ == "__main__":
    path = "..\\..\\data\\nosemaze\\both_cohorts_1days\\G1\\"
    file1 = "interactions_resD1_01.csv"
    file2 = "interactions_resD1_02.csv"
    file3 = "interactions_resD1_03.csv"
    file4 = "interactions_resD1_04.csv"
    file5 = "interactions_resD1_05.csv"
    file6 = "interactions_resD1_06.csv"
    file7 = "interactions_resD1_07.csv"
    file8 = "interactions_resD1_08.csv"
    file9 = "interactions_resD1_09.csv"
    file10 = "interactions_resD1_10.csv"
    file11 = "interactions_resD1_11.csv"
    file12 = "interactions_resD1_12.csv"
    paths = [path+file1, path+file2,path+file3, path+file4, 
            path+file5,  path+file6,  path+file7, path+file8
            , path+file9, path+file10, path+file11, path+file12]
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    plot_temporal_layout(paths, ax, mnn = 5, deg = 3,
                         node_size = 10, edge_width = 2, between_layer_edges = False, 
                         rm_fb_loops=True,  cluster_num = None, node_labels = True, rm_index = True,
                         node_metric = "k-core", node_cmap = cm.coolwarm, edge_cmap = cm.Greys, scale_edge_width = False)