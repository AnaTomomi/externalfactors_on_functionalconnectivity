#!/bin/bash
#SBATCH --time=02:30:00
#SBATCH --mem=500M
#SBATCH --array=1-210
#SBATCH --output=/m/cs/scratch/networks-pm/jobs/decoder-%A_%a.out
#SBATCH --cpus-per-task=1

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

echo randomise -i ./data/mri/decoder/decoder_24HMP-8Phys-Spike_HPF_TRw25_step-1_subjects-1.nii -o ./results/H8/1TR/${array[2]}_24HMP-8Phys-Spike_HPF_TRw25_step-1_subjects-1 -d ./data/mri/decoder/${array[0]}_${array[2]}_design.mat -t ./data/mri/decoder/contrast.con  -m ./data/mri/conn_matrix/${array[0]}/group_mask_mult.nii -n 10000 -T -D

randomise -i ./data/mri/decoder/decoder_24HMP-8Phys-Spike_HPF_TRw25_step-1_subjects-1.nii -o ./results/H8/1TR/${array[2]}_24HMP-8Phys-Spike_HPF_TRw25_step-1_subjects-1 -d ./data/mri/decoder/${array[0]}_${array[2]}_design.mat -t ./data/mri/decoder/contrast.con  -m ./data/mri/conn_matrix/${array[0]}/group_mask_mult.nii -n 10000 -T -D
