# wofs-obs-satellite

### Example usage

```
sudo docker build -t wofs-obs-satellite .

docker run --mount type=bind,source=$PWD/data,target=/mnt/data wofs-obs-satellite 202211071730 [path_to_wrf_input] [data_directory] [16|18]

bash create.sh 202402081400 /mnt/c/Joshua/temp/sat/geo_em.d01.nc /mnt/c/Joshua/temp/sat 18
```

The path to the WRF input file defaults to the mounted data directory (/mnt/data/wrfinput_d01) if not provided. 