#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import time
import math
import json
import argparse
import numpy as np
import scipy.sparse as sparse_mat
import scipy.sparse.linalg as sparse_algebra
from pprint import pprint

from thermal_model import thermal_model

#direction convention  
#length is along x Dimesion 0
#width  is along y Dimension 1
#height is along z Dimension 2

#TODO right now resx and resy have to be the same

def quant(a,reso):
    return math.ceil(a/reso)*reso


def load_json(json_file):
       with open(json_file) as f:
           json_data = json.load(f)
       return json_data

tool_config = load_json('./input/tool_config.json')
model_param = load_json('./input/model_parameters.json')

parser = argparse.ArgumentParser(description="Find the temperature rise to self-heating")
parser.add_argument("-tech", choices= ['Bulk','SOI'],
                    help="Provide technology name", required = True)
parser.add_argument("-n_gate", type=int, choices= [0,1,2,3,4,5,6,7,8,9,10],
                    help="Provide number of gates", required = True)
parser.add_argument("-width", type=float, 
                    help="Provide width in nm", required = True)
parser.add_argument("-type",  choices= ['NMOS','PMOS'],
                    help="Provide trasistor type", required = True)
parser.add_argument("-power", type=float, 
                    help="Provide the total power dissipated")
parser.add_argument("-active", "--active", 
                    help="Provide list of active gates in quotes seperated by comma delimiter", required = True)
args = parser.parse_args()

w_chnl = args.width
n_gate = args.n_gate
power = args.power
#a_gates = args.active # active gates
a_gates = [int(item)for item in args.active.split(',')]
print(a_gates)

TECH = args.tech #'BULK' #SOI BULK 
MOS = args.type  # NMOS or PMOS

# properties
l_chnl = model_param["dimensions"]["l_chnl"]
t_gate = model_param["dimensions"]["t_gate"]
#design dimensions
t_substrate = model_param["dimensions"]["t_substrate"] #thickness of substrate that has been modelled for after the point at which it is
t_box  = model_param["dimensions"]["t_box"] #25  # thickness of box layer
t_chnl = model_param["dimensions"]["t_chnl"] #6   # thickness of channel, source and drain diffusions
t_gox  = model_param["dimensions"]["t_gox"] #1   # thickness of gate oxide
t_diff_ext = model_param["dimensions"]["t_diff_ext"] #20 # height of the diffusion extension above the diffusion


e_gate  = model_param["dimensions"]["e_gate"] #10  # extension of gate out of diffusion
l_diff  =  model_param["dimensions"]["l_diff"] #35 # lenght of source and drain diffusion
l_diff_ext = model_param["dimensions"]["l_diff_ext"] #25 # length of the source and drain diffusion extension


l_cont = model_param["dimensions"]["l_cont"] #10 #length of contact
w_cont = model_param["dimensions"]["w_cont"] #10 #width of contact



res = tool_config["resolution"]
t_sub2gnd = tool_config["t_sub2gnd"] #475 # thickness of substrate to ground not represented in node
t_cnt2gnd = tool_config["t_cnt2gnd"] #1000 # distance from contact to ground
l_sp_diff_ext = tool_config["l_sp_diff_ext"] #5 # spacing between gate and either edge
sp_edge   = tool_config["sp_edge"] #5   # spacing to the edges
t_sp_edge = tool_config["t_sp_edge"] #20   # spacing to the edges

resx=res[0]
resy=res[1]
resz=res[2]

w_chnl  = quant(w_chnl,resy)
l_chnl  = quant(l_chnl,resx)
t_gate  = quant(t_gate,resz)
t_box   = quant(t_box,resz)
t_chnl  = quant(t_chnl,resz)
t_gox   = quant(t_gox,resz)
sp_edge = quant(sp_edge,resx) #TODO x and y 
t_sp_edge = quant(sp_edge,resz)
e_gate  = quant(e_gate,resy) 
l_diff  = quant(l_diff,resx)
t_substrate = quant(t_substrate,resz)
l_diff_ext= quant(l_diff_ext,resx)
t_diff_ext = quant(t_diff_ext,resz)
l_sp_diff_ext = quant(l_sp_diff_ext,resx)
l_cont = quant(l_cont,resx)
w_cont = quant(w_cont,resy)
# t_sub2gnd and t_cnt2gnd do not need quatization as there are not used in mask

assert TECH =='SOI' or TECH == 'BULK',"Undefined TECH type"

length = 2*sp_edge + l_diff + n_gate*(l_chnl+l_diff)
width = 2*(sp_edge+ e_gate) + w_chnl
height = t_substrate + t_box + t_chnl + t_sp_edge + max(t_gox + t_gate,t_diff_ext)

print("INFO: Model Dimensions: %4.3f %4.3f %4.3f"%(length,width,height))
print("INFO: Resolution : %4.3e %4.3e %4.3e"%(resx,resy,resz))

nmos = thermal_model(
            length = length, 
            width = width, 
            height = height, 
            resolution = res
            )
      
nmos.set_device_parameters(  
                           channel_length = l_chnl, 
                           gate_thickness = t_gate,
                           substrate2ground = t_sub2gnd,
                           contact2ground = t_cnt2gnd,
                           gate_oxide_thickness = t_gox 
                           )
                           
nmos.set_conductivity_table()

#bottom up approach to building
#substrate
if TECH == 'SOI':
    nmos.create_substrate(thickness = t_substrate)
#t_box
    or_z = t_substrate
    origin = (0,0,or_z)
    size = (length,width,t_box)
    nmos.create_t_box( origin, size)   

    or_z = or_z + t_box
elif TECH == 'BULK':
    nmos.create_substrate(thickness = (t_substrate+t_box))
    or_z = t_substrate + t_box
    
    #create channel source and drain diffusions
sz_z = t_chnl
or_y = sp_edge+ e_gate
sz_y = w_chnl

    #source diffusion
or_x = sp_edge
sz_x = l_diff
origin = (or_x, or_y, or_z)
size = (sz_x,sz_y,sz_z)
nmos.create_diffusion( origin, size, MOS)

for n in range(n_gate):
    #channel
    or_x = or_x + sz_x
    or_y = sp_edge+ e_gate
    origin = (or_x, or_y, or_z)
    nmos.create_channel( origin=origin, channel_width=sz_y, channel_depth=sz_z, d_type=MOS)
    
    # drain diffusion
    or_x = or_x + l_chnl
    sz_x = l_diff
    origin = (or_x, or_y, or_z)
    size = (sz_x,sz_y,sz_z)
    nmos.create_diffusion( origin, size, MOS)
    
#gate oxide 
or_z = or_z + t_chnl
or_y = sp_edge+ e_gate
sz_y = w_chnl

for n in range(n_gate):    
    or_x = sp_edge + l_diff + n*(l_diff+l_chnl)
    origin = (or_x, or_y, or_z)
    nmos.create_gate_oxide(origin=origin, channel_width=sz_y)
    
#source and drain extensions
or_z = or_z 
sz_z = t_diff_ext
or_y = sp_edge + e_gate   
sz_y = w_chnl

#source extension
or_x = sp_edge+l_sp_diff_ext
sz_x = l_diff_ext
origin = (or_x, or_y, or_z)
size = (sz_x, sz_y, sz_z)
nmos.create_diffusion( origin, size, MOS)

#create contact
c_or_x = or_x+(sz_x/2)-(l_cont/2) 
c_sz_x = l_cont
c_or_y = or_y+(sz_y/2)-(w_cont/2) 
c_sz_y = w_cont
c_or_z = or_z + sz_z
c_sz_z = height - c_or_z
c_origin = (c_or_x, c_or_y, c_or_z)
c_size = (c_sz_x, c_sz_y, c_sz_z)
nmos.create_contact( c_origin, c_size)
    
for n in range(n_gate):
    or_x = sp_edge + (n+1)*(l_diff + l_chnl)+  l_sp_diff_ext
    origin = (or_x, or_y, or_z)
    nmos.create_diffusion(origin, size,MOS)
    #SD contact
    c_or_x = or_x+(sz_x/2)-(l_cont/2) 
    c_origin = (c_or_x, c_or_y, c_or_z)
    nmos.create_contact( c_origin, c_size)

or_z = or_z + t_gox
or_y = sp_edge
sz_x = l_chnl
sz_y = 2*e_gate + w_chnl
sz_z = t_gate

c_sz_x = l_cont
c_or_y = or_y+(sz_y/2)-(w_cont/2) 
c_sz_y = w_cont
c_or_z = or_z + sz_z
c_sz_z = height - c_or_z
c_size = (c_sz_x, c_sz_y, c_sz_z)

#gate 
for n in range(n_gate):
    or_x = sp_edge + l_diff + n*(l_diff+l_chnl)
    
    origin = (or_x, or_y, or_z)
    nmos.create_gate(origin, gate_width=sz_y)
    #gate contact
    c_or_x = or_x+(sz_x/2)-(l_cont/2) 
    c_origin = (c_or_x, c_or_y, c_or_z)
    nmos.create_contact( c_origin, c_size)

# fill any unfilled areas
nmos.filler()

print("INFO: Completed layout drawing")
print("INFO: Beginning G matrix creation")
# create G matrix
s1 = time.time()
nmos.create_G()
e1 = time.time()
print("INFO: Completed G matrix in %e"%(e1-s1))
s1=time.time()
nmos.create_P(a_gates,power)
e1 = time.time()
print("INFO: Completed P matrix in %e"%(e1-s1))


#solve the equations
G = nmos.G.tocsc()
P = sparse_mat.csc_matrix(nmos.P)
I = sparse_mat.identity(G.shape[0]) * 1e-13
G = G + I
print("INFO: Size of matrix %d x %d"%G.shape)
print("INFO: Number of Non zeros %d"%G.nnz)
print("INFO: Solving for temperature")
s1=time.time()
T = sparse_algebra.spsolve(G, P, permc_spec=None, use_umfpack=True)
e1=time.time()

print("INFO: Completed solving in %e"%(e1-s1))
np.savetxt('./output/T.out',T)
np.savetxt('./work/T.out',T)


print("Result: Max temperature rise:%e"%(max(T)))
print("Result: Minimum temperature rise: %e"%(min(T)))
print("Result: Average temperature rise: %e"%(np.average(T)))
T= T.reshape((nmos.N_x,nmos.N_y,nmos.N_z),order='F')
print("\n")

data2save = np.array([[resx,resy,resz],[length,width,height]])
np.savetxt('./work/device_parameters.csv',data2save,'%5.4e',',')

