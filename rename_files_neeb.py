#!/usr/bin/env python
from subprocess import call
import sys
import glob
import os

folder = sys.argv[1]
list_series = glob.glob(folder+'/*')

for series in list_series:

    list_files = sorted(glob.glob(series+'/*[dD][cC][mM]*'))
    print("files listed below")
    print(list_files)
    for filename in list_files:
        print(filename)
        
        sans_type = os.path.basename(filename).split('.')[0]
        
        if "-" in os.path.basename(list_files[0]):
            number = int(sans_type.split('-')[-1])
        else:
            number = int(sans_type.split('I')[-1][-4:])

        print(series+'/File_anon'+('%04d' % number)+'.ima')
        call(['mv', filename, series+'/File_anon'+('%04d' % number)+'.ima'])
