import os

import F0_set as set
import F1_generalised as general

# Definitions
def skip_command_words ():
    #   precondition
    assert(True)
    #   postcondition
    # Return a list of words which should be skipped from a command.

    words = []
    words.append('from')
    words.append('to')
    words.append('file')

    return words

def correct_commands (commands):
    #   precondition
    assert(commands.__class__ == list)
    #   postcondition
    # Return true if the command list is valid, 
    # false if any entry is invalid.

    valid = True

    for command in commands:
        for entry in command:
            valid = valid and entry.__class__ == str
            valid = valid and len(entry) > 1
            valid = valid and len(entry) < 11
            if not valid:
                print('command entries have to be 2-10 char long.', entry)
                return valid

        last_oblig_ind = -1
        for ind in range(len(command) - 1):
            entry = command[ind+1]
            valid = valid and (entry[0] == '-' or entry[0] == '*')

            if entry[0] == '*' and last_oblig_ind == -1:
                last_oblig_ind = ind

            valid = valid and not (entry[0] == '-' and last_oblig_ind >= 0)
            valid = valid and (entry[1:] == 'int' or entry[1:] == 'str' or entry[1:] == 'float')

        if not valid:
            print('One or more commands are invalid.')
            print('Entries have to be integers, strings or floats.')
            print('The order is always [obligatory] [optional].')
            print(command)
            return valid

    return valid

# Enter & Split Command
def is_legal (char):
    #   precondition
    assert(char.__class__ == str)
    assert(len(char) == 1)
    #   postcondition
    # return true if the char is legal, else false.

    # only non-caps (97-122), numbers (48-57) and . - (46, ?) are allowed characters.
    if char == '.' or char == '-':
        return True
    
    if ord(char) > 122:
        return False

    if ord(char) > 57 and ord(char) < 97:
        return False
                
    if ord(char) < 48:
        return False
       
    return True

def divide_command (command):
    #   precondition
    assert(command.__class__ == str)
    #   postcondition
    # divide command into array elements, seperated by one/more illegal characters.

    split_command = []
    start_index, moving_index = 0, 0
    
    # seperate all words/instances of legal characters.
    while moving_index < len(command):
        if not is_legal(command[moving_index]) and moving_index == start_index:
            start_index = moving_index + 1

        elif not is_legal(command[moving_index]):
            split_command.append( command[start_index:moving_index] )
            start_index = moving_index + 1
        
        moving_index += 1

    # Add the final piece to the command.
    if start_index != moving_index:
        split_command.append( command[start_index:] )    
        
    return split_command

def remove_filler_words (command):
    #   precondition
    assert(command.__class__ == list)
    for i in command:
        assert(i.__class__ == str)
    #   postcondition
    # filter out all of the filler words in command.

    ignore = []

    for ind in range(len(command)):
        for word in skip_command_words ():
            if command[ind] == word:
                ignore.append(ind)

    command = general.delete_array_inds (command, ignore)
    
    return command

def enter_command ():
    #   precondition
    assert(True)
    #   postcondition
    # get a command from the user.
    # keep asking untill it contains at least 1 legal character.

    split_command = []

    while len(split_command) == 0:
        print('Enter a command. For a list of commands, type \'help\'.')
        command = input()

        split_command = divide_command      (command)
        split_command = remove_filler_words (split_command)
                        
    return split_command

# Recognizing command
def compare_command (command, base_command):
    #   precondition
    assert( True )
    #   postcondition
    # Return true if the command fits the specified base command index.
    #   to fit, all keywords of the command need to satisfy
    #   the criteria and there have to be exactly that many keywords.

    # First test the first entry
    if len(command) == 0 or base_command[0] != command[0]:
        return False

    # Then, test all other entries.
    command_position = 1
    for i in range(len(base_command)-1):
        # Determine if the argument is obligatory
        is_obligatory = base_command[i+1][0] == '-'
        if not is_obligatory and base_command[i+1][0] != '*':
            print('uncharacterised command option:', base_command[i+1])
        
        # Test if the command is long enough.
        if command_position >= len(command):
            return not is_obligatory

        # Test argument
        try:
            if   base_command[i+1][1:] == 'str':
                str  (command[command_position])
                command_position += 1
            elif base_command[i+1][1:] == 'int':
                int  (command[command_position])
                command_position += 1
            elif base_command[i+1][1:] == 'float':
                float(command[command_position])
                command_position += 1
            else:
                print('Command entry type not checked for:', base_command[i+1][1:])
        except ValueError:
            if is_obligatory:
                return False

    # final test.
    if len(command) != command_position:
        print('Loose end on command', command)
        return False

    return True

def basic_validity (command, commands):
    #    precondition
    assert( command.__class__ == list )
    assert( correct_commands(commands) )
    #   postcondition
    # Find which command fits the shape of this command.
    # Return the index of this command, return -1 if none fits.

    option_nr = -1

    # go past all possible commands and try to fit them.
    for ind in range(len(commands)):
        fits = compare_command (command, commands[ind])

        if fits and option_nr == -1:
            option_nr = ind
        elif fits:
            print('Ambiguous command. Using the later definition.')
            option_nr = ind

    if option_nr == -1:
        print('Unknown command format or keyword.')
        return -1

    return option_nr

