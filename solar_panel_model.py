#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:09:12 2024

@author: alx
"""
import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt


import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt


#extract 5-parameters of the solar cell equivalent circuit
def get_solar_parameters_stc(Isc,Voc,Imp,Vmp,N):
  #print("Estimation of PV parameters with Stornelli et al method")
  q = 1.6e-19  # Electron charge  (C)
  k = 1.38e-23  # Boltzmann constant (J/K)
  T = 298  # Temperature (K)
  Vt = (k * T * N) / q #Thermal Voltage (V) (* A =1) 
  Pmax = Imp * Vmp
  # Series resistance (Rs)
  Rs = (Voc / Imp) - (Vmp / Imp) + ((Vt / Imp) * np.log(Vt / (Vt + Vmp)))
  # Initial diode saturation current (I0)
  I0 = Isc / (np.exp(Voc / Vt) - np.exp(Rs * Isc / Vt))
  # Photocurrent (Ipv)
  Ipv = I0 * (np.exp(Voc / Vt) - 1)
  # First step
  iter = 10000
  it = 0
  tol = 0.1
  A1 = 1
  # Initial guess for VmpC
  VmpC = (Vt * np.log((Ipv + I0 - Imp) / I0)) - (Rs * Imp)
  e1 = VmpC - Vmp
  Rs1 = Rs
  # Iteration loop for adjusting A
  while it < iter and e1 > tol:
    if VmpC < Vmp:
      A1 -= 0.01
    else:
     A1 += 0.01
    Vt1 = (k * A1 * T * N) / q
    I01 = Isc / (np.exp(Voc / Vt1) - np.exp(Rs1 * Isc / Vt1))
    Ipv1 = I01 * (np.exp(Voc / Vt1) - 1)
    VmpC = (Vt1 * np.log((Ipv1 + I01 - Imp) / I01)) - (Rs1 * Imp)
    e1 = VmpC - Vmp
    it += 1


  # Update Vt1 and Rs1
  Vt1 = (k * A1 * T * N) / q
  Rs1 = (Voc / Imp) - (VmpC / Imp) + ((Vt1 / Imp) * np.log(Vt1 / (Vt1 + VmpC)))

  # Second part
  tolI = 0.001
  iter = 10000
  itI = 0

  # Recalculate I0 with Rs1
  I01 = Isc / (np.exp(Voc / Vt1) - np.exp(Rs1 * Isc / Vt1))
  Ipv1 = I01 * (np.exp(Voc / Vt1) - 1)

  # Initial guess for Rp
  Rp = ((-Vmp) * (Vmp + (Rs1 * Imp))) / (Pmax - (Vmp * Ipv1) + (Vmp * I01 * (np.exp((Vmp + (Rs1 * Imp)) / Vt1) - 1)))

  # Calculate I0 with new Rp
  I02 = (Isc * (1 + Rs1 / Rp) - Voc / Rp) / (np.exp(Voc / Vt1) - np.exp(Rs1 * Isc / Vt1))
  Ipv2 = I02 * (np.exp(Voc / Vt1) - 1) + Voc / Rp
  ImpC = Pmax / VmpC
  err = abs(Imp - ImpC)
  Rpnew = Rp

  # Iteration loop for Rpnew
  while err > tolI and itI < iter:
    if ImpC < Imp:
      Rpnew = Rp + 0.1 * itI
    elif ImpC >= Imp:
      Rpnew = Rp - 0.1 * itI

    # Calculate I0 with Rpnew
    I02 = (Isc * (1 + Rs1 / Rpnew) - Voc / Rpnew) / (np.exp(Voc / Vt1) - np.exp(Rs1 * Isc / Vt1))
    Ipv2 = I02 * (np.exp(Voc / Vt1) - 1) + Voc / Rpnew

    # Define equation to solve for ImpC
    def eqn(ImpC):
      return Ipv2 - (I02 * (np.exp((Vmp + (Rs1 * ImpC)) / Vt1) - 1)) - ImpC - (Vmp + Rs1 * ImpC) / Rpnew

    # Use fsolve to solve for ImpC
    ImpC = fsolve(eqn, Imp)

    err = abs(Imp - ImpC)
    itI += 1

  return A1,I02,Ipv2,np.abs(Rs1),Rpnew

def get_solar_parameters_stc_brano(i_exp,v_exp):
  print("Estimation of PV parameters with Brano et al method")
  if i_exp is None or v_exp is None:
    print("I-V experimental points is None")
  current = i_exp
  voltage = v_exp
  power = current * voltage
  pmpp = np.max(power)
  pmp_i = np.argmax(power)
  vmpp= voltage[pmp_i]
  impp = current[pmp_i]
  #find slope of current with respect to voltage for volage = 0 to find rsh0
  s = []
  for i in range(1,10):
    s.append((current[i]-current[0])/(voltage[i] - voltage[0]))

  rsh0 = (round((-1/np.mean(s)),3))
  rsh0_v = rsh0

  #find slope of current with respect for I = 0 to find rs

  s = []
  for i in range(1,10):
    s.append((current[-i-1] - current[-1])/ (voltage[-i-1] - voltage[-1]))
  rs0 = -round((1/np.mean(s)),3)
  rs0_v = rs0
  
  isc = current[0]
  voc = voltage[-1]

  k = 1.38064852e-23
  q = 1.60217662e-19
  T = 298.15
  vt = k*T/q;
  N = 1
  n_guess = k*N/q
  il = isc
  rsh = rsh0
  rs = rs0
  n = n_guess

  diff_rs = []
  for i in range(10):
    diff_n = []
    for j in range(100):
      i0 = -(impp*rs + impp*rsh - il*rsh + vmpp)/(rsh*(np.exp((impp*rs + vmpp)/(T*n)) - 1))
      il = i0*np.exp(isc*rs/(T*n)) - i0 + isc*rs/rsh + isc
      rsh = T*n*(-rs + rsh0)/(T*n + i0*rs*np.exp(isc*rs/(T*n)) - i0*rsh0*np.exp(isc*rs/(T*n)))

      #calculate n and compare it to the current estimate
      n1 = voc/(T*np.log(1 + il/i0 - voc/(i0*rsh)))
      diff_n.append(abs(1-n/n1))

      #update n
      n = n1
  #calculate rs and compare it to the current estimate
    rs1 = (T*n*rs0 - T*n*rsh + i0*rs0*rsh*np.exp(voc/(T*n)))/(T*n + i0*rsh*np.exp(voc/(T*n)))
    diff_rs.append(abs(1-rs/rs1))

    rs = rs1
  i_0 = i0
  i_pv = il
  n_f = n*q/k
  return n_f,i_0,i_pv,np.abs(rs),rsh

class SolarPanel:
  def __init__(self,Isc = 1,Voc = 1,Imp = 0.8,Vmp = 0.8,N = 1,G = 1000, area = 1e-2,method = 'Default',i_exp=None,v_exp = None):
    self.Isc = Isc #short circuit current - data sheet
    self.Voc = Voc #open circuit voltage - data sheet
    self.Imp = Imp #Max-power current - data sheet
    self.Vmp = Vmp #Max-power voltage - data sheet
    self.N = N #No of cells in series - data sheet
    self.G = G #Irradiance (default is Gstc = 1000 W/M2)
    self.A = None #ideality factor (1/5 eq.circuit params)(suppose =1 hard-coded at the start of the algorithm)
    self.I0 = None #diode-saturation current - (2/5) eq.circuit params
    self.Ipv = None #photocurrent - (3/5) eq.circuit params
    self.Rs = None #series resistance - (4/5) eq.circuit params
    self.Rp = None #parallel resistance - (5/5) eq.circuit params
    self.Vt = None #thermal voltage (Volt)
    self.Pmax = self.Vmp * self.Imp #Maximum power point in W
    self.Pmax_irr = None  #Maximum Pmax based on irradiance - if irradiance = 1000 w/m2 => Pmax_irr = Pmax
    self.area = area #default = 100 cm^2
    self.efficiency = None
    Gstc = 1000 #W/M2
    self.i_exp = i_exp
    self.v_exp = v_exp
    self.method = method 
    
  def getArea(self):
      return self.area
  
  def get_solar_parameters(self, Gcorrection = False):
    if self.method == 'Brano':
      i = get_solar_parameters_stc_brano(self.i_exp,self.v_exp)
    else:
      i = get_solar_parameters_stc(self.Isc,self.Voc,self.Imp,self.Vmp,self.N)
    q = 1.6e-19  # Electron charge  (C)
    k = 1.38e-23  # Boltzmann constant (J/K)
    T = 298  # Temperature (K)
    Gstc = 1000 #W/M2
    self.A = i[0]
    self.I0 = i[1]
    self.Ipv = i[2]
    self.Rs = i[3]
    self.Rp = i[4]
    self.Vt = (k * self.A * T * self.N) / q
    if Gcorrection: #correction with irradiance
      self.Isc = self.Isc * self.G/Gstc
      self.Voc = self.Voc  + self.Vt* np.log(self.G/Gstc)
      self.Rp = self.Rp * Gstc/self.G
      self.Rs = self.Rs * Gstc/self.G
      self.Ipv = self.I0 * (np.exp(self.Voc / self.Vt) - 1)

  def setG(self,newG):
    self.G = newG
    self.get_solar_parameters(True)

  def iv_curve(self,plot_on = False):
    q = 1.6e-19  # Electron charge  (C)
    k = 1.38e-23  # Boltzmann constant (J/K)
    T = 298  # Temperature (K)
    v_range = np.linspace(0, self.Voc, 100)

    def f(i):
     return self.Ipv - self.I0 * (np.exp((v_range + i * self.Rs) / (self.Vt)) - 1) - (v_range + i * self.Rs) / self.Rp - i

    i_out = fsolve(f, self.Ipv * np.ones_like(v_range)) #solve f with initial value Ipv = I
    v_out = v_range[:len(i_out)]
    p_out = i_out * v_out
    ind = np.argmax(p_out)
    mpp_v = v_out[ind]
    self.Vmp = v_out[ind]
    self.Imp = i_out[ind]
    mpp_i = i_out[ind]
    mpp_p = p_out[ind]
    self.Pmax_irr = p_out[ind]
    #print("Maximum power at irradiance " + str(self.G) + " watt/m2 is equal to " + str(self.Pmax_irr*1000) + " mW")
    if plot_on:
     # Plotting the curves
      plt.figure(figsize=(10, 6))
     # Plot I-V curve
      plt.subplot(2, 1, 1)
      plt.plot(v_out, i_out, label='I-V Curve', color='blue')
      plt.scatter(mpp_v, mpp_i, color='red', label=f'MPP ({mpp_v:.2f} V, {mpp_i:.2f} A)')
      plt.title('I-V Curve of Solar Panel')
      plt.xlabel('Voltage (V)')
      plt.ylabel('Current (I)')
      plt.legend()
      plt.grid(True)

      # Plot P-V curve
      plt.subplot(2, 1, 2)
      plt.plot(v_out, p_out, label='P-V Curve', color='orange')
      plt.scatter(mpp_v, mpp_p, color='red', label=f'MPP ({mpp_v:.2f} V, {mpp_p:.2f} W)')
      plt.title('P-V Curve of Solar Panel')
      plt.xlabel('Voltage (V)')
      plt.ylabel('Power (W)')
      plt.legend()
      plt.grid(True)

      # Show plot
      plt.tight_layout()
      plt.show()
  def calc_efficiency(self):
    f = 1/self.area
    self.efficiency = f * self.Pmax_irr / self.G

#
