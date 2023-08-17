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
path = 'noaa-goes'+sat+'/ABI-L1b-'+dtype+'/'+f'{dt:%Y/%j/%H}'+'/'
files = np.array(fs.ls(path))
print(files)

start = dt - datetime.timedelta(minutes = int(options.range) - 2)
end = dt + datetime.timedelta(minutes = 1)

valid_files = []

for v in files:
      m = re.match('^OR_ABI-L1b-RadC-M6C(?P<chan>\d{2})_G'+sat+'_s(?P<year>\d{4})(?P<day>\d{3})(?P<hour>\d{2})(?P<minute>\d{2})', v.split('/')[-1])
      if m != None:
            d = datetime.datetime.strptime(m.group('year') + "-" + m.group('day') + '-' + m.group('hour') + m.group('minute'), "%Y-%j-%H%M")
            if start <= d and d <= end:
                  valid_files.append((m.group('chan'), d, v.split('/')[-1]))

# group the files by channel
grouped = groupby(sorted(valid_files, key = itemgetter(0)), itemgetter(0))

# then sort within each grouping by date descending and return the first of the list
most_recent_per_channel = [next(iter(sorted(data, key = itemgetter(1), reverse = True)))    for (key, data) in grouped]

for (chan, time, file) in most_recent_per_channel:
      c = int(chan)
      if c == 2 or (7 <= c and c <= 16):
            print(file)
            fs.get(path+file, file)
            os.system("mv "+file+" "+os.path.join(outdir, f'ch{chan}_TB.nc'))

