#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modified part of pyowiot
@author: alx
"""

import numpy as np
from defaults import *
from create_points import *
import owutils as ut

diag = diagonal_points(0,10,0,10,0)
arr = gen_points(1,9,1,9,3,5,5,False) 
arr2 = gen_points(2,12,2,12,3,5,5,False) 
arr3 = gen_points(0.3,9.7,0.3,9.7,0,7,7,False)
#opt solar orientation vector
op = np.load('op_l_sun.npy')
nor = ut.spher_to_cart_ar(1, op[:,0], op[:,1]).T
op = np.load('op_l_nsun.npy')
nor_n = ut.spher_to_cart_ar(1, op[:,0], op[:,1]).T

design = {
    'test':{
        #define room dimensions
        'room_L' : 10,
        'room_W' : 10,
        'room_H' : 3,
        #define wall reflectivities 
        'refl_north' : 0.6,
        'refl_south' : 0.6,
        'refl_east' : 0.6,
        'refl_west' : 0.6,
        'refl_ceiling' : 0.6,
        'refl_floor' : 0.3,
        #ambient sources - window variables
        'amb_L1': 2,
        'amb_L2': 2,
        #communication variables
        #sensor variables
        'r_sensor':arr3, #position of sensors
        'FOV_sensor': np.pi/2.0, #Field of View - Photodiode  
        'nR_sensor': constants.ez, #Orientation (normal vector) of Photodiode - default (0,0,1)
        'A_pd': 1e-4, #Active area of the photodiode [m^2]
        #master node variables
        'r_master': np.array([5,5,3]), # Position of the VLC transmitter
        'm_master_vlc':1, #Lambertian order of the VLC transmitter
        'nS_master_vlc': -constants.ez, #Orientation (normal vector) of the VLC transmitter - default (0,0,-1)
        'PT_master': 6, #optical power of the VLC transmitter in Watt
        'sensitivity': -99, #sensitivity of RF master receiver
        #bitrate & packet length
        'Rb_master': 250e3, #VLC Downlink bit-rate
        'Rb_sensor': 250e3, #RF effective bit-rate
        'bits_master':88, # ack packet length in bits
        'bits_sensor': 8*20, #uplink packet length in bits
        #other
        'no_bounces':4 , #bounces to be considered in the diffuse algorithm 
        #SN power consumption variables
        'IWU': 1.7e-3 , #wake up current
        'tWU': 165e-6, #wake up time
        'Iadc': 0.7e-3, #ADC peripheral current consumption
        'Iact': 2.73e-3, #CPU current consumption
        'Vmcu': 3, #MCU operating voltage
        'Vsensor': 5, #Sensors operating voltage
        'Isensor' : np.array([0.2e-3,0.16,0.5e-3]), #Sensors current consumption
        'Itia':0.7e-3, #Transimpendance amplifier quiscent current 
        'Icca':6.4e-3, #Current consumption when node performs CCA
        'Tcycle':1, #duty cycle in seconds
        #Lighting variables
        'm_leds': 1, #Lambertian order of the lighting LEDs
        'r_leds': arr, #position of the lighting LEDs
        'PT_leds': 6, #Optical transmitted power from the lighting leds
        #Solar panel variables
        'nR_solar': nor,
        'nS_leds': -constants.ez, #orientation (normal vector) of the lighting leds         
        'A_solar': 5.2 * 5.2 * 1e-4, #Active area of the solar cell [m^2]    
        'Isc':0.165, #Short-circuit current of PV panel in Amperes
        'Voc': 2.79, #Open-circuit voltage of PV panel in Volts
        'Imp': 0.14, #Maximum point current of PV panel in Amperes
        'Vmp': 2.24, #Maximum point voltage of PV panel in Volts
        'N': 4, #Number of PV cells connected in series
        'Pmax': 0.14*2.24,
        'A': 1 #first approximation of ideality factor
        
        }
    }

