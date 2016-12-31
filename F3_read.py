import time 
import os
import numpy as np

import F0_set as set
import F1_generalised as general
import F2_fft as input0

# Assertions
def assert_lines(lines):

    valid = lines.__class__ == list
    valid = valid and len(lines) > 0

    if not valid:
        return valid

    for line in lines:
        valid = valid and line.__class__ == str

    return valid

def assert_read (path):

    valid = path.__class__ == str
    valid = valid and os.path.isfile(path)
    
    recreated = set.directories('user') + 'Julian_'
    nums      = general.find_numbers(path, 99, int)

    valid = valid and len(nums) >= 2

    if not valid:
        return valid

    recreated += str(nums[-2]) + '_' + str(nums[-1]) + ' Analysis.dat'
    valid = valid and recreated == path

    return valid

# Read split
def split (index, run):
    #   precondition
    assert(True)
    #   postcondition
    # Read in the data in the specified split data file.
    # [type] -> [floats]

    path =  set.directories('split') + 'Julian_' + str(index) + '_' 
    path += str(run) + '.dat'
    
    if not os.path.isfile (path):
        print('Split data does not exist.')
        return []

    file = open(path, 'r')
    data = np.loadtxt(file, skiprows=2)
    file.close()

    data = [[data[i][j] for i in range(len(data))] for j in range(len(data[0]))]
    data[3] = [data[3][i]*6.38 + 0.94357 for i in range(len(data[3]))]
    
    return data

# Read peaksfile
def read_field (lines):
    #   precondition
    assert( assert_lines(lines) )
    #   postcondition
    # Read in the field range.

    index = 1
    key = 'Field'
    while index < len(lines) and not lines[index][:len(key)] == key:
        index += 1

    if index == len(lines):
        raise ValueError('\n\nFailed to find field\n')

    field = general.find_numbers(lines[index], 3, float)

    if len(field) != 2:
        raise ValueError('\n\nThis field entry is corrupted:\n' + lines[index] + '\n')
    
    return field

def read_temp (lines):
    #   precondition
    assert( assert_lines(lines) )
    #   postcondition
    # Read in the temperature with deviation

    index = 0
    key = 'The temperature'
    while index < len(lines) and not lines[index][:len(key)] == key:
        index += 1

    if index == len(lines):
        raise ValueError('\n\nFailed to find temperature.\n')

    nums = general.find_numbers(lines[index], 3, float)

    if len(nums) != 2:
        raise ValueError('\n\nThis temperature entry is corrupted:\n' + lines[index] + '\n')

    return nums

def read_type (lines):
    #   precondition
    assert( assert_lines(lines) )
    #   postcondition
    # Read in the type.

    index = 0   
    key = 'This analysis is now marked as: '
    while index < len(lines) and not lines[index][:len(key)] == key:
        index += 1

    if index == len(lines) or len(lines[index]) < 35:
       raise ValueError('\n\nFailed to determine analysis type\n')

    return lines[index][32:]

def read_angle (lines):
    #   precondition
    assert( assert_lines(lines) )
    #   postcondition
    # Read in the optimal FFT angle.

    index = 0
    key = 'The optimal theta'
    while index < len(lines) and not lines[index][:len(key)] == key:
        index += 1

    if index == len(lines):
        raise ValueError('\n\nFailed to find theta optimal value\n')

    nums = general.find_numbers(lines[index], 2, float)

    if len(nums) != 1:
        raise ValueError('\n\nThis optimal theta entry is corrupted:\n' + lines[index] + '\n')
        
    return nums[0]

def read_settings(lines):
    #   precondition
    assert( assert_lines(lines) )
    #   postcondition
    # Read in the 2 settings.

    # Interpolation length
    index = 0
    key = 'Data interpolated'
    while index < len(lines) and not lines[index][:len(key)] == key:
        index += 1

    if index == len(lines):
        raise ValueError('\n\nFailed to find interpolation length setting\n')

    nums1 = general.find_numbers(lines[index], 2, int)

    if len(nums1) != 1:
        raise ValueError('\n\nThis interpolation length entry is corrupted:\n' + lines[index] + '\n')
        
    # FFT pad length
    index = 0
    key = 'FFT padded'
    while index < len(lines) and not lines[index][:len(key)] == key:
        index += 1

    if index == len(lines):
        raise ValueError('\n\nFailed to find FFT pad length setting\n')

    nums2 = general.find_numbers(lines[index], 2, int)

    if len(nums2) != 1:
        raise ValueError('\n\nThis FFT pad length entry is corrupted:\n' + lines[index] + '\n')

    return [nums1[0], nums2[0]]

def read_ab (lines, key):
    #   precondition
    assert( assert_lines(lines) )
    assert(key == 'a' or key == 'b')
    #   postcondition
    # Read in all peaks.
    # [serie] -> [freq/ampl] -> [harm num / floats]

    peaks = []

    for line in lines:
        # See if it is a peak.
        nums = general.find_numbers(line, 99, int)
        is_peak = len(nums) >= 4 and len(nums) <= 6
        if is_peak:
            test_start = str(nums[0]) + key + str(nums[1])
            is_peak = is_peak and line[:len(test_start)] == test_start

        # Read in the peak.
        if is_peak:
            harm_ind  = general.find_numbers(line, 1, int)[0]-1
            serie_ind = general.find_numbers(line, 2, int)[-1]-1
        
            while len(peaks) < serie_ind+1:
                peaks.append([[], []])

            freq = general.find_numbers(line, 99, float)[-2]
            ampl = general.find_numbers(line, 99, float)[-1]
            general.insert_element(peaks[serie_ind][0], freq, harm_ind)
            general.insert_element(peaks[serie_ind][1], ampl, harm_ind)

    if key == 'a' and len(peaks) > 3:
        raise ValueError('\n\nCorrupted peaksfile with ' + len(peaks) + ' alpha peaks.\n')

    return peaks

def read_freq_fact (lines):
    #   precondition
    assert( assert_lines(lines) )
    #   postcondition
    #

    
    index = 0
    key = 'The FFT freq factor'
    while index < len(lines) and not lines[index][:len(key)] == key:
        index += 1

    # The one setting which does not have to be there.
    # Reason: Earlier it was not included and now some files miss it.
    # In that time however there were also no frequency shifts, so it is then 1.
    if index == len(lines):
        return 1

    nums = general.find_numbers(lines[index], 2, float)

    if len(nums) != 1:
        raise ValueError('\n\nThis freq factor entry is corrupted:\n' + lines[index] + '\n')
        
    return nums[0]

def peaks (filepath):
    #   precondition
    assert( assert_read (filepath) )
    #   postcondition
    # alpha|beta:   [serie num] -> [freq/ampl] -> [harmonic num / list of floats]
    # info      :   [2field, 2temp, type, angle, 2settings]

    # get contents of the file
    peaks_file = open(filepath)
    lines = []
    for line in peaks_file:
        if len(line) > 1 and line.__class__ == str:
            lines.append(line[:-1])
    peaks_file.close()

    # Read all relevant data.
    file_nums= general.find_numbers(filepath, 99, int)[-2:]
    field    = read_field     (lines)
    temp     = read_temp      (lines)
    type     = read_type      (lines)
    angle    = read_angle     (lines)
    factor   = read_freq_fact (lines)
    settings = read_settings  (lines)

    alpha = read_ab (lines, 'a')
    beta  = read_ab (lines, 'b')

    # Finalise
    info  = [file_nums, field, temp, type, angle, factor, settings]
    return alpha, beta, info

# alpha|beta:   [serie num] -> [freq/ampl] -> [harmonic num / list of floats]
# info      :   [2index, 2field, 2temp, type, angle, freq_fact, 2settings]
