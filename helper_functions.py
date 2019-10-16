
import pandas as pd
import re
from shapely.geometry import Polygon
import glob
import fiona
from shapely.geometry import shape
import networkx as nx
from shapely.geometry import Point

from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.linestring import LineString


def get_nodes_as_points(G):
    list_of_nodes = []
    for node in G.nodes:
        list_of_nodes.append(Point(node))
    return list_of_nodes

def create_graph(gp_frame, draw_shapefile=False, draw_graph=False):
    G = nx.Graph()
    for shp in range(len(gp_frame)-1):
        # the geometry property here may be specific to my shapefile
        road1 = gp_frame['geometry'].iloc[shp]
        for shp2 in range(shp+1, len(gp_frame)):
            road2 = gp_frame['geometry'].iloc[shp2]
            if road1.intersects(road2):
                 G.add_edge(shp, shp2)

    return G

def make_single_string_object(gp_segment):
    """ some data contain multistring objects - I separte those"""
    new_df_with_col_names = pd.DataFrame(data=None, columns=gp_segment.columns)
    indexes_to_delete = []
    for road in range(len(gp_segment)):          
        # take each road
        if isinstance(gp_segment['geometry'].iloc[road], MultiLineString): # if it is a multistring
            multistrings = gp_segment['geometry'].iloc[road]
            temp_df_object = gp_segment.iloc[road].copy()
            indexes_to_delete.append([road])
            for i in range(len(multistrings)):
                temp_df_object['geometry'] = multistrings[i]
                new_df_with_col_names = new_df_with_col_names.append(temp_df_object, ignore_index=True)  
            
        else:
            new_df_with_col_names = new_df_with_col_names.append(gp_segment.iloc[road], ignore_index=True)           
    return new_df_with_col_names
            
def getpolygons(csv_files):
    list_polygons = []
    for file in csv_files:
        myFile = pd.read_csv(file)
        myFile.columns=['int', 'polygon']
        for j in range(len(myFile.polygon)):
            test_string = myFile.polygon[j]
            res =  re.sub(r"[^Z0-9]+", ' ', test_string) #''.join(there.findall(test_string))
            coordinates = res.split()
            # test_poly  = Polygon([[int(coordinates[0].ljust(7, '0')), int(coordinates[1].ljust(7, '0'))], [int(coordinates[2].ljust(7, '0')), int(coordinates[3].ljust(7, '0'))],
            #           [int(coordinates[4].ljust(7, '0')),
            #             int(coordinates[5].ljust(7, '0'))], [int(coordinates[6].ljust(7, '0')), int(coordinates[7].ljust(7, '0'))]])
            test_poly = Polygon([[int(coordinates[0]), int(coordinates[1])], [int(coordinates[2]), int(coordinates[3])],
                                 [int(coordinates[4]),
                                  int(coordinates[5])], [int(coordinates[6]), int(coordinates[7])]])
            list_polygons.append(test_poly)
    return list_polygons


def make_dictionary_img_polygon(polygons, image_names):
    """ function just arranges polygons - corresponding images in a python dictionnary """

def drop_columns_and_add_one(pd_df, pd_dataframe_type):
    ''' this function just cleans the df removing extra columns'''
    if pd_dataframe_type == 'roads':
        pd_df =pd_df.drop(['ACCES_PED','ACCES_VL','ALIAS_D','ALIAS_G','BORNEDEB_D','BORNEDEB_G','BORNEFIN_D',
                           'BORNEFIN_G','BUS','CL_ADMIN','SENS','SOURCE','STATUT_TOP','TOPONYME',
                         'TYPE_ROUTE','TYP_ADRES','URBAIN','VIT_MOY_VL','VOIE_VERTE',
                         'CYCLABLE','C_POSTAL_D','C_POSTAL_G','DATE_APP','DATE_CONF','DATE_CREAT','DATE_MAJ',
                          'DATE_SERV','ETAT','FERMETURE', 'FICTIF','GESTION',
                         'ID_RN','ID_SOURCE','ID_VOIE_D','ID_VOIE_G','IMPORTANCE','INSEECOM_D','INSEECOM_G','PREC_ALTI',
                          'PREC_PLANI','PRIVE','RESTR_H','RESTR_LAR','RESTR_LON','RESTR_MAT','RESTR_P','RESTR_PPE',
                         'ITI_CYCL','IT_VERT','LARGEUR','NATURE','NAT_RESTR','NB_VOIES','NOM_1_D','NOM_1_G','NOM_2_D','NOM_2_G','NUMERO',
                          'NUM_EUROP','POS_SOL'], axis=1)        
        pd_df['Nature'] = 0

    else:       #water
        pd_df = pd_df.drop(['CODE_HYDRO','COMMENT','DATE_APP', 
                                      'DATE_CONF','DATE_CREAT','DATE_MAJ',
                                      'SOURCE','STATUT','STATUT_TOP','TOPONYME',
                                      'ID_SOURCE','IMPORTANCE','MAREE',
                                      'PERMANENT'], axis=1)
        

        pd_df['Nature'] = 1
    return pd_df



def create_adjacency_matrix(gp_frame):
    ''' function takes the pandas frame and creates the adjcency matrix for edges and a list of nodes with values,
    where non-zero values are the intersection point coordinates'''
    total_edges = len(gp_frame)
    adjacency_matrix = np.zeros((total_edges,total_edges), dtype='O')
    node_values = np.zeros((total_edges,total_edges), dtype='O')
    for shp in range(1, len(gp_frame)):
        # the geometry property here may be specific to my shapefile
        line1 = gp_frame['geometry'].iloc[shp]
        for shp2 in range(0, shp-1):
            line2 = gp_frame['geometry'].iloc[shp2]
            if line1.intersects(line2):
                node_values[shp, shp2] = line1.intersection(line2)
                adjacency_matrix[shp,shp2] =gp_frame['Nature'].iloc[shp], gp_frame['Nature'].iloc[shp2]

    return adjacency_matrix, node_values

def check_order(img_paths, csv_paths, num_cut = 25):
    img_paths.sort()
    csv_paths.sort()
    for i in range(0, len(img_paths), num_cut):
        given_im = img_paths[i]
        folder_im = given_im[57:-14]
        given_csv = csv_paths[int(i/25)]
        folder_csv = given_csv[-49:-18]

        if folder_csv != folder_im:
            print("Check the folder correspondence! Error in the check order funtion")
            break
    return 1

def check_if_image_exists(polygon_bbox, csv_poly):
    found = None
    for i, poly in enumerate(csv_poly):
        if poly.area <= 10000000:
            if polygon_bbox.intersection(poly).area >= 10000:
            #    poly.intersects(bb_boxes.geometry[2000]):
                 print('found')
                 #del csv_poly[i] # delete the element so it is never taken again
                 found = i
                 break

    return found

from shapely.geometry.multilinestring import MultiLineString
def make_silgle_string_roads(gp_segment):
    """ funciton takes the gpd df and breakes down the segments in two when the roads are made out of multi srting object"""
    new_df_with_col_names = pd.DataFrame(data=None, columns=gp_segment.columns)
    indexes_to_delete = []
    for road in range(len(gp_segment)):
        # take each road
        if isinstance(gp_segment['geometry'].iloc[road], MultiLineString) : # if it is a multistring
            multistrings = gp_segment['geometry'].iloc[road]
            temp_df_object = gp_segment.iloc[road].copy()
            indexes_to_delete.append([road])
            for i in range(len(multistrings)):
                temp_df_object['geometry'] = multistrings[i]
                new_df_with_col_names = new_df_with_col_names.append(temp_df_object)
        else:
            continue
    gp_segment.drop(gp_segment.index[tuple(indexes_to_delete)])
    return gp_segment.append(new_df_with_col_names, ignore_index = True)

# unit testing
if __name__ == '__main__':
    images_paths = 'D:/allegoria/topo_ortho/ING_processed_margo/basrhin_2019/'
    imagePaths = glob.glob(images_paths + '*/*img.png')
    excelPaths = glob.glob(images_paths + '*/*.csv')

    print(len(imagePaths))  # images
    print(len(excelPaths))  # corresponding csv paths

    check_order(imagePaths, excelPaths)

    csv_poly = getpolygons(excelPaths)
    print("Saved csv polygons are loaded correctly and passed the verfication test, there %d and %d of each." % (
        len(imagePaths), len(csv_poly)))

    print("Example of a directory name ", imagePaths[0][57:-13 ])
    print("Example of an img save name ",imagePaths[0][-45: ] )
    print("Example of an label save name ",imagePaths[0][-45:-8 ]+"_lbl.png" )

