import numpy as np
import os

import F2_fft as input0
import F3_read as read

import F0_set as set
import F1_generalised as general

# Assertions
def assert_ab (peaks, type):

    valid = peaks.__class__ == list or peaks.__class__ == np.ndarray
    valid = valid and (type == 'alpha' or type == 'beta')

    if type == 'alpha':
        valid = valid and len(peaks) <= 3

    for run in peaks:
        valid = valid and len(run) == 2
        freq, ampl = run
        valid = valid and len(freq) == len(ampl)

        for f in freq:
            valid = valid and general.can_type(f, float)
        for a in ampl:
            valid = valid and general.can_type(a, float)
    
    return valid

def assert_peaks (dir, index, run_nr, field_range, alpha, beta, InPTTTF):

    # All but last argument
    valid = dir == 'out' or dir == 'user'
    valid = valid and index.__class__ == int
    valid = valid and run_nr.__class__ == int
    if not valid:
        return valid
    path = set.directories('split') + 'Julian_' + str(index) + '_' + str(run_nr) + '.dat'
    valid = valid and os.path.isfile(path)

    valid = valid and field_range.__class__ == list
    valid = valid and len(field_range) == 2
    valid = valid and general.can_type(field_range[0], float)
    valid = valid and general.can_type(field_range[1], float)
    valid = valid and float(field_range[0]) != float(field_range[1])
    valid = valid and float(field_range[0]) > 0
    valid = valid and float(field_range[1]) > 0

    valid = valid and assert_ab(alpha, 'alpha')
    valid = valid and assert_ab(beta, 'beta')

    # InPTTT: Interpolate points, Pad, Type, Temp, Theta
    valid = valid and InPTTTF.__class__ == list
    valid = valid and len(InPTTTF) == 6

    valid = valid and general.can_type(InPTTTF[0], int)
    valid = valid and general.can_type(InPTTTF[1], int)
    valid = valid and general.can_type(InPTTTF[4], float)
    valid = valid and general.can_type(InPTTTF[5], float)
    valid = valid and int(InPTTTF[0])   > 0
    valid = valid and int(InPTTTF[1])   > 0
    valid = valid and float(InPTTTF[4]) > 0
    valid = valid and float(InPTTTF[5]) > 0
    valid = valid and int(np.log2(int(InPTTTF[0]))) == np.log2(int(InPTTTF[0]))
    valid = valid and int(np.log2(int(InPTTTF[1]))) == np.log2(int(InPTTTF[1]))
    valid = valid and int(InPTTTF[0]) <= int(InPTTTF[1])

    valid = valid and InPTTTF[2].__class__ == str
    valid = valid and InPTTTF[3].__class__ == list
    valid = valid and len(InPTTTF[3]) == 2
    valid = valid and general.can_type(InPTTTF[3][0], float)
    valid = valid and general.can_type(InPTTTF[3][1], float)
        
    return valid

def assert_info (info):
    #info = [2file, 2field, 2temp, type, angle, fft_fact, 2settings]

    try:
        file, field, temp, type, angle, fft_fact, settings = info

        valid = len(file) == 2
        valid = valid and general.can_type(file[0], int) 
        valid = valid and general.can_type(file[1], int) 
        valid = valid and file[0] > 0 
        valid = valid and file[1] > 0 

        valid = valid and len(field) == 2
        valid = valid and general.can_type(field[0], float)    
        valid = valid and general.can_type(field[1], float) 
        valid = valid and field[0] != field[1]  
        valid = valid and field[0] > 0

        valid = valid and len(temp) == 2
        valid = valid and general.can_type(temp[0], float)    
        valid = valid and general.can_type(temp[1], float) 
        valid = valid and temp[0] > 0
        valid = valid and temp[1] >= 0

        valid = valid and type.__class__ == str
        valid = valid and len(type) > 1

        valid = valid and general.can_type(angle, float)
        valid = valid and angle > 0
        valid = valid and angle < 180

        valid = valid and general.can_type(fft_fact, float)
        valid = valid and fft_fact > 0
        valid = valid and fft_fact < 10

        valid = valid and len(settings) == 2
        valid = valid and settings[0].__class__ == int
        valid = valid and settings[1].__class__ == int

    except:
        return False

    return valid

# Writing
def peaks (dir, index, run_nr, field_range, alpha, beta, InPTTTF):
    #   precondition
    # InPTTTF: Interpolate points, Pad, Type, Temp, Theta, Freq factor
    assert( assert_peaks(dir, index, run_nr, field_range, alpha, beta, InPTTTF) )
    #   postcondition
    # Save the peaks results

    path =  set.directories(dir) + 'Julian_' + str(index) + '_' 
    path += str(run_nr) + ' Analysis.dat'
    file = open(path, 'w+')

    # Specifics
    to_write = 'Analysis data for Julian ' + str(index) + ' run ' + str(run_nr) + '\n'
    to_write += 'Field range: ' + general.string_round(field_range[0],2)
    to_write += ' to ' + general.string_round(field_range[1],2) + ' T\n'
    to_write += 'The FFT freq factor is ' + general.string_round(InPTTTF[5], 4) + '.\n'
    to_write += 'This analysis is now marked as: ' + InPTTTF[2] + '\n'
    to_write += 'The temperature is ' + general.string_round(InPTTTF[3][0], 3) 
    InPTTTF[3][1] = np.ceil(InPTTTF[3][1]*1000)/1000
    to_write += ' +- ' + general.string_round(InPTTTF[3][1], 3) + ' mK\n\n'

    to_write += 'Data interpolated to ' + str(InPTTTF[0]) + ' points\n'
    to_write += 'FFT padded to ' + str(InPTTTF[1]) + ' points\n'
    to_write += 'The optimal theta is ' + general.string_round(InPTTTF[4], 3) + ' degrees\n\n'

    to_write += 'The determined alpha and beta peaks:\n'

    # Alpha
    pos1 = 10
    pos2 = 23
    for run_ind, run in enumerate(alpha):   
        freq, ampl = run
        for harm_ind in range(len(freq)):
            new_line  = str(harm_ind+1) + 'a' + str(run_ind+1) + ':'
            new_line  = general.fill_to (new_line, pos1, ' ')
            
            new_line += general.string_round(freq[harm_ind], 5)
            new_line  = general.fill_to (new_line, pos2, ' ')

            new_line += general.string_round(ampl[harm_ind], 5)
            to_write += new_line + '\n'
        to_write += '\n'

    # Beta
    for run_ind, run in enumerate(beta):   
        freq, ampl = run
        for harm_ind in range(len(freq)):
            new_line  = str(harm_ind+1) + 'b' + str(run_ind+1) + ':'
            new_line  = general.fill_to (new_line, pos1, ' ')

            new_line += general.string_round(freq[harm_ind], 5)
            new_line  = general.fill_to (new_line, pos2, ' ')

            new_line += general.string_round(ampl[harm_ind], 5)
            to_write += new_line + '\n'
        to_write += '\n'

    file.write(to_write)
    return

def peaks_simple (dir, alpha, beta, info):
    #   precondition
    #info = [2file, 2field, 2temp, type, angle, 2settings]
    assert( dir == 'user' or dir == 'out')
    assert( assert_info(info) )
    assert( assert_ab (alpha, 'alpha') )
    assert( assert_ab (beta, 'beta') )
    #   postcondition
    # Save the peaksfile.

    InPTTTF = [info[6][0], info[6][1], info[3], info[2], info[4], info[5]]
    peaks(dir, info[0][0], info[0][1], info[1], alpha, beta, InPTTTF)

    return