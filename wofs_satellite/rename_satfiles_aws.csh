#!/bin/csh 
#
#-----------------------------------------------------------------------
#  DOWNLOAD GOES-R L2 PRODUCTS FROM AWS 
#   -- realtime script
#-----------------------------------------------------------------------
source ~/.tcshrc
source /home/Thomas.Jones/WOFenv_rlt_2022
#
set indate = `date +%Y%m%d`
#
set gdate = `date -u --date='0 minutes ago' +%Y%m%d%j%H%M`
set currmin = `date -u --date='0 minutes ago' +%M`
#set prevmin = `date -u --date='7 minutes ago' +%M`

### account for 56 minute file
echo ${currmin}
if (${currmin} == '01') then 
   set gdate = `date -u --date='2 minutes ago' +%Y%m%d%j%H%M`
endif

echo ${gdate}

set sat = 16

set OUTDIR = '/work/Thomas.Jones/realtime/OBSGEN/SATDATA/Products_RLT/'
set PYDIR = '/home/Thomas.Jones/GOES16_PROCESS/python/' 

#CTH
echo
cd ${OUTDIR}
/home/Thomas.Jones/anaconda2/bin/python ${PYDIR}/rename_sataws.py -o ${OUTDIR}"CTH/" -p "ACHAC" -t ${gdate} -s ${sat}

sleep 5
set sat = 17
/home/Thomas.Jones/anaconda2/bin/python ${PYDIR}/rename_sataws.py -o ${OUTDIR}"CTH/" -p "ACHAC" -t ${gdate} -s ${sat}


exit(0)
#COT
#python ${PYDIR}/rename_sat.py -d ${INDIR}"Y01/"${indate}"/" -o ${OUTDIR}"COT/" -p "Y01" -s "COT" -t ${gdate}

#CLOUD_MASK
python ${PYDIR}/rename_sat.py -d ${INDIR}"H99/" -o ${OUTDIR}"MASK/" -p "H99" -s "CLOUD_MASK" -t ${gdate}

#AMV
python ${PYDIR}/rename_sat.py -d ${INDIR}"U99/" -o ${OUTDIR}"AMV/" -p "U99" -s "AMV" -t ${gdate}
#
#AOT
python ${PYDIR}/rename_sat.py -d ${INDIR}"B99/" -o ${OUTDIR}"AOT/" -p "B99" -s "AOT" -t ${gdate}

#Aerosol Tyoe
python ${PYDIR}/rename_sat.py -d ${INDIR}"A99/" -o ${OUTDIR}"ATYPE/" -p "A99" -s "ATYPE" -t ${gdate}
