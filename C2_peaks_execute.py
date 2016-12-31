import time
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import B3_ab as ab

import F0_set as set
import F1_generalised as general
import F2_fft as fft
import F3_read as read
import F4_save as save

# assertions & checks
def assert_peaks (peaks, type):
    # serie ind | freq/ampl | harm index
    
    try:
        test = type == 'a' and len(peaks) <= 3 
        valid = test or type == 'b'

        for serie in peaks:
            freq, ampl = serie
            valid = valid and len(freq) == len(ampl)
            valid = valid and len(freq) > 0
        
            for f in freq:
                valid = valid and general.can_type(f, float)
            for a in ampl:
                valid = valid and general.can_type(a, float)
    except:
        return False

    return valid

def assert_peak (entry):
    valid = entry.__class__ == str

    valid1 = valid  and len(entry) == 2
    valid1 = valid1 and (entry[0] == 'a' or entry[0] == 'b')
    valid1 = valid1 and general.can_type(entry[1], int)
    valid1 = valid1 and int(entry[1]) > 0

    valid2 = valid  and len(entry) == 3
    valid2 = valid2 and general.can_type(entry[0], int)
    valid2 = valid2 and int(entry[0]) > 0
    valid2 = valid2 and (entry[1] == 'a' or entry[1] == 'b')
    valid2 = valid2 and general.can_type(entry[2], int)
    valid2 = valid2 and int(entry[2]) > 0

    valid3 = valid  and len(entry) == 3
    valid3 = valid3 and entry[0] == 'X'
    valid3 = valid3 and (entry[1] == 'a' or entry[1] == 'b')
    valid3 = valid3 and general.can_type(entry[2], int)
    valid3 = valid3 and int(entry[2]) > 0
    
    return valid1 or valid2 or valid3

def assert_info (info):
    #info = [2file, 2field, 2temp, type, angle, freq factor, 2settings]

    try:
        file, field, temp, type, angle, factor, settings = info

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

        valid = valid and general.can_type(factor, float)
        valid = valid and factor > 0

        valid = valid and len(settings) == 2
        valid = valid and settings[0].__class__ == int
        valid = valid and settings[1].__class__ == int

    except:
        return False

    return valid

def assert_fft (fft_opt):

    fft_opt = np.array(fft_opt)

    try:
        freq, ampl = fft_opt
        valid = len(freq) == len(ampl)

        for i in freq:
            valid = valid and general.can_type(i, float)
        for i in ampl:
            valid = valid and general.can_type(i, float)
    except AssertionError:
        return False

    return valid

def assert_plot_command (command):
    
    try:
        valid = command[0] == 'plot' or command[0] == 'show'
        valid1 = valid and len(command) == 1
        
        valid2 = valid  and len(command) == 2
        valid2 = valid2 and float(command[1])
        
        valid3 = valid  and len(command) == 3
        valid3 = valid3 and float(command[1])
        valid3 = valid3 and float(command[2])
    except:
        return False

    return valid1 or valid2 or valid3

def assert_add_command (command):

    valid = command.__class__ == list
    valid = valid and len(command) in [2,3]
    valid = valid and command[0] == 'add'
    
    if len(command) > 2:
        valid = valid and general.can_type(command[2], float)

    return valid

def assert_type (command, alpha, beta, temp, type, file, run):

    valid = command.__class__ == list
    valid = valid and len(command) == 2
    valid = valid and command[0] == 'type'
    valid = valid and assert_peaks(alpha, 'alpha')
    valid = valid and assert_peaks(beta, 'beta')
    valid = valid and temp.__class__ == list
    valid = valid and len(temp) == 2
    valid = valid and general.can_type(temp[0], float)
    valid = valid and general.can_type(temp[1], float)
    valid = valid and type.__class__ == str
    valid = valid and file.__class__ == int
    valid = valid and run.__class__ == int
    valid = valid and run > 0

    return valid

def is_tail_peak (entry, alpha, beta):
    #   precondition
    assert( assert_peak(entry) )
    assert( assert_peaks (alpha, 'a'))
    assert( assert_peaks (beta, 'b'))
    #   postcondition
    # Return if the entry corresponds to an existing peak
    # and this peak is the last harmonic in a series

    if len(entry) == 2:
        entry = 'X' + entry

    if entry[1] == 'a':
        peaks = alpha
    else:
        peaks = beta

    valid = assert_peak (entry)
    valid = valid and len(peaks) >= int(entry[2])
    valid = valid and len(peaks[int(entry[2])-1]) > 0
    valid = valid and (entry[0] == 'X' or len(peaks[int(entry[2])-1][0]) == int(entry[0]))

    return valid

# print
def print_peaks (peaks, type):
    #   precondition
    assert(assert_peaks(peaks, type))
    #   postcondition
    # Print the peak harmonics.

    for ind, serie in enumerate(peaks):
        freq, ampl = serie
        for harm, f in enumerate(freq):
            to_print = str(harm+1) + type[0] + str(ind+1) + ':'
            to_print = general.fill_to (to_print, 12, ' ')            
            to_print += general.string_round(f, 0)
            to_print = general.fill_to (to_print, 20, ' ')
            to_print += general.string_round(ampl[harm], 1)
            print(to_print)

        if type == 'a':
            to_print = str(harm+2) + 'a' + str(ind+1) + ':'
            to_print = general.fill_to (to_print, 12, ' ')            
            to_print += general.string_round(freq[0] + freq[-1], 0)
            print(to_print)
            print()

    return

def list_peaks (alpha, beta, info):
    #   precondition
    #info = [2field, 2temp, type, angle, 2settings]
    assert(assert_peaks (alpha, 'a'))
    assert(assert_peaks (beta,  'b'))
    assert(assert_info  (info))
    #   postcondition
    # Print the peaks and info on screen.

    #info = [2file, 2field, 2temp, type, angle, 2settings]
    to_print  = 'Currently working on file ' 
    to_print += str(info[0][0])                     + ' run '
    to_print += str(info[0][1])                     + ',\nwith fieldrange '
    to_print += general.string_round(info[1][0], 2) + ' to '
    to_print += general.string_round(info[1][1], 2) + '.\nThe run was performed at '
    to_print += general.string_round(info[2][0], 3) + ' +- '
    to_print += general.string_round(info[2][1], 3) + ' mK.\nThe analysis type is now '
    to_print += info[3]                             + '.\nAnd the optimal angle is '
    to_print += general.string_round(info[4], 2)    + '.\nThe freq compensation factor is '
    to_print += general.string_round(info[5], 3)    + '.\nFinally the data was interpolated to '
    to_print += str(info[6][0])                     + ' points and padded to '
    to_print += str(info[6][1])                     + '.\n'

    os.system('cls')
    print(to_print)

    if len(alpha) > 0 or len(beta) > 0:
        print('The peaks are:\n')
        print_peaks (alpha, 'a')
        print_peaks (beta, 'b')
    else:
        print('There are no peaks selected for this run.')    

    return

# plot
def applicable_plot (command):
    #   precondition
    assert( assert_plot_command(command) )
    #   postcondition
    # return the freq, ampl of the relevant fft part.
    # return if all went well or not.

    if len(command) == 3:
        # reference!
        command[1] = float(command[1])
        command[2] = float(command[2])

        if command[2] > set.settings('max_freq'):
            print('Overwriting your freq high limit to', set.settings('max_freq'))
            # reference!
            command[2] = set.settings('max_freq')

        valid = command[2] > command[1] + 250
        return valid and command[1] >= 0

    if len(command) == 2:
        # reference!
        command[1] = float(command[1])
        command.append(command[1]+1000)
        command[1] -= 1000
    
        if command[2] > set.settings('max_freq'):
            print('Overwriting your freq high to', set.settings('max_freq'))
            # reference!
            command[1] = set.settings('max_freq')


        return command[1] >= 0
        
    if len(command) == 1:
        command.append(0)
        command.append(set.settings('max_freq'))
        return True
    
    return False

def plot_peaks (command, alpha, beta, info, fft):
    #   precondition
    assert( assert_fft(fft) )
    fft = np.array(fft)
    assert( assert_plot_command(command) )
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta,  'b') )
    assert( assert_info (info) )
    #   postcondition
    # Plot the options

    if not applicable_plot (command):
        print('Unapplicable plot command.')
        return
    
    plt.plot(fft[0], fft[1], 'b-')

    alpha_col = 'y'
    beta_col  = 'r'
    patch = [ mpatches.Patch(color='y', label='Alpha') ]
    patch.append( mpatches.Patch(color='r', label='Beta') )

    for ind, serie in enumerate(alpha):
        freq, ampl = serie
        plt.plot(freq, ampl, alpha_col + '.', ms = 12)

    for ind, serie in enumerate(beta):
        freq, ampl = serie
        plt.plot(freq, ampl, beta_col + '.', ms = 12)

    if len(command) == 3:
        plt.xlim(float(command[1]), float(command[2]))
        freq, ampl = fft
        abs_max = np.max(ampl)
        temp  = ampl[freq>float(command[1])]     
        temp2 = freq[freq>float(command[1])]  
        temp  = temp[temp2<float(command[2])]
        if len(temp) > 0:
            max_ampl = np.max(temp)
            if max_ampl < 0.9*abs_max:
                plt.ylim(0, max_ampl*2+5)
            else:
                plt.ylim(0, max_ampl*1.1+5)

    plt.legend(handles = patch)
    plt.title('FFT and peaks from Julian ' + str(info[0][0]) + ' run ' + str(info[0][1]))
    plt.xlabel('freq (T)')
    plt.ylabel('FFT amplitude of magnetization')
    plt.show()
    return

def nb (command, info):
    #   precondition
    assert( command[0] == 'nb')
    assert( len(command) == 1 or general.can_type(command[1], float))
    assert ( assert_info (info) )
    #   postcondition
    # Plot the no background magnetisation

    timestamps, x, y, temp, field = np.array(read.split (info[0][0], info[0][1]))

    if len(x) < 5:
        print('No data in the split data file.')
        return

    if len(command) == 2:
        theta = float(command[1])/180.*np.pi
    else:
        theta = info[4]/180.*np.pi
    
    magn  = x*np.cos(theta)+y*np.sin(theta)
    magn3 = fft.no_background (field, magn, 3) 
    para  = fft.no_background (field, magn, 3, para=True) 
 
    def func (x, a, b, c, d):
        return a*x**3 + b*x**2 + c*x + d
    x = np.linspace(np.min(field), np.max(field), 10000)
    y = func(x, *para)  
    title = 'Magnetisation ' + general.string_round(theta/np.pi*180, 2) + ' deg | '

    plt.figure(1)
    plt.plot(field, magn, 'b-')
    plt.plot(x, y, 'r-')
    plt.title(title + 'original')
    plt.xlim([np.min(field), np.max(field)])
    plt.xlabel('Field (T)')
    plt.ylabel('Magnetisation')
    
    plt.figure(2)
    plt.plot(field, magn3, 'g-')
    plt.title(title + '3rd order background removed.')
    plt.xlim([np.min(field), np.max(field)])
    plt.xlabel('Field (T)')
    plt.ylabel('Magnetisation')

    plt.show()
    return

# delete
def delete (command, alpha, beta, info):
    #   precondition
    assert( len(command) == 2 )
    assert( command[0] == 'delete' or command[0] == 'remove' )
    
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta,  'b') )
    assert( assert_info (info) )
    #   postcondition
    # Delete the selected peak.

    # check for validity
    if len(command[1]) == 2:
        command[1] = 'X' + command[1]
    if not assert_peak (command[1]):
        print('Invalid peak. Stopping delete...')
        return
    if not is_tail_peak (command[1], alpha, beta):
        print('Peak could not be located or is not the last harmonic.')
        print('Stopping delete...')
        return
    
    

    
    # creates reference!
    if command[1][1] == 'a':
        peaks = alpha
    else:
        peaks = beta

    # remove peaks data
    serie_ind = int(command[1][2])-1

    if not command[1][0] == 'X':
        del peaks[serie_ind][0][-1]
        del peaks[serie_ind][1][-1]

    if peaks[serie_ind] == [[], []] or command[1][0] == 'X':
        del peaks[serie_ind]

    # overwrite file
    save.peaks_simple ('user', alpha, beta, info)
    print('Succesfully deleted the peak.')
    return

def delete_b (command, alpha, beta, info):
    #   precondition
    assert( command == ['delete', 'b'] or command == ['remove', 'b'] )
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta,  'b') )
    assert( assert_info (info) )
    #   postcondition
    # Delete all beta peaks.
    
    print('Enter y to confirm you want to delete all beta peaks.')
    string = ''
    while string == '':
        string = input()
    if string != 'y':
        return

    save.peaks_simple('user', alpha, [], info)
    print('Succesfully deleted all beta peaks.')
    return

# move
def applicable_move (command, alpha, beta, info):
    #   precondition
    assert( len(command) == 3 ) 
    assert( command[0] == 'move' )
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta,  'b') )
    assert( assert_info (info) )
    #   postcondition
    # Return if the move is applicable or not
    
    valid = assert_peak(command[1])
    valid = valid and assert_peak(command[2])

    if valid and len(command[2]) == 2:
        command[2] = 'X' + command[2]

    valid  = valid  and len(command[1]) == 3 and not command[1][0] == 'X'
    valid  = valid  and is_tail_peak (command[1], alpha, beta)
    valid  = valid  and command[2][0] == 'X'
    
    # to beta
    valid1 = valid  and command[2][1] == 'b'
    valid1 = valid1 and len(beta) >= int(command[2][2])-1

    # to alpha
    valid2 = valid  and command[2][1] == 'a'
    valid2 = valid2 and len(alpha) >= int(command[2][2])-1

    return valid1 or valid2

def move (command, alpha, beta, info):
    #   precondition
    assert( len(command) == 3 ) 
    assert( command[0] == 'move' )
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta,  'b') )
    assert( assert_info (info) )
    #   postcondition
    # move a peak from one location to another.

    # due to references: adds 'X' in front of 'a2'
    if not applicable_move (command, alpha, beta, info): 
        print('Your move command cannot be executed.')
        print('Enter your entries as 5a2 b2')
        print('Stopping move...')
        return

    # creates references.
    if command[1][1] == 'a':
        origin = alpha
    else:
        origin = beta

    if command[2][1] == 'a':
        destiny = alpha
    else:
        destiny = beta

    # locations
    serie_from = int(command[1][2])-1
    serie_to   = int(command[2][2])-1

    if len(destiny) == serie_to:
        destiny.append([ [], [] ])

    # move
    temporary = origin[serie_from][0][-1]
    del origin[serie_from][0][-1]
    destiny[serie_to][0].append(temporary)

    temporary = origin[serie_from][1][-1]
    del origin[serie_from][1][-1]
    destiny[serie_to][1].append(temporary)

    # delete empty beta
    if origin[serie_from] == [[], []]:
        del origin[serie_from]

    # overwrite file
    save.peaks_simple ('user', alpha, beta, info)
    print('Succesfully moved the peak.')
    return

# add
def applicable_add (command, alpha, beta):
    #   precondition
    assert(assert_add_command (command) )
    assert(assert_peaks (alpha, 'a'))
    assert(assert_peaks (beta,  'b'))
    #   postcondtiion
    # Return if the add command is applicable or not.

    # basic requirements
    valid = assert_peak (command[1]) or command[1] in ['a', 'b']
    
    # Case 1: make an extra alpha at a freq   
    valid1 = valid  and command[1] == 'a'
    valid1 = valid1 and len(alpha) < 3
    valid1 = valid1 and len(command) == 3

    # Case 2: make an extra beta at a freq
    valid2 = valid  and command[1] == 'b'
    valid2 = valid2 and len(command) == 3

    # Case 3: make a new alphaY
    valid3 = valid  and command[1][0] == 'a' 
    valid3 = valid3 and len(command[1]) == 2
    valid3 = valid3 and len(alpha)+1 >= int(command[1][1])
    valid3 = valid3 and int(command[1][1]) <= 3

    # Case 4: make a new betaY
    valid4 = valid  and command[1][0] == 'b'
    valid4 = valid4 and len(command[1]) == 2
    valid4 = valid4 and len(beta)+1 >= int(command[1][1])

    valid = valid1 or valid2 or valid3 or valid4
    
    # different command specifics
    valid1 = valid and len(command) == 2

    valid2 = valid  and len(command) == 3
    valid2 = valid2 and int(command[2]) > 2500
    valid2 = valid2 and int(command[2]) < set.settings('max_freq')
    
    return valid1 or valid2

def translate_add (command, alpha, beta):
    #   precondition
    assert( applicable_add(command, alpha, beta) )
    #   postcondition
    # Translate the command, using a reference!
    # -> Add the peak to append if it remained vague (a, b)
    # -> Calculate the expectation frequency if it remained vague

    if command[1] == 'b':
        command[1] = command[1] + str(len(beta)+1)
    elif command[1] == 'a':
        command[1] = command[1] + str(len(alpha)+1)
    elif len(command) == 2 and command[1][-2] == 'a':
        command.append( alpha[ int(command[1][-1])-1 ][0][0] )
        command[-1] +=  alpha[ int(command[1][-1])-1 ][0][-1] 
    elif len(command) == 2 and command[1][-2] == 'b':
        command.append( beta[ int(command[1][-1])-1 ][0][0] )
        command[-1] +=  beta[ int(command[1][-1])-1 ][0][-1]
    elif len(command) == 2:
        raise AssertionError('Update translate add to match applicable add.')

    return

def get_options (freq, ampl):
    #   precondition
    assert(len(freq) == len(ampl))
    #   postcondition       
    # Calculate the options (ampl max). Print & Return.

    # determine options
    max_ind, min_ind  = general.extreme_indices (ampl, 1, 0)
    max_freq = freq[max_ind]
    max_ampl = ampl[max_ind]

    # print options
    print('Option 0: Add nothing')
    for ind, f in enumerate(max_freq):
        to_print = 'Option ' + str(ind+1) + ':'
        to_print = general.fill_to (to_print, 12, ' ')
        to_print += general.string_round(f, 0)
        to_print = general.fill_to (to_print, 20, ' ')
        to_print += general.string_round(max_ampl[ind], 1)
        print(to_print)

    return [max_freq, max_ampl]

def plot_options (freq, ampl, alpha, beta, max_freq, max_ampl):
    #   precondition    
    # Pointless
    assert( True )
    #   postcondtiion
    # plot the options over the FFT.

    # FFT and alpha, beta peaks.
    plt.figure(1)
    plt.plot(freq, ampl, 'b-')
    
    # group options
    equi_color_options = [[[], []], [[], []], [[], []], [[], []]]
    labels = ['Options:', 'Options:', 'Options:', 'Options:']
    for i in range(len(max_freq)):
        equi_color_options[i%4][0].append(max_freq[i])
        equi_color_options[i%4][1].append(max_ampl[i])
        labels[i%4] += ' ' + str(i+1)

    # plot options
    cols = ['g', 'c', 'k', 'm']
    patch = [    mpatches.Patch(color='y', label='Alpha')]
    patch.append(mpatches.Patch(color='r', label='Beta'))
    for ind, option in enumerate(equi_color_options):
        plt.figure(1)
        plt.plot(option[0], option[1], cols[ind] + 'o', ms = 13)
        patch.append(mpatches.Patch(color=cols[ind], label=labels[ind]))

    # plot alpha
    for ind, serie in enumerate(alpha):
        f, a = serie
        plt.plot(f, a, 'yo', ms = 8)

    # plot beta
    for ind, serie in enumerate(beta):
        f, a = serie
        plt.plot(f, a, 'ro', ms = 8)

    plt.xlim(min(freq), max(freq))
    plt.ylim(0, max(ampl))
    plt.legend( handles=patch )
    plt.show()
    return

def add_peak (peaks, serie_ind, freq, ampl):
    #   precondition
    # pointless
    assert( True )
    #   postcondition
    # Add the freq and ampl pair to the given serie in peaks.

    if serie_ind == len(peaks):
        peaks.append( [[], []] )

    peaks[serie_ind][0].append(freq)
    peaks[serie_ind][1].append(ampl)

    return

def add (command, alpha, beta, info, fft):
    #   precondition
    assert(assert_fft (fft))
    fft = np.array(fft)
    assert(assert_add_command (command) )
    assert(assert_peaks (alpha, 'a'))
    assert(assert_peaks (beta,  'b'))
    assert(assert_info  (info))
    #   postcondition
    # Add a peak around a given frequency to a peak series as a new harmonic.

    # Process command with reference
    if not applicable_add (command, alpha, beta):
        print('Invalid or unapplicable add command.')
        return
    
    translate_add (command, alpha, beta)
    plot_range = 1000

    # Determine, print, plot options
    freq, ampl = fft
    ampl = ampl[freq > int(command[2]) - plot_range]
    freq = freq[freq > int(command[2]) - plot_range]
    ampl = ampl[freq < int(command[2]) + plot_range]
    freq = freq[freq < int(command[2]) + plot_range]

    max_freq, max_ampl = get_options(freq, ampl)
    plot_options (freq, ampl, alpha, beta, max_freq, max_ampl)

    # user option
    is_valid = False
    while not is_valid:
        string = input()
        is_valid = general.can_type(string, int) 
        is_valid = is_valid and int(string) >= 0 
        is_valid = is_valid and int(string) <= len(max_freq)

    # add option with reference.
    if int(string) == 0:
        print('Peaks remain unchanged.')
        return
    
    serie = int(command[1][-1])
    if command[1][-2] == 'a':
        add_peak (alpha, serie-1, max_freq[int(string)-1], max_ampl[int(string)-1])
    else:
        add_peak (beta,  serie-1, max_freq[int(string)-1], max_ampl[int(string)-1])

    # save
    save.peaks_simple('user', alpha, beta, info)
    os.system('cls')
    print('Succesfully added the peak.')
    list_peaks (alpha, beta, info)
    return

# type & shift & temp
def list_types ():
    #   precondition
    assert(True)
    #   postcondition
    # List the base types.
        
    base_types = set.standard_types()

    to_print = '\nThe following ' + str(len(base_types)) + ' types are basic:\n'

    for base in base_types:
        to_print += '> ' + base + '\n'

    print(to_print[:-1])
    return

def type (command, alpha, beta, info):
    #   precondition
    assert( command[0] == 'type' )
    assert( len(command) >= 2 )
    assert( assert_peaks (alpha, 'a'))
    assert( assert_peaks (beta,  'b'))
    assert( assert_info  (info))
    #   postcondition
    # Change the type

    # initiate
    type = info[3]
    standards = set.standard_types()

    string = ''
    for i, word in enumerate(command[1:]):
        if i != 0:
            string += ' '
        string += str(word)

    is_valid = string in standards

    # start protocol if type is not standard.  
    if string in standards:
        info[3] = string
        string2 = 'y'
    else:
        print('This type is not standard. Enter \'y\' to confirm it.')
        string2 = input()
        if string2 == 'y':
            info[3] = string
    
    if string2 == 'y':
        save.peaks_simple('user', alpha, beta, info)
        print('Succesfully changed the type from', type, 'to', info[3])
    else:
        print('Analysis remains unchanged.')
    return

def shift(command, alpha, beta, info):
    #   precondition
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta, 'b') )
    assert( assert_info(info) )
    #   postcondition
    # Change the frequency factor to a new one.
    
    
    valid = len(command) == 2
    valid = valid and command[0] == 'shift'
    valid = valid and general.can_type(command[1], float)
    valid = valid and float(command[1]) > 0.5
    valid = valid and float(command[1]) < 1.5
    
    if not valid:
        print('Cannot apply your frequency shift. Aborting...')

    command[1] = float(command[1])
    relative_shift = command[1] / info[5]

    for ind in range(len(alpha)):        
        for ind2 in range(len(alpha[ind][0])):
            alpha[ind][0][ind2] *= relative_shift

    for ind in range(len(beta)):        
        for ind2 in range(len(beta[ind][0])):
            beta[ind][0][ind2] *= relative_shift

    info[5] = command[1]
    save.peaks_simple('user', alpha, beta, info)
    return

def temp(command, alpha, beta, info):
    #   Precondition
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta, 'b') )
    assert( assert_info(info) )
    #   Postcondition
    # Change the temperature to the given one (positive)
    # Or restore the default temperature (negative)

    if len(command) != 2 or command[0] != 'temp' \
        or not general.can_type(command[1], float):
        print('Could not process your command to change the temperature.')
        return 

    if float(command[1]) > 0:
        info[2] = [float(command[1]), 0]
    else:
        info[2] = fft.fft(info[0][0], info[0][1], info[4], info[6], info[5])[3]

    save.peaks_simple ('user', alpha, beta, info)
    to_print =  'Succesfully changed the temperature to '
    to_print += general.string_round(info[2][0], 4) + ' +- '
    to_print += general.string_round(info[2][1], 4) + ' mK'
    print(to_print)
    return

# reset & theta & xy
def reset(command, alpha, beta, info, fft):
    #   precondition
    assert( command == ['standard'] or command == ['reset'])
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta, 'b') )
    assert( assert_info(info) )
    assert( assert_fft(fft) )
    #   postcondition
    # Derive the standard alpha and beta peaks and overwrite the current set.

    alpha, beta = ab.derive(fft)
    info[3] = 'auto'
    save.peaks_simple('user', alpha, beta, info)
    print('Succesfully reset the basic peaks.')
    return

def theta(command, alpha, beta, info, dev = 0.01):
    #   precondition
    #info = [2file, 2field, 2temp, type, angle, freq factor, 2settings]
    assert( (len(command) == 2 and general.can_type(command[1], float)) \
            or len(command) == 1)
    assert( command[0] == 'theta' or command[0] == 'angle' )
    assert( assert_info(info) )
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta, 'b') )
    assert( dev > 0 )
    #   postcondition
    # Re-optimize theta and plot a range of theta 1a peaks.
    
    print('Step 1/5: Importing data from split runs file')
    data = read.split (info[0][0], info[0][1])
    data = [ data[1], data[2], data[4] ]
    
    print('Step 2/5: Interpolating the data')
    data[0], data[1:] = fft.interpolate_data (data[2], data[:2], info[6][0])
    # data is now field-x-y, interpolated.

    print('Step 3/5: Optimizing theta\n')
    show = len(command) == 2
    theta_opt = fft.theta_optimize(data, info[6][0]*2, False, info[5])
    fft_opt = fft.fft(info[0][0], info[0][1], theta_opt, info[6], info[5])[0]
    
    if show:
        print('Step 4/5: Plotting highest alpha in a range')
        if len(command) == 1:
            borders = [theta_opt-45,theta_opt+45]
        else:
            borders = [theta_opt-float(command[1]), theta_opt+float(command[1])]

        fft.theta_sweep (borders[0], borders[1], 30, data, info[6][0]*2, True, info[5])
    else:
        print('Step 4/5: Skipping plot for theta range.')

    if abs(info[4] - theta_opt) < dev:
        to_print =  '> The change is too small. '
        to_print += 'From ' + general.string_round(info[4], 3)
        to_print += ' to ' + general.string_round(theta_opt, 3)
        print(to_print)
        return True

    to_print =  '> The change is significant. From '
    to_print += general.string_round(info[4], 3) + ' to '
    to_print += general.string_round(theta_opt, 3)
    to_print += '.\nStep 5/5: reset all peaks and save the results'
    print(to_print)

    info[4] = theta_opt
    reset( ['reset'], alpha, beta, info, fft_opt )

    return 'remake'

def xy (alpha, beta, info):
    #   precondition
    assert( assert_peaks (alpha, 'a') )
    assert( assert_peaks (beta, 'b') )
    assert( assert_info(info) )
    #   postcondition
    # Create FFTs at 0 and 90 degrees.


    freq0, ampl0 = fft.fft (info[0][0], info[0][1], 0, info[6], info[5])[0]
    plt.figure(1)
    plt.plot(freq0, ampl0, 'b-')
    plt.xlabel('Freq (T)')
    plt.ylabel('FFT of magnetisation')
    plt.title('FFT at 0 degrees | FFT of x component')
    plt.ylim(bottom = 0)
    ylim1 = plt.ylim()

    freq90, ampl90 = fft.fft (info[0][0], info[0][1], 90, info[6], info[5])[0]
    plt.figure(2)
    plt.plot(freq90, ampl90, 'b-')
    plt.xlabel('Freq (T)')
    plt.ylabel('FFT of magnetisation')
    plt.title('FFT at 90 degrees | FFT of y component')
    plt.ylim(bottom = 0)
    ylim2 = plt.ylim()

    for serie in alpha:
        for i in range(len(serie[0])):
            x = [serie[0][i], serie[0][i]]
            plt.figure(1)
            plt.plot(x, ylim1, 'y-')
            plt.figure(2)
            plt.plot(x, ylim2, 'y-')

    for serie in beta:
        for i in range(len(serie[0])):
            x = [serie[0][i], serie[0][i]]
            plt.figure(1)
            plt.plot(x, ylim1, 'r-')
            plt.figure(2)
            plt.plot(x, ylim2, 'r-')

    plt.show()
    return

# order
def order_peaks (peaks, ascending):
    #   precondition
    assert( assert_peaks (peaks,  'b'))
    assert( ascending.__class__ == bool)
    #   postcondition
    # order the peaks given.

    # peaks themselves.
    for serie_ind, serie in enumerate(peaks):
        freq, ampl = serie
        order = general.bubble_sort(freq, True)

        new_serie = [freq, []]
        for ind in order:
            new_serie[1].append(ampl[ind])

        peaks[serie_ind] = new_serie

    #between peaks ordered.
    start_freq = []
    for serie_ind in range(len(peaks)):
        start_freq.append( peaks[serie_ind][0][0] )
    order = general.bubble_sort (start_freq, ascending)

    new_peaks = []
    for ind in order:
        new_peaks.append( peaks[ind] )

    return new_peaks

def order (alpha, beta, info):
    #   precondition
    assert( assert_peaks (alpha, 'a'))
    assert( assert_peaks (beta,  'b'))
    assert( assert_info  (info))
    #   postcondition
    # order each alpha series, each beta series and the seperate beta series.
        
    alpha = order_peaks (alpha, False)
    beta  = order_peaks (beta, True)

    save.peaks_simple('user', alpha, beta, info)
    print('Succesfully ordered peaks.')
    return

