#!/bin/bash 
#SBATCH --time=1-00:00:00
#SBATCH --array=1-91
#SBATCH --mem=38G
#SBATCH --cpus-per-task=10

module load matlab

x=${SLURM_ARRAY_TASK_ID}

matlab -r "run_decode_par($x,25,1,1,'ISCout1','decode_ISCout1_25_1_1') ; exit(0)"
