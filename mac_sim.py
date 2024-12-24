#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thursday 31 Oct 16:09:12 2024

@author: alx
"""

import numpy as np
import matplotlib.pyplot as plt
def simulate(N,packet):
  #all nodes should wake up in the first p timeslots
  p = 3000
  sleep_state = np.random.randint(0,p,N)
  #print(sleep_state)
  s = np.min(sleep_state)
  sleep_state = sleep_state - s
  #print(sleep_state)
  aMinBE = 3  # Minimum Backoff Exponent
  aMaxBE = 5  # Maximum Backoff Exponent
  macMaxCSMABackoffs = 5  # Maximum CSMA backoffs
  #packet = 2 #packet length in time-slots
  RT_max = 4
  ACK = 1 #12 SYMBOLS TURNAROUND TIME + ack
  MaxAckWait = 3 #timeslots - typically 54
  NB = np.zeros(N, dtype=int)  # Number of backoffs
  BE = np.full(N, aMinBE, dtype=int)  # Backoff exponent
  delay = np.random.randint(0, 2**aMinBE, N)  # Delay values
  tx_packet = np.zeros(N, dtype=int)  # Time remaining in busy state for each node
  RT = np.zeros(N,dtype=int)
  channel_busy = 0 #timeslot left for busy channel
  #Tracking variables
  nbTx= np.zeros(N, dtype=int)
  nbCol = np.zeros(N, dtype=int)
  nbFail = np.zeros(N, dtype=int)
  nbBackoff = np.zeros(N,dtype = int)
  nbCCA = np.zeros(N, dtype=int)
  nbRx = np.zeros(N,dtype = int)
  delay_n = delay
  waitAck = np.zeros(N,dtype=int)
  k=0
  id = 0 #count timeslots in which no node is active

  while np.any(delay > -10): #while there are still nodes with packets
     #assign delay = -9 to nodes who are still sleeping
      #print(f"sleep state is {sleep_state}")
      delay_n = np.where(sleep_state!=0,-9,delay_n)
      delay = delay_n
      op = np.where((waitAck>0) & (delay>-10))
      waitAck[op] -=1
      inx = np.where((delay != -100) & (delay != -200))
      #print(f'{np.all(delay[inx])} delay inx')
      if np.all(delay[inx] == -9) :
          id += 1 
          #print("idle timeslot")
      if (np.any(waitAck[op]==0)):
        #resetCounters
        delay_n[op] = np.random.randint(0, 2**aMinBE, op[0].size)  # Delay value
      if channel_busy>0:
        channel_busy -=1
        if channel_busy==0:
          h = np.where(delay==-3)
          waitAck[h] = MaxAckWait
      #print(f"Currently simulating slot {k}:")
      #check to see if any node is ready for CCA
      #print(f"Channel is Busy for {channel_busy} more time-slots")
      #print(f"Backoff Counter at the start of {k} slot is {delay}")
     # print("Wait Ack" + str(waitAck))
      bo = np.where(delay>-1) #nodes either in backoff or cca
      nbBackoff[bo]+=1
      delay_n[bo] = delay_n[bo] -1 #decrement counter
      arg_cca = np.where(delay == -1) #nodes that just did cca
      nbCCA[arg_cca] += 1 #keep track of number of cca performed
      if channel_busy == 0:
        cca_no = arg_cca[0].size
        if cca_no > 1:
          #case of collision
          delay_n[arg_cca] = -3 #tx_col
          channel_busy = packet + 1
          #update metrics
          nbCol[arg_cca] +=1
          #update RT
          RT[arg_cca] +=1
          #print("RT IS " + str(RT))
          NB[arg_cca] = 0 #reset
          ux = np.where((RT>RT_max) & (delay>-50))
          delay_n[ux] = -200 #failed due to reaching the max levels of retries
        elif cca_no == 1:
          delay_n[arg_cca] = -2 #tx_col
          channel_busy = packet + ACK +1
          nbTx[arg_cca] +=1
          delay_n[arg_cca] = -100 #succesfull transmission
          #check to see if that is the last node
          mask = np.arange(delay.shape[0]) != arg_cca
          #print(f'mask is {mask}')
          if np.all(delay[mask.flatten()] < -10):
            k += packet  #and one timeslot is added to the end of the algorithm
      else:
        NB[arg_cca] +=1
        if arg_cca[0].size>0:  # This checks if arg_cca is not empty
          for i in arg_cca[0]:
            BE[i] = np.min(np.array([BE[i] + 1, aMaxBE]))
            #print(f"BE is {BE}")
        delay_n[arg_cca] = np.array([np.random.randint(1, 2**BE[i]) for i in arg_cca])  # Delay value
        f = np.where(NB>macMaxCSMABackoffs)
        delay_n[f] = -200 #failed to transmit due to reaching max value of BackOffs
      s_wu = np.where(sleep_state == 1)
      #print(f"s_wu is {s_wu} and s_wu size is {s_wu[0].size} ")
     # print(f"delay n[wu]  shape is {delay_n[s_wu[0]].shape}")
      #print(delay_n)
      delay_n[s_wu] = np.random.randint(0,2**aMinBE,s_wu[0].size)
      sleep_state = np.where(sleep_state != 0, sleep_state - 1, sleep_state)
      k += 1
     # print("NB status is " + str(NB))
     # print("k is " + str(k))
  transmissions = (delay == -100).sum()
  throughput = np.sum(transmissions*packet)/(k-1-id)
  col = (nbCol == 1).sum()
  bo_mean = np.mean(nbBackoff)
  cca_mean = np.mean(nbCCA)
  return np.array([throughput,col,transmissions,bo_mean,cca_mean])


def sim_avg(n=20,packet=2,it=2000):
    thr_h = np.zeros((it,))
    col_h = np.zeros((it,))
    tx_h = np.zeros((it,))
    bo_h = np.zeros((it,))
    cca_h = np.zeros((it,))
    for j in range(0,it):
        var = simulate(n,packet)
        thr_h[j] = var[0]
        col_h[j] = var[1]
        tx_h[j] = var[2]
        bo_h[j] = var[3]
        cca_h[j] = var[4]
    thr = np.mean(thr_h)
    col = np.mean(col_h)
    tx = np.mean(tx_h)
    bo = np.mean(bo_h)
    cca = np.mean(cca_h)
    print(thr,col,tx,bo,cca)
    return [thr,col,tx,bo,cca]

#var = sim_avg()
#print(var)
