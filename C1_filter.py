import os
import time
import numpy as np

import A3_command as command
import C2_peaks_execute as execute

from E2_rest_commands import odd_theta

import F0_set as set
import F1_generalised as general
import F2_fft as fft
import F3_read as read
import F4_save as save

# Assertions
def assert_command (command):
    
    valid = command.__class__ == list
    valid = valid and len(command) >= 1
    valid = valid and len(command) < 5
    valid = valid and command[0] == 'filter'
    
    return valid

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

    try:
        freq, ampl = fft_opt
        valid = len(freq) == len(ampl)

        for i in freq:
            valid = valid and general.can_type(i, float)
        for i in ampl:
            valid = valid and general.can_type(i, float)
    except:
        return False

    return valid

def assert_filter(path):

    valid = path.__class__ == str
    valid = valid and len(general.find_numbers(path, 3, int)) >= 2

    if not valid:
        return valid

    nums = general.find_numbers(path, 99, int)[-2:]
    recreated =  set.directories('user') + 'Julian_' 
    recreated += str(nums[0]) + '_' + str(nums[1]) + ' Analysis.dat'
    valid = valid and recreated == path

    return valid

def assert_recreate (index, run, new_set):

    try:
        path =  set.directories('user') + 'Julian_'
        path += str(index) + '_' + str(run) + ' Analysis.dat'
        valid = os.path.isfile(path)

        valid = valid and len(new_set) == 2
        valid = valid and int(np.log2(new_set[0])) == np.log2(new_set[0])
        valid = valid and int(np.log2(new_set[1])) == np.log2(new_set[1]) 
        valid = valid and new_set[0] <= new_set[1]
    except:
        return False
        
    return valid

# Commands
def commands (show_error = False):
    #   precondition
    assert(True)
    #   postcondition
    # return all available command classes.
    # [command keyword, type, type, ...]
    # a '-' means obligatory, a '*' means optional argument.

    # Add command here, to execute and to help.
    
    command_list = []

    # program commands
    command_list.append(['help'])
    command_list.append(['cls'])
    command_list.append(['quit'])
    command_list.append(['stop'])
    command_list.append(['continue'])
    command_list.append(['next'])

    # visualisation commands
    command_list.append(['list'])
    command_list.append(['options'])
    command_list.append(['show', '*int', '*int'])
    command_list.append(['plot', '*int', '*int'])
    command_list.append(['show1'])
    command_list.append(['plot1'])
    command_list.append(['show2'])
    command_list.append(['plot2'])
    command_list.append(['show3'])
    command_list.append(['plot3'])
    command_list.append(['nb', '*float'])
    command_list.append(['xy'])

    # basic filtering commands
    command_list.append(['move', '-str', '-str'])
    command_list.append(['remove', '-str'])
    command_list.append(['delete', '-str'])
    command_list.append(['add', '-str', '*int'])

    # hard re-calculation commands
    command_list.append(['standard'])
    command_list.append(['reset'])
    command_list.append(['theta', '*float'])
    command_list.append(['angle', '*float'])

    # other
    command_list.append(['order'])
    command_list.append(['shift', '-float'])
    command_list.append(['temp', '-float'])
    command_list.append(['type', '-str', '*str', '*str', '*str', \
        '*str', '*str', '*str', '*str', '*str', '*str', '*str'])
    command_list.append(['base-types'])
    
    basic_command_words = [command_list[i][0] for i in range(len(command_list))]
    for word in set.standard_types():
        if word in basic_command_words:
            if show_error:
                print('Command with same name as a type:', word)    
                print('The shortcut for just naming the base type is disabled.')
            return command_list

    for word in set.standard_types():
        command_list.append([word])        
    
    return command_list

def print_help():
    #   precondition
    assert(True)
    #   postcondition
    # print help
    
    # Legend
    to_print =  'Legend:\n'
    to_print += 'Each line gives the basic name of the command, then the arguments.\n'
    to_print += 'A - means the argument is obligatory, a * means optional.\n'
    to_print += 'Alternative names are seperated by |\n'

    # Basic
    to_print += '\nBasic program commands: \n'
    to_print += '> help             \n'
    to_print += '> cls              \n'
    to_print += '> quit | stop      \n'
    to_print += '> continue | next  \n'
     
    # Visualisation
    to_print += '\nVisualisation commands: \n'
    to_print += '> list | options   \n'
    to_print += '> show | plot      *freq start        *freq stop \n'
    to_print += '> show1 | plot1      \n'
    to_print += '> show2 | plot2      \n'
    to_print += '> show3 | plot3      \n'
    to_print += '> nb               *angle in degrees \n'
    to_print += '> xy               \n'

    # Filtering    
    to_print += '\nFiltering commands: \n'
    to_print += '> move             '
    to_print += '-peak from         '
    to_print += '-peak to           \n'

    to_print += '> remove | delete  '
    to_print += '-peak              \n'

    to_print += '> add              '
    to_print += '-peak to append    '
    to_print += '*frequency        \n'

    # Re-calculation
    to_print += '\nRe-calculate commands: \n'
    to_print += '> reset | standard \n'

    to_print += '> theta | angle    '
    to_print += '*plot width        \n'
    
    # Rest
    to_print += '\nOther commands:  \n'
    to_print += '> base-types   \n'

    to_print += '> type             '
    to_print += '-new type          \n'

    to_print += '> shift            '
    to_print += '-new factor        \n'

    to_print += '> temp             '
    to_print += '-new temp          \n'


    # Notes
    to_print += '\nNotes on certain commands:\n'
    to_print += '> show1:   Shows the region 4000 - 7000\n'
    to_print += '> show2:   Shows the region 6000 - 15000\n'
    to_print += '> show3:   Shows the region 14000 - 20000\n'
    to_print += '> nb:      Shows the basic and no background magnetisation\n'
    to_print += '           Base angle is the one stored in the peaksfile.'
    to_print += '> xy:      Shows 0 and 90 deg FFT, base x and base y data\n'
    to_print += '\n'
    to_print += '> move:    \'peak from\' entered as 3a2, \'peak to\' as b5\n'
    to_print += '> remove:  \'peak\' entered as 3a2 or a2. To delete all beta: b\n'
    to_print += '> add:     \'peak\' can be entered as a2/b5. The next harmonic will be added.\n'
    to_print += '           This can be the next-unoccupied peak. Alternatively, enter \'a\' or \'b\'\n'
    to_print += '           to add a fresh alpha/beta peak. The latter requires a frequency guess.\n'
    to_print += '\n'
    to_print += 'reset:     Recalculates alpha and beta peaks using the built-in analysis.\n'
    to_print += 'theta:     Re-optimize theta, draw (theta, height FFT)\n'  
    to_print += '\n'
    to_print += 'temp:      Enter a negative temperature to restore the file temperature. \n'

    # Print
    os.system('cls')
    print(to_print)
    return

def execute_command (commando, alpha, beta, info, fft_opt):
    #   precondition
    # Warning: loose check on data, file. 
    assert( assert_peaks(alpha, 'a') )
    assert( assert_peaks(beta, 'b'))
    assert( assert_info(info))
    assert( assert_fft (fft_opt))
    #   postcondition
    # Initiate the command if possible.
    # Return if the program should continue or not.
    # Some commands yield their own return statement.

    # Initiate
    command_list = commands()
    command_type = command.basic_validity (commando, command_list)
    if command_type < 0:
        return True
    
    keyword = command_list[command_type][0]

    if (keyword == 'remove' or keyword == 'delete') \
        and len(commando) == 2 and commando[1] == 'b':
        keyword = 'delete_b'

    if command_type > len(command_list):
        print('Something is off with basic_validity. Quiting.')
        return False

    # System
    elif keyword == 'help':         print_help ()
    elif keyword == 'cls':          os.system('cls')
    elif keyword == 'quit':         execute.order (alpha, beta, info)
    elif keyword == 'stop':         execute.order (alpha, beta, info)
    elif keyword == 'next':         execute.order (alpha, beta, info)
    elif keyword == 'continue':     execute.order (alpha, beta, info)

    # Visualisation
    elif keyword == 'list':         execute.list_peaks (alpha, beta, info)
    elif keyword == 'options':      execute.list_peaks (alpha, beta, info)

    elif keyword == 'plot':         return commando
    elif keyword == 'show':         return commando
    elif keyword == 'show1':        return ['show', 4000, 7000]
    elif keyword == 'plot1':        return ['plot', 4000, 7000]
    elif keyword == 'show2':        return ['show', 6000, 15000]
    elif keyword == 'plot2':        return ['plot', 6000, 15000]
    elif keyword == 'show3':        return ['show', 14000, 20000]
    elif keyword == 'plot3':        return ['plot', 14000, 20000]

    elif keyword == 'nb':           execute.nb    (commando, info)
    elif keyword == 'xy':           execute.xy    (alpha, beta, info)

    # Filter 
    elif keyword == 'move':         execute.move     (commando, alpha, beta, info)

    elif keyword == 'delete_b':     execute.delete_b (commando, alpha, beta, info)
    elif keyword == 'delete':       execute.delete   (commando, alpha, beta, info)
    elif keyword == 'remove':       execute.delete   (commando, alpha, beta, info)

    elif keyword == 'add':          execute.add      (commando, alpha, beta, info, fft_opt)

    # Re-calc
    elif keyword == 'theta':        execute.theta (commando, alpha, beta, info)
    elif keyword == 'angle':        execute.theta (commando, alpha, beta, info)

    elif keyword == 'reset':        execute.reset    (commando, alpha, beta, info, fft_opt)
    elif keyword == 'standard':     execute.reset (commando, alpha, beta, info, fft_opt)

    # Other 
    elif keyword == 'order':        execute.order (alpha, beta, info)
    elif keyword == 'temp':         execute.temp  (commando, alpha, beta, info)
    elif keyword == 'shift':        execute.shift (commando, alpha, beta, info)
    
    elif keyword == 'base-types':   execute.list_types ()
    elif keyword == 'type':         execute.type  (commando, alpha, beta, info)
    elif keyword in set.standard_types() and len(commando) == 1:
        execute.type (['type', keyword], alpha, beta, info)

    # Error
    else:
        print('Command type is recognized, but no implementation seems to be implemented.')

    # Give the right respond.    
    if keyword == 'quit':           return 'quit'
    if keyword == 'stop':           return 'quit'

    if keyword == 'next':           return False
    if keyword == 'continue':       return False

    if keyword == 'theta':          return 'remake'
    if keyword == 'shift':          return 'remake'

    return True

# Recreate
def relocate (fft_opt, freq, ampl):
    #   precondition
    assert( assert_fft(fft_opt) )
    assert( general.can_type(freq, float) )
    assert( general.can_type(ampl, float) )
    #   postcondition
    # Find a peak within a small range of the given frequency.
    # Determine the corresponding amplitude and return these two.
    # Dilemma: higher distance more resilient, but increase odds of double/not interesting peak.

    max_distance = 10
    freq0, ampl0 = np.array(fft_opt)
    max_ind = general.extreme_indices(ampl0, 1, 0)[0]
    max_f   = freq0[max_ind]
    max_a   = ampl0[max_ind]

    for index in range(len(max_f)):
        if abs(max_f[index]-freq) < max_distance:
            return max_f[index], max_a[index]

    return 0, 0

def relocate_peaks (fft_opt, peaks):
    #   precondition
    assert( assert_fft (fft_opt) )
    assert( assert_peaks (peaks, 'b') )
    #   postcondition
    # Find the closest maxima to the current peaks and substitute them in.
    
    new_peaks = []
    for serie_ind, serie in enumerate(peaks):
        freq, ampl = serie
        new_peaks.append([[], []])
        for harm_ind in range(len(freq)):
            new_f, new_a = relocate (fft_opt, freq[harm_ind], ampl[harm_ind])

            if new_f != 0:
                new_peaks[-1][0].append(new_f)
                new_peaks[-1][1].append(new_a)
            else:
                print('Peak unresolvable at freq ', freq[harm_ind], 'T; Deleted!')

        if new_peaks[-1] == [[], []]:
            del new_peaks[-1]

    return new_peaks

def recreate (index, run, new_set, freq_fact):
    #   precondition
    assert ( assert_recreate (index, run, new_set) )
    #   postcondition
    # Create FFT with the new settings,
    # find all maxima within 10 T of the current frequencies and
    # derive this way the new amplitudes & frequencies of the saved peaks.
    # Overwrite the peaksfile with this new data.
    
    filepath =  set.directories('user') + 'Julian_' 
    filepath += str(index) + '_' + str(run) + ' Analysis.dat'
    alpha, beta, old_info = read.peaks (filepath)
    fft_opt, field, theta, temp = fft.fft (index, run, -1, new_set, old_info[5])

    #info = [2file, 2field, 2temp, type, angle, 2settings]
    info = [[index, run]]
    info.append(field)
    info.append(temp)
    info.append('auto')
    info.append(theta)
    info.append(old_info[5])
    info.append(new_set)

    #Peaks and save
    alpha = relocate_peaks(fft_opt, alpha)
    beta  = relocate_peaks(fft_opt, beta)

    save.peaks_simple('user', alpha, beta, info)
    print('Succesfully overwritten the file.')
    return fft_opt

# Command processing
def is_type (type):
    #   precondition
    assert(type.__class__ == str)
    #   postcondition

    types = set.standard_types()
    types.append('rest')

    for type0 in types:
        if type0 == type:
            return True

    return False

def classify (command):
    #   precondition
    assert(assert_command(command))
    #   postcondition
    # Give the classification of the command.
    
    # type 1
    if len(command) == 1:
        return '1.'

    # type 2
    valid =           len(command) == 2
    valid = valid and general.can_type(command[1], int)
    if valid:
        return '2.i'
    
    valid =           len(command) == 2
    valid = valid and is_type(command[1])
    if valid:
        return '2.t'

    valid =           len(command) == 2
    valid = valid and general.can_type(command[1], float)
    if valid:
        return '2.f'

    # type 3
    valid =           len(command) == 3
    valid = valid and general.can_type(command[1], int)
    valid = valid and general.can_type(command[2], int)
    if valid:
        return '3.ii'

    valid =           len(command) == 3
    valid = valid and general.can_type(command[1], float)
    valid = valid and general.can_type(command[2], float)
    if valid:
        return '3.ff'
    
    valid =           len(command) == 3
    valid = valid and general.can_type(command[1], int)
    valid = valid and is_type(command[2])
    if valid:
        return '3.it'

    valid =           len(command) == 3
    valid = valid and is_type(command[1])
    valid = valid and general.can_type(command[2], int)
    if valid:
        return '3.ti'

    # type 4
    valid =           len(command) == 4
    valid = valid and is_type(command[1])
    valid = valid and general.can_type(command[2], int)
    valid = valid and general.can_type(command[3], int)
    if valid:
        return '4.tii'

    valid =           len(command) == 4
    valid = valid and general.can_type(command[1], int)
    valid = valid and general.can_type(command[2], int)
    valid = valid and is_type(command[3])
    if valid:
        return '4.iit'

    # type theta
    valid =           len(command) == 3
    valid = valid and general.can_type(command[1], int)
    valid = valid and command[2] == 'theta'
    if valid:
        return '5.i'

    print('Could not recognize filter command.')
    return '0'

def translate (command, command_class):
    #   precondition
    assert(command_class == classify(command))
    #   postcondition
    # Return the index range and type to analyse.
    
    if command_class == '0':
        runs  = [[0,0], [0,0]]
        type = 'all'
    elif command_class == '1.':
        runs = [[0,0], [1000,25]]
        type = 'all'

    elif command_class == '2.i':
        runs = [[int(command[1]), 0], [int(command[1]), 25]]
        type = 'all'
    elif command_class == '2.f':
        runs = [[int(float(command[1])), int( round(float(command[1])%1*10) )], \
                [int(float(command[1])), int( round(float(command[1])%1*10) )]]
        type = 'all'
    elif command_class == '2.t':
        runs = [[0,0], [1000,25]]
        type = command[1]

    elif command_class == '3.ii':
        runs = [[int(command[1]), 0], [int(command[2]), 25]]
        type = 'all'
    elif command_class == '3.ff':
        runs = [[int(float(command[1])), int( round(float(command[1])%1*10) )], \
                [int(float(command[2])), int( round(float(command[2])%1*10) )]]
        type = 'all'
    elif command_class == '3.it':
        runs = [[int(command[1]), 0], \
                [int(command[1]), 25]]
        type = command[2]
    elif command_class == '3.ti':
        runs = [[int(command[2]), 0], \
                [int(command[2]), 25]]
        type = command[1]

    elif command_class == '4.iit':
        runs = [[int(command[1]), 0], \
                [int(command[2]), 25]]
        type = command[3]
    elif command_class == '4.tii':
        runs = [[int(command[2]), 0], \
                [int(command[3]), 25]]
        type = command[1]

    else:
        raise AssertionError('Translate is not up to date.')

    return runs, type

# Find files
def good_file (indices, type, file):
    #   precondition
    assert( indices.__class__ == list)
    assert( type.__class__ == str)
    assert( file.__class__ == str)
    #   postcondition
    # Return if the file has to be filtered or not.

    # initiate
    filepath = set.directories('user') + file
    assert( os.path.isfile(filepath) )
    nums = general.find_numbers(file, 3, int)     
    add = len(nums) == 2
        
    # Larger than start
    add1 = add and nums[0] > indices[0][0]
    add2 = add and nums[0] == indices[0][0] and nums[1] >= indices[0][1]
    add = add1 or add2

    # Smaller than stop
    add1 = add and nums[0] < indices[1][0]
    add2 = add and nums[0] == indices[1][0] and nums[1] <= indices[1][1]
    add = add1 or add2

    # good type
    alpha, beta, info = read.peaks(filepath)   
    add1 = add and type == info[3]    
    add2 = add and type == 'rest' and info[3] not in set.standard_types()
    add3 = add and type == 'all'

    return add1 or add2 or add3

def which_files (command):
    #   precondition
    # assertion implemented in deriving the command.
    #   postcondition
    # Return the run files in the user directory which have to be filtered.
        
    # determine index range
    command_class = classify (command)
    indices, type = translate(command, command_class)

    # find runs to do
    files = os.listdir(set.directories('user'))
    files_to_do = []
    for file in files:
        if good_file(indices, type, file):
            files_to_do.append(file)

    if len(files_to_do) == 0:
        print('No files found to filter.')

    return files_to_do

# Main
def process_end_request (request, path, alpha, beta, info, fft_opt):
    #   precondition
    assert(os.path.isfile(path))
    assert(assert_peaks (alpha, 'a'))
    assert(assert_peaks (beta, 'b'))
    assert(assert_info (info))
    assert(assert_fft (fft_opt))
    #   postcondition
    # Execute a remaining request from the last command if any.
    
    if request == 'remake':
        alpha, beta, info = read.peaks (path)
        fft_opt = fft.fft (info[0][0], info[0][1], info[4], info[6], info[5])[0]
        go_on = True

    elif request.__class__ == list and request[0] in ['show', 'plot']:
        alpha, beta, info = read.peaks (path)
        execute.list_peaks (alpha, beta, info)
        execute.plot_peaks (request, alpha, beta, info, fft_opt)
        go_on = True

    elif request == 'quit':
        go_on = -1
    
    elif request.__class__ == bool:
        go_on = request

    else:
        print('End request of the command could not be executed:', request.__class__, request)
        go_on = False

    return go_on, alpha, beta, info, fft_opt

def filter_file (path):
    #   precondition
    assert( assert_filter(path) )
    #   postcondition
    # Initiate the command structure on peaks filtering.

    # Read in
    #       info = [2field, 2temp, type, angle, 2settings]
    alpha, beta, info = read.peaks (path)
    if not command.correct_commands(commands()):
        print('Fix your filtering commands.')
        return False
    
    # Create FFT
    settings = [set.settings('interpolated_points'), set.settings('pad')]
    if settings[0] != info[6][0] or settings[1] != info[6][1]:
        fft_opt = recreate (info[0][0], info[0][1], settings)
    else:
        fft_opt = fft.fft (info[0][0], info[0][1], info[4], info[6], info[5])[0]

    # Filter
    go_on = True
    while go_on:
        alpha, beta, info = read.peaks (path)
        commando     = command.enter_command ()
        start_time   = time.time()
        go_on        = execute_command (commando, alpha, beta, info, fft_opt)
        print()

        go_on, alpha, beta, info, fft_opt = process_end_request (go_on, path, alpha, beta, info, fft_opt)
        if go_on == -1:
            return False

        if time.time() - start_time > 30:
            time_taken = general.string_time (time.time() - start_time)
            print('Executing command took ' + time_taken + '.')

    return True

def filter(command):
    #   precondition
    assert( assert_command (command) )
    #   postcondition
    # Initiate new command structure

    # find files to filter
    commands(show_error = True)
    class_command = classify (command)

    if class_command == '0':
        return

    if class_command[0] != '5':
        files = which_files (command)
    else:
        files = odd_theta (show = False, dev = int(command[1]))

    start_time = time.time()
    
    # filter files
    for file_ind, file in enumerate(files):
        nums = general.find_numbers(file, 2, int)
        path = set.directories('user') + file
        
        if file_ind > 0:
            os.system('cls')
            print('Busy for', general.string_round(time.time()-start_time, 1), \
                  'seconds, now at', general.string_round(file_ind / len(files)*100, 1), '%')

        print(len(files) - file_ind, 'run(s) to go')

        # do some commands
        go_on = filter_file (path)
    
        if not go_on:
            print('Returning to main command structure.')
            return

    if len(files) > 0:
        print('Filtered all', len(files), 'runs.')
    return

# Notes
'''
Info:
    [2file, 2field, 2temp, type, angle, freq factor, 2settings]

The classification table:
     Classify the command.             return          len(command)
       if not possible:                0               [undef]
       if filter all:                  1               1
       if filter one type:             2.t             2
       if filter one index:            2.i             2
       if filter one run:              2.f             2
       if filter set indices:          3.ii    3.ff    3   
       if filter one index, type:      3.it    3.ti    3     
       if filter set indices, type:    4.iit   4.tii   4

'''

    