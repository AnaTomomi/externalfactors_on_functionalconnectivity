#! user/bin/bash

day=$1
path=/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/sub-01/day-$day/behavioral;
cd $path

for filename in $(find . -name '*.zip');
do
    unzip -d "${filename%.zip}" "$filename"
    rm ${filename:2}
done

for dir in $path/*/
do
    cd $dir
    folder=$(basename $dir)
    run="${folder: -1}"
    
    mv ${dir}ACC.csv $path/sub-01_day-${day}_device-wristband_run-${run}_accelerometer.csv
    mv ${dir}BVP.csv $path/sub-01_day-${day}_device-wristband_run-${run}_photoplethysmograph.csv
    mv ${dir}EDA.csv $path/sub-01_day-${day}_device-wristband_run-${run}_electrodermal.csv
    mv ${dir}HR.csv $path/sub-01_day-${day}_device-wristband_run-${run}_hr.csv
    mv ${dir}IBI.csv $path/sub-01_day-${day}_device-wristband_run-${run}_interbeatinterval.csv
    mv ${dir}tags.csv $path/sub-01_day-${day}_device-wristband_run-${run}_tags.csv
    mv ${dir}TEMP.csv $path/sub-01_day-${day}_device-wristband_run-${run}_temperature.csv
    
    cd ..
    rm -R ${dir}
done
