#!/bin/csh 
#
#-----------------------------------------------------------------------
#  CREATE GOES-16 clear-sky TB observation file in netcdf format 
#  	from Level 1B and L2 data
#-----------------------------------------------------------------------
source ~/.tcshrc

source /home/Thomas.Jones/WOFenv_rlt_2022

#set indate = `date +%Y%m%d`

set gdate = `date -u --date='7 minutes ago' +%Y%m%d%H%M`
set gjday = `date -u --date='7 minutes ago' +%j`

set gdate1 = `date -u --date='14 minutes ago' +%Y%m%d%H%M`
set gjday1 = `date -u --date='14 minutes ago' +%j`

set sat = 'G16'

set TBDIR = /work/LDM/GOES16/Brightness/2022/
#set COTDIR = /oldscratch/tajones/realtime/OBSGEN/SATDATA/Products_RLT/CTH/
set COTDIR = /work/Thomas.Jones/realtime/OBSGEN/SATDATA/Products_RLT/CTH/

set TEMPDIR = /home/Thomas.Jones/GOES16_PROCESS/allsky16
set WORKDIR = ${TEMPDIR}
set PYDIR = /home/Thomas.Jones/GOES16_PROCESS/python
#set WRFDIR = /scratch/wof/realtime/WRFINPUTS/
set WRFDIR = /work/rt_obs/WRFINPUTS/

set MRMSSAT = /work/Thomas.Jones/realtime/OBSGEN/MRMS_template
set OUTDIR = /work/rt_obs/Satellite/RADIANCE


rm ${TEMPDIR}/*nc
rm ${WORKDIR}/wrfinput_d01_ic
cp ${WRFDIR}/wrfinput_d01.${event}  ${WORKDIR}/wrfinput_d01_ic

  cd ${WORKDIR}

  set year = `echo ${gdate} | cut -c 1-4`
  set month = `echo ${gdate} | cut -c 5-6`
  set day = `echo ${gdate} | cut -c 7-8`
  set hour = `echo ${gdate} | cut -c 9-10`
  set minute = `echo ${gdate} | cut -c 11-12`
  set obstime = ${hour}${minute}
  set thisday = ${year}${month}${day}

  set month1 = `echo ${gdate1} | cut -c 5-6`
  set day1 = `echo ${gdate1} | cut -c 7-8`
  set hour1 = `echo ${gdate1} | cut -c 9-10`
  set minute1 = `echo ${gdate1} | cut -c 11-12`
  set thisday1 = ${year}${month1}${day1}

  #SERACH FOR LEVEL 1B FILES NEAREST TO TIME 
  # LOOP THROUGH CHANNELS
  foreach chan ( 07 08 09 10 11 12 13 14 15 16 )
    rm sat*
    if (${minute} == '00') then
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday1}${hour1}57*nc >! sat00a
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday1}${hour1}58*nc >! sat00b
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday1}${hour1}59*nc >! sat00c
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}00*nc >! sat00d
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}01*nc >! sat00e
        cat sat00a sat00b sat00c sat00d sat00e > sat00
        set GOESFILE  = `head -1 sat00`
        echo ${GOESFILE} 
        cp ${GOESFILE} ${TEMPDIR}/ch${chan}_TB.nc
    endif

    if (${minute} == '15') then
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}12*nc >! sat15a
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}13*nc >! sat15b
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}14*nc >! sat15c
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}15*nc >! sat15d
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}16*nc >! sat15e
        cat sat15a sat15b sat15c sat15d sat15e > sat15
        set GOESFILE  = `head -1 sat15`
        echo ${GOESFILE}
        cp ${GOESFILE} ${TEMPDIR}/ch${chan}_TB.nc
    endif

    if (${minute} == '30') then
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}27*nc >! sat30a
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}28*nc >! sat30b
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}29*nc >! sat30c
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}30*nc >! sat30d
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}31*nc >! sat30e
        cat sat30a sat30b sat30c sat30d sat30e > sat30
        set GOESFILE  = `head -1 sat30`
        echo ${GOESFILE}
        cp ${GOESFILE} ${TEMPDIR}/ch${chan}_TB.nc
    endif

    if (${minute} == '45') then
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}42*nc >! sat45a
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}43*nc >! sat45b
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}44*nc >! sat45c
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}45*nc >! sat45d
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_${sat}_s${year}${gjday}${hour}46*nc >! sat45e
        cat sat45a sat45b sat45c sat45d sat45e > sat45
        set GOESFILE  = `head -1 sat45`
        echo ${GOESFILE}
        cp ${GOESFILE} ${TEMPDIR}/ch${chan}_TB.nc
    endif

  end
 
  #GET L2 CTH FILE be sure to only get CONUS FILE
   rm cot*
   echo ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}${minute}

   if (${minute} == '00') then
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month1}${day1}${hour1}56*nc >! cot00aa
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month1}${day1}${hour1}57*nc >! cot00a
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month1}${day1}${hour1}58*nc >! cot00b
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month1}${day1}${hour1}59*nc >! cot00c
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}00*nc >! cot00d
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}01*nc >! cot00e
      cat  cot00aa cot00a cot00b cot00c cot00d cot00e > cot00
      set COTFILE  = `head -1 cot00`
      echo ${COTFILE}
      cp ${COTFILE} ${TEMPDIR}/cth.nc
  endif  

  if (${minute} == '15') then
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}11*nc >! cot15aa
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}12*nc >! cot15a
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}13*nc >! cot15b
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}14*nc >! cot15c
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}15*nc >! cot15d
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}16*nc >! cot15e

      cat cot15aa cot15a cot15b cot15c cot15d cot15e > cot15
      set COTFILE  = `head -1 cot15`
      echo ${COTFILE}
      cp ${COTFILE} ${TEMPDIR}/cth.nc
  endif

  if (${minute} == '30') then
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}26*nc >! cot30aa
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}27*nc >! cot30a
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}28*nc >! cot30b
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}29*nc >! cot30c
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}30*nc >! cot30d
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}31*nc >! cot30e

      cat cot30aa cot30a cot30b cot30c cot30d cot30e > cot30
      set COTFILE  = `head -1 cot30`
      echo ${COTFILE}
      cp ${COTFILE} ${TEMPDIR}/cth.nc
  endif

  if (${minute} == '45') then
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}41*nc >! cot45aa
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}42*nc >! cot45a
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}43*nc >! cot45b
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}44*nc >! cot45c
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}45*nc >! cot45d
      ls -rt1 ${COTDIR}/${sat}_CONUS_ACHAC_${year}${month}${day}${hour}46*nc >! cot45e

      cat cot45aa  cot45a cot45b cot45c cot45d cot45e > cot45
      set COTFILE  = `head -1 cot45`
      echo ${COTFILE}
      cp ${COTFILE} ${TEMPDIR}/cth.nc
  endif

  ############ RUN PYTHON PROGRAM TO GENERATE CLEAR-SKY TB OBSERVATIONS
  cd ${PYDIR}

  /home/Thomas.Jones/anaconda2/bin/python goesabi_tb_obs_allsky_rlt.py -d ${TEMPDIR} -m ${MRMSSAT} -w ${WORKDIR} -o ${OUTDIR}/${year} -a ${obstime} -t 2 -s ${sat}


cd ${WORKDIR}
rm sat*
rm cot*
rm ${TEMPDIR}/*nc
exit(0)
