#!/usr/bin/env python3
#from hlab_pytools.launch_ipcluster import ucsf_grid_job

from subprocess import call
import sys
import glob
import os
from pathlib import Path
import logging as log
log.basicConfig(stream=sys.stdout, level=log.DEBUG)

#print(os.system("which python"))

import pydicom
import argparse
import shutil
from zipfile import ZipFile
#import pdb

usage = """
input msid/tp 
currently written for single subject, use run_on_grid.py for batch processing
"""

log.info("1. Welcome to Neeb! I'll be processing the data you fed me nom nom.")

# print(os.listdir("/flywheel/v0/input"))
# print(os.listdir("/flywheel/v0/input/epi_bh30"))
# print(os.listdir("/flywheel/v0/input/MEGET2star"))
# print(os.listdir("/flywheel/v0/"))
# print(os.listdir("/flywheel/v0/output/"))

# prefix components:
space =  '    '
branch = "|   "
# pointers:
tee =    "├── "
last =   "└── "


def tree(dir_path=Path, prefix=''):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """    
    contents = list(dir_path.iterdir())
    # contents each get pointers that are with a final :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir(): # extend the prefix and recurse:
            extension = branch if pointer == tee else space 
            # i.e. space because last above so no more |
            yield from tree(path, prefix=prefix+extension)



def copy_files(input_dir, dest):
    if not os.path.isdir(dest):
        os.makedirs(dest)
    src_files = list(glob.glob(os.path.join(input_dir, "*.zip")))
    #print(os.listdir(input_dir))
    assert len(src_files) == 1, "multiple zip files in {0} input directory: {1}".format(input_dir, src_files)
    #print(src_files[0])
    with ZipFile(src_files[0], 'r') as myzip: #stops here bc its a directory
        #print("name list")
        #print(myzip.namelist())
        for file in myzip.namelist():
            myzip.extract(file, dest)
    #print(dest)
    # for file_name in src_files:
    #     print(file_name)
    #     full_file_name = os.path.join(src, file_name)
    #     if os.path.isfile(full_file_name):
    #         shutil.copy(full_file_name, dest)
#moving flywheel directories

copy_files("/flywheel/v0/input/epi_bh30", "/flywheel/v0/processing/E1/1")
copy_files("/flywheel/v0/input/epi_bh90", "/flywheel/v0/processing/E1/2")
copy_files("/flywheel/v0/input/epi_bb90", "/flywheel/v0/processing/E1/3")
copy_files("/flywheel/v0/input/MEGET1", "/flywheel/v0/processing/E1/4")
copy_files("/flywheel/v0/input/MEGET1_intensities", "/flywheel/v0/processing/E1/5")
copy_files("/flywheel/v0/input/MEGET2star", "/flywheel/v0/processing/E1/6")
copy_files("/flywheel/v0/input/MEGET2star_intensities", "/flywheel/v0/processing/E1/7")

if os.path.exists("/flywheel/v0/output/"):
    log.info("2. " + str(os.listdir("/flywheel/v0/output/")))
if os.path.exists("/flywheel/v0/processing/"):
    log.info("3. " + str(os.listdir("/flywheel/v0/processing/")))

#print(os.listdir("/flywheel/v0/processing/E1/1"))

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

def copy_output(src, dst, direc, symlinks=False, ignore=None):
    if not os.path.exists(direc):
        os.mkdir(direc)
    if os.path.isdir(src):
        shutil.copytree(src, dst, symlinks, ignore)
    else:
        shutil.copy2(src, dst)


# parser = argparse.ArgumentParser(description="Performs Neeb processing of specified time point")
# parser.add_argument("<subject_folder/time_pt>", help="subject folder")

# if len(sys.argv) < 2:
#     parser.print_help()
#     sys.exit(1)

patient_folder = "/flywheel/v0/processing/"

log.info("4. I just completed parsing your arguments! Let's see if we can find your data.")

if patient_folder in ['/data/henry6/EPIC8/ms0172/08', '/data/henry6/EPIC8/ms0241/09']:
    log.info("5. either missing or acquired wrong scans... cannot process Neeb")
    sys.exit(1)

# grab and arrange data
#print(patient_folder)
if(os.path.isdir(patient_folder)):
    if os.path.islink(patient_folder):
        log.info("6. Skipping... Time point directory is a symlink...")
        sys.exit(1)
    if os.path.exists(os.path.join(patient_folder,'Neeb')):
        log.info("7. Neeb directory already exists. If Neeb needs to be rerun, delete Neeb folder.")
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
            log.info("8. Non-integer named series... Deleting Neeb folder.")
            sys.exit(1)
        if(list_series):
            for series in list_series:
                #print(series)
                list_dicoms = sorted(glob.glob(series+'/*[dD][cC][mM]*'))
                #print(os.listdir(os.path.join(folder, series)))
                if "gz" in list_dicoms[0]:
                    call(['gunzip', list_dicoms[0]])
                    list_dicoms[0] = list_dicoms[0][:-3]
                ds = pydicom.dcmread(list_dicoms[0])
                if ("epi_bh90" in ds.SeriesDescription):
                    log.info("9. " + str(ds.SeriesDescription))
                    # call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/epi_highflip')])
                    #pdb.set_trace()
                    copytree(series, os.path.join(patient_folder,'Neeb/epi_highflip'))
                if ("epi_bh30" in ds.SeriesDescription):
                    log.info("10. " + str(ds.SeriesDescription))
                    call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/epi_lowflip')]) 
                if ("epi_bb90" in ds.SeriesDescription):
                    log.info("11. " + str(ds.SeriesDescription))
                    call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/epi_body')]) 
                if "MEGET2star" in ds.SeriesDescription:
                    log.info("12. " + str(ds.SeriesDescription))
                    if os.path.isdir(patient_folder+'/Neeb/gre_lowflip'):
                        call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/gre_lowflip_phase')]) 
                    else: 
                        call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/gre_lowflip')]) 
                if "MEGET1" in ds.SeriesDescription:
                    log.info("13. " + str(ds.SeriesDescription))
                    if os.path.isdir(patient_folder+'/Neeb/gre_highflip'):
                        pass
                    else: 
                        call(['cp', '-r', series, os.path.join(patient_folder,'Neeb/gre_highflip')]) 

if not glob.glob(os.path.join(patient_folder,'Neeb')+'/*'):
    log.info("14. no Neeb scans")
    call(['rmdir', os.path.join(patient_folder,'Neeb')])
    sys.exit(1)

zipped = glob.glob(os.path.join(patient_folder,'Neeb',"*")+'/*.gz')
if zipped:
    log.info("15. unzipping the following files: {0}".format(zipped))
    call(['gunzip']+zipped)
call(['/home/neeb_docker_utils/rename_files_neeb.py', os.path.join(patient_folder, 'Neeb')])

log.info("16. If you made it to this point that means I was able to acquire some data and will be processing it!")

# write processing list
processing_list = os.path.join(patient_folder, 'Neeb/Neeb_ProcessingList.txt')
patient_list = open(processing_list,'w')
lines = [patient_folder+'/Neeb/\n']
patient_list.writelines(lines)
patient_list.close()

log.info("17. I put the list of DICOMs that I'll be processing in Neeb/Neeb_ProcessingList.txt")

log.info("18. Starting processing now...")

# run Neeb processing
call(['/home/neeb_docker_utils/predictMS', processing_list, '/home/neeb_docker_utils/MyleinProcessingMatrix.txt', os.path.join(patient_folder,'Neeb/Neeb_RunInfo.txt'), os.path.join(patient_folder,'Neeb/Neeb_RunResults.txt')])
# print pid

call(['/home/neeb_docker_utils/convert_neeb_niftis3.py', os.path.join(patient_folder, 'Neeb')])

for line in tree(Path("/flywheel/v0/processing/Neeb")):
    log.info("19. " + str(line))

# print(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/H2OMaps/*.nii.gz'))[0])
# print(os.listdir(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/H2OMaps/'))[0]))

copy_output(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/Neeb_ProcessingList.txt'))[0], '/flywheel/v0/output/Neeb_ProcessingList.txt', '/flywheel/v0/output/')
copy_output(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/Myelin/MyelinMapsSmooth'))[0], '/flywheel/v0/output/Myelin/MyelinMapsSmooth', '/flywheel/v0/output/Myelin/')

copy_output(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/H2OMaps/*.nii.gz'))[0], '/flywheel/v0/output/H2OMaps/H2OMap.nii.gz', '/flywheel/v0/output/H2OMaps/')
copy_output(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/Myelin/MyelinMaps/*.nii.gz'))[0], '/flywheel/v0/output/Myelin/MyelinMaps/MyelinMaps.nii.gz', '/flywheel/v0/output/Myelin/MyelinMaps/')

copy_output(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/Myelin/T2Star_Fast/*.nii.gz'))[0], '/flywheel/v0/output/T2Star_Fast/T2Star_Fast.nii.gz', '/flywheel/v0/output/T2Star_Fast/')
copy_output(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/Myelin/T2Star_Slow/*.nii.gz'))[0], '/flywheel/v0/output/T2Star_Slow/T2Star_Slow.nii.gz', '/flywheel/v0/output/T2Star_Slow/')

copy_output(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/Neeb_RunInfo.txt'))[0], '/flywheel/v0/output/Neeb_RunInfo.txt', '/flywheel/v0/output/')
copy_output(glob.glob(os.path.join(patient_folder, '/flywheel/v0/processing/Neeb/Neeb_RunResults.txt'))[0], '/flywheel/v0/output/Neeb_RunResults.txt', '/flywheel/v0/output/')

log.info("20. ...all done processing! Until next time :)")
