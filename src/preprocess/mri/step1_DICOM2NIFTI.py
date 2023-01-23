"""
This script converts DICOM files to NIFTI and organizes the files in pseudo-BIDS format.

Requirements: 
            - DICOM files organized and labeled as #_sequence (e.g. 5_EPI). No subfolders! 
            See step0_organize_mrifiles.sh for inspiration
            - dcm2niix installed in a folder that can be accessed by the user. 

Outputs: - NIFTI and JSON files in the specified folder. 

If you need help on the order of BIDS labels, please see https://docs.flywheel.io/hc/en-us/articles/360017426934-How-do-I-name-scan-acquisitions-so-they-can-be-in-BIDS-format-in-Flywheel-

@author: ana.trianahoyos@aalto.fi
Created: 16.02.2021
Modified: 09.07.2021 Include more labels in the names
Modified: 20.01.2023 Include new folder definitions according to AMI, include exceptions for angiography
"""

################################## User input needed ##########################
# Please modify this part 
datapath = '/m/cs/archive/networks-pm/mri'
savepath = '/m/cs/project/networks-pm/mri/fast_prepro_bids'
dcm2niix_path = '/m/cs/scratch/networks-pm/software/dcm2niix/build/bin/dcm2niix'
date = '20230123'
subject = 'sub-03'

###############################################################################

# No major modifications required! Modify if you are sure or need another sequence.
import os

#Prepare the paths and batch convert all that was scanned in the session
folder = os.path.join(datapath, date)

subfolders = next(os.walk(folder))[1]
subfolders.sort()
if len(subfolders)==0:
    raise NameError('The folder does not have any DICOM images')

#Create the order of sequences and tasks for the names
sequences = {}
tasks = {}
epi_counter = 1
for item in subfolders:
    key = item.split('_')[0]
    value = item.split('_')[1]
    sequences[key] = value
    if value=='EPI' and epi_counter==1:
        tasks[key] = 'pvt'
        epi_counter = epi_counter+1
    elif value=='EPI' and epi_counter==2:
        tasks[key] = 'resting'
        epi_counter = epi_counter+1
    elif value=='EPI' and epi_counter==3:
        tasks[key] = 'movie'
        epi_counter = epi_counter+1
    elif value=='EPI' and epi_counter==4:
        tasks[key] = 'nback'
        epi_counter = epi_counter+1
    else:
        tasks[key] = value
           
if len(subfolders)!=len(sequences):
    raise NameError('Number of sequences does not match the number of subfolders. Please check the sequences.')
if len(subfolders)!=len(tasks):
    raise NameError('Number of sequences does not match the number of tasks. Please check the tasks.')
if len(tasks)!=len(sequences):
    raise NameError('Number of sequences does not match the number of tasks. Please check the sequences and the tasks.')

#Assign names automatically
print("Starting DICOM to NIFTI conversion...")
for sequence_key, task_key in zip(sequences,tasks):
    if sequences[sequence_key]=='localizer':
        print("Localizers are not converted")
        continue
    elif sequences[sequence_key]=='T1':
        in_folder = os.path.join(folder,f'{sequence_key}_{sequences[sequence_key]}')
        out_folder = os.path.join(savepath,subject,"anat")
        filename = f'{subject}_T1w'
    elif sequences[sequence_key]=='T2':
        in_folder = os.path.join(folder,f'{sequence_key}_{sequences[sequence_key]}')
        out_folder = os.path.join(savepath,subject,"anat")
        filename = f'{subject}_T2w'
    elif sequences[sequence_key]=='EPI':
        in_folder = os.path.join(folder,f'{sequence_key}_{sequences[sequence_key]}')
        out_folder = os.path.join(savepath,subject,"func")
        filename = f'{subject}_task-{tasks[task_key]}_bold'
    elif sequences[sequence_key]=='DTI':
        print("Diffusion not yet supported")
        continue
    elif sequences[sequence_key]=='DTI2':
        print("Diffusion not yet supported")
        continue
    elif sequences[sequence_key]=='angio':
        print("Diffusion not yet supported")
        continue
    else:
       raise NameError('Sequence type not found, please add it to the script')
    
    #Start the conversion
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder)
    if not os.path.isfile(os.path.join(out_folder,filename+".nii")):
        command =  f'{dcm2niix_path} -z n -b y -f {filename} -o {out_folder} {in_folder}'
        print(command)
        os.system(command)
    else:
        print("the file already exists. Please check the folders. No conversion is done.")

print("Conversion finnished!")
