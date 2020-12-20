
# Conversion of the geomaps in the shapefile form to graphs

This project is a collection of notebooks performing different methods to create graphs and semantic labels from the shapefiles data.

The most known geomaps open source is OSM, so the demo notebooks are adapted to use OSM shapefiles as can be found here: https://www.openstreetmap.org/

We also use IGN data, available for research purposes under a license  "Recherche et Enseignement": https ://geoservices.ign.fr

# OSM data & polygons
An example of the OSM data used in the project is available here: https://drive.google.com/file/d/131ZEmiO2KCfE-5cLIPmxBtaeaAXEGK80/view?usp=sharing
It is the slightly processed OSM data (we merged buildings which touch each other)
The polygons for Moselle deparments are given for the reference as well in a shape file image_polygons_57.shp.

# RNG graphs creation script for OSM data
Please, check the notebook:
### RNG_graph_creation_demo.ipynb
The notebook shows how to create RNG attributed  graphs using the algorithm introduced in [1].


# Delaunay graphs creation script for OSM data
The notebook shows how to create RNG attributed  graphs using the Delaunay triangulation (check the difference between RNG and Delaunay graphs in [1])
### Delaunay_graphs_creation_demo.ipynb
We also left an old demo for the graph creation form the IGN data, but we don't provide the BD topo used along with the project. Please, check the notebook for details: data_parser_distinguished_graphs.ipynb

![An example of the resulting graphs created for OSM and IGN data](https://github.com/margokhokhlova/geomaps_with_pandas/blob/master/rng_delaunay.png)
 
# Just a semantic map creation from shapely OSM/IGN data

A project to get the .png maps of given resolution  from shapefiles using Geopandas and Shapely, the notebook is available here:
### data_parser_test_alignment_2004.ipynb
Having an image as a jp2 file and labels as vector data in .shp format, extract the vector data using the bounding boxes from an image, and then save the result as a .png file. 
![An example of the resulting png image created](https://github.com/margokhokhlova/geomaps_with_pandas/blob/master/1-2017-0850-6680-LA93-0M50-E080.png?v=300&s=200)

# Final data as txt files and dataloaders

The data can  be downloaded from here:
https://drive.google.com/drive/folders/12cWiUhE278O4y2Z-hV6rMROvnVUoqxP5?usp=sharing
These graph datasets are derived from exceirpts of the reference vector database produced by the French Mapping Agency (https://www.ign.fr/), namely the BDTOPO®
    and Open Street Map (https://www.openstreetmap.org/), namely OSM.

Each graph represents the geographic entites located in a bouding box of 200 m on each side, centered on a given point of interest, and theirs spatial relationships.

  The graphs are built for BBOX located the following French admnistratives units:
  - Moselle
  - Meurthe-et-Moselle 

  A distinct graph is built for each POI-centered BBOX, and for the following years:
  - 2004
  - 2010
  - 2014
  - 2019

This  is cross-temporal and cross-source dataset for French departments. The same source and cross-source data are separated by folders.

 We provide the data in the form which is the most convenient for our two set of experiements, as described in [1]. There are 2 folders, ech per_department, and the graphs IDs match each other across all the subfolders in one folder, but not across the higher folders in the hierarchy. 

Each separate data IGN+'Year' has the following components (inspired by the other commong graph dataset structure):
     IGN+'Year'_A.txt - edge list
     IGN+'Year'_edge_labels.txt - edge labels
     IGN+'Year'_graph_indicator.txt - list of the node-graph correspondences
     IGN+'Year'_graph_labels.txt - graph areas IDs
     IGN+'Year'_node_attributes.txt - continious node attributes
     IGN+'Year'_node_labels.txt - discreet node labels


 Each deparment contains 4 distinct dates for IGN data. OSM data we use are dated 2020, however, there are also 4 sets of data to match the cross-time cross-search data retrieval/
         /2004
         /2010
         /2014
         /2019

## DATALOADERS

 To ease the use of our dataset, we provide the daloaders compatible with Pytorch 
 Geometric (the code here is the modified code from Pytorch Geometric data loader)
 
 You can find the daloader in the file:

 ign_dataset.py

 To upload the dataset, please import the dataloader from .py file to your workspace, then call:
 ign = IGNDataset('/path/to/the folder/with/txt', prefix ='IGN_19',use_node_attr=True)
 When loaded, the dataset can be passed to the torch_geometric.data.DataLoader as an argument.

You can also display view the graphs, but we use a different dataloader for that.
Please, check the following jupyter notebook from scripts folder for demos and details:
results_visualization_notebook.ipynb
    
We envisaged the final task as the similarity-based graph matching across years and databases. 
However,the task is not always trivial, the resulting graphs can be pretty different for different databases and across years.
![An example of two RNG graphs created from the same area for IGN and OSM](https://github.com/margokhokhlova/geomaps_with_pandas/blob/master/ign_osm_superimposed_rng_100_moselle.png?v=300&s=200)


# Requirements
Full project requirements are specified in requirements.txt
The minimal requirements for graph creation notebooks are:
* Networkx
* Geopandas
* Pandas
* Shapely
* Matplotlib
* Earthpy
* Pickle

# License
All code found in this repository is licensed under GPLv3:

Copyright 2019-2020 Margarita Khokhlova, margarita.khokhlova@ign.fr, margokhokhlova@gmail.com

Graph creation Examples is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Graph creation Examples are distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details <https://www.gnu.org/licenses/>.

# Aknowledgements
This  work  is  supported  by  ANR,  the  French  National  Re-search Agency, within the ALEGORIA project, under GrantANR-17-CE38-0014-01.

# To cite

More information on the graph creation process in provided in the following article:
Margarita Khokhlova, Nathalie Abadie, Valérie Gouet, Liming Chen. Learning embeddings for cross-time geographic areas represented as graphs. In 36th ACM/SIGAPP Symposium On Applied Computing - Technical Track Geographic Information Analysis. 2021.

# Referencies
1. Toussaint, G. T. (1980), "The relative neighborhood graph of a finite planar set", Pattern Recognition, 12 (4): 261–268, doi:10.1016/0031-3203(80)90066-7.
2. Khokhlova, Margarita, Gouet-Brunet, V., Abadie, N., & Chen, L. "Cross-year multi-modal image retrieval using siamese networks." 2020 IEEE International Conference on Image Processing (ICIP). IEEE, 2020
3. Khokhlova, Margarita, Gouet-Brunet, V., Abadie, N., & Chen, L. "Recherche multimodale d'images aériennes multi-date à l'aide d'un réseau siamois." RFIAP. 2020.

