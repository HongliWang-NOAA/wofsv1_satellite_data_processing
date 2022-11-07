# wofs-obs-satellite

### Example usage

```
sudo docker build -t wofs-obs-satellite .

docker run --mount type=bind,source=$PWD/data/input,target=/mnt/input --mount type=bind,source=$PWD/data/output,target=/mnt/output wofs-obs-satellite 202211071730
```

The mounted input directory must contain the `wrfinput_d01` for your domain.