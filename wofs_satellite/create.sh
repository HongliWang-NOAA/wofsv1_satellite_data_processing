cycle_time=$1
wrf_file_path=$2
data_directory=/mnt/data

mkdir -p $data_directory/TB

eval "$(conda shell.bash hook)"
conda activate wofs-satellite

python download_level2.py -o "$data_directory/TB/" -p "ACHAC" -t $cycle_time -s 16

python download_radiance.py -o "$data_directory/TB/" -p "RadC" -t $cycle_time -s 16

bash cwp.sh $cycle_time $data_directory $wrf_file_path

obstime=$(echo ${cycle_time} | cut -c 9-12)
python goesabi_tb_obs_allsky_rlt.py -d ${data_directory}/TB -m ${data_directory} -w ${wrf_file_path} -o $data_directory -a ${obstime} -t 2 -s 'G16'