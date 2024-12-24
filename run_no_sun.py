#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: alx
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import os
import shutil
import owutils as ut



#################
#################
######STEP 2#####
###NO SUNLIGHT###
#################
original_file = "design.py"
backup_file = "design_backup.py"

shutil.copyfile(original_file, backup_file)

updated_lines = []
with open(original_file, "r") as file:
    for line in file:
        if "'amb_L1'" in line:
            line = "'amb_L1': 0,\n"  # Replace amb_L1 value
        elif "'amb_L2'" in line:
            line = "'amb_L2': 0,\n"  # Replace amb_L2 value
        elif "'nR_solar'" in line:
            line = "'nR_solar': nor_n,\n"  # Replace nR_solar value
        updated_lines.append(line)

with open(original_file, "w") as file:
    file.writelines(updated_lines)

print("File successfully updated for no sun conditions.")


from h_comm import *
from nrg_harvesting import *

#Run network simulation 
network = Hybrid_WSN()
#Run energy harvesting simulation 
eh = EH()



# -----------------------------
# Plot 1: VLC - Total SNR dB (without ambient sunlight)
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
plt.title('SNR - without ambient sunlight')
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
plt.title('Diffuse SNR - without ambient sunlight')
plt.show()


# -----------------------------
# Plot 3: EH per hour for SNs
# -----------------------------
energy_hour_inter = griddata((x_coords, y_coords), eh.ensun_h, (grid_x, grid_y), method='cubic')
plt.figure(figsize=(8, 6))
plt.imshow(energy_hour_inter, extent=(x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()),
           origin='lower', cmap='viridis', aspect='auto') 
colorbar = plt.colorbar(label='Energy harvested per hour [J]')
plt.xlabel("Length [m]")
plt.ylabel("Width [m]")
plt.title('Energy harvested per hour without sunlight')
plt.show()

# -----------------------------
# Plot 3: Power Harvested per hour for SNs per cm^2
# -----------------------------
power_hour_inter = griddata((x_coords, y_coords), eh.pext_no_sun_cm*1e6, (grid_x, grid_y), method='cubic')
plt.figure(figsize=(8, 6))
plt.imshow(power_hour_inter, extent=(x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()),
           origin='lower', cmap='viridis', aspect='auto') 
colorbar = plt.colorbar(label='Power per cm$^2$ [μW]')
plt.xlabel("Length [m]")
plt.ylabel("Width [m]")
plt.title('Harvested power per cm$^2$ [μW] when there is no sunlight')
plt.show()

# -----------------------------
# Plot 4: Minimum PV Active Area
# -----------------------------
area = calculate_min_solar_panel_area(network,eh,0,8,1)
area_interp = griddata((x_coords, y_coords), area * 1e4, (grid_x, grid_y), method='cubic')

plt.figure(figsize=(8, 6))
plt.imshow(area_interp, extent=(x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()),
           origin='lower', cmap='viridis', aspect='auto')
plt.colorbar(label='Active area of the PV $[cm^2]$')
plt.xlabel("Length [m]")
plt.ylabel("Width [m]")
plt.title('Minimum PV active area [cm$^2$]')
plt.show()

shutil.copyfile(backup_file, original_file)
os.remove(backup_file)
print("Reverted to the original design.")





