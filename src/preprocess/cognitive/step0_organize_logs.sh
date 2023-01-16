#! user/bin/bash

day=$1
path=/m/cs/archive/networks-pm/cognitive;
mv_path=/m/cs/project/networks-pm/cognitive;

cp ${path}/sub-01_day-${day}_task-_1back_rawdata.txt ${mv_path}/sub-01_day-${day}_task-nback_run-1_pres.txt
cp ${path}/sub-01_day-${day}_task-_1back_summary.txt ${mv_path}/sub-01_day-${day}_task-nback_run-1_pres-summary.txt
cp ${path}/sub-01_day-${day}_task-_2back_rawdata.txt ${mv_path}/sub-01_day-${day}_task-nback_run-2_pres.txt
cp ${path}/sub-01_day-${day}_task-_2back_summary.txt ${mv_path}/sub-01_day-${day}_task-nback_run-2_pres-summary.txt
cp ${path}/sub-01_day-${day}_task--Nback.log ${mv_path}/sub-01_day-${day}_task-nback_run-0_pres.log
cp ${path}/sub-01_day-${day}_task-_pvt_log.txt ${mv_path}/sub-01_day-${day}_task-pvt_log.txt
cp ${path}/sub-01_day-${day}_task-_pvt_summary.txt ${mv_path}/sub-01_day-${day}_task-pvt_summary.txt
cp ${path}/sub-01_day-${day}_task--pvt.log ${mv_path}/sub-01_day-${day}_task-pvt_log.log

echo "files organized!"
