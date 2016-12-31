import numpy as np
import scipy.fftpack
import scipy.interpolate
import os
import time
import matplotlib.pyplot as plt

# Group 1: Generator Functions
def num_generator ():
    i = 0
    while True:
        i += 1
        yield i

def timer ():
    #   precondition
    assert(True)
    #   postcondition
    # keep track of the time passed. 
    # return the time and the action performed.

    timer = 0

    while True:
        timer -= time.time()
        yield timer, 'started'

        timer += time.time()
        yield timer, 'stopped'

# Group 2: String Functions
def find_numbers (line, max_numbers, type):
    #   precondition
    assert(max_numbers.__class__ == int)
    assert(line.__class__ == str)
    assert(type == int or type == float)
    #   postcondition
    # return up to max_numbers floats/ints in the line as a list.    

    ind = 0
    numbers = []

    while ind < len(line) and len(numbers) < max_numbers:
        
        stop = ind 
        while (stop < len(line)):
            try:
                stop += 1
                new_num = type ( line[ind:stop] )   
            except ValueError:
                stop -= 1
                break

        if stop > ind :
            new_num = type (line[ind:stop])
            if ind > 0 and line[ind-1] == '-':
                new_num *= -1
            numbers.append(new_num)

        ind = max(stop, ind+1)

    return numbers

def number_layout (number, length):
    #   precondition
    assert(number >= 1)
    assert(number < 10**length)
    assert(length == int(length))
    #   postcondition
    # Return the number as string with 0's to fill up remaining spots.

    pre_zeros = ''

    for i in range(length):
        if number >= 10 ** (length - i - 1):
            return pre_zeros + str(number)

        else:
            pre_zeros += '0' 
    
    print('Error in number_layout, returning some 0\'s')
    print( number, length )
    return pre_zeros

def string_round (num, decimals):
    #   preconditions
    assert(num.__class__ == int or num.__class__ == float or num.__class__ == np.float64)
    assert(decimals.__class__ == int)
    #   postconditions
    # return as a string the rounded number.

    if abs(num) < 0.5*10**-decimals:
        result = '0'
        if decimals > 0:
            result += '.'
        for i in range(abs(decimals)):
            result += '0'
        return result

    # initiate result   
    sign = num / abs(num)
    num = round( abs(num), decimals )
    result = ''
    if sign == -1:
        result += '-'
    
    # determine the pre-. digits
    pre_dot_len = max(1, int (np.log10 (num)) + 1)
    for i in range(pre_dot_len):
        digit = int ( (num * 10 ** (1 + i - pre_dot_len)) % 10)
        result += str(digit)
    
    # the .
    if decimals <= 0:
        return result
    result += '.'

    # the post-. digits.
    for i in range(decimals):
        digit = int( num * 10 ** (i + 1)  % 10)
        result += str(digit)

    return result

def can_type (entry, type):
    #   precondition
    assert(type == int or type == str or type == float or type == bool)
    #   postcondition
    # return if the entry is the selected type.

    try:
        type(entry)
        return True
    except (ValueError, TypeError):
        return False

def fill_to (string, new_len, fill_char):
    #   precondition
    assert(string   .__class__ == str)
    assert(new_len  .__class__ == int)
    assert(fill_char.__class__ == str)
    assert(new_len >= 0)
    assert(len(fill_char) >= 1)
    #   postcondition
    # Fill the string with the given char until it is at least new_len long.

    while len(string) < new_len:
        string += fill_char

    return string

# Group 3: Array Functions
def find_value (array, value):
    #   precondition
    assert(array.__class__ == np.ndarray or array.__class__ == list)
    for ind in range(len(array)):
        assert( array[ind].__class__ == value.__class__ )
    #   postcondition
    # Find the first occurence of value in array.

    for index, element in enumerate(array):
        if element == value:
            return index

    return -1

def insert_element (array, element, position):
    #   precondition
    assert(array.__class__ == list or array.__class__ == np.ndarray)
    assert(position.__class__ == int)
    assert(position >= 0 and position <= len(array))
    #   postcondition
    # Insert the element at the given position

    array.append(0)
    for i in range(len(array)-1, position, -1):
        array[i] = array[i-1]

    array[position] = element
    
    return array

def filter_array_inds (array, wanted_ind):
    #   precondition
    assert(len(array) > 0)
    assert(np.max(wanted_ind) < len(array))
    assert(np.min(wanted_ind) > - len(array))
    #   postcondition
    # return the wanted sub-elements of the array.

    if len(wanted_ind) == 0:
        print('> Warning: filter_cols deletes an array')
        return []
    
    #mark everything as delete ...
    mask = np.zeros(len(array), dtype = bool)

    #... except those indices which are marked wanted.
    for index in wanted_ind:
        mask[index] = True

    array = np.array(array)
    return array[mask]

def delete_array_inds (array, delete_ind):
    #   precondition
    assert(array.__class__ == list or array.__class__ == np.ndarray)
    assert(delete_ind.__class__ == list or delete_ind.__class__ == np.ndarray)
    for ind in range(len(delete_ind)):
        i = delete_ind[ind]
        assert(i.__class__ == int or i.__class__ == np.int)
        assert(i < len(array) and i >= 0)
    # note: duplicates in delete are fine.
    #   postcondition
    # Remove the selected indices from array.

    new_array = []

    for i in range(len(array)):
        delete = False
        for j in delete_ind:
            if i == j:
                delete = True

        if not delete:
            new_array.append(array[i])

    if array.__class__ == np.ndarray:
        new_array = np.array(new_array)

    return new_array

def extreme_indices (array, order, drop_off):
    #   precondition
    assert(array.__class__ == list or array.__class__ == np.ndarray)
    assert(order.__class__ == int and order >= 1)
    assert( (drop_off.__class__ == float and drop_off >= 0 and drop_off < 1 )
            or (drop_off.__class__ == int and drop_off == 0) )
    #   postcondition
    # Return the indices where array has a max/min. 
    # order: that many neighbours to both sides have to be lower/higher for a max/min.
    # drop_off: max: the neighbours are < (1-drop_off)*max
    #           min: the minimum is < (1-drop_off)*neighbour
    #           0: absolute min/max.

    max = []
    min = []

    for iteration in range(len(array) - 2*order):
        i = iteration + order
        is_max = True  
        is_min = True

        for j in np.arange(1, order+1):
            is_min = is_min and i+j < len(array) 
            is_min = is_min and (1-drop_off)*array[i+j] > array[i]
            is_min = is_min and i-j >= 0
            is_min = is_min and (1-drop_off)*array[i-j] > array[i]
            
            is_max = is_max and i+j < len(array) 
            is_max = is_max and (1-drop_off)*array[i] > array[i+j]
            is_max = is_max and i-j >= 0
            is_max = is_max and (1-drop_off)*array[i] > array[i-j]

        if is_max:
            max.append (i)
        if is_min:
            min.append (i)

    return max, min

def delete_equal_neighbours (data):
    #   precondition
    assert(len(data) >= 1)
    assert(len(data[0]) > 1)
    for i in range(len(data) - 1):
        assert( len(data[i]) == len(data[i+1]) )
    #   postcondition
    # Result has array where two equal, neighbouring x-entries are eliminated.
    # the corresponding data in the other lists is also changed.
    # only the first neighbour value is kept. First list in data is x.
    
    x = data[0]
    mask = np.ones(len(x), dtype = bool)

    for j in range(len(x) - 1):
        if x[j] == x[j+1]:
            mask[j+1] = 0

    data = np.array(data)
    new_data = []

    for i in range(len(data)):
        temp = data[i]
        new_data.append(temp[mask])
    
    new_data = np.array(new_data)

    return new_data

def bubble_sort (numbers, ascending):
    #   precondition
    assert(numbers.__class__ == list or numbers.__class__ == np.ndarray)
    assert(ascending.__class__ == bool)
    for i in numbers:
        assert(can_type(i, float))
    #   postcondition
    # Order the numbers using bubble sort. 
    # Sort numbers using REFERENCE!
    # return a list with the index order.

    for i in range(len(numbers)):
        if numbers[i].__class__ == str:
            numbers[i] = float(numbers[i])

    switches = 0
    first_switch_ind = 0
    index_order = np.arange(0, len(numbers), 1)

    for sorted in range(len(numbers)):
        start = max(0, first_switch_ind-1)
        end = len(numbers) - sorted - 1
        indices = np.arange(start, end, 1)
        for ind in indices:
            if ascending and numbers[ind] > numbers[ind+1]:
                swap = True
            elif (not ascending) and numbers[ind] < numbers[ind+1]:
                swap = True
            else:
                swap = False

            if swap:
                temp = numbers[ind]
                numbers[ind] = numbers[ind+1]
                numbers[ind+1] = temp

                temp = index_order[ind]
                index_order[ind] = index_order[ind+1]
                index_order[ind+1] = temp

    return index_order

# Group 4: Data manipulation
def interpolate (x, y, order, n):
    #   precondition
    assert(len(x) > 3)
    assert(len(x) == len(y))
    assert(n > 1)
    #   postcondition
    #   x is linearized into n intervals.
    #   y is interpolated to fit the x values using 'order' as degree.

    x_new = np.linspace(np.min(x), np.max(x), n)

    if order == 1:
        type = 'slinear'
    elif order == 2:
        type = 'quadratic'
    elif order == 3:
        type = 'cubic'
    else:
        print('Warning: Changed interpolation order from ', order, ' to 3')
        type = 'cubic'

    x, y = delete_equal_neighbours([x, y])
    interpolation = scipy.interpolate.interp1d(x, y, kind = type)
    y_new = interpolation(x_new)
    
    return x_new, y_new

def fft (x, y, norm, pad):
    #   precondition:
    assert(pad >= len(x) or np.log2(len(x)) == int(np.log2(len(x))))
    assert(np.log2(pad) == int(np.log2(pad)))
    assert(len(x) > 2)
    assert(len(x) == len(y))
    #   postcondition:
    #   x and y fourier transformed
    
    testing_mode = False
    #plot incoming data
    if testing_mode:
        print('points per unit:', len(x) / (np.max(x) - np.min(x)))         
        plt.figure(1)
        plt.plot(x, y, 'b-')
        plt.title('incoming data fft')
    
    #determine the x interval
    delta_x = (np.max(x) - np.min(x)) / (1.*len(x))

    #pad x and y
    if pad - len(x) > 0:
        zeros = np.zeros(pad - len(x))
        pad_factor = pad / (len(x)*1.)
        padded_x = np.hstack([x,zeros])
        padded_y = np.hstack([y,zeros])
    else:
        padded_x = x
        padded_y = y
        pad_factor = 1    
    
    #fourier transform
    xf = np.linspace(0.0, 1.0 / (2.0*delta_x), len(padded_x)/2)
    yf = abs(scipy.fftpack.fft(padded_y)[:len(padded_x)/2])
    
    #normalize
    if norm:
        yf = yf / np.sum(yf)
    
    if testing_mode:
        plt.figure(2)
        plt.plot(xf, yf, 'b-')
        plt.title('fourier transform')
        plt.show()

    return [xf, yf]

# Group 5: Rest
def string_time (time):
    #   precondition
    assert(time.__class__ == float or time.__class__ == int)
    assert(time >= 0)
    #   postcondition
    # Return a string format dd:hh:mm:ss for time.

    round_intervals = [60, 60, 24, 999]
    str_time = ''
    index = 0
    time = int(time)
    if time == 0:
        return '00:00'

    while time > 0 and index < len(round_intervals):
        entry = time % round_intervals[index]
        time  = int(time / round_intervals[index])

        if index == len(round_intervals) - 1 and time > 0:
            return '999:00:00:00'

        entry = str(entry)
        
        if len(entry) == 1:
            str_time = '0' + entry + ':' + str_time
        else:
            str_time = entry + ':' + str_time
        
        index += 1    

    str_time = str_time[:-1]

    if len(str_time) == 2:
        str_time = '0:' + str_time

    return str_time

def split_float(number):
    #   precondition
    assert(can_type(number, float))
    #   postcondition
    # Split number in an int and positive decimal

    number = float(number)
    integer = int(np.floor(number))
    decimal = number - integer

    return [integer, decimal]
