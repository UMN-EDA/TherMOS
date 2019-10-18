#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import math
import json
import numpy as np
import scipy.sparse as sparse_mat

#direction convention  
#length is along x Dimesion 0
#width  is along y Dimension 1
#height is along z Dimension 2
class thermal_model():
    def __init__(self,length, width, height, resolution,n_fin=0):
        self.n_fin= n_fin
        self.res_x = resolution[0]
        self.res_y = resolution[1]
        self.res_z = resolution[2]
        self.sz_x = length
        self.sz_y = width 
        self.sz_z = height
        (self.N_x,self.N_y,self.N_z)  = self.quantize_values((length,width,height))
        #conductivity matrix(conductivity of all nodes)
        self.C = np.zeros((self.N_x,self.N_y,self.N_z))  
        self.G = sparse_mat.dok_matrix(
            (self.N_x*self.N_y*self.N_z, self.N_x*self.N_y*self.N_z))
        self.n_gate = 0
        self.gate_loc = {}
        self.contact_mask = np.zeros((self.N_x,self.N_y))
        self.parameters = False
        self.cond_table = False
        
    def set_device_parameters(  self, 
                                channel_length, 
                                gate_thickness,
                                substrate2ground,
                                contact2ground,
                                gate_oxide_thickness
                                ):
        self.chnl_l = channel_length
        self.gate_t = gate_thickness
        self.t_ox = gate_oxide_thickness
        self.t_sub2gnd= substrate2ground
        self.t_cnt2gnd= contact2ground

        self.parameters =True;

    def set_conductivity_table(self,model_file):
        self.cond = {}
        with open(model_file) as f:
           cond_data = json.load(f) 
        self.cond['gate'] =       cond_data['thermal_conductivity']['gate'] #197e-9
        self.cond['Si NMOS SD'] = cond_data['thermal_conductivity']['Si NMOS SD'] #148e-9
        self.cond['Si PMOS SD'] = cond_data['thermal_conductivity']['Si PMOS SD'] #114e-9
        self.cond['Si NMOS fin'] = cond_data['thermal_conductivity']['Si NMOS fin']
        self.cond['Si PMOS fin'] = cond_data['thermal_conductivity']['Si PMOS fin'] 
        self.cond['Si substrate'] =cond_data['thermal_conductivity']['Si substrate'] #148e-9
        self.cond['SiGe PMOS channel'] = cond_data['thermal_conductivity']['SiGe PMOS channel'] #12.75e-9
        self.cond['Si NMOS channel'] = cond_data['thermal_conductivity']['Si NMOS channel'] #14.7e-9 #148e-9
        self.cond['SiO2'] = cond_data['thermal_conductivity']['SiO2'] #0.8e-9
        self.cond['spacer'] = cond_data['thermal_conductivity']['spacer'] #30e-9
        self.cond['contact'] = cond_data['thermal_conductivity']['contact'] #385e-9 # conductivity of copper
        self.cond_table =True;

    def quantize_values(self,val):
        val_x = math.ceil(val[0]/self.res_x) 
        val_y = math.ceil(val[1]/self.res_y)
        val_z = math.ceil(val[2]/self.res_z)
        return (val_x, val_y, val_z) 

    def create_box(self, origin, size, cond):
        assert isinstance(origin,tuple),"Origin expected type tuple but received type %s instead"%(type(origin))           
        assert len(origin) == 3, "Size expected a length of 3 for x y and z coordinates, user provided only %d values"%len(origin)
        assert isinstance(size,tuple),"Origin expected type tuple but received type %s instead"%(type(origin))           
        assert len(size) == 3, "Size expected a length of 3 for x y and z coordinates, user provided only %d values"%len(origin)
        
        (or_x, or_y, or_z) = self.quantize_values(origin)
        (sz_x, sz_y, sz_z) = self.quantize_values(size)

        assert or_x >= 0 and or_x < self.N_x,"Origin x coordinate out of bounds"
        assert or_y >= 0 and or_y < self.N_y,"Origin y coordinate out of bounds"
        assert or_z >= 0 and or_z < self.N_z,"Origin z coordinate out of bounds"

        assert sz_x > 0 and (or_x + sz_x - 1) < self.N_x,(
            "Size x coordinate out of bounds sz_x %d or_x %d"%(sz_x,or_x))
        assert sz_y > 0 and (or_y + sz_y - 1) < self.N_y,(
            "Size y coordinate out of bounds sz_y %d or_y %d N_y %d"%(sz_y,or_y,self.N_y))
        assert sz_z > 0 and (or_z + sz_z - 1) < self.N_z,(
            "Size z coordinate out of bounds sz_z %d or_z %d"%(sz_z,or_z))
        
        assert np.count_nonzero(self.C[or_x:(or_x + sz_x),or_y:(or_y +
            sz_y),or_z:(or_z + sz_z)]) == 0," Overlap with existing box,"+\
            " please check your dimensions and refer doc/UserGuide.md"
        self.C[or_x:(or_x + sz_x),or_y:(or_y + sz_y),or_z:(or_z + sz_z)] = cond
    
    def create_gate(self, origin, gate_width):
        #note gate width not to be confused with channel width
        assert self.parameters, "Set the device parameters before designing the layout"
        assert self.cond_table, "Set the conductivity table before designing the layout"
        sz_x = self.chnl_l
        sz_y = gate_width
        sz_z = self.gate_t
        cond = self.cond['gate']
        size = (sz_x,sz_y,sz_z)
        self.create_box(origin, size, cond)
        
    #TODO allow for separate conductivities for gaafet 
    def create_diffusion(self, origin, size, d_type='PMOS',finFET=0):
        assert self.cond_table, "Set the conductivity table before designing the layout"
        assert d_type == 'PMOS' or d_type == 'NMOS', "Diffusion type not recognized"
        if finFET == 1:
            if d_type == 'PMOS':
                cond = self.cond['Si PMOS fin']
            else:
                cond = self.cond['Si NMOS fin']
        else:
            if d_type == 'PMOS':
                cond = self.cond['Si PMOS SD']
            else:
                cond = self.cond['Si NMOS SD']
        self.create_box(origin, size, cond)

    def create_gate_oxide(self, origin, channel_width):
        assert self.parameters, "Set the device parameters before designing the layout"
        assert self.cond_table, "Set the conductivity table before designing the layout"
        sz_x = self.chnl_l
        sz_y = channel_width
        sz_z = self.t_ox
        size = (sz_x,sz_y,sz_z)
        cond = self.cond['SiO2']
        self.create_box(origin, size, cond)

    def create_channel(self, origin, channel_width, channel_depth, d_type='PMOS'):
        assert self.parameters, "Set the device parameters before designing the layout"
        assert self.cond_table, "Set the conductivity table before designing the layout"
        assert d_type == 'PMOS' or d_type == 'NMOS', "Diffusion type not recognized"
        sz_x = self.chnl_l
        sz_y = channel_width
        sz_z = channel_depth
        if d_type == 'PMOS':
            cond = self.cond['SiGe PMOS channel']
        else:
            cond = self.cond['Si NMOS channel'] 
        size = (sz_x, sz_y, sz_z)
        self.create_box(origin, size, cond)
        n_gate = self.n_gate
        self.gate_loc[n_gate] = {}
        self.gate_loc[n_gate]['origin'] = origin 
        self.gate_loc[n_gate]['size'] = size 
        (sz_x, sz_y, sz_z) = self.quantize_values(size)
        #TODO replace with actual power profile
        self.gate_loc[n_gate]['power_profile'] = np.ones((sz_x,sz_y,sz_z))/(sz_x*sz_y*sz_z) 
        self.n_gate = self.n_gate+1

    def create_t_box(self, origin, size):
        assert self.cond_table, "Set the conductivity table before designing the layout"
        cond = self.cond['SiO2']
        self.create_box(origin, size, cond)

    def create_substrate(self, thickness):
        assert self.cond_table, "Set the conductivity table before designing the layout"
        origin = (0, 0, 0)
        sz_x = self.sz_x
        sz_y = self.sz_y
        sz_z = thickness
        size = (sz_x, sz_y, sz_z)
        cond = self.cond['Si substrate']
        self.create_box(origin, size, cond)
        
    def create_contact_short(self, origin, size):
        assert self.cond_table, "Set the conductivity table before designing the layout"
        cond = self.cond['contact']
        self.create_box(origin, size, cond)

    def create_contact(self, origin, size):
        assert self.cond_table, "Set the conductivity table before designing the layout"
        cond = self.cond['contact']
        self.create_box(origin, size, cond)
        (or_x, or_y, or_z) = self.quantize_values(origin)
        (sz_x, sz_y, sz_z) = self.quantize_values(size)

        assert or_x >= 0 and or_x < self.N_x,"Origin x coordinate out of bounds"
        assert or_y >= 0 and or_y < self.N_y,"Origin y coordinate out of bounds"
        assert sz_x > 0 and (or_x + sz_x - 1) < self.N_x,(
            "Size x coordinate out of bounds sz_x %d or_x %d"%(sz_x,or_x))
        assert sz_y > 0 and (or_y + sz_y - 1) < self.N_y,(
            "Size y coordinate out of bounds sz_y %d or_y %d N_y %d"%(sz_y,or_y,self.N_y))
        assert np.count_nonzero(self.contact_mask[or_x:(or_x + sz_x),or_y:(or_y + sz_y)]) == 0," Overlap with existing box"

        self.contact_mask[or_x:(or_x + sz_x),or_y:(or_y + sz_y)] = 1

    #assigns any node not already assigned to t_box
    def filler(self): 
        assert self.cond_table, "Set the conductivity table before designing the layout"
        cond = self.cond['SiO2']
        self.C[self.C == 0] = cond

    def create_G(self):
        for k in range(0,self.N_z):
            for j in range(0,self.N_y):
                for i in range(0,self.N_x):
                    cur_node = self.G_index(i,j,k)
                    #+ve x
                    next_node = self.G_index(i+1,j,k)
                    if next_node >= 0:
                        cond = (self.res_y*self.res_z/self.res_x) * (self.C[i,j,k]+self.C[i+1,j,k])/2
                        self.G[cur_node,next_node] = - cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    #-ve x
                    next_node = self.G_index(i-1,j,k)
                    if next_node >= 0:
                        cond = (self.res_y*self.res_z/self.res_x) * (self.C[i,j,k]+self.C[i-1,j,k])/2
                        self.G[cur_node,next_node] = -cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    #+ve y
                    next_node = self.G_index(i,j+1,k)
                    if next_node >= 0:
                        cond = (self.res_x*self.res_z/self.res_y) * (self.C[i,j,k]+self.C[i,j+1,k])/2
                        self.G[cur_node,next_node] = - cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    #-ve y
                    next_node = self.G_index(i,j-1,k)
                    if next_node >= 0:
                        cond = (self.res_x*self.res_z/self.res_y) * (self.C[i,j,k]+self.C[i,j-1,k])/2
                        self.G[cur_node,next_node] = - cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    #+ve z
                    next_node = self.G_index(i,j,k+1)
                    if next_node >= 0:
                        cond = (self.res_x*self.res_y/self.res_z) * (self.C[i,j,k]+self.C[i,j,k+1])/2
                        self.G[cur_node,next_node] = - cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    else: #handle the case of contact to above
                        if self.contact_mask[i,j]: #location of a contact in the top plane
                            cond = (self.res_x*self.res_y/self.t_cnt2gnd) * self.C[i,j,k]
                            self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond                        
                    #-ve z
                    next_node = self.G_index(i,j,k-1)
                    if next_node >= 0:
                        cond = (self.res_x*self.res_y/self.res_z) * (self.C[i,j,k]+self.C[i,j,k-1])/2
                        self.G[cur_node,next_node] = -cond
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond
                    else: 
                    # if it is the lowermost layer we add a resistance to the ground
                    # for conduction 
                        cond = (self.res_x*self.res_y/self.t_sub2gnd) * self.C[i,j,k]
                        self.G[cur_node,cur_node] = self.G[cur_node,cur_node]+ cond                        
                    
    def create_P(self,active_gates,power):
        # active gates is list type and contains all the gates you like to
        # distribute power across
        assert isinstance(active_gates,list),"active_gates expected type list but received type %s instead"%(type(active_gates)) 
        pwr = np.zeros((self.N_x,self.N_y,self.N_z))
        #TODO modify so that it reuse the create box function
        for gate in active_gates:
            #TODO modify if you require uneven distribution between gates
            pwr_gate = power/len(active_gates)
            if self.n_fin == 0:
                origin = self.gate_loc[gate]['origin']
                size = self.gate_loc[gate]['size']
                power_profile = self.gate_loc[gate]['power_profile']
                (or_x, or_y, or_z) = self.quantize_values(origin)
                (sz_x, sz_y, sz_z) = self.quantize_values(size)
                pwr[or_x:(or_x + sz_x),or_y:(or_y + sz_y),or_z:(or_z + sz_z)] = power_profile*pwr_gate 
            else:
                for n in range(self.n_fin):
                    pwr_fin = pwr_gate/self.n_fin
                    gate_num =  gate*self.n_fin + n
                    origin = self.gate_loc[gate_num]['origin']
                    size = self.gate_loc[gate_num]['size']
                    power_profile = self.gate_loc[gate_num]['power_profile']
                    (or_x, or_y, or_z) = self.quantize_values(origin)
                    (sz_x, sz_y, sz_z) = self.quantize_values(size)
                    pwr[or_x:(or_x + sz_x),or_y:(or_y + sz_y),or_z:(or_z + sz_z)] = power_profile*pwr_fin 
        self.P = pwr.reshape((self.N_x*self.N_y*self.N_z,1),order='F') #fortran ordering to index x first then y then z
        
                    
    def G_index(self,i,j,k):
        if (i < 0 or i >= self.N_x or
            j < 0 or j >= self.N_y or
            k < 0 or k >= self.N_z ):
            return -1
        else:
            return self.N_x * self.N_y * k + j* self.N_x + i 
