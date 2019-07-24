# general libs
import argparse
import geopandas as gpd
import pandas as pd
import csv
import os

import matplotlib
from matplotlib import pyplot as plt
from shapely.geometry import Point, Polygon
from matplotlib.collections import PatchCollection
from descartes.patch import PolygonPatch
from PIL import Image
import os
import numpy as np

# Load the box module from shapely to create box objects
from shapely.geometry import box

## Raster data library
import rasterio
import rasterio.features
import rasterio.warp
import rasterio.mask
from rasterio import plot as rioplot



# some custom files
from img_helpers import get_all_images_in_folder, return_polygons


parser = argparse.ArgumentParser(description="Extracting geo data for all the specified region")

# Dataset
parser.add_argument("--global_path", type=str, default= "D:/allegoria/datasets_alegoria/BD/BD_topo/moselle/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_D057_2019-03-19/BDTOPO/1_DONNEES_LIVRAISON_2019-03-00260",
                    help="Path to the data folder with topo data")
parser.add_argument("--path-images", type=str, default='D:/allegoria/datasets_alegoria/BD/BD_ortho/mozelle/BDORTHO_2-0_RVB-0M50_JP2-E080_LAMB93_D057_2015-01-01/BDORTHO/1_DONNEES_LIVRAISON_2016-02-00008/BDO_RVB_0M50_JP2-E080_LAMB93_D57-2015',
                    help="Path to corresponding ortho images.")

parser.add_argument("--save-path", type=str, default = "D:/allegoria/topo_ortho/ING_processed_margo/moselle/", help = "Where to save the results")
parser.add_argument("--resolution", type=int, default = 1000, help = "The final image resolution")
parser.add_argument("--meta_ortho", type = str, default = "D:/allegoria/datasets_alegoria/BD/BD_ortho/mozelle/BDORTHO_2-0_RVB-0M50_JP2-E080_LAMB93_D057_2015-01-01/BDORTHO/5_SUPPLEMENTS_LIVRAISON_2016-02-00008/BDO_RVB_0M50_JP2-E080_LAMB93_D57-2015/dalles.shp")

args = vars(parser.parse_args())
print(args)
global_path = args["global_path"]
resolution = args["resolution"]


# images and dalles
bb_boxes_path = args["meta_ortho"]
bb_boxes = gpd.read_file(bb_boxes_path)

img_type = '.jp2'
image_files = get_all_images_in_folder(args["path_images"], img_type)


################## MAIN PART, SAVE IMAGES & PNG LABELS ######################
my_dpi = 300
for i in range(1,len(image_files)):  # range - number of images len(image_files)
    name = image_files[i][-36:]
    print(name)
    with rasterio.open(image_files[i]) as dataset:
        # Read the dataset's valid data mask as a ndarray.
        mask = dataset.dataset_mask()
        # Extract feature shapes and values from the array.
        for geom, val in rasterio.features.shapes(
                mask, transform=dataset.transform):
            # Transform shapes from the dataset's own coordinate
            # reference system to CRS84 (EPSG:4326).
            geom = rasterio.warp.transform_geom(
                dataset.crs, 'epsg:2154', geom, precision=6)

        raster = rasterio.open(image_files[i])

        #  some setup
        bb_box = geom['coordinates']
        polygon_bbox = Polygon(bb_box[0])
        polygons = return_polygons(image_bounds=polygon_bbox.bounds,
                                   resolution=(resolution, resolution))  # cut image into patches, the geo res is used

        # create a directory where the patches will be stored
        try:
            os.mkdir(args["save_path"] + name[:-4])
        except:
            print("already exists!")
        pd_poly = pd.DataFrame(polygons)
        pd_poly.to_csv(args["save_path"] + name[:-4] + "/geo_polygons.csv")
        for count, polygon_patch in enumerate(polygons):
            #get rastr patch and save
            out_image, _ = rasterio.mask.mask(raster,  [polygon_patch], crop=True)
            new_im = Image.fromarray(np.swapaxes(out_image, 0, 2))
            new_im.save(args["save_path"]+ name[:-4] + "/" + str(count).zfill(4) + "_img.png")





