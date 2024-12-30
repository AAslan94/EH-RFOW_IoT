#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: alx
"""

import numpy as np
import matplotlib.pyplot as plt
def gen_points(x_start,x_end,y_start,y_end,z_height, num_points_x, num_points_y,plot = False):
    x = np.linspace(x_start, x_end, num_points_x)
    y = np.linspace(y_start, y_end, num_points_y)
    xx, yy = np.meshgrid(x, y)
    z = np.full_like(xx, z_height)
    ceiling_points = np.stack([xx, yy, z], axis=-1).reshape(-1, 3)
    if plot:
        plt.figure(figsize=(6, 6))
        plt.scatter(ceiling_points[:, 0], ceiling_points[:, 1], color='blue', marker='o', label='Lighting LEDs')
        plt.scatter(5,5,color = 'red', marker = 'x', label='Communication LED')  
        plt.title("LEDs Arrangement in the ceiling")
        plt.xlabel("Width [m]")
        plt.ylabel("Length [m]")
        plt.grid(True)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlim([0,10])
        plt.ylim([0,10])
        #plt.legend(loc='upper right')
        #plt.show()        
    return ceiling_points

def diagonal_points(x_start,x_fin,y_start,y_fin,height, N = 20):
	start = np.array([x_start, y_start,height])
	end = np.array([x_fin,y_fin,height])
	return np.linspace(start, end, N+2)[1:-1]
	



  
