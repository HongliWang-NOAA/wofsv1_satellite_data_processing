######## GENERATE GOES-R TB OBSERVATIONS FOR ALL IR CHANNELS
##   USE CONUS LEVEL 1-B DATA GILES
##   USE CONUS LEVEL 2 CLOUD TOP HEIGHT 
##   OUTPUT OBSERVATIONS IN 1-D NETCDF FORMAT
##   
##   By: 			Thomas A. Jones
##	 Create Date:	May 10, 2018
##	 Version 		1.3
##	 Modified 		November 20, 2018: Start adding all-sky requirements
##				December 1, 2022: Bug fixes and modifiecations for use on the cloud
##	                        June 2023: Make version for 2 km CTH product								
####################################################

# CONUS
import sys
import os
from netCDF4 import Dataset
import numpy as np
#from pyproj import Proj
import pyresample
from news_e_post_cbook import *
from datetime import *
from math import pi, sin, cos, sqrt, acos, asin
from optparse import OptionParser

from pygeodesy.sphericalNvector import LatLon
from pygeodesy.points import isenclosedBy

####################################### Parse Options: ######################################################

parser = OptionParser()
parser.add_option("-d", dest="tb_dir", type="string", default= None, help="Input Directory of L1B files")
parser.add_option("-w", dest="wrf_dir", type="string", help = "Path to wrfinput_d01 file domain info")
parser.add_option("-o", dest="out_dir", type="string", help = "Output Directory observation file")
parser.add_option("-a", dest="observation_time", type="string", help = "Time at which obs are to be assimialted")
parser.add_option("-t", dest="thin", type="int", help = "Thinning Number")
parser.add_option("-s", dest="sat", type="string", help = "Satellite: G16, G17, G18")
(options, args) = parser.parse_args()

tb_dir = options.tb_dir
wrf_dir = options.wrf_dir
out_dir = options.out_dir
obstime = options.observation_time
thin = options.thin
sat = options.sat
#sat = 'GOES16'

# GRID SPACING
gspace = 0.05 #5 km
gspace_m = 5000

_domain_gridpoint_margin = 7

# DEFINE PROJECTION FOR GOES
if ( sat == 'G16'): 
#   p = Proj(proj='geos', h='35786023.0', lon_0='-75.2', sweep='x')
   osat = 'GOES16'
if ( sat == 'G17'):             
#   p = Proj(proj='geos', h='35786023.0', lon_0='-137.2', sweep='x')
   osat = 'GOES17'
if ( sat == 'G18'):
#   p = Proj(proj='geos', h='35786023.0', lon_0='-137.2', sweep='x')
   osat = 'GOES18'


# INPUT FILES
file7 = os.path.join(tb_dir, 'ch07_TB.nc')
file8 = os.path.join(tb_dir, 'ch08_TB.nc')
file9 = os.path.join(tb_dir, 'ch09_TB.nc')
file10 = os.path.join(tb_dir, 'ch10_TB.nc')
file11 = os.path.join(tb_dir, 'ch11_TB.nc')
file12 = os.path.join(tb_dir, 'ch12_TB.nc')
file13 = os.path.join(tb_dir, 'ch13_TB.nc')
file14 = os.path.join(tb_dir, 'ch14_TB.nc')
file15 = os.path.join(tb_dir, 'ch15_TB.nc')
file16 = os.path.join(tb_dir, 'ch16_TB.nc')
cthfile = os.path.join(tb_dir, 'cth.nc')

wrffile = wrf_dir

#file7 = '/home/Thomas.Jones/GOES16_PROCESS/test_data/OR_ABI-L1b-RadC-M3C07_G16_s20181162307.nc'
#file8 = '/home/Thomas.Jones/GOES16_PROCESS/test_data/OR_ABI-L1b-RadC-M3C08_G16_s20181162307.nc'
#file9 = '/home/Thomas.Jones/GOES16_PROCESS/test_data/OR_ABI-L1b-RadC-M3C09_G16_s20181162307.nc'
#file10 = '/home/Thomas.Jones/GOES16_PROCESS/test_data/OR_ABI-L1b-RadC-M3C10_G16_s20181162307.nc'
#file11 = '/home/Thomas.Jones/GOES16_PROCESS/test_data/OR_ABI-L1b-RadC-M3C11_G16_s20181162307.nc'
#file12 = '/home/Thomas.Jones/GOES16_PROCESS/test_data/OR_ABI-L1b-RadC-M3C12_G16_s20181162307.nc'
#file13 = '/home/Thomas.Jones/GOES16_PROCESS/test_data/OR_ABI-L1b-RadC-M3C13_G16_s20181162307.nc'
#file14 = '/home/Thomas.Jones/GOES16_PROCESS/test_data/OR_ABI-L1b-RadC-M3C14_G16_s20181162307.nc'


# READ IN WRFINPUT FILE FOR DOMAIN BOUNDARIES
wrfin = Dataset(wrffile, "r")
#wlat = wrfin.variables["XLAT"][:]
#wlon = wrfin.variables["XLONG"][:]
wlat = wrfin.variables['XLAT' if 'XLAT' in wrfin.variables else 'XLAT_M'][:]
wlon = wrfin.variables['XLONG' if 'XLONG' in wrfin.variables else 'XLONG_M'][:]
cen_lat = wrfin.CEN_LAT
cen_lon = wrfin.CEN_LON
stand_lon = wrfin.STAND_LON
true_lat1 = wrfin.TRUELAT1
true_lat2 = wrfin.TRUELAT2

inner_domain = LatLon(wlat[0,_domain_gridpoint_margin,_domain_gridpoint_margin], wlon[0,_domain_gridpoint_margin,_domain_gridpoint_margin]), \
   LatLon(wlat[0,_domain_gridpoint_margin,-_domain_gridpoint_margin], wlon[0,_domain_gridpoint_margin,-_domain_gridpoint_margin]), \
   LatLon(wlat[0,-_domain_gridpoint_margin,-_domain_gridpoint_margin], wlon[0,-_domain_gridpoint_margin,-_domain_gridpoint_margin]), \
   LatLon(wlat[0,-_domain_gridpoint_margin,_domain_gridpoint_margin], wlon[0,-_domain_gridpoint_margin,_domain_gridpoint_margin])

print(f"Bottom left inner domain: {inner_domain[0]}")
print(f"Bottom right inner domain: {inner_domain[1]}")
print(f"Top right inner domain: {inner_domain[2]}")
print(f"Top left inner domain: {inner_domain[3]}")

# CREATE OBS GRID
nlons = 220 #int((len(wrfin.dimensions['west_east']) * wrfin.getncattr('DX'))  /  gspace_m)
nlats = 220 #int((len(wrfin.dimensions['south_north']) * wrfin.getncattr('DY'))  /  gspace_m)
print(f'Creating {nlons}x{nlats} grid.')

wrfin.close()

maxlat = np.max(wlat)
minlat = np.min(wlat)
maxlon = np.max(wlon)
minlon = np.min(wlon)

print("maxlon: ", maxlon)
print("minlon: ", minlon)
print("maxlat: ", maxlat)
print("minlat: ", minlat)

mlon = np.zeros(shape=(nlons,nlats))*np.nan
mlat = np.zeros(shape=(nlons,nlats))*np.nan

for j in range(0, nlats):
   for i in range(0, nlons):
      mlat[i,j] = maxlat - gspace*(j)
      mlon[i,j] = maxlon - gspace*(i)

print(mlon[0,0], mlat[0,0])
print(mlon[nlons-1, nlats-1], mlat[nlons-1, nlats-1])

# 3.9 um
ch7 = Dataset(file7, 'r')
rad39 = ch7.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch7.variables['planck_fk1'][0]
fk2 = ch7.variables['planck_fk2'][0]
bc1 = ch7.variables['planck_bc1'][0]
bc2 = ch7.variables['planck_bc2'][0]

tb39 = ( fk2 / ( np.log((fk1 / rad39) + 1 )) - bc1) / bc2

print("max of data_var ch7: ",np.max(tb39))
print("min of data_var ch7: ",np.min(tb39))

# LAT, LON, TIME INFO (first file only)
time = ch7.variables['t'][0]
time=float(time)
dttme=datetime.strptime('2000-01-01 12:00:00', '%Y-%m-%d %H:%M:%S') + timedelta(seconds=time)
year=datetime.strftime(dttme, "%Y")
month=datetime.strftime(dttme, "%m")
day=datetime.strftime(dttme, "%d")
hour=datetime.strftime(dttme, "%H")
minute=datetime.strftime(dttme, "%M")
jday=datetime.strftime(dttme, "%j")

angletime=int(hour) + int(minute)/60.0
h_ang = -1.0*pi*(angletime - 12.0)/12.0
declin = -23.45*cos(float(jday)*2 * pi/365.0 + 10.*2. * pi/365.0)

h = ch7.variables['goes_imager_projection'].perspective_point_height
r_eq = ch7.variables['goes_imager_projection'].semi_major_axis
r_pol = ch7.variables['goes_imager_projection'].semi_minor_axis
H = r_eq+h
lon_origin = ch7.variables['goes_imager_projection'].longitude_of_projection_origin
sat_lon = ch7.variables['goes_imager_projection'].longitude_of_projection_origin
sat_lat = ch7.variables['goes_imager_projection'].latitude_of_projection_origin
sat_sweep = ch7.variables['goes_imager_projection'].sweep_angle_axis
north = ch7.variables['geospatial_lat_lon_extent'].geospatial_northbound_latitude
south = ch7.variables['geospatial_lat_lon_extent'].geospatial_southbound_latitude
east = ch7.variables['geospatial_lat_lon_extent'].geospatial_eastbound_longitude
west = ch7.variables['geospatial_lat_lon_extent'].geospatial_westbound_longitude
x = ch7.variables['x']
y = ch7.variables['y']
X = x[:] #* h
Y = y[:] #* h

nx = rad39.shape[0]
ny = rad39.shape[1]
#print north, south, east, west
#print nx, ny

ch7.close()

# Convert map points to lats/lons
#Xs, Ys = np.meshgrid(X, Y)
#lons, lats = p(Xs, Ys, inverse=True)

# ***********
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


rmaxlat = np.max(lats[5:nx,5:ny])
rminlat = np.min(lats[5:nx,5:ny])
rmaxlon = np.max(lons[5:nx,5:ny])
rminlon = np.min(lons[5:nx,5:ny])

print("rmaxlon: ", rmaxlon)
print("rminlon: ", rminlon)
print("rmaxlat: ", rmaxlat)
print("rminlat: ", rminlat)


# 6.2 um
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
ch8.close()

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


# 8.5 um
ch11 = Dataset(file11, 'r')
rad85 = ch11.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch11.variables['planck_fk1'][0]
fk2 = ch11.variables['planck_fk2'][0]
bc1 = ch11.variables['planck_bc1'][0]
bc2 = ch11.variables['planck_bc2'][0]

tb85 = ( fk2 / ( np.log((fk1 / rad85) + 1 )) - bc1) / bc2

print("max of data_var ch11: ",np.max(tb85))
print("min of data_var ch11: ",np.min(tb85))
ch11.close()

# 9.6 um
ch12 = Dataset(file12, 'r')
rad96 = ch12.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch12.variables['planck_fk1'][0]
fk2 = ch12.variables['planck_fk2'][0]
bc1 = ch12.variables['planck_bc1'][0]
bc2 = ch12.variables['planck_bc2'][0]

tb96 = ( fk2 / ( np.log((fk1 / rad96) + 1 )) - bc1) / bc2

print("max of data_var ch12: ",np.max(tb96))
print("min of data_var ch12: ",np.min(tb96))
ch12.close()

# 10.3 um
ch13 = Dataset(file13, 'r')
rad103 = ch13.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch13.variables['planck_fk1'][0]
fk2 = ch13.variables['planck_fk2'][0]
bc1 = ch13.variables['planck_bc1'][0]
bc2 = ch13.variables['planck_bc2'][0]

tb103 = ( fk2 / ( np.log((fk1 / rad103) + 1 )) - bc1) / bc2

print("max of data_var ch13: ",np.max(tb103))
print("min of data_var ch13: ",np.min(tb103))
ch13.close()


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

# 12.3 um
ch15 = Dataset(file15, 'r')
rad123 = ch15.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch15.variables['planck_fk1'][0]
fk2 = ch15.variables['planck_fk2'][0]
bc1 = ch15.variables['planck_bc1'][0]
bc2 = ch15.variables['planck_bc2'][0]

tb123 = ( fk2 / ( np.log((fk1 / rad123) + 1 )) - bc1) / bc2

print("max of data_var ch15: ",np.max(tb123))
print("min of data_var ch15: ",np.min(tb123))
ch15.close()


# 13.3 um
ch16 = Dataset(file16, 'r')
rad133 = ch16.variables['Rad'][:,:]

# Convert radiance to Brightness Temp 
fk1 = ch16.variables['planck_fk1'][0]
fk2 = ch16.variables['planck_fk2'][0]
bc1 = ch16.variables['planck_bc1'][0]
bc2 = ch16.variables['planck_bc2'][0]

tb133 = ( fk2 / ( np.log((fk1 / rad133) + 1 )) - bc1) / bc2

print("max of data_var ch16: ",np.max(tb133))
print("min of data_var ch16: ",np.min(tb133))
ch16.close()




####### CLOUD TOP HEIGHT (m)
cthf = Dataset(cthfile, 'r')
#cthf.set_auto_scale(False)
cth = cthf.variables['HT']
cth_orig = cth[:,:]

cth_scalefactor = cth.scale_factor
cth_orig.astype('float')

cth_qc = cthf.variables['DQF'][:,:]  #0 = good

cthf.set_auto_scale(True)
cth_x = cthf.variables['x']
cth_y = cthf.variables['y']
cth_X = cth_x[:] #* h
cth_Y = cth_y[:] #* h

cth_nx = cth.shape[0]
cth_ny = cth.shape[1]

cthf.close()

# Convert map points to lats/lons
#cth_Xs, cth_Ys = np.meshgrid(cth_X, cth_Y)
#cth_lons, cth_lats = p(cth_Xs, cth_Ys, inverse=True)
cth_lat_rad, cth_lon_rad = np.meshgrid(cth_X, cth_Y)

# lat/lon calc routine from satellite radian angle vectors
lambda_0 = (lon_origin*np.pi)/180.0

a_var = np.power(np.sin(cth_lat_rad),2.0) + (np.power(np.cos(cth_lat_rad),2.0)*(np.power(np.cos(cth_lon_rad),2.0)+(((r_eq*r_eq)/(r_pol*r_pol))*np.power(np.sin(cth_lon_rad),2.0))))
b_var = -2.0*H*np.cos(cth_lat_rad)*np.cos(cth_lon_rad)
c_var = (H**2.0)-(r_eq**2.0)

r_s = (-1.0*b_var - np.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)

s_x = r_s*np.cos(cth_lat_rad)*np.cos(cth_lon_rad)
s_y = - r_s*np.sin(cth_lat_rad)
s_z = r_s*np.cos(cth_lat_rad)*np.sin(cth_lon_rad)

# latitude and longitude projection for plotting data on traditional lat/lon maps
cth_lats = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
cth_lons = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)


# FIX RAW CTH VALUES AND SCALE MANUALLY
cth_fix = cth_orig 
#cth_fix = np.where(cth_fix < -1.0, np.abs(cth_fix)+32767.0, cth_fix )
#cth_scale = cth_fix*cth_scalefactor
cth_scale = cth_fix

cmaxlat = np.max(cth_lats[1:cth_nx,1:cth_ny])
cminlat = np.min(cth_lats[1:cth_nx,1:cth_ny])
cmaxlon = np.max(cth_lons[1:cth_nx,1:cth_ny])
cminlon = np.min(cth_lons[1:cth_nx,1:cth_ny])

print("cmaxlon: ", cmaxlon)
print("cminlon: ", cminlon)
print("cmaxlat: ", cmaxlat)
print("cminlat: ", cminlat)
print("MAX CTH: ", np.max(cth_scale[1:cth_nx,1:cth_ny]))
print("MIN CTH: ", np.min(cth_scale[1:cth_nx,1:cth_ny]))

#print cth_qc[30:cth_nx,30:cth_ny]

### DEFINE ARRAYS
n=0
temptb39 = np.zeros(shape=(nx,ny))*np.nan
temptb62 = np.zeros(shape=(nx,ny))*np.nan
temptb69 = np.zeros(shape=(nx,ny))*np.nan
temptb73 = np.zeros(shape=(nx,ny))*np.nan
temptb85 = np.zeros(shape=(nx,ny))*np.nan
temptb96 = np.zeros(shape=(nx,ny))*np.nan
temptb103 = np.zeros(shape=(nx,ny))*np.nan
temptb112 = np.zeros(shape=(nx,ny))*np.nan
temptb123 = np.zeros(shape=(nx,ny))*np.nan
temptb133 = np.zeros(shape=(nx,ny))*np.nan


#### LOOP THROUGH DATA AND SUBSET RADIANCES FOR MODEL DOMAIN
for ii in range(0, len(tb62[:,0])):
    for jj in range(0, len(tb62[0,:])):
        #if ( ((cth_scale[ii,jj] <= 0.0) or (cth_scale[ii,jj] > 25.0)) and (lats[ii,jj] > minlat) and (lats[ii,jj] < maxlat) and (lons[ii,jj] > minlon) and (lons[ii,jj] < maxlon)):
        if ((lats[ii,jj] > minlat) and (lats[ii,jj] < maxlat) and (lons[ii,jj] > minlon) and (lons[ii,jj] < maxlon)):
		    
            temptb39[ii,jj]=tb39[ii,jj]
            temptb62[ii,jj]=tb62[ii,jj]
            temptb69[ii,jj]=tb69[ii,jj]
            temptb73[ii,jj]=tb73[ii,jj]
            temptb85[ii,jj]=tb85[ii,jj]
            temptb96[ii,jj]=tb96[ii,jj]
            temptb103[ii,jj]=tb103[ii,jj]
            temptb112[ii,jj]=tb112[ii,jj]
            temptb123[ii,jj]=tb123[ii,jj]			
            temptb133[ii,jj]=tb133[ii,jj]
			
            n=n+1


#### REFORM DATA TO NEW  GRID
orig_def = pyresample.geometry.SwathDefinition(lons=lons[5:nx,5:ny], lats=lats[5:nx,5:ny])
cth_def = pyresample.geometry.SwathDefinition(lons=cth_lons[5:cth_nx,5:cth_ny], lats=cth_lats[5:cth_nx,5:cth_ny])
targ_def = pyresample.geometry.SwathDefinition(lons=mlon, lats=mlat)

wf = lambda r: 1/r**2


tb39_5km = pyresample.kd_tree.resample_custom(orig_def, temptb39[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)
                          
tb62_5km = pyresample.kd_tree.resample_custom(orig_def, temptb62[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)
                          
tb69_5km = pyresample.kd_tree.resample_custom(orig_def, temptb69[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)

tb73_5km = pyresample.kd_tree.resample_custom(orig_def, temptb73[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)

tb85_5km = pyresample.kd_tree.resample_custom(orig_def, temptb85[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)

tb96_5km = pyresample.kd_tree.resample_custom(orig_def, temptb96[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)
                          
tb103_5km = pyresample.kd_tree.resample_custom(orig_def, temptb103[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)      
                          
tb112_5km = pyresample.kd_tree.resample_custom(orig_def, temptb112[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)    
                          
tb123_5km = pyresample.kd_tree.resample_custom(orig_def, temptb123[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)                                  

tb133_5km = pyresample.kd_tree.resample_custom(orig_def, temptb133[5:nx,5:ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=None)      


cth_5km = pyresample.kd_tree.resample_custom(cth_def, cth_scale[5:cth_nx,5:cth_ny], \
                          targ_def, radius_of_influence=10000, neighbours=10,\
                          weight_funcs=wf, fill_value=0.0)



###### OUTPUT DATA TO NETCDF FILE
tb_out=np.zeros(shape=(10,n)) #(Brightness temperatures, K)
cth_out=np.zeros(shape=(n))
cmask_out = np.zeros(shape=(n)) # 0 = clear; 1=cloud
lat_out=np.zeros(shape=(n))
lon_out=np.zeros(shape=(n))
plat_out=np.zeros(shape=(n))
plon_out=np.zeros(shape=(n))
sza_out=np.zeros(shape=(n)) #solar zenith angle (deg)
vza_out=np.zeros(shape=(n)) # viewing (satellite) zenith angle
solaz_out=np.zeros(shape=(n)) #solar azimuth angle
sataz_out=np.zeros(shape=(n)) #satellite azimuth angle
sca_out=np.zeros(shape=(n)) #scattering angle
raz_out=np.zeros(shape=(n)) #relative azimuth angle

#time_out=np.zeros(shape=(n))
nn=0
rad = pi / 180.0


deg2rad = pi/180.0
rad2deg = 1.0/deg2rad
sat_lon_deg = sat_lon
sat_lat_deg = sat_lat
sat_lat = sat_lat*deg2rad
sat_lon = sat_lon*deg2rad
sat_h = 35785.0       #km
eqr_rad = 6378.137
pol_rad = 6356.7523
rad_rat = (eqr_rad / pol_rad) * (eqr_rad / pol_rad)
sat_lat_m   =   np.arctan(np.tan(sat_lat) / rad_rat)
sat_x       =   sat_h * np.cos(sat_lat_m) * np.cos(sat_lon)
sat_y       =   sat_h * np.cos(sat_lat_m) * np.sin(sat_lon)
sat_z       =   sat_h * np.sin(sat_lat_m)

border_obs_skipped = 0

for ii in range(1, len(tb39_5km[:,0])-2, thin):
    for jj in range(1, len(tb39_5km[0,:])-2, thin):
    
      tlat=mlat[ii,jj]
      tlon=mlon[ii,jj]

      point = LatLon(tlat, tlon)
      if not isenclosedBy(point, inner_domain):
         border_obs_skipped += 1
         continue

    #HALO...remove observations within 5 km of clouds it total COT > 0.1
      #boxcot3=cot_5km[ii-1,jj-1]+cot_5km[ii,jj-1]+cot_5km[ii+1,jj-1]+cot_5km[ii-1,jj]+ \
      #        cot_5km[ii,jj]+cot_5km[ii+1,jj]+cot_5km[ii-1,jj+1]+cot_5km[ii,jj+1]+cot_5km[ii+1,jj+1]
      # 

      if (cth_5km[ii,jj] > 0.01 and cth_5km[ii,jj]/1000. < 25.):
         iscloud=1
      else:
         iscloud=0

      #if ((tb62_5km[ii,jj] > 100.0) and (tb62_5km[ii,jj] < 400.0) ): 
      if ( (tb62_5km[ii,jj] > 100.0) and (tb62_5km[ii,jj] < 400.0) and (iscloud == 0) ):
       #print(ii, jj, cth_5km[ii,jj], tb73_5km[ii,jj])
       lat_out[nn]=mlat[ii,jj]
       lon_out[nn]=mlon[ii,jj]
       #time_out[nn]=time[ii,jj]
    
       tb_out[0,nn]=tb39_5km[ii,jj]
       tb_out[1,nn]=tb62_5km[ii,jj]
       tb_out[2,nn]=tb69_5km[ii,jj]
       tb_out[3,nn]=tb73_5km[ii,jj]              
       tb_out[4,nn]=tb85_5km[ii,jj]
       tb_out[5,nn]=tb96_5km[ii,jj]
       tb_out[6,nn]=tb103_5km[ii,jj]
       tb_out[7,nn]=tb112_5km[ii,jj]
       tb_out[8,nn]=tb123_5km[ii,jj]                           
       tb_out[9,nn]=tb133_5km[ii,jj]
       
       # Calculate angles
       mu = (sin(lat_out[nn]*rad) * sin(declin*rad)) + cos(lat_out[nn]*rad)*cos(declin*rad)*cos(h_ang-lon_out[nn]*rad)
       sza_out[nn] = acos(mu)/rad
       
       beta=acos( cos(lat_out[nn]*rad) * cos((sat_lon_deg - lon_out[nn])*rad) )
       vza_out[nn] = asin(42164.*sin(beta) / sqrt(1.8084e9 - 5.3725e8*cos(beta))) / rad
       
       solaz_out[nn] = (acos( cos((lat_out[nn] - declin)*rad) * cos(h_ang - lon_out[nn]*rad) ))/rad
       
       sataz_out[nn] = (sin((sat_lon_deg - lon_out[nn])*rad) / sin(beta))/rad
       
       raz_out[nn] = (solaz_out[nn] - sataz_out[nn])
       
       cosga = -cos(sza_out[nn]*rad)*cos(vza_out[nn]*rad) - sin(sza_out[nn]*rad)*sin(vza_out[nn]*rad)*sin(raz_out[nn]*rad)
       sca_out[nn] = acos(cosga) / rad
       
       #print lat_out[nn], lon_out[nn], sza_out[nn], vza_out[nn], solaz_out[nn], sataz_out[nn], sca_out[nn]


       # CALCUALTE PARALLAX CORRECTIONS
       plat_out[nn] = lat_out[nn]
       plon_out[nn] = lon_out[nn]
       if (cth_5km[ii,jj] > 0.0001): 
         cmask_out[nn] = 1
         cth_out[nn] = cth_5km[ii,jj]/1000.0 #km
	     
         obs_lat   =   lat_out[nn]*deg2rad
         obs_lon   =   lon_out[nn]*deg2rad
         obs_lat1  =   np.arctan(np.tan(obs_lat) / rad_rat)
         r   = np.sqrt(eqr_rad*eqr_rad*np.cos(obs_lat1)*np.cos(obs_lat1) + \
            pol_rad*pol_rad*np.sin(obs_lat1)*np.sin(obs_lat1))
         #
         omod_x      =   r * np.cos(obs_lat1) * np.cos(obs_lon)
         omod_y      =   r * np.cos(obs_lat1) * np.sin(obs_lon)
         omod_z      =   r * np.sin(obs_lat1)
       
         #print obs_lat, obs_lat1, obs_lon, omod_x, omod_y, omod_z
         #
         ob_mod      =   np.sqrt(omod_x * omod_x+omod_y * omod_y+omod_z * omod_z)
         mod_x       =   sat_x - omod_x
         mod_y       =   sat_y - omod_y
         mod_z       =   sat_z - omod_z
         #
         ax_mod      =   np.sqrt(mod_x*mod_x + mod_y*mod_y + mod_z*mod_z)
         cosbeta     =   -(omod_x*mod_x + omod_y*mod_y + omod_z*mod_z)/(ob_mod*ax_mod)
         aa          =   1.
         bb          =   -2*ob_mod * cosbeta
         cc          =   ob_mod*ob_mod - (ob_mod+cth_out[nn])*(ob_mod+cth_out[nn])
         x           =   (-bb+sqrt(bb*bb-4*aa*cc))/(2*aa)
         axis_x      =   omod_x + (x/ax_mod)*mod_x
         axis_y      =   omod_y + (x/ax_mod)*mod_y
         axis_z      =   omod_z + (x/ax_mod)*mod_z
      
         #print omod_x, omod_y, omod_z, axis_x, axis_y, axis_z, x/ax_mod
      
         #
         new_lat     =   np.arctan(axis_z/np.sqrt((axis_x*axis_x)+(axis_y*axis_y)))
         new_lat     =   np.arctan(np.tan(new_lat)*rad_rat)
         new_lat     =   new_lat * (1./deg2rad)
         #
         new_lon     = np.arctan2(axis_y,axis_x)*(1./deg2rad)

         plat_out[nn] = new_lat 
         plon_out[nn] = new_lon 

         #print lat_out[nn], plat_out[nn],lon_out[nn], plon_out[nn], cth_out[nn]

       nn=nn+1


print(f"\n Number of obs skipped outside domain: {border_obs_skipped}")

## WRITE OBSERVATIONS TO OUTPUT FILE (to be used by read_goesabi_netcdf.f90 in GSI)
if (nn > 10):

  ofile = str(year)+str(month)+str(day)+str(obstime)+"_"+str(osat)+"_TB_CLRSKY.nc"
  outfile = os.path.join(out_dir, ofile)
  #outfile = '/home/Thomas.Jones/GOES16_PROCESS/test_data/tb_obs.nc'
  fout = Dataset(outfile, "w")

  fout.setncattr('satellite', sat)
  fout.setncattr('year', year)
  fout.setncattr('month', month)
  fout.setncattr('day', day)
  fout.setncattr('hour', hour)
  fout.setncattr('minute', minute)
  fout.setncattr('jday', jday)

  fout.createDimension('ntime', 1)
  fout.createDimension('ndate', 5)
  fout.createDimension('nobs', nn)
  fout.createDimension('nchan', 10)

  fout.createVariable('time', 'f8', 'ntime') #seconds since 2000-01-01 12:00:00
  fout.createVariable('date', 'i4', 'ndate') #yyyy, month, day, hour, minute
  #fout.createVariable('jday', 'i4', 'ntime')
  fout.createVariable('sat_lon','f4', 'ntime')
  fout.createVariable('olat', 'f8', 'nobs')
  fout.createVariable('olon', 'f8', 'nobs')
  fout.createVariable('lat', 'f8', 'nobs')
  fout.createVariable('lon', 'f8', 'nobs')
  fout.createVariable('channel', 'f4', 'nchan')

  fout.createVariable('value', 'f8', ('nchan','nobs'))
  fout.createVariable('sza', 'f8', ('nobs'))
  fout.createVariable('vza', 'f8', ('nobs'))
  fout.createVariable('solaz', 'f8', ('nobs'))
  fout.createVariable('sataz', 'f8', ('nobs'))
  fout.createVariable('sca', 'f8', ('nobs'))
  fout.createVariable('raz', 'f8', ('nobs'))
  fout.createVariable('cth', 'f8', ('nobs'))
  fout.createVariable('cloud_mask', 'i4', ('nobs'))

  fout.createVariable('numobs', 'i4', ('ntime'))

  channels=[3.9,6.2,6.9,7.3,8.4,9.6,10.3,11.2,12.3,13.3]
  outdate = [int(year),int(month),int(day),int(hour),int(minute)]

  fout.variables['time'][:] = time
  fout.variables['date'][:] = outdate
  #fout.variables['jday'][:] = int(jday)
  fout.variables['sat_lon'][:] = sat_lon
  fout.variables['olat'][:] = lat_out[0:nn]
  fout.variables['olon'][:] = lon_out[0:nn]
  fout.variables['lat'][:] = plat_out[0:nn]
  fout.variables['lon'][:] = plon_out[0:nn]
  fout.variables['channel'][:] = channels[:]
  fout.variables['value'][:,:] = tb_out[:,0:nn]
  fout.variables['sza'][:] = sza_out[0:nn]
  fout.variables['vza'][:] = vza_out[0:nn]
  fout.variables['solaz'][:] = solaz_out[0:nn]
  fout.variables['sataz'][:] = sataz_out[0:nn]
  fout.variables['sca'][:] = sca_out[0:nn]
  fout.variables['raz'][:] = raz_out[0:nn]
  fout.variables['cth'][:] = cth_out[0:nn]
  fout.variables['cloud_mask'][:] = cmask_out[0:nn]
  fout.variables['numobs'][:] = nn

  fout.close()
  del fout


#wv_plot = web_plot('',                   \
#                   'GOES-16 ABI  Water Vapor (K)',                      \
#                   '',                   \
#                   cb_colors.gray6,      \
#                   wv_levels,            \
#                   pmm_wv_levels,        \
#                   '',                   \
#                   '',                   \
#                   pmm_wv_colors_gray,        \
#                   'none',              \
#                   'none',              \
#                   cb_colors.wv_cmap,              \
#                   'neither',                \
#                   plot_alpha,               \
#                   neighborhood)

#gwlat = wlat[0,edge:-edge,edge:-edge]
#gwlon = wlon[0,edge:-edge,edge:-edge]
#sw_lat_full = gwlat[0,0]
#sw_lon_full = gwlon[0,0]
#ne_lat_full = gwlat[-1,-1]
#ne_lon_full = gwlon[-1,-1]

#map, fig, ax1, ax2, ax3 = create_fig(sw_lat_full, sw_lon_full, ne_lat_full, ne_lon_full, true_lat1, true_lat2, cen_lat, stand_lon, damage_files, resolution, area_thresh)

#x, y = map(lons[:], lats[:])
#xx, yy = map.makegrid(lats.shape[1], lats.shape[0], returnxy=True)[2:4]   #equidistant x/y grid for streamline plots

#dumbvar = np.zeros((lats.shape[0], lats.shape[1]))
#wv_plot.name = 'g16wv'
#wv_plot.var1_title = 'GOES-16 Upper-level Water Vapor (6.9 um) Tb (K)   '
#sat_plot(map, fig, ax1, ax2, ax3, x, y, wv_plot, tb69[:,:], dumbvar[:,:], '0', init_label, valid_label, domain, plotdir, '', '', '', 5, 0, spec='False', quiv='False')



