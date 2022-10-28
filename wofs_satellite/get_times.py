import sys, json
from datetime import datetime, timedelta

dt = datetime.strptime(sys.stdin.read()[0:12], "%Y%m%d%H%M")

start = dt - timedelta(minutes = 3)

for i in range(5):
    t = start + timedelta(minutes = i)
    print(f'{t:%Y%j%H%M}')



