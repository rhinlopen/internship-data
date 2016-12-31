# Shape of the program:
#   First find all files in the split directory to be analysed.
#   For each, split it into runs and read the data (field, time, x, y, temperature)
#   
#   Interpolate the data for linear 1/field and find the optimal theta (max 1aX peak).
#   Use another (higher) padfactor to determine the optimal fft.
#
#   From this fft, determine the alpha, beta peaks.
#       first 3 highest peaks are 1alpha
#       next filter max of max of the FFT to find potential peaks
#       filter out the alpha harmonics
#       the rest forms beta, group higher harmonics.
#   Save alpha, beta, all settings involved

import time
import os
import numpy as np

from E1_file_master import delete
import B3_ab as ab

import F0_set as set
import F2_fft as input
import F1_generalised as general
import F4_save as save

# Assertions
def assert_analyse (command):
    
    valid = command.__class__ == list
    valid = valid and len(command) > 0 
    valid = valid and command[0] == 'analyse'

    valid1 = valid and len(command) == 1
    
    valid2 = valid and len(command) == 2
    valid2 = valid2 and general.can_type(command[1], float)
    valid2 = valid2 and round(float(command[1])*10)/10 == float(command[1])

    valid3 = valid and len(command) == 3
    valid3 = valid3 and general.can_type(command[1], int)
    valid3 = valid3 and general.can_type(command[2], int)
    valid3 = valid3 and int(command[1]) < int(command[2])
    valid3 = valid3 and int(command[1]) >= 0

    return valid1 or valid2 or valid3

# Help functions
def initiate_infiles (command):
    #   precondition
    assert(assert_analyse(command))
    #   postcondition
    # return list of .dat files in the split directory to be analysed

    files = os.listdir (set.directories ('split'))
    all_files = []
    data_files = []

    #select dat files
    for file in files:
        if file[-4:] == '.dat':
            all_files.append(file)
    
    #select Julian data files with the correct index (if specified).
    for file in all_files:
        nums = general.find_numbers (file, 2, int)
        assert(file == 'Julian_' + str(nums[0]) + '_' + str(nums[1]) + '.dat')

        if len(command) == 1:
            data_files.append(file)
        elif len(command) == 2 and float(command[1]) == nums[0] + (nums[1]/10)%1:
            data_files.append(file)
        elif len(command) == 2 and general.can_type(command[1], int) \
         and nums[0] == int(command[1]) \
         and int(general.string_round(int(command[1]), 1)[-1]) == 0:
            data_files.append(file)
        elif len(command) == 3 and int(command[1]) <= nums[0] and nums[0] <= int(command[2]):
            data_files.append(file)

    return data_files

def print_progress (percentage, start_time):
    #   precondition
    assert(general.can_type(percentage, float))
    assert(start_time.__class__ == float)
    #   postcondition
    # Print progress.
    
    if percentage == 0:
        return

    to_print =  'Busy for '
    to_print += general.string_round (time.time() - start_time, 1)
    to_print += ' seconds: analysis at '
    to_print += general.string_round (percentage, 2) + '%'
    print(to_print)
    return

# Analyse functions
def analyse_one (path):
    #   precondition
    assert(os.path.isfile(path))
    #   postcondition
    # Derive FFT, Alpha, Beta and create the peaksfile. 

    settings        = [set.settings('interpolated_points'), set.settings('pad')]
    index, run_nr   = general.find_numbers(path, 99, int)[-2:]
    inter_points    = set.settings('interpolated_points')
    pad_fft         = set.settings('pad')
    type            = 'auto'

    fft_opt, field_range, theta, temperature  = input.fft (index, run_nr, -1, settings, 1) 
    alpha, beta     = ab.derive (fft_opt)

    InPTTTF = [inter_points, pad_fft, type, temperature, theta, 1]
    save.peaks('out', index, run_nr, field_range, alpha, beta, InPTTTF) 
    return 

def analyse (command):
    #   precondition
    assert(assert_analyse(command))
    #   postcondition
    # Analyse all files in the directory.

    # Find files
    start_time = time.time()
    data_files = initiate_infiles (command)

    if len(data_files) == 0:
        print('No matching files found to analyse.')
        return

    # Analyse files
    for i in range(len(data_files)):
        print_progress (i / (1.*len(data_files)) * 100, start_time)
        path = set.directories('split') + data_files[i]
        nums = general.find_numbers(path, 99, int)[-2:]
        print('Starting with file', nums[0], 'run', nums[1])

        analyse_one (path)

    print('Analysis of ' + str(len(data_files)) + ' runs finished.')
    return