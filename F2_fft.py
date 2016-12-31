import os
import numpy as np
import time
import matplotlib.pyplot as plt
import scipy.optimize as optimize
import warnings

warnings.simplefilter("ignore", optimize.OptimizeWarning)

import F0_set as set
import F1_generalised as general

# Only internal: Assertions
def assert_data (data):
    # for type -> row
    # 3 data types.

    valid = data.__class__  == list
    valid = valid and (data[0].__class__ == list or data[0].__class__ == np.ndarray)
    valid = valid and (data[1].__class__ == list or data[1].__class__ == np.ndarray)
    valid = valid and (data[2].__class__ == list or data[2].__class__ == np.ndarray)
    valid = valid and len(data[0]) == len(data[1])
    valid = valid and len(data[0]) == len(data[2])

    return valid

def assert_fft (file_index, run_nr, theta, settings, freq_factor):

    valid = file_index.__class__ == int
    valid = valid and run_nr.__class__ == int
    valid = valid and general.can_type(theta, float)
    valid = valid and (theta >= 0 or theta == -1)
    valid = valid and general.can_type(freq_factor, float)
    valid = valid and freq_factor > 0

    path  = set.directories('split') + 'Julian_' 
    path += str(file_index) + '_' + str(run_nr) + '.dat'
    valid = valid and os.path.isfile(path)

    valid = valid and settings.__class__ == list
    valid = valid and len(settings) == 2
    valid = valid and general.can_type(settings[0], int)  
    valid = valid and general.can_type(settings[1], int)  
    valid = valid and int(np.log2(int(settings[0]))) == np.log2(int(settings[0]))
    valid = valid and int(np.log2(int(settings[1]))) == np.log2(int(settings[1]))    
    valid = valid and int(settings[1]) >= int(settings[0])

    return valid

def assert_amplitude (theta, data, pad, order,freq_factor):

    valid = general.can_type(theta, float)
    valid = valid and general.can_type(pad, int)
    valid = valid and general.can_type(pad, int)
    valid = valid and general.can_type(order, int)
    valid = valid and general.can_type(freq_factor, float)
    valid = valid and order > 0 and order < 4
    valid = valid and assert_data (data)
    valid = valid and freq_factor > 0

    if valid and pad > len(data[0]):
        return valid and np.log2(pad) == int(np.log2(pad))
    else:
        return valid and np.log2(len(data[0])) == int(np.log2(len(data[0])))

def assert_sweep (min, max, steps, data, pad, plot, freq_factor):

    valid = general.can_type(min, float)
    valid = valid and general.can_type(max, float)
    valid = valid and general.can_type(steps, int)
    valid = valid and general.can_type(pad, int)
    valid = valid and general.can_type(plot, bool)
    valid = valid and general.can_type(freq_factor, float)
    valid = valid and freq_factor > 0
    valid = valid and min <= max
    valid = valid and steps >= 1

    valid = valid and assert_data (data)

    if valid and pad > len(data[0]):
        return valid and np.log2(pad) == int(np.log2(pad))
    else:
        return valid and np.log2(len(data[0])) == int(np.log2(len(data[0])))
   
def assert_temperature (file_index, run_ind):

    valid = file_index.__class__ == int
    valid = valid and run_ind.__class__ == int
    valid = valid and run_ind >= 0
    return valid

# Group 1: Data interpolation
# Used to get equal 1/B interval spacings.
def check_interpolate_data (x, all_y):
    #   precondition
    assert(True)
    #   postcondition
    # Return true if and only if the data is in a suitable form for data interpolation.

    valid = x.__class__     in [list, np.ndarray]   
    valid = all_y.__class__ in [list, np.ndarray]
    valid = valid and len(x) > 3
    valid = valid and len(all_y) > 0

    if not valid:
        return valid

    # x elements
    for ind, el in enumerate(x):
        valid = valid and general.can_type(el, float)
        valid = valid and el != 0

        if not valid:
            return valid

        for ind2 in range(ind):
            valid = valid and x[ind] != x[ind2]

    # y elements
    for y in all_y:
        valid = valid and y.__class__ in [list, np.ndarray]
        valid = valid and len(y) == len(x)

        if not valid:
            return valid

        for i in y:
            valid = valid and general.can_type(i, float)
    
    return valid

def interpolate_data (x, all_y, new_length):
    #   precondition:
    assert( check_interpolate_data (x, all_y) )
    assert(new_length.__class__ == int)
    assert(new_length >= 0)
    #   postcondition
    # Linearize x over its current range, interpolate the y data columns.

    if new_length == 0:
        return [], []

    if new_length == len(x):
        return x, all_y

    i_x = 1 / np.array(x)   
    new_all_y = []

    for y in all_y:
        new_i_x, new_y = general.interpolate (i_x, y, 3, new_length)
        new_all_y.append(new_y)
    
    new_x = 1/new_i_x

    return new_x, new_all_y

# Group 2: FFT calculation
def no_background (x, y, order, para=False):
    #   precondition
    assert(len(x) >= order+1 and len(x) == len(y))
    assert(order > 0 and order < 4)
    #   postcondition
    #   data is filtered of 3rd order polynomial background.

    if order == 3:
        def func (x, a, b, c, d):
            return a*x**3 + b*x**2 + c*x + d
    
    elif order == 2:
        def func (x, a, b, c, d):
            return a*x**2 + b*x + c

    else:
        def func (x, a, b, c, d):
            return a*x+b

    fit = optimize.curve_fit (func, x, y)[0]
    y = y - func(x, fit[0], fit[1], fit[2], fit[3])
    
    if not para:
        return y
    if para:
        return fit[:order+1]

def amplitude (theta, data, pad, order, freq_factor):
    #   precondition
    assert( assert_amplitude (theta, data, pad, order, freq_factor) )
    #   postcondition
    # return either the maximum amplitude (freq > 2500) of the fft  
    # or the complete fft for theta.
    
    data = np.array(data)
    theta_rad = theta/180.*np.pi
    
    ampl = data[1]*np.cos(theta_rad) + data[2]*np.sin(theta_rad)
    inv_field = 1/data[0]
    ampl = no_background(data[0], ampl, order)

    freq, ampl = general.fft ( inv_field, ampl, False, pad)    
    freq *= freq_factor
    ampl = ampl[freq < set.settings('max_freq')]   
    freq = freq[freq < set.settings('max_freq')]

    return [freq, ampl]

# Group 3: Optimize theta
def theta_sweep (min, max, steps, data, pad, plot, freq_factor):
    #   precondition
    assert( assert_sweep (min, max, steps, data, pad, plot, freq_factor) )
    #   postcondition
    # Result the highest FFT peak for each selected theta value.
    # Plot if requested.
    
    # theta values to evaluate
    if plot:
        steps_sides = int(steps/6.)
        steps_centre = steps - steps_sides*2

        theta1 = np.linspace(min, min + (max-min)/2.*0.5, steps_sides)
        theta2 = np.linspace(min + (max-min)/2.*0.5, max - (max-min)/2.*0.5, steps_centre)
        theta3 = np.linspace(max - (max-min)/2.*0.5, max, steps_sides) 

        theta = []
        for i in theta1:
            theta.append(i)
        for i in theta2:
            theta.append(i)
        for i in theta3:
            theta.append(i)
        theta = np.array(theta)
    else:
        theta = np.linspace(min, max, steps)

    # corresponding fft highs values
    fft_highs = []
    for t in theta:
        freq, ampl = amplitude(t, data, pad, 3, freq_factor)
        ampl = ampl[freq > 2500]
        fft_highs.append( np.max(ampl) )
    
    # result
    if plot:
        plt.figure(1)
        theta_interpolated = general.interpolate (theta, fft_highs, 3, 10000)
        plt.plot( theta, fft_highs, 'bo' )
        plt.plot( theta_interpolated[0], theta_interpolated[1], 'b-' )
        plt.title ('Theta optimization plot')
        plt.xlabel ('Theta (deg)')
        plt.ylabel ('Highest FFT peak')           
        plt.show()
    
    return fft_highs

def theta_optimize (data, pad, plot, freq_factor):
    #   precondition
    assert( assert_data (data) ) 
    assert( general.can_type(plot, bool) )
    assert( int(np.log2(pad)) == np.log2(pad))
    assert( pad >= len(data[0]) )
    assert( freq_factor > 0 )
    #   postcondition
    #   find the optimized theta value for the highest FFT peak amplitude.

    #   Algorithm devises the total interval in steps, then picks the best one of these.
    #       Next it reduces the interval to the values next to the current best one.
    #       Repeat until the error on theta is below the margin.
    #       The ideal steps is chosen after time-tests on Julian_105.dat.
    #       Analytically it is >=7, tests show 8-9.
        
    start  = time.time()
    steps  = 8
    mini   = 25
    maxi   = 100
    
    while (maxi - mini) / 2 > 1e-3:
        peaks = theta_sweep (mini, maxi, steps, data, pad, False, freq_factor)
        theta = np.linspace (mini, maxi, steps)
        extreme_ind = np.argmax(peaks)
        
        mini = theta[ max(0, extreme_ind - 1) ]
        maxi = theta[ min(len(theta) - 1, extreme_ind + 1) ]
        
    theta_opt = (mini + maxi) / 2.
    to_print =  'Optimizing theta to ' + general.string_round(theta_opt, 3) 
    to_print += ' took ' + general.string_round(time.time() - start, 1) + ' seconds.'
    print(to_print)    

    if plot:
        theta_sweep (theta_opt-40, theta_opt+40, 100, data, pad, True, freq_factor)

    return theta_opt

# Main:
def fft (index, run_nr, theta, settings, freq_factor):
    #   precondition
    # settings: interpolate - theta pad - fft pad
    assert( assert_fft(index, run_nr, theta, settings, freq_factor) )
    #   postcondition
    # Derive the FFT
    print('Deriving FFT for Julian ' + str(index) + ' run ' + str(run_nr))
    tijd = time.time()

    # Import run data
    path  = set.directories('split') + 'Julian_'
    path += str(index) + '_' + str(run_nr) + '.dat'
    file = open(path)
    data = np.loadtxt(file, skiprows=2)
    file.close()

    t_data  = [data[i][3] for i in range(len(data))]
    temp    = [np.average(t_data)*6.38 + 0.94357, np.std(t_data)*6.38]
    field   = [data[0][-1], data[-1][-1]]

    # data to [field, x, y] --> row
    cols = [1,2,4]
    data = [ [data[i][j] for i in range(len(data))] for j in cols]
    data[0], data[1:] = interpolate_data (data[2], data[:2], settings[0])

    # Create optimal fft
    if theta <0:
        theta = theta_optimize (data, settings[0]*2, False, freq_factor)

    pad = settings[1]
    freq, ampl = amplitude(theta, data, pad, 3, freq_factor)
    ampl = ampl[freq < set.settings('max_freq')]
    freq = freq[freq < set.settings('max_freq')]
    print('The FFT has stepsize', general.string_round(freq[1]-freq[0], 2) + 'T')
    print('Deriving FFT took ' + general.string_round(time.time() - tijd, 1) + ' seconds.\n')
    return [freq, ampl], field, theta, temp


