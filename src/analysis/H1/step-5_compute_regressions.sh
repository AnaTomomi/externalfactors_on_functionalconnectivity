#!/bin/bash
#SBATCH --time=00:10:00
#SBATCH --mem=16G
#SBATCH --array=1-12
#SBATCH --output=/m/cs/scratch/networks-pm/jobs/H1regress-%j.out
#SBATCH --cpus-per-task=4

n=$SLURM_ARRAY_TASK_ID
variants=`sed "${n}q;d" options.txt`

module load r
Rscript /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H1/eff.R $variants
Rscript /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H1/pc.R $variants
#Rscript /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H1/links.R $variants
