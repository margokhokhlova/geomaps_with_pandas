
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
![An example of the resulting graph created](https://github.com/margokhokhlova/geomaps_with_pandas/blob/master/meurthe_last_ign_rng.png.png)


# Delaunay graphs creation script for OSM data
The notebook shows how to create RNG attributed  graphs using the Delaunay triangulation (check the difference between RNG and Delaunay graphs in [1])
### Delaunay_graphs_creation_demo.ipynb
![An example of the resulting graph created](https://github.com/margokhokhlova/geomaps_with_pandas/blob/master/2004_delaunay.png)
 
# Just a semantic map creation from shapely OSM/IGN data

A project to get the .png maps of given resolution  from shapefiles using Geopandas and Shapely, the notebook is available here:
### data_parser_test_alignment_2004.ipynb
Having an image as a jp2 file and labels as vector data in .shp format, extract the vector data using the bounding boxes from an image, and then save the result as a .png file. 
![An example of the resulting png image created](https://github.com/margokhokhlova/geomaps_with_pandas/blob/master/1-2017-0850-6680-LA93-0M50-E080.png)

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
Copyright 2019-2020 Margarita Khokhlova
Graph creation Examples is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Graph creation Examples are distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

# aknowledgements
This  work  is  supported  by  ANR,  the  French  National  Re-search Agency, within the ALEGORIA project, under GrantANR-17-CE38-0014-01.

# referencies
1. Toussaint, G. T. (1980), "The relative neighborhood graph of a finite planar set", Pattern Recognition, 12 (4): 261–268, doi:10.1016/0031-3203(80)90066-7.
2. Khokhlova, Margarita, Gouet-Brunet, V., Abadie, N., & Chen, L. "Cross-year multi-modal image retrieval using siamese networks." 2020 IEEE International Conference on Image Processing (ICIP). IEEE, 2020
3. Khokhlova, Margarita, Gouet-Brunet, V., Abadie, N., & Chen, L. "Recherche multimodale d'images aériennes multi-date à l'aide d'un réseau siamois." RFIAP. 2020.

