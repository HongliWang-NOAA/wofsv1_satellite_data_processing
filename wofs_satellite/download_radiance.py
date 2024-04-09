import os, datetime, re
import s3fs
import numpy as np
from itertools import groupby
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
files = np.array(fs.ls(f'noaa-goes{sat}/ABI-L1b-{dtype}/{dt:%Y/%j/%H}/'))

if dt.time() < datetime.time(0, 10):
      yday = dt - datetime.timedelta(hours=1)
      files = np.concatenate((files, np.array(fs.ls(f'noaa-goes{sat}/ABI-L1b-{dtype}/{yday:%Y/%j/%H}/', detail = False, refresh = True))))

print(files)

start = dt - datetime.timedelta(minutes = int(options.range) - 2)
end = dt + datetime.timedelta(minutes = 1)

valid_files = []

for v in files:
      m = re.match('^OR_ABI-L1b-RadC-M6C(?P<chan>\d{2})_G'+sat+'_s(?P<year>\d{4})(?P<day>\d{3})(?P<hour>\d{2})(?P<minute>\d{2})', v.split('/')[-1])
      if m != None:
            d = datetime.datetime.strptime(m.group('year') + "-" + m.group('day') + '-' + m.group('hour') + m.group('minute'), "%Y-%j-%H%M")
            if start <= d and d <= end:
                  valid_files.append((m.group('chan'), d, v))

# group the files by channel
grouped = groupby(sorted(valid_files, key = itemgetter(0)), itemgetter(0))

# then sort within each grouping by date descending and return the first of the list
most_recent_per_channel = [next(iter(sorted(data, key = itemgetter(1), reverse = True)))    for (key, data) in grouped]

# most_recent_per_channel = [
#       ( '02', 0, 'OR_ABI-L1b-RadC-M6C02_G16_s20240682001172_e20240682003545_c20240682003580.nc'),
#       ( '07', 0, 'OR_ABI-L1b-RadC-M6C07_G16_s20240682001172_e20240682003556_c20240682003594.nc'),
#       ( '08', 0, 'OR_ABI-L1b-RadC-M6C08_G16_s20240682001172_e20240682003545_c20240682004021.nc'),
#       ( '09', 0, 'OR_ABI-L1b-RadC-M6C09_G16_s20240682001172_e20240682003551_c20240682004030.nc'),
#       ( '10', 0, 'OR_ABI-L1b-RadC-M6C10_G16_s20240682001172_e20240682003556_c20240682004016.nc'),
#       ( '11', 0, 'OR_ABI-L1b-RadC-M6C11_G16_s20240682001172_e20240682003544_c20240682004005.nc'),
#       ( '12', 0, 'OR_ABI-L1b-RadC-M6C12_G16_s20240682001172_e20240682003551_c20240682004001.nc'),
#       ( '13', 0, 'OR_ABI-L1b-RadC-M6C13_G16_s20240682001172_e20240682003557_c20240682004033.nc'),
#       ( '14', 0, 'OR_ABI-L1b-RadC-M6C14_G16_s20240682001172_e20240682003545_c20240682004036.nc'),
#       ( '15', 0, 'OR_ABI-L1b-RadC-M6C15_G16_s20240682001172_e20240682003550_c20240682004010.nc'),
#       ( '16', 0, 'OR_ABI-L1b-RadC-M6C16_G16_s20240682001172_e20240682003556_c20240682004027.nc')
# ]

for (chan, time, file) in most_recent_per_channel:
      c = int(chan)
      if c == 2 or (7 <= c and c <= 16):
            local_file = file.split('/')[-1]
            print(local_file)
            fs.get(file, local_file)
            os.system("mv "+local_file+" "+os.path.join(outdir, f'ch{chan}_TB.nc'))

