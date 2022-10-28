#!/bin/csh 
#
#-----------------------------------------------------------------------
#  Plot GOES-16 TBs from Level 1B data at 5 min intervals
#-----------------------------------------------------------------------
source ~/.tcshrc
source /home/Thomas.Jones/WOFenv_rlt_2022

set gdate = `date -u --date='10 minutes ago' +%Y%m%d%H%M`
set gjday = `date -u --date='10 minutes ago' +%j`

set gdate1 = `date -u --date='15 minutes ago' +%Y%m%d%H%M`
set gjday1 = `date -u --date='15 minutes ago' +%j`

set gjdaynxt = `date -u --date='12 hours' +%j`

echo ${gdate}


#set ntimes = 72
set ntimes = 216
set cnt = 0
set wcnt = 0

set WORKDIR = /home/Thomas.Jones/WOFS_POST/abiplot
set TBDIR = /work/LDM/GOES16/Brightness/2022/
set TEMPDIR = /home/Thomas.Jones/WOFS_POST/abiplot/
set PYDIR = /home/Thomas.Jones/WOFS_POST/abiplot
#set FCSTDIR = /scratch/wof/realtime/FCST/
#set WRFDIR = /scratch/wof/realtime/WRFINPUTS
set WRFDIR = /work/rt_obs/WRFINPUTS/

#### CHECK TO SEE OF FORECAST SET HAS STARTED
set fcheck = 0
set year = `echo ${gdate} | cut -c 1-4`
set month = `echo ${gdate} | cut -c 5-6`
set day = `echo ${gdate} | cut -c 7-8`
set hour = `echo ${gdate} | cut -c 9-10`
set minute = `echo ${gdate} | cut -c 11-12`
set obstime = ${hour}${minute}
set starttime = ${obstime}


#set IMAGE_DIR = /www/wof.nssl.noaa.gov/newse_images/${event}/${obstime}/
#set IMAGE_DIR = /work/Thomas.Jones/POST/images/${event}/
set IMAGE_DIR = /work/rt_obs/Satellite/ABI_PLOTS/${event}/
mkdir ${IMAGE_DIR}
echo ${IMAGE_DIR}

cp ${WRFDIR}/wrfinput_d01.${event}  ${TEMPDIR}/wrfinput_d01_ic

mkdir ${TEMPDIR}/${event}
rm ${TEMPDIR}/${event}/*nc
cd ${TEMPDIR}/${event}/
cp ${WORKDIR}/input.nml ./
cp ${WORKDIR}/sdum ./

#### LOOP FROM FORECAST START TIME TO 3 HOURS LATER AT 5 MINUTE INTERVALS
while ( ${cnt} <= ${ntimes} )
  set fcheck = 0  
  rm ${TEMPDIR}/${event}/*nc
  cd ${TEMPDIR}/${event}/

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

  echo ${thisday} ${gdate}

  # IF obstime == 0000 go to next Jday
  if (${obstime} == '0000') then
    set gjday1 = ${gjday}
    set gjday = ${gjdaynxt}
  endif
  
  # GET Minute info -3, +1
  set gdatem5  =  `echo  ${gdate} -5m | ${WORKDIR}/advance_time`
  set gdatem4  =  `echo  ${gdate} -4m | ${WORKDIR}/advance_time`
  set gdatem3  =  `echo  ${gdate} -3m | ${WORKDIR}/advance_time`
  set gdatem2  =  `echo  ${gdate} -2m | ${WORKDIR}/advance_time`
  set gdatem1  =  `echo  ${gdate} -1m | ${WORKDIR}/advance_time`
  set gdatep1  =  `echo  ${gdate} +1m | ${WORKDIR}/advance_time`

  set minute_m5 = `echo ${gdatem5} | cut -c 11-12`
  set minute_m4 = `echo ${gdatem4} | cut -c 11-12`
  set minute_m3 = `echo ${gdatem3} | cut -c 11-12`
  set minute_m2 = `echo ${gdatem2} | cut -c 11-12`
  set minute_m1 = `echo ${gdatem1} | cut -c 11-12`
  set minute_p1 = `echo ${gdatep1} | cut -c 11-12`

  set hour_m1 = `echo ${gdatem1} | cut -c 9-10`

  echo ${minute_m3} ${minute_m2} ${minute_m1} ${minute} ${minute_p1}

  #SERACH FOR LEVEL 1B FILES NEAREST TO TIME 
  # LOOP THROUGH CHANNELS
  foreach chan ( 02 08 09 10 14 )
    rm sat*
    set fcheck = 0
    if (${obstime} == '0000') then
        #set IMAGE_DIR = /work/Thomas.Jones/POST/images/${year}${month}${day}
        set IMAGE_DIR = /work/rt_obs/Satellite/ABI_PLOTS/${year}${month}${day}/
        mkdir ${IMAGE_DIR}

        while ( ${fcheck} == 0 )
         ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday1}${hour_m1}${minute_m5}*nc >! sataaa
         ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday1}${hour_m1}${minute_m4}*nc >! sataa
         ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday1}${hour_m1}${minute_m3}*nc >! sata
         ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday1}${hour_m1}${minute_m2}*nc >! satb
         ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday1}${hour_m1}${minute_m1}*nc >! satc
         ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour}${minute}*nc >!   satd
         ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour}${minute_p1}*nc >! sate
         cat sataaa sataa sata satb satc satd sate sdum > sat
         set GOESFILE  = `head -1 sat`
         echo ${GOESFILE} 

        sleep 2
        # WAIT UNTIL FILE EXISTS
          if ( -e ${GOESFILE} ) then
            set fcheck = 1
            cp ${GOESFILE} ${TEMPDIR}/${event}/ch${chan}_TB.nc
	  else
	    echo "WAITING FOR GOES-16 L1B FILE"
            sleep 60
	  endif
      end
    else
      while ( ${fcheck} == 0 )
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour_m1}${minute_m5}*nc >! sataaa
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour_m1}${minute_m4}*nc >! sataa
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour_m1}${minute_m3}*nc >! sata
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour_m1}${minute_m2}*nc >! satb
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour_m1}${minute_m1}*nc >! satc
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour}${minute}*nc >!   satd
        ls -rt1 ${TBDIR}/C${chan}/OR_ABI-L1b-RadC-M6C${chan}_G16_s${year}${gjday}${hour}${minute_p1}*nc >! sate
        cat sataaa sataa sata satb satc satd sate sdum > sat
        set GOESFILE  = `head -1 sat`
        echo ${GOESFILE}

        sleep 2
        # WAIT UNTIL FILE EXISTS
          if ( -e ${GOESFILE} ) then
            set fcheck = 1
            cp ${GOESFILE} ${TEMPDIR}/${event}/ch${chan}_TB.nc
          else
	    echo "WAITING FOR GOES-16 L1B FILE"
            sleep 60
	    #@ wcnt++
	    #if ( ${wcnt} > 10 ) then
	    #   set GOESFILE = /work/Thomas.Jones/none.nc
               set fcheck = 0
	    #endif
	  endif
      end
        
    endif

  end
 

  ############ RUN PYTHON PROGRAM TO GENERATE CLEAR-SKY TB OBSERVATIONS
  rm sat*
  #rm sdum
  cd ${PYDIR}

  /home/Thomas.Jones/anaconda2/bin/python abi_data_plot_cloud.py -p ${IMAGE_DIR} -d ${TEMPDIR}/${event} -w ${TEMPDIR} -t ${cnt} -g ${gdate}

  sleep 2

   # Advance time here
   set gdate  =  `echo  ${gdate} +5m | ${WORKDIR}/advance_time` 
   set gdate1  =  `echo  ${gdate1} +5m | ${WORKDIR}/advance_time`

   echo ${gdate}
   echo ${gdate1}

   #cd ${TEMPDIR}
   @ cnt++ 
end
  # End time loop

cd ${TEMPDIR}/${event}/${obstime}
rm sat*
rm ${TEMPDIR}/${event}/${obstime}/*nc
exit(0)
