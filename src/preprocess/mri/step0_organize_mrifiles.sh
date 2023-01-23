#! user/bin/bash

date=$1
path=/m/cs/archive/networks-pm/mri/$date;

cd $path

if [ ! -d $path/$date ] ; then 
    echo "unzipping files..."
    for filename in $(find . -name '*.zip');
    do
        unzip -d "${filename%.zip}" "$filename"
    done
fi

for folder in $(find -maxdepth 4 -mindepth 4 -type d ); 
do
    sequence=$(basename $folder)
    if [[ $sequence =~ "localizer" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_localizer
        echo "copying localizer \n"
    elif [[ $sequence =~ "Timo_SMS" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_EPI
        echo "copying EPIs \n"
    elif [[ $sequence =~ "MPRAGE" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_T1
        echo "copying T1 \n"
    elif [[ $sequence =~ "t2" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_T2
        echo "copying T2 \n"
    elif [[ $sequence =~ "b0s" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_DTI
        echo "copying DTI \n"
    elif [[ $sequence =~ "A__P" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_DTI2
        echo "copying DTI \n"
    elif [[ $sequence =~ "multi_slab" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_angio
        echo "copying angiography \n"
    elif [[ $sequence =~ "MIP_SAG" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_angio_sag
        echo "copying saggital \n"
    elif [[ $sequence =~ "MIP_COR" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_angio_cor
        echo "copying coronal \n"
    elif [[ $sequence =~ "MIP_TRA" ]]; then
        number=`echo ${sequence} | cut -b 1`
        cp -R ${folder}/resources/DICOM/files ${path}/${number}_angio_tra
    fi
done

rm -r ${path}/${date}
