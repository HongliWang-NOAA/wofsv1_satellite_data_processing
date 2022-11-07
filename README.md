# wofs-obs-satellite

### Example usage

```
sudo docker build -t wofs-obs-satellite .

docker run --mount type=bind,source=$PWD/data,target=/mnt/data wofs-obs-satellite 202211071730 <path_to_wrf_input>
```
