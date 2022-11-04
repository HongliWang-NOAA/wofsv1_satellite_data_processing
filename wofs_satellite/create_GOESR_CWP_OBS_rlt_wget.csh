#!/bin/csh 
#
#-----------------------------------------------------------------------
#  CREATE GOES-16 clear-sky TB observation file in netcdf format 
#  	from Level 1B and L2 data
#-----------------------------------------------------------------------
source ~/.tcshrc
source /home/Thomas.Jones/WOFenv_rlt_2022

set indate = `date +%Y%m%d`

#set gdate = `date -u --date='4 minutes ago' +%Y%m%d%H%M`
#set gjday = `date -u --date='4 minutes ago' +%j`
#set gdate1 = `date -u --date='8 minutes ago' +%Y%m%d%H%M`
#set gjday1 = `date -u --date='8 minutes ago' +%j`

set gdate = `date -u --date='5 minutes ago' +%Y%m%d%H%M`
set gjday = `date -u --date='5 minutes ago' +%j`
set gdate1 = `date -u --date='9 minutes ago' +%Y%m%d%H%M`
set gjday1 = `date -u --date='9 minutes ago' +%j`

set year = `echo ${gdate} | cut -c 1-4`
set month = `echo ${gdate} | cut -c 5-6`
set day = `echo ${gdate} | cut -c 7-8`
set hour = `echo ${gdate} | cut -c 9-10`
set minute = `echo ${gdate} | cut -c 11-12`

set month1 = `echo ${gdate1} | cut -c 5-6`
set day1 = `echo ${gdate1} | cut -c 7-8`
set hour1 = `echo ${gdate1} | cut -c 9-10`
set minute1 = `echo ${gdate1} | cut -c 11-12`

set fcheck = 0
set sat = 'G16'
set osat = 'GOES16'

#set LARC = https://satcorps.larc.nasa.gov/prod/GOES16-FD/visst-pixel-netcdf/SEUSA/${year}/${month1}/${day1}
set LARC = https://satcorps.larc.nasa.gov/prod/www-user/rabi/GOES16-FD/visst-pixel-netcdf/SEUSA/${year}/${month1}/${day1}
set WORKDIR = /home/Thomas.Jones/GOES16_PROCESS/scripts_rt

set TEMPDIR = /work/rt_obs/Satellite/CWP/temp2
set PYDIR = /home/Thomas.Jones/GOES16_PROCESS/python
#set WRFDIR = /scratch/wof/realtime/WRFINPUTS/
set WRFDIR = /work/rt_obs/WRFINPUTS/

set MRMSSAT = /work/Thomas.Jones/realtime/OBSGEN/MRMS_template
set SATDIR = /work/LDM/GOES16/
set SAVEDIR = /work/Thomas.Jones/realtime/OBSGEN/SATDATA/CWP/2022/

#set OUTDIR = /oldscratch/tajones/realtime/OBSGEN/Satellite/CWP
set OUTDIR = /work/rt_obs/Satellite/CWP/

rm ${TEMPDIR}/*nc

if ( ${hour}${minute} == '1500' ) then
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


  #FIND G16 GILE
  set SFILE = ${sat}V04.0.TJ.${year}${gjday1}.${hour1}${minute1}.PX.02K.nc
  #set GOESFILE = ${SATDIR}/${sat}V04.0.TJ.${year}${gjday1}.${hour1}${minute1}.PX.02K.nc 
  echo ${SFILE} 
  set LGOESFILE = ${LARC}/${sat}V04.0.TJ.${year}${gjday1}.${hour1}${minute1}.PX.02K.nc

  set fff = 0
  while ( ${fcheck} == 0 ) 
    wget ${LGOESFILE}
    sleep 2
    if (-e ${SFILE} ) then
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
    endif
  end

  sleep 2

  cp ${SFILE} ${TEMPDIR}/cwp_larc.nc
  mv ${SFILE} ${SAVEDIR}/

  sleep 3

  echo ${TEMPDIR}

  ############ RUN PYTHON PROGRAM TO GENERATE CWP OBSERVATIONS
  cd ${PYDIR}

  #/home/Thomas.Jones/anaconda2/bin/python goesabi_larccwp_obs_rlt.py -d ${TEMPDIR} -m ${MRMSSAT} -w ${WORKDIR} -o ${OUTDIR}/${year} -a ${obstime} -t 2 -s ${sat}
  sleep 2

  #mv ${OUTDIR}/${year}/${year}${month1}${day1}${hour1}${minute1}_${osat}_CWP_OBS.nc  ${OUTDIR}/${year}/${year}${month}${day}${obstime}_${osat}_CWP_OBS.nc 


cd ${WORKDIR}
rm sat*
rm cot*
#rm ${TEMPDIR}/*nc
exit(0)
