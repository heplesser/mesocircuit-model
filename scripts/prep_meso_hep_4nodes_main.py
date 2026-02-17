"""Run mesocircuit
------------------

Main example script to run a simulation of the mesocircuit with NEST and 
subsequently analyze and plot the results.
The simulation of the spiking neuronal network can be followed by an LFP
simulation and the corresponding postprocessing and plotting.
"""

###############################################################################
# The script `mesocircuit_framework` contains the main functionality for
# parameter evalutation and job execution.
# The mesocircuit framework allows for the evaluation of parameter spaces, but
# here we only simulate one individual parameter combination.
# Several interesting parameter combinations (overwriting default values) are
# collected in a dictionary in the script `parametersets` for convenience.

from mesocircuit import mesocircuit_framework as mesoframe
import parametersets

################################################################################
# Here, we choose the parameter set `mesocircuit_MAMV1` which is the default
# model. It is an upscaled version of the microcircuit representing area V1 of
# the Multi-Area Model (Schmidt and van Albada, 2018).
# 'mesocircuit_MAMV1_evoked` applies a thalamic stimulus to the center of the
# same model.
# For local testing, `local_microcircuit_PD` and `local_mesocircuit_PD` are good
# choices. These models base on the original microcircuit
# (Potjans and Diesmann, 2014) and are downscaled for execution on a laptop.

name = 'mesocircuit_MAMV1'
# name = 'local_mesocircuit_PD'
params_key = name
custom_params = parametersets.ps_dicts[params_key]

custom_params["sim_dict"] = {"t_presim": 0.1, "t_sim": 10000}
custom_params["sim_dict"].update({"rec_dev": []})
custom_params["sys_dict"] = {"hpc": {"network": {"local_num_threads": 64, "num_mpi": 2,
                                                 "num_nodes": 4, "partition": "hamsteinZen3",
                                                 "nest_binary": "main",
                                                 'wall_clock_time': '01:00:00'}}}

print(50*'*')
print(custom_params)
print(50*'*')

################################################################################
# Next, we instantiate a `MesocircuitExperiment` with the custom parameters.
# The argument `name` can be chosen freely; here we just use the name of the
# parameter set.
# Upon instantiation, data directories are created, derived parameters
# calculated, and job scripts written.
# If an already existing experiment should be loaded, a class can be
# instantiated with the arguments of the existing `name` and `load=True`.

meso_exp = mesoframe.MesocircuitExperiment(name, custom_params)


################################################################################
# A `MesocircuitExperiment` provides an overview over all the parameter
# combinations it is holding (`parameterview`) and a list of all the individual
# model instances of class `Mesocircuit`` (`circuits`).

print('-' * 50)
print(meso_exp.parameterview)
print('-' * 50)
print(meso_exp.circuits)
print('-' * 50)

