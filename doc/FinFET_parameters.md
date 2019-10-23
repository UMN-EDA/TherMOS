# TherMOS: FinFET Parameters

This document explains the various paramteres in the
*input/model_parameters_FinFET.json* file

## A 7nm FinFET

The image on the right shows a 7nm Bulk FinFET which describes the variables
used the JSON file.

<img align = "right" width="30%" src="doc/image/Bulk_FinFET.png">

The table below lists the various values specified in the JSON file with
comments and pointers to their source:


| Variable      	| Value (nm) 	| Source 	| Comments                                                          	|
|---------------	|------------	|--------	|-------------------------------------------------------------------	|
| l_chnl        	| 20         	| [1]    	| ASAP7 PDK Paper, Table 1.                                         	|
| t_box         	| 25         	| [2]    	| ASAP7 PDK ICCAD Presentation, Slide 48                            	|
| t_substrate   	| 500        	|        	|                                                                   	|
| t_gate        	| 44         	| [2]    	| ASAP7 PDK ICCAD Presentation, Slide 48                            	|
| t_chnl        	| 32         	| [2]    	| ASAP7 PDK ICCAD Presentation, Slide 48                            	|
| t_gox         	| 1.6        	| [2]    	| ASAP7 PDK ICCAD Presentation, Slide 48                            	|
| t_cont        	| 10         	|        	|                                                                   	|
| t_diff_ext    	| 20         	|        	|                                                                   	|
| l_gate_space  	| 34         	| [1]    	| ASAP7 PDK Paper, Table 1 (Gate pitch - channel  length)           	|
| l_diff_ext    	| 25         	| [1]    	| ASAP7 PDK Paper, Fig. 1. Scaled according to the other parameters 	|
| l_cont        	| 18         	| [1]    	| ASAP7 PDK Paper, Table 1                                          	|
| l_sd_junc     	| 20         	|        	|                                                                   	|
| l_g2sd_junc   	| 30         	| [1]    	| ASAP7 PDK Paper, Fig. 1. Scaled according to the other parameters 	|
| w_fin         	| 7          	| [1]    	| ASAP7 PDK Paper, Table 1                                          	|
| w_fin_space   	| 20         	| [1]    	| ASAP7 PDK Paper, Table 1                                          	|
| w_cont        	| 18         	| [1]    	| ASAP7 PDK Paper, Table 1                                          	|
| e_gate        	| 10         	| [1]    	| ASAP7 PDK Paper, Fig. 1. Scaled according to the other parameters 	|

## References
[1] Lawrence T. Clark, Vinay Vashishtha, Lucian Shifren, Aditya Gujja, Saurabh Sinha, Brian Cline, Chandarasekaran Ramamurthy, Greg Yeric,
"ASAP7: A 7-nm finFET predictive process design kit," Microelectronics Journal, Volume 53, 2016.
[2] Vinay Vashishtha, Manoj Vangala, Lawrence T. Clark, "ASAP7 Predictive Design
Kit Development and Cell Design Technology Co-optimization," ICCAD Embedded
Tutorial, 2017.

