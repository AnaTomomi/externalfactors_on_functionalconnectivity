#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --mem=20G
#SBATCH --array=11-24
#SBATCH --output=/m/cs/scratch/networks-pm/jobs/glm-%j.out
#SBATCH --cpus-per-task=4

n=$SLURM_ARRAY_TASK_ID
variants=`sed "${n}q;d" variants.txt`
IFS=' ' read -a array <<< "$variants"

cd /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity

module load fsl
source $FSLDIR/etc/fslconf/fsl.sh

echo "For the array $n"
echo "task=${array[0]}"
echo "strategy=${array[1]}"
echo "variable=${array[2]}"

echo randomise -i ./results/supplementary/${array[0]}_glm-first_${array[1]}_include-thresholds.nii -o ./results/supplementary/${array[0]}_${array[2]}_glm-second_${array[1]}_include-thresholds -d ./data/mri/glm/${array[0]}_${array[2]}_design.mat -t ./data/mri/glm/contrast.con  -m ./data/mri/conn_matrix/${array[0]}/group_mask_mult.nii -n 10000 -T -D

randomise -i ./results/supplementary/${array[0]}_glm-first_${array[1]}_include-thresholds.nii -o ./results/supplementary/${array[0]}_${array[2]}_glm-second_${array[1]}_include-thresholds -d ./data/mri/glm/${array[0]}_${array[2]}_design.mat -t ./data/mri/glm/contrast.con  -m ./data/mri/conn_matrix/${array[0]}/group_mask_mult.nii -n 10000 -T -D
