#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import argparse
import re
import sys
from FinFET import FinFET
from MOSFET import MOSFET
from tempSolve import tempSolve
import thermalModel

def main():
    header()
    f_model_param_finfet = './input/model_parameters_FinFET.json'
    f_tool_config = './input/tool_config.json'
    f_model_param_mosfet = './input/model_parameters_MOSFET.json'

    parser = argparse.ArgumentParser(description="Find the temperature rise due to self-heating")
    subparsers = parser.add_subparsers(help = 'Choose a process, Either Bulk_MOSFET or SOI_MOSFET or Bulk_FinFET or SOI_FinFET')
    MOSFET_Bulk_parser = subparsers.add_parser ('Bulk_MOSFET')
    MOSFET_SOI_parser = subparsers.add_parser ('SOI_MOSFET')
    FinFET_Bulk_parser = subparsers.add_parser ('Bulk_FinFET')
    FinFET_SOI_parser = subparsers.add_parser ('SOI_FinFET')
    
    MOSFET_Bulk_parser.add_argument("-device_type",  choices= ['NMOS','PMOS'],
                        help="Provide trasistor type", required = True)
    MOSFET_SOI_parser.add_argument("-device_type",  choices= ['NMOS','PMOS'],
                        help="Provide trasistor type", required = True)
    FinFET_Bulk_parser.add_argument("-device_type",  choices= ['NMOS','PMOS'],
                        help="Provide trasistor type", required = True)
    FinFET_SOI_parser.add_argument("-device_type",  choices= ['NMOS','PMOS'],
                        help="Provide trasistor type", required = True)
    
    MOSFET_Bulk_parser.add_argument("-n_gate", type=int, choices= [1,2,3,4,5,6,7,8,9,10],
                                    help="Provide number of gates", required = True)
    MOSFET_SOI_parser.add_argument("-n_gate", type=int, choices= [1,2,3,4,5,6,7,8,9,10],
                                    help="Provide number of gates", required = True)
    FinFET_Bulk_parser.add_argument("-n_gate", type=int, choices= [1,2,3,4,5,6,7,8,9,10],
                                    help="Provide number of gates", required = True)
    FinFET_SOI_parser.add_argument("-n_gate", type=int, choices= [1,2,3,4,5,6,7,8,9,10],
                        help="Provide number of gates", required = True)

    MOSFET_Bulk_parser.add_argument("-power", type=float, 
                                    help="Provide the total power dissipated in W", required = True)
    MOSFET_SOI_parser.add_argument("-power", type=float, 
                                    help="Provide the total power dissipated in W", required = True)
    FinFET_Bulk_parser.add_argument("-power", type=float, 
                                    help="Provide the total power dissipated in W", required = True)
    FinFET_SOI_parser.add_argument("-power", type=float, 
                        help="Provide the total power dissipated in W", required = True)
    
    MOSFET_Bulk_parser.add_argument("-active", "--active", 
                                    help="Provide list of active gates in quotes seperated by comma delimiter", required =False )
    MOSFET_SOI_parser.add_argument("-active", "--active", 
                                    help="Provide list of active gates in quotes seperated by comma delimiter", required=False )
    FinFET_Bulk_parser.add_argument("-active", "--active", 
                                    help="Provide list of active gates in quotes seperated by comma delimiter", required =False )
    FinFET_SOI_parser.add_argument("-active", "--active", 
                                    help="Provide list of active gates in quotes seperated by comma delimiter", required = False)
    



    MOSFET_Bulk_parser.add_argument("-percent", "--percent", 
                                    help="Provide list of percentage of power distributed in active gates in quotes seperated by comma delimiter", required =False )
    MOSFET_SOI_parser.add_argument("-percent", "--percent", 
                                    help="Provide list of percentage of power distributed in active gates in quotes seperated by comma delimiter", required =False )
    FinFET_Bulk_parser.add_argument("-percent", "--percent", 
                                    help="Provide list of percentage of power  distributed in active gates in quotes seperated by comma delimiter", required =False )
    FinFET_SOI_parser.add_argument("-percent", "--percent", 
                                    help="Provide list of percentage of power distributed in active gates in quotes seperated by comma delimiter", required =False )


    MOSFET_Bulk_parser.add_argument("-width", type = float,  
                        help= "Provide width in nm for MOSFET", required = True)
    MOSFET_SOI_parser.add_argument("-width", type = float,  
                        help= "Provide width in nm for MOSFET", required = True)
    FinFET_Bulk_parser.add_argument("-n_fin", type = int,  choices= [1,2,3,4,5,6,7,8,9,10],
                        help= "Provide number of fins", required = True)
    FinFET_SOI_parser.add_argument("-n_fin", type = int,  choices= [1,2,3,4,5,6,7,8,9,10],
                        help= "Provide numberof fins", required = True)

    args = parser.parse_args()
    n_gate = args.n_gate
    power = args.power
    #percent = args.percent
    if(args.active):
        a_gates = [int(item)for item in args.active.split(',')]
        print(a_gates)
    else:
        a_gates = []
        for val in range(n_gate):
            a_gates.append(val)
        print(a_gates)


    if(args.percent):
        percent = [float(item) for item in args.percent.split(',')]
        print(percent)
    else:
        percent = []
        for val in range(n_gate):
            percent.append(100/n_gate)
        print(percent)
    
    MOS = args.device_type  # NMOS or PMOS
    if (sys.argv[1] == "Bulk_MOSFET"):
        w_chnl = args.width
        device_model = MOSFET('Bulk', MOS, n_gate, w_chnl, f_model_param_mosfet,f_tool_config )
    elif (sys.argv[1]  == "SOI_MOSFET"):
        w_chnl = args.width
        device_model = MOSFET('SOI', MOS, n_gate, w_chnl, f_model_param_mosfet,f_tool_config )
    elif (sys.argv[1] == "Bulk_FinFET"):
        n_fin = args.n_fin
        device_model = FinFET('Bulk', MOS, n_gate, n_fin, f_model_param_finfet,f_tool_config )
    elif (sys.argv[1] == "SOI_FinFET"):
        n_fin = args.n_fin
        device_model = FinFET('SOI', MOS, n_gate, n_fin, f_model_param_finfet,f_tool_config )
    else:
        device_model = NULL
        print("Device model not created. Neither MOSFET nor FinFET")
    device_model.save_model()
    temp_sol = tempSolve(device_model.device)
    temp_sol.create_equations(device_model.device, a_gates,power, percent)
    temp_sol.solve(device_model.device)
    print("\n")

def header():
    print("               )     (      *       )  (")     
    print("  *   ) ( /(     )\ ) (  `   ( /(  )\ ) ") 
    print("` )  /( )\())(  (()/( )\))(  )\())(()/( ") 
    print(" ( )(_)|(_)\ )\  /(_)|(_)()\((_)\  /(_))") 
    print("(_(_()) _((_|(_)(_)) (_()((_) ((_)(_))  ") 
    print("|_   _|| || | __| _ \|  \/  |/ _ \/ __| ") 
    print("  | |  | __ | _||   /| |\/| | (_) \__ \ ") 
    print("  |_|  |_||_|___|_|_\|_|  |_|\___/|___/ ")
    print("\n")
    print("\n")
    print("BSD 3-Clause License")


main()
