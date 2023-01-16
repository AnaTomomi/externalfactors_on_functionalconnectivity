#! user/bin/bash

day=$1
path=/m/cs/archive/networks-pm/behavioral/wristband/day-$day;
mv_path=/m/cs/project/networks-pm/behavioral;

cd $mv_path
mkdir -p day-${day}
echo "new directory created....."

cd $path

for filename in $(find . -name '*.zip');
do
    unzip -d "${filename%.zip}" "$filename"
    rm ${filename:2}
done

if [ -d $path/ses1/ ] ; then 
echo "E4 files found!"
for dir in $path/ses*/
do
    cd $dir
    folder=$(basename $dir)
    run="${folder: -1}"
    
    cp ${dir}ACC.csv $mv_path/day-${day}/sub-01_day-${day}_device-e4_run-${run}_accelerometer.csv
    cp ${dir}BVP.csv $mv_path/day-${day}/sub-01_day-${day}_device-e4_run-${run}_photoplethysmograph.csv
    cp ${dir}EDA.csv $mv_path/day-${day}/sub-01_day-${day}_device-e4_run-${run}_electrodermal.csv
    cp ${dir}HR.csv $mv_path/day-${day}/sub-01_day-${day}_device-e4_run-${run}_hr.csv
    cp ${dir}IBI.csv $mv_path/day-${day}/sub-01_day-${day}_device-e4_run-${run}_interbeatinterval.csv
    cp ${dir}tags.csv $mv_path/day-${day}/sub-01_day-${day}_device-e4_run-${run}_tags.csv
    cp ${dir}TEMP.csv $mv_path/day-${day}/sub-01_day-${day}_device-e4_run-${run}_temperature.csv
    
    cd ..
done
fi

if [ -d $path/SUB*/digital_biomarkers/aggregated_per_minute/ ] ; then
echo "EmbracePlus files found!"
dir=$path/SUB*/digital_biomarkers/aggregated_per_minute/
    cd $dir
    cp ${dir}1-1-SUB01*_eda.csv $mv_path/day-${day}/sub-01_day-${day}_device-embraceplus_electrodermal.csv
    cp ${dir}1-1-SUB01*_movement-intensity.csv $mv_path/day-${day}/sub-01_day-${day}_device-embraceplus_movement.csv
    cp ${dir}1-1-SUB01*_prv.csv $mv_path/day-${day}/sub-01_day-${day}_device-embraceplus_hrv.csv
    cp ${dir}1-1-SUB01*_pulse-rate.csv $mv_path/day-${day}/sub-01_day-${day}_device-embraceplus_hr.csv
    cp ${dir}1-1-SUB01*_respiratory-rate.csv $mv_path/day-${day}/sub-01_day-${day}_device-embraceplus_rr.csv
    cp ${dir}1-1-SUB01*_temperature.csv $mv_path/day-${day}/sub-01_day-${day}_device-embraceplus_temperature.csv
    cp ${dir}1-1-SUB01*_wearing-detection.csv $mv_path/day-${day}/sub-01_day-${day}_device-embraceplus_weartime.csv
fi
