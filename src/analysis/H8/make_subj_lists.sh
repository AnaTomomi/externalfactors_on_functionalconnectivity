a=0;
for n in task-movie_SGdetrend_24HMP-8Phys-4GSR-Spike_HPF_smooth-6mm.nii task-movie_SGdetrend_24HMP-8Phys-Spike_HPF.nii task-movie_SGdetrend_24HMP-8Phys-4GSR-Spike_HPF.nii task-movie_SGdetrend_24HMP-8Phys-Spike_HPF_smooth-6mm.nii; do 
	echo $n
    echo "subjs={" > "subjects"$a".m"
	find /m/cs/scratch/networks-pm/pm_denoise/|grep $n|sort|sed "s/^/'/g"|sed "s/$/'/g" >>  "subjects"$a".m"
	echo "};" >>  "subjects"$a".m"
	let a=a+1
done

