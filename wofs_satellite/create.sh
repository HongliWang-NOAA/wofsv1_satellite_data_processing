cycle_time=$1
input_directory=/mnt/input #$2
output_directory=/mnt/output #$3

mkdir -p $output_directory/TB

eval "$(conda shell.bash hook)"
conda activate wofs-satellite

python download_level2.py -o "$output_directory/TB/" -p "ACHAC" -t $cycle_time -s 16

python download_radiance.py -o "$output_directory/TB/" -p "RadC" -t $cycle_time -s 16

bash cwp.sh $cycle_time $input_directory $output_directory

obstime=$(echo ${cycle_time} | cut -c 9-12)
python goesabi_tb_obs_allsky_rlt.py -d ${output_directory}/TB -m ${output_directory} -w ${input_directory} -o $output_directory -a ${obstime} -t 2 -s 'G16'