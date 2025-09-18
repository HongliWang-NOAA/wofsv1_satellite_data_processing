#!/bin/bash

cycle_time=$1 #yyyyMMddHHMM
data_directory=$2 
wrf_file_path=$3
sat="G$4"
sat_num=$4

year=$(echo ${cycle_time} | cut -c 1-4)
month=$(echo ${cycle_time} | cut -c 5-6)
day=$(echo ${cycle_time} | cut -c 7-8)
hour=$(echo ${cycle_time} | cut -c 9-10)
minute=$(echo ${cycle_time} | cut -c 11-12)
obstime=${hour}${minute}

high_res_time=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC -4 minutes" +%Y%m%d%H%M)
low_res_time=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC -15 minutes" +%Y%m%d%H%M)

get_high_resolution_url() {
    local yr=`echo $1 | cut -b 1-4`
    local mo=`echo $1 | cut -b 5-6`
    local dd=`echo $1 | cut -b 7-8`
    local hr=`echo $1 | cut -b 9-10`
    local min=`echo $1 | cut -b 11-12`
    local gj=$(date -u --date="$yr-$mo-${dd}T${hr}:${min}:00 UTC" +%j)
    echo "https://satcorps.larc.nasa.gov/prod/www-user/rabi/visst-pixel-netcdf/GOES_CONUS/${yr}/${mo}/${dd}/${sat}V04.0.TJ.${yr}${gj}.${hr}${min}.PX.02K.nc"
}

get_low_resolution_url() {
    local yr=`echo $1 | cut -b 1-4`
    local mo=`echo $1 | cut -b 5-6`
    local dd=`echo $1 | cut -b 7-8`
    local hr=`echo $1 | cut -b 9-10`
    local min=`echo $1 | cut -b 11-12`
    local gj=$(date -u --date="$yr-$mo-${dd}T${hr}:${min}:00 UTC" +%j)
    echo "https://satcorps.larc.nasa.gov/prod/RapidRefresh/visst-pixel-netcdf/${yr}/${mo}/${dd}/${sat}V04.0.RR.${yr}${gj}.${hr}${min}.PX.06K.nc"
}

data_urls=(
    $(get_high_resolution_url $high_res_time)  # T-4 min
    $(get_low_resolution_url $cycle_time)      # T
    $(get_low_resolution_url $low_res_time)    # T-15 min
)

for item in "${data_urls[@]}"; do
    # wget --spider $item

    # if [ $? -eq 0 ]; then
    #     wget -O "$data_directory/cwp_larc.nc" $item
    #     break
    # fi

    status=$(curl --retry 5 --retry-max-time 60 --retry-connrefused -s -o "$data_directory/cwp_larc.nc" -w "%{http_code}" "$item")

    if [ "$status" -eq 200 ]; then
        break
    fi
done

if [ -f "$data_directory/cwp_larc.nc" -a -s "$data_directory/cwp_larc.nc" ]; then
    python goesabi_larccwp_obs_rlt.py -d $data_directory -w $wrf_file_path -o $data_directory/ -a ${obstime} -t 1 -s ${sat}

    cd $data_directory

    for f in *GOES${sat_num}_CWP_OBS*; do mv "$f" "${year}${month}${day}${hour}${minute}$(echo "$f" | cut -c 13-)"; done
fi
