#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import math
from math import cos
import numpy as np
import sys
from netCDF4 import Dataset
from optparse import OptionParser
import os
from datetime import *
from optparse import OptionParser
from wofs_plotting_cbook_sat import *

####################################### Parse Options: ######################################################

parser = OptionParser()
parser.add_option("-p", dest="plotdir", type="string", default= None, help="Directory for Plots")
parser.add_option("-d", dest="tb_dir", type="string", help = "Directory to GOES-ABI L1B Data")
parser.add_option("-w", dest="geodir", type="string", help = "Location of wrfinput file for domain info")
# parser.add_option("-t", dest="t", type="int", help = "Timestep to process")
parser.add_option("-g", dest="gdate", type="string", help = "Input time")


(options, args) = parser.parse_args()

if ((options.plotdir == None) or (options.tb_dir == None)):
    print
    parser.print_help()
    print
    sys.exit(1)
else:
    tb_dir = options.tb_dir
    plotdir = options.plotdir
    geodir = options.geodir
    #t = options.t
    gdate = options.gdate


# DEFINE PROJECTION FOR GOES-east
#p = Proj(proj='geos', h='35786023.0', lon_0='-75.2', sweep='x')


# timestep = str(t)
domain = 'full'

#################################### User-Defined Variables:  #####################################################

edge            = 7 		#number of grid points to remove from near domain boundaries
thin		= 2		#thinning factor for quiver values (e.g. 6 means slice every 6th grid point)

neighborhood = 10
plot_alpha 	= 0.6		#transparency value for filled contour plots,

#################################### Basemap Variables:  #####################################################

resolution 	= 'h'
area_thresh 	= 1000.
damage_files = ''

#################################### Contour Levels:  #####################################################

prob_levels    		= np.arange(0.1,1.1,0.1)		#(%)
vis_levels              = np.arange(0.05,1.1,0.05)
ir_levels      	 	= np.arange(188,314,2)	        # K
wv_levels               = np.arange(190,274,2)	        # K
cp_levels               = np.arange(50,1050,50)
#cwp_levels              = np.arange(0,12.0,0.5)
cwp_levels              = [0.05,0.075,0.1,0.25,0.5,0.75,1.0,1.25,1.5,2.0,2.5,3.0,4.0,5.0,6.0,8.0,10.0,15.0,30.0,60.]

pmm_ir_levels 		= [100., 320.]				#K 
pmm_ir_colors_gray	= [cb_colors.gray8, cb_colors.gray8]	#gray contours

pmm_wv_levels 		= [100., 300.]				#K 
pmm_wv_colors_gray	= [cb_colors.gray8, cb_colors.gray8]	#gray contours

pmm_vis_levels           = [0., 1.0]                          #K 
pmm_vis_colors_gray      = [cb_colors.gray1, cb_colors.gray1]    #gray contours

#################################### Initialize plot attributes using 'web plot' objects:  #####################################################

ir_plot = web_plot('',                   \
                   'GOES-16 ABI Infrared (K)',			\
                   '',                   \
                   cb_colors.gray6,      \
                   ir_levels,            \
                   pmm_ir_levels,        \
                   '',                   \
                   '',                   \
                   pmm_wv_colors_gray,        \
                   'none',		\
                   'none',		\
                   cb_colors.ir_cmap,              \
                   'neither',                \
                   plot_alpha,               \
                   neighborhood)  

wv_plot = web_plot('',                   \
                   'GOES-16 ABI  Water Vapor (K)',			\
                   '',                   \
                   cb_colors.gray6,      \
                   wv_levels,            \
                   pmm_wv_levels,        \
                   '',                   \
                   '',                   \
                   pmm_wv_colors_gray,        \
                   'none',		\
                   'none',		\
                   cb_colors.wv_cmap,              \
                   'neither',                \
                   plot_alpha,               \
                   neighborhood)  
                  
 
vis_plot = web_plot('',                   \
                   'GOES-16 Visible',                      \
                   '',                   \
                   cb_colors.gray6,      \
                   vis_levels,            \
                   pmm_vis_levels,        \
                   '',                   \
                   '',                   \
                   pmm_vis_colors_gray,        \
                   'none',              \
                   'none',              \
                   cb_colors.vis_cmap,              \
                   'neither',                \
                   plot_alpha,               \
                   neighborhood)


######################################################################################################
#################################### Read Data:  #####################################################
######################################################################################################

################### Read probability matched mean WV and IR radiances, CTP and CBP: ##################

#VISIBLE
file2 = os.path.join(tb_dir, 'ch02_TB.nc')
ch2 = Dataset(file2, 'r')
vis64 = ch2.variables['Rad'][:,:]

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

nxv = vis64.shape[0]
nyv = vis64.shape[1]


hv = ch2.variables['goes_imager_projection'].perspective_point_height
r_eq = ch2.variables['goes_imager_projection'].semi_major_axis
r_pol = ch2.variables['goes_imager_projection'].semi_minor_axis
H = r_eq+hv
sat_lon = ch2.variables['goes_imager_projection'].longitude_of_projection_origin
sat_lat = ch2.variables['goes_imager_projection'].latitude_of_projection_origin
sat_sweep = ch2.variables['goes_imager_projection'].sweep_angle_axis
lon_origin = ch2.variables['goes_imager_projection'].longitude_of_projection_origin

xv = ch2.variables['x']
yv = ch2.variables['y']
Xv = xv[:] #* hv
Yv = yv[:] #* hv
ch2.close()

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

#Xsv, Ysv = np.meshgrid(Xv, Yv)
#lonsv, latsv = p(Xsv, Ysv, inverse=True)

# WV / IR
file8 = os.path.join(tb_dir, 'ch08_TB.nc')
file9 = os.path.join(tb_dir, 'ch09_TB.nc')
file10 = os.path.join(tb_dir, 'ch10_TB.nc')
#file13 = os.path.join(tb_dir, 'ch13_TB.nc')
file14 = os.path.join(tb_dir, 'ch14_TB.nc')


ch8 = Dataset(file8, 'r')
rad62 = ch8.variables['Rad'][:,:]
# Convert radiance to Brightness Temp 
fk1 = ch8.variables['planck_fk1'][0]
fk2 = ch8.variables['planck_fk2'][0]
bc1 = ch8.variables['planck_bc1'][0]
bc2 = ch8.variables['planck_bc2'][0]

tb62 = ( fk2 / ( np.log((fk1 / rad62) + 1 )) - bc1) / bc2

print("max of data_var ch8: ",np.max(tb62))
print("min of data_var ch8: ",np.min(tb62))

# LAT, LON, TIME INFO (first file only)
time = ch8.variables['t'][0]
time=float(time)
dttme=datetime.strptime('2000-01-01 12:00:00', '%Y-%m-%d %H:%M:%S') + timedelta(seconds=time)
year=datetime.strftime(dttme, "%Y")
month=datetime.strftime(dttme, "%m")
day=datetime.strftime(dttme, "%d")
hour=datetime.strftime(dttme, "%H")
minute=datetime.strftime(dttme, "%M")
jday=datetime.strftime(dttme, "%j")

angletime=int(hour) + int(minute)/60.0
h_ang = -1.0*math.pi*(angletime - 12.0)/12.0
declin = -23.45*cos(float(jday)*2 * math.pi/365.0 + 10.*2. * math.pi/365.0)

#h = ch8.variables['goes_imager_projection'].perspective_point_height
#sat_lon = ch8.variables['goes_imager_projection'].longitude_of_projection_origin
#sat_lat = ch8.variables['goes_imager_projection'].latitude_of_projection_origin
#sat_sweep = ch8.variables['goes_imager_projection'].sweep_angle_axis
#north = ch8.variables['geospatial_lat_lon_extent'].geospatial_northbound_latitude
#south = ch8.variables['geospatial_lat_lon_extent'].geospatial_southbound_latitude
#east = ch8.variables['geospatial_lat_lon_extent'].geospatial_eastbound_longitude
#west = ch8.variables['geospatial_lat_lon_extent'].geospatial_westbound_longitude
x = ch8.variables['x']
y = ch8.variables['y']
X = x[:] #* h
Y = y[:] #* h

lat_rad, lon_rad = np.meshgrid(X, Y)
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
lats = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
lons = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)


nx = tb62.shape[0]
ny = tb62.shape[1]
#print north, south, east, west
#print nx, ny

ch8.close()

# Convert map points to lats/lons
#Xs, Ys = np.meshgrid(X, Y)
#lons, lats = p(Xs, Ys, inverse=True)

# 6.9 um
ch9 = Dataset(file9, 'r')
rad69 = ch9.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch9.variables['planck_fk1'][0]
fk2 = ch9.variables['planck_fk2'][0]
bc1 = ch9.variables['planck_bc1'][0]
bc2 = ch9.variables['planck_bc2'][0]

tb69 = ( fk2 / ( np.log((fk1 / rad69) + 1 )) - bc1) / bc2

print("max of data_var ch9: ",np.max(tb69))
print("min of data_var ch9: ",np.min(tb69))
ch9.close()

# 7.3 um
ch10 = Dataset(file10, 'r')
rad73 = ch10.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch10.variables['planck_fk1'][0]
fk2 = ch10.variables['planck_fk2'][0]
bc1 = ch10.variables['planck_bc1'][0]
bc2 = ch10.variables['planck_bc2'][0]

tb73 = ( fk2 / ( np.log((fk1 / rad73) + 1 )) - bc1) / bc2

print("max of data_var ch10: ",np.max(tb73))
print("min of data_var ch10: ",np.min(tb73))
ch10.close()


# 10.3 um
#ch13 = Dataset(file13, 'r')
#rad103 = ch13.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
#fk1 = ch13.variables['planck_fk1'][0]
#fk2 = ch13.variables['planck_fk2'][0]
#bc1 = ch13.variables['planck_bc1'][0]
#bc2 = ch13.variables['planck_bc2'][0]

#tb103 = ( fk2 / ( np.log((fk1 / rad103) + 1 )) - bc1) / bc2

#print("max of data_var ch13: ",np.max(tb103))
#print("min of data_var ch13: ",np.min(tb103))
#ch13.close()

# 11.2 um
ch14 = Dataset(file14, 'r')
rad112 = ch14.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch14.variables['planck_fk1'][0]
fk2 = ch14.variables['planck_fk2'][0]
bc1 = ch14.variables['planck_bc1'][0]
bc2 = ch14.variables['planck_bc2'][0]

tb112 = ( fk2 / ( np.log((fk1 / rad112) + 1 )) - bc1) / bc2

print("max of data_var ch14: ",np.max(tb112))
print("min of data_var ch14: ",np.min(tb112))
ch14.close()


geofile = geodir
gin = Dataset(geofile, "r")


############# Get/process date/time info, handle 00Z shift for day but not month/year ############

indate=str(year)+str(month)+str(day)+str(hour)+str(minute)
yyyymodd = indate[0:8]
hour = indate[8:10]
minute = indate[10:12]
valid_label = 'Valid: ' + yyyymodd + ' ' + hour +':'+ minute + ' UTC'
init_label = ' '

############ Get grid/projection info, chop 'edge' from boundaries: ####################

gxlat = gin.variables['XLAT' if 'XLAT' in gin.variables else 'XLAT_M'][:]
gxlon = gin.variables['XLONG' if 'XLONG' in gin.variables else 'XLONG_M'][:]

gxlat = gxlat[0,edge:-edge,edge:-edge]
gxlon = gxlon[0,edge:-edge,edge:-edge]

sw_lat_full = gxlat[0,0]
sw_lon_full = gxlon[0,0]
ne_lat_full = gxlat[-1,-1]
ne_lon_full = gxlon[-1,-1]

cen_lat = gin.CEN_LAT
cen_lon = gin.CEN_LON
stand_lon = gin.STAND_LON
true_lat1 = gin.TRUELAT1
true_lat2 = gin.TRUELAT2
 
gin.close()
del gin

######################## check for missing/unrealistic values and replace with zeros: #############################################

#goes_ir = np.where(goes_ir > 309., 308.9, goes_ir)
#wv = np.where(wv > 350., 0., wv)

################################# Make Figure Template: ###################################################

map, fig, ax1, ax2, ax3 = create_fig(sw_lat_full, sw_lon_full, ne_lat_full, ne_lon_full, true_lat1, true_lat2, cen_lat, stand_lon, damage_files, resolution, area_thresh)

x, y = map(lons[:], lats[:])
xx, yy = map.makegrid(lats.shape[1], lats.shape[0], returnxy=True)[2:4]   #equidistant x/y grid for streamline plots

xv, yv = map(lonsv[:], latsv[:])

##########################################################################################################
###################################### Make Plots: #######################################################
##########################################################################################################

print('plot part')

######################## Synthetic Satellite Plots: #####################

dumbvar = np.zeros((lats.shape[0], lats.shape[1]))
dumbvarv = np.zeros((latsv.shape[0], latsv.shape[1]))

vis_plot.name = 'g16vis_'+gdate
vis_plot.var1_title = 'GOES-16 Visible (0.64 um)  '
sat_plot(map, fig, ax1, ax2, ax3, xv, yv, vis_plot, vis64_gamma[:,:], dumbvarv[:,:], 0, init_label, valid_label, domain, plotdir, '', '', '', 5, 0, spec='False', quiv='False')

ir_plot.name = 'g16ir112_'+gdate
ir_plot.var1_title = 'GOES-16 Infrared (11.2 um) Tb (K) '
sat_plot(map, fig, ax1, ax2, ax3, x, y, ir_plot, tb112[:,:], dumbvar[:,:], 0, init_label, valid_label, domain, plotdir, '', '', '', 5, 0, spec='False', quiv='False') 

#ir_plot.name = 'g16ir103_'+gdate
#ir_plot.var1_title = 'GOES-16 Infrared (10.3 um) Tb (K) '
#sat_plot(map, fig, ax1, ax2, ax3, x, y, ir_plot, tb103[:,:], dumbvar[:,:], t, init_label, valid_label, domain, plotdir, '', '', '', 5, 0, spec='False', quiv='False') 

wv_plot.name = 'g16wv73_'+gdate
wv_plot.var1_title = 'GOES-16 Low-level Water Vapor (7.3 um) Tb (K) '
sat_plot(map, fig, ax1, ax2, ax3, x, y, wv_plot, tb73[:,:], dumbvar[:,:], 0, init_label, valid_label, domain, plotdir, '', '', '', 5, 0, spec='False', quiv='False') 

wv_plot.name = 'g16wv69_'+gdate
wv_plot.var1_title = 'GOES-16 Mid-level Water Vapor (6.9 um) Tb (K) '
sat_plot(map, fig, ax1, ax2, ax3, x, y, wv_plot, tb69[:,:], dumbvar[:,:], 0, init_label, valid_label, domain, plotdir, '', '', '', 5, 0, spec='False', quiv='False')

wv_plot.name = 'g16wv62_'+gdate
wv_plot.var1_title = 'GOES-16 Upper-level Water Vapor (6.2 um) Tb (K) '
sat_plot(map, fig, ax1, ax2, ax3, x, y, wv_plot, tb62[:,:], dumbvar[:,:], 0, init_label, valid_label, domain, plotdir, '', '', '', 5, 0, spec='False', quiv='False')

###### Update latest time .json for web viewer: ######

# lead_time_seconds = t * 300
# json_file = os.path.join(plotdir, 'latest_complete_satellite_verif_g16.json')

# complete_times = {'latest_complete_times' : {
#                     'model': lead_time_seconds }}

# #json_string = json.dumps( complete_times )

# with open(json_file, "w") as file_out:

#     file_out.write( json.dumps(complete_times) )

