#!/usr/bin/env python
from subprocess import call
import sys
import glob
import os
import logging as log

folder = sys.argv[1]
list_series = glob.glob(folder+'/*')

for series in list_series:

    list_files = sorted(glob.glob(series+'/*[dD][cC][mM]*'))
    count = 1
    for filename in list_files:
        print(filename)
        
        # sans_type = os.path.basename(filename).split('.')[0]
        
        # if "-" in os.path.basename(list_files[0]):
        #     number = int(sans_type.split('-')[-1])
        # else:
        #     number = int(sans_type.split('I')[-1][-4:])

        anon_name = 'File_anon'+('%04d' % count)+'.ima'
        new_path = os.path.join(series, anon_name)
        print("new path: {0}".format(new_path))
        print("series: {0}".format(series))
        log.info("Renaming {0} to {1}".format(filename, new_path))
        call(['mv', filename, new_path])
        count += 1
