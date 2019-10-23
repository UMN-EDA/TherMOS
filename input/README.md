# TherMOS: Input Directory

This directory contains the model parameter files. There are a total of three
files in this directory:

- *model_parameters_MOSFET.json*: This file stores the values of the model dimensions
  and thermal conductivities of the various material used in planar MOS
  technology. The numbers in this file are by default for a 14nm FDSOI technology from publically available literature sources
  and detailed information can be found in *doc/MOSFET_parameters.md*.

- *model_paramters_FinFET.json*: This file stores the values of the model dimensions
  and thermal conductivities of the various material used in planar MOS
  technology. The numbers in this file are by default for a 7nm FinFET technology from publically available literature sources
  and detailed information can be found in *doc/FinFET_parameters.md*.

- *tool_config.json*: This file contains parameters that control the accuracy of TherMOS results. See the *doc/UserGuide.md* for details on these variables.

The variables in each of these files are referenced in the figure below and in *doc/* directory.
