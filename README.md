# wofs-obs-satellite

### Example usage

```sudo docker build -t wofs-obs-satellite .```

```docker run --mount type=bind,source=$PWD,target=/mnt/input --mount type=bind,source=$DATA_PATH,target=/mnt/output wofs-obs-satellite cwp.sh -t 202003030615```