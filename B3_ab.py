import numpy as np
import os
import time

import F0_set as set
import F1_generalised as general

# Group 1: Base filter
def has_potential (max_x, max_y, y, avg_y):
    #   precondition
    assert(y > 0)
    assert(y in max_y)
    assert(len(max_x) == len(max_y))
    #   postcondition
    # Return if the peak has potential as a non-offside peak

    pos   = general.find_value(max_y, y)

    # Case 1: pyramid
    pot1   = pos > 1 and pos < len(max_y)-2
    
    pot1_1 = pot1   and y            > max_y[pos+1] + avg_y*0.3
    pot1_1 = pot1_1 and max_y[pos+1] > max_y[pos+2] + avg_y*0.1
    pot1   = pot1_1  or (pot1 and y  > max_y[pos+1] + avg_y*0.9)
    
    pot1_2 = pot1   and y            > max_y[pos-1] + avg_y*0.3
    pot1_2 = pot1_2 and max_y[pos-1] > max_y[pos-2] + avg_y*0.1
    pot1   = pot1_2  or (pot1 and y  > max_y[pos-1] + avg_y*0.9)
    
    # Case 2: hard maximum
    pot2 = pos > 0 and pos < len(max_y) -1
    pot2 = pot2 and y > max_y[pos+1]*1.7
    pot2 = pot2 and y > max_y[pos-1]*1.7
    pot2 = pot2 and y > 1.7*avg_y

    # Case 3: double-peaked hard max left lob
    pot3 = pos > 0 and pos < len(max_y)-2
    pot3 = pot3 and y > 2*avg_y
    pot3 = pot3 and y > max_y[pos+2]*2
    pot3 = pot3 and y > max_y[pos-1]*2
    pot3 = pot3 and abs(y-max_y[pos+1]) < 0.2*y

    # Case 4: double-peaked hard max right lob
    pot4 = pos > 1 and pos < len(max_y)-1
    pot4 = pot4 and y > 2*avg_y
    pot4 = pot4 and y > max_y[pos-2]*2
    pot4 = pot4 and y > max_y[pos+1]*2
    pot4 = pot4 and abs(y-max_y[pos-1]) < 0.2*y

    return pot1 or pot2 or pot3 or pot4

def potential_peaks (fft):
    #   precondition
    assert(fft.__class__ in [list,np.ndarray])
    assert(len(fft) == 2)
    assert(len(fft[0]) == len(fft[1]))
    #   postcondition
    # Return the potential peaks. These are the conditions:
    #   1) higher than the average peak in the allowed region
    #   2) 30% 1st order max OR 50% 2nd order max

    # reduce FFT
    x, y = np.array(fft)
    y = y [x < set.settings('max_base_freq')]
    x = x [x < set.settings('max_base_freq')]
    y = y [x > 3500]
    x = x [x > 3500]

    # Find maxima
    max_ind  = general.extreme_indices(y, 1, 0)[0]
    max_x    = x[max_ind]
    max_y    = y[max_ind]
    temp_y   = max_y[max_x > 7000]
    general.bubble_sort(temp_y, False)
    avg_y    = np.average( temp_y[ temp_y < temp_y[ int(np.floor((len(temp_y))/4.)) ] ] )
    print('The limiting amplitude is ' + general.string_round(avg_y, 1))

    # Add peaks
    freq, ampl = [], []
    for i, ind in enumerate(max_ind):
        if has_potential (max_x, max_y, y[ind], avg_y):
            freq.append(x[ind])
            ampl.append(y[ind])

    # Assure the highest 3 peak-peaks are present.
    max2_ind = general.extreme_indices(max_y, 1, 0)[0]
    max2_y   = max_y[max2_ind]
    max2_x   = max_x[max2_ind]
    order = general.bubble_sort(max2_y, False)
    max2_x = max2_x[order]

    for ind in range(3):
        if max2_x[min(ind, len(max2_x)-1)] not in freq:
            freq.append(max2_x[ind])
            ampl.append(max2_y[ind])

    return freq, ampl

# Group 2: A&B filter
def filter_harmonics (series_freq, series_ampl, peak_freq, peak_ampl):
    #   preconditions
    assert(len(peak_freq)   == len(peak_ampl))
    assert(len(series_freq) == len(series_ampl))
    #   postconditions
    # mark the peaks which are higher harmonics of base.

    # see if the call is a corner case and has to end.  
    if len(series_freq) == 0:
        return series_freq, series_ampl, peak_freq, peak_ampl

    # initiate loop
    base_freq = series_freq[0]
    p = 1
    harmonic_found = True
    mask = np.ones ( len(peak_freq), dtype = bool )
    
    # each while, all HH appearing after the previous HH in the array is found
    # the while ensures that they are all found even if they are not in order.
    while harmonic_found:
        peak_freq, peak_ampl = peak_freq[mask], peak_ampl[mask]
        mask = np.ones ( len(peak_freq), dtype = bool )
        harmonic_found = False

        # each peak ...
        for peak_index in range(len(peak_freq)):
            freq = peak_freq[peak_index]
            ampl = peak_ampl[peak_index]
        
            # ... checked
            if abs( base_freq * (p+1) - freq ) < 100:
                series_freq.append(freq)
                series_ampl.append(ampl)
                p += 1
                mask [peak_freq == freq] = False
                harmonic_found = True

    return series_freq, series_ampl, peak_freq, peak_ampl

def filter_alpha (freq, ampl):
    #   preconditions
    assert(len(freq) == len(ampl))
    assert(len(freq) >= 3)
    #   postconditions  
    # Filter out the alpha base peaks.
    # Return the alpha peaks & remaining given peaks.

    # version1: select the 3 highest peaks
    freq, ampl = np.array(freq), np.array(ampl)
    mask = np.ones(len(freq), dtype = bool)
    alpha_freq = []
    alpha_ampl = []
    for i in range(3):
        freq, ampl = freq[mask], ampl[mask]
        mask = np.ones(len(freq), dtype = bool)

        alpha_index = np.argmax(ampl)

        alpha_freq.append( freq[alpha_index] )
        alpha_ampl.append( ampl[alpha_index] )        

        mask[alpha_index] = False
    
    # version2: sort the alpha from high to low freq in indices
    alpha_freq = np.array(alpha_freq)
    alpha_ampl = np.array(alpha_ampl)
    index_order = np.argsort(alpha_freq)
    index_order = list(reversed(index_order))
    
    alpha_freq2 = []
    alpha_ampl2 = []
    for index in index_order:
        alpha_freq2.append ( alpha_freq[index] )
        alpha_ampl2.append ( alpha_ampl[index] )

    # finalise: delete freqs < 1a1 + 1000.
    min_freq = alpha_freq2[0] + 1000
    ampl = ampl [freq > min_freq]
    freq = freq [freq > min_freq]
    return alpha_freq2, alpha_ampl2, freq, ampl
        
def filter_beta (freq, ampl):
    #   precondition    
    assert(freq.__class__ == np.ndarray or freq.__class__ == list)
    assert(ampl.__class__ == np.ndarray or ampl.__class__ == list)
    assert(len(freq) == len(ampl))
    #   postcondition   
    # Divide up the peaks into beta series.
    # Return beta: [serie num] --> [freq/ampl] --> [harmonic num / floats]

    freq, ampl = np.array(freq), np.array(ampl)
    b_freq = []
    b_ampl = []

    # filter the lowest freq peak out and add it as beta.
    # then filter all harmonics of this peak.
    # continue on untill no peaks are left.
    while len(freq[ freq < set.settings('max_base_freq') ]) > 0:  
        index = np.argmin(freq)

        beta_freq_now = [freq[index]]
        beta_ampl_now = [ampl[index]]
        ampl = ampl[ampl != beta_ampl_now]
        freq = freq[freq != beta_freq_now]

        beta_freq_now, beta_ampl_now, freq, ampl = filter_harmonics (beta_freq_now, beta_ampl_now, freq, ampl)
        b_freq.append( beta_freq_now )
        b_ampl.append( beta_ampl_now )

    # now reshape from [freq/ampl] --> [serie num] --> [harmonic num / floats]
    # to               [serie num] --> [freq/ampl] --> [harmonic num / floats]
    beta = [b_freq, b_ampl]
    return [ [beta[i][j] for i in [0,1] ] for j in range(len(beta[0])) ]

# Group 3: Main
def derive (fft):
    #   precondition
    assert(fft.__class__ == list or fft__class__ == np.ndarray)
    assert(len(fft) == 2)
    assert(len(fft[0]) == len(fft[1]))
    #   postcondition
    # return the alpha and beta peaks of the FFT.
    # [serie num] --> [freq/ampl] --> [floats / harmonic num]

    fft = np.array(fft)     

    freq, ampl                   = potential_peaks  (fft)
    a_freq, a_ampl, freq, ampl   = filter_alpha     (freq, ampl)
    a1_freq, a1_ampl, freq, ampl = filter_harmonics ([a_freq[0]], [a_ampl[0]], freq, ampl)
    a2_freq, a2_ampl, freq, ampl = filter_harmonics ([a_freq[1]], [a_ampl[1]], freq, ampl)
    a3_freq, a3_ampl, freq, ampl = filter_harmonics ([a_freq[2]], [a_ampl[2]], freq, ampl)
    
    alpha    = [ [a1_freq, a1_ampl], [a2_freq, a2_ampl], [a3_freq, a3_ampl] ]
    all_beta = filter_beta      (freq, ampl)     
  
    return alpha, all_beta

