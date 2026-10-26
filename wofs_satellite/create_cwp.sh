#!/bin/bash

source ~/.bashrc
micromamba activate /scratch4/NCEPDEV/fv3-cam/Hongli.Wang/WoFS/conda/envs/wofs-satellite

cycle_time=$1 
wrf_file_path=${2-/mnt/data/wrfinput_d01} # 2nd parameter is the path to the WRF input file; defaults to the data directory if nt provided
data_directory=${3-/mnt/data}
satellite=${4-19}
use_clr_sky=${5-1}

mkdir -p $data_directory/TB

# eval "$(micromamba shell hook --shell=bash)"
# micromamba activate wofs-satellite

echo "bash cwp.sh $cycle_time $data_directory $wrf_file_path "$satellite" "
bash cwp.sh $cycle_time $data_directory $wrf_file_path "$satellite"

exit 0
