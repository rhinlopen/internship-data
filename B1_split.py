import os
import numpy as np
import matplotlib.pyplot as plt
import time

from E1_file_master import delete

import F0_set as set
import F1_generalised as general
from F2_fft import no_background

# Assertions
def assert_data (full_data):
    # Row -> type*5

    valid = full_data.__class__ == list or full_data.__class__ == np.ndarray

    if not valid:
        return valid

    for data in full_data:
        valid = valid and (data.__class__ == list or data.__class__ == np.ndarray)
        valid = valid and len(data) == 5
        
        if not valid:
            return valid

        for num in data:
            valid = valid and general.can_type(num, float)

    return valid

def assert_splitting (keep, ignore):

    valid = keep.__class__ == list
    valid = valid and ignore.__class__ == list
    
    if not valid:
        return valid

    for num in keep:
        valid = valid and general.can_type(num, int)

    for interval in ignore:
        valid = valid and (interval.__class__ == list or interval.__class__ == np.ndarray)
        valid = valid and len(interval) == 2
        valid = valid and general.can_type(interval[0], int)
        valid = valid and general.can_type(interval[1], int)

    return valid

def assert_user_split (command):

    valid1 = command.__class__ == list
    valid1 = valid1 and len(command) == 3
    valid1 = valid1 and general.can_type(command[0], int)
    valid1 = valid1 and general.can_type(command[1], float)
    valid1 = valid1 and general.can_type(command[2], float)
    valid1 = valid1 and float(command[2]) > float(command[1])

    valid2 = command == 'done'
    valid3 = command == [0,0,0]

    valid4 = command[0] == 'all'
    valid4 = valid4 and general.can_type(command[1], float)
    valid4 = valid4 and general.can_type(command[2], float)
    valid4 = valid4 and float(command[2]) > float(command[1])

    return valid1 or valid2 or valid3 or valid4

def assert_init (command):
    
    valid = command.__class__ == list
    valid = valid and len(command) >= 1
    valid = valid and command[0] == 'split'

    valid1 = valid and len(command) == 1
    
    valid2 = valid and len(command) == 2
    valid2 = valid2 and general.can_type(command[1], int)

    valid3 = valid and len(command) == 2
    valid3 = valid3 and not general.can_type(command[1], int)
    valid3 = valid3 and general.can_type(command[1], float)

    valid4 = valid and len(command) == 3
    valid4 = valid4 and general.can_type(command[1], int)
    valid4 = valid4 and general.can_type(command[2], int)

    return valid1 or valid2 or valid3 or valid4

def applicable_split (command):
    #   precondition
    assert( assert_init(command) )
    #   postcondition
    # Return if the split command is applicable.

    if len(command) == 1:
        return True

    valid = int(np.floor(float(command[1]))) > 0

    if len(command) == 2:
        return valid

    valid = valid and int(command[2]) > int(command[1])

    return valid

# Group 1: Splitting
def auto_split (array):
    #   precondition
    assert(len(array) > 2)
    for i in array:
        assert(general.can_type(i, float))

    #   Algorithm
    # Start and stop indices of runs are determined as the maxima and minima of 
    # the field (= array) plus the first and final index. However the 
    # start/stop can be flat ("wiggling field") and this causes bad stuff 
    # in interpolate/FFT. Thus remember the indices of extremes which are closer
    # together than min_dist in a seperate array (ignore).

    #   postcondition:
    # Return the start/stop indices of runs 
    # Return the index-intervals in which the field fluctuates too fast.

    last = array[0]
    now = array[1]
    extremes = [0]
    min_dist = 100
    last_extreme = -min_dist
    ignore = []
    
    #loop through all elements with a neighbour; [1, ..., n-1]
    for i in range(len(array[2:])):
        #take the element before, at and after position (i+1).
        next = array[i+2]
        
        if (now >= last and now >= next) or (now <= next and now <= last):
            #extreme means the run has ended and the next begins.
            if i - last_extreme > min_dist:
                extremes.append(i+1)
            
            #mark ignore if the last run lasted too short.
            else:
                if len(ignore) > 0:
                    #combine this short interval with the last one if possible.
                    #so interval 50 - 52, then 52 - 59 with min_dist = 10 then 
                    #instead of [[50,52], [52, 59]], clean it up to [[50, 59]]
                    if extremes[-1] == ignore[-1][0]:
                        ignore[-1] = [extremes[-1],i+1]
                    else:
                        ignore.append([extremes[-1],i+1])
                else:
                    ignore.append([extremes[-1],i+1])
            
            last_extreme = i
            
        last = now
        now = next
    
    #finally analyse the last run, stopping at the end of the array.
    #the last run is either added to extremes or to ignore.
    if i - last_extreme > min_dist:
        extremes.append(i+2)
    else:
        if i - ignore[-1][1] < min_dist:
            ignore[-1][1] = i+2
        else:
            ignore.append([extremes[-1],i+2])
        extremes[-1] = (i+2)
        
    return extremes, ignore

def splitter (full_data, keep, ignore):
    #   precondition:
    # Full data is row --> data type
    assert (assert_data (full_data))
    assert (assert_splitting (keep, ignore))
    #   postcondition
    # Split the data according to keep and ignore    

    sliced = [[]]

    for ind, data_set in enumerate(full_data):
        is_valid = ind not in keep

        if is_valid:
            for interval in ignore:
                if ind > interval[0] and ind < interval[1]:
                    is_valid = False

        if is_valid:
            sliced[-1].append(data_set)
        elif len(sliced[-1]) > 10:
            sliced.append([])    
        else:
            sliced[-1] = []

    if len(sliced[-1]) < 10:
        del sliced[-1]
   
    return np.array(sliced)

def preview_split (all, sliced, index, show):
    #   precondition
    # Full data and sub-sliced: row --> 5*data type
    assert( assert_data(all) )
    assert(sliced.__class__ == list or sliced.__class__ == np.ndarray)
    assert(index.__class__ == int)
    assert(len(show) == 2 and show[0].__class__ == bool)
    assert(show[0] or show[1])
    for i in sliced:
        assert( assert_data(i) )
    #   postcondition
    # Plot in color the runs and ignored parts of the data.

    col = ['g', 'b']
    if show[0]:
        plt.plot(all.T[0], all.T[-1], 'r-')

    if show[1]:
        f, ax_arr = plt.subplots(len(sliced), 1, sharex = True, sharey = True)
        if len(sliced) > 1:
            ax_arr[0].set_title('Julian ' + str(index) + ' with background at 60 degrees.')
        else:   
            ax_arr.set_title('Julian ' + str(index) + ' with background at 60 degrees.')

    for ind, run in enumerate(sliced):
        run = np.array(run)
        
        if show[1]:
            y_data = run[:,1]*0.5*np.sqrt(3) + run[:,2]*0.5
            if len(sliced) > 1:
                ax_arr[ind].plot(run[:,-1], y_data)
                ax_arr[ind].yaxis.set_visible(False)
            else:
                ax_arr.plot(run[:,-1], y_data)        

        if show[0]:
            plt.figure(1)
            plt.plot(run[:,0], run[:,-1], col[ind%2] + '-')

    if show[0]:
        plt.figure(1)
        ylim = plt.gca().get_ylim()
        ylim = [ylim[0]-0.1, ylim[1]+0.1]
        plt.ylim(ylim)
        plt.title('Julian ' + str(index) + ' split into ' + str(len(sliced)) + ' runs')
    
    plt.show()
    return

# Group 2: Adjusting
def valid_slice (string, nr_of_runs):

    valid = string.__class__ == str
    valid = valid and nr_of_runs.__class__ == int
    
    if   string == 'done'   or string == 'show' \
      or string == 'show1'  or string == 'show2' \
      or string == 'help'  or string == 'ignore' \
      or string == 'quit':
        return True

    valid = valid and len(general.find_numbers(string, 4, float)) in [2,3]

    if not valid:
        return valid

    nums = general.find_numbers(string, 3, float)
    valid = valid and len(nums) == 3
    valid = valid and nums[0] == int(nums[0])
    valid = valid and nums[0] > 0
    valid = valid and nums[0] <= nr_of_runs
    valid = valid and float(nums[1]) < float(nums[2])
    valid = valid and float(nums[1]) > 0   
    
    if valid:
        return valid

    nums = general.find_numbers(string, 2, float)
    valid = string[:4] == 'all ' or nr_of_runs == 1
    valid = valid and float(nums[0]) < float(nums[1])
    valid = valid and float(nums[0]) > 0   
    return valid

def help ():

    print()
    print('Enter changes you want to make in the form of commands.') 
    print('Enter run number, low field, high field e.g.: \'5 5.4 6.3\'.')
    print('Enter \'done\' to save.')
    print('Enter \'show\' to preview.')
    print('Enter \'show1\' or \'show2\' to preview only that figure.')
    print('Enter \'ignore\' to remove all red/ignored intervals.')
    print('Enter \'quit\' to stop without saving.')
    print()

    return

def user_slice (runs):
    #   precondition
    assert( runs.__class__ == int)
    assert( runs > 0 )
    #   postcondition
    # Get a slice from the user: run - field low - field high

    print('Enter a split command')
    string = ''

    while not valid_slice (string, runs):
        string = input()

    if string =='done':
        return [0, 0, 0]
    if string =='show':
        return [-1, -5, -4]
    if string =='show1':
        return [-2, -5, -4]
    if string =='show2':
        return [-3, -5, -4]
    if string =='ignore':
        return [-4, -500, -4]
    if string =='quit':
        return [-5, -50, -4]
    if string =='help':
        return [-6, -50, -4]
    
    command = general.find_numbers(string, 3, float)
    
    if len(command) == 2:
        command = ['all', command[0], command[1]]

    return command

def adjust_split (full_data, keep, ignore, command):
    #   precondition
    assert( assert_data(full_data) )
    assert( assert_splitting(keep, ignore) )
    assert( assert_user_split (command) )
    #   postcondition
    # Ignore a part of a run which is not inside the user-defined fieldrange.

    if general.can_type(command[0], int):
        run_inds = [int(command[0])-1]
    else:
        run_inds = np.arange(len(keep)-1)

    for run_ind in run_inds:
        minimal = keep[run_ind]
        maximal = keep[run_ind+1]

        # Lower boundary: ignored part.
        adjusted = True
        while adjusted:
            adjusted = False
            for interval in ignore:
                if minimal >= interval[0] and minimal <= interval[1]:
                    minimal += 1
                    adjusted = True

        # Lower boundary: New ignore
        new_min = minimal
        new_max = maximal
        adjusted = True
        while adjusted:
            adjusted = False
            if new_max > new_min and (full_data[new_min][-1] < command[1] \
                                 or   full_data[new_min][-1] > command[2]):
                new_min += 1
                adjusted = True

        if new_min - minimal > 2:
            ignore.append([minimal, new_min])

        # Upper boundary: ignored part.
        adjusted = True
        while adjusted:
            adjusted = False
            for interval in ignore:
                if maximal >= interval[0] and maximal <= interval[1]:
                    maximal -= 1
                    adjusted = True

        # Upper boundary: New ignore
        adjusted = True
        while adjusted:
            adjusted = False
            if new_max > new_min and (full_data[new_max][-1] < command[1] \
                                  or  full_data[new_max][-1] > command[2]):
                new_max -= 1
                adjusted = True

        if maximal - new_max > 2:
            ignore.append([new_max, maximal])

    return ignore

# Group 3: Saving
def starting_lines (index, run_nr, space_per_float):
    #   precondition
    assert(index.__class__ == int)
    assert(run_nr.__class__ == int)
    assert(space_per_float.__class__ == int)
    #   postcondition
    # Make the base starting intro lines

    text = 'Data for Julian file ' + str(index) + ' run ' + str(run_nr) + '\n'

    new_line = 'Time'
    while len(new_line) < space_per_float:
        new_line += ' '

    new_line += 'X-component'
    while len(new_line) < space_per_float*2:
        new_line += ' '

    new_line += 'Y-component'
    while len(new_line) < space_per_float*3:
        new_line += ' '

    new_line += 'Temperature'
    while len(new_line) < space_per_float*4:
        new_line += ' '

    new_line += 'Field'
    text += new_line + '\n'
    return text

def data_lines (data, space_per_float):
    #   precondition
    assert(data.__class__ == list or data.__class__ == np.ndarray)
    assert(space_per_float.__class__ == int)
    #   postcondition
    # Convert the data to a table.  
    # Each subsequent entry in a line set to space_per_float spaces minimum.

    text = ''

    for row in data:
        new_line = str(row[0])
        while len(new_line) < space_per_float:
            new_line += ' '

        new_line += str(row[1])
        while len(new_line) < space_per_float*2:
            new_line += ' '

        new_line += str(row[2])
        while len(new_line) < space_per_float*3:
            new_line += ' '

        new_line += str(row[3])
        while len(new_line) < space_per_float*4:
            new_line += ' '

        new_line += str(row[4])
        text += new_line + '\n'

    return text

def save_split (index, run_nr, sliced):
    #   precondition
    assert(index.__class__ == int)
    assert(index > 0)
    assert(sliced.__class__ == list or sliced.__class__ == np.ndarray)
    assert( run_nr >= 0 )
    for run in sliced:
        assert( assert_data(run) )
    #   postcondition
    # Save the split data in different files in the split directory.
    
    # Delete existing split files
    files = os.listdir(set.directories('split'))
    for file in files:
        nums = general.find_numbers(file, 2, int)
        if run_nr == 0 and nums[0] == index:
            command = ['delete', 'split', index]
            delete(command)
            break
        elif nums[0] == index and nums[1] == run_nr:
            command = ['delete', 'split', index+run_nr/10.]
            delete(command)
            break
            
    # Write each run
    space_per_float = 15
    for run_ind, data in enumerate(sliced):
        # Create text to enter        
        to_write =  starting_lines (index, run_ind+1, space_per_float)
        to_write += data_lines (data, space_per_float)

        # Write the text
        path =  set.directories('split') + 'Julian_' 
        if run_nr == 0:
            path += str(index) + '_' + str(run_ind+1) + '.dat'
        else:
            assert(run_ind == 0)
            path += str(index) + '_' + str(run_nr) + '.dat'
        file = open(path, 'w+')
        file.write(to_write)
        file.close()

    return

# Main
def split (index, run = 0):
    #   precondition:
    assert (index.__class__ == int)
    #   postcondition: 
    # Create new files in the split directory with the runs split.
    # Let the user adjust the boundaries of the splitting.  
    # Return 1 if the splitting was executed, 0 if it was aborted.

    #big 2D array with data points.
    # full_data:  time - x - y - temp - field | file row
    path        = set.directories('in') + 'Julian_' + str(index) + '.dat'
    if not os.path.isfile(path):
        return 0

    # notify
    os.system('cls')
    if run == 0:
        print('Starting on Julian file ' + str(index))
    else:
        print('Starting on Julian file ' + str(index) + ' run ' + str(run))
    
    full_data   = np.loadtxt(path, skiprows = 6)
    wanted_cols = [0, 3, 4, 5, 6]
    full_data   = general.filter_array_inds (full_data.T, wanted_cols)

    #auto divide into runs based on field maxima/minima
    keep, ignore = auto_split (full_data[-1,:])
    sliced = splitter (full_data.T, keep, ignore)

    if run != 0 and run < len(keep):
        keep = [keep[run-1], keep[run]]
        ignore = [[0, max(0, keep[0]-1) ], [min(keep[1]+1, len(full_data[0])), len(full_data[0])]]
        sliced = splitter(full_data.T, keep, ignore)
    elif run != 0:
        print('Only', len(keep)-1, 'runs available.')
        return 0

    preview_split (full_data.T, sliced, index, [False, True])

    #let user adjust the splitting
    # slice -> show -> adjust limits -> repeat
    status = ''
    while status != 'done':
        sliced = splitter (full_data.T, keep, ignore)
        status = 'busy'
        command = user_slice (len(sliced))
        
        if not general.can_type(command[0], int) or command[0] > 0:
            ignore = adjust_split (full_data.T, keep, ignore, command)
        elif command[0] == -1:
            preview_split (full_data.T, sliced, index, [True, True])
        elif command[0] == -2:
            preview_split (full_data.T, sliced, index, [True, False])
        elif command[0] == -3:
            preview_split (full_data.T, sliced, index, [False, True])
        elif command[0] == -4:
            ignore = []
        elif command[0] == -5:
            return 0
        elif command[0] == -6:
            help()
        else:
            status = 'done'

    save_split (index, run, sliced)
    return 1

def initiate(command):
    #   precondition
    assert( assert_init(command) )
    #   postcondition
    # Split the given files

    if not applicable_split (command):
        print('Could not apply your split command. Aborting...')
        return

    run_nr = 0

    if len(command) == 1:
        min = 0
        max = 10000

    elif len(command) == 2 and general.can_type(command[1], int):
        min = int(command[1])
        max = int(command[1])
    
    elif len(command) == 2:
        command[1] = float(command[1])
        min = int(np.floor(command[1])) 
        max = int(np.floor(command[1]))
        run_nr = int(general.split_float(float(command[1]))[1]*10)
        assert(run_nr.__class__ == int)

    elif len(command) == 3:
        min = int(command[1])
        max = int(command[2])

    files_split = 0
    for i in range(min, max+1):
        files_split += split(i, run_nr)

    print('Succesfully split', files_split, 'file(s)')
    return
