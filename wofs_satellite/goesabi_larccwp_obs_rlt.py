######## GENERATE GOES-R CWP OBSERVATIONS
##   USE NASA LARC RETRIAVAL FILES (both special WoF files and standard RR files)
##   APPLY PARALLAX CORRECTION
##   OUTPUT OBSERVATIONS IN 1-D NETCDF FORMAT
##   
##   By: 			Thomas A. Jones
##	 Create Date:	September 5, 2018
##	 Version 		1.3
##	 Modified:      December 1, 2022: Bug fixes and modifications for cloud running
########################################

# CONUS
import sys
import os
from netCDF4 import Dataset
import numpy as np
from pyproj import Proj
import pyresample
from news_e_post_cbook import *
from datetime import *
from math import pi, cos, sqrt
from optparse import OptionParser

from pygeodesy.sphericalNvector import LatLon
from pygeodesy.points import isenclosedBy

####################################### Parse Options: ######################################################

parser = OptionParser()
parser.add_option("-d", dest="cwp_dir", type="string", default= None, help="Input Directory of NASA LARC files")
#parser.add_option("-m", dest="mrms_dir", type="string", help = "Path to dummy MRMS grid file")
parser.add_option("-w", dest="wrf_dir", type="string", help = "Path to wrfinput_d01 file domain info")
parser.add_option("-o", dest="out_dir", type="string", help = "Output Directory observation file")
parser.add_option("-a", dest="observation_time", type="string", help = "Time at which obs are to be assimialted")
parser.add_option("-t", dest="thin", type="int", help = "Thinning Number")
parser.add_option("-s", dest="sat", type="string", help = "Satellite G16, G17")
(options, args) = parser.parse_args()

cwp_dir = options.cwp_dir
#mrms_dir = options.mrms_dir
wrf_dir = options.wrf_dir
out_dir = options.out_dir
obstime = options.observation_time
cwp_clear_thin = options.thin
sat = options.sat

# GRID SPACING
gspace = 0.05 #5 km
gspace_m = 5000

_domain_gridpoint_margin = 7

# MIN THRESHOLDS
lwp_min = 0.05
lwp_min2 = 0.015
iwp_min = 0.05

# DEFINE CONSTANTS
deg2rad = pi/180.0
rad2deg = 1.0/deg2rad
sat_lat = 0.02 * deg2rad
if ( sat  == 'G16'):
   sat_lon = -75.18 * deg2rad  #G16
   p = Proj(proj='geos', h='35786023.0', lon_0=sat_lon*rad2deg, sweep='x')
   osat = 'GOES16'
if ( sat == 'G17'):
   sat_lon = -137.2 * deg2rad  #G17
   p = Proj(proj='geos', h='35786023.0', lon_0=sat_lon*rad2deg, sweep='x')
   osat = 'GOES17'
if ( sat == 'G18'):
   sat_lon = -137.2 * deg2rad  #G17
   p = Proj(proj='geos', h='35786023.0', lon_0=sat_lon*rad2deg, sweep='x')
   osat = 'GOES18'


sat_h = 35786.023       #km
eqr_rad = 6378.137
pol_rad = 6356.7523

rad_rat = (eqr_rad / pol_rad) * (eqr_rad / pol_rad)
sat_lat_m   =   np.arctan(np.tan(sat_lat) / rad_rat)
sat_x       =   sat_h * np.cos(sat_lat_m) * np.cos(sat_lon)
sat_y       =   sat_h * np.cos(sat_lat_m) * np.sin(sat_lon)
sat_z       =   sat_h * np.sin(sat_lat_m)


# DEFINE PROJECTION FOR GOES-east
#p = Proj(proj='geos', h='35786023.0', lon_0='-75.18', sweep='x')

# INPUT FILES
cwpfile = os.path.join(cwp_dir, 'cwp_larc.nc')
wrffile = wrf_dir
#wrffile = os.path.join(wrf_dir, 'wrfinput_d02.1')
#mrmsfile = os.path.join(mrms_dir, 'dummy_mrmsgoesabi.nc')
#mrmsfile = os.path.join(mrms_dir, 'dummy_mrmsgoes16.nc')

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


# CREATE 5 km SMOOTHED GRID
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


# READ IN INFORMATION FROM LARC RETRIAVAL FILE
cwpin = Dataset(cwpfile, "r")
domain = cwpin.Domain_Processed

# TIME
basetime = cwpin.variables['base_time'][:]
timeoffset = cwpin.variables['time_offset'][:]

print(basetime, timeoffset)

dttme=datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S') + timedelta(seconds=basetime+timeoffset)
year=datetime.strftime(dttme, "%Y")
month=datetime.strftime(dttme, "%m")
day=datetime.strftime(dttme, "%d")
hour=datetime.strftime(dttme, "%H")
minute=datetime.strftime(dttme, "%M")
jday=datetime.strftime(dttme, "%j")

print(year, month, day, hour, minute)

angletime=int(hour) + int(minute)/60.0
h_ang = -1.0*pi*(angletime - 12.0)/12.0
declin = -23.45*cos(float(jday)*2 * pi/365.0 + 10.*2. * pi/365.0)


# LOCATION
clat = cwpin.variables["latitude"][:,:]
clon = cwpin.variables["longitude"][:,:]

maxlat_cwp = np.max(clat)
minlat_cwp = np.min(clat)
maxlon_cwp = np.max(clon)
minlon_cwp = np.min(clon)

print("maxlon_cwp: ", maxlon_cwp)
print("minlon_cwp: ", minlon_cwp)
print("maxlat_cwp: ", maxlat_cwp)
print("minlat_cwp: ", minlat_cwp)

# DIMS
xxx = cwpin.variables["image_x"][:]
yyy = cwpin.variables["image_y"][:]

ny = len(xxx[:])
nx = len(yyy[:])

#**** READ IN 2-D CWP (g/m2)
cwp = cwpin.variables['cloud_lwp_iwp'][:,:]

#**** READ IN 2-D PHASE
phase = cwpin.variables['cloud_phase'][:,:]
		#cloud_phase:value_0 = "snow" ;
		#cloud_phase:value_1 = "water cloud" ;
		#cloud_phase:value_2 = "ice cloud" ;
		#cloud_phase:value_3 = "no retrieval" ;
		#cloud_phase:value_4 = "clear" ;
		#cloud_phase:value_5 = "bad data" ;              DO NOT USE
		#cloud_phase:value_6 = "suspected water cloud" ; DO NOT USE
		#cloud_phase:value_7 = "suspected ice cloud" ;   DO NOT USE
                #cloud_phase:value_13 = "cleaned data" ; ????

#**** READ IN 2-D CTH (km)
cth = cwpin.variables['cloud_top_height'][:,:]

#**** READ IN 2-D CTP (hPA)
ctp = cwpin.variables['cloud_top_pressure'][:,:]

#**** READ IN 2-D CBP
cbp = cwpin.variables['cloud_bottom_pressure'][:,:]

#**** READ IN 2-D CEP, middle of cloud, use as LWP/IWP vertical coord
cep = cwpin.variables['cloud_effective_pressure'][:,:]

#**** READ IN 2-D COT
cot = cwpin.variables['cloud_visible_optical_depth'][:,:]

#**** READ IN 2-D IR (K)
ir112 = cwpin.variables['temperature_ir'][:,:]

#**** READ IN SZA (deg)
sza = cwpin.variables['pixel_sza'][:,:]

#**** READ IN VZA
vza = cwpin.variables['pixel_vza'][:,:]

#**** READ IN AZA
aza = cwpin.variables['pixel_aza'][:,:]


adjcwp  = np.zeros(shape=(nx,ny))*np.nan

#### APPLY PARALLAX CORRECTION
plat = np.zeros(shape=(nx,ny))*np.nan
plon = np.zeros(shape=(nx,ny))*np.nan

#### SEPERATE IWP / LWP VARIABLES
newiwp = np.zeros(shape=(nx,ny))*0.0
newlwp = np.zeros(shape=(nx,ny))*0.0
newclear = np.zeros(shape=(nx,ny))*9999.

#output1 = open("test1.txt", "w+")
qq=0

#print len(cot[:,0]), len(cot[0,:])
print(np.min(cwp[:,:])/1000.0, np.max(cwp[:,:])/1000.0 )
print(np.min(phase[:,:]), np.max(phase[:,:]) )
ii=0
jj=0
qq=0
for ii in range(0, len(cot[:,0])-1):
    for jj in range(0, len(cot[0,:])-1):
      if ( (clat[ii,jj] > minlat) and ( clat[ii,jj] < maxlat) and (clon[ii,jj] > minlon) and ( clon[ii,jj] < maxlon) ) :
     
       plon[ii,jj] = clon[ii,jj]
       plat[ii,jj] = clat[ii,jj]
       adjcwp[ii,jj] = cwp[ii,jj]
       
       obs_cth   =   cth[ii,jj] 
       obs_lat   =   clat[ii,jj]*deg2rad
       obs_lon   =   clon[ii,jj]*deg2rad
       obs_lat1  =   np.arctan(np.tan(obs_lat) / rad_rat)
       re = np.sqrt(eqr_rad*eqr_rad*np.cos(obs_lat1)*np.cos(obs_lat1) + \
            pol_rad*pol_rad*np.sin(obs_lat1)*np.sin(obs_lat1))
    
       omod_x      =   re * np.cos(obs_lat1) * np.cos(obs_lon)
       omod_y      =   re * np.cos(obs_lat1) * np.sin(obs_lon)
       omod_z      =   re * np.sin(obs_lat1)

       #if (cth[ii,jj] > 2.0 and (clat[ii,jj] > 30) and (clat[ii,jj] < 40)):
       #  print obs_lat, obs_lat1, obs_lon, omod_x, omod_y, omod_z
 
       ob_mod      =   np.sqrt(omod_x * omod_x+omod_y * omod_y+omod_z * omod_z)
       mod_x       =   sat_x - omod_x
       mod_y       =   sat_y - omod_y
       mod_z       =   sat_z - omod_z

       ax_mod      =   np.sqrt(mod_x*mod_x + mod_y*mod_y + mod_z*mod_z)
       cosbeta     =   -(omod_x*mod_x + omod_y*mod_y + omod_z*mod_z)/(ob_mod*ax_mod)
       aa          =   1.
       bb          =   -2*ob_mod * cosbeta
       cc          =   ob_mod*ob_mod - (ob_mod+obs_cth)*(ob_mod+obs_cth)
       x           =   (-bb+sqrt(bb*bb-4*aa*cc))/(2*aa)
       axis_x      =   omod_x + (x/ax_mod)*mod_x
       axis_y      =   omod_y + (x/ax_mod)*mod_y
       axis_z      =   omod_z + (x/ax_mod)*mod_z

       new_lat     =   np.arctan(axis_z/np.sqrt((axis_x*axis_x)+(axis_y*axis_y)))
       new_lat     =   np.arctan(np.tan(new_lat)*rad_rat)
       new_lat     =   new_lat * (1./deg2rad)
         
       new_lon     =   np.arctan2(axis_y,axis_x)*(1./deg2rad)
        
       plat[ii,jj]     = new_lat
       plon[ii,jj]     = new_lon

       # WHILE WE ARE HERE, DO HIGH CWP ADJUSTMENT
       if ( (ir112[ii,jj] < 240.0) and (cot[ii,jj] > 8.0) and (phase[ii,jj] == 2) ):
         templwp=( 4.7*(cot[ii,jj]**1.1) )  
         tempiwp=( 0.305*(cwp[ii,jj]**1.194) )  
         adjcwp[ii,jj] = templwp + tempiwp
         #print cwp[ii,jj], adjcwp[ii,jj], templwp, tempiwp
       #else :
       #  adjcwp[ii,jj] = cwp[ii,jj]

       # ALSO WHILE WE ARE HERE, GENERATE SEPARATE ARRAYS FOR IWP AND LWP FIELDS
       if ( (phase[ii,jj] == 1) and (adjcwp[ii,jj] > 0.03) ): 
          #newlwp[ii,jj] = adjcwp[ii,jj]
          newlwp[ii,jj] = cwp[ii,jj]  # LWP never adjusted

       if ( (phase[ii,jj] == 2) and (adjcwp[ii,jj] > 0.03) ): 
          #newiwp[ii,jj] = adjcwp[ii,jj]
          newiwp[ii,jj] = cwp[ii,jj]
 
       #if ( (phase[ii,jj] == 6) and (adjcwp[ii,jj] > 0.03) ):
          #newlwp[ii,jj] = adjcwp[ii,jj]
       #   newlwp[ii,jj] = cwp[ii,jj]  # LWP never adjusted

       if ( (phase[ii,jj] == 7) and (adjcwp[ii,jj] > 0.03) ):
          #newiwp[ii,jj] = adjcwp[ii,jj]
          newiwp[ii,jj] = cwp[ii,jj]


       # CLEAR STUFF
       if ( (phase[ii,jj] == 4) or (phase[ii,jj] == 3) or (phase[ii,jj] == 0) ): 
           adjcwp[ii,jj] = 0.0
           cwp[ii,jj] = 0.0
       if ( adjcwp[ii,jj] < lwp_min2 ): 
           adjcwp[ii,jj] = 0.0
           cwp[ii,jj] = 0.0
      
       # BAD DATA
       if ( (phase[ii,jj] == 5) or (phase[ii,jj] == 6) ):
           adjcwp[ii,jj] = np.nan
           cwp[ii,jj] = np.nan
           newiwp[ii,jj] = np.nan
           newlwp[ii,jj] = np.nan
           sza[ii,jj] = np.nan
           ctp[ii,jj] = np.nan

       qq=qq+1

       #if (cth[ii,jj] > 1.0 ):
       #   output1.write("%10.3f %10.3f %10.3f %10.3f %10.3f %10.3f \n" % (qq*1.0,clat[ii,jj],plat[ii,jj],clon[ii,jj],plon[ii,jj],cth[ii,jj] ) )

#output1.close()

#### 

#### REFORM DATA ON TO 5 KM MRMS GRID
orig_def = pyresample.geometry.SwathDefinition(lons=plon[0:nx,0:ny], lats=plat[0:nx,0:ny])
targ_def = pyresample.geometry.SwathDefinition(lons=mlon, lats=mlat)
wf = lambda r: 1 - r/20000.0


cwp_5km = pyresample.kd_tree.resample_custom(orig_def, cwp[0:nx,0:ny], \
                          targ_def, radius_of_influence=15000, neighbours=12,\
                          weight_funcs=wf, fill_value=0.0)                         
                          
lwp_5km = pyresample.kd_tree.resample_custom(orig_def, newlwp[0:nx,0:ny], \
                          targ_def, radius_of_influence=15000, neighbours=12,\
                          weight_funcs=wf, fill_value=None)
                          
iwp_5km = pyresample.kd_tree.resample_custom(orig_def, newiwp[0:nx,0:ny], \
                          targ_def, radius_of_influence=15000, neighbours=12,\
                          weight_funcs=wf, fill_value=None)
                          
ctp_5km = pyresample.kd_tree.resample_custom(orig_def, ctp[0:nx,0:ny], \
                          targ_def, radius_of_influence=15000, neighbours=12,\
                          weight_funcs=wf, fill_value=None)
                                                    
cbp_5km = pyresample.kd_tree.resample_custom(orig_def, cbp[0:nx,0:ny], \
                          targ_def, radius_of_influence=15000, neighbours=12,\
                          weight_funcs=wf, fill_value=None) 
                          
cep_5km = pyresample.kd_tree.resample_custom(orig_def, cep[0:nx,0:ny], \
                          targ_def, radius_of_influence=15000, neighbours=12,\
                          weight_funcs=wf, fill_value=None)                                         
                          
clear_5km = pyresample.kd_tree.resample_custom(orig_def, newclear[0:nx,0:ny], \
                          targ_def, radius_of_influence=15000, neighbours=12,\
                          weight_funcs=wf, fill_value=0.0)  
                          
sza_5km = pyresample.kd_tree.resample_custom(orig_def, sza[0:nx,0:ny], \
                          targ_def, radius_of_influence=15000, neighbours=12,\
                          weight_funcs=wf, fill_value=0.0)                        



print(np.max(newiwp)/1000.0, np.max(iwp_5km)/1000.0)
print(np.max(newlwp)/1000.0, np.max(lwp_5km)/1000.0)
print(np.min(newiwp)/1000.0, np.min(iwp_5km)/1000.0)
print(np.min(newlwp)/1000.0, np.min(lwp_5km)/1000.0)
print(np.max(cwp)/1000.0, np.max(cwp_5km)/1000.0)
print(np.min(cwp)/1000.0, np.min(cwp_5km)/1000.0)
#print(np.max(newclear), np.max(clear_5km))
#print(np.min(newclear), np.min(clear_5km))
print(np.max(ctp), np.max(ctp_5km))
print(np.min(ctp), np.min(ctp_5km))
print(np.max(sza), np.max(sza_5km))


#mlats = mlat[:,0]
#mlons = mlon[0,:]

mlats = mlat[0,:]
mlons = mlon[:,0]

index  = (mlats > minlat ) & (mlats < maxlat)
bbindex = np.arange(mlats.size)[index]
index  = (mlons > minlon ) & (mlons < maxlon)
aaindex = np.arange(mlons.size)[index]


##### MAKE OBSERVATIONS TO ASSIMILATE AND ADD OBS ERRORS
# set counters
count       = 0
count_cwp0  = 0
count_lwp0  = 0
count_lwp   = 0
count_iwp   = 0
count_cwp0_ngt  = 0
count_lwp0_ngt  = 0
count_lwp_ngt   = 0
count_iwp_ngt   = 0

nmax_cloud=250000
cc=0
cwp_out=np.zeros(shape=(nmax_cloud))*np.nan
ctp_out=np.zeros(shape=(nmax_cloud))*np.nan
cbp_out=np.zeros(shape=(nmax_cloud))*np.nan
cep_out=np.zeros(shape=(nmax_cloud))*np.nan
cwp_lat=np.zeros(shape=(nmax_cloud))*np.nan
cwp_lon=np.zeros(shape=(nmax_cloud))*np.nan
cwp_err=np.zeros(shape=(nmax_cloud))*np.nan
cwp_phase=np.zeros(shape=(nmax_cloud))*np.nan  #0=CWP0, 1=LWP, 2=IWP, 3=CWP0_NGT, 4=LWP_NGT, 5=IWP_NGT
										#6=LWP0, 7=LWP_NGT0
cwp_phase[:] = -999
cwp_stddev0 = 0.0225    #DEFAULT CWP OBS ERROR

border_obs_skipped = 0

thin=1  #FOR NOW, DON'T THIN ALL OBS
for aa in range(1, len(sza_5km[:,0])-2, thin):
     for bb in range(1, len(sza_5km[0,:])-2, thin):
      tlat=mlat[aa,bb]
      tlon=mlon[aa,bb]

      point = LatLon(tlat, tlon)
      if not isenclosedBy(point, inner_domain):
         border_obs_skipped += 1
         continue

      if (tlat > minlat and tlat < maxlat and tlat > minlat_cwp and tlat < maxlat_cwp and \
          tlon > minlon and tlon < maxlon and tlon > minlon_cwp and tlon < maxlon_cwp):
       szatemp = sza_5km[aa,bb]
       cleartemp = clear_5km[aa,bb]
       #cottemp = cot_5km[aa,bb]
       cwptemp = cwp_5km[aa,bb] / 1000.0
       lwptemp = lwp_5km[aa,bb] / 1000.0
       iwptemp = iwp_5km[aa,bb] / 1000.0
       ceptemp = cep_5km[aa,bb]
       ctptemp = ctp_5km[aa,bb] 
       cbptemp = cbp_5km[aa,bb]


       #*** CORRECT CBP FOR CONVECTION. RETRIEVAL SATURATED, NEED TO LOWER CBP
       if (ctptemp < 200.0 and cbptemp < 500.0 and cwptemp > 1.5 ) :
        cbptemp=900.0
        ceptemp=500.0


      # BASELINE OBSERVATION ERROR 2018+
      # cwp_stddev = 0.0225
       cwp_stddev = cwp_stddev0   #2023

       #### DAYTIME CWP = 0
       sat_zeros = 0
       if (( cwptemp <= lwp_min2) and (szatemp < 81.0) and (szatemp >= 0.0) ) :
            sat_zeros = (aa % cwp_clear_thin) + (bb % cwp_clear_thin) #thin cwp=0 observations

            if sat_zeros == 0: 
              cwp_out[cc] = 0.0
              cep_out[cc] = 500.0  #pressure height of CWP retrieval
              ctp_out[cc] = -999.9
              cbp_out[cc] = 9999.9
              cwp_phase[cc] = 0
              cwp_lon[cc] = mlon[aa,bb]
              cwp_lat[cc] = mlat[aa,bb]
              cwp_err[cc] = cwp_stddev0
              cc=cc+1
              count_cwp0 += 1

       #if ( lat < 40.5 and lat > 39.5 ) :
       #  if (lon < -99.0 ) :
             #if ( cwptemp > 50. ):
       #      print "MISSING CLEAR", cc,cwptemp, cleartemp, lon, lat, szatemp

       #LWP
       if ((lwptemp > lwp_min) and (szatemp < 81.0) and (szatemp > 0.0) and (iwptemp < iwp_min) ):
            cwp_out[cc] = lwptemp
            cep_out[cc] = ceptemp
            ctp_out[cc] = ctptemp
            cbp_out[cc] = cbptemp             
            cwp_phase[cc] = 1  
            cwp_lon[cc] = mlon[aa,bb]
            cwp_lat[cc] = mlat[aa,bb]  
            
            if lwptemp >= 0.025 and lwptemp < 0.18:
               cwp_stddev = 0.05
            if lwptemp >= 0.18 and lwptemp < 2.0:
               cwp_stddev = lwptemp * 0.35
            if lwptemp >= 2.0:
               cwp_stddev = 0.75
      
            cwp_err[cc] = cwp_stddev 
            cc=cc+1             
            count_lwp += 1
            #print cwptemp, szatemp, phasetemp
            
       # INSERT ZEROS ABOVE LOW LEVEL CLOUDS
#       if ((lwptemp > lwp_min) and (szatemp < 81.0) and (szatemp > 0.0) and (ctptemp < 700.) ):     
#           sat_zeros = (aa % cwp_clear_thin) + (bb % cwp_clear_thin)        

#           if sat_zeros == 0: 
#             cwp_out[cc] = 0.0
#             cep_out[cc] = 300.0  #pressure height of CWP retrieval
#             ctp_out[cc] = -999.9
#             cbp_out[cc] = 9999.9
#             cwp_phase[cc] = 6
#             cwp_lon[cc] = mlon[aa,bb]
#             cwp_lat[cc] = mlat[aa,bb] 
#             cwp_err[cc] = cwp_stddev0
#             cc=cc+1
#             count_lwp0 += 1     

       #IWP (for obs purposes, CWP = IWP)
       if ((iwptemp > iwp_min) and (szatemp < 81.0) and (szatemp > 0.0) ) :
            cwp_out[cc] = cwptemp
            cep_out[cc] = ceptemp
            ctp_out[cc] = ctptemp
            cbp_out[cc] = cbptemp      
            cwp_phase[cc] = 2 
            cwp_lon[cc] = mlon[aa,bb]
            cwp_lat[cc] = mlat[aa,bb]  
            if cwptemp >= 0.025 and cwptemp < 0.18:
               cwp_stddev = 0.05
            if iwptemp >= 0.18 and cwptemp < 2.0:
               cwp_stddev = cwptemp * 0.35
            if cwptemp >= 2.0:
               cwp_stddev = 0.75
		       
            cwp_err[cc] = cwp_stddev 
            cc=cc+1                   
            count_iwp += 1
            #print cwptemp, szatemp, phasetemp

       #### NIGHT TIME RETRIEVALS
       if ((cwptemp <= lwp_min2) and (szatemp >= 82.0) and (szatemp > 0.0) and (iwptemp < iwp_min)) :
            night_zeros = (aa % cwp_clear_thin) + (bb % cwp_clear_thin)        

            if night_zeros == 0: 
              cwp_out[cc] = 0.0
              cep_out[cc] = 500.0  #pressure height of CWP retrieval
              ctp_out[cc] = -999.9
              cbp_out[cc] = 9999.9
              cwp_phase[cc] = 3
              cwp_lon[cc] = mlon[aa,bb]
              cwp_lat[cc] = mlat[aa,bb] 
              cwp_err[cc] = cwp_stddev0         
              cc=cc+1
              count_cwp0_ngt += 1

       # LWP
       if ((lwptemp > lwp_min) and (szatemp >= 82.0) and (szatemp > 0.0) ):
            cwp_out[cc] = lwptemp
            cep_out[cc] = ceptemp
            ctp_out[cc] = ctptemp
            cbp_out[cc] = cbptemp      
            cwp_phase[cc] = 4  
            cwp_lon[cc] = mlon[aa,bb]
            cwp_lat[cc] = mlat[aa,bb] 
            if lwptemp >= 0.025 and lwptemp < 0.18:
               cwp_stddev = 0.05
            if lwptemp >= 0.18 and lwptemp < 2.0:
               cwp_stddev = lwptemp * 0.35
            if lwptemp >= 2.0:
               cwp_stddev = 0.75 
		       
            cwp_err[cc] = cwp_stddev                
            cc=cc+1             
            count_lwp_ngt += 1

       # INSERT ZEROS ABOVE LOW LEVEL CLOUDS
#       if ((lwptemp > lwp_min) and (szatemp >= 82.0) and (szatemp > 0.0) and (ctptemp < 700.) ):  
#           night_zeros = (aa % cwp_clear_thin) + (bb % cwp_clear_thin)        

#           if night_zeros == 0:    
#             cwp_out[cc] = 0.0
#             cep_out[cc] = 300.0  #pressure height of CWP retrieval
#             ctp_out[cc] = -999.9
#             cbp_out[cc] = 9999.9
#             cwp_phase[cc] = 7
#             cwp_lon[cc] = mlon[aa,bb]
#             cwp_lat[cc] = mlat[aa,bb] 
#             cwp_err[cc] = 0.0225
#             cc=cc+1
#             count_lwp0_ngt += 1     

       # IWP
       if ((iwptemp > iwp_min)  and (szatemp >= 82.0) and (szatemp > 0.0) ) :
            cwp_out[cc] = cwptemp
            cep_out[cc] = ceptemp
            ctp_out[cc] = ctptemp
            cbp_out[cc] = cbptemp      
            cwp_phase[cc] = 5
            cwp_lon[cc] = mlon[aa,bb]
            cwp_lat[cc] = mlat[aa,bb]  
            if cwptemp >= 0.025 and cwptemp < 0.18:
               cwp_stddev = 0.05
            if iwptemp >= 0.18 and cwptemp < 2.0:
               cwp_stddev = cwptemp * 0.35
            if iwptemp >= 2.0:
               cwp_stddev = 0.75
            cwp_err[cc] = cwp_stddev               
            cc=cc+1                   
            count_iwp_ngt += 1



print(f"\n Number of obs skipped outside domain: {border_obs_skipped}")
print("\n >%s<" % ("=" * 79))
print("\n  PyDart.CWP->  Total number of OBSs:     %d" % cc)
print("\n  PyDart.CWP->  Total number of LWP:           %d" % count_lwp)
print("\n  PyDart.CWP->  Total number of LWP0:          %d" % count_lwp0)
print("\n  PyDart.CWP->  Total number of IWP:           %d" % count_iwp)
#print("\n  PyDart.CWP->  Total number of CWP:           %d" % cc)
print("\n  PyDart.CWP->  Total number of CWP_ZER0:      %d" % count_cwp0) 
print("\n  PyDart.CWP->  Total number of LWP NIGHTTIME: %d" % count_lwp_ngt)
print("\n  PyDart.CWP->  Total number of LWP0 NIGHTTIME: %d" % count_lwp0_ngt)
print("\n  PyDart.CWP->  Total number of IWP NIGHTTIME: %d" % count_iwp_ngt)
print("\n  PyDart.CWP->  Total number of CWP_ZER0 NIGHT: %d" % count_cwp0_ngt)                         
print("\n >%s<" % ("=" * 79))



#OUTPUT CWP OBSERVATIONS (netcdf)
if (cc > 1):

  osatfile = str(year)+str(month)+str(day)+str(hour)+str(minute)+"_"+str(osat)+"_CWP_OBS.nc"
  satoutfile = os.path.join(out_dir, osatfile)
  #outfile = '/home/Thomas.Jones/GOES16_PROCESS/test_data/tb_obs.nc'
  sout = Dataset(satoutfile, "w")

  sout.setncattr('satellite', sat)
  sout.setncattr('year', year)
  sout.setncattr('month', month)
  sout.setncattr('day', day)
  sout.setncattr('hour', hour)
  sout.setncattr('minute', minute)
  #sout.setncattr('second', ssec)
  sout.setncattr('jday', jday)

  sout.createDimension('ntime', 1)
  sout.createDimension('nobs', cc)

  sout.createVariable('time', 'f8', 'ntime') #seconds since 1970-01-01 00:00:00
  sout.createVariable('numobs', 'f8', 'ntime')
  sout.createVariable('lat', 'f8', 'nobs')
  sout.createVariable('lon', 'f8', 'nobs')
  sout.createVariable('pressure', 'f8', 'nobs')

  sout.createVariable('cwp', 'f8', ('nobs'))
  sout.createVariable('ctp', 'f8', ('nobs'))
  sout.createVariable('cbp', 'f8', ('nobs'))
  sout.createVariable('phase', 'i4', ('nobs'))
  sout.createVariable('cwp_err', 'f8', ('nobs'))

  sout.variables['time'][:] = basetime+timeoffset
  sout.variables['lat'][:] = cwp_lat[0:cc]
  sout.variables['lon'][:] = cwp_lon[0:cc]
  sout.variables['pressure'][:] = cep_out[0:cc]
  sout.variables['cwp'][:] = cwp_out[0:cc]
  sout.variables['ctp'][:] = ctp_out[0:cc]
  sout.variables['cbp'][:] = cbp_out[0:cc]
  sout.variables['phase'][:] = cwp_phase[0:cc]
  sout.variables['cwp_err'][:] = cwp_err[0:cc]

  sout.variables['numobs'][:] = cc

  sout.close()
  del sout
