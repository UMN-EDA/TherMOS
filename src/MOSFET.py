#BSD 3-Clause License
#
#Copyright (c) 2019, The Regents of the University of Minnesota
#
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#* Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#* Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#* Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author = Vidya A Chhabria
"""

import time
import math
import json
import argparse
import numpy as np
import scipy.sparse as sparse_mat
import scipy.sparse.linalg as sparse_algebra
from thermalModel import thermalModel

#direction convention
#length is along x Dimesion 0
#width  is along y Dimension 1
#height is along z Dimension 2


class MOSFET:
    def __init__(self, TECH, MOS, n_gate, width, f_model_param, f_tool_config):
        self.TECH = TECH
        self.MOS = MOS
        self.n_gate = n_gate
        self.w_chnl = width
        self.initialize(f_tool_config, f_model_param)
        self.create_model()

    def quant(self, a, reso):
        return math.ceil(a / reso) * reso

    def load_json(self, json_file):
        with open(json_file) as f:
            json_data = json.load(f)
        return json_data

    def initialize(self, file_tool_config, file_model_param):

        tool_config = self.load_json(file_tool_config)
        model_param = self.load_json(file_model_param)

        # properties
        l_chnl = model_param["dimensions"]["l_chnl"]
        t_gate = model_param["dimensions"]["t_gate"]

        #design dimensions
        #thickness of substrate that has been modelled
        #after the value defined in tool_config.json
        t_substrate = model_param["dimensions"]["t_substrate"]
        t_box = model_param["dimensions"][
            "t_box"]  #25  # thickness of box layer
        # thickness of channel, source and drain diffusions
        t_chnl = model_param["dimensions"]["t_chnl"]  #6
        t_gox = model_param["dimensions"][
            "t_gox"]  #1   # thickness of gate oxide
        # height of the diffusion extension above the diffusion
        t_diff_ext = model_param["dimensions"]["t_diff_ext"]  #20
        l_sd_junc = model_param["dimensions"]["l_sd_junc"]

        e_gate = model_param["dimensions"][
            "e_gate"]  #10  # extension of gate out of diffusion
        l_gate_space = model_param["dimensions"][
            "l_gate_space"]  #35 # lenght of source and drain diffusion
        l_diff_ext = model_param["dimensions"][
            "l_diff_ext"]  #25 # length of the source and drain diffusion extn

        l_cont = model_param["dimensions"]["l_cont"]  #10 #length of contact
        w_cont = model_param["dimensions"]["w_cont"]  #10 #width of contact

        self.res = tool_config["resolution"]
        l_sp_diff_ext = tool_config[
            "l_sp_diff_ext"]  #5 # spacing between gate and either edge
        sp_edge = tool_config["sp_edge"]  #5   # spacing to the edges
        t_sp_edge = tool_config["t_sp_edge"]  #20 # spacing to the edges

        # thickness of substrate to ground not represented in node
        self.t_sub2gnd = tool_config["t_sub2gnd"]  #475
        self.t_cnt2gnd = tool_config[
            "t_cnt2gnd"]  #1000 # distance from contact to ground

        resx = self.res[0]
        resy = self.res[1]
        resz = self.res[2]
        self.resx = resx
        self.resy = resy
        self.resz = resz

        self.w_chnl = self.quant(self.w_chnl, resy)
        self.l_chnl = self.quant(l_chnl, resx)
        self.t_gate = self.quant(t_gate, resz)
        self.t_box = self.quant(t_box, resz)
        self.t_chnl = self.quant(t_chnl, resz)
        self.t_gox = self.quant(t_gox, resz)
        self.l_sp_edge = self.quant(sp_edge, resx)
        self.w_sp_edge = self.quant(sp_edge, resy)
        self.t_sp_edge = self.quant(t_sp_edge, resz)
        self.e_gate = self.quant(e_gate, resy)
        self.l_gate_space = self.quant(l_gate_space, resx)
        self.t_substrate = self.quant(t_substrate, resz)
        self.l_diff_ext = self.quant(l_diff_ext, resx)
        self.t_diff_ext = self.quant(t_diff_ext, resz)
        self.l_sp_diff_ext = self.quant(l_sp_diff_ext, resx)
        self.l_cont = self.quant(l_cont, resx)
        self.w_cont = self.quant(w_cont, resy)
        self.l_sd_junc = self.quant(l_sd_junc, resx)

        # t_sub2gnd and t_cnt2gnd do not need quatization as
        # there are not used in mask

        assert self.TECH == 'SOI' or self.TECH == 'Bulk', "Undefined TECH type"

        self.length = 2*self.l_sp_edge + 2*self.l_sd_junc +\
            self.n_gate*self.l_chnl+(self.n_gate-1)*l_gate_space
        self.width = 2 * (self.w_sp_edge + self.e_gate) + self.w_chnl
        self.height = self.t_substrate + self.t_box + self.t_chnl +\
            self.t_sp_edge + max(self.t_gox + self.t_gate, self.t_diff_ext)

        print("INFO: Model Dimensions: %4.3f %4.3f %4.3f"%(\
                self.length, self.width, self.height))
        print("INFO: Resolution : %4.3e %4.3e %4.3e" % (resx, resy, resz))

        self.device = thermalModel(length=self.length,
                                   width=self.width,
                                   height=self.height,
                                   resolution=self.res)

        self.device.set_device_parameters(channel_length=self.l_chnl,
                                          gate_thickness=self.t_gate,
                                          substrate2ground=self.t_sub2gnd,
                                          contact2ground=self.t_cnt2gnd,
                                          gate_oxide_thickness=self.t_gox)

        self.device.set_conductivity_table(file_model_param)
        print("INFO: Initialization complete")


#bottom up approach to building

    def create_substrate(self):
        #substrate
        if self.TECH == 'SOI':
            self.device.create_substrate(thickness=self.t_substrate)
            #t_box
            or_z = self.t_substrate
            origin = (0, 0, or_z)
            size = (self.length, self.width, self.t_box)
            self.device.create_t_box(origin, size)

            or_z = or_z + self.t_box
        elif self.TECH == 'Bulk':
            self.device.create_substrate(thickness=(self.t_substrate +
                                                    self.t_box))
            or_z = self.t_substrate + self.t_box
        return or_z

    def create_SD_junction(self, or_x, or_z):
        #create channel source and drain diffusions
        or_y = self.w_sp_edge + self.e_gate
        sz_x = self.l_sd_junc
        sz_y = self.w_chnl
        sz_z = self.t_chnl
        origin = (or_x, or_y, or_z)
        size = (sz_x, sz_y, sz_z)
        #print("origin size SD Junc")
        #pprint(origin)
        #pprint(size)
        self.device.create_diffusion(origin, size, self.MOS)
        return or_x + sz_x, or_z + sz_z

    def create_channel(self, or_x_in, or_z_in):
        or_y = self.w_sp_edge + self.e_gate
        or_z = or_z_in
        sz_y = self.w_chnl
        sz_z = self.t_chnl
        for n in range(self.n_gate):
            #channel
            or_x = or_x_in + n * (self.l_chnl + self.l_gate_space)
            #print("or_x %d"%or_x )
            origin = (or_x, or_y, or_z)
            self.device.create_channel(origin=origin,
                                       channel_width=sz_y,
                                       channel_depth=sz_z,
                                       d_type=self.MOS)

            if n < self.n_gate - 1:
                # drain diffusion
                or_x = or_x + self.l_chnl
                sz_x = self.l_gate_space
                origin = (or_x, or_y, or_z)
                size = (sz_x, sz_y, sz_z)
                #print("origin size SD diff")
                #pprint(origin)
                #pprint(size)
                self.device.create_diffusion(origin, size, self.MOS)
        end_x = or_x + self.l_chnl
        end_z = or_z + sz_z
        return end_x, end_z

    def create_gate_oxide(self, or_x_in, or_z_in):
        #gate oxide
        or_z = or_z_in
        or_y = self.w_sp_edge + self.e_gate
        sz_y = self.w_chnl

        for n in range(self.n_gate):
            or_x = or_x_in + self.l_sd_junc + n * (self.l_gate_space +
                                                   self.l_chnl)
            origin = (or_x, or_y, or_z)
            #print("origin size gox")
            #pprint(origin)
            #size = (self.l_chnl,sz_y,self.t_gox)
            #pprint(size)
            self.device.create_gate_oxide(origin=origin, channel_width=sz_y)
        return or_x + self.l_chnl, or_z + self.t_gox

    def create_SD_contact(self, or_x_in, or_z_in):
        #source and drain extensions
        or_z = or_z_in
        sz_z = self.t_diff_ext
        or_y = self.w_sp_edge + self.e_gate
        sz_y = self.w_chnl

        #source extension
        or_x = or_x_in + self.l_sd_junc / 2 - self.l_diff_ext / 2
        sz_x = self.l_diff_ext
        origin = (or_x, or_y, or_z)
        size = (sz_x, sz_y, sz_z)
        #print("origin size SD Contact")
        #pprint(origin)
        #pprint(size)
        self.device.create_diffusion(origin, size, self.MOS)
        #create contact
        c_or_x = or_x + (sz_x / 2) - (self.l_cont / 2)
        c_sz_x = self.l_cont
        c_or_y = or_y + (sz_y / 2) - (self.w_cont / 2)
        c_sz_y = self.w_cont
        c_or_z = or_z + sz_z
        c_sz_z = self.height - c_or_z
        c_origin = (c_or_x, c_or_y, c_or_z)
        c_size = (c_sz_x, c_sz_y, c_sz_z)
        self.device.create_contact(c_origin, c_size)
        for n in range(self.n_gate - 1):
            #sd extension
            or_x = or_x_in + self.l_sd_junc +\
                n*(self.l_gate_space+ self.l_chnl) +\
                self.l_chnl + self.l_gate_space/2 - self.l_diff_ext/2
            origin = (or_x, or_y, or_z)
            self.device.create_diffusion(origin, size, self.MOS)
            #SD contact
            c_or_x = or_x + (sz_x / 2) - (self.l_cont / 2)
            c_origin = (c_or_x, c_or_y, c_or_z)
            self.device.create_contact(c_origin, c_size)
        #drain extension
        or_x = or_x_in + self.l_sd_junc + \
            (self.n_gate-1)*(self.l_gate_space+ self.l_chnl) +\
            self.l_chnl + self.l_sd_junc/2 - self.l_diff_ext/2
        origin = (or_x, or_y, or_z)
        self.device.create_diffusion(origin, size, self.MOS)
        #SD contact
        c_or_x = or_x + (sz_x / 2) - (self.l_cont / 2)
        c_origin = (c_or_x, c_or_y, c_or_z)
        self.device.create_contact(c_origin, c_size)

    def create_gate(self, or_x_in, or_z):
        or_y = self.w_sp_edge
        sz_x = self.l_chnl
        sz_y = 2 * self.e_gate + self.w_chnl
        sz_z = self.t_gate

        c_sz_x = self.l_cont
        c_or_y = or_y + (sz_y / 2) - (self.w_cont / 2)
        c_sz_y = self.w_cont
        c_or_z = or_z + sz_z
        c_sz_z = self.height - c_or_z
        c_size = (c_sz_x, c_sz_y, c_sz_z)
        #gate
        for n in range(self.n_gate):
            or_x = or_x_in + self.l_sd_junc + n * (self.l_gate_space +
                                                   self.l_chnl)
            origin = (or_x, or_y, or_z)
            self.device.create_gate(origin, gate_width=sz_y)
            #gate contact
            c_or_x = or_x + (sz_x / 2) - (self.l_cont / 2)
            c_origin = (c_or_x, c_or_y, c_or_z)
            self.device.create_contact(c_origin, c_size)

    def create_model(self):
        or_z = self.create_substrate()
        or_x = self.l_sp_edge
        or_x_sd1, or_z_sd1 = self.create_SD_junction(or_x, or_z)
        or_x = or_x_sd1
        or_x, or_z_chl = self.create_channel(or_x, or_z)
        _, or_z = self.create_SD_junction(or_x, or_z)
        assert or_z == or_z_sd1 and or_z == or_z_chl, "Confirm t in code."
        or_x = self.l_sp_edge
        _, or_z_gate = self.create_gate_oxide(or_x, or_z)
        self.create_SD_contact(or_x, or_z)
        self.create_gate(or_x, or_z_gate)
        self.device.filler()
        print("INFO: Completed layout drawing")

    def create_equations(self, a_gates, power):
        print("INFO: Beginning G matrix creation")
        # create G matrix
        s1 = time.time()
        self.device.create_G()
        e1 = time.time()
        print("INFO: Completed G matrix in %e" % (e1 - s1))
        s1 = time.time()
        self.device.create_P(a_gates, power)
        e1 = time.time()
        print("INFO: Completed P matrix in %e" % (e1 - s1))

    def solve(self):
        #solve the equations
        G = self.device.G.tocsc()
        P = sparse_mat.csc_matrix(self.device.P)
        I = sparse_mat.identity(G.shape[0]) * 1e-13
        G = G + I
        print("INFO: Size of matrix %d x %d" % G.shape)
        print("INFO: Number of Non zeros %d" % G.nnz)
        print("INFO: Solving for temperature")
        s1 = time.time()
        T = sparse_algebra.spsolve(G, P, permc_spec=None, use_umfpack=True)
        e1 = time.time()

        print("INFO: Completed solving in %e" % (e1 - s1))
        np.savetxt('./output/T.out', T)
        np.savetxt('./work/T.out', T)

        print("Result: Max temperature rise:%e" % (max(T)))
        print("Result: Minimum temperature rise: %e" % (min(T)))
        print("Result: Average temperature rise: %e" % (np.average(T)))
        T = T.reshape((self.device.N_x, self.device.N_y, self.device.N_z),
                      order='F')

    def save_model(self):
        C = self.device.C.reshape((-1), order='f')
        np.savetxt('./work/C.out', C)
        print("\n")

        data2save = np.array([[self.resx, self.resy, self.resz],
                              [self.length, self.width, self.height]])
        np.savetxt('./work/device_parameters.csv', data2save, '%5.4e', ',')


def main():
    f_model_param = "input/model_parameters_FinFET.json"
    f_tool_config = "input/tool_config.json"
    parser = argparse.ArgumentParser(
        description="Find the temperature rise to self-heating")
    parser.add_argument("-tech",
                        choices=['Bulk', 'SOI'],
                        help="Provide technology name",
                        required=True)
    parser.add_argument("-n_gate",
                        type=int,
                        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        help="Provide number of gates",
                        required=True)
    parser.add_argument("-width",
                        type=float,
                        help="Provide width in nm",
                        required=True)
    parser.add_argument("-type",
                        choices=['NMOS', 'PMOS'],
                        help="Provide trasistor type",
                        required=True)
    parser.add_argument("-power",
                        type=float,
                        help="Provide the total power dissipated",
                        required=True)
    parser.add_argument(
        "-active",
        "--active",
        help=
        "Provide list of active gates in quotes seperated by comma delimiter",
        required=True)
    args = parser.parse_args()

    w_chnl = args.width
    n_gate = args.n_gate
    power = args.power
    #a_gates = args.active # active gates
    a_gates = [int(item) for item in args.active.split(',')]
    print(a_gates)

    TECH = args.tech  #'Bulk' #SOI Bulk
    MOS = args.type  # NMOS or PMOS
    SH_PL = MOSFET(TECH, MOS, n_gate, w_chnl, f_model_param, f_tool_config)
    SH_PL.create_equations(a_gates, power)
    SH_PL.solve()
    SH_PL.save_model()
    print("\n")


if __name__ == '__main__':
    main()
