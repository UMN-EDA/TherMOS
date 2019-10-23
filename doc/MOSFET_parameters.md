# TherMOS: MOSFET Parameters

This document explains the various paramteres in the
*input/model_parameters_FinFET.json* file

## A 14nm FDSOI MOSFET

The image below shows a 7nm Bulk FinFET which describes the variables
used the JSON file.

<img align = "center" width="50%" src="image/PlanarSOI.png">

The table below lists the various values specified in the JSON file with
comments and pointers to their source:

| Variable      	| Value (nm) 	| Source 	| Comments             	|
|---------------	|------------	|--------	|----------------------	|
| l_chnl:       	| 20         	| [1]    	| Fig.2                	|
| t_box:        	| 25         	| [1]    	| Fig.2                	|
| t_substrate:  	| 25         	|        	|                      	|
| t_gate:       	| 40         	|        	|                      	|
| t_chnl:       	| 6          	|        	|                      	|
| t_gox:        	| 1          	| [1]    	| Experimental section 	|
| t_diff_ext:   	| 20         	|        	|                      	|
| l_gate_space: 	| 35         	|        	|                      	|
| l_sd_junc     	| 40         	|        	|                      	|
| l_diff_ext:   	| 25         	|        	|                      	|
| l_cont:       	| 10         	|        	|                      	|
| w_cont:       	| 10         	|        	|                      	|
| e_gate:       	| 10         	|        	|                      	|


## References
[1] Q. Liu et al., "High performance UTBB FDSOI devices featuring 20nm gate length for 14nm node and beyond," IEEE International Electron Devices Meeting, pp. 9.2.1-9.2.4, 2013.


