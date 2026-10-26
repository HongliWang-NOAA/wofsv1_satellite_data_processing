#!/bin/bash

set -x
cycle_time=$1 #yyyyMMddHHMM
data_directory=$2 
wrf_file_path=$3
sat="G$4"
sat_num=$4

rm -fr "$data_directory/cwp_larc.nc"

year=$(echo ${cycle_time} | cut -c 1-4)
month=$(echo ${cycle_time} | cut -c 5-6)
day=$(echo ${cycle_time} | cut -c 7-8)
hour=$(echo ${cycle_time} | cut -c 9-10)
minute=$(echo ${cycle_time} | cut -c 11-12)
obstime=${hour}${minute}

#high_res_time=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC -4 minutes" +%Y%m%d%H%M)
#low_res_time=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC -15 minutes" +%Y%m%d%H%M)

get_high_resolution_url() {
    local yr=$(echo $1 | cut -b 1-4)
    local mo=$(echo $1 | cut -b 5-6)
    local dd=$(echo $1 | cut -b 7-8)
    local hr=$(echo $1 | cut -b 9-10)
    local min=$(echo $1 | cut -b 11-12)
    local gj=$(date -u --date="$yr-$mo-${dd}T${hr}:${min}:00 UTC" +%j)
    echo "https://satcorps.larc.nasa.gov/prod/www-user/rabi/visst-pixel-netcdf/GOES_CONUS/${yr}/${mo}/${dd}/${sat}V04.0.TJ.${yr}${gj}.${hr}${min}.PX.02K.nc"
}

get_low_resolution_url() {
    local yr=$(echo $1 | cut -b 1-4)
    local mo=$(echo $1 | cut -b 5-6)
    local dd=$(echo $1 | cut -b 7-8)
    local hr=$(echo $1 | cut -b 9-10)
    local min=$(echo $1 | cut -b 11-12)
    local gj=$(date -u --date="$yr-$mo-${dd}T${hr}:${min}:00 UTC" +%j)
    echo "https://satcorps.larc.nasa.gov/prod/RapidRefresh/visst-pixel-netcdf/${yr}/${mo}/${dd}/${sat}V04.0.RR.${yr}${gj}.${hr}${min}.PX.06K.nc"
}

# Target array to store valid data URLs
data_urls=()

echo "Searching for available files in the past 15 minutes..."

# Loop 1: Find the closest High Resolution file
for offset in {0..15}; do
    check_time=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC - $offset minutes" +%Y%m%d%H%M)
    url_high=$(get_high_resolution_url "$check_time")

    if curl --connect-timeout 5 --max-time 10 --output /dev/null --silent --head --fail "$url_high"; then
        echo "Found available High-Res file at T-$offset minutes"
        data_urls+=("$url_high")
        break # Exits the HIGH-RES loop immediately
    fi
done

# Loop 2: Find the closest Low Resolution file
for offset in {0..15}; do
    check_time=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC - $offset minutes" +%Y%m%d%H%M)
    url_low=$(get_low_resolution_url "$check_time")

    if curl --connect-timeout 5 --max-time 10 --output /dev/null --silent --head --fail "$url_low"; then
        echo "Found available Low-Res file at T-$offset minutes"
        data_urls+=("$url_low")
        break # Exits the LOW-RES loop immediately
    fi
done

# Fallback block / Final Summary Output
if [ ${#data_urls[@]} -eq 0 ]; then
    echo "Warning: No available files found within the 15-minute cycle window."
else
    echo "Files successfully found for processing:"
    # Using [@] ensures every single captured URL prints on its own line
    printf '%s\n' "${data_urls[@]}"
fi

for item in "${data_urls[@]}"; do
    echo "Check for file: $item"

    max_attempts=2
    attempt=1
    success=false

    while [ $attempt -le $max_attempts ]; do
        if [ $max_attempts -gt 1 ]; then
            echo "  -> Attempt $attempt of $max_attempts..."
        fi

        status=$(curl --retry 5 --max-time 30 --connect-timeout 10 --retry-max-time 60 --retry-connrefused -s -o "$data_directory/cwp_larc.nc" -w "%{http_code}" "$item")

        if [ "$status" -eq 200 ]; then
            echo "Success!"
            success=true
            break 2  # Breaks completely out of BOTH the while loop and the parent for loop
        else
            echo "  -> Status received: $status"
            rm -f "$data_directory/cwp_larc.nc"

            # If this wasn't the last attempt, wait a moment before trying again
            if [ $attempt -lt $max_attempts ]; then
                echo "  -> Retrying in 5 seconds..."
                sleep 5
            fi
        fi

        attempt=$((attempt + 1))
    done

    # If it fails both attempts for this specific item, the script automatically
    # moves on to evaluate the next URL string in the array.
    if [ "$success" = false ]; then
        echo "Failed to download from: $item after $max_attempts attempts."
    fi
done

if [ -f "$data_directory/cwp_larc.nc" -a -s "$data_directory/cwp_larc.nc" ]; then
    python goesabi_larccwp_obs_rlt.py -d $data_directory -w $wrf_file_path -o $data_directory/ -a ${obstime} -t 1 -s ${sat}

    cd $data_directory

    for f in *GOES${sat_num}_CWP_OBS*; do mv "$f" "${year}${month}${day}${hour}${minute}$(echo "$f" | cut -c 13-)"; done
fi
