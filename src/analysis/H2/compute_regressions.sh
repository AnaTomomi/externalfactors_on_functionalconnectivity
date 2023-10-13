#!/bin/bash
#SBATCH --time=08:00:00
#SBATCH --mem=20G
#SBATCH --array=1-4
#SBATCH --output=/m/cs/scratch/networks-pm/jobs/H2regress-%j.out
#SBATCH --cpus-per-task=4

n=$SLURM_ARRAY_TASK_ID
variants=`sed "${n}q;d" options.txt`

module load r
Rscript /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H2/eff_pc.R $variants
Rscript /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H2/pc.R $variants
Rscript /m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis/H2/links.R $variants
