import numpy as np
import os
import shutil

import F1_generalised as general

# Group 1: Settings.
def settings (var):
    #   precondition
    assert(var.__class__ == str)
    #   postcondition
    # return the setting.
 
    if (var == 'field_ranges'):
        # which field ranges are interesting, runs will be cut to match these.
        return [ [4.7,5.3], [5.4,5.6], [6.0,6.3] ]
    elif (var == 'pad'):
        # Total length after padding and interpolating for the resulting FFT.
        # Higher costs more FFT time.
        # Lower causes larger freq steps, thus more data loss due to FFT 
            # (steps ~1 T for pad factor 2**7, field 6-6.3).
        return 2**24
    elif (var == 'interpolated_points'):
        # Total length after interpolating directly after import.
        # Higher costs anti-background time.
        # Higher causes bigger freq steps 
            # (steps ~1 T for pad factor 2**7, field 6-6.3).
        # Lower causes less accurate data interpolation.
        return 2**17
    elif (var == 'max_freq'):
        # Above this frequency, ignore eveything.
        return 30000
    elif (var == 'max_base_freq'):
        # Above this frequency, do not derive base peaks.
        return 17500

    print('Could not find setting:', var)
    return

def directories (ind):
    #   precondition
    assert(ind.__class__ == str)
    #   postcondition
    # Return the full path of the right directory.

    if ind == 'in' or ind == '0':
        return 'c:/Users/rhinl/Documents/001_Studie/Jaar3/005_Stage/010 Input/'
    
    elif ind == 'split' or ind == '1':
        return 'c:/Users/rhinl/Documents/001_Studie/Jaar3/005_Stage/011 Split/'

    elif ind == 'out' or ind == '2':
        return 'c:/Users/rhinl/Documents/001_Studie/Jaar3/005_Stage/012 Output/'
    
    elif ind == 'user' or ind == '3':
        return 'c:/Users/rhinl/Documents/001_Studie/Jaar3/005_Stage/013 User Analysis/'

    elif ind == 'delete' or ind == '4':
        return 'c:/Users/rhinl/Documents/001_Studie/Jaar3/005_Stage/014 Recycle Bin/'

    else:
        return

def standard_types ():

    types = []
    types.append('done')
    types.append('broad')
    types.append('alix')

    types.append('freqshift')
    types.append('re-temp')
    types.append('check')

    types.append('queue')
    types.append('auto')
    types.append('redo')
    types.append('bad')

    return types

# Group 2: check all settings, directories, files.
def initiate_directories ():
    dirs = 5

    # directories exist:
    try:
        for i in range(dirs):
            os.chdir(directories(str(i)))
    except:
        print('one or more directories in settings did not exist.')
        return False

    if directories(str(dirs)) != None:
        print('more directories exist than checked.')
        print('Fix your dirs or initiate_directory.')
        return False

    # each file in every directory other than input has exactly 
    # 2 integer indices classifying it for operations
    files = os.listdir(directories('in'))
    for file in files:
        if len(general.find_numbers(file, 2, int)) != 1:
            print('Illegal file in input directory:', file)
            return False
    
    for i in range(dirs-1):
        dir = directories(str(i+1))
        files = os.listdir(dir)
        for file in files:
            if len(general.find_numbers(file, 3, int)) != 2:
                print('Found an illegal file while initiating.')
                print('directory', dir, '\nfile', file)
                return False

    return True

def check_settings ():

    # Field
    valid = settings('field_ranges').__class__ == list
    i = 0
    while valid and i < len(settings('field_ranges')):
        valid = valid and settings('field_ranges')[i].__class__ == list
        valid = valid and len(settings('field_ranges')[i]) == 2
        valid = valid and general.can_type(settings('field_ranges')[i][0], float)
        valid = valid and general.can_type(settings('field_ranges')[i][1], float)
        i += 1

    # Pad*3
    valid = valid and settings('pad').__class__ == int
    valid = valid and settings('pad') > 0
    valid = valid and np.log2(settings('pad')) == int(np.log2(settings('pad')))

    valid = valid and settings('interpolated_points').__class__ == int
    valid = valid and settings('interpolated_points') > 0
    valid = valid and np.log2(settings('interpolated_points')) \
                    == int(np.log2(settings('interpolated_points')))

    # Freq*2
    valid = valid and settings('max_freq').__class__ == int
    valid = valid and settings('max_freq') > 10000
    valid = valid and settings('max_base_freq').__class__ == int
    valid = valid and settings('max_base_freq') > 10000

    return valid

def initiate ():
    #   precondition
    assert(True)
    #   postcondition
    # Result true if and only if all settings and directories are entered correctly.

    if not check_settings():
        print('One or more settings are invalid. Fix them before running the program.')
        return False

    if not initiate_directories():
        print('One or more directiories were not found. Fix this before running the program.')
        return False

    return True
