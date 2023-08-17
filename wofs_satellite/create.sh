cycle_time=$1 
wrf_file_path=${2-/mnt/data/wrfinput_d01} # 2nd parameter is the path to the WRF input file; defaults to the data directory if nt provided
data_directory=${3-/mnt/data}
satellite=${4-16}

mkdir -p $data_directory/TB

# eval "$(micromamba shell hook --shell=bash)"
# micromamba activate wofs-satellite

python download_level2.py -o "$data_directory/TB/" -p "ACHAC" -t $cycle_time -s $satellite

python download_radiance.py -o "$data_directory/TB/" -p "RadC" -t $cycle_time -s $satellite

bash cwp.sh $cycle_time $data_directory $wrf_file_path "$satellite"

obstime=$(echo ${cycle_time} | cut -c 9-12)
python goesabi_tb_obs_allsky_rlt.py -d ${data_directory}/TB -m ${data_directory} -w ${wrf_file_path} -o $data_directory -a ${obstime} -t 2 -s "G$satellite"

python3 -m plot -d ${data_directory}/TB -p ${data_directory} -w ${wrf_file_path} -g $cycle_time