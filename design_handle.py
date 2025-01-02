#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modified part of pyowiot
@author: alx
"""

import numpy as np
from design import design
d = design['test']

designs = {
     'e' :  {
       'room_L' : d['room_L'],
       'room_W' : d['room_W'],
       'room_H' : d['room_H'],
       'refl_north' : d['refl_north'],
       'refl_south' : d['refl_south'],
       'refl_east' : d['refl_east'],
       'refl_west' : d['refl_west'],
       'refl_ceiling' : d['refl_ceiling'],
       'refl_floor' : d['refl_floor'],
       'm_sensor' : 1, #doesn't matter
       'r_sensor': d['r_sensor'],
       'm_master' : d['m_master_vlc'],
       'r_master' : d['r_master'],
       'FOV_master' : np.pi /2.0, #doesn't matter
       'FOV_sensor' : d['FOV_sensor'], 
       'amb_L1' : d['amb_L1'],
       'amb_L2' : d['amb_L2'],
       'nR_sensor' : d['nR_sensor'],
       'nS_sensor' : np.array([0,0,0]), #doesn't matter
       'nR_master' : np.array([0,0,0]), #doesn't matter
       'nS_master' : d["nS_master_vlc"],
       'no_bounces' : d['no_bounces'],
       'Rb_master' : d['Rb_master'],
       'Rb_sensor' : d['Rb_sensor'],  
       'PT_sensor' : 5e-3, #doesn't matter
       'PT_master' : d['PT_master'],
       'A_master' : 1e-4, #doesn't matter
       'A_sensor' : d['A_pd'],
       "SOLAR": False,
       'bits_master':d['bits_master'],
       'bits_sensor': d['bits_sensor'], #13  + 7(data),
       'sensitivity':d['sensitivity'],
       'IWU': d['IWU'] ,
       'tWU': d['tWU'],
       'Iadc': d['Iadc'],
       'Iact': d['Iact'],
       'Vmcu': d['Vmcu'],
       'Vsensor': d['Vsensor'],
       'Isensor' : d['Isensor'],
       'Itia':d['Itia'],
       'Icca':d['Icca'],
       'Tcycle':d['Tcycle']       
       },
  'e_solar' :  {
    'room_L' : d['room_L'],
    'room_W' : d['room_W'],
    'room_H' : d['room_H'],
    'refl_north' : d['refl_north'],
    'refl_south' : d['refl_south'],
    'refl_east' : d['refl_east'],
    'refl_west' : d['refl_west'],
    'refl_ceiling' : d['refl_ceiling'],
    'refl_floor' : d['refl_floor'],
    'm_sensor' : 1, #doesn't matter
    'r_sensor': d['r_sensor'],
    'm_master' :d['m_leds'] ,
    'r_master' : d['r_leds'],#positions of lamps
    'FOV_master' : np.pi/2.0, #doesn't matter
    'FOV_sensor' : np.pi,
    'amb_L1' : d['amb_L1'],
    'amb_L2' : d['amb_L2'],
    'nR_sensor' : d['nR_solar'],
    'nS_sensor' :np.array([0,0,0]),
    'nR_master' : np.array([0,0,0]), #doesn't matter
    'nS_master' : d['nS_leds'],
    'no_bounces' : d['no_bounces'],
    'Rb_master' : 250e3, #irrelevant
    'Rb_sensor' : 10e3,  #irrelevant
    'PT_sensor' : 25e-3, #irrelevant
    'PT_master' : d['PT_leds'], 
    'A_master' : 1e-4, #irrelevant
    'A_sensor' : d['A_solar'],
    'Vcharge': d['Vcharge'],
     "SOLAR": True
      }     
}
  
