import sys, datetime, re
import os
import s3fs
import numpy as np
import netCDF4
from netCDF4 import Dataset
from operator import itemgetter
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-o", dest="outdir", type="string", help = "Output Directory ")
parser.add_option("-p", dest="prefix", type="string", help = "Prefix")
parser.add_option("-t", dest="date", type="string", help = "date") #YYYYMODDHHMM
parser.add_option("-s", dest="sat", type="string", help = "date")
parser.add_option("-r", "--range", dest="range", default = 5)

(options, args) = parser.parse_args()

outdir = options.outdir
dtype = options.prefix
date = options.date
sat = options.sat

dt = datetime.datetime.strptime(options.date, "%Y%m%d%H%M")

# FIND FILES ON AMAZON SERVER
fs = s3fs.S3FileSystem(anon=True)
# today
files = np.array(fs.ls(f'noaa-goes{sat}/ABI-L2-{dtype}/{dt:%Y/%j/%H}/'))

if dt.time() < datetime.time(0, 10):
      yday = dt - datetime.timedelta(hours=1)
      files = np.concatenate((files, np.array(fs.ls(f'noaa-goes{sat}/ABI-L2-{dtype}/{yday:%Y/%j/%H}/', detail = False, refresh = True))))

print(files)

start = dt - datetime.timedelta(minutes = int(options.range) - 2)
end = dt + datetime.timedelta(minutes = 1)

valid_files = []

for v in files:
      m = re.match('^OR_ABI-L2-ACHAC-M6_G'+sat+'_s(?P<year>\d{4})(?P<day>\d{3})(?P<hour>\d{2})(?P<minute>\d{2})', v.split('/')[-1])
      if m != None:
            d = datetime.datetime.strptime(m.group('year') + "-" + m.group('day') + '-' + m.group('hour') + m.group('minute'), "%Y-%j-%H%M")
            if start <= d and d <= end:
                  valid_files.append((d, v))

# sort the files
sorted_files = sorted(valid_files, key = itemgetter(0), reverse = True)

# top (most recent within time block) to download
file_to_download = next(iter(sorted_files))[1]
local_file = file_to_download.split('/')[-1]

# GET NEWEST FILE
fs.get(file_to_download, local_file)
print(local_file)

##################### Process RENAME SAT Files ########################
 
domain=" "

try:							
      fin = netCDF4.Dataset(local_file, "r")
      print("Opening %s \n" % local_file)
except:
      print("%s does not exist! \n" %local_file)
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
print(domain, satellite, startdate)
print(syear, smonth, sday, shour, sminute, ssecond)

#   outfile = outdir+satellite+"_"+domain+"_"+dtype+"_"+date+ssecond+".nc"
outfile = outdir+satellite+"_"+domain+"_"+dtype+"_"+syear+smonth+sday+shour+sminute+ssecond+".nc"
print(outfile)
cmmd = "mv "+local_file+" "+os.path.join(outdir, "cth.nc")

os.system(cmmd) 

