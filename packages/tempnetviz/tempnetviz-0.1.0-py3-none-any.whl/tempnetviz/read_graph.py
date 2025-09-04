import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import igraph as ig
from copy import deepcopy
from matplotlib.cm import ScalarMappable, get_cmap
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap, Normalize
from igraph.drawing.colors import ClusterColoringPalette
import random
import os, sys
from copy import copy
from warnings import warn
from tkinter import messagebox as mb

if __name__ == "__main__" and __package__ is None:
    # Go up one level to the package root
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    __package__ = "tempnetviz"
    
from .multilayer_plot import *
from .graph_animation import *
import pandas as pd
import time 
import matplotlib.colors as mcolors


def isSymmetric(mat):
    transmat = np.array(mat).transpose()
    if np.array_equal(mat, transmat):
        return True
    return False

def rescale(arr, max_val = 5):
    normalized_arr = (arr - np.min(arr))/(np.max(arr)-np.min(arr))
    return normalized_arr*max_val

def inverse(arr, remove_feedback_loops = True):
    """
    Computes the 'inverse' of a graph matrix by taking 1/x where x is an entry
    only when x != 0 and represents the edge values (or distances between vertices).
    """
    inv_arr = deepcopy(arr)
    inv_arr[inv_arr == 0] = 10e-10 #np.Inf
    inv_arr = 1/inv_arr
    if remove_feedback_loops: # affinity for each element with itself is set to 0 in this case.
        idx = np.diag_indices(inv_arr.shape[0], 2)
        inv_arr[idx] = 0 
    return inv_arr

def nn_cut(arr, nn = 2):
    """
    Cuts the edges of the graph in the input array by keeping only the edges that are nearest neighbors.
    Nodes that are further away the 'nn' neighbours have their edges cut.  The cut is NOT direction specific,
    meaning that two nodes are nearest neighbors if they are nearest neighbors in the outgoing direction 
    OR in the ingoing direction.

        Parameter:
                arr: array representing the graph
                nn: number of nearest neighbors to keep
        return:
                array representing the graph with cut edges
    """
    assert nn >= 1, "nn should be a positive integer bigger than 1." # nn = 0 means self ineractions with is trivially true (unless stated otherwise)
    nn_arr = np.zeros_like(arr) 
    neighbors_i = np.argsort(-arr, 1) #computing the nearest neighbors for local nn estimation
    neighbors_j = np.argsort(-arr, 0)
    for i in range(nn_arr.shape[0]):
        # nearest neighbours keep their value
        nn_arr[i, neighbors_i[i, :nn]] = arr[i, neighbors_i[i, :nn]]
        nn_arr[neighbors_j[:nn, i], i] = arr[neighbors_j[:nn, i], i] 
        # other elements are put to 0 (0.01 for visualization).
        nn_arr[i, neighbors_i[i, nn:]] = 0.0
        nn_arr[neighbors_j[nn:, i], i] = 0.0  

    return nn_arr

def mnn_cut(arr, nn = 2):
    """
    Cuts the edges of the graph in the input array by keeping only the edges that are mutual nearest neighbors.
    Nodes that are further away the 'nn' neighbours have their edges cut.

        Parameter:
                arr: array representing the graph
                nn: number of nearest neighbors to keep
        return:
                array representing the graph with cut edges
    """
    assert nn >= 1, "nn should be a positive integer bigger than 1." # nn = 0 means self ineractions with is trivially true (unless stated otherwise)
    mnn_arr = np.zeros_like(arr) + 0.0 #0.01 for visualization, to force igraph to keep layout
    neighbors_i = np.argsort(-arr, 1) #computing the nearest neighbors for local nn estimation
    neighbors_j = np.argsort(-arr, 0)
    for i in range(arr.shape[1]):
        for j in range(i, arr.shape[1]):
            if any(np.isin(neighbors_i[i, 0:nn], j)) and any(np.isin(neighbors_j[0:nn, j], i)): #local nearest distance estimation
                mnn_arr[i, j] += arr[i, j]
                mnn_arr[j, i] += arr[j, i]
    return mnn_arr

def read_labels(path_to_file):
    """
    Reads a list of labels for the nodes to plot in the graph

    Parameters
    ----------
    path_to_file : TYPE string or list of string containing the path to the file(s)

    Returns
    -------
    TYPE
        list of nodes labels
    """

    if type(path_to_file) == str:
        arr = pd.read_csv(path_to_file)
        labels = arr.iloc[:, 0]
        return [l for l in labels]
    
    elif type(path_to_file) == list:
        arr = pd.read_csv(path_to_file[0])
        labels = arr.iloc[:, 0]
        return [l for l in labels]
        
def read_graph(path_to_file, percentage_threshold = 0.01, mnn = None, return_ig = False,
               avg_graph = False, affinity = True, rm_fb_loops = True, mutual = True, rm_index = True):
    """
    Reads a file containing the weights defning the adjacency matrix. 

    Parameters
    ----------
    path_to_file : TYPE string or list of string containing the path to the file(s)
    percentage_threshold : parameter specifying the edge value threshold under which edges are not displayed.
        should be given as a percentage of the maximum edge value. Default is 0.0
    mnn : number of nearest neighbours for graph cut. Default is None
    return_ig : TYPE, optional
        Whether or not to return the read graphs as an ig.Graph. if false, numpy arrays are returned.
        The default is False.
    affinity: TYPE Bool. Whethere or not the data stored in the graph represents affinity between nodes or distance.
        If true, the graph is read as is, otherwise the values in the input matrice(s) are inverted.

    Returns
    -------
    TYPE
        list of graphs as np array or ig.Graph
    """

    random.seed(1) #making sure layout of plots stays the same when changing metrics
    start_idx = 1 if rm_index else 0
    if not avg_graph:
        #accounting for potential multiple layers
        data = []
        for i in range(len(path_to_file)):
            arr = np.loadtxt(path_to_file[i], delimiter=",", dtype=str)
            layer_data = arr[start_idx:, start_idx:].astype(float)
            if not affinity: # if graph edges represent distances and not affinities, need to invert values
               layer_data = inverse(layer_data, rm_fb_loops)

            threshold = np.max(layer_data) * (percentage_threshold / 100.0)
            layer_data = np.where(layer_data < threshold, 0.0, layer_data)  #0.01 for visualization, to force igraph to keep layout
            if mnn is not None:
                if mutual:
                    layer_data = mnn_cut(layer_data, mnn) # mutual nearest neighbours
                else:
                    layer_data = nn_cut(layer_data, mnn)  # nearest neighbours

            data.append(layer_data)
        if return_ig: # return_ig specifies if the output should be returned as an ig.Graph.
            layers = [ig.Graph.Weighted_Adjacency(d, mode='directed') for d in data]
            return layers
        return data
    
    elif avg_graph:
        # averaged graph
        arr = np.loadtxt(path_to_file[0], delimiter=",", dtype=str)
        data = arr[start_idx:, start_idx:].astype(float)/len(path_to_file)
        for i in range(1, len(path_to_file)):
            arr = np.loadtxt(path_to_file[i], delimiter=",", dtype=str)
            data += arr[start_idx:, start_idx:].astype(float)/len(path_to_file) 
        if not affinity:
           data = inverse(data, rm_fb_loops)
           
        threshold = np.max(data) * (percentage_threshold / 100.0)
        data = np.where(data < threshold, 0.0, data)
        if mnn is not None:
            if mutual:
                data = mnn_cut(data, mnn)
            else:
                data = nn_cut(data, mnn)
        if return_ig: # return ig specifies if the read graphs should be returned as an ig.Graph.
            avg_layer = ig.Graph.Weighted_Adjacency(data, mode='directed') 
            return [avg_layer]
        return [data]
        
def randomize_graph(path_to_file, percentage_threshold = 0.01, mnn = None, return_ig = False,
                    avg_graph = False, affinity = True, mutual = True, rm_index = True):
    """
    Reads a file containing the weights defning the adjacency matrix, then randomizes the graph 
    for bootstrap purposes.

    see 'read_graph' for input params.
    """

    random.seed(1) #making sure layout of plots stays the same when changing metrics
    start_idx = 1 if rm_index else 0
    if len(path_to_file) == 1:
        arr = np.loadtxt(path_to_file, delimiter=",", dtype=str)
        data = arr[start_idx:, start_idx:].astype(float)
        np.random.shuffle(data) # randomizing graph while keeping weights constant.
        if not affinity: # If input data represents distance, need to invert values
            data = inverse(data)
        threshold = np.max(data) * (percentage_threshold / 100.0)
        data = np.where(data < threshold, 0.0, data)
        
        if mnn is not None:
            if mutual:
                data = mnn_cut(data, mnn)
            else:
                data = nn_cut(data, mnn)

        if return_ig: # return ig specifies if the read graphs should be returned as an ig.Graph.
            graph = [ig.Graph.Weighted_Adjacency(data, mode='directed')]
            return graph
        return [data]
    
    elif len(path_to_file) > 1:
        arr = np.loadtxt(path_to_file[0], delimiter=",", dtype=str)
        data = arr[start_idx:, start_idx:].astype(float)/len(path_to_file)
        for i in range(1, len(path_to_file)):
            arr = np.loadtxt(path_to_file[i], delimiter=",", dtype=str)
            data += arr[start_idx:, start_idx:].astype(float)/len(path_to_file) 
        np.random.shuffle(data) # randomizing graph while keeping weights constant.
        if not affinity: # If input data represents distance, need to invert values
            data = inverse(data)
        threshold = np.max(data) * (percentage_threshold / 100.0)
        data = np.where(data < threshold, 0.0, layer_data)  #0.01 for visualization, to force igraph to keep layout
        if mnn is not None:
            if mutual:
                data = mnn_cut(data, mnn)
            else:
                data = nn_cut(data, mnn)

        if return_ig: # return ig specifies if the read graphs should be returned as an ig.Graph.
            avg_layer = ig.Graph.Weighted_Adjacency(data, mode='directed')
            return [avg_layer]
        return [data]
        
def rich_club_weights(graph, k, min_val = 0.05):
    """
    Computes the rich-club for input graph: each node that has a degree < k is not part of it.

    Parameters
    ----------
    graph : the graph to compute onto
    k: the degree for rich-club computation
    min_val: minimum weight value (defaults to 0.05)

    Returns
    -------
    A list of nodes weights where each member of the rich-club is 1 and others are 'min_val'
    """

    weights = []
    for i in range(len(graph.vs())):
        incident_edges = np.array([e["weight"] for e in graph.vs[i].incident()])
        if np.sum(incident_edges > 0.01) >= k:
            weights.append(1)
        else:
            weights.append(min_val)
    return weights

def k_core_weights(data, k, min_val = 0.05):
    """
    Computes the k_core(s) for input graph: nodes that have at least k connexdion among themselves are
    part of k-core.

    Parameters
    ----------
    graph : the graph to compute onto
    k: the degree for rich-club computation
    min_val: minimum weight value (defaults to 0.05)

    Returns
    -------
    A list of nodes weights where each member of the rich-club is 1 and others are 'min_val'
    """
    
    if type(data) != np.ndarray:
        data = np.array(data.get_adjacency(attribute="weight").data)
    
    weights = []
    # First figure out rich-club within data matrix
    binary_data = copy(data)
    binary_data[data > min_val] = 1
    binary_data[data <= min_val] = 0
    core_matrix = binary_data
    core_matrix[np.sum(binary_data, 1) < k, :] = 0
    core_matrix[:, np.sum(binary_data, 0) < k] = 0
    # Then, figure out if members of rich-club are connected enough
    for i in range(core_matrix.shape[0]):
        if np.sum(core_matrix[i, :]) >= k:
            weights.append(1)
        else:
            weights.append(min_val)
    return weights

def rich_club_size(graph, k, min_val = 0.05):
    """
    Returns the size of the rich_club of input graph  for degree = k.
    """
    sizes = rich_club_weights(graph, k)
    core_size = 0
    for s in sizes:
        if s > 0.1:
            core_size += 1
    return core_size

def k_core_size(graph, k, min_val = 0.05):
    """
    Returns the size of the k core of input graph for degree = k.
    """
    sizes =  k_core_weights(graph, k)
    core_size = 0
    for s in sizes:
        if s > 0.1:
            core_size += 1
    return core_size

def rich_club_p_value(path_to_file, k, percentage_threshold, mnn, affinity = True, bootstrap_iter = 250, mutual = True):
    """
    Computes an estimation of the k core size in the random case to give a p-value for
    the computed rich-club in the input graph. Does so by randomizing the network (keep weights same) 
    this is done 'bootstrap_iter' times and allows to the distribution of the random rich_club values.

    Parameters
    ----------
    path_to_file 
    k : Int. degree value for the rich-club computation
    bootstrap_iter : Int. number of iterations for the bootstrap estimation.

    Returns
    -------
    p_value

    """
    if len(path_to_file) > 1:
        mb.showwarning(title = "Warning", message = "The measurment of the rich-club p-value is given for the averaged graph, as no multilayer single confidence interval can be given. ")
    input_layer = randomize_graph(path_to_file, percentage_threshold=percentage_threshold,\
                                       mnn=mnn,return_ig= True, avg_graph = True, affinity = affinity, mutual = mutual)
    actual_observation = rich_club_size(input_layer, k)
    random_observations = np.zeros(bootstrap_iter)
    for i in range(bootstrap_iter):
        random_layer = randomize_graph(path_to_file, percentage_threshold=percentage_threshold,\
                                       mnn=mnn,return_ig= True, avg_graph = True, affinity = affinity, mutual = mutual)
        random_observations[i] = rich_club_size(random_layer, k)
    p_value = np.sum(random_observations == actual_observation)/bootstrap_iter
    return p_value

def community_clustering(path_to_file, algorithm = "modularity", mnn = None, percentage_threshold = 0.0, mutual = True,  affinity = True, **kwargs):
    """
    Clusters input graph into communities, follow the optimal community algorithm

    Parameters
    ----------
    path_to_file : list of path to graph files

    Returns 
    -------
    idx: list of indexes for the nodes.
    """
    if len(path_to_file) > 1:
        # mb.showwarning(title = "Warning", message = "Community will be computed on the averaged graph, as the algorithm cannot deal with multilyer information.")
        data = read_graph(path_to_file, avg_graph=True, mnn = mnn, 
                          percentage_threshold=percentage_threshold, mutual = mutual,  affinity = affinity)[0]
    else:
        data = read_graph(path_to_file, avg_graph=True, mnn = mnn, 
                          percentage_threshold=percentage_threshold, mutual = mutual,  affinity = affinity)[0]
    
    data = np.where(data <= 0.01, 0, data) 
    
    if isSymmetric(data):
        g = ig.Graph.Weighted_Adjacency(data, mode='undirected')
    else:
        g = ig.Graph.Weighted_Adjacency(data, mode='directed')
        
    if algorithm == "modularity":
        communities = g.community_optimal_modularity(weights = [1/(e['weight']) for e in g.es()])
    elif algorithm == "louvain":
        communities = g.community_multilevel(weights=[1/e['weight'] for e in g.es()])
    elif algorithm == "walktrap":
        dendrogram = g.community_walktrap(weights=[1/e['weight'] for e in g.es()])
        communities = dendrogram.as_clustering()
    elif algorithm == "infomap":
        communities = g.community_infomap(edge_weights=[1/e['weight'] for e in g.es()])

    total_length = data.shape[0]
    idx = [0 for i in range(total_length)]
    for i in range(len(communities)):
        for j in communities[i]:
            idx[j] = i
    return idx
    
def display_graph(path_to_file, ax, percentage_threshold = 0.0, mnn = None, avg_graph = False,
                  affinity = True, rm_fb_loops = True, mutual = True, rm_index = True, **kwargs):
    """
    This function displays the graph to analyze and colors the vertices/edges according
    to the given input parameters.

    Parameters
    ----------
    path_to_file : string
        path specifying where the file containing the matrix representing the graph 
        is stored. Should be a .csv file.
    ax : matplotlib.axis
        the axis to plot the graph onto.
    threshold : parameter specifying the edge value threshold under which edges are not displayed.
    mnn : number of nearest neighbours for graph cut
    avg_graph: Bool. In case of multilayers, whether or not to plot the averaged graph instead.
    affinity: Whether the edges represent an affinity measurement (if True) or a distance (if False) (i.e. high value = high similarity or 
        high value = high difference). Defaults to True.
    rm_fb_loops: Bool. Whether or not to remove the feedback loops (edges of nodes with themselves) in graph display.
    **kwargs : strings
        layout : specifies which layout to use for displaying the graph. see igraph documentation for 
            a detailed list of all layout. should be given as a string as stated in the igraph doc.
        node_metric : specifies which metric to use in order to color and size the vertices of the graph.
            allowed values: ["strength", "betweenness", "closeness", "eigenvector centrality", "page rank", "hub score", "authority score"]

    Returns
    -------
    None.
    """

    random.seed(1) #making sure layout of plots stays the same when changing metrics
    
    if "layout" in kwargs:
        layout_style = kwargs["layout"]
    else:
        layout_style = "fr"
        
    if rm_index == False and ("node_labels" in kwargs and kwargs["node_labels"]):
        node_labels = [str(i) for i in range(len(read_labels(path_to_file)))] 
    elif ("node_labels" in kwargs and kwargs["node_labels"]):
        node_labels = read_labels(path_to_file) 
    else:
        node_labels = None
        
    if len(path_to_file) > 1 and not avg_graph:
        layer_labels = kwargs["layer_labels"] if "layer_labels" in kwargs else None
        display_graph_3d(path_to_file, ax = ax, percentage_threshold = percentage_threshold, mnn = mnn, affinity = affinity, \
                         rm_fb_loops = rm_fb_loops, mutual = mutual, layout = layout_style, node_metric = kwargs["node_metric"], idx = kwargs["idx"], \
                         cluster_num = kwargs["cluster_num"], layer_labels = layer_labels, node_labels = node_labels, deg = kwargs["deg"], 
                         node_size = kwargs["node_size"], edge_width = kwargs["edge_width"], scale_edge_width = kwargs["scale_edge_width"],
                         between_layer_edges = kwargs["between_layer_edges"], rm_index = rm_index,
                         show_planes = kwargs["show_planes"], edge_cmap = kwargs["edge_cmap"], node_cmap = kwargs["node_cmap"])
        return
    else:
        data = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, mutual = mutual, \
                          avg_graph = avg_graph, affinity = affinity, rm_fb_loops = rm_fb_loops, rm_index = rm_index)[0]

    if isSymmetric(data):
        g = ig.Graph.Weighted_Adjacency(data, mode='undirected')
    else:
        g = ig.Graph.Weighted_Adjacency(data, mode='directed')
        
    # default values
    node_color = "black"
    default_node_size = kwargs["node_size"] if "node_size" in kwargs else 15
    default_edge_width = kwargs["edge_width"] if "edge_width" in kwargs else 5

    if "node_cmap" in kwargs and kwargs["node_cmap"] != "none":
        cmap1 = kwargs["node_cmap"]
    else:
        cmap1 = mcolors.ListedColormap(['black'])
        
    if "node_metric" in kwargs:
        if kwargs["node_metric"] == "betweenness":
            edge_betweenness = g.betweenness(weights = [1/e['weight'] for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
            edge_betweenness = ig.rescale(edge_betweenness)
            node_size = [(1+e)*default_node_size for e in edge_betweenness]
            node_color = [cmap1(b) for b in edge_betweenness]
        elif kwargs["node_metric"] == "strength":
            edge_strength = g.strength(weights = [e['weight'] for e in g.es()])
            edge_strength = ig.rescale(edge_strength)
            node_size = [(1+e)*default_node_size for e in edge_strength]
            node_color = [cmap1(b) for b in edge_strength]
        elif kwargs["node_metric"] == "closeness":
            edge_closeness = g.closeness(weights = [1/e['weight'] for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
            edge_closeness = ig.rescale(edge_closeness)
            node_size = [(1+e)*default_node_size for e in edge_closeness]
            node_color = [cmap1(b) for b in edge_closeness]
        elif kwargs["node_metric"] == "hub score":
            edge_hub = g.hub_score(weights = [e['weight'] for e in g.es()])
            edge_hub = ig.rescale(edge_hub)
            node_size = [(1+e)*default_node_size for e in edge_hub]
            node_color = [cmap1(b) for b in edge_hub]
        elif kwargs["node_metric"] == "authority score":
            edge_authority = g.authority_score(weights = [e['weight'] for e in g.es()])
            edge_authority = ig.rescale(edge_authority)
            node_size = [(1+e)*default_node_size for e in edge_authority]
            node_color = [cmap1(b) for b in edge_authority]
        elif kwargs["node_metric"] == "eigenvector centrality":
            random.seed(1)
            edge_evc = g.eigenvector_centrality(weights = [e['weight'] for e in g.es()])
            edge_evc = ig.rescale(edge_evc)
            node_size = [(1+e)*default_node_size for e in edge_evc]
            node_color = [cmap1(b) for b in edge_evc]
        elif kwargs["node_metric"] == "page rank":
            edge_pagerank = g.personalized_pagerank(weights = [e['weight'] for e in g.es()])
            edge_pagerank = ig.rescale(edge_pagerank)
            node_size = [(1+e)*default_node_size for e in edge_pagerank]
            node_color = [cmap1(b) for b in edge_pagerank]
        elif kwargs["node_metric"] == "rich-club":
            k_degree = kwargs["deg"]
            node_size = rich_club_weights(g, k_degree, 0.3)
            # node_color = [cmap1(0.5) if b == 1 else cmap1(0.2) for b in node_size]
            node_color = ["gray" for b in node_size]
            node_size = [n*default_node_size for n in node_size]
        elif kwargs["node_metric"] == "k-core":
            k_degree = kwargs["deg"]
            node_size = k_core_weights(data, k_degree, 0.5)
            node_color = [cmap1(0.99) if b == 1 else cmap1(0.2) for b in node_size]
            node_size = [n*default_node_size for n in node_size]
        else: # in case no metric is given
            node_size = default_node_size
        
    if "idx" in kwargs:
        if len(kwargs["idx"]) == 0:
            marker_frame_color = node_color
        else:
            cmap = get_cmap('Spectral')
            values, _ = np.unique(kwargs["idx"], return_counts=True)
            palette = ClusterColoringPalette(len(values))
            marker_frame_color = [palette[i] for i in kwargs["idx"]]#cmap(kwargs["idx"])
    else:
        marker_frame_color = node_color
        
    layout = g.layout(layout_style)
    visual_style = {}
    visual_style["vertex_size"] = node_size
    visual_style["vertex_color"] = node_color
    visual_style["vertex_frame_color"] = marker_frame_color
    if "edge_cmap" in kwargs:
        edge_cmap = kwargs["edge_cmap"]
    else:
        edge_cmap = get_cmap('Greys')
    visual_style["edge_arrow_width"] = rescale(np.array([w['weight'] for w in g.es]), default_edge_width)*(default_edge_width)
    
    if "scale_edge_width" in kwargs and type(kwargs["scale_edge_width"]) == bool:
        if kwargs["scale_edge_width"]: #if true, adapt edge_thickness to edge value, else all edges are shown with same width.
            display_edge_width = rescale(np.array([w['weight'] for w in g.es]), default_edge_width)
            edge_color = [edge_cmap(edge) for edge in rescale(np.array([w['weight'] for w in g.es])) - 0.01]
        else:
            display_edge_width = np.array([0.99 if w['weight'] > 0.01 else 0 for w in g.es])*default_edge_width
            edge_color = [edge_cmap(edge) for edge in rescale(np.array([w['weight'] for w in g.es])) - 0.01]
    else:
        display_edge_width = rescale(np.array([w['weight'] for w in g.es]), default_edge_width)
        edge_color = [edge_cmap(edge) for edge in rescale(np.array([w['weight'] for w in g.es])) - 0.01]

    visual_style["edge_width"] = display_edge_width
    visual_style["edge_color"] = edge_color
    
    visual_style["layout"] = layout

    if isSymmetric(data):
        visual_style["edge_curved"] = 0.0
    else:
        visual_style["edge_curved"] = 0.2
    visual_style["vertex_frame_width"] = 3
    visual_style["vertex_label"] = node_labels
    g.vs["name"] = node_labels
    visual_style["vertex_label_dist"] = 5  # Adjust this value as needed
    visual_style["vertex_font"] = "Times"
    ig.plot(g, target=ax, **visual_style)
    
def display_graph_3d(path_to_file, ax, percentage_threshold = 0.0, mnn = None, affinity = True,
                     rm_fb_loops = True, mutual = True, rm_index = True, **kwargs):
    """
    This function displays the graph to analyze and colors the vertices/edges according
    to the given input parameters.

    Parameters
    ----------
    path_to_file : string
        path specifying where the file containing the matrix representing the graph 
        is stored. Should be a .csv file.
    ax : matplotlib.axis
        the axis to plot the graph onto.
    threshold : parameter specifying the edge value threshold under which edges are not displayed.
    mnn : number of nearest neighbours for graph cut
    affinity: Whether the edges represent an affinity measurement (if True) or a distance (if False) (i.e. high value = high similarity or 
        high value = high difference). Defaults to True.
    rm_fb_loops: Bool. Whether or not to remove feedback loops from graph display
    **kwargs : strings
        layout : specifies which layout to use for displaying the graph. see igraph documentation for 
            a detailed list of all layout. should be given as a string as stated in the igraph doc.
        node_metric : specifies which metric to use in order to color and size the vertices of the graph.
            allowed values: ["strength", "betweenness", "closeness", "eigenvector centrality", "page rank", "hub score", "authority score"]

    Returns
    -------
    None.

    """
    random.seed(1) #making sure layout of plots stays the same when changing metrics

    layers_layout = read_graph(path_to_file, percentage_threshold = 0, mnn = None, return_ig=True, affinity = affinity,
                               rm_fb_loops = rm_fb_loops, mutual = mutual,  rm_index = rm_index) #here to make sure layout stays consistent upon graph cut
    layers = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, return_ig=True, affinity = affinity,
                        rm_fb_loops = rm_fb_loops, mutual = mutual, rm_index = rm_index) 
    layers_data = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, return_ig=False,
                             affinity = affinity, rm_fb_loops = rm_fb_loops, mutual = mutual, rm_index = rm_index)

    default_node_size = kwargs["node_size"] if "node_size" in kwargs else 15
    default_edge_width = kwargs["edge_width"] if "edge_width" in kwargs else 5
    node_color = "red"
    node_size = []
    for g in layers:
        size = np.array([default_node_size for v in range(g.vcount())])
        node_size.append(size)
        
    if "node_metric" in kwargs:
        if kwargs["node_metric"] == "none":
            node_size = []
            for g in layers:
                size = np.array([default_node_size for v in range(g.vcount())])
                node_size.append(size)
                
        elif kwargs["node_metric"] == "betweenness":
            node_size = []
            for g in layers:
                edge_betweenness = g.betweenness(weights = [1/(e['weight']) for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
                edge_betweenness = ig.rescale(edge_betweenness)
                node_size.append(np.array(edge_betweenness)*default_node_size+0.07)
        elif kwargs["node_metric"] == "strength":
            node_size = []
            for g in layers:
                edge_strength = g.strength(weights = [e['weight'] for e in g.es()])
                edge_strength = ig.rescale(edge_strength)
                node_size.append(np.array(edge_strength)*default_node_size+0.07)
        elif kwargs["node_metric"] == "closeness":
            node_size = []
            for g in layers:
                edge_closeness = g.closeness(weights = [1/(e['weight']) for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
                edge_closeness = ig.rescale(edge_closeness)
                node_size.append(np.array(edge_closeness)*default_node_size+0.07)
        elif kwargs["node_metric"] == "hub score":
            node_size = []
            for g in layers:
                edge_hub = g.hub_score(weights = [e['weight'] for e in g.es()])
                edge_hub = ig.rescale(edge_hub)
                node_size.append(np.array(edge_hub)*default_node_size+0.07)
        elif kwargs["node_metric"] == "authority score":
            node_size = []
            for g in layers:
                edge_authority = g.authority_score(weights = [e['weight'] for e in g.es()])
                edge_authority = ig.rescale(edge_authority)
                node_size.append(np.array(edge_authority)*default_node_size+0.07)
        elif kwargs["node_metric"] == "eigenvector centrality":
            node_size = []
            for g in layers:
                edge_evc = g.eigenvector_centrality(weights = [e['weight'] for e in g.es()])
                edge_evc = ig.rescale(edge_evc)
                node_size.append(np.array(edge_evc)*default_node_size+0.07)
        elif kwargs["node_metric"] == "page rank":
            node_size = []
            for g in layers:
                edge_pagerank = g.personalized_pagerank(weights = [e['weight'] for e in g.es()])
                edge_pagerank = ig.rescale(edge_pagerank)
                node_size.append(np.array(edge_pagerank)*default_node_size+0.07)
        elif kwargs["node_metric"] == "rich-club":
            node_size = []
            for g in layers:
                k_degree = kwargs["deg"]
                size = rich_club_weights(g, k_degree, 0.01)
                node_size.append(np.array([n*default_node_size for n in size]))
        elif kwargs["node_metric"] == "k-core":
            node_size = []
            for d in layers_data:
                k_degree = kwargs["deg"]
                size = k_core_weights(d, k_degree, 0.01)
                node_size.append(np.array([n*default_node_size for n in size]))
        
    if "idx" in kwargs:
        if len(kwargs["idx"]) == 0:
            marker_frame_color = None
        else:
            color_num = len(np.unique(kwargs["idx"]))
            cmap = get_cmap('Spectral')
            palette = ClusterColoringPalette(color_num)
            marker_frame_color = [palette[i] for i in kwargs["idx"]]#cmap(kwargs["idx"])
    else:
        marker_frame_color = None

    if "layout" in kwargs: 
        if kwargs["layout"] == "circle": 
            layout=nx.circular_layout
        elif kwargs["layout"] == "large" or kwargs["layout"] == "fr":
            layout=nx.spring_layout
        elif kwargs["layout"] == "kk": 
            layout=nx.kamada_kawai_layout
        elif kwargs["layout"] ==  "random": 
            layout=nx.random_layout
        elif kwargs["layout"] ==  "drl": 
            layout=nx.spectral_layout
        elif kwargs["layout"] == "tree":
            layout = nx.planar_layout
        else:
            layout=nx.spring_layout
    else:
        layout=nx.spring_layout
        
    if "node_labels" in kwargs:
        node_labels = kwargs["node_labels"]
    else:
        node_labels = None
        
    if "layer_labels" in kwargs:
        layer_labels = kwargs["layer_labels"]
    else:
        layer_labels = None
    
    scale_edge_width = kwargs["scale_edge_width"] if "scale_edge_width" in kwargs and type(kwargs["scale_edge_width"]) == bool else True   
    LayeredNetworkGraph(layers_layout, layers, layers_data, ax=ax, layout=layout, 
                        node_labels = node_labels, nodes_width=node_size, node_edge_colors=marker_frame_color, 
                        layer_labels=layer_labels, default_edge_width=default_edge_width,
                        scale_edge_width = scale_edge_width, between_layer_edges = kwargs["between_layer_edges"],
                        show_planes = kwargs["show_planes"], edge_cmap = kwargs["edge_cmap"], node_cmap = kwargs["node_cmap"])
    ax.set_axis_off()

    
def display_stats(path_to_file, ax, percentage_threshold = 0.0, mnn = None, affinity = True, avg_graph = False,
                  mutual = True, node_metric = "none", stacked = True, rm_index = True, bins = 10, **kwargs):
    """
    This function displays a histogram representation of the metrics of the graph to analyze.

    Parameters
    ----------
    path_to_file : string
        path specifying where the file containing the matrix representing the graph 
        is stored. Should be a .csv file.
    ax : matplotlib.axis
        the axis to plot the graph onto.
    mnn: whether or not to do a graph cut based on mutual nearest neighbors. If an 'int' is provided,
        this represents the number of nn to take into account.
    affinity: bool. Whether or not the graph type is affinity or distance.
    **kwargs : strings
        node_metric : specifies which metric to use in order to color and size the vertices of the graph.
            allowed values: ["strength", "betweenness", "closeness", "eigenvector centrality", "page rank", "hub score", "authority score"]

    Returns
    -------
    None.

    """    
            
    if len(path_to_file) != 1 and not avg_graph:
        display_stats_multilayer(path_to_file, ax, percentage_threshold, mnn, affinity, mutual,
                                 node_metric = node_metric, deg = kwargs["deg"],
                                 stacked = stacked, show_legend = kwargs["show_legend"],
                                 rm_index = rm_index, bins = bins)
        return
    else:
        data = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, affinity = affinity, 
                          avg_graph = avg_graph, mutual = mutual, rm_index = rm_index)[0]

    if isSymmetric(data):
        g = ig.Graph.Weighted_Adjacency(data, mode='undirected')
    else:
        g = ig.Graph.Weighted_Adjacency(data, mode='directed')
        
    if node_metric == "none":
        edge_strength = [e['weight'] for e in g.es()]
        ax.hist(edge_strength)

    elif node_metric == "betweenness":
        edge_betweenness = g.betweenness(weights = [1/(e['weight']**2) for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
        edge_betweenness = ig.rescale(edge_betweenness)
        ax.hist(edge_betweenness)
    elif node_metric == "strength":
        edge_strength = g.strength(weights = [e['weight'] for e in g.es()])
        edge_strength = ig.rescale(edge_strength)
        ax.hist(edge_strength)
    elif node_metric == "closeness":
        edge_closeness = g.closeness(weights = [1/(e['weight']**2) for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
        edge_closeness = ig.rescale(edge_closeness)
        ax.hist(edge_closeness)
    elif node_metric == "hub score":
        edge_hub = g.hub_score(weights = [e['weight'] for e in g.es()])
        edge_hub = ig.rescale(edge_hub)
        ax.hist(edge_hub)
    elif node_metric == "authority score":
        edge_authority = g.authority_score(weights = [e['weight'] for e in g.es()])
        edge_authority = ig.rescale(edge_authority)
        ax.hist(edge_authority)
    elif node_metric == "eigenvector centrality":
        edge_evc = g.eigenvector_centrality(weights = [e['weight'] for e in g.es()])
        edge_evc = ig.rescale(edge_evc)
        ax.hist(edge_evc)
    elif node_metric == "page rank":
        edge_pagerank = g.personalized_pagerank(weights = [e['weight'] for e in g.es()])
        edge_pagerank = ig.rescale(edge_pagerank)
        ax.hist(edge_pagerank)
    elif node_metric == "rich-club":
        k_degree = kwargs["deg"]
        for i in range(len(path_to_file)):
            g = read_graph(path_to_file[i], percentage_threshold, mnn, return_ig=True)[0]
            core_size = rich_club_size(g, k_degree)
            p_value = rich_club_p_value(path_to_file[i], k_degree, percentage_threshold, mnn)
            ax.text(0.1, 0.1+0.1*i, os.path.basename(path_to_file[i])+": rich-club size = "+str(core_size)+" p_value = "+str(p_value),\
                    transform=ax.transAxes, fontsize=15)
        ax.axis("off")
    else: 
        edge_strength = [e['weight'] for e in g.es()]
        ax.hist(edge_strength)
        ax.set_xlabel("Edge values")
        ax.set_title("No 'node metric' was selected, showing edge values.")
        return
        
    ax.set_ylabel("Count")
    if node_metric != "none":
        ax.set_xlabel(node_metric +" values")
    else:
        ax.set_xlabel("Edge values")
        ax.set_title("No 'node metric' was selected, showing edge values.")


            
def display_stats_multilayer(path_to_file, ax, percentage_threshold = 0.0, mnn = None, affinity = True, mutual = True,
                             node_metric = "none",stacked = True, rm_index = True, bins = 10, **kwargs):
    """
    This function displays a histogram representation of the metrics of the graphs to analyze.

    Parameters
    ----------
    path_to_file : string
        path specifying where the file containing the matrix representing the graph 
        is stored. Should be a .csv file.
    ax : matplotlib.axis
        the axis to plot the graph onto.
    mnn: whether or not to do a graph cut based on mutual nearest neighbors. If an 'int' is provided,
        this represents the number of nn to take into account.
    affinity: bool. Whether or not the graph type is affinity or distance.
    **kwargs : strings
        node_metric : specifies which metric to use in order to color and size the vertices of the graph.
            allowed values: ["strength", "betweenness", "closeness", "eigenvector centrality", "page rank", "hub score", "authority score"]

    Returns
    -------
    None.
    """    

    data = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, affinity = affinity,
                      mutual = mutual, rm_index = rm_index)
    graph_data = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn,
                            affinity = affinity, mutual = mutual, return_ig = True, rm_index = rm_index)
    cm = matplotlib.colormaps.get_cmap("coolwarm")

    if node_metric == "none":
        node_size = []
        for g in graph_data:
            edge_strength = [e['weight'] for e in g.es()]
            node_size.append(np.array(edge_strength))
            
    elif node_metric == "betweenness":
        node_size = []
        for g in graph_data:
            edge_betweenness = g.betweenness(weights = [1/(e['weight']) for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
            node_size.append(np.array(edge_betweenness))
            
    elif node_metric == "strength":
        node_size = []
        for g in graph_data:
            edge_strength = g.strength(weights = [e['weight'] for e in g.es()])
            node_size.append(np.array(edge_strength))
            
    elif node_metric == "closeness":
        node_size = []
        for g in graph_data:
            edge_closeness = g.closeness(weights = [1/(e['weight']) for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
            node_size.append(np.array(edge_closeness))
    elif node_metric == "hub score":
        node_size = []
        for g in graph_data:
            edge_hub = g.hub_score(weights = [e['weight'] for e in g.es()])
            node_size.append(np.array(edge_hub))
    elif node_metric == "authority score":
        node_size = []
        for g in graph_data:
            edge_authority = g.authority_score(weights = [e['weight'] for e in g.es()])
            node_size.append(np.array(edge_authority))
    elif node_metric == "eigenvector centrality":
        node_size = []
        for g in graph_data:
            edge_evc = g.eigenvector_centrality(weights = [e['weight'] for e in g.es()])
            node_size.append(np.array(edge_evc))
    elif node_metric == "page rank":
        node_size = []
        for g in graph_data:
            edge_pagerank = g.personalized_pagerank(weights = [e['weight'] for e in g.es()])
            node_size.append(np.array(edge_pagerank))

    elif node_metric == "rich-club":
        node_size = []
        k_degree = kwargs["deg"]
        for g in graph_data:
            core_size = rich_club_size(g, k_degree)
            node_size.append([core_size])
            
    elif node_metric == "k-core":
        node_size = []
        k_degree = kwargs["deg"]
        for g in graph_data:
            core_size = k_core_size(g, k_degree)
            node_size.append([core_size])
    else: 
        node_size = []
        for idx, g in enumerate(graph_data):
            edge_strength = [e['weight'] for e in g.es()]
            node_size.append(np.array(edge_strength))
        total_data = []
        for idx in range(len(graph_data)):
            total_data.extend(node_size[idx])
            
        _, bins_pos = np.histogram(total_data, bins = bins)
        colors = [cm(idx/len(graph_data)) for idx in range(len(graph_data))]
        ax.hist(node_size, histtype='bar', stacked=stacked, rwidth = 0.8, color = colors)
        ax.set_ylabel("Count")
        labels_legend = [os.path.basename(path).split(".")[0] for path in path_to_file]
        ax.legend(labels=labels_legend)
        ax.set_xlabel("Edge values")
        ax.set_title("No 'node metric' was selected, showing edge values.")
        return
    
    total_data = []
    for idx in range(len(graph_data)):
        total_data.extend(node_size[idx])
        
    _, bins_pos = np.histogram(total_data, bins = bins)
    
    colors = [cm(idx/len(graph_data)) for idx in range(len(graph_data))]
    ax.hist(node_size, histtype='bar', bins = bins_pos, stacked=stacked, rwidth = 0.8, color = colors)
    ax.set_ylabel("Count")
    labels_legend = [os.path.basename(path).split(".")[0] for path in path_to_file]
    ax.legend(labels=labels_legend)
    if node_metric != "none":
        ax.set_xlabel(node_metric+" values")
    else:
        ax.set_xlabel("Edge values")
        ax.set_title("No 'node metric' was selected, showing edge values.")
    if "show_legend" in kwargs and kwargs["show_legend"] is False:
        ax.get_legend().remove()
        
def display_animation(path_to_file, parent_frame = None, percentage_threshold = 0.0, mnn = None,
                      affinity = True, rm_fb_loops = True, mutual = True, rm_index = True, **kwargs):
    
    layers_layout = read_graph(path_to_file, percentage_threshold = 0, mnn = None, return_ig=True, affinity = affinity,
                               rm_fb_loops = rm_fb_loops, mutual = mutual, rm_index = rm_index) #here to make sure layout stays consistent upon graph cut
    layers = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, return_ig=True, affinity = affinity,
                        rm_fb_loops = rm_fb_loops, mutual = mutual, rm_index = rm_index) 
    layers_data = read_graph(path_to_file, percentage_threshold = percentage_threshold, mnn = mnn, return_ig=False, affinity = affinity,
                             rm_fb_loops = rm_fb_loops, rm_index = rm_index )
    
    if rm_index == False and ("node_labels" in kwargs and kwargs["node_labels"]):
        node_labels = [str(i) for i in range(len(read_labels(path_to_file)))] 
    elif ("node_labels" in kwargs and kwargs["node_labels"]):
        node_labels = read_labels(path_to_file) 
    else:
        node_labels = None
        
    default_node_size = kwargs["node_size"] if "node_size" in kwargs else 15
    default_edge_width = kwargs["edge_width"] if "edge_width" in kwargs else 5
    node_color = "blue"
    node_size = []
    for g in layers:
        size = np.array([default_node_size for v in range(g.vcount())])
        node_size.append(size)
        
    if "node_metric" in kwargs:
        if kwargs["node_metric"] == "none":
            node_size = []
            for g in layers:
                size = np.array([default_node_size for v in range(g.vcount())])
                node_size.append(size)
                
        elif kwargs["node_metric"] == "betweenness":
            node_size = []
            for g in layers:
                edge_betweenness = g.betweenness(weights = [1/(e['weight']) for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
                edge_betweenness = ig.rescale(edge_betweenness)
                node_size.append(np.array(edge_betweenness)*default_node_size+0.07)
        elif kwargs["node_metric"] == "strength":
            node_size = []
            for g in layers:
                edge_strength = g.strength(weights = [e['weight'] for e in g.es()])
                edge_strength = ig.rescale(edge_strength)
                node_size.append(np.array(edge_strength)*default_node_size+0.07)
        elif kwargs["node_metric"] == "closeness":
            node_size = []
            for g in layers:
                edge_closeness = g.closeness(weights = [1/(e['weight']) for e in g.es()]) #taking the inverse of edge values as we want high score to represent low distances
                edge_closeness = ig.rescale(edge_closeness)
                node_size.append(np.array(edge_closeness)*default_node_size+0.07)
        elif kwargs["node_metric"] == "hub score":
            node_size = []
            for g in layers:
                edge_hub = g.hub_score(weights = [e['weight'] for e in g.es()])
                edge_hub = ig.rescale(edge_hub)
                node_size.append(np.array(edge_hub)*default_node_size+0.07)
        elif kwargs["node_metric"] == "authority score":
            node_size = []
            for g in layers:
                edge_authority = g.authority_score(weights = [e['weight'] for e in g.es()])
                edge_authority = ig.rescale(edge_authority)
                node_size.append(np.array(edge_authority)*default_node_size+0.07)
        elif kwargs["node_metric"] == "eigenvector centrality":
            node_size = []
            for g in layers:
                edge_evc = g.eigenvector_centrality(weights = [e['weight'] for e in g.es()])
                edge_evc = ig.rescale(edge_evc)
                node_size.append(np.array(edge_evc)*default_node_size+0.07)
        elif kwargs["node_metric"] == "page rank":
            node_size = []
            for g in layers:
                edge_pagerank = g.personalized_pagerank(weights = [e['weight'] for e in g.es()])
                edge_pagerank = ig.rescale(edge_pagerank)
                node_size.append(np.array(edge_pagerank)*default_node_size+0.07)
        elif kwargs["node_metric"] == "rich-club":
            node_size = []
            for g in layers:
                k_degree = kwargs["deg"]
                size = rich_club_weights(g, k_degree, 0.01)
                node_size.append(np.array([n*default_node_size for n in size]))
        elif kwargs["node_metric"] == "k-core":
            node_size = []
            for d in layers_data:
                k_degree = kwargs["deg"]
                size = k_core_weights(d, k_degree, 0.01)
                node_size.append(np.array([n*default_node_size for n in size]))
        
    if "idx" in kwargs:
        if len(kwargs["idx"]) == 0:
            marker_frame_color = None
        else:
            color_num = len(np.unique(kwargs["idx"]))
            cmap = get_cmap('Spectral')
            palette = ClusterColoringPalette(color_num)
            marker_frame_color = [palette[i] for i in kwargs["idx"]]#cmap(kwargs["idx"])
    else:
        marker_frame_color = None
    
    if "layout" in kwargs:
        layout_style = kwargs["layout"]
    else:
        layout_style = "fr"
            
    if "layer_labels" in kwargs:
        layer_labels = kwargs["layer_labels"]
    else:
        layer_labels = None
        
    if "edge_cmap" in kwargs:
        edge_cmap = kwargs["edge_cmap"]
    else:
        edge_cmap = get_cmap('Greys')
        
    if "node_cmap" in kwargs and kwargs["node_cmap"] != "none":
        node_cmap = kwargs["node_cmap"]
    else:
        node_cmap = mcolors.ListedColormap(['black'])
    
    styles = []
    for i in range(len(layers)):
        visual_style = {}
        visual_style["vertex_size"] = node_size[i]
        sizes_for_cm = rescale(node_size[i], 0.999) if len(np.unique(node_size[i])) > 1 else [0.99]*len(node_size[i])
        node_color = [node_cmap(node) for node in sizes_for_cm]
        visual_style["vertex_color"] = node_color
        visual_style["vertex_frame_color"] = marker_frame_color
        visual_style["edge_arrow_width"] = rescale(np.array([w['weight'] for w in layers[i].es]), default_edge_width)*(default_edge_width)
        visual_style["vertex_label"] = node_labels
        visual_style["vertex_label_dist"] = 1 
        
        if "scale_edge_width" in kwargs and kwargs["scale_edge_width"]:
            g_edge_width = rescale(np.array([e['weight'] for e in layers[i].es()]), default_edge_width)
            visual_style["edge_width"] = g_edge_width
        edge_color = [edge_cmap(edge) for edge in rescale(np.array([w['weight'] for w in layers[i].es]), 1) - 0.01]
        visual_style["edge_color"] = edge_color
        
        if isSymmetric(layers_data[i]):
            visual_style["edge_curved"] = 0.0
            visual_style["edge_arrow_width"] = rescale(np.array([w['weight'] for w in layers[i].es]), default_edge_width)*0
        else:
            visual_style["edge_curved"] = 0.2

        styles.append(visual_style)
    
    if "interframe" in kwargs:
        interframe = kwargs["interframe"]
    else:
        interframe = 200
        
    layout = layers[0].layout(layout_style)
    animation = GraphAnimator(layers, layout, styles, parent_frame, interframe)
    f, ax = animation.get_fig()
    return f, ax

if __name__ == '__main__':

    # path = "..\\..\\data\\nosemaze\\both_cohorts_1days\\G1\\"
    # file1 = "interactions_resD1_01.csv"
    # file2 = "interactions_resD1_02.csv"
    # file3 = "interactions_resD1_03.csv"
    # file4 = "interactions_resD1_04.csv"
    
    path = "..\\..\\data\\random_graph\\"
    file1 = "rand_graph1.csv"
    file2 = "rand_graph2.csv"
    file3 = "rand_graph3.csv"
    file4 = "rand_graph4.csv"
    file5 = "rand_graph5.csv"

    # data = read_graph([path+file1], mnn = 3, return_ig=False)[0]
    # if isSymmetric(data):
    #     g = ig.Graph.Weighted_Adjacency(data, mode='undirected')
    # else:
    #     g = ig.Graph.Weighted_Adjacency(data, mode='directed')
    
    #  = community_clustering([path+file1, path+file2, path+file3, path+file4], algorithm = "infomap", mnn = 4, mutual = True, affinity = True)
    # print(c)
    
    
## 1D plot example     
    # f = plt.Figure()
    # fig, ax = plt.subplots(1, 1)
    # display_graph([path+file1], ax, mnn = None, deg = 0, percentage_threshold = 50,
    #               node_metric = "none", mutual = True, idx = [], node_size = 5, edge_width = 2,
    #               scale_edge_width = True, between_layer_edges = False,  cluster_num = None, rm_index = True,
    #               node_labels = False, show_planes = True, edge_cmap = cm.Greys, node_cmap = cm.Greens)
    # plt.show()

## stacked plot example     
    # f = plt.Figure()
    # fig, ax = plt.subplots(1, 1)
    # ax = fig.add_subplot(111, projection='3d')
    # display_graph([path+file1, path+file2], ax, mnn = None, deg = 0, percentage_threshold = 50,
    #               node_metric = "none", mutual = True, idx = [], node_size = 5, edge_width = 2,
    #               scale_edge_width = True, between_layer_edges = False,  cluster_num = None, rm_index = True,
    #               node_labels = False, show_planes = True, edge_cmap = cm.Greys, node_cmap = cm.Greens)
    # plt.show()

# histogram plot example     
    f = plt.Figure()
    fig, ax = plt.subplots(1, 1)
    display_stats([path+file1, path+file2, path+file3, path+file4], ax, mnn = 5, deg = 3, percentage_threshold = 0,
                  node_metric = "k-core", mutual = True, idx = [], node_size = 5, edge_width = 2, bins = 10,
                  scale_edge_width = True, between_layer_edges = False,  cluster_num = None, rm_index = True, show_planes = True, show_legend = False)
    plt.show()
    
## animation example  
    # fig, ax = plt.subplots(1, 1)
    # root = tk.Tk()
    # root.resizable(width=True, height=True)
    # root.title("Multilayer graph analysis")
    # display_animation([path+file1, path+file2, path+file3, path+file4], root,  mnn = 5, deg = 0, 
    #                   percentage_threshold = 50, layout = "circle",
    #               node_metric = "strength", mutual = True, idx = [], node_size = 50, edge_width = 2,
    #               scale_edge_width = True, between_layer_edges = False,  cluster_num = None, node_labels = True, rm_index = False,
    #               node_cmap = cm.coolwarm, edge_cmap = cm.coolwarm)
    # root.mainloop()

    
    # plt.show()
    # c = display_stats([path+file1, path+file2, path+file3], ax = ax, mnn = 4, node_metric = "rich-club", deg = 2)
    # g = read_graph(path+file, return_ig=True)
    # display_graph([path+"\\interactions_resD7_1.csv", path+"\\interactions_resD7_1.csv"], a, node_metric = "closeness", deg =3, cluster_num = 2, idx = [1, 1, 1, 0,0,1,1,1,1,1])
    
# clusterer = graphClusterer(D, True, "fully connected")
# cluster_num = 2
# clusterer.k_elbow_curve(a)
# nn = 4
# _, idx, _, _ = clusterer.clustering(cluster_num, isAffinity = True)
# clusterer.sigma_grid_search(a, 30, 2)
