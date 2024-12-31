# -*- coding: utf-8 -*-

#linear fit -  current = a*power + b
p_min = -20 #dB
p_max = 5 #dB
i_min = 4 #mA
i_max = 10 #mA

a = (i_max - i_min)/(p_max-p_min)
b = i_min - a*p_min
print(f'a is {a} and b is {b}')
print("Replace these values in the  min_tx_power_level(power) function @rf.py")

