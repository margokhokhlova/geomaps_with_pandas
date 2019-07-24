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

import csv


# some custom files
from img_helpers import get_all_images_in_folder, return_polygons


parser = argparse.ArgumentParser(description="Extracting geo data for all the specified region")
 
# Dataset
parser.add_argument("--global_path", type=str, default= "D:/allegoria/datasets_alegoria/BD/old_data_moselle/BDTOPO/1_DONNEES_LIVRAISON_2019-06-00227/",
                    help="Path to the data folder with topo data")
parser.add_argument("--path-images", type=str, default='D:/allegoria/datasets_alegoria/BD/old_data_moselle/BDORTHO/1_DONNEES_LIVRAISON_2019-06-00226/BDO_RVB_0M50_JP2-E080_LAMB93_MOSELLE',
                    help="Path to corresponding ortho images.")

parser.add_argument("--save-path", type=str, default = "D:/allegoria/topo_ortho/ING_processed_margo/moselle_2004_small/", help = "Where to save the results")
parser.add_argument("--resolution", type=int, default = 500, help = "The final geo coord resolution")
parser.add_argument("--meta_ortho", type = str, default = 'D:/allegoria/datasets_alegoria/BD/old_data_moselle/BDORTHO/3_SUPPLEMENTS_LIVRAISON_2019-06-00226/BDO_RVB_0M50_JP2-E080_LAMB93_MOSELLE/dalles.shp')

args = vars(parser.parse_args())
print(args)
global_path = args["global_path"]
resolution = args["resolution"]


# load all the shapely files related to ROADS

fp_road = global_path + "BDT_2-0_SHP_LAMB93_D057-ED083/A_RESEAU_ROUTIER/ROUTE.shp"
fp_nmrd =  global_path + "BDT_2-0_SHP_LAMB93_D057-ED083/A_RESEAU_ROUTIER/ROUTE_NOMMEE.shp"
fp_prrd=  global_path + "BDT_2-0_SHP_LAMB93_D057-ED083/A_RESEAU_ROUTIER/ROUTE_PRIMAIRE.shp"
fp_scrd = global_path + "BDT_2-0_SHP_LAMB93_D057-ED083/A_RESEAU_ROUTIER/ROUTE_SECONDAIRE.shp"
# Read file using gpd.read_file()
data_road = gpd.read_file(fp_road)
data_nmrd =  gpd.read_file(fp_nmrd)
data_prrd = gpd.read_file(fp_prrd)
data_scrd = gpd.read_file(fp_scrd)
# make a single table with all the roads, not just a signle type
all_roads=  pd.concat([data_road, data_nmrd, data_prrd, data_scrd],ignore_index=True )


# Load all the data from the BUILDINGS caegory
fp_bati =  global_path +"BDT_2-0_SHP_LAMB93_D057-ED083/E_BATI/BATI_INDIFFERENCIE.shp"
fp_inds =global_path +"BDT_2-0_SHP_LAMB93_D057-ED083/E_BATI/BATI_INDUSTRIEL.shp"
# Read file using gpd.read_file()
buildings1= gpd.read_file(fp_bati)
buildings2 =gpd.read_file(fp_inds)
# concaenate the buildings into a single table
all_buildings =  pd.concat([buildings1, buildings2],ignore_index=True, sort=False)
# special buildings
fp_remk = global_path +"BDT_2-0_SHP_LAMB93_D057-ED083/E_BATI/BATI_REMARQUABLE.shp"
buildings3 = gpd.read_file(fp_remk)


# separate them
churches = buildings3.loc[(buildings3['NATURE'] == "Eglise") | (buildings3['NATURE'] == "Chapelle") | (buildings3['NATURE'] =="Bâtiment religieux divers")]
print(len(churches))
towers = buildings3.loc[buildings3['NATURE'] == "Tour, donjon, moulin"]
monuments = buildings3.loc[buildings3['NATURE'] == "Monument"]
forts = buildings3.loc[buildings3['NATURE'] == 'Fort, blockhaus, casemate']
castels =buildings3.loc[buildings3['NATURE'] =='Château']
ordinary_buildings = buildings3.loc[(buildings3['NATURE'] == "Préfecture") | (buildings3['NATURE'] == "Mairie") |
                                   (buildings3['NATURE'] =="Sous-préfecture") | (buildings3['NATURE'] =="Bâtiment sportif") ]

all_buildings = pd.concat([all_buildings , ordinary_buildings],ignore_index=True, sort=False)

#all water
fp_water = global_path +"BDT_2-0_SHP_LAMB93_D057-ED083/D_HYDROGRAPHIE/SURFACE_EAU.shp"
fp_cours =  global_path +"BDT_2-0_SHP_LAMB93_D057-ED083/D_HYDROGRAPHIE/TRONCON_COURS_EAU.shp"
data_water = gpd.read_file(fp_water)
data_cours = gpd.read_file(fp_cours)
all_water =  pd.concat([data_water, data_cours],ignore_index=True,sort=False)

# all sport
fp_sport =global_path +"BDT_2-0_SHP_LAMB93_D057-ED083/E_BATI/TERRAIN_SPORT.shp"
data_sport = gpd.read_file(fp_sport)

# all cemetries
fp_cemetries = global_path +"BDT_2-0_SHP_LAMB93_D057-ED083/E_BATI/CIMETIERE.shp"
data_cemetries = gpd.read_file(fp_cemetries)

# Maybe we will have to remove parks label from here => it is really occupying too much of the surface. We can include it as forest/city data maps aditionally
fp_greenery = global_path + "BDT_2-0_SHP_LAMB93_D057-ED083/F_VEGETATION/ZONE_VEGETATION.shp"
all_greenery = gpd.read_file(fp_greenery)

# aerodroms
fp_aero = global_path + "BDT_2-0_SHP_LAMB93_D057-ED083/E_BATI/PISTE_AERODROME.shp"
data_aero = gpd.read_file(fp_aero)

#railroads
fp_rail = global_path + "BDT_2-0_SHP_LAMB93_D057-ED083/B_VOIES_FERREES_ET_AUTRES/TRONCON_VOIE_FERREE.shp"
data_rail  = gpd.read_file(fp_rail)

# images and dalles
bb_boxes_path = args["meta_ortho"]
bb_boxes = gpd.read_file(bb_boxes_path)

img_type = '.jp2'
image_files = get_all_images_in_folder(args["path_images"], img_type)

with open('D:/allegoria/topo_ortho/ING_processed_margo/ignore_2004_moselle.csv', 'r') as f:
    reader = csv.reader(f)
    ignored_list = list(reader)


################## MAIN PART, SAVE IMAGES & PNG LABELS ######################
my_dpi = 300
for i in range(len(image_files)):  # range - number of images len(image_files)
    name = image_files[i][-36:]
    print(name)
    if [name] in ignored_list:
        print("%s is an image to ignore" %name)
        continue
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
            # get rastr patch and save
            out_image, _ = rasterio.mask.mask(raster,  [polygon_patch], crop=True)
            new_im = Image.fromarray(np.swapaxes(out_image, 0, 2))
            new_im.save(args["save_path"]+ name[:-4] + "/" + str(count).zfill(4) + "_img.png")
            #get vector data pixelized and save
            # shapefiles
            sg_roads = all_roads[all_roads.geometry.intersects(polygon_patch)]  # extract segments of roads
            sg_houses = all_buildings[
                all_buildings.geometry.intersects(polygon_patch)]  # extract segments of ordinary buildings
            sg_churches = churches[churches.geometry.intersects(polygon_patch)]  # churches
            sg_towers = towers[towers.geometry.intersects(polygon_patch)]  # towers
            sg_monuments = monuments[monuments.geometry.intersects(polygon_patch)]  # monuments
            sg_forts = monuments[monuments.geometry.intersects(polygon_patch)]  # forts
            sg_castels = castels[castels.geometry.intersects(polygon_patch)]  # chateux
            
            sg_water = all_water[all_water.geometry.intersects(polygon_patch)]  # extract segments of water
            sg_sport = data_sport[data_sport.geometry.intersects(polygon_patch)]  # extract segments of sport  things
            sg_cemetries = data_cemetries[data_cemetries.geometry.intersects(polygon_patch)]  # cemetries
            sg_aero = data_aero[data_aero.geometry.intersects(polygon_patch)]  # aeroports
            sg_railroads = data_rail[data_rail.geometry.intersects(polygon_patch)]  # railroads
            sg_greenery = all_greenery[all_greenery.geometry.intersects(polygon_patch)]  # forests
            # now get them as image
            fig, ax = plt.subplots(figsize=(10.0, 10.0), dpi=100)  # resolution is fixed for 2000

            sg_roads.plot(linewidth=4.0, edgecolor='#FFA500', color='#FFA500', ax=ax)
            
            
            sg_water.plot(color='#0000FF', ax=ax)
            sg_sport.plot(color='#8A2BE2', ax=ax)
            sg_houses.plot(color='#FF0000', ax=ax)
            sg_churches.plot(color='#FFFF00', ax=ax)
            sg_towers.plot(color="#A52A2A", ax=ax)
            sg_monuments.plot(color='#F5F5DC', ax=ax)
            sg_forts.plot(color='#808080', ax=ax)
            sg_castels.plot(color='#000000', ax=ax)
         
            sg_cemetries.plot(color='#4B0082', ax=ax)
            sg_aero.plot(color='#5F021F', ax=ax)
            sg_railroads.plot(color='#FF00FF', ax=ax)
            
            sg_greenery.plot(color='#00FF00', ax=ax)
            ax.set_xlim([polygon_patch.bounds[0], polygon_patch.bounds[2]])
            ax.set_ylim([polygon_patch.bounds[3], polygon_patch.bounds[1]])
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.axis('off')
            plt.subplots_adjust(left=0., right=1., top=1., bottom=0.)         
            plt.savefig(args["save_path"] + name[:-4] + "/" + str(count).zfill(
                4) + "_lbl.png", dpi=100, bbox_inches='tight', pad_inches=0)  # save the resulting figure
            plt.close('all')

