#!/bin/bash
#
#-----------------------------------------------------------------------
#  CREATE GOES-16 clear-sky TB observation file in netcdf format 
#  	from Level 1B and L2 data
#-----------------------------------------------------------------------

cycle_time=$1 #yyyyMMddHHMM
input_directory=/mnt/input #$2
output_directory=/mnt/output #$3
sat='G16'

conda activate wofs-satellite

TBDIR=$input_directory/TB
COTDIR=$input_directory/COT
TEMPDIR=$(mktemp -d)
WORKDIR=${TEMPDIR}
WRFDIR=$input_directory
MRMSSAT=$input_directory
OUTDIR=$output_directory

obstime=$(echo ${cycle_time} | cut -c 9-12)

#SERACH FOR LEVEL 1B FILES NEAREST TO TIME 
# LOOP THROUGH CHANNELS
foreach chan ( 07 08 09 10 11 12 13 14 15 16 )
    rm sat*

    # Loop through the T-3 and T+1 times and search for available obs
    i=0
    echo $cycle_time | python3 get_times.py | while read yr_day_hr_min
    do
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${yr_day_hr_min}*nc >| sat${i}
        ((i=i+1))
    done
    cat sat* > sat_final
    GOESFILE=$(head -1 sat_final)
    echo ${GOESFILE} 
    cp ${GOESFILE} ${TEMPDIR}/ch${chan}_TB.nc
end

#GET L2 CTH FILE be sure to only get CONUS FILE
rm cot*

i=0
echo $cycle_time | python3 get_times.py -r 6 | while read yr_day_hr_min
do
    ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${yr_day_hr_min}*nc >| cot${i}
    ((i=i+1))
done
cat cot* > cot_final
COTFILE=$(head -1 cot_final)
echo ${COTFILE}
cp ${COTFILE} ${TEMPDIR}/cth.nc

############ RUN PYTHON PROGRAM TO GENERATE CLEAR-SKY TB OBSERVATIONS

python goesabi_tb_obs_allsky_rlt.py -d ${TEMPDIR} -m ${MRMSSAT} -w ${TEMPDIR} -o ${OUTDIR} -a ${obstime} -t 2 -s ${sat}

rm sat*
rm cot*
rm -r ${TEMPDIR}
exit(0)