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
network = Hybrid_WSN()
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
plt.show()


#################
#################
######STEP 2#####
###NO SUNLIGHT###
#################
original_file = "design.py"
backup_file = "design_backup.py"

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

#network_n = Hybrid_WSN()
#eh_n = EH()



    


#op = np.load('op_l_sun_2500.npy')
#nor = ut.spher_to_cart_ar(1, op[:,0], op[:,1]).T
#op_n = np.load('op_l_nsun_diago.npy')
#nor_n = ut.spher_to_cart_ar(1, op_n[:,0], op_n[:,1]).T
#D = SolarPanel(Isc = d['Isc'], Voc = d['Voc'], Imp = d['Imp'], Vmp = d['Vmp'], N = d['N'], G = 1000, area= d['A_solar'])



#u = solar_power('e',panel,nor)
#f = solar_power('e',panel,nor) 
#g = solar_power('e',P121_panel,nor_n) 

#area = calculate_min_solar_panel_area(ws,f,0,1,0)

#plt.plot(ws.r_sensor[:,0], area*1e4)
#plt.xlabel("Diagonal [m]")
#lt.ylabel("Area of Solar Cell [cm**2]")

#plt.figure(figsize=(10, 6))



#plt.plot(f.l.r_sensor[:,0], f.eff_sun*100 , marker='^', label='Efficiency of PV in indoor environment with ambient sunlight')
#plt.plot(f.l.r_sensor[:,0], g.eff_no_sun*100 , marker='o', label='Efficiency of PV in indoor environment without ambient sunlight')

#plt.xlabel("Diagonal [m]")
#plt.ylabel("PV Efficiency (%)")
#plt.title("Plot of PV efficiency for sensor nodes in the diagonal")
#plt.legend()


#plt.figure(figsize=(10, 6))



#plt.plot(f.l.r_sensor[:,0], op[:,0] , marker='^', label='Azimuth')
#plt.plot(f.l.r_sensor[:,0], op[:,1], marker='o', label='angle')
#plt.plot(f.l.r_sensor[:,0], op_n[:,0] , marker='^', label='Azimuth1')
#plt.plot(f.l.r_sensor[:,0], op_n[:,1], marker='o', label='angle1')

#plt.xlabel("Diagonal [m]")
#plt.ylabel("PV Efficiency (%)")
#plt.title("Plot of PV efficiency for sensor nodes in the diagonal")
#plt.legend()



#plt.figure(figsize=(10, 6))
#plt.plot(f.l.r_sensor[:,0], f.p_out_sun*1000, marker='o',label='Naive Orientation')
#plt.plot(g.l.r_sensor[:,0], g.p_out_sun*1000,marker='^', label='Near Optimal Orientation')
#plt.xlabel("Diagonal [m]")
#plt.ylabel("Output power of PV [mW]")
#plt.title("Plot of output PV power in the diagonal in the presence of sunlight")
#plt.legend()
#plt.show()


