# Program for the analysis of Julian data files.
# Created by Roemer Hinlopen Sep-Nov 2016

import time 
start_time = time.time()
import os

import A3_command as command

import B1_split as split
import B2_analysis as auto
import C1_filter as user
import D1_combine as peaks
import E1_file_master as files
import E2_rest_commands as rest

import F0_set as set
import F1_generalised as general

''' Done:
+A1: Main
+A3: interpretting commands

+B1: split
+B2: auto analysis
+B3: derive ab

+C1: filter
+C2: execute commands

+E1: file master

+F0: set
F1: generalised >>> Testing use of 2 funcs
+F2: create FFT
+F3: read
+F4: save peaks

'''

''' General set-up:
Main command structure
> Split command structure
> Filter command structure
'''

# TO DO
# 1) All filtering
# 2) D1: combine
#       fix 1a1 1a2 1a3
#       save results
# 3) Introduce c peaks for off-side?
# 4) E2: rest
#       show fft
#       field overview (like type)
#       order all
# 5) EXTRA:
#       INTERNET: in C2-show, implement arrow keys for movement left/right. Rescale auto or up/down.
#       In theta optimization, go to a recursive algorithm which starts at a value (base 60) and stepsize(5)
#           then calcs left and right, does step. Each time it cannot, it decreases stepsize by factor 10
#       make a complete-do-over: split-analyse-filter in filter.
#       merge out & user. Make an overwrite-check and question for analyse.
#       find peaks algorithm: add 'wide pyramid': 3rd order pyramid 0%. 1.7*avg value. --> somewhere 105 12500
#       find peaks algorithm: add 'global max': 4th order max 0%. 1.9*avg value. -->10200 at 107.2 | 17000 109.1
#       find peaks algorithm: combi wide pyramid one side, hard drop other. For 13800's like 107.3.
#       re-make re-theta. Make it compile all bad files which differ > 0.01. Then ask the norm for remake (or quit to just get the overview.)
#               odd theta is still usefull: time issue.
#       find peaks algorithm: absolute max: if BOTH 2nd order peaks are higher or 1 is higher, the other insignificant difference ignore.
# 6) Data:
#   165: maybe bad 5.4-5.5? Like the one other file.

# Lists of settings.
def commands ():
    #   precondition
    assert(True)
    #   postcondition
    # return all available command classes.
    # [command keyword, type, type, ...]
    # a '-' means obligatory, a '*' means optional argument.

    # Add command here, to execute and to help.
    
    commands = []
    
    # Programm
    commands.append(['help'])
    commands.append(['cls'])
    commands.append(['quit'])
    commands.append(['stop'])

    # Files
    commands.append(['move', '-str', '-str', '-float', '*float'])
    commands.append(['delete', '-str', '-float', '*float'])
    commands.append(['remove', '-str', '-int', '*int'])

    # Analysis
    commands.append(['split', '*float', '*int'])
    commands.append(['analyse', '*int', '*int', '*float'])   
    commands.append(['filter', '*str', '*str', '*str'])
    commands.append(['peaks', '-str', '-str', '-str', '*str']) 
    commands.append(['peak', '-str', '-str', '-str', '*str'])
    commands.append(['fft', '-str', '-int', '*float', '*float'])

    # Other
    commands.append(['list', '-str'])
    commands.append(['indices', '-str'])
    commands.append(['types', '*str'])
    commands.append(['type', '*str'])
    commands.append(['theta'])
    commands.append(['angle'])

    commands.append(['checktheta'])
    commands.append(['re-type', '-str', '-str'])

    return commands

def print_help ():
    #   precondition
    assert(True)
    #   postcondition
    # Print all commands available.

    # Program:
    to_print  = 'List of possible commands\n'
    to_print += '\nProgram commands:\n'
    to_print += '> help             \n'
    to_print += '> cls              \n'
    to_print += '> quit             \n'
    to_print += '> stop             \n'

    # Files:
    to_print += '\nFile commands:\n'

    to_print += '> move             '
    to_print += '-dir               '
    to_print += '-dir               '
    to_print += '-index             '
    to_print += '*index range       \n' 

    to_print += '> delete | remove  '
    to_print += '-dir               '
    to_print += '-index             '
    to_print += '*index range       \n' 
    
    # Analysis
    to_print += '\nAnalysis commands:\n'
    to_print += '> split            '
    to_print += '*index             '
    to_print += '*index range       \n'

    to_print += '> analyse          '
    to_print += '*index+run/10      '
    to_print += '*index             '
    to_print += '*index range       \n'

    to_print += '> filter           '
    to_print += '-index             '
    to_print += '*index range       '
    to_print += '*analyse stage     \n' 

    to_print += '> peak | peaks     '
    to_print += '*type              '
    to_print += '*freq/ampl         '
    to_print += '*field low         '
    to_print += '*field high        \n'

    to_print += '> fft              '
    to_print += '-dir               '
    to_print += '-index             '
    to_print += '*freq low          '
    to_print += '*freq high         \n'

    # Other
    to_print += '\nRemaining commands:\n'
    
    to_print += '> list | indices   '
    to_print += '-dir               \n'

    to_print += '> types | type     '
    to_print += '*[base=\'amount\', base type, \'ind(ices)\'] \n'

    to_print += '> theta | angle    \n'

    to_print += '> checktheta \n'
    to_print += '> re-type          '
    to_print += '- old type         '
    to_print += '- new type         '

    # Notes
    to_print += '\nNotes:\n'
    to_print += '> Directories are: in, split, out, user \n'
    to_print += '> Standard types are:'

    for type in set.standard_types():
        to_print += ' ' + type

    to_print += '\n'
    to_print += '> Filter: analyse stage can be a standard type, rest or theta.\n'
    to_print += '  The last option uses your index as '
    to_print += 'the max deviation from 60 considered reasonable. (~5)\n'
    
    # Finalise
    print(to_print)
    return

# Initiate a command.
def assert_execute_command (commando, commands):
    if commando.__class__ != list:
        print('Wrong command class', commando)
        return False

    for i in commando:
        if i.__class__ != str:
            print('Wrong command entry class', i)
            return False

        for word in command.skip_command_words ():
            if word == i:
                print('Fix code: Filler word remaining in command', i)
                return False

    return True

def execute_command (commando, commands):
    #   precondition
    assert( assert_execute_command (commando, commands) )
    #   postcondition
    # Initiate the command if possible.
    # Return if the program should quit or not.

    command_type = command.basic_validity (commando, commands)

    if command_type < 0:        return True
    
    keyword      = commands[command_type][0]
    print()

    if command_type > len(commands): 
        print('Something is off with basic_validity. Quiting.')
        return False

    # Programm
    elif keyword == 'help':             print_help ()
    elif keyword == 'cls':              os.system('cls')
    elif keyword == 'quit':             return False        
    elif keyword == 'stop':             return False

    # Files
    elif keyword == 'move':             files.move   (commando)
    elif keyword == 'delete':           files.delete (commando)
    elif keyword == 'remove':           files.delete (commando)
        
    # Analysis
    elif keyword == 'split':            split.initiate(commando)
    elif keyword == 'analyse':          auto.analyse (commando)
    elif keyword == 'filter':           user.filter (commando)
    elif keyword == 'peaks':            peaks.analyse (commando)
    elif keyword == 'peak':             peaks.analyse (commando)
    elif keyword == 'fft':              rest.show_fft (commando)

    # Other
    elif keyword == 'indices':          files.indices (commando)
    elif keyword == 'list':             files.indices (commando)
    elif keyword == 'types':            rest.types(commando)
    elif keyword == 'type':             rest.types(commando)
    elif keyword == 'theta':            rest.odd_theta()
    elif keyword == 'angle':            rest.odd_theta()
    elif keyword == 'checktheta':       rest.redo_theta()
    elif keyword == 're-type':          rest.re_type (commando)

    else:
        print('Command type is recognized, but no implementation seems to be implemented.')

    return True

# Main
def main (start_time):
    #   precondition
    assert(start_time.__class__ == float)
    #   postcondition
    # Execute commands on the data for analysis.
    
    if not set.initiate():
        return

    if not command.correct_commands (commands()):
        return

    print('Succesfully initiated settings, directories and files.')
    go_on = True

    while go_on:
        commando     = command.enter_command ()
        start_time2  = time.time()
        go_on        = execute_command (commando, commands())
        print()

        if time.time() - start_time2 > 5:
            time_taken = general.string_time (time.time() - start_time2)
            print('Executing command took ' + time_taken + '.')
    return

main(start_time)
