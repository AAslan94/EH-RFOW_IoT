# EH-OWRF_IoT
Open-source Python 3 library for simulating a hybrid VLC(downlink)/RF(uplink) indoor WSN for IoT with Energy Harvesting (EH) capabilities. 
The communication model includes simulation of PHY and MAC (Unslotted CSMA-CA) layers. 
VLC employes ON-OFF Keying modulation taking into account both LOS & Diffuse contributions, where the RF uplink is based on 802.15.4 @2.4GHz. Duty-cycling is also assumed and the period can be set accordingly.
For the EH, the PV panels are modelled with the five-parameters equivalent circuit. The harvested power extracted for PV panels in indoor environments can be calculated in the presence or absence of sunlight coming from a window. 
The library is partially based on the PYOWIOT library [1].

**HOW TO USE IT**

See **Hybrid_EH_IoT_quick_start_guide.pdf** for a detailed quick start guide.

**Funding**

This code was written as part of the work for **[OWIN6G MSCA](https://owin6g.eu)** , supported by the **European Union**

**More documentation is on the way**


[1] https://github.com/thomaskamalakis/pyowiot

[2] V. Stornelli, M. Muttillo, T. de Rubeis, and I. Nardi, “A new simplified five-parameter estimation
method for single-diode model of photovoltaic panels,” Energies, vol. 12, no. 22, 2019.

