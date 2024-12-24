#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modified part of pyowiot
@author: alx
"""

import numpy as np
from scipy.special import erfc
import matplotlib.pyplot as plt
from scipy.optimize import brentq

def thermal_noise(bandwidth_hz=2e6, temperature_kelvin=290):
    # Boltzmann constant in J/K
    k = 1.38e-23
    # Calculate noise power in watts
    noise_power_watts = k * temperature_kelvin * bandwidth_hz
    # Convert noise power to dBm
    noise_power_dbm = 10 * np.log10(noise_power_watts / 1e-3)
    return noise_power_dbm

#def min_tx_power_level(power_levels_array):
#    print(f'power_level_arrays is {power_levels_array}')
    #list of power levels and their current consumption
#    power_levels = np.array([-20, -18, -15, -12, -10, -9, -6, -5, -3, 0, 1, 2, 3, 4, 5])  # dBm
#    current_consumption = np.array([ 4.0 , 4.48 , 5.2 ,  5.92 , 6.4  , 6.64 , 7.36 , 7.6 ,  8.08 , 8.8 ,  9.04 , 9.28, 9.52 , 9.76, 10.0  ])  # mA

#    next_power_levels = np.empty_like(power_levels_array, dtype=int)
#    consumption_levels = np.empty_like(power_levels_array)
#    print('Correct-o Mundo')

    # Iterate through each node's power level in the input array
#    for idx, tx_power in enumerate(power_levels_array):
        # Find the index of the first power level that's bigger than the current one
#        for i in range(len(power_levels)):
#            if power_levels[i] >= tx_power:
#                next_power_levels[idx] = power_levels[i]
#                consumption_levels[idx] = current_consumption[i]
#               break
 #       else:
            # If no bigger power level is found, return None equivalents
 #           next_power_levels[idx] = np.nan
 #           consumption_levels[idx] = np.nan
 #   print(consumption_levels)
 #   return next_power_levels, consumption_levels

#def min_tx_power_level(power_levels_array):
#    print(f'power_level_arrays is {power_levels_array}')
    #list of power levels and their current consumption
#    power_levels = np.array([-20, -19, -18, -17,-16,-15,-14,-13, -12, -11,-10, -9,-8, -7,-6, -5,-4, -3,-2,-1, 0, 1, 2, 3, 4, 5])  # dBm
#    current_consumption = np.array([ 4,    4.24 , 4.48,  4.72,  4.96 , 5.2 ,  5.44,  5.68 , 5.92 , 6.16,  6.4 ,  6.64,  6.88 , 7.12,  7.36,  7.6,   7.84 , 8.08  ,8.32 , 8.56 , 8.8 ,  9.04 , 9.28 , 9.52,  9.76 ,10.  ])  # mA

#    next_power_levels = np.empty_like(power_levels_array, dtype=int)
#    consumption_levels = np.empty_like(power_levels_array)
#    print('Correct-o Mundo')

    # Iterate through each node's power level in the input array
#    for idx, tx_power in enumerate(power_levels_array):
        # Find the index of the first power level that's bigger than the current one
#        for i in range(len(power_levels)):
#            if power_levels[i] >= tx_power:
#                next_power_levels[idx] = power_levels[i]
                #consumption_levels[idx] = current_consumption[i]
#                break
#        else:
            # If no bigger power level is found, return None equivalents
#            next_power_levels[idx] = np.nan
#            consumption_levels[idx] = np.nan
#    print(consumption_levels)
#    return next_power_levels, consumption_levels

def min_tx_power_level(power):
    return power,0.24* power + 8.8

#ITU-R P.1238-12 - site general - 2.45GHz - Office
def PL(d, mode = 'ITU_R'):
    if mode == 'ITU_R':
        print("calc with itu_r")
        return 10*1.46*np.log10(d) + 34.62 + 10*2.03*np.log10(2.45) #+ np.random.normal(0,3.76)
    elif mode == 'NIST':#NIST PAP02-Task 6 Model - office
        d0 = 1
        d1 = 10
        pl0 = 26.8
        n0 = 4.2
        d1 = 10
        n1 = 8.7
        ind1 = np.where(d<=d1)
        ind2 = np.where(d>d1)
        pl = np.zeros(d.shape)
        pl[ind1] = pl0 + 10 * n0 * np.log10(d[ind1]/d0)
        pl[ind2] = pl0 + 10 * n0 * np.log10(d[ind2]/d0) + 10 * n1 * np.log10(d[ind2]/d1)
        return pl
    else:
        #return 40*np.log10(d) + 55 + 2*4 #default path loss model
         return 26*np.log10(d/2) + 50.7 + 2*5.8  
 
def calc_TX_power(d,sensitivity,pl_model = ''):
  path_loss = PL(d, pl_model)
  #the received power must be greater than the sensitivity
  return sensitivity + path_loss

def Packet_length_z(data):
  length = 13 + data #bytes
  return length

def Packet_length_time(length,bitrate): #length in bytes
  return length*8/bitrate
  
def bytes_to_slots(b):
    sym = b * 2
    return sym/20


def calculate_ber_oqpsk(eb_no_db):
    """
    Calculate BER for OQPSK using coherent detection.
    """
    # Convert Eb/No from dB to linear scale
    eb_no_linear = 10 ** (eb_no_db / 10)

    # Calculate BER using the Q-function approximation
    ber = 0.5 * erfc(np.sqrt(eb_no_linear))

    return ber

def calculate_min_eb_no(ber_target):
   
    # Define the BER equation
    def ber_oqpsk(eb_no_linear):
        return 0.5 * erfc(np.sqrt(eb_no_linear)) - ber_target

    # Solve for Eb/No in linear scale
    eb_no_linear_min = brentq(ber_oqpsk, 1e-10, 100) 

    # Convert to dB
    eb_no_db_min = 10 * np.log10(eb_no_linear_min)
    return eb_no_db_min

#based on https://ieeexplore.ieee.org/document/4511247
#a function to approximate the sensitivity of the receiver for non-default packet size (Bytes) and Packet Error Rate (0-1)

def calc_new_sensitivity(sens,packet,per):
  C = 2 #dB - coding gain
  P = 9 #dB - processing gain
  snr_m = 8.43 - 2 - 9 #dB - minimum needed SNR for default packet , per
  ser = per/(packet*2) #target symbol error rate
  ber = ser/2 #target bit error rate
  #print(ber)
  eb_no = calculate_min_eb_no(ber) #target Eb/No in dB
  snr_n = eb_no - C - P #required SNR 
  #print(eb_no)
  return sens - snr_m + snr_n



