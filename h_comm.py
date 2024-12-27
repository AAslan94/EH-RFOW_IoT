#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: alx
"""


import numpy as np
import owutils as ut
from design_handle import designs
from rf import *
from libow8 import *
import matplotlib.pyplot as plt
from mac_sim import *
from defaults import constants
from scipy.spatial.distance import pdist, squareform

def sim_optic(design):
    params_d = designs[design]  
    l = sensor_net(**params_d) 
    l.calch()
    l.light_sim()
    params_d['r_master'] = designs[design + '_solar']['r_master']
    params_d['PT_master'] = designs[design + '_solar']['PT_master']
    x = sensor_net(**params_d) 
    x.calch()
    x.light_sim()
    x.calc_noise()
    x.calc_rq() 
   # calculate shot noise from LEDs used for lighting
    n_led = (np.sum(x.i_sm_tot,axis = 0) - np.sum(l.i_sm_tot,axis = 0)) * constants.qe * l.B_master[0] * 2
    l.calc_noise(n_led)
    params_d['no_bounces'] = 4
    l.calc_rq() 
    return l
    


class Hybrid_WSN:
    def __init__(self,design = 'e'):
        loaded_data = np.load("time_data.npz") #loaded mac data , for not running algo again
        bo_time= loaded_data['bo_time']
        cca = loaded_data['cca_time']
        cpu_on = loaded_data['cpu_on_time']
        ack_all = loaded_data['ack_all_time']
        tx_all = loaded_data['tx_all']
        self.l = sim_optic(design)
        self.N = self.l.r_sensor.shape[0]
        self.Rb_downlink = self.l.Rb_master
        self.Rb_uplink = self.l.Rb_sensor
        self.L_downlink = self.l.bits_master
        self.L_uplink = self.l.bits_sensor
        self.t_downlink = self.L_downlink/self.Rb_downlink
        self.t_uplink = self.L_uplink/self.Rb_uplink
        self.r_sensor = self.l.r_sensor
        self.r_master = self.l.r_master
        self.ber_downlink = ut.Qfunction(self.l.g_s_tot)
        self.sensitivity = self.l.sensitivity
        self.Tperiod = self.l.Tcycle
        #self.d = np.sqrt(np.sum((self.r_sensor - self.r_master)**2,axis=1))
        self.d = self.calc_max_dist()
        self.sensitivity = calc_new_sensitivity(self.sensitivity,self.L_uplink[0]/8,0.01) #calculate sensitivity for given packet size (in bytes) and target PER
        self.TX_min = calc_TX_power(self.d,self.sensitivity,'') #min rf tx required power
        self.TX,self.Itx = min_tx_power_level(self.TX_min)
        #self.t_backoff,self.t_cca,self.t_act,self.t_ack,self.t_tx = self.calc_time_mac(self.N,bytes_to_slots(self.L_uplink[0]/8),self.Tperiod,2000)
        self.t_backoff,self.t_cca,self.t_act,self.t_ack,self.t_tx = bo_time,cca,cpu_on,ack_all,tx_all
        self.Iact = self.l.Iact
        self.IWU = self.l.IWU
        self.tWU = self.l.tWU
        self.Iadc = self.l.Iadc
        self.Vmcu = self.l.Vmcu
        self.Vsensor = self.l.Vsensor
        self.Isensor = self.l.Isensor
        self.Itia = self.l.Itia
        self.Icca = self.l.Icca
        self.ISL = self.l.ISL
        self.I = None #to plot power cycle
        self.T = None #to plot power cycle
        self.energy_cycle  = self.calc_period_energy()
        self.energy_day = self.energy_cycle* 24*60*60/self.Tperiod
        self.energy_cycle_nomac = self.calc_period_energy_no_mac()
        self.energy_day_nomac = self.energy_cycle_nomac* 24*60*60/self.Tperiod
        self.show_power_cycle()
        self.vlc_snr_los = self.l.snr_s_los_dB.flatten()
        self.vlc_snr_total = self.l.snr_s_tot_dB.flatten()
        self.vlc_snr_diffuse = self.l.snr_s_diff_dB.flatten()
        self.sensor_pos = self.l.r_sensor
        
    def calc_max_dist(self):
        a = self.r_master
        b = self.r_sensor
        h = np.vstack((a,b))
        dist = pdist(h, metric='euclidean')
        dist_matrix = squareform(dist)
        r = np.delete(dist_matrix,[0],axis=0)
        return np.max(r,axis = 1)
    
    def calc_times_mac(self, it = 5000):
            bits_per_symbol = 4
            L = (bytes_to_slots(self.L_uplink/8))
            print(f'L is {L[0]}')
            [thr,col,tx,bo,cca] = sim_avg(n = self.N, packet = int(L[0]), it = it)
            t_symbol = (1/self.Rb_uplink) * bits_per_symbol
            print(f't_symbol is {t_symbol}')
            t_slot = 20 * t_symbol
            print(f'{t_slot} is tslot')
            bo_time = bo * t_slot
            print(f'{bo_time} is bo')
            cca_time = cca* t_slot * (6/20) #cca duration (6 symbols) - (14 symbols cpu on)
            print(f'{cca_time} is ccatime')
            cpu_on_time = cca * t_slot * (14/20) + bo_time + (col/self.N)* t_slot*(12/20) + (tx/self.N)*t_slot*(12/20) #backoff periods + turnaround_time (for succesfull and unsuccessful)
            print(f'{cpu_on_time} is cpu_on')
            wack_time = (col/self.N)*54*t_symbol #due to collisions
            print(f'{wack_time} is twack')
            ack_time = (tx/self.N)*(8*t_symbol + 10*t_symbol)  #successful 10t-symbol average delay
            print(f'{ack_time} is acktime')
            ack_all_time =  wack_time + ack_time
            print(f'{ack_all_time} is ackalltime')
            tx_all = (col/self.N) * t_slot * L + (tx/self.N)*t_slot*L
            print(f'{tx_all} is tx_all')
            np.savez("time_data.npz", bo_time=bo_time, cca_time=cca_time, cpu_on_time=cpu_on_time, ack_all_time=ack_all_time, tx_all=tx_all)
            return [bo_time,cca_time,cpu_on_time,ack_all_time,tx_all]

    def calc_period_energy(self):
        Vsn = self.Vsensor
        Vmcu = self.Vmcu
        t = 0
        p = np.array(self.IWU[0] * self.tWU[0] * Vmcu)
        t += self.tWU[0] 
        No_sensors = np.shape(self.Isensor)[0]
        samples = No_sensors*4 #for averaging
        sampling_Rate = 200*1e3
        Tsam = samples/sampling_Rate
        Isam= (self.Iadc) + self.Iact
        t += Tsam
        self.T = np.append(self.T,t)
        Isn = np.sum(self.Isensor)
        ps = Isam * Tsam * Vmcu + Isn * Tsam * Vsn
        p = np.append(p,ps)
        CPU_cycles = 5000 #assume
        CPU_f = 48*1e6
        Tproc = CPU_cycles/CPU_f
        Iproc =  self.Iact
        ps = Tproc * Iproc * Vmcu
        p = np.append(p,ps)
        t += Tproc
        Tact = self.t_act[0]
        Iact = self.Iact
        ps = Tact * Iact * Vmcu
        p = np.append(p,ps)
        t += Tact
        Tcca = self.t_cca[0]
        Icca = self.Icca
        ps = Tcca* Icca * Vmcu
        p = np.append(p,ps)
        t += Tcca
        Itx = 1 #later
        Ttx = self.t_tx[0]
        ps = Itx * Ttx * Vmcu
        p = np.append(p,ps)
        t += Ttx 
        self.I = np.append(self.I, Iact)
        self.T = np.append(self.T,t)
        Tack = self.t_ack[0]
        Iack = self.Iadc + self.Iact + self.Itia
        #Iack = Icca
        ps = Tack * Iack * Vmcu
        p = np.append(p,ps)
        t += Tack
        Tsleep = self.Tperiod[0] - t
        Isleep = self.ISL[0]
        ps = Tsleep * Isleep * Vmcu
        p = np.append(p,ps)
        p_f = np.tile(p,(self.N,1))
        p_f[:,5] *= self.Itx*1e-3
        return np.sum(p_f,axis = 1)
       

    def calc_period_energy_no_mac(self):
        Vsn = self.Vsensor
        Vmcu = self.Vmcu
        t = 0
        p = np.array(self.IWU[0] * self.tWU[0] * Vmcu)
        t += self.tWU[0] 
        No_sensors = np.shape(self.Isensor)[0]
        samples = No_sensors*4 #for averaging
        sampling_Rate = 200*1e3
        Tsam = samples/sampling_Rate
        Isam= (self.Iadc) + self.Iact
        t += Tsam
        Isn = np.sum(self.Isensor)
        ps = Isam * Tsam * Vmcu + Isn * Tsam * Vsn
        p = np.append(p,ps)
        CPU_cycles = 5000 #assume
        CPU_f = 48*1e6
        Tproc = CPU_cycles/CPU_f
        Iproc =  self.Iact
        ps = Tproc * Iproc * Vmcu
        p = np.append(p,ps)
        t += Tproc
        Tcca = (4/self.Rb_uplink[0]) * 6 #6*Tsymbol
        Icca = self.Icca
        ps = Tcca* Icca * Vmcu
        p = np.append(p,ps)
        t += Tcca
        Itx = 1 #later
        Ttx = self.l.bits_sensor[0]/self.Rb_uplink[0]
        ps = Itx * Ttx * Vmcu
        p = np.append(p,ps)
        Tack = self.l.bits_master[0]/self.Rb_downlink[0]
        Iack = self.Iadc + self.Iact + self.Itia
        ps = Tack * Iack * Vmcu
        p = np.append(p,ps)
        t += Tack
        Tsleep = self.Tperiod[0] - t
        Isleep = self.ISL[0]
        ps = Tsleep * Isleep * Vmcu
        p = np.append(p,ps)
        p_f = np.tile(p,(self.N,1))
        #print(f'p_f is {p_f[0]}')
        p_f[:,4] *= self.Itx*1e-3
        return np.sum(p_f,axis = 1)
 
    def show_power_cycle(self):
        #this is for illustration - plotting
        t1 = 1e-3
        self.I = np.array(self.ISL[0])
        self.T = np.array(1e-3)
        t1 += self.tWU[0]
        self.I = np.append(self.I, self.IWU[0])
        self.T = np.append(self.T,t1)
        t1 +=1e-3
        self.I = np.append(self.I, self.Iact)
        self.T = np.append(self.T,t1)
        No_sensors = np.shape(self.Isensor)[0]
        samples = No_sensors*4 #for averaging
        sampling_Rate = 200*1e3       
        Tsam = samples/sampling_Rate
        Isam= (self.Iadc) + self.Iact
        t1 +=Tsam
        self.I = np.append(self.I, Isam)
        self.T = np.append(self.T,t1)
        CPU_cycles = 5000 #assume
        CPU_f = 48*1e6
        Tproc = CPU_cycles/CPU_f
        t1 += Tproc
        self.I = np.append(self.I, self.Iact)
        self.T = np.append(self.T,t1)
        Tcca = (4/self.Rb_uplink[0]) * 6 #6*Tsymbol
        t1 += Tcca
        self.I = np.append(self.I, self.Icca)
        self.T = np.append(self.T,t1)
        t1 += 0.4e-3
        self.I = np.append(self.I, self.Iact)
        self.T = np.append(self.T,t1)
        Ttx = self.l.bits_sensor[0]/self.Rb_uplink[0]
        t1 += Ttx
        self.I = np.append(self.I, self.Itx[0]*1e-3)
        self.T = np.append(self.T,t1)
        t1 += 0.5e-3
        self.I = np.append(self.I, self.Iact)
        self.T = np.append(self.T,t1)
        Tack = self.l.bits_master[0]/self.Rb_downlink[0]
        Iack = self.Iadc + self.Iact + self.Itia
        t1 += Tack
        self.I = np.append(self.I, Iack)
        self.T = np.append(self.T,t1)
        t1 += 0.2e-3
        self.I = np.append(self.I, self.Iact)
        self.T = np.append(self.T,t1)
        t1 += 1e-3
        self.I = np.append(self.I, self.ISL[0])
        self.T = np.append(self.T,t1)
        
        
        
        
