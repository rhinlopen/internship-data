import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import scipy.optimize as opt

import F0_set as set
import F1_generalised as general
import F3_read as read

# checks

def is_peakset (entry):

    valid = entry.__class__ == str

    valid1 = valid and entry == 'b'

    valid2 = valid and len(entry) == 2
    valid2 = valid2 and general.can_type(entry[0], int)
    valid2 = valid2 and entry[1] == 'a'

    valid3 = valid and len(entry) == 3
    valid3 = valid3 and general.can_type(entry[0], int)
    valid3 = valid3 and entry[1] == 'a'
    valid3 = valid3 and general.can_type(entry[2], int)

    return valid1 or valid2 or valid3

def assert_command (command):

    valid = command.__class__ == list
    valid = valid and len(command) in [4,5]
    valid = valid and (command[0] == 'peaks' or command[0] == 'peak')

    return valid

def assert_get_peaks (field, peak_type, read_type):

    try:
        valid = field[0] < field[1]
        valid = valid and len(field) == 2

        valid = valid and is_peakset(peak_type)
        valid = valid and len(peak_type) != 2

        valid = valid and read_type.__class__ == str

    except:
        return False

    return valid

# import

def get_peaks (field, peak_type, read_type):
    #   precondition
    assert( assert_get_peaks(field, peak_type, read_type) )
    #   postcondition
    # Return the temps, freqs and ampls for up an down seperately.

    files = os.listdir(set.directories('user'))
    tempU1, tempU2, freqU, amplU = [], [], [], []
    tempD1, tempD2, freqD, amplD = [], [], [], []

    for file in files:
        filepath = set.directories('user') + file
        alpha, beta, info = read.peaks(filepath)
    
        # check if field and analysis type match.
        do  = abs(info[1][0] - field[0]) < 0.05 or abs(info[1][0] - field[1]) < 0.05
        do  = do  and (abs(info[1][1] - field[0]) < 0.05 \
            or abs(info[1][1] - field[1]) < 0.05)
        do_type = read_type == 'rest' and info[2] not in set.standard_types()
        do_type = do_type or peak_type == 'all'
        do_type = do_type or info[3] == read_type
        do  = do and do_type

        # if they match, analyse it.
        if do:
            dirU = info[1][0] < info[1][1]

            # Add all beta peaks
            if len(peak_type) == 1:
                for serie in beta:
                    freqs, ampls = serie
                    for ind in range(len(freqs)):
                        if dirU:
                            freqU.append(serie[0][ind])
                            amplU.append(serie[1][ind])
                            tempU1.append(info[2][0])
                            tempU2.append(info[2][1])
                        else:
                            freqD.append(serie[0][ind])
                            amplD.append(serie[1][ind])
                            tempD1.append(info[2][0])
                            tempD2.append(info[2][1])
                            
            # Add all alpha peaks '1a1'
            elif len(peak_type) == 3:
                exists = len(alpha) >= int(peak_type[2])
                exists = exists and len(alpha[int(peak_type[2])-1][0]) >= int(peak_type[0])

                if exists and dirU:
                    freqU.append(alpha[int(peak_type[2])-1][0][int(peak_type[0])-1])
                    amplU.append(alpha[int(peak_type[2])-1][1][int(peak_type[0])-1])
                    tempU1.append(info[2][0])
                    tempU2.append(info[2][1])

                elif exists:
                    freqD.append(alpha[int(peak_type[2])-1][0][int(peak_type[0])-1])
                    amplD.append(alpha[int(peak_type[2])-1][1][int(peak_type[0])-1])
                    tempD1.append(info[2][0])
                    tempD2.append(info[2][1])

    down = [freqD, amplD, tempD1, tempD2]
    up   = [freqU, amplU, tempU1, tempU2]
    
    return up, down

def mass_fit (temp, mass, constant, H):

    temp = temp / 1000.             #mK
    mass = mass * 9.10938356e-31    #e- mass
    k = 1.38064852e-23              #J/K
    e = 1.6021766208e-19            #C
    hbar = 1.054571800e-34          #Js
    c = 3e8                         #m/s
    beta = e*hbar / ( mass*c )
    p = 1

    X = 2* np.pi**2 *p*k*temp*mass / ( e * hbar * H ) 
   
    if X.__class__ == list or X.__class__ == np.ndarray:
        res = []

        for i in X:
            if i > 50:
                res.append(5e100*A)
            else:
                res.append(constant * i / np.sinh (i))
        
        return np.array(res)

    if X > 50:
        return 5e100

    return constant * X / np.sinh (X)

def fit (temp, ampl, H, p):

    # postcondition
    # Return the mass and fitconstant
    # Return -1 for the mass if failure.

    # case1: too few data to fit.
    if len(temp) < 3:
        return [-1, 0], [0,0]

    # case2: enough data to fit. Fitting in p=1, then converting to actual harmonic.
    sol, Dsol = opt.curve_fit(lambda x, m, C: mass_fit(x, m, C, H), temp, ampl, bounds = ([0.01, 0], [100, 50000]))

    m = [ sol[0]/p, np.sqrt(Dsol[0][0])/p ] 
    C = [ sol[1], np.sqrt(Dsol[1][1]) ]

    return m, C

def do_plot (up, down, peak_type, fieldavg):

    if peak_type == 'b':
        # Temp, amplitude
        plt.figure(1)
        plt.errorbar(up[0][2], up[0][1], xerr = up[0][3], color = 'b', ms = 12, fmt='o')
        plt.xlim(left=0)
        plt.ylim(bottom = 0)
        plt.title('Up | Beta frequencies as a function of temperature')
        plt.xlabel('Temp (mK)')
        plt.ylabel('Freq (T)')

        # Freq, ampl
        plt.figure(2)
        patch = [ mpatches.Patch(color='b', label='up') ]
        plt.plot(up[0][0], up[0][1], 'bo')
        plt.xlim(left=0)
        plt.ylim(bottom = 0)
        plt.title('Up | Stability of beta amplitudes as a function of frequency.')
        plt.xlabel('Freq (T)')
        plt.ylabel('FFT amplitude of magnetization')

        # Temp, amplitude
        plt.figure(3)
        plt.errorbar(down[0][2], down[0][0], xerr = down[0][3], color = 'b', ms = 12, fmt='o')
        plt.xlim(left=0)
        plt.ylim(bottom = 0)
        plt.title('Down | Beta frequencies as a function of temperature')
        plt.xlabel('Temp (mK)')
        plt.ylabel('Freq (T)')

        # Freq, ampl
        plt.figure(4)
        patch.append( mpatches.Patch(color='r', label='down') )
        plt.plot(down[0][0], down[0][1], 'ro')
        plt.xlim(left=0)
        plt.ylim(bottom = 0)
        plt.title('Down | Stability of beta amplitudes as a function of frequency.')
        plt.xlabel('Freq (T)')
        plt.ylabel('FFT amplitude of magnetization')
        
    else:
        # up temp, amplitude fit plots.
        cols = ['y', 'r', 'c']
        patch = []
        for ind in range(len(up)):
            plt.figure(1)
            plt.errorbar(up[ind][2], up[ind][1], xerr = up[ind][3], color = cols[ind%3], fmt = 'o')
            txt = peak_type[0:2] + str(ind+1)
            patch.append( mpatches.Patch(color=cols[ind%3], label=txt) )

            mass, constant = fit(up[ind][2], up[ind][1], fieldavg, int(peak_type[0]))
            if mass[0] != -1:
                print('NOT SAVED: mass ', mass[0], ' +- ', mass[1])
                Tpoints = np.linspace(0, 50, 10000)
                Apoints = mass_fit (Tpoints, mass[0], constant[0], fieldavg)
                plt.figure(1)
                plt.plot(Tpoints, Apoints, 'b-')
        
        plt.xlim(left=0)
        plt.ylim(bottom = 0)
        plt.title('Up | Alpha fits')
        plt.xlabel('Temp (mK)')
        plt.ylabel('Freq (T)')
        plt.legend( handles=patch )

        # up freq, ampl fit plots.
        patch = []
        for ind in range(len(up)):
            plt.figure(2)
            plt.plot(up[ind][0], up[ind][1], cols[ind%3] + 'o', ms = 12)
            txt = peak_type[0:2] + str(ind+1)
            patch.append( mpatches.Patch(color=cols[ind%3], label=txt) )
        
        plt.xlim(left=0)
        plt.ylim(bottom = 0)
        plt.title('Up | Alpha scatter')
        plt.xlabel('Freq (T)')
        plt.ylabel('FFT amplitude of magnetization')
        plt.legend( handles=patch )
                  
        # down temp, amplitude fit plots.
        patch = []
        for ind in range(len(down)):
            plt.figure(3)
            plt.errorbar(down[ind][2], down[ind][1], xerr = down[ind][3], color = cols[ind%3], fmt = 'o')
            txt = peak_type[0:2] + str(ind+1)
            patch.append( mpatches.Patch(color=cols[ind%3], label=txt) )

            mass, constant = fit(down[ind][2], down[ind][1], fieldavg, int(peak_type[0]))
            if mass[0] != -1:
                print('NOT SAVED: mass ', mass[0], ' +- ', mass[1])
                Tpoints = np.linspace(0, 50, 10000)
                Apoints = mass_fit (Tpoints, mass[0], constant[0], fieldavg)
                plt.figure(3)
                plt.plot(Tpoints, Apoints, 'b-')
        
        plt.xlim(left=0)
        plt.ylim(bottom = 0)
        plt.title('Down | Alpha fits')
        plt.xlabel('Temp (mK)')
        plt.ylabel('Freq (T)')
        plt.legend( handles=patch )

        # down freq, ampl fit plots.
        patch = []
        for ind in range(len(down)):
            plt.figure(4)
            plt.plot(down[ind][0], down[ind][1], cols[ind%3] + 'o', ms = 12)
            txt = peak_type[0:2] + str(ind+1)
            patch.append( mpatches.Patch(color=cols[ind%3], label=txt) )
        
        plt.xlim(left=0)
        plt.ylim(bottom = 0)
        plt.title('Down | Alpha scatter')
        plt.xlabel('Freq (T)')
        plt.ylabel('FFT amplitude of magnetization')
        plt.legend( handles=patch )

    plt.show()

    return

# main
def translate (command):
    #   precondition
    assert( assert_command (command) )
    #   postcondition
    # See if the command makes sense.

    base_types = set.standard_types()

    # [field, field, peakset]
    valid1 = general.can_type(command[1], float)
    valid1 = valid1 and general.can_type(command[2], float)
    valid1 = valid1 and float(command[1]) < float(command[2])
    valid1 = valid1 and is_peakset(command[3])
    valid1 = valid1 and len(command) == 4

    # [field, field, peakset, type]
    valid2 = general.can_type(command[1], float)
    valid2 = valid2 and general.can_type(command[2], float)
    valid1 = valid1 and float(command[1]) < float(command[2])
    valid2 = valid2 and is_peakset(command[3])
    valid2 = valid2 and len(command) == 5
    valid2 = valid2 and command[4] in set.standard_types()

    # [peakset, field, field]
    valid3 = general.can_type(command[2], float)
    valid3 = valid3 and general.can_type(command[3], float)
    valid3 = valid3 and float(command[2]) < float(command[3])
    valid3 = valid3 and is_peakset(command[1])
    valid3 = valid3 and len(command) == 4
   
    # [peakset, field, field, type]
    valid4 = general.can_type(command[2], float)
    valid4 = valid4 and general.can_type(command[3], float)
    valid4 = valid4 and float(command[2]) < float(command[3])
    valid4 = valid4 and is_peakset(command[1])
    valid4 = valid4 and len(command) == 5
    valid4 = valid4 and command[4] in set.standard_types()

    if valid1:
        return [float(command[1]), float(command[2])], 'check', command[3]
    if valid2:
        return [float(command[1]), float(command[2])], command[4], command[3]
    if valid3:
        return [float(command[2]), float(command[3])], 'check', command[1]
    if valid4:
        return [float(command[2]), float(command[3])], command[4], command[1]
            
    return [0, 0], 0, 0

def analyse (command):
    #   precondition
    assert( assert_command(command) )
    #   postcondition
    # beta: show (T, freq) and (freq, ampl).
    #   show the number of peaks vs total runs for each freq (uncertainty 300)
    # I alpha: show (T, f), (T, a) and (f, a)
    #   calculate the masses for each

    # interpret command
    field, read_type, peak_type = translate (command)
    if peak_type == 0:
        print('Could not interpret your peaks command.')
        return

    # collect peaks
    if peak_type == 'b' or len(peak_type) == 3:
        up, down = get_peaks(field, peak_type, read_type)
        up = [up]
        down = [down]
    else:
        up1, down1 = get_peaks(field, peak_type + '1', read_type)
        up2, down2 = get_peaks(field, peak_type + '2', read_type)
        up3, down3 = get_peaks(field, peak_type + '3', read_type)
        up = [up1, up2, up3]
        down = [down1, down2, down3]

    # Plotting & fitting
    do_plot (up, down, peak_type, 0.5*field[0] + 0.5*field[1])
    return
