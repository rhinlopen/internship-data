import os
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import C2_peaks_execute as execute

import F0_set as set
import F1_generalised as general
import F2_fft as input0
import F3_read as read
import F4_save as save

# Definitions

def allowed_dirs_types ():
    return [set.directories('user'), set.directories('out')]

# OLD FFT show
def assert_show_fft(command):

    valid = command.__class__ == list
    valid = valid and len(command) in [3, 5]
    valid = valid and general.can_type(command[2], int)

    return valid

def applicable_fft (command):
    #   precondition
    assert( assert_show_fft(command) )
    #   postcondition
    # Check if the fft exists and can be plotted.
    
    valid = set.directories(command[1]) == set.directories('user') \
        or set.directories(command[1]) == set.directories('out')

    valid = valid and int(command[2]) >= 0

    valid1 = valid and len(command) == 3

    valid2 = valid and len(command) == 5
    valid2 = valid2 and general.can_type(command[3], float)
    valid2 = valid2 and general.can_type(command[4], float)
    valid2 = valid2 and float(command[3]) < float(command[4])
    valid2 = valid2 and float(command[3]) >= 0
    valid2 = valid2 and float(command[4]) > 5000
        
    return valid1 or valid2 

def show_fft (command):
    #   precondition
    assert(assert_show_fft(command))
    #   postcondition
    # show the fft's stored in the specified index (range).

    index = int(command[2])
    if not applicable_fft (command):
        print('Unapplicable command. Aborting ...')
        return

    # determine freq range:
    freq_range = [0, set.settings('max_freq')]
    if len(command) == 5:
        freq_range[0] = float(command[3])
        freq_range[1] = float(command[4])

    # determine infiles.
    files = os.listdir(set.directories('in'))
    infile = ''
    for file in files:
        if general.find_numbers (file, 1, int)[0] == index:
            infile = set.directories('in') + file

    # determine peakfiles
    files = os.listdir(set.directories(command[1]))
    peakfile = ''
    for file in files:
        if general.find_numbers(file, 1, int)[0] == index:
            peakfile = set.directories(command[1]) + file

    if peakfile == '' or infile == '':
        print('Could not find the peak or input file to create the FFTs. Aborting ...')
        return

    # import files
    a, b, f, t, ty, th = read.read_peaks (peakfile)
    
    for run_ind in len(a):
        alpha = a [run_ind]
        beta  = b [run_ind]
        field = f [run_ind]
        temp  = t [run_ind]
        type  = ty[run_ind]
        theta = th[run_ind]
        fft_opt, theta_opt = input0.fft (index, run_ind, theta)

        if len(fft_opt[0]) > 0:
            plt.figure(run_ind+1)
            plt.plot(fft_opt[0], fft_opt[1], 'b-')
            plt.title('FFT for run ' + str(run_ind+1) + \
                ' with theta ' + general.string_round(theta, 1))
            plt.xlabel('freq (T)')
            plt.ylabel('FFT ampl of magnitisation')

    plt.show()
    return

# Types
def assert_types (command):

    valid = command.__class__ == list
    valid = valid and len(command) in [1,2]
    valid = valid and command[0] in ['types', 'type']

    return valid

def type_amount ():
    #   precondition
    assert(True)
    #   postcondition
    # For each base type & rest: find out the amount.

    base_types = set.standard_types()
    base_types.append('rest')
    nrs = np.zeros(len(base_types))
    
    # Determine numbers
    files = os.listdir(set.directories('user'))
    for file in files:
        nums = general.find_numbers(file, 3, int)
        path = set.directories('user') + file        

        info = read.peaks(path)[2]
        type_pos = general.find_value (base_types, info[3])
        # Not found -> -1 -> rest no conversion necessary
        nrs[type_pos] += 1

    # Print results
    print('Types with their frequency, relative occurence and cumulative:')
    empty_types = []
    for i in range(len(base_types)):
        if nrs[i] != 0:
            to_print  = '> ' + base_types[i]
            to_print  = general.fill_to(to_print, 15, ' ')
            to_print += general.string_round(nrs[i],0)

            to_print  = general.fill_to(to_print, 20, ' ')
            to_print += general.string_round(nrs[i]/np.sum(nrs)*100, 0)
            to_print += ' %'

            print(to_print)
        else:
            empty_types.append (base_types[i])

    print()
    print('Unused types:')
    for i in empty_types:
        print('> ' + i)

    print('\nTotal', np.sum(nrs), 'runs.')
    return

def type_indices ():
    #   precondition
    assert( True )
    #   postcondition
    # For each index, print the types inside.

    base_types  = set.standard_types()
    base_types.append('rest')
    index_types = []

    # Determine all types for all existing indices
    files = os.listdir(set.directories('user'))
    for file in files:  
        nums = general.find_numbers(file, 3, int)
        path = set.directories('user') + file        

        indices = [index_types[i][0] for i in range(len(index_types))]
        index_pos = general.find_value (indices, nums[0])

        if index_pos == -1:
            index_types.append([nums[0]])

        info = read.peaks(path)[2]
        type_pos = general.find_value (base_types, info[3])
        index_types[index_pos].append (type_pos)

    # Print results
    print('Indices with their runtypes:')
    tot_runs = 0
    space_per = 5

    for name in base_types:
        if len(name)+2 > space_per:
            space_per = len(name)+2

    for group in index_types:
        to_print = '> ' + str(group[0])
        to_print = general.fill_to(to_print, 12, ' ')

        for type_ind in group[1:]:
            to_print += base_types[type_ind]
            tot_runs += 1
    
            for i in range(space_per-len(base_types[type_ind])):
                to_print += ' '
        
        print(to_print)

    print('\nTotal', tot_runs, 'runs.')
    return

def type_base (command):
    #   precondition
    assert(command[1] in set.standard_types())
    #   postcondition
    # Write down all indices which have this type.

    base_type = command[1]
    grouped_runs = []

    # Loop all run files, determine type, add if it matches.
    files = os.listdir(set.directories('user'))
    for file in files:  
        nums = general.find_numbers(file, 2, int)
        path = set.directories('user') + file        
    
        index, run_nr = nums
        info = read.peaks(path)[2]

        if info[3] == base_type:
            indices = [grouped_runs[i][0] for i in range(len(grouped_runs))]
            index_pos = general.find_value (indices, index)

            if index_pos == -1:
                grouped_runs.append([index])

            grouped_runs[index_pos].append(run_nr)

    # Print results
    if len(grouped_runs) == 0:
        print('No runs match type', base_type)
        return

    print('Run numbers which match the type ' + base_type + ':')
    tot_runs = 0
    for group in grouped_runs:
        to_print = '> ' + str(group[0])

        while len(to_print) < 12:
            to_print += ' '

        for run_nr in group[1:]:
            to_print += str(run_nr)
            tot_runs += 1
    
            for i in range(int(1-np.floor(np.log10(run_nr)))):
                to_print += ' '
        
        print(to_print)

    print('\nTotal', tot_runs, 'runs.')

    return

def type_rest ():
    #   precondition
    assert(True)
    #   postcondition
    # Print all runs with their rest types    

    # Find files
    combined = []
    files    = os.listdir(set.directories('user'))
    for file in files:
        nums = general.find_numbers(file, 2, int)
        path = set.directories('user') + file
        info = read.peaks(path)[2]
        if info[3] not in set.standard_types():
            combined.append( [nums[0], nums[1], info[3]] )
    
    # Print results
    if len(combined) == 0:
        print('No runs have been marked with a rest type.')
        return

    print('The following ' + str(len(combined)) + \
        ' runs with alternative type were found:\n')
    for combi in combined:
        to_print  = '> ' + str(combi[0])
        to_print  = general.fill_to(to_print, 7, ' ')
        to_print += str(combi[1])
        to_print  = general.fill_to(to_print, 10, ' ')
        to_print += combi[2]
        print(to_print)

    return

def types (command):
    #   precondition
    assert( assert_types (command) )
    #   postcondition
    # Initiate one of the following command types:
    # 1) Print a list of all types and their frequency.
    # 2) Print a list of files and the types of each run
    # 3) Print for 1 type the corresponding runs and the total frequency

    # Case 1
    if len(command) == 1 or command[1] == 'amount':
        type_amount ()
        return

    # Case 2
    if len(command[1]) >= 3 and command[1][:3] == 'ind':
        type_indices ()
        return

    # Case 3
    if command[1] in set.standard_types():
        type_base (command)
        return

    # Case 4
    if command[1] == 'rest':
        type_rest ()
        return

    # Error
    print('Could not apply your type command.')
    return

# Re-type
def re_type (command):
    #   precondition
    assert(len(command) == 3)
    assert(command[0] == 're-type')
    #   postcondition
    # Change all types from a base type to a new base type

    if command[1] not in set.standard_types() or command[2] not in set.standard_types():
        print('Re-type can only recast base types to base types.')
        return

    files = os.listdir(set.directories('user'))
    changes = 0
    for file in files:
        path = set.directories('user') + file
        assert( len(general.find_numbers(file, 3, int)) == 2 )
    
        alpha, beta, info = read.peaks (path)
        if info[3] == command[1]:
            info[3] = command[2]
            save.peaks_simple('user', alpha, beta, info)
            changes += 1

    print('Changed', changes, 'types from', command[1], 'to', command[2])
    return

# Odd theta & redo all theta
def odd_theta (show = True, dev = 5):
    #   precondition
    assert(True)
    #   postconition
    # Print or return a list of files which have a bad theta value.   
    # bad theta = more than a specified deviation from 60.

    # Find files
    grouped_files = []
    full_names    = []
    files = os.listdir(set.directories('user'))
    
    for file in files:
        path = set.directories('user') + file
        nums = general.find_numbers(file, 3, int)

        if len(nums) != 2:
            print('Illegal file:', file)
            return

        info = read.peaks(path)[2]

        if abs(info[4] - 60) > dev:
            indices = [grouped_files[i][0] for i in range(len(grouped_files))]
            index_pos = general.find_value (indices, nums[0])

            if index_pos < 0:
                grouped_files.append( [nums[0]] )
    
            grouped_files[index_pos].append(nums[1])
            full_names.append(file)        

    # Print or return results
    if not show:
        return full_names

    if len(grouped_files) == 0:
        print('No bad theta values were found.')
        return
    
    print('The following runs have a theta value outside', \
            60-dev, '-', 60+dev)
    tot_runs = 0
    for group in grouped_files:
        to_print = '> ' + str(group[0])

        while len(to_print) < 8:
            to_print += ' '
    
        for run_nr in group[1:]:
            to_print += str(run_nr)
            tot_runs += 1

            for i in range(1-int(np.floor(np.log10(run_nr)))):
                to_print += ' '
        
        print(to_print)

    print('In total', tot_runs, 'runs had a bad theta.')
    return 

def redo_theta ():
    #   precondition
    assert(True)
    #   postcondition
    # Redo all files which have a theta value deviating too much
    #    from the currently implemented analysis.
    
    # Find files
    files = os.listdir(set.directories('user'))
    files_reset = 0
    start = time.time()

    for ind, file in enumerate(files):
        print('Busy for', general.string_round(time.time() - start, 1),\
                'seconds, now at', general.string_round(ind/len(files)*100, 1), '%.') 
        path = set.directories('user') + file
        nums = general.find_numbers(file, 2, int)

        alpha, beta, info = read.peaks(path)
        print('Starting with index', nums[0], 'run', nums[1], 'with angle', info[4])
        add = (execute.theta(['theta'], alpha, beta, info, dev = 0.1) == 'remake')

        if add:
            files_reset += 1

        print()

    print('Remade', files_reset, 'runs, their types are set to auto.')
 
    return