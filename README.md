# Hybrid_EH_IoT
Library for simulating a hybrid VLC(downlink)/RF(uplink) indoor WSN for IoT with Energy Harvesting (EH) capabilities. 
Include simulation of PHY and MAC (Unslotted CSMA-CA) layers. 
VLC employes ON-OFF Keying modulation taking into account both LOS & Diffuse contributions, where the RF uplink is based on 802.15.4 @2.4GHz. Duty-cycling is also assumed and the period can be set accordingly.
For the EH, the PV panels are modelled with the five-parameters equivalent circuit. The harvested power extracted for PV panels in indoor environments can be calculated in the presence or absence of sunlight coming from a window. 
The library is partially based on the PYOWIOT library [1].
The library supports two methods for extracting the five-parameters for any PV panel. The default method is Stormelli et al [1]. The alternative method is Brano et al [2]. 

**HOW TO USE IT**
For full functionality you will need to install the following libraries:
*Numpy
*Matplotlib
*Scipy
*Pyswarms

To run the default scenario you can use either execute "run.py" (with ambient sunlight) or "run_no_sun.py" (without ambient sunlight). 
**You can define the parameters for your specific scenario altering the "design.py" file.**
The following work-flow is recommended for using the library:
1. Specify your scenario editing and saving the "design.py" file. You can use the functions in the "create_points.py" file, to create a grid of points (to use as positions of the LEDs, SNs, e.t.c.).
2. Run the "opt_solar_orientation.ipynb" notebook to find the optimal orientation of the PV panels. Once the script is run, make sure to save the results and pass the orientation numpy array to the design file.
3. The current MAC simulation results are for 20 nodes and are saved in the 'time_data.npz' file. For any custom scenario, you can either:
   - Uncomment line 65/ Comment line 66 of the h_comm file 
   - Run the unslotted simulator for the desired number of nodes/iterations and save the results with name         'time_data.npz'
4. Open "run.py" file:
   - You can create an object representing the hybrid network by calling the Hybrid_WSN class, eg:
     **network = Hybrid_WSN()** (Don't forget to include the "h_comm.py" file)
   - You can create an object representing the EH system by calling the EH class, eg:
     **eh = EH()** (Don't forget to include the "nrg_harvesting.py" file)

You are also free to use these two main classes independently - there is no dependency between them.

The results are stored as attributes of the created objects. For instance, to determine the energy harvested per hour from the PV panels, you can access the attribute "eh.esun_h".

In the "nrg_harvesting.py" file, there are also other energy related functions. For example, one can use "battery_life_est" function, to estimate the battery life of the WSN if a non-rechargeable power is to be used. In this case, you will need to pass an Hybrid_WSN object to the function. You can also use the "calculate_min_solar_panel_area(network,eh,...)" to estimate the size of the PV panel required for a given network.


To use the Brano et al method:
*Open "solar_panel_model.py"
*In the declaration of the SolarPanel Class, change method = 'Default' to method = 'Brano'


**More documentation is on the way**


[1] https://github.com/thomaskamalakis/pyowiot

[2] V. Stornelli, M. Muttillo, T. de Rubeis, and I. Nardi, “A new simplified five-parameter estimation
method for single-diode model of photovoltaic panels,” Energies, vol. 12, no. 22, 2019.

[3] V. Lo Brano, A. Orioli, C. Giuseppina, and A. Di Gangi, “An improved five-parameter model for
photovoltaic modules,” Solar Energy Materials and Solar Cells, vol. 94, pp. 1358–1370, 08 2010.
