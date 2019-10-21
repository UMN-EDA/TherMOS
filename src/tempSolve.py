#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import time
import math
import json
import numpy as np
import scipy.sparse as sparse_mat
import scipy.sparse.linalg as sparse_algebra
from pprint import pprint
#from thermal_model import thermal_model

class tempSolve:
    def __init__ (self, device_model, a_gates, power):
        self.G = sparse_mat.dok_matrix((device_model.N_x*device_model.N_y*device_model.N_z,
                device_model.N_x*device_model.N_y*device_model.N_z))
        self.P = np.zeros((device_model.N_x, device_model.N_y, device_model.N_z))
        self.T = np.zeros((device_model.N_x*device_model.N_y*device_model.N_z,1))
                
       
    def create_G(self, device_model):
        for k in range(0,device_model.N_z):
            for j in range(0,device_model.N_y):
                for i in range(0,device_model.N_x):
                    cur_node = self.G_index(device_model,i,j,k)
                    #+ve x
                    next_node = self.G_index(device_model,i+1,j,k)
                    if next_node >= 0:
                        cond = (device_model.res_y*device_model.res_z/device_model.res_x) * (device_model.C[i,j,k]+device_model.C[i+1,j,k])/2
                        self.G[cur_node,next_node] = - cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    #-ve x
                    next_node = self.G_index(device_model,i-1,j,k)
                    if next_node >= 0:
                        cond = (device_model.res_y*device_model.res_z/device_model.res_x) * (device_model.C[i,j,k]+device_model.C[i-1,j,k])/2
                        self.G[cur_node,next_node] = -cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    #+ve y
                    next_node = self.G_index(device_model,i,j+1,k)
                    if next_node >= 0:
                        cond = (device_model.res_x*device_model.res_z/device_model.res_y) * (device_model.C[i,j,k]+device_model.C[i,j+1,k])/2
                        self.G[cur_node,next_node] = - cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    #-ve y
                    next_node = self.G_index(device_model,i,j-1,k)
                    if next_node >= 0:
                        cond = (device_model.res_x*device_model.res_z/device_model.res_y) * (device_model.C[i,j,k]+device_model.C[i,j-1,k])/2
                        self.G[cur_node,next_node] = - cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    #+ve z
                    next_node = self.G_index(device_model,i,j,k+1)
                    if next_node >= 0:
                        cond = (device_model.res_x*device_model.res_y/device_model.res_z) * (device_model.C[i,j,k]+device_model.C[i,j,k+1])/2
                        self.G[cur_node,next_node] = - cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    else: #handle the case of contact to above
                        if device_model.contact_mask[i,j]: #location of a contact in the top plane
                            cond = (device_model.res_x*device_model.res_y/device_model.t_cnt2gnd) * device_model.C[i,j,k]
                            self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond                        
                    #-ve z
                    next_node = self.G_index(device_model,i,j,k-1)
                    if next_node >= 0:
                        cond = (device_model.res_x*device_model.res_y/device_model.res_z) * (device_model.C[i,j,k]+device_model.C[i,j,k-1])/2
                        self.G[cur_node,next_node] = -cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    else: 
                    # if it is the lowermost layer we add a resistance to the ground
                    # for conduction 
                        cond = (device_model.res_x*device_model.res_y/device_model.t_sub2gnd) * device_model.C[i,j,k]
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond


    def create_P(self,device_model,active_gates,power):
        # active gates is list type and contains all the gates you like to
        # distribute power across
        assert isinstance(active_gates,list),"active_gates expected type list but received type %s instead"%(type(active_gates)) 
        pwr = np.zeros((device_model.N_x,device_model.N_y,device_model.N_z))
        #TODO modify so that it reuse the create box function
        for gate in active_gates:
            #TODO modify if you require uneven distribution between gates
            pwr_gate = power/len(active_gates)
            if device_model.n_fin == 0:
                origin = device_model.gate_loc[gate]['origin']
                size = device_model.gate_loc[gate]['size']
                power_profile = device_model.gate_loc[gate]['power_profile']
                (or_x, or_y, or_z) = device_model.quantize_values(origin)
                (sz_x, sz_y, sz_z) = device_model.quantize_values(size)
                pwr[or_x:(or_x + sz_x),or_y:(or_y + sz_y),or_z:(or_z + sz_z)] = power_profile*pwr_gate 
            else:
                for n in range(device_model.n_fin):
                    pwr_fin = pwr_gate/device_model.n_fin
                    gate_num =  gate*device_model.n_fin + n
                    origin = device_model.gate_loc[gate_num]['origin']
                    size = device_model.gate_loc[gate_num]['size']
                    power_profile = device_model.gate_loc[gate_num]['power_profile']
                    (or_x, or_y, or_z) = device_model.quantize_values(origin)
                    (sz_x, sz_y, sz_z) = device_model.quantize_values(size)
                    pwr[or_x:(or_x + sz_x),or_y:(or_y + sz_y),or_z:(or_z + sz_z)] = power_profile*pwr_fin 
        self.P = pwr.reshape((device_model.N_x*device_model.N_y*device_model.N_z,1),order='F') #fortran ordering to index x first then y then z
        
                    
    def G_index(self,device_model,i,j,k):
        if (i < 0 or i >= device_model.N_x or
            j < 0 or j >= device_model.N_y or
            k < 0 or k >= device_model.N_z ):
            return -1
        else:
            return device_model.N_x * device_model.N_y * k + j* device_model.N_x + i

    def create_equations(self,device_model, a_gates,power): 
        print("INFO: Beginning G matrix creation")
        # create G matrix
        s1 = time.time()
        self.create_G(device_model)
        e1 = time.time()
        print("INFO: Completed G matrix in %e"%(e1-s1))
        s1=time.time()
        self.create_P(device_model,a_gates,power)
        e1 = time.time()
        print("INFO: Completed P matrix in %e"%(e1-s1))

    def solve(self, device_model):
        #solve the equations
        G = self.G.tocsc()
        P = sparse_mat.csc_matrix(self.P)
        I = sparse_mat.identity(G.shape[0]) * 1e-13
        G = G + I
        print("INFO: Size of matrix %d x %d"%G.shape)
        print("INFO: Number of Non zeros %d"%G.nnz)
        print("INFO: Solving for temperature")
        s1=time.time()
        self.T = sparse_algebra.spsolve(G, P, permc_spec=None, use_umfpack=True)
        e1=time.time()
        
        print("INFO: Completed solving in %e"%(e1-s1))
        np.savetxt('./output/T.out',self.T)
        np.savetxt('./work/T.out',self.T)
        
        
        print("Result: Max temperature rise:%e"%(max(self.T)))
        print("Result: Minimum temperature rise: %e"%(min(self.T)))
        print("Result: Average temperature rise: %e"%(np.average(self.T)))
        self.T= self.T.reshape((device_model.N_x,device_model.N_y,device_model.N_z),order='F')

    #def save_model(self):
    #    C= self.C.reshape((-1),order='f')
    #    np.savetxt('./work/C.out',C)
    #    print("\n")
    #    
    #    data2save = np.array([[self.resx,self.resy,self.resz],
    #                          [self.length,self.width,self.height]])
    #    np.savetxt('./work/device_parameters.csv',data2save,'%5.4e',',')



    #def quantize_values(self,val):
    #    val_x = math.ceil(val[0]/self.res_x) 
    #    val_y = math.ceil(val[1]/self.res_y)
    #    val_z = math.ceil(val[2]/self.res_z)
    #    return (val_x, val_y, val_z)

