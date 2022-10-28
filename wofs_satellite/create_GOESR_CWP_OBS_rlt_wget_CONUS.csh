#!/bin/csh 
#
#-----------------------------------------------------------------------
#  CREATE GOES-16 clear-sky TB observation file in netcdf format 
#  	from Level 1B and L2 data
#-----------------------------------------------------------------------
source ~/.tcshrc
source /home/Thomas.Jones/WOFenv_rlt_2022

set indate = `date +%Y%m%d`

set gdate = `date -u --date='0 minutes ago' +%Y%m%d%H%M`
set gjday = `date -u --date='0 minutes ago' +%j`
set gdate1 = `date -u --date='22 minutes ago' +%Y%m%d%H%M`
set gjday1 = `date -u --date='22 minutes ago' +%j`
set gdate2 = `date -u --date='7 minutes ago' +%Y%m%d%H%M`

set year = `echo ${gdate} | cut -c 1-4`
set month = `echo ${gdate} | cut -c 5-6`
set day = `echo ${gdate} | cut -c 7-8`
set hour = `echo ${gdate} | cut -c 9-10`
set minute = `echo ${gdate} | cut -c 11-12`

set month1 = `echo ${gdate1} | cut -c 5-6`
set day1 = `echo ${gdate1} | cut -c 7-8`
set hour1 = `echo ${gdate1} | cut -c 9-10`
set minute1 = `echo ${gdate1} | cut -c 11-12`

set month2 = `echo ${gdate2} | cut -c 5-6`
set day2 = `echo ${gdate2} | cut -c 7-8`
set hour2 = `echo ${gdate2} | cut -c 9-10`
set minute2 = `echo ${gdate2} | cut -c 11-12`

set fcheck = 0
set sat = 'G16'
set osat = 'GOES16'

set LARC = /work/rt_obs/Satellite/CWP/RAW_DATA/GOES-E/${year}/RR/
set WORKDIR = /home/Thomas.Jones/GOES16_PROCESS/scripts_rt

set TEMPDIR = /work/rt_obs/Satellite/CWP/temp/CONUS/
set PYDIR = /home/Thomas.Jones/GOES16_PROCESS/python
#set WRFDIR = /scratch/wof/realtime/WRFINPUTS/
set WRFDIR = /work/rt_obs/WRFINPUTS/

set MRMSSAT = /work/Thomas.Jones/realtime/OBSGEN/MRMS_template
set SAVEDIR = /work/Thomas.Jones/realtime/OBSGEN/SATDATA/CWP/${year}/CONUS/

set OUTDIR = /work/rt_obs/Satellite/CWP/${year}/CONUS/

rm ${TEMPDIR}/*nc

if ( ${hour1}${minute1} == '1500' ) then
  rm ${WORKDIR}/wrfinput_d01_ic
  cp ${WRFDIR}/wrfinput_d01.${event}  ${WORKDIR}/wrfinput_d01_ic
  echo "COPY OVER wrfinput_d01 file for domain info"
endif

  cd ${WORKDIR}

  set year = `echo ${gdate} | cut -c 1-4`
  set month = `echo ${gdate} | cut -c 5-6`
  set day = `echo ${gdate} | cut -c 7-8`
  set hour = `echo ${gdate} | cut -c 9-10`
  set minute = `echo ${gdate} | cut -c 11-12`
  set thisday = ${year}${month}${day}
  set obstime = ${hour}${minute}
  set hhh = `echo ${hour} | cut -c 1-1`

  set month1 = `echo ${gdate1} | cut -c 5-6`
  set day1 = `echo ${gdate1} | cut -c 7-8`
  set hour1 = `echo ${gdate1} | cut -c 9-10`
  set minute1 = `echo ${gdate1} | cut -c 11-12`
  set thisday1 = ${year}${month1}${day1}


  #FIND G16/17/18 FILE
  set LGOESFILE = ${LARC}/${sat}V04.0.RR.${year}${gjday1}.${hour1}${minute1}.PX.06K.nc
  echo ${LGOESFILE}

  set fff = 0
  while ( ${fcheck} == 0 ) 
    if (-e ${LGOESFILE} ) then
     set fcheck = 1
    else
     sleep 15
     echo "WAITING FOR "${LGOESFILE}
     @ fff++
     if ( ${fff} > 60 ) then
        echo "NO FILE, EXITING"
        exit(0)
     endif
    endif
  end

  sleep 2

  cp ${LGOESFILE} ${TEMPDIR}/cwp_larc.nc

  sleep 5

  echo ${TEMPDIR}

  ############ RUN PYTHON PROGRAM TO GENERATE CWP OBSERVATIONS
  cd ${PYDIR}

  /home/Thomas.Jones/anaconda2/bin/python goesabi_larccwp_obs_rlt.py -d ${TEMPDIR} -m ${MRMSSAT} -w ${WORKDIR} -o ${OUTDIR}/ -a ${obstime} -t 2 -s ${sat}
  sleep 2

  mv ${OUTDIR}/${year}${month1}${day1}${hour1}${minute1}_${osat}_CWP_OBS.nc  ${OUTDIR}/${year}${month2}${day2}${hour2}${minute2}_${osat}_CWP_OBS.nc
  echo ${OUTDIR}/${year}${month1}${day1}${hour1}${minute1}_${osat}_CWP_OBS.nc
  echo  ${OUTDIR}/${year}${month}${day}${hour}${minute}_${osat}_CWP_OBS.nc


cd ${WORKDIR}
rm sat*
rm cot*
#rm ${TEMPDIR}/*nc
exit(0)
