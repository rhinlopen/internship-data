import os
import numpy as np

import F0_set as set
import F1_generalised as general

# Definitions
def allowed_dirs (command):
    #   precondition
    assert( command[0] in ['move', 'delete', 'remove', 'list', 'indices'] )
    #   postcondition
    # Return a list of allowed directories.

    allowed = []

    if command[0] == 'move':
        allowed.append(set.directories('user'))
        allowed.append(set.directories('out'))

    elif command[0] in ['delete', 'remove']:
        allowed.append(set.directories('user'))
        allowed.append(set.directories('out'))
        allowed.append(set.directories('split'))

    elif command[0] in ['list', 'indices']:
        allowed.append(set.directories('in'))
        allowed.append(set.directories('split'))
        allowed.append(set.directories('out'))
        allowed.append(set.directories('user'))
    
    else:
        print('No list of allowed directories available for', command[0])

    return allowed

# Assertions
def assert_move (command):

    valid = command.__class__ == list
    valid = valid and len(command) in [4,5]
    valid = valid and command[0] == 'move'

    if not valid: 
        print('first half error')
        return valid

    for i in command[3:]:
        valid = valid and general.can_type(i, float)
    
    return valid

def assert_delete (command):
    
    valid = command.__class__ == list
    valid = valid and len(command) in [3,4]
    valid = valid and command[0] in ['delete', 'remove']

    return valid

def assert_list (command):
    
    valid = command.__class__ == list
    valid = valid and len(command) == 2
    valid = valid and command[0] in ['list', 'indices']

    return valid

# Variously Applicable
def find_files (directory, lower, upper):
    #   precondition
    assert( set.directories(directory) != None)
    assert( len(lower) == 2 )
    assert( len(upper) == 2 )
    #   postcondition
    # Return all files which are between lower and upper indices.

    files = os.listdir(set.directories(directory))
    good_files = []
    for file in files:
        nums = general.find_numbers(file, 3, int)
        add = len(nums) == 2
    
        add1 = add and nums[0] > lower[0]
        add2 = add and nums[0] == lower[0] and nums[1] >= lower[1]
        add = add1 or add2

        add1 = add and nums[0] < upper[0]
        add2 = add and nums[0] == upper[0] and nums[1] <= upper[1]
        add = add1 or add2

        if add:
            good_files.append(file)

    return good_files

# Move 
def applicable_move (command):
    #   precondition
    assert( assert_move (command) )
    #   postcondition
    # see if the command is applicable. If so, return true.

    # basic requirements    
    valid = set.directories(command[0]) in allowed_dirs(command)
    valid = valid and set.directories(command[1]) in allowed_dirs(command)
    valid = valid and set.directories(command[0]) != set.directories(command[1])

    return True

def move (command):
    #   precondition
    assert(assert_move (command))
    #   postcondition
    # move the file.

    # initiate
    start = set.directories (command[1])
    end   = set.directories (command[2])
    if not applicable_move (command):
        return 

    # Lower and upper boundary
    integer3, decimal3 = general.split_float(float(command[3]))
    decimal3 = int(round(decimal3*10))
    if len(command) == 4:
        lower = [integer3, decimal3]
        upper = [integer3, decimal3]
    else:
        integer4, decimal4 = general.split_float(float(command[4]))
        decimal4 = int(round(decimal4*10))
        lower = [integer3, decimal3]
        upper = [integer4, decimal4]
        
    if upper[1] == 0:
        upper[1] = 10

    # From and to.
    file_names = find_files (command[1], lower, upper)
    old_files = []
    new_files = []
    for name in file_names:
        old_files.append( set.directories(command[1]) + name )
        new_files.append( set.directories(command[2]) + name )

    # Overwrite
    bad_files = []
    for file in new_files:
        if os.path.isfile(file):
            bad_files.append(file)
        
    if len(bad_files) > 0:
        print('Do you really want to overwrite the following files? [y/n]')
        for file in bad_files:
            print(file)
        
        string = ''
        while string != 'y':
            string = input()
            if string == 'n':
                print('No files were moved.')
                return

    # Move
    for i in bad_files:
        os.remove(i)

    for i in range(len(new_files)):
        os.rename( old_files[i], new_files[i] )

    print(len(new_files), 'file(s) succesfully moved.')
    return 

# delete command
def applicable_delete (command):
    #   precondition
    assert( assert_delete(command) )
    #   postcondition
    # Return if the delete can be executed.
    
    valid = set.directories(command[1]) in allowed_dirs(command)
    valid = valid and general.can_type(command[2], float)
    valid = valid and (len(command) == 3 or general.can_type(command[3], float))

    return valid

def delete (command):
    #   precondition
    assert( assert_delete (command))
    #   postcondition
    # delete the file group [index - directory]
    # overwrite the last file with this name in the bin.

    if not applicable_delete(command):
        print('Unapplicable delete command.')
        return

    # Find files
    lower = general.split_float(float(command[2]))
    lower[1] = int(lower[1]*10)
    if len(command) == 4:
        upper = general.split_float(float(command[3]))
        upper[1] = int(round(upper[1]*10))
    else:
        upper = [lower[0], lower[1]]

    if upper[1] == 0: upper[1] = 10

    files_to_move = find_files (command[1], lower, upper) 

    if len(files_to_move) == 0:
        print('No files were found to delete.')
        return

    # Start & End
    start_files    = []
    end_files      = []

    for file in files_to_move:
        start_files.append( set.directories(command[1]) + file )
        end_files.append( set.directories('delete') + command[1] + '_' + file )

    # Make space
    files2 = os.listdir (set.directories('delete'))
    for file2 in files2:
        file2 = set.directories('delete') + file2 
        for file in end_files:
            if file == file2:
                os.remove(file)

    # Delete
    for i in range(len(start_files)):
        os.rename( start_files[i], end_files[i] )

    print('Succesfully moved', len(end_files), 'file(s) to the recycle bin')
    return

# list files
def indices_in (command):
    #   precondition
    assert( assert_list(command) )
    assert( set.directories(command[1]) == set.directories('in') )
    #   postcondition
    # Print all indices in the input directory - files have 1 index

    files = os.listdir(set.directories('in'))
    nr_valid = 0
    print('Indices in directory:')
        
    for file in files:
        nums = general.find_numbers(file, 2, int)
        if len(nums) == 1:
            print('>', nums[0])
            nr_valid += 1
        else:
            print('> Illegal file:', file)
            
    if nr_valid > 0:
        print()
        print('Found', nr_valid, 'input files in the directory.')
        return

    print('No valid files in the directory')
    return

def group_files (dir):
    #   precondition
    assert ( os.path.isdir (dir) )
    # Presume all legal files have 2 indices with first primary, then secundary number.
    #   postcondition   
    # Group all indices as [105, 1, 2, 3]
    
    files = os.listdir(dir)
    runs_grouped = []

    # Group runs on their index
    for file in files:
        nums = general.find_numbers(file, 3, int)
        
        if len(nums) != 2:
            raise AssertionError('Illegal file:', file)
        
        set_pos = -1
        for pos, group in enumerate(runs_grouped):
            if nums[0] == group[0]:
                set_pos = pos

        if set_pos >= 0:
            runs_grouped[set_pos].append(nums[1])
        else:
            runs_grouped.append( nums )

    # Sort run numbers within each index
    for pos, group in enumerate(runs_grouped):
        runs = group[1:]
        sorted_runs = general.bubble_sort(runs, True)

        for new_loc, old_loc in enumerate(sorted_runs):
            runs_grouped[pos][new_loc+1] = runs[old_loc]

    # Sort all indices themselves
    indices = [runs_grouped[i][0] for i in range(len(runs_grouped))]
    sorted_indices = general.bubble_sort(indices, True)
    runs_grouped_ordered = []

    for old_loc in sorted_indices:
        runs_grouped_ordered.append( runs_grouped[old_loc] )

    return runs_grouped_ordered

def indices_base (command):
    #   precondition
    assert( assert_list(command) )
    assert( set.directories(command[1]) != set.directories('in'))
    assert( set.directories(command[1]) in allowed_dirs(command))
    #   postcondition
    # Print all indices in a non-input directory - files have 2 indices

    runs_grouped = group_files (set.directories(command[1]))
    nr_runs = 0
    
    if len(runs_grouped) > 0:
        print('Indices in directory:')
        for group in runs_grouped:
            to_print = '> ' + str(group[0]) + '\t'
            
            for run_nr in group[1:]:
                to_print += ' ' + str(run_nr)
                nr_runs += 1        
    
            print(to_print)

        print()
        print('Found', len(runs_grouped), 'groups in the directory.')
        print('Which combined contained', nr_runs, 'runs.')

    else:
        print('No valid files in the directory.')

    return

def indices (command):
    #   precondition
    assert( assert_list (command) )
    #   postcondition
    # Print all indices in the directory.

    # Case 1: Input directory (1 index)
    if set.directories(command[1]) == set.directories('in'):
        indices_in (command)
        return

    # Case 2: Other directory (1 index + 1 run number)
    if set.directories(command[1]) in allowed_dirs(command):
        indices_base(command)
        return
    
    print('No such directory or blocked directory')
    return
