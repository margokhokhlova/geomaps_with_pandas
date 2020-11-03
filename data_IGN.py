"""The base file for loading default datasets."""
import os
import math
import shutil
import zipfile
import ssl

try:
    # Python 2
    from urllib2 import HTTPError
    from urllib2 import urlopen
except ImportError:
    # Python 3+
    from urllib.error import HTTPError
    from urllib.request import urlopen

import numpy as np
import collections
from shutil import copyfileobj

from collections import Counter

from sklearn.utils import Bunch

from grakel.graph import Graph

global symmetric_dataset

symmetric_dataset = False


def read_data(
        name,
        with_classes=True,
        prefer_attr_nodes=False,
        prefer_attr_edges=False,
        produce_labels_nodes=False,
        as_graphs=False,
        is_symmetric=symmetric_dataset, path = None):
    """Create a dataset iterable for GraphKernel.

    Parameters
    ----------
    name : str
        The dataset name.

    with_classes : bool, default=False
        Return an iterable of class labels based on the enumeration.

    produce_labels_nodes : bool, default=False
        Produce labels for nodes if not found.
        Currently this means labeling its node by its degree inside the Graph.
        This operation is applied only if node labels are non existent.

    prefer_attr_nodes : bool, default=False
        If a dataset has both *node* labels and *node* attributes
        set as labels for the graph object for *nodes* the attributes.

    prefer_attr_edges : bool, default=False
        If a dataset has both *edge* labels and *edge* attributes
        set as labels for the graph object for *edge* the attributes.

    as_graphs : bool, default=False
        Return data as a list of Graph Objects.

    is_symmetric : bool, default=False
        Defines if the graph data describe a symmetric graph.

    Returns
    -------
    Gs : iterable
        An iterable of graphs consisting of a dictionary, node
        labels and edge labels for each graph.

    classes : np.array, case_of_appearance=with_classes==True
        An one dimensional array of graph classes aligned with the lines
        of the `Gs` iterable. Useful for classification.

    """
    indicator_path = path+str(name)+"_graph_indicator.txt"
    edges_path =  path + "/" + str(name) + "_A.txt"
    node_labels_path = path + "/" + str(name) + "_node_labels.txt"
    node_attributes_path = path +"/"+str(name)+"_node_attributes.txt"
    edge_labels_path = path + "/" + str(name) + "_edge_labels.txt"
    edge_attributes_path = \
        path + "/" + str(name) + "_edge_attributes.txt"
    graph_classes_path = \
        path + "/" + str(name) + "_graph_labels.txt"

    # node graph correspondence
    ngc = dict()
    # edge line correspondence
    elc = dict()
    # dictionary that keeps sets of edges
    Graphs = dict()
    # dictionary of labels for nodes
    node_labels = dict()
    # dictionary of labels for edges
    edge_labels = dict()

    # Associate graphs nodes with indexes
    with open(indicator_path, "r") as f:
        for (i, line) in enumerate(f, 1):
            ngc[i] = int(line[:-1])
            if int(line[:-1]) not in Graphs:
                Graphs[int(line[:-1])] = set()
            if int(line[:-1]) not in node_labels:
                node_labels[int(line[:-1])] = dict()
            if int(line[:-1]) not in edge_labels:
                edge_labels[int(line[:-1])] = dict()

    # Create backwards configuration
    graph_node_correspondence = collections.defaultdict(list)
    for node in range(len(ngc)):
        graph_node_correspondence[ngc[node+1]].append(node+1)


    # Extract graph edges
    with open(edges_path, "r") as f:
        for (i, line) in enumerate(f, 1):
            edge = line[:-1].replace(' ', '').split(",")
            elc[i] = (int(edge[0]), int(edge[1]))
            Graphs[ngc[int(edge[0])]].add((int(edge[0]), int(edge[1])))
            if is_symmetric:
                Graphs[ngc[int(edge[1])]].add((int(edge[1]), int(edge[0])))

    # Extract node attributes
    if prefer_attr_nodes:
        with open(node_attributes_path, "r") as f:
            for (i, line) in enumerate(f, 1):
                node_labels[ngc[i]][i] = \
                    [float(num) for num in
                     line[:-1].replace(' ', '').split(",")]
                #if np.isnan(node_labels[ngc[i]][i]).any():  # then there are None values
                node_labels[ngc[i]][i] = [0.00 if math.isnan(x) else x  for x in node_labels[ngc[i]][i]][:]  # remove NaNs and take only 3 first

                #node_labels[ngc[i]][i] = [x for x in node_labels[ngc[i]][i][1:2]]  # remove NaNs
    # Extract node labels
    elif not produce_labels_nodes:
        with open(node_labels_path, "r") as f:
            for (i, line) in enumerate(f, 1):
                node_labels[ngc[i]][i] = int(line[:-1])
    elif produce_labels_nodes:
        for i in range(1, len(Graphs)+1):
            node_labels[i] = dict(Counter(s for (s, d) in Graphs[i] if s != d))
            if not bool(node_labels[i]): #if labels are empty
                node_labels[i] = {s:0 for s in graph_node_correspondence[i]}

    # Extract edge attributes
    if prefer_attr_edges:
        with open(edge_attributes_path, "r") as f:
            for (i, line) in enumerate(f, 1):
                attrs = [float(num)
                         for num in line[:-1].replace(' ', '').split(",")]
                edge_labels[ngc[elc[i][0]]][elc[i]] = attrs
                if is_symmetric:
                    edge_labels[ngc[elc[i][1]]][(elc[i][1], elc[i][0])] = attrs

    # Extract edge labels
    elif not prefer_attr_edges and  os.path.exists(edge_labels_path):
        with open(edge_labels_path, "r") as f:
            for (i, line) in enumerate(f, 1):
                edge_labels[ngc[elc[i][0]]][elc[i]] = float(line[:-1])
                if is_symmetric:
                    edge_labels[ngc[elc[i][1]]][(elc[i][1], elc[i][0])] = \
                        float(line[:-1])
    elif not prefer_attr_edges and  not os.path.exists(edge_labels_path):
        with open(edges_path, "r") as f:
            for (i, line) in enumerate(f, 1):
                edge_labels[ngc[elc[i][0]]][elc[i]] = 1
                if is_symmetric:
                    edge_labels[ngc[elc[i][1]]][(elc[i][1], elc[i][0])] = 1

    Gs = list()
    if as_graphs:
        for i in range(1, len(Graphs)+1):
            Gs.append(Graph(Graphs[i], node_labels[i], edge_labels[i]))
    else:
        for i in range(1, len(Graphs)+1):
            Gs.append([Graphs[i], node_labels[i], edge_labels[i]])

    if with_classes:
        classes = []
        with open(graph_classes_path, "r") as f:
            for line in f:
                classes.append(int(line[:-1]))

        classes = np.array(classes, dtype=np.int)
        return Bunch(data=Gs, target=classes)
    else:
        return Bunch(data=Gs)

