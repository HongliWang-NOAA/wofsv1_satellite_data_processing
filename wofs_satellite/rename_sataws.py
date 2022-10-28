import sys
import os
import s3fs
import numpy as np
import netCDF4
from netCDF4 import Dataset
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-o", dest="outdir", type="string", help = "Output Directory ")
parser.add_option("-p", dest="prefix", type="string", help = "Prefix")
parser.add_option("-t", dest="date", type="string", help = "date") #YYYYMODDJJJHHMM
parser.add_option("-s", dest="sat", type="string", help = "date")

(options, args) = parser.parse_args()

outdir = options.outdir
dtype = options.prefix
date = options.date
sat = options.sat

year = date[0:4]
month = date[4:6]
day = date[6:8]
jday = date[8:11]
hour = date[11:13]
minute = date[13:15]


print (year, month, day, hour, minute, jday)

# FIND FILES ON AMAZON SERVER
fs = s3fs.S3FileSystem(anon=True)
path = 'noaa-goes'+sat+'/ABI-L2-'+dtype+'/'+year+'/'+jday+'/'+hour+'/'
#files = np.array(fs.ls('noaa-goes17/ABI-L2-ACHAC/2020/200/00/'))
files = np.array(fs.ls(path))
print(files)


# GET NEWEST FILE
fs.get(files[-1], files[-1].split('/')[-1])
infile = files[-1].split('/')[-1]
print(infile)


##################### Process RENAME SAT Files ########################
 
domain=" "

try:							
      fin = netCDF4.Dataset(infile, "r")
      print("Opening %s \n" % infile)
except:
      print("%s does not exist! \n" %infile)
      sys.exit(1)

domain = fin.scene_id
satellite = fin.platform_ID
startdate = fin.time_coverage_start

fin.close()
del fin

syear = startdate[0:4]
smonth = startdate[5:7]
sday = startdate[8:10]
shour = startdate[11:13]
sminute = startdate[14:16]
ssecond = startdate[17:19]
print domain, satellite, startdate
print syear, smonth, sday, shour, sminute, ssecond

#   outfile = outdir+satellite+"_"+domain+"_"+dtype+"_"+date+ssecond+".nc"
outfile = outdir+satellite+"_"+domain+"_"+dtype+"_"+syear+smonth+sday+shour+sminute+ssecond+".nc"
print outfile
cmmd = "mv "+infile+" "+outfile

os.system(cmmd) 

