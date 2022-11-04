#!/bin/bash

cycle_time=$1 #yyyyMMddHHMM
input_directory=/mnt/input #$2
output_directory=/mnt/output #$3
sat='G16'
osat='GOES16'

conda activate wofs-satellite

gdate2=$cycle_time
year2=$(echo ${gdate2} | cut -c 1-4)
month2=$(echo ${gdate2} | cut -c 5-6)
day2=$(echo ${gdate2} | cut -c 7-8)
hour2=$(echo ${gdate2} | cut -c 9-10)
minute2=$(echo ${gdate2} | cut -c 11-12)

gdate=$(date -u --date='$year2-$month2-${day2}T${hour2}:${minute2}:00 UTC +7 minutes' +%Y%m%d%H%M)
gjday=$(date -u --date='$year2-$month2-${day2}T${hour2}:${minute2}:00 UTC +7 minutes' +%j)
gdate1=$(date -u --date='$year2-$month2-${day2}T${hour2}:${minute2}:00 UTC -14 minutes' +%Y%m%d%H%M)
gjday1=$(date -u --date='$year2-$month2-${day2}T${hour2}:${minute2}:00 UTC -14 minutes' +%j)

year=`echo ${gdate} | cut -c 1-4`
month=`echo ${gdate} | cut -c 5-6`
day=`echo ${gdate} | cut -c 7-8`
hour=`echo ${gdate} | cut -c 9-10`
minute=`echo ${gdate} | cut -c 11-12`

month1=`echo ${gdate1} | cut -c 5-6`
day1=`echo ${gdate1} | cut -c 7-8`
hour1=`echo ${gdate1} | cut -c 9-10`
minute1=`echo ${gdate1} | cut -c 11-12`

LARC=/work/rt_obs/Satellite/CWP/RAW_DATA/GOES-E/${year}/RR/

TEMPDIR=$(mktemp -d)
WORKDIR=$TEMPDIR

WRFDIR=$input_directory

MRMSSAT=$input_directory
SAVEDIR=/work/Thomas.Jones/realtime/OBSGEN/SATDATA/CWP/${year}/CONUS/

OUTDIR=$output_directory

cd ${WORKDIR}

obstime=${hour}${minute}

#FIND G16/17/18 FILE
LGOESFILE=${LARC}/${sat}V04.0.RR.${year}${gjday1}.${hour1}${minute1}.PX.06K.nc
echo ${LGOESFILE}

cp ${LGOESFILE} ${TEMPDIR}/cwp_larc.nc

echo ${TEMPDIR}

python goesabi_larccwp_obs_rlt.py -d ${TEMPDIR} -m ${MRMSSAT} -w ${WORKDIR} -o ${OUTDIR}/ -a ${obstime} -t 2 -s ${sat}

mv ${OUTDIR}/${year}${month1}${day1}${hour1}${minute1}_${osat}_CWP_OBS.nc  ${OUTDIR}/${year}${month2}${day2}${hour2}${minute2}_${osat}_CWP_OBS.nc
echo ${OUTDIR}/${year}${month1}${day1}${hour1}${minute1}_${osat}_CWP_OBS.nc
echo  ${OUTDIR}/${year}${month}${day}${hour}${minute}_${osat}_CWP_OBS.nc


cd ${WORKDIR}
rm sat*
rm cot*
rm -r ${TEMPDIR}
exit(0)
