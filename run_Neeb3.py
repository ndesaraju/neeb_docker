#!/usr/bin/env python
#from hlab_pytools.launch_ipcluster import ucsf_grid_job

from subprocess import call
import sys
import glob
import os

print(os.system("which python"))

import pydicom
import argparse
import shutil
#import pdb

usage = """
input msid/tp 
currently written for single subject, use run_on_grid.py for batch processing
"""

print("Welcome to Neeb! I'll be processing the data you fed me nom nom.")

def copytree(src, dst, symlinks=False, ignore=None):
    # taken from https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
    if not os.path.exists(dst):
        os.mkdir(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

parser = argparse.ArgumentParser(description="Performs Neeb processing of specified time point")
parser.add_argument("<subject_folder/time_pt>", help="subject folder")

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

patient_folder = os.path.abspath(sys.argv[1])

print("I just completed parsing your arguments! Let's see if we can find your data.")

if patient_folder in ['/data/henry6/EPIC8/ms0172/08', '/data/henry6/EPIC8/ms0241/09']:
    print ("either missing or acquired wrong scans... cannot process Neeb")
    sys.exit(1)

# grab and arrange data
print(patient_folder)
if(os.path.isdir(patient_folder)):
    if os.path.islink(patient_folder):
        print ("Skipping... Time point directory is a symlink...")
        sys.exit(1)
    if os.path.exists(os.path.join(patient_folder,'Neeb')):
        print ("Neeb directory already exists. If Neeb needs to be rerun, delete Neeb folder.")
        sys.exit(1)
    os.mkdir(os.path.join(patient_folder,'Neeb'))
    dicom_folder = sorted(glob.glob(patient_folder+'/E*'))
    if not dicom_folder:
        sys.exit(1)
    for folder in dicom_folder:
        try:
            list_series = [os.path.basename(i) for i in glob.glob(folder+"/[0-9]*")]
            list_series = sorted(list_series, key=int)
            list_series = ['{}/{}'.format(folder, i) for i in list_series]
        except:
            call(['rmdir', os.path.join(patient_folder,'Neeb')])
            print ("Non-integer named series... Deleting Neeb folder.")
            sys.exit(1)
        if(list_series):
            for series in list_series:
                print(series)
                list_dicoms = sorted(glob.glob(series+'/*[dD][cC][mM]*'))
                if "gz" in list_dicoms[0]:
                    call(['gunzip', list_dicoms[0]])
                    list_dicoms[0] = list_dicoms[0][:-3]
                ds = pydicom.dcmread(list_dicoms[0])
                if ("epi_bh90" in ds.SeriesDescription):
                    print(ds.SeriesDescription)
                    # call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/epi_highflip')])
                    #pdb.set_trace()
                    copytree(series, os.path.join(patient_folder,'Neeb/epi_highflip'))
                if ("epi_bh30" in ds.SeriesDescription):
                    print(ds.SeriesDescription)
                    call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/epi_lowflip')]) 
                if ("epi_bb90" in ds.SeriesDescription):
                    print(ds.SeriesDescription)
                    call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/epi_body')]) 
                if "MEGET2star" in ds.SeriesDescription:
                    print(ds.SeriesDescription)
                    if os.path.isdir(patient_folder+'/Neeb/gre_lowflip'):
                        call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/gre_lowflip_phase')]) 
                    else: 
                        call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/gre_lowflip')]) 
                if "MEGET1" in ds.SeriesDescription:
                    print(ds.SeriesDescription)
                    if os.path.isdir(patient_folder+'/Neeb/gre_highflip'):
                        pass
                    else: 
                        call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/gre_highflip')]) 

if not glob.glob(os.path.join(patient_folder,'Neeb')+'/*'):
    print ("no Neeb scans")
    call(['rmdir', os.path.join(patient_folder,'Neeb')])
    sys.exit(1)

zipped = glob.glob(os.path.join(patient_folder,'Neeb',"*")+'/*.gz')
if zipped:
    print("unzipping the following files: {0}".format(zipped))
    call(['gunzip']+zipped)
call(['/home/neeb_docker_utils/rename_files_neeb.py', os.path.join(patient_folder, 'Neeb')])

print("If you made it to this point that means I was able to acquire some data and will be processing it!")

# write processing list
processing_list = os.path.join(patient_folder, 'Neeb/Neeb_ProcessingList.txt')
patient_list = open(processing_list,'w')
lines = [patient_folder+'/Neeb/\n']
patient_list.writelines(lines)
patient_list.close()

print("I put the list of DICOMs that I'll be processing in Neeb/Neeb_ProcessingList.txt")

print("Starting processing now...")

# run Neeb processing
call(['/home/neeb_docker_utils/predictMS', processing_list, '/home/neeb_docker_utils/MyleinProcessingMatrix.txt', os.path.join(patient_folder,'Neeb/Neeb_RunInfo.txt'), os.path.join(patient_folder,'Neeb/Neeb_RunResults.txt')])
# print pid

call(['/neeb_docker_utils/convert_neeb_niftis3.py', os.path.join(patient_folder, 'Neeb')])

print("...all done processing! Until next time :)")
