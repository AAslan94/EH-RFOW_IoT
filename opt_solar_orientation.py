#!/usr/bin/env python
# coding: utf-8

import numpy as np
from libow8 import sensor_net
import matplotlib.pyplot as plt
import owutils as ut
from design_handle import designs
from pyswarms.single.global_best import GlobalBestPSO


KEY = 'e_solar'
params_d = designs[KEY] 



h_ww = None
r_sens = None
n_particles = 20
def sensor_ar(x,params_d = None): 
    global h_ww
    global r_sens
    global n_particles
    r_sensor = np.tile(r_sens,(n_particles,1)) 
    nR =ut.spher_to_cart_ar(1, x[:,0], x[:,1]).T
    params_d['r_sensor'] = r_sensor
    params_d['nR_sensor'] = nR
    #params_d['nS_sensor'] = nR
    l = sensor_net( **params_d ) 
    l.calch(h_ww = h_ww)
    l.light_sim()
    h_ww = l.h_ww
    fitness = np.sum(np.sum(l.Pin_sm_diff,axis = 0),axis = 1) + np.sum(l.Pin_sm,axis = 0) + l.Pin_sa #LOS + Diffuse + Ambient
    return fitness 



def fit_function(x):
    f = sensor_ar(x,params_d=params_d)
    g = 1/f
    g = np.array(g)
    g = g.reshape(x.shape[0])
    print(g)
    return g



r_sen = designs[KEY]['r_sensor'] 
N = r_sen.shape[0]
pos_l = [0]*N #SN Position
pow_l = [0]*N #SN Optical Power
op_l = [0]*N #SN Orientation
options = {'c1': 0.5, 'c2': 0.3, 'w': 0.8}
lb = np.array([0, 0])
ub = np.array([np.pi/2,2*np.pi])
for i in range(0,N):
    r_sens = r_sen[i]
    optimizer = GlobalBestPSO(n_particles=n_particles, dimensions=2, options=options, bounds=(lb, ub))
    best_cost, best_pos = optimizer.optimize(fit_function, iters=20) 
    pos_l[i] = r_sens
    pow_l[i] = 1/best_cost
    op_l[i] = best_pos

np.save('op_l_suno.npy', op_l)



