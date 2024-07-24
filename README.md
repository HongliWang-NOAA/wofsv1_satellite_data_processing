# wofs-obs-satellite

### Example usage

```
sudo docker build -t wofs-obs-satellite .

docker run --mount type=bind,source=$PWD/data,target=/mnt/data wofs-obs-satellite 202211071730 [path_to_wrf_input] [data_directory] [16|18]

bash create.sh 202402081400 /mnt/c/Joshua/temp/sat/geo_em.d01.nc /mnt/c/Joshua/temp/sat 18
```

The path to the WRF input file defaults to the mounted data directory (/mnt/data/wrfinput_d01) if not provided. 

To create multiple satellite observations for a model run at once, use the `create_run.sh` as seen below.

```
bash create_run.sh [target directory] [satellite number] [start] [end]
```

The target directory must container the `geo_em.d01.nc` for the model run. 
### Example usage

```
bash create_run.sh /mnt/c/Joshua/temp/sat 16 202407231500 202407231800
```