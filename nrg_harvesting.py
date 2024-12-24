#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: alx
"""
import numpy as np
from libow8 import *
import owutils as ut
from design_handle import designs
from solar_panel_model import SolarPanel
from h_comm import *
import pickle
import matplotlib.pyplot as plt
from defaults import constants
from design import design
d = design['test']

def sim_light_solar(design,sp_params,opt_orientation):
    design = design + "_solar"
    params_d = designs[design] 
    params_d['nR_sensor'] = opt_orientation
    params_d['A_sensor'] =  sp_params['Area']
    params_d['no_bounces'] = 4
    l = sensor_net(**params_d) 
    l.calch()
    l.light_sim()
    return l



panel = {
    "Isc": d['Isc'],
    "Voc": d['Voc'],
    "Imp": d['Imp'],
    "Vmp": d['Vmp'],
    "N": d['N'],
    "Pmax": d['Pmax'],
    "A": d['A'],
    "Area":d['A_solar'],
    "G": 1000
}


class EH():
    def __init__(self,design = 'e',sp_params = panel,opt_orientation= d['nR_solar']):
        self.s = sp_params
        self.l = sim_light_solar(design,self.s,opt_orientation)
        self.p_all = np.sum(np.sum(self.l.Pin_sm_diff,axis = 0),axis = 1) + np.sum(self.l.Pin_sm,axis = 0) + self.l.Pin_sa #LOS + Diffuse + Ambient
        self.p_no_sun = np.sum(np.sum(self.l.Pin_sm_diff,axis = 0),axis = 1) + np.sum(self.l.Pin_sm,axis = 0)
        self.p_los = np.sum(self.l.Pin_sm,axis = 0)
        self.p_diff = np.sum(np.sum(self.l.Pin_sm_diff,axis = 0),axis = 1)
        self.p_amb = self.l.Pin_sa
        self.ratio_los = self.p_los/(self.p_los + self.p_diff)
        self.ratio_diff = self.p_diff/(self.p_los + self.p_diff)
        self.irr_all = self.p_all/self.l.A_sensor
        self.irr_no_sun = self.p_no_sun/self.l.A_sensor
        self.eff_sun = None #efficiency in sunny conditions 
        self.eff_no_sun = None #efficiency with no sun
        self.p_out_sun = None #power out of the solar panel
        self.p_out_no_sun = None
        self.i_mpp_sun = None  
        self.i_mpp_no_sun = None
        self.v_mpp_sun = None
        self.v_mpp_no_sun = None
        self.i_sc_sun = None
        self.i_sc_no_sun = None
        self.i_voc_sun = None
        self.i_voc_no_sun = None
        self.pext_sun = None #power out of buck-boost converter
        self.pext_no_sun = None 
        self.pext_sun_cm = None #power out of buck-boost converter per sq.cm
        self.pext_no_sun_cm = None 
        self.calc_params_sun() #extract params for cells in every position
        self.calc_params_no_sun()
        self.buck_boost_eff() #efficiency of buck-boost (spv1050)
        self.Vbatt = 4.2 #charging voltage of battery
        self.iext_sun = self.pext_sun/self.Vbatt 
        self.iext_no_sun = self.pext_no_sun/self.Vbatt
        self.cap_current() #charging circuit cannot provide more that 70mA
        self.esun_h = self.iext_sun * 60 * 60 * self.Vbatt
        self.ensun_h = self.iext_no_sun * 60 * 60 * self.Vbatt
        #self.plot_on()
        #self.plot_power()
        
        
    def calc_params_sun(self):
        self.eff_sun = np.zeros(self.p_all.shape[0])
        self.p_out_sun = np.zeros(self.p_all.shape[0])
        self.i_mpp_sun = np.zeros(self.p_all.shape[0])
        self.v_mpp_sun = np.zeros(self.p_all.shape[0])
        self.i_sc_sun =  np.zeros(self.p_all.shape[0])
        self.i_voc_sun = np.zeros(self.p_all.shape[0])
        for i in range(0 , self.p_all.shape[0]):
             D = SolarPanel(Isc =self.s['Isc'], Voc = self.s['Voc'], Imp = self.s['Imp'], Vmp = self.s['Vmp'], N = self.s['N'], G = self.irr_all[i], area= self.s['Area'])
             D.get_solar_parameters(True)
             D.iv_curve()
             D.calc_efficiency()
             self.eff_sun[i] = round(D.efficiency,3)
             self.p_out_sun[i] = D.Pmax_irr
             self.i_mpp_sun[i] = D.Imp
             self.v_mpp_sun[i] = D.Vmp
             self.i_sc_sun[i] = D.Isc
             self.i_voc_sun[i] = D.Voc
    def cap_current(self):
        j = np.where(self.iext_sun > 70e-3)
        self.iext_sun[j] = 70e-3
        j = np.where(self.iext_no_sun > 70e-3)
        self.iext_no_sun[j] = 70e-3 
        self.pext_sun = self.iext_sun * self.Vbatt
        self.pext_no_sun = self.iext_no_sun * self.Vbatt
             
    def calc_params_no_sun(self):
        self.eff_no_sun = np.zeros(self.p_all.shape[0])
        self.p_out_no_sun = np.zeros(self.p_all.shape[0])
        self.i_mpp_no_sun = np.zeros(self.p_all.shape[0])
        self.v_mpp_no_sun = np.zeros(self.p_all.shape[0])
        self.i_sc_no_sun =  np.zeros(self.p_all.shape[0])
        self.i_voc_no_sun = np.zeros(self.p_all.shape[0])
        for i in range(0 , self.p_all.shape[0]):
             D = SolarPanel(Isc =self.s['Isc'], Voc = self.s['Voc'], Imp = self.s['Imp'], Vmp = self.s['Vmp'], N = self.s['N'], G = self.irr_no_sun[i], area= self.s['Area'])
             D.get_solar_parameters(True)
             D.iv_curve()
             D.calc_efficiency()
             self.eff_no_sun[i] = round(D.efficiency,3) 
             self.p_out_no_sun[i] = D.Pmax_irr
             self.i_mpp_no_sun[i] = D.Imp
             self.v_mpp_no_sun[i] = D.Vmp
             self.i_sc_no_sun[i] = D.Isc
             self.i_voc_no_sun[i] = D.Voc
    
    
    def buck_boost_eff(self):
        self.pext_no_sun = np.zeros(self.i_mpp_no_sun.shape[0])
        self.pext_sun = np.zeros(self.i_mpp_no_sun.shape[0])
        self.pext_no_sun_cm = np.zeros(self.i_mpp_no_sun.shape[0])
        self.pext_sun_cm = np.zeros(self.i_mpp_no_sun.shape[0])
        for i in range (0, self.i_mpp_no_sun.shape[0]):
            if self.i_mpp_no_sun[i] > 1e-3:
                self.pext_no_sun[i] = self.p_out_no_sun[i] * 0.82
            elif self.i_mpp_no_sun[i] > 500e-6:
                self.pext_no_sun[i] = self.p_out_no_sun[i] * 0.81
            elif self.i_mpp_no_sun[i] > 250e-6:
                self.pext_no_sun[i] = self.p_out_no_sun[i] * 0.80
            else:
                self.pext_no_sun[i] = self.p_out_no_sun[i] * 0.77     
        for i in range (0, self.i_mpp_no_sun.shape[0]):
            if self.i_mpp_sun[i] > 1e-3:
                self.pext_sun[i] = self.p_out_sun[i] * 0.82
            elif self.i_mpp_no_sun[i] > 500e-6:
                self.pext_sun[i] = self.p_out_sun[i] * 0.81
            elif self.i_mpp_no_sun[i] > 250e-6:
                self.pext_sun[i] = self.p_out_sun[i] * 0.80
            else:
                self.pext_sun[i] = self.p_out_sun[i] * 0.77  
        self.pext_no_sun_cm = self.pext_no_sun/(self.s['Area']*1e4)
        self.pext_sun_cm = self.pext_sun/(self.s['Area']*1e4)
    def plot_on(self):
        attributes = [
            (self.eff_sun*100, "Efficiency with Sun", "Efficiency [%]"),
            (self.eff_no_sun*100, "Efficiency without Sun", "Efficiency [%]"),
            (self.p_out_sun*1000, "Power Output with Sun", "Power Output [mW]"),
            (self.p_out_no_sun*1000, "Power Output without Sun", "Power Output [mW]"),
            (self.i_mpp_sun*1000, "Current at MPP with Sun", "Current [mA]"),
            (self.i_mpp_no_sun*1000, "Current at MPP without Sun", "Current [mA]"),
            (self.v_mpp_sun, "Voltage at MPP with Sun", "Voltage [V]"),
            (self.v_mpp_no_sun, "Voltage at MPP without Sun", "Voltage [V]"),
            (self.i_sc_sun*1000, "Short-Circuit Current with Sun", "Current [mA]"),
            (self.i_sc_no_sun*1000, "Short-Circuit Current without Sun", "Current [mA]"),
            (self.i_voc_sun, "Open-Circuit Voltage with Sun", "Voltage [V]"),
            (self.i_voc_no_sun, "Open-Circuit Voltage without Sun", "Voltage [V]"),
            (self.iext_sun*1000, "Icharging with sun","Current [mA]"),
            (self.iext_no_sun*1000, "Icharging without sun","Current [mA]")
            ]

        fig, axs = plt.subplots(4, 4, figsize=(15, 12))
        fig.suptitle("Solar Panel Variables", fontsize=16)

        # Flattening the axes for easier indexing
        axs = axs.flatten()

        # Plot each attribute in a separate subplot
        for i, (attribute, label, value) in enumerate(attributes):
            axs[i].plot(self.l.r_sensor[:,0],attribute, marker='o', linestyle='-', color='b')
            axs[i].set_title(label)
            axs[i].set_xlabel("Meters")
            axs[i].set_ylabel(value)
            axs[i].grid(True)

        # Hide any unused subplots if there are less than 12
        for j in range(len(attributes), len(axs)):
            axs[j].axis("off")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to fit the title
        plt.show()

    def plot_power(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.l.r_sensor[:,0], 10*np.log10(self.p_los), marker='o',label='LOS')
        plt.plot(self.l.r_sensor[:,0], 10*np.log10(self.p_diff),marker='^', label='Diffuse')
        plt.plot(self.l.r_sensor[:,0], 10*np.log10(self.p_no_sun), marker='s',label='Total')
        plt.xlabel("Diagonal [m]")
        plt.ylabel("Incident Power to PV [dBm]")
        plt.title("Plot of LOS, Diffuse, and Total incident power to PVs in the diagonal with no solar power")
        plt.legend()
        plt.show()


def calculate_min_solar_panel_area(wsn,nrg,h1,h2,m):
    #first approximation
    #wsn: hybrid network object
    #nrg: solar power object
    #h1: mean sunlight duration/day (hours)
    #h2: mean lights duration/day (hours)
    #m: safety margin (e.g. =0.2 (20%))
    nrg_consumed_day = wsn.energy_day
    nrg_consumed_day_margin = (1+m) * nrg_consumed_day
    nrg_harv_t1 = nrg.esun_h * h1
    nrg_harv_t2 = nrg.ensun_h * h2
    nrg_harv = nrg_harv_t1 + nrg_harv_t2
    sp_area = nrg.l.A_sensor 
    factor = nrg_consumed_day_margin/nrg_harv
    return sp_area * factor
    
    
def mAh_to_J(mAh,voltage):
    Ah = mAh * 1e-3
    return Ah*voltage*3600

def battery_life_est(mAh,voltage,ws, V = 3, i_self = 1e-6):
    #ws : wsn 
    return mAh_to_J(mAh, voltage)/(ws.energy_day + V*i_self*3600*24) 

def battery_life_est_nomac(mAh,voltage,ws):
    #ws : wsn 
    return mAh_to_J(mAh, voltage)/ws.energy_day_nomac
        

