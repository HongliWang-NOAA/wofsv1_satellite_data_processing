#!/bin/bash

cycle_time=$1 #yyyyMMddHHMM
data_directory=$2 
wrf_file_path=$3
sat="G$4"
sat_num=$4
#osat='GOES16'

# eval "$(/root/.local/bin/micromamba shell hook --shell=bash)"
# micromamba activate wofs-satellite

gdate=$cycle_time
year=$(echo ${gdate} | cut -c 1-4)
month=$(echo ${gdate} | cut -c 5-6)
day=$(echo ${gdate} | cut -c 7-8)
hour=$(echo ${gdate} | cut -c 9-10)
minute=$(echo ${gdate} | cut -c 11-12)

gjday=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC" +%j)

gdate1=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC -15 minutes" +%Y%m%d%H%M)
gjday1=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC -15 minutes" +%j)

month1=$(echo ${gdate1} | cut -c 5-6)
day1=$(echo ${gdate1} | cut -c 7-8)
hour1=$(echo ${gdate1} | cut -c 9-10)
minute1=$(echo ${gdate1} | cut -c 11-12)

obstime=${hour}${minute}

#FIND G16/17/18 FILE
# High res file..
highres_time_hour=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC -4 minutes" +%H)
highres_time_min=$(date -u --date="$year-$month-${day}T${hour}:${minute}:00 UTC -4 minutes" +%M)
SFILE=${sat}V04.0.TJ.${year}${gjday}.${highres_time_hour}${highres_time_min}.PX.02K.nc
LGOESFILE=https://satcorps.larc.nasa.gov/prod/www-user/rabi/visst-pixel-netcdf/GOES_CONUS/${year}/${month}/${day}/$SFILE
wget -O $data_directory/$SFILE ${LGOESFILE}
wgetreturn=$?

echo $SFILE

# Low-res T-0 if not available 
if [[ $wgetreturn -ne 0 ]]; then
    echo "========= High-res file, $SFILE, was not found. Downloading low-res T-0 file...========="
    SFILE=${sat}V04.0.RR.${year}${gjday}.${hour}${minute}.PX.06K.nc
    LGOESFILE=https://satcorps.larc.nasa.gov/prod/RapidRefresh/visst-pixel-netcdf/${year}/${month}/${day}/$SFILE
    wget -O $data_directory/$SFILE ${LGOESFILE}
    wgetreturn=$?
fi

# Low-res T-15 if not available
if [[ $wgetreturn -ne 0 ]]; then
    echo "========= Low-res file, $SFILE, was not found. Downloading low-res T-15 mins file...========="
    SFILE=${sat}V04.0.RR.${year}${gjday1}.${hour1}${minute1}.PX.06K.nc
    LGOESFILE=https://satcorps.larc.nasa.gov/prod/RapidRefresh/visst-pixel-netcdf/${year}/${month1}/${day1}/$SFILE
    wget -O $data_directory/$SFILE ${LGOESFILE}
    wgetreturn=$?
fi


if [ ! -s "$FILE" ]; then
    mv $data_directory/${SFILE} $data_directory/cwp_larc.nc
    python goesabi_larccwp_obs_rlt.py -d $data_directory -w $wrf_file_path -o $data_directory/ -a ${obstime} -t 1 -s ${sat}

    cd $data_directory

    for f in *GOES${sat_num}_CWP_OBS*; do mv "$f" "${year}${month}${day}${hour}${minute}$(echo "$f" | cut -c 13-)"; done
fi



# mv ${OUTDIR}/${year}${month1}${day1}${hour1}${minute1}_${osat}_CWP_OBS.nc  ${OUTDIR}/${year}${month2}${day2}${hour2}${minute2}_${osat}_CWP_OBS.nc
# echo ${OUTDIR}/${year}${month1}${day1}${hour1}${minute1}_${osat}_CWP_OBS.nc
# echo  ${OUTDIR}/${year}${month}${day}${hour}${minute}_${osat}_CWP_OBS.nc
