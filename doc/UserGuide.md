# TherMOS: A Brief User Guide
TherMOS is a creates a thermal model for self-heating in advanced MOS devices.
There are two primary paths for the flow of heat in FinFETs and planar MOSFETS:
-- Down towards the substrate of the device
-- Along the channel of through the source and drain contacts into the metal
  layer stack

The thermal model is based on the finite differences method (FDM),
the electrical-thermal equivalence can be used to build a thermal resistance network. 
The power dissipation (or heat) in each element is modeled as a current source. 
If there are *n* finite regions, then the temperature at each FDM node can be
obtained by solving a system of *n* linear equations: *GT=P*.

TherMOS is based on the work done in [Impact of Self-heating on Performance and Reliability in FinFET and GAAFET designs](https://ieeexplore.ieee.org/document/8697786)

## Download and Install TherMOS

We use a python3.6 virtual environment to install all the required python libraries
using pip18.1. 

``` bash
~$ git cone https://github.com/VidyaChhabria/TherMOS.git
~$ cd Thermal-model
~$ source install.sh
```

TherMOS uses pytest for unit tests. 

`~$ pytest`


## Input Parameter Files
TherMOS relies on a model parameter file which specifies various technology
specific parameters including device and material properties such as device
dimensions and thermal conductivities. 

### FinFET Parameter File
The file [model_parameter_FinFET.json](../input/model_parameters_FinFET.json) specifies the device dimensions
and thermal coductivities of the various materials used in a 7nm FinFET technology.

The image below shows a 7nm Bulk FinFET which describes the variables
used the JSON file.

<img align = "center" width="50%" src="image/Bulk_FinFET.png">

The table below lists the various values specified in the JSON file with
comments and pointers to their source:

| Variable      	| Value (nm) 	| Source 	| Comments                                                          	|
|---------------	|------------	|--------	|-------------------------------------------------------------------	|
| l_chnl        	| 20         	| [1]    	| ASAP7 PDK Paper, Table 1.                                         	|
| t_box         	| 25         	| [2]    	| ASAP7 PDK ICCAD Presentation, Slide 48                            	|
| t_substrate   	| 500        	| [3]     |                                                                 |
| t_gate        	| 44         	| [2]    	| ASAP7 PDK ICCAD Presentation, Slide 48                            	|
| t_chnl        	| 32         	| [2]    	| ASAP7 PDK ICCAD Presentation, Slide 48                            	|
| t_gox         	| 1.6        	| [2]    	| ASAP7 PDK ICCAD Presentation, Slide 48                            	|
| t_cont        	| 80        	| [3]     | Scaled the data given in [3] by 0.7                                 |                       
| t_diff_ext    	| 32        	| [4]     | Nearly same as fin height                                           |                   
| l_gate_space  	| 34         	| [1]    	| ASAP7 PDK Paper, Table 1 (Gate pitch - channel  length)           	|
| l_diff_ext    	| 25         	| [1]    	| ASAP7 PDK Paper, Fig. 1. Scaled according to the other parameters 	|
| l_cont        	| 18         	| [1]    	| ASAP7 PDK Paper, Table 1                                          	|
| l_sd_junc     	| 20         	| [3]     | Scaled the data given in [3] by 0.7                                 |                       
| l_g2sd_junc   	| 30         	| [1]    	| ASAP7 PDK Paper, Fig. 1. Scaled according to the other parameters 	|
| w_fin         	| 7          	| [1]    	| ASAP7 PDK Paper, Table 1                                          	|
| w_fin_space   	| 20         	| [1]    	| ASAP7 PDK Paper, Table 1                                          	|
| w_cont        	| 18         	| [1]    	| ASAP7 PDK Paper, Table 1                                          	|
| e_gate        	| 10         	| [1]    	| ASAP7 PDK Paper, Fig. 1. Scaled according to the other parameters 	|


### MOSFET Parameter File
The file [model_parameters_MOSFET.json](../input/model_parameters_MOSFET.json) specifies the device dimensions
and thermal coductivities of the various materials used in a 14nm planar MOSFET technology.

The table below lists the various values specified in the JSON file with
comments and pointers to their source:

| Variable      	| Value (nm) 	| Source 	| Comments                              	  |
|---------------	|------------	|--------	|--------------------------------       	  |
| l_chnl:       	| 20         	| [5]    	| Fig. 2                                    |
| t_box:        	| 25         	| [5]    	| Fig. 2                                    |
| t_substrate:  	| 500           | [5]     |                                           |
| t_gate:       	| 40         	| [5]  	  | Scaled from Fig. 2                        |
| t_chnl:       	| 6          	| [5]     | Page 1 Col. 2                             |
| t_gox:        	| 1          	| [5]    	| Experimental section                      |
| t_diff_ext:   	| 20         	| [5]     | Scaled from Fig. 2                        |
| l_gate_space: 	| 54         	| [5]    	| Scaled from Fig. 2                        |
| l_sd_junc     	| 40         	| [5]    	| Scaled from Fig. 2                        |
| l_diff_ext:   	| 40         	| [5]   	| Scaled from Fig. 2                        |
| l_cont:       	| 32         	| [6]    	| Table 1, extracted from M1 pitch          |
| w_cont:       	| 32         	| [6]    	| Table 1, extracted from M1 pitch          |
| e_gate:       	| 18         	| [7]    	| Scaled from 45nm Free PDK                 |
| t_cont        	| 48         	| [6]	    | Assuming thickness to width ratio of 1.5 	|



### Tool Configuration File
The file *input/tool_config.json* specifies the various paramters that impact the
  accuracy of TherMOS results. The table below briefly explains each variable:

| Variable      | Value (nm)    | Comments                                                                                         |
|---------------|---------------|--------------------------------------------------------------------------------------------------|
| resolution    | [2.5,2.5,2.5] | Specifies the dimension of a finite element in the FDM analysis                                 |
| t_sub2gnd     | 475           | Value is added to the thickness of the substrate ("t_substrate")                                 |
| t_cnt2gnd     | 10000         | Represents the distance between the source/drain terminal contacts and power pad via the PDN     |
| sp_edge       | 5             | Spacing between the device and the edge of the simulation region in *x*-direction; Do not change |
| t_sp_edge     | 20            | Spacing between the device and the edge of the simulation region in *z*-direction; Do not change |
| l_sp_diff_ext | 5             | Spacing between the device and the edge of the simulation region in *z*-direction; Do not change |


-- *resolution*: This specifies the size of each finite element in the Finite
Difference Method (FDM) simulation. This is an array of float numbers that
represents the dimension of the finite element in the *x*,*y*, and *z*-directions. 
A small value used here would provide a more accurate result at the
cost of run-time. It is recommended to use a larger value in the *z*-direction, due
to the large device dimensions in that direction and a smaller value in the *x*-
and *y*-directions.

-- *t_sub2gnd*: This variable is added to the variable *t_substrate* from the
input/model_parameter_<device> .json file. The effective substrate thickness is
*t_substrate + t_sub2gnd*. The *t_sub2gnd* variable has a different finite
element size. For reasonable run-times and accuracy it is recommended that the
value of this variable be 75% of the total substrate thickness.

-- *t_cnt2gnd*: This variable represents the distance between the
source/drain terminal pin of the device and the thermal ambient via the BEOL
stack. Intuitively, this can be thought of as the equivalent metal distance from
the pin to the C4 bump via the power delivery network (PDN). 


## Running TherMOS
TherMOS requires a model_parameter file, example [model_parameter_FinFET.json](input/model_parameter_FinFET.json), file which specifies the various parameters of
the device in consideration. The default parameters in the file 
[model_parameter_FinFET.json](../input/model_parameter_FinFET.json) and 
[model_parameter_MOSFET.json](../input/model_parameter_MOSFET.json) for a planar 7nm FinFET and 14nm FDSOI planar MOSFET technology and are
obtained from literature sources as documented in [FinFET_parameters.md](doc/FinFET_parameters.md) and  [MOSFET_parameters.md](doc/MOSFET_parameters.md) respectively.

TherMOS is used as follows:

`python3 <process_type> -device_type <str> -n_gate <int>  -power <float> [-n_fin <int> | -width <float>] -active "<int_list>" -percent "<float_list>"


| Argument              	| Comments                                                                             	|
|-----------------------	|--------------------------------------------------------------------------------------	|
| -h, --help            	| Prints out the usage                                                                 	|
| <process_type>        	| Process and technology specification (str, required)                                 	|
| -n_gate <int>         	| Specifies the number of transistors in the simulation (int, required)                	|
| -power <float>        	| Specifies the total power dissipated by the array of transistors(s)                   	|
| -n_fin <int>          	| Number of fins in FinFET (required, int, use only when   <process_type> is FinFET)   	|
| -width <float>        	| Width of the MOSFET (required, float, use only when process is MOSFET)               	|
| -active    "int_list" 	| States the list of gate ids that are dissipating power (list of int,   optional)     	|
| -percent "float_list" 	| Percentage of power distributed between the active gates (optional, list_of_float) 	|

-- *active*: active gates must be an integer of gate ids that dissipate power. By
default TherMOS distributes power to all gates based on the specified
distribution in "percent".

-- *percent*: this variable provides the distribution of power between the
active gates. For example if active is "0,1" and percent is "25, 75" then 25% 
of the power is applied to gate 0 and 75% to gate 1.

After TherMOS completes execution, it generates a temperature report in the
output directory which contains the maximum, and average temperature rise in
the transistor(s).

To view a graphic of temperature distribution within the transistor(s):

```
cd scripts
octave -r -nodisplay 'visualize_T';
```


## Output Files
The following outputs are generated by TherMOS:

- [temperature.rpt](../output/temperature.rpt): a report which states the maximum, minimum and average
  temperature of all the devices simulated.
- [T.out](../output/T.out): a python object which is an array of temperatures that can be used in
  MATLAB to plot the temperature profile.
- [T.png](../output/T.png): an image with the 3D temperature contour plot of the simulated
  devices. 
 



## References
[1] L. T. Clark *et al.*, "ASAP7: A 7-nm finFET predictive process design kit," *Microelectronics Journal*, Volume 53, 2016.

[2] V Vashishtha *et al.*, "ASAP7 Predictive Design Kit Development and Cell Design Technology Co-optimization," *ICCAD Embedded Tutorial*, 2017.

[3] M. Shrivastava, et al.,"Physical insight toward heat transport and an improved electrothermal modeling framework for FinFET architectures" IEEE Transactions on Electron Devices, vol. 59, no. 5, pp. 1353-1363, 2012.

[4] B. Swahn and S. Hassoun, "Electro-thermal analysis of multi-fin devices," IEEE transactions on very large scale integration (VLSI) systems, vol. 16, no. 7, pp. 816-829, 2008.

[5] Q. Liu et al., "High performance UTBB FDSOI devices featuring 20nm gate length for 14nm node and beyond," IEEE International Electron Devices Meeting, pp. 9.2.1-9.2.4, 2013.

[6] O. Weber et al., "14nm FDSOI technology for high speed and energy efficient applications," Symposium on VLSI Technology (VLSI-Technology), pp. 1-2, 2014.

[7] "NCSU 45nm FreePDK", Available at https://www.eda.ncsu.edu/wiki/FreePDK45:PolyRules

