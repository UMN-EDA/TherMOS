# TherMOS 
A thermal model for self-heating in advanced MOS devices.

[![Standard](https://img.shields.io/badge/python-3.6-blue)](https://commons.wikimedia.org/wiki/File:Blue_Python_3.6_Shield_Badge.svg)
[![Download](https://img.shields.io/badge/Download-here-red)](https://github.com/VidyaChhabria/TherMOS/archive/master.zip)
[![Version](https://img.shields.io/badge/version-0.1-green)](https://github.com/VidyaChhabria/TherMOS/tree/master)
[![AskMe](https://img.shields.io/badge/ask-me-yellow)](https://github.com/VidyaChhabria/TherMOS/issues)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

There are two primary paths for the flow of heat in FinFETs and planar MOSFETS:
- Down towards the substrate of the device
- Along the channel of through the source and drain contacts into the metal
  layer stack

The thermal model is based on the finite differences method (FDM),
the electrical-thermal equivalence can be used to build a thermal resistance network. 
The power dissipation (or heat) in each element is modeled as a current source. 
If there are *n* finite regions, then the temperature at each FDM node can be
obtained by solving a system of *n* linear equations: *GT=P*

## Why TherMOS?
<img align = "right" width="30%" src="doc/image/SOI_FinFET_temp_dist.png">

Self-heating is critical in modern devices with three
dimensional architectures and highly resistive thermal paths. 
TherMOS is a tool which estimates the temperature rise within advanced MOS
devices due to self-heating. It is developed from ground up using basic python
libraries. 

Key features are:
+ Simulation for different technologies at the change of a button (FinFET, MOSFET)
+ Improved run-times by using non-uniform meshing in FDM simulation
+ Fast multifin and multigate array simulation
+ One-stop-shop for device parameters compiled from literature sources for 7FF
  and 14nm FDSOI technologies
+ Precise estimate of temperature through detailed modeling


## Getting started

### Prerequisites

+ python3.6
+ pip 18.1
+ python3-venv
+ GNU Octave (optional)
Additionally, please refere to *requirements.txt* file in this respository.

### Install on machine

#### Setup

We use a python virtual environment to install all the required python libraries
using pip. 

``` bash
~$ git cone https://github.com/VidyaChhabria/TherMOS.git
~$ cd Thermal-model
~$ source install.sh
```

#### Run tests

TherMOS uses pytest for unit tests. 

`~$ pytest`

### Usage

TherMOS requires a model_parameter file, example [model_parameter_FinFET.json](input/model_parameter_FinFET.json), file which specifies the various parameters of
the device in consideration. The default parameters in the file 
[model_parameter_FinFET.json](input/model_parameter_FinFET.json) and 
[model_parameter_MOSFET.json](input/model_parameter_MOSFET.json) for a planar 7nm FinFET and 14nm FDSOI planar MOSFET technology and are
obtained from literature sources as documented in [FinFET_parameters.md](doc/FinFET_parameters.md) and  [MOSFET_parameters.md](doc/MOSFET_parameters.md) respectively.

TherMOS can be used as follows:

`python3 src/TherMOS.py <process_type> -device_type <str> -n_gate <int>  -power <float> [-n_fin <int> | -width <float>] -active "<int_list>" -percent "<float_list>"`

| Argument              	| Comments                                                                             	|
|-----------------------	|--------------------------------------------------------------------------------------	|
| -h, --help            	| Prints out the usage                                                                 	|
| <process_type>        	| Process and technology specification (str, required)                                 	|
| -device_type <str>      | NMOS or PMOS device type (required, str)                                              |
| -n_gate <int>         	| Specifies the number of transistors in the simulation (int, required)                	|
| -power <float>        	| Specifies the total power dissipated by the array of transistors(s)                   	|
| -n_fin <int>          	| Number of fins in FinFET (required, int, use only when   <process_type> is FinFET)   	|
| -width <float>        	| Width of the MOSFET (required, float, use only when process is MOSFET)               	|
| -active    "int_list" 	| States the list of gate ids that are dissipating power (list of int,   optional)     	| 
| -percent "float_list" 	| Percentage of power distributed between the active gates (optional,   list_of_float) 	|



After TherMOS completes execution, it generates a temperature report in the
output directory which contains the the maximum, and the average temperature rise in
the transistor(s).

To view a graphic of temperature distribution within the transistor(s):

```
cd scripts
octave -r -nodisplay 'visualize_T';
```

The following outputs are generated by TherMOS:

- [temperature.rpt](output/temperature.rpt): a report which states the maximum, minimum and average
  temperature of all the devices simulated.
- [T.out](output/T.out): a python object which is an array of temperatures that can be used in
  Octave to plot the temperature profile.
- [T.png](output/T.png): an image with the 3D temperature contour plot of the simulated
  devices. 
 

## Limitations and Todo

- The software only handles transistor arrays that share a common diffusion
  only.
- Stead-state temperature analysis only.
- Dockerize and CI.

## Paper

This repository is based on the work done in [Impact of Self-heating on
Performance and Reliability in FinFET
and GAAFET designs](https://ieeexplore.ieee.org/document/8697786)


## License

This software is released under the BSD 3-Clause License.

>Copyright (c) 2019, The Regents of the University of Minnesota
>All rights reserved.
>
>Redistribution and use in source and binary forms, with or without
>modification, are permitted provided that the following conditions are met:
>
>1. Redistributions of source code must retain the above copyright notice, this
>   list of conditions and the following disclaimer.
>
>2. Redistributions in binary form must reproduce the above copyright notice,
>   this list of conditions and the following disclaimer in the documentation
>   and/or other materials provided with the distribution.
>
>3. Neither the name of the copyright holder nor the names of its
>   contributors may be used to endorse or promote products derived from
>   this software without specific prior written permission.
>
>THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
>AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
>IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
>DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
>FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
>DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
>SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
>CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
>OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
>OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

