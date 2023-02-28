""" Minor data preprocessing before plotting data """

# Python Modules 
from datetime import datetime
import itertools
from collections import OrderedDict

# Internal Modules
from wofs.common.zarr import open_dataset
from wofs.plotting.util import to_list, is_list, is_same_type, check_threshs_for_plot_type
from wofs.plotting.data_preprocessing import DataPreProcessor

import os
import numpy as np


class SatelliteLevel2Processor(DataPreProcessor):
    """
    Processes the data and prepares it for plotting. 
    """

    def __init__(self, files_to_load,): 
        self.files_to_load = files_to_load       
        self.config = {
            "ch02_TB.nc": {
                "output" : "g16vis_",
                "name": "vis",
                "load_data": self.get_visible
            },
            "ch14_TB.nc": {
                "output" : "g16ir112_",
                "name": "ir112",
                "load_data": self.get_data
            },
            "ch10_TB.nc": {
                "output" : "g16wv73_",
                "name": "wv73",
                "load_data": self.get_data
            },
            "ch09_TB.nc": {
                "output" : "g16wv69_",
                "name": "wv69",
                "load_data": self.get_data
            },
            "ch08_TB.nc": {
                "output" : "g16wv62_",
                "name": "wv62",
                "load_data": self.get_data
            }
        }

    def load_data(self):
        data = {}
        for file in self.files_to_load:
            config = self.config.get(os.path.basename(file))
            data[config['name']] = config.get('load_data')(file)
        return data
    
    def get_data(self, file):    
        ch = open_dataset(file, decode_times=False)

        rad = ch.variables['Rad'].values[:,:]

        # Convert radiance to Brightness Temp 
        fk1 = ch.variables['planck_fk1'].values
        fk2 = ch.variables['planck_fk2'].values
        bc1 = ch.variables['planck_bc1'].values
        bc2 = ch.variables['planck_bc2'].values

        data = ( fk2 / ( np.log((fk1 / rad) + 1 )) - bc1) / bc2

        print("max of data_var: ",np.max(data))
        print("min of data_var: ",np.min(data))

        (lats, lons) = self.get_lat_lon(ch)

        return {  
            "lats" : lats,
            "lons" : lons,
            "data" : data
        }

    def get_lat_lon(self, ch):
        hv = ch.variables['goes_imager_projection'].attrs['perspective_point_height']
        r_eq = ch.variables['goes_imager_projection'].attrs['semi_major_axis']
        r_pol = ch.variables['goes_imager_projection'].attrs['semi_minor_axis']
        H = r_eq+hv
        lon_origin = ch.variables['goes_imager_projection'].attrs['longitude_of_projection_origin']

        xv = ch.variables['x'].values
        yv = ch.variables['y'].values
        Xv = xv[:] #* hv
        Yv = yv[:] #* hv

        # Convert map points to lats/lons
        lat_rad, lon_rad = np.meshgrid(Xv, Yv)
        # lat/lon calc routine from satellite radian angle vectors
        lambda_0 = (lon_origin*np.pi)/180.0

        a_var = np.power(np.sin(lat_rad),2.0) + (np.power(np.cos(lat_rad),2.0)*(np.power(np.cos(lon_rad),2.0)+(((r_eq*r_eq)/(r_pol*r_pol))*np.power(np.sin(lon_rad),2.0))))
        b_var = -2.0*H*np.cos(lat_rad)*np.cos(lon_rad)
        c_var = (H**2.0)-(r_eq**2.0)

        r_s = (-1.0*b_var - np.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)

        s_x = r_s*np.cos(lat_rad)*np.cos(lon_rad)
        s_y = - r_s*np.sin(lat_rad)
        s_z = r_s*np.cos(lat_rad)*np.sin(lon_rad)

        # latitude and longitude projection for plotting data on traditional lat/lon maps
        latsv = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
        lonsv = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)

        return (latsv, lonsv)

    def get_visible(self, file):
        ch = open_dataset(file, decode_times=False)
        vis64 = ch.variables['Rad'][:,:]

        #CONVERT TO REFLECTANCE
        Esun_Ch_01 = 726.721072
        Esun_Ch_02 = 663.274497
        Esun_Ch_03 = 441.868715
        d2 = 0.3

        vis64 = (vis64 * np.pi * d2) / Esun_Ch_02

        # Make sure all data is in the valid data range
        vis64 = np.maximum(vis64, 0.0)
        vis64 = np.minimum(vis64, 1.0)

        # Apply the formula to adjust reflectance gamma
        vis64_gamma = np.sqrt(vis64)

        (lats, lons) = self.get_lat_lon(ch)

        return {  
            "lats" : lats,
            "lons" : lons,
            "data" : vis64_gamma.values
        }
