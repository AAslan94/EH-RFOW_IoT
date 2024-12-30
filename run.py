#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: alx
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from h_comm import *
from nrg_harvesting import *
from design import design



#Run network simulation 
print("starting hybrid network simulation - MAC simulation may take some time")
network = Hybrid_WSN()
print("ending hybrid network simulation")
#Run energy harvesting simulation 
eh = EH()

#Calculate battery life (250 mAh, 3.7 V)
battery_life = battery_life_est(250, 3.7, network)  

# -----------------------------
# Plot 1: VLC - Total SNR dB (with ambient sunlight)
# -----------------------------
sensor_coords = network.sensor_pos[:, :2] #x,y coords
x_coords = sensor_coords[:, 0]
y_coords = sensor_coords[:, 1]
grid_x, grid_y = np.linspace(0, 10, 200), np.linspace(0, 10, 200) 
grid_x, grid_y = np.meshgrid(grid_x, grid_y)
snr_grid_interp = griddata(sensor_coords, network.vlc_snr_total, (grid_x, grid_y), method='cubic')
plt.figure(figsize=(8, 6))
plt.imshow(snr_grid_interp, origin='lower', cmap='viridis', extent=(x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()), aspect='auto')
plt.colorbar(label='SNR [dB]')
plt.xlabel('Length [m]')
plt.ylabel('Width [m]')
plt.title('SNR - with ambient sunlight')
plt.ion()
plt.show()


# -----------------------------
# Plot 2: VLC - Diffuse SNR dB (with ambient sunlight)
# -----------------------------
snr_grid_interp = griddata(sensor_coords, network.vlc_snr_diffuse, (grid_x, grid_y), method='cubic')
plt.figure(figsize=(8, 6))
plt.imshow(snr_grid_interp, origin='lower', cmap='viridis', extent=(x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()), aspect='auto')
plt.colorbar(label='SNR [dB]')
plt.xlabel('Length [m]')
plt.ylabel('Width [m]')
plt.title('Diffuse SNR - with ambient sunlight')
plt.ion()
plt.show()



# -----------------------------
# Plot 3: Calculate battery life for SNs
# -----------------------------
batt_grid_inter = griddata(sensor_coords, battery_life, (grid_x, grid_y), method='cubic')
plt.figure(figsize=(8, 6))
plt.imshow(batt_grid_inter, extent=(x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()), 
           origin='lower', cmap='viridis', aspect='auto')
plt.colorbar(label="Battery Life Estimate [days]")
plt.title(f"Battery life estimate - T = {network.Tperiod[0]} s")
plt.xlabel("Length [m]")
plt.ylabel("Width [m]")
plt.ion()
plt.show()

# -----------------------------
# Plot 3: EH per hour for SNs
# -----------------------------
energy_hour_inter = griddata((x_coords, y_coords), eh.esun_h, (grid_x, grid_y), method='cubic')
plt.figure(figsize=(8, 6))
plt.imshow(energy_hour_inter, extent=(x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()),
           origin='lower', cmap='viridis', aspect='auto', vmin=0, vmax=100) 
colorbar = plt.colorbar(label='Energy harvested per hour [J]', ticks=np.arange(2, 103, 10))
plt.xlabel("Length [m]")
plt.ylabel("Width [m]")
plt.title('Energy harvested per hour with sunlight')
plt.ion()
plt.show()

while True:
    user_input = input("Type 'exit' to close the program: ")
    if user_input.lower() == 'exit':
        break
