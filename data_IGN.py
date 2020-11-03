import pandas as pd
import geopandas as gpd

from sklearn.utils import Bunch

import networkx as nx
global symmetric_dataset
symmetric_dataset =1
from earthpy import clip as cl


def read_data(
        name,
        with_classes=True,
        prefer_attr_nodes=False,
        prefer_attr_edges=False,
        produce_labels_nodes=False,
        as_graphs=False,
        is_symmetric=symmetric_dataset, path = None, with_node_posistions=False):
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
    node_positions_path = \
        path + "/" + str(name) + "_node_positions.txt"
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
    #dictionary for positions
    node_positions = dict()

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
                node_labels[ngc[i]][i] = [0.00 if math.isnan(x) else x for x in node_labels[ngc[i]][i]][:]  # remove NaNs and take only 2 last

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
            nx_graph = nx.Graph()
            #nx_graph.add_nodes_from(Graphs[i])
            nx_graph.add_edges_from(edge_labels[i])
            nx.set_node_attributes(nx_graph, node_labels[i], 'labels')
            Gs.append(nx_graph)
    else:
        for i in range(1, len(Graphs)+1):
            Gs.append([Graphs[i], node_labels[i], edge_labels[i]])

    if with_node_posistions:
        with open(node_positions_path, "r") as f:
            for (i, line) in enumerate(f, 1):
                positions = [float(num) for num in
                     line.replace(' ', '').split(",")]
                if ngc[i] not in node_positions:
                    node_positions[ngc[i]]= {i:positions}
                else:
                    node_positions[ngc[i]].update({i:positions})#
        classes = []
        with open(graph_classes_path, "r") as f:
            for line in f:
                classes.append(int(line[:-1]) - 1)

        classes = np.array(classes, dtype=np.int)
        return Bunch(data=Gs, target=classes, positions = node_positions)

    if with_classes:
        classes = []
        with open(graph_classes_path, "r") as f:
            for line in f:
                classes.append(int(line[:-1])-1)

        classes = np.array(classes, dtype=np.int)
        return Bunch(data=Gs, target=classes)
    else:
        return Bunch(data=Gs)



def visualize_matches(index, knn_matches, gt19, dataset04, dataset19):
    ''' a quick function to visualize the graphs
    index - the index of the mathcing query int
    knn_matches  - returned most similar graphs (labels) [[]]
    gt19 - GT correspondences []
    datasets - datasets with nx graphs to display the result - custom class'''
    query_result = knn_matches[index]
    query_gt = gt19[index]
    # find the graphs which correspond to queris and GT and display them
    query_graph_index = np.where(dataset19.target==query_gt)[0][0] #take only one graph as a demo
    query_graph_position = dataset19.positions[query_graph_index+1]
    graph_query = dataset19.data[query_graph_index]
    fig, axs = plt.subplots(1, 6,figsize=(20, 8))
    nx.draw(graph_query, pos = query_graph_position, with_labels=False,node_color=[color_map[graph_query._node[node]['labels']] for node in  graph_query] , ax=axs[0])
    axs[0].set_title(f"Query graph, gt {query_gt}")
    for i in range(1,len(query_result)+1):
        graph = dataset04.data[np.where(dataset04.target==query_result[i-1])[0][0]]
        returned_graph_position = dataset04.positions[1+np.where(dataset04.target==query_result[i-1])[0][0]]
        #color_map = get_color_map(graph)
        print(len(graph.nodes), len(returned_graph_position))
        nx.draw(graph, pos=returned_graph_position, with_labels=False, node_color=[color_map[graph._node[node]['labels']] for node in  graph], ax=axs[i])
        axs[i].set_title(f"gt {query_result[i-1]}")
    fig.suptitle('Returned KNN-matches')
    plt.show()

color_map = {
        0: 'green',
        1: 'red',
        2: 'brown',
        3: 'violet',
        4: 'yellow',
        5: 'pink',
        6: 'gray',
        7: 'cyan',
        8: 'gold',
        9: 'salmon',
        10: 'magenta',
        11: 'indigo',
        12: 'orange',
        13: 'blue',
        14: 'lilac'
    }

def visualize_matches_with_the_map(index, knn_matches, gt19, dataset04, dataset19):
    ''' a quick function to visualize the graphs
    index - the index of the mathcing query int
    knn_matches  - returned most similar graphs (labels) [[]]
    gt19 - GT correspondences []
    datasets - datasets with nx graphs to display the result - custom class'''
    query_result = knn_matches[index]
    query_gt = gt19[index]
    # find the graphs which correspond to queris and GT and display them
    query_graph_index = np.where(dataset19.target==query_gt)[0][0] #take only one graph as a demo
    query_graph_position = dataset19.positions[query_graph_index+1]
    polygon = minimum_rotated_rectangle_on_graph(query_graph_position)
    graph_query = dataset19.data[query_graph_index]
    BD_topo = return_df(polygon, False)
    fig, axs = plt.subplots(1, 6,figsize=(20, 5))
    plot_data(graph_query, query_graph_position, BD_topo, axs[0],  f"Query graph, gt {query_gt}")
    for i in range(1,len(query_result)+1):
        graph = dataset04.data[np.where(dataset04.target==query_result[i-1])[0][0]]
        returned_graph_position = dataset04.positions[1+np.where(dataset04.target==query_result[i-1])[0][0]]
        polygon = minimum_rotated_rectangle_on_graph(returned_graph_position)
        BD_topo_bd = return_df(polygon, True)
        plot_data(graph, returned_graph_position, BD_topo_bd, axs[i],  f"gt {query_result[i-1]}")
#         nx.draw(graph, pos=returned_graph_position, with_labels=False, node_color=[color_map[graph._node[node]['labels']] for node in  graph], ax=axs[i])
#         axs[i].set_title()
    fig.suptitle('Returned KNN-matches')
    plt.show()

def plot_data(graph, pos, BD_topo, ax, title):
    ' takes the graph, BD topo and axis and plots'
    BD_topo.roads.plot(linewidth=2.0, edgecolor='#FFA500', color='#FFA500', alpha = 0.5, ax=ax)
    BD_topo.houses.plot(color='#FF0000', alpha = 0.5, ax=ax)
    BD_topo.water.plot(linewidth=2.0, color='#0000FF', ax=ax)
    BD_topo.railroads.plot(linewidth=2.0, color='#FF00FF', ax=ax)
    BD_topo.rem_houses.plot(color='#FFFF00', ax=ax)
    nx.draw(graph, pos = pos, with_labels=False,node_color=[color_map[graph._node[node]['labels']] for node in  graph] , ax=ax)
    ax.set_title(title)

def minimum_rotated_rectangle_on_graph(graph_positions):
    ''' this function takes a dictionary with node coordinates as the attributes and
    returnes the shapely polygon around it'''
    point = shgm.MultiPoint(list(graph_positions.values()))
    minimal_polygon = point.minimum_rotated_rectangle
    return minimal_polygon


def display_attribute_unions(index, knn_matches, gt19, dataset04, dataset19):
    ''' a quick function to display the common sets of attributes in the matched graphs
    index - the index of the mathcing query int
    knn_matches  - returned most similar graphs (labels) [[]]
    gt19 - GT correspondences []
    datasets - datasets with nx graphs to display the result - custom class'''
    query_result = knn_matches[index]
    query_gt = gt19[index]
    # find the graphs which correspond to queris and GT and display them
    query_graph_index = np.where(dataset19.target==query_gt)[0][0] #take only one graph as a demo
    graph_query = dataset19.data[query_graph_index]
    attributes_query = list(nx.get_node_attributes(graph_query, 'labels').values())
    for i in range(0,len(query_result)):
        graph = dataset04.data[np.where(dataset04.target == query_result[i])[0][0]]
        attributes_match = list(nx.get_node_attributes(graph, 'labels').values())
        intersection = np.intersect1d(np.around(attributes_query, d=1), np.around(attributes_match,1))#multidim_intersect(attributes_query, attributes_match)
        print(f'Attributes similarity index for the {i+1}  returned match {len(intersection)/(len(graph_query.nodes)+len(graph.nodes))}')



def multidim_intersect(arr1, arr2):
    arr1_view = arr1.view([('', arr1.dtype)] * arr1.shape[1])
    arr2_view = arr2.view([('', arr2.dtype)] * arr2.shape[1])
    intersected = np.intersect1d(arr1_view, arr2_view)
    return intersected.view(arr1.dtype).reshape(-1, arr1.shape[1])


def return_df(rectangle, f_year = True):
    ''' will return the geographic objects inside the polygon
    input is a shapely polygon, output is a Bunch of pandas dataframes for each category
    first and second year data are global - they are big and heavy DF'''
    if f_year:
        sg_houses = clip_data(first_year.buildings, rectangle)
        sg_water = clip_data(first_year.rivers, rectangle)
        sg_rem_houses = clip_data(first_year.build_reml, rectangle)
        sg_roads = clip_data(first_year.roads, rectangle)
        sg_railroads = clip_data(first_year.rail, rectangle)
    else:
        sg_houses = clip_data(second_year.buildings, rectangle)
        sg_water = clip_data(second_year.rivers, rectangle)
        sg_rem_houses = clip_data(second_year.build_reml, rectangle)
        sg_roads = clip_data(second_year.roads, rectangle)
        sg_railroads = clip_data(second_year.rail, rectangle)
    return Bunch(houses = sg_houses, water = sg_water, rem_houses = sg_rem_houses, roads = sg_roads, railroads = sg_railroads)

def clip_data(pd_obj, pd_polyg):
    sg =gpd.clip(pd_obj,pd_polyg) #extract segments of roads
    return sg


if __name__ == '__main__':
    # Experiment parameters
    parser = argparse.ArgumentParser(description='contrastive_GCN')

    parser.add_argument('--first_dataset', type=str, default='ign_2004',
                        help='Name of dataset number 1, should correspond to the folder with data')
    parser.add_argument('--test_dataset', type=str, default='ign_2019',
                        help='Name of the matching dataset, should correspond to the folder with data')
    parser.add_argument('--batch-size', type=int, default=50, metavar='N',
                        help='input training batch-size')
    parser.add_argument('--threads', type=int, default=0,
                        help='num of threads')
    parser.add_argument('--n_folds', type=int, default=1,
                        help='n-fold cross validation, default is 2 folds - single check of best val accuracy')
    parser.add_argument('--seed', type=int, default=111,
                        help='seed for reproduction')
    parser.add_argument('--N', type=bool, default=5, help='N in map@N')

    args = parser.parse_args()

    def cross_val_map_local(data04, data19, dims=17):
        features04 = np.empty((0, dims))
        features19 = np.empty((0, dims))
        gt04 = []
        gt19 = []
        dist_graphs_19 = []  #to store the distinct graphs
        for i in range(len(data19.data['features_onehot'])):
            gt19 += [data19.data['targets'][i]] * len(data19.data['features_onehot'][i])
            features19 = np.vstack((features19, data19.data['features_onehot'][i]))
            dist_graphs_19 += [i] * len(data19.data['features_onehot'][i])
        dist_graphs_04 = []  # to store the distinct graphs
        for i in range(len(data04.data['features_onehot'])):
            gt04 += [data04.data['targets'][i]] * len(data04.data['features_onehot'][i])
            features04 = np.vstack((features04, data04.data['features_onehot'][i]))
            dist_graphs_04 += [i] * len(data04.data['features_onehot'][i])
        indexer = BagOfNodesIndex(dimension=features04.shape[1], N_CENTROIDS=128)
        indexer.train(features04, dist_graphs_04)
        unique_graphs = np.unique(dist_graphs_19)
        gt_gt19 = build_gt_voc(dist_graphs_19, gt19)
        gt_gt04 = build_gt_voc(dist_graphs_04, gt04)
        gt_19 = []
        knn_array = []
        for i in unique_graphs:
            query_features = features19[dist_graphs_19 == i]
            answer = indexer.search(query_features)
            sorted(answer, key=lambda x: x[1], reverse=True)  # sort the array
            gt_19.append(gt_gt19[i])
            knn_array.append([gt_gt04[a] for a in answer[0][:args.N]])  # workaround for structure

        map = map_for_dataset(gt_19, knn_array)
        return map, knn_array, gt_19

    def build_gt_voc(dist_graphs, gt):
        ''' return a vocabulary matching gt zone labes with graph labels'''
        gt_g = {}
        for i in range(len(dist_graphs)):
            if dist_graphs[i] not in gt_g:
                gt_g[dist_graphs[i]] = gt[i]
        return gt_g


    args = parser.parse_args()

    IGN04 = read_data('IGN04', #TODO fix this to make automatic
                      with_classes=True,
                      prefer_attr_nodes=True,
                      prefer_attr_edges=False,
                      produce_labels_nodes=False,
                      as_graphs=True,
                      is_symmetric=symmetric_dataset,
                      path='./data/IGN_final/57_67/%s/'% args.first_dataset.upper(), with_node_posistions = True)

    IGN19 = read_data('IGN19',
                      with_classes=True,
                      prefer_attr_nodes=True,
                      prefer_attr_edges=False,
                      produce_labels_nodes=False,
                      as_graphs=True,
                      is_symmetric=symmetric_dataset,
                      path='./data/IGN_final/57_67/%s/' % args.test_dataset.upper(), with_node_posistions = True)

    #
    knn_matches = [[3846, 3949, 4012, 2323, 3891], [1939, 1503, 184, 4611, 5917], [3593, 200, 5956, 1290, 2476], [3983, 3447, 3725, 3569, 5940], [2402, 749, 2446, 2667, 541], [2548, 5868, 1670, 1164, 1664], [1085, 20, 2506, 3701, 2041], [1753, 3947, 3106, 3919, 3122], [4604, 297, 2024, 5305, 4763], [4086, 2738, 2679, 2762, 2527]]
    gt19 = [2406, 654, 3593, 172, 2774, 4987, 1085, 4365, 5888, 2738]
    #now just go through the KNN and display the returned values and a true corresponding graph
    visualize_matches_with_the_map(0, knn_matches,gt19, IGN04, IGN19)
    display_attribute_unions(2, knn_matches,gt_19, IGN04,IGN19)
