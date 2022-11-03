import sys
from datetime import datetime, timedelta
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-r", "--range", dest="range", default = 5)
(options, args) = parser.parse_args()

dt = datetime.strptime(sys.stdin.read()[0:12], "%Y%m%d%H%M")
start = dt - timedelta(minutes = int(options.range) - 2)

for i in range(int(options.range)):
    t = start + timedelta(minutes = i)
    print(f'{t:%Y%j%H%M}')