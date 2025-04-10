cycle_time=$1 
wrf_file_path=${2-/mnt/data/wrfinput_d01} # 2nd parameter is the path to the WRF input file; defaults to the data directory if nt provided
data_directory=${3-/mnt/data}
satellite=${4-16}
use_clr_sky=${5-1}

mkdir -p $data_directory/TB

source ~/.bashrc

# eval "$(micromamba shell hook --shell=bash)"
# micromamba activate wofs-satellite

python3 download_level2.py -o "$data_directory/TB/" -p "ACHAC" -t $cycle_time -s $satellite

python3 download_radiance.py -o "$data_directory/TB/" -p "RadC" -t $cycle_time -s $satellite

bash cwp.sh $cycle_time $data_directory $wrf_file_path "$satellite"

obstime=$(echo ${cycle_time} | cut -c 9-12)

if [ "$use_clr_sky" -eq 1 ]; then
    goesabi="goesabi_tb_obs_clrsky_rlt.py"
else
    goesabi="goesabi_tb_obs_allsky_rlt.py"
fi

python3 $goesabi -d ${data_directory}/TB -w ${wrf_file_path} -o $data_directory -a ${obstime} -t 1 -s "G$satellite"

python3 -m plot -d ${data_directory}/TB -p ${data_directory} -w ${wrf_file_path} -g $cycle_time
