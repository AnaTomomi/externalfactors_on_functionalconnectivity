# Documentation for reusing the code and reproducing the results

In this folder a series of matlab, bash, and slurm files to

1) memory-map all fMRI movie data and compute inter-subject correlation using the isc-toolbox https://www.nitrc.org/projects/isc-toolbox/
2) compute leave one subject out decoding as described in the paper in a serial manner (slow) and in parallel using slurm on HPC (fast)
3) compute leave a percentage of subjects out

**Q: Why Matlab?**
*Some technical considerations based on personal experience in favour of Matlab isc-toolbox*
When working with voxelwise inter-subject correlation, ISC matrices need to be computed for each voxel. To do so, one needs to load the specific voxel time series for all subjects and compute the correlation matrix across subjects. To reduce I/O one could load all subjects in memory, but this requires a very large amount of RAM. Alternatively, one could load only the voxel time series of interest for each subject, but this results in a very large amount of I/O operations. The Matlab isc-toolbox efficiently uses memory-mapping to map the original fMRI data as binarized memory-mapped data. This results in an acceptable amount of I/O and low RAM usage. The voxelwise decoding approach used in this study suffers from the same I/O vs memory trade-off, and for this reason the memory-mapping performed by the isc-toolbox is used.


# Stage 1 - memory-mapping the data and compute intersubject correlations
The first stage is to memory-map all fMRI movie data and compute inter-subject correlation using the isc-toolbox https://www.nitrc.org/projects/isc-toolbox/. First we run the script `step1_make_subj_lists.sh` that generates the files `subjects[0-3].m` with the corresponding filesystem locations of the preprocessed fMRI movie data with various post-fmriprep strategies. Note that for the decoding stages, we will use only unsmoothed data as recommended by the original study that proposed the method. To then compute the inter-subject correlation, the script `step2_ISC.m` is run. The script requires the isc-toolbox which is downloadable at the link above.

# Stage 2 - computing leave-one-session out decoding
Then, the actual decoding happens. The algorithm works briefly like this:

1) consider the voxel BOLD time series in a sphere with radius 10mm
2) leave one subject out (in our case "one session out") and use the remaining N-1 subjects to compute an average time series for each voxel in the sphere of interest
3) split the data in multiple overlapping sliding windows of 25TRs with sliding steps of 1, 2, and 4 TRs.
4) now compute the similarity between the sliding windows of the subject that was left out and the sliding windows of the "average other subjects". Note that now we compute also the similarity between windows at different time points
5) The final correlation matrix has all possible similarities between every time window of left-out-subject and average-other-subjects. The decoding "happens" so that we are able to identify the right time point for the left-out subject, using the average-other-subjects. Which means that if the maximum correlation is on the diagonal of the cross correlation matrix, then we have successfully "decoded" the time point of the left-out-subject.
6) We then look at all time windows and count how many successful decoding (= on the diagonal) we obtained.
7) We repeat this so that all subjects will be left out once and obtain an average score of successful decoding.

To run this stage we first need to identify the 10mm radius spheres in the standard MNI space. This is done only once and the output (`sphoutMAT_v2.mat`) is used by the scripts, without recomputing the spheres. To generate the file, you need to then first run the script `make_spheres.m`.

Now we can finally compute the decoding accuracy for each sphere centered at every voxel, by going through each voxel in the 2mm MNI space. As you can imagine, some voxels will be outside of the brain mask, and so the script will skip those spheres. The script `run_decode.m` will do exactly this. The actual decoding is delegated to a function `decode_success.m` which will take care of computing the cross-correlation matrix and identify the successfully decoded time-windows. This approach has no parallelization and so it can easily take a few months to go through all voxels (for one run of the script only). 

Since waiting for a year to analyse the data was not a feasible option, parallelisation was added in the script `run_decode_par.m` and the corresponding function `decode_success_par.m`. There are two types of parallelisation happening here: within the function, a parfor loop has been introduced so that the N subjects left out are processed in parallel. A further level of parallelization across computers was also achieved using slurm over an HPC cluster. Basically the script `run_decode_par.m` was turned into a function so that it accepts the number of slide x, so that slurm can run 91 parallel computations for each slide in the x direction (in MNI 2mm space the size of the xyz volume is 91,109,91). With these two levels of parallelisation, the months of computing were reduced to only a few days.

# Stage 3 - computing leave-some-subjects out decoding
In our study we also looked at leaving a percentage of subjects out, rather than just the "leave one out" approach. To achieve this we had to introduce a percentage parameter in our functions so that only a subset of the subjects is used to compute the "average-other-subjects" signals. Since there are multiple ways of picking a subset of subjects, we iterated the process 100 times. Running it for the whole brain would have then required around 150-300 days since each of the 100 iterations would have run over slurm as explained in the section before. We then decided to only run this for three regions of interest to show the feasibility of our approach and to also demonstrate that, in practice, the average decoding accuracy with this approach is almost identical to the leave-one-subject out approach. For running this over a single roi, we used the script `run_roi_decoding.m` which then calls the function `run_decode_xyz.m` that is then calling the function `decode_success_par_new.m` which performs the decoding over a subset of the subjects.

# Future improvements
1) Inline documentation: the code would benefit from more inline comments. In the spirit of openness, we released it as it is, and if readers find this useful, we are happy to accept pull requests and further improvements
2) code refactoring: right now stage 2 and stage 3 contain highly similar scripts that achieve the same purpose but with different strategies. One could refactor all the scripts into a main function that, depending on the flavour (parfor or not, slurm or not, leave one out or leave percentage out, ...) it would then pick the right configuration to run.
3) Methodologically this code is written following the original python code at https://github.com/mvdoc/budapest-fmri-data/blob/master/scripts/hyperalignment-and-decoding/decoding_segments_splits.py, the main difference being that in our analysis we are dealing with volumetric data, while in the Budapest-fmri project cortical data was mapped into surface format. A rewrite in python of our code is possible, but we took advantage of the isc-toolbox efficient data management.
4) Paths: in the code there are some hardcoded paths and local relative paths. If you follow the git structure, you need to edit the pahts. There is an example in the code to generate supplenetary figure 41 in script `run_roi_decoding.m`
