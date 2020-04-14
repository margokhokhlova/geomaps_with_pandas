import random
import glob
import os
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, MultiPoint, Polygon, shape
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.linestring import LineString
from shapely.geometry.collection import  GeometryCollection 
from shapely.affinity import translate
import pandas as pd
import numpy as np
from shapely import ops


def calculate_number_of_points(geometry):
    ''' function calculates number of points in the object '''
    if geometry.type == 'Polygon':
        return len(geometry.exterior.coords)
    elif geometry.type == 'LineString':
        return len(geometry.coords)
    else:
        try:
            return(len(geometry.coords))
        except:
            print(f"Error! Unknown type detected: {type(geometry)}, returning 0")
            return 0
def calculate_eccentricity(geometry):
    ''' function calculates eccentricity measure (w/l of min envelop rectangle) '''
    envelop_rect = geometry.minimum_rotated_rectangle
    minx, miny, maxx, maxy = envelop_rect.bounds
    width = maxx - minx
    height = maxy - miny
    if width < height:
        return  width/height
    else:
        return height/width
        
def calculate_perimeter(geometry):
    ''' function calculates the perimeter of the shapely geometry '''
    return geometry.length

def determine_if_connected(geodf, idx1, idx2, delaunay_tringales):
    ' check if the nodes are connected in the graph (the centroinds should belong to one triangle):'
    connected = False
    for d_cell in delaunay_tringales:
        if d_cell.intersects(geodf.centroid[idx1]) and d_cell.intersects(geodf.centroid[idx2]): #if they belong to one cell, they are connected
            return True
        
    return connected
        

def get_node_attributes(shapely_geometry, poly_bound, nature, within_poly = True):
    """ function returns attributes of road/house node"""
    attributes = {}
    obj_type = nature
    if within_poly:
        obj_length = calculate_perimeter(shapely_geometry)
        frame_perimeter = poly_bound.length
        obj_normed_length = obj_length/frame_perimeter 
        obj_points = calculate_eccentricity(shapely_geometry)
    else:
        obj_normed_length = 0
        obj_points = 0
    attributes = {'nature': obj_type, 'normed_length':obj_normed_length, 
                 'eccentricity':obj_points}
    return attributes

def calculate_distance(obj1, obj2):
    ''' this fucntion calculates the minimum distance between the objects:
    if an object is a polygon, its center is considered as a central point
    if an object is a line, the distance is the lenght of the normal from another object,
    if both objects are lines, the distance is 0'''
    d = None
    if obj1.type == 'Polygon' and obj2.type == 'Polygon':
        #print("polyg polyg")
        proj_dist = obj1.centroid.distance(obj2.centroid) #euclidean distance
        d = proj_dist
    elif obj1.type == 'LineString' and obj2.type == 'Polygon':
        #print("linestr polyg")
        proj_dist= obj2.centroid.distance(obj1) 
#         print(proj_dist)
#         print(obj1.project(obj2.centroid))
        d = proj_dist
    elif obj2.type=='LineString' and obj1.type == 'Polygon':
        #print(" polyg linestr")
        proj_dist= obj1.centroid.distance(obj2)     
        d = proj_dist
    elif obj1.type == 'LineString' and  obj2.type=='LineString':
        #print(" linestr linestr")
        if obj1.intersects( obj2):
            d = 0
        else:
            d = None
    elif obj1.type == 'shapely.geometry.LineString' and  obj2.type=='shapely.geometry.LineString':
        #print(" linestr linestr")
        if obj1.intersects( obj2):
            d = 0
        else:
            d = None    
    else:
        print(" unkn unkn")
        try:
            print(type(obj1),type(obj2))
            d = obj2.distance(obj1.centroid)
        except:
            print('Distance calc didnt work')
            d = None
    return d

def calculate_centroids(geodf):
    geodf = geodf.assign(centroid="")
    
    for i in range(len(geodf)):
        geodf.loc[i, ('centroid')] = geodf.loc[i, ('geometry')].centroid
    
    return geodf[~geodf.geometry.is_empty] #last check on empty or not

def clean_and_append(final_data, data_segment, nature, polygon_bbox):
    ''' function copies data from a data frame to a new data list of a following structure:
    nature
    within the image (bool) if the object is entirely inside the polygon or not
    geometry
    returns list of lists with objects like  [[nat, within, geom], [], []...]  '''
    # if it is line object
    if data_segment.empty == True:
        pass     
    else:
        # check if object is completely within the polygon
        for index, row in data_segment.iterrows(): # for each element           
            if row['geometry'].geom_type == 'MultiPolygon' or row['geometry'].geom_type == 'MultiLineString':
                for single_obj in row['geometry']:
                        #print("data ", len(final_data), 'obj', type(single_obj))
                        final_data.append([nature, 1, single_obj]) 
                print('a multistring detected and transformed') 
            elif row['geometry'].is_empty:
                pass
            else:   
                final_data.append([nature, 1, row['geometry']]) # polygons are classified depending on their status always within 

    return final_data