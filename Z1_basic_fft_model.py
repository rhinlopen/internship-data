import numpy as np
import matplotlib.pyplot as plt
import os

import F0_set as set
import F1_generalised as general
import F3_read as read

#General graph with multiplicative weights:
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

def weight_func (distance, cut_off, scaling):

    if distance == 0:
        return 1

    if distance == 1:
        return cut_off

    factor = cut_off
    for i in range(distance-1):
        factor /= scaling

    # old formula:
    #  cut_factor ** ( (1-scaling**distance) / scaling )

    return factor

def get_weight (options, weights, start, end):
    #   precondition
    assert(options.__class__ == list or options.__class__ == np.ndarray)
    assert(weights.__class__ == list or weights.__class__ == np.ndarray)
    assert(find_value(options, start) >= 0)
    assert(find_value(options, end) >= 0)
    for w in weights:
        assert(general.can_type(w, float))
    assert(len(weights) == len(options)*(len(options) - 1)/2)
    for ind, option in enumerate(options):
        for ind2, option2 in enumerate(options):
            assert(option != option2 or ind == ind2)
    #   postcondition
    # Return the weight associated with this transition in the graph.

    start_ind   = find_value(options, start)
    end_ind     = find_value(options, end)

    # corner case
    if start == end:
        return 1

    # reduce to situation end > start
    if start_ind > end_ind:
        temp = start_ind
        start_ind = end_ind
        end_ind = temp

    # sum( len-1 + ... + (len-start_ind) )       + steps from start to stop
    index = (2*len(options)-start_ind-1)*(start_ind)/2 + end_ind - start_ind - 1

    index = int(index)
    return weights[index]

def path_weight (path, options, weights):
    
    weight = 1
    for ind in range(len(path)-1):
        weight *= get_weight (options, weights, path[ind], path[ind+1])
            
    return weight

def filter_paths (paths):

    for index, path in enumerate(paths):
        go_on = True

        for position, element in enumerate(path):
            
            if position == 0:
                if element == path[1]:
                    del paths[index]
                    go_on = False

            elif go_on and position == len(path) - 1:
                if element == path[position-1]:
                    del paths[index]
                    go_on = False
        
            elif go_on: 
                if element == path[position-1] or element == path[position+1]:
                    del paths[index]
                    go_on = False

    return paths

def find_paths_w (start, end, options, weights, max_weight, characteristics):
    #   precondition
    assert(general.can_type(max_weight, float))
    assert(len(weights) == 0.5*(len(options)-1)*len(options))
    assert(start in options)
    assert(end in options)
    #   postcondition
    # Return all paths with at most steps+1 elements
    # which have a weight less than or equal to max_weight.

    paths = [[start, end]]
    answer = []
    end_index = find_value (options, end)

    while len(paths) > 0:
        new_set = []
        for ind, path in enumerate(paths):
            good_paths = 0

            for option in options:
                if option == path[-2]:
                    continue

                # copy the current path
                temp = [i for i in path]
        
                # add option
                temp.append(0)
                temp[-2] = option
                temp[-1] = end                
    
                # check if it still fits
                weight = path_weight (temp, options, weights)
                
                # if it fits, add it.
                if weight < max_weight:
                    new_set.append(temp)
                    good_paths += 1

            answer.append(path)

        paths = new_set

    answer = filter_paths (answer)
                    
    return answer

def find_paths (start, end, steps, options):
    assert(start in options)
    assert(end in options)

    if steps <= 0:
        return [start]

    paths = [[start]]

    for i in range(steps-1):

        for ind, path in enumerate(paths):
            new_set = []
            for option in options:
                # make copy NOT reference:
                temp = [i for i in path]
                temp.append(0)
                temp[-1] = option
                new_set.append(temp)

        paths = new_set

    for path in paths:
        path.append(end)

    return paths

# FFT model
def paths_to_follow (freq, base_freq, base_ampl, characteristics):
    #   precondition
    assert(freq.__class__ == np.ndarray)
    assert(base_freq.__class__ == np.ndarray)
    assert(base_ampl.__class__ == np.ndarray)
    for i in base_ampl:
        assert(i > 0)
    for i in base_freq:
        assert(i in freq)
    assert(len(base_ampl) == len(base_freq))
    #   postcondition
    # Return all corrections.
    
    cut_off, scaling = characteristics
    compensation = np.zeros(len(base_freq))

    weights = []
    for ind1, f1 in enumerate(base_freq):
        for ind2, f2 in enumerate(base_freq):
            if ind2 > ind1:
                pos1 = find_value(freq, f1)
                pos2 = find_value(freq, f2)

                factor = weight_func (abs(pos2 - pos1), cut_off, scaling)
                weights.append(factor)

    for index, f in enumerate(base_freq):
        for index2, f2 in enumerate(base_freq):
            # choose weight = start to get all error terms > 1 ampl unit.
            # paths = find_paths_w (f2, f, base_freq, weights, base_ampl[index2], characteristics)
            paths = find_paths (f2, f, 1, base_freq)

            paths_weight = []
            for path in paths:
                paths_weight.append(path_weight (path, base_freq, weights))
            
            #print(paths, paths_weight)

            inverse_sum = 0
            for w in paths_weight:
                if w != 1:
                    inverse_sum += 1/w

            compensation[index] += inverse_sum* base_ampl[index2]

    return compensation

def recreate_ampl (freq, base_f, base_a, characteristics):

    comp = paths_to_follow (freq, base_f, base_a, characteristics)

    for index in range(len(base_a)):
        base_a[index] -= comp[index]

    return base_a

def model_fft ():

    # settings and init
    file        = os.path.join(set.directories('user'), '121 FFT.dat')
    F, A        = np.array(read.read_fft_part (file, 2))
    A           = A[F>3000]
    F           = F[F>3000]
    A           = A[F<15000]
    F           = F[F<15000]
    indices     = general.extreme_indices(A, 1, 0)[0]
    freq        = F[indices]
    fft_ampl    = A[indices]
        #resulting answer fft

    max_ind = general.extreme_indices(fft_ampl, 1, 0)[0]
    base_freq = freq[max_ind]
    base_ampl = fft_ampl[max_ind]

    model_ampl = np.zeros(len(freq)) #modeled answer from the pure max of max
    cut_factor = 3
    scaling    = 2/3

    # Model round 1
    characteristics = [cut_factor, scaling]
    model_base_ampl = recreate_ampl (freq, base_freq, base_ampl, characteristics)

    # Model round 2   
    for ind, f in enumerate(base_freq):
        start_ampl = base_ampl[ind]
        position_f = find_value (freq, f)

        if position_f == -1:
            print('ERROR')
            return

        for ind in range(len(model_ampl)):
            factor = weight_func (abs(ind - position_f), cut_factor, scaling)
            model_ampl[ind] += start_ampl / factor

    plt.plot(F, A, 'g-')
    plt.plot(freq, fft_ampl, 'b-')
    plt.plot(freq, fft_ampl, 'bo')
    plt.plot(freq, model_ampl, 'r-')
    plt.plot(freq, model_ampl, 'ro')
    plt.ylim(0, np.max(base_ampl)*1.2)
    plt.show()

    return

model_fft()