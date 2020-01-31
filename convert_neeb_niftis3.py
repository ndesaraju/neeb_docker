#!/usr/bin/env python
from subprocess import call
import glob
import os
import sys
import logging as log

subjects = sys.argv[1:]
# ms????/0?/Neeb/

def main(subject):
    folders = sorted(glob.glob(subject+'/*'))
    for folder in folders:
        #print(folder)
        contents = glob.glob(folder+'/*')
        if contents and ("ima" in contents[0]): # "ima"
            files = glob.glob(folder+'/*.ima') # ".ima
            if (files):
                rename(files)
                call(['/home/neeb_docker_utils/dcmgz2nii', '-o', folder, folder])
        else:
            for content in contents:
                files = glob.glob(content+'/*.ima') # "ima"
                if(files):
                    rename(files)
                    call(['/home/neeb_docker_utils/dcmgz2nii', '-o', content, content])
    return

def rename(files):
    for file in files:
        call(['mv', file, os.path.join(os.path.dirname(file), os.path.basename(file).split('.')[0]+'.DCM')])
    return

def smooth_maps(subject):
    myelin = glob.glob(subject+'/Myelin/MyelinMaps/*.nii.gz')[0]
    for mm in [0.5, 0.8, 1]:
        call(['/home/neeb_docker_utils/fslmaths', myelin, '-s', str(mm), subject+'/Myelin/MyelinMapsSmooth/MyelinMap_Smoothed_'+('%02d' % int(mm*10))+'.nii.gz'])

for subject in subjects:
    subject = os.path.abspath(subject)
    #print(subject)
    main(subject)
    smooth_maps(subject)


