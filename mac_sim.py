#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thursday 31 Oct 16:09:12 2024

@author: alx
"""
import numpy as np
import matplotlib.pyplot as plt
#t - duty cycle in seconds
#packet - packet length in timeslots (1 timeslot -> 10 bytes)
def simulate(N,packet=2,t=1):
  #all nodes should wake up in the first p timeslots
  p = t/0.00032 - 125 #duty cycle in timeslot (substract some to ensure every node will be done by the end of the period)
  #p = 15
  sleep_state = np.random.randint(0,p,N)
  s = np.min(sleep_state)
  sleep_state = sleep_state - s #no need to wait for the first node to wake up
  #print(f'sleep state at the beginning of the execution is {sleep_state}')
  #MAC values  
  aMinBE = 3  # Minimum Backoff Exponent
  aMaxBE = 5  # Maximum Backoff Exponent
  macMaxCSMABackoffs = 5  # Maximum CSMA backoffs
  RT_max = 4
  ACK = 1 # typical ack length in timeslots (12 SYMBOLS TURNAROUND TIME + ack packet length)
  MaxAckWait = 3 #timeslots - typically 54
  #arrays for storing values   
  NB = np.zeros(N, dtype=int)  #stores Number of backoffs for all nodes
  BE = np.full(N, aMinBE, dtype=int)  #stores Backoff exponent for all nodes
  delay = np.random.randint(0, 2**aMinBE, N)  # stores Delay values (-9:sleeping,-100:success,-200:failure,-1:CCA,-3:tx failure)
  waitAck = np.zeros(N,dtype=int) #indicates if a node waits for Ack  
  tx_packet = np.zeros(N, dtype=int)  # Time remaining in busy state for each node in timeslots
  RT = np.zeros(N,dtype=int) #stores number of tx retries
  channel_busy = 0 #channel status = timeslot left for busy channel
  #Tracking variables
  nbTx= np.zeros(N, dtype=int)
  nbCol = np.zeros(N, dtype=int)
  nbFail = np.zeros(N, dtype=int)
  nbBackoff = np.zeros(N,dtype = int)
  nbCCA = np.zeros(N, dtype=int)
  nbRx = np.zeros(N,dtype = int)
  #helping arrays  
  delay_n = delay.copy()
  #timeslots counters
  k=0 #total simulated timeslots
  id = 0 #count timeslots in which no node is active (to substract them at the end)

  while np.any(delay > -10): #while there are still nodes with packets

      #assign delay = -9 to nodes who are still sleeping
      delay_n = np.where(sleep_state!=0,-9,delay_n)
      #dealy array indicates the status of nodes
      delay = delay_n
      #print("starting timeslot simulation")
      op = np.where((waitAck>0) & (delay>-10)) #find nodes which are waiting for ack and will not receive it because of collision
      #print("are there nodes waiting for a ACK they will never receive? " + str(op))
      waitAck[op] -=1 #update time to wait for ack
      inx = np.where((delay != -100) & (delay != -200)) #find nodes that have not reached success or failure states
      #print(f'nodes still in the game are {inx}')
      #print('delay at the start of the timeslot is' + str(delay_n))  
     
      if np.all(delay[inx] == -9) :
          if channel_busy == 0:
              sl = np.min(sleep_state[inx])
              sleep_state[inx] = sleep_state[inx] - sl + 1
              #print(f'skipping {sl} timeslots')
              #all nodes in interest are still sleeping and no on-going transmission
              id += 1 
              #print("idle timeslot")
      if (np.any(waitAck[op]==0)):
        #resetCounters --caution
        #print("colliding nodes back in the game this timeslot")
        delay_n[op] = np.random.randint(0, 2**aMinBE, op[0].size)  # nodes are back in the game
      
      if channel_busy>0:
        channel_busy -=1 #update channel status
        #print("at this timeslot channel is busy (1+) or idle (0) " + str(channel_busy))  
        if channel_busy==0:
          h = np.where(delay==-3) #the nodes are done waiting - back to default values
          waitAck[h] = MaxAckWait
      bo = np.where(delay>=0) #nodes either in backoff or cca
      nbBackoff[bo]+=1
      delay_n[bo] = delay_n[bo] -1 #decrement counter
      arg_cca = np.where(delay == -1) #nodes that just did cca
      nbBackoff[arg_cca] -=1 #remove the one extra charged backoff
      nbCCA[arg_cca] += 1 #keep track of number of cca performed
      if channel_busy == 0:
        cca_no = arg_cca[0].size #the number of nodes that simultaneously access the channel
        if cca_no > 1:
          #case of collision
          delay_n[arg_cca] = -3 #tx_col
          channel_busy = packet + 1
          #update metrics
          nbCol[arg_cca] +=1
          #update RT
          RT[arg_cca] +=1         
          NB[arg_cca] = 0 #reset
          ux = np.where((RT>RT_max) & (delay>-50))
          delay_n[ux] = -200 #failed due to reaching the max levels of retries
        elif cca_no == 1:
          channel_busy = packet +1
          nbTx[arg_cca] +=1
          delay_n[arg_cca] = -100 #succesfull transmission
          #check to see if that is the last node
          mask = np.arange(delay.shape[0]) != arg_cca
          if np.all(delay[mask.flatten()] < -10):
            k += packet + ACK  #and one timeslot is added to the end of the algorithm
      else:
        NB[arg_cca] +=1
        if arg_cca[0].size>0:  # This checks if arg_cca is not empty
          for i in arg_cca[0]:
            BE[i] = np.min(np.array([BE[i] + 1, aMaxBE]))
            
        delay_n[arg_cca] = np.array([np.random.randint(1, 2**BE[i]) for i in arg_cca])  # Delay value
        f = np.where(NB>macMaxCSMABackoffs)
        delay_n[f] = -200 #failed to transmit due to reaching max value of BackOffs
      s_wu = np.where(sleep_state == 1)
      delay_n[s_wu] = np.random.randint(0,2**aMinBE,s_wu[0].size)
      sleep_state = np.where(sleep_state != 0, sleep_state - 1, sleep_state)
      k += 1
      
      #print(f'idle timeslots so far {id}')
      #print("NB status is " + str(nbBackoff))
      
      #print("delay is at the end of the timeslot " + str(delay_n))
      #print(f"end of {k}th timeslot simulation")
      #print("................ ")
      #print("................ ")  

  transmissions = (delay == -100).sum()
  throughput = np.sum(transmissions*packet)/(k-id)
  col = (nbCol == 1).sum()
  bo_mean = np.mean(nbBackoff)
  cca_mean = np.mean(nbCCA)
  #print("packet transmission timeslots")  
  #print(np.sum(transmissions*packet))
  #print("*******")
  #print(f"total timeslots are {k}")
  #print('*********')
  #print(f'idle timeslots are {id}')
  #print("................ ")
  #print("................ ")  
  return np.array([throughput,col,transmissions,bo_mean,cca_mean])


def sim_avg(n=20,packet=2,t=1,it=2000):
    thr_h = np.zeros((it,))
    col_h = np.zeros((it,))
    tx_h = np.zeros((it,))
    bo_h = np.zeros((it,))
    cca_h = np.zeros((it,))
    for j in range(0,it):
        var = simulate(n,packet,t)
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
    
    return [thr,col,tx,bo,cca]

