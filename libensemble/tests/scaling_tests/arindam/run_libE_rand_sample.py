#!/usr/bin/env python
# """
# Execute via one of the following commands:
#    mpiexec -np 4 python run_libE_rand_sample.py
#    python run_libE_rand_sample.py --comms local --nworkers 3

# The number of concurrent evaluations of the objective function will be 4-2=2
# as one MPI rank for the manager and one MPI rank for the persistent gen_f.
# """

import os
import numpy as np
from arindam_simf import run_covid  # Sim func from current dir

# Import libEnsemble modules
from libensemble.libE import libE
from libensemble.gen_funcs.sampling import uniform_random_sample as gen_f
from libensemble.alloc_funcs.give_sim_work_first import give_sim_work_first as alloc_f
from libensemble.tools import parse_args, save_libE_output, add_unique_random_streams
from libensemble import libE_logger
from libensemble.executors.mpi_executor import MPIExecutor

libE_logger.set_level('INFO')

nworkers, is_master, libE_specs, _ = parse_args()

# Set to full path of executable
sim_app = './sim_f'

# Creates a dummy directory where each evaluation is performed (for example, if file system
# I/O is needed for calculating a quantity of interest.) See libE_specs['sim_input_dir']
os.makedirs('./sim', exist_ok=True)

n = 2  # Problem dimension
exctr = MPIExecutor(central_mode=True)
exctr.register_calc(full_path=sim_app, calc_type='sim')

# State the objective function, its arguments, output, and necessary parameters (and their sizes)
sim_specs = {'sim_f': run_covid,           # Function whose output is being minimized
             'in': ['x'],                  # Name of input for sim_f
             'out': [('val1', float),  # Name, type of output from sim_f.
                     ('val2', float),
                     ('f', float)],          # Objective to be minimized
             'user': {'nodes': 1,
                      'ranks_per_node': 1,
                      'input_filename': 'inputs',
                      'sim_kill_minutes': 10.0}  # Timeout for sim ....
             }

# State the generating function, its arguments, output, and necessary parameters.
gen_specs = {'gen_f': gen_f,                 # Generator function
             'in': [],                       # Generator input
             'out': [('x', float, (n,))],       # nb of parameters to input into sim
             'user': {'gen_batch_size': 3,   # Total max number of sims
                      'lb': -1*np.ones(n),        # Lower bound for the n parameters
                      'ub': 2*np.ones(n),         # Upper bound for the n parameters
                      }
             }

alloc_specs = {'alloc_f': alloc_f,
               'out': [('allocated', bool)],
               'user': {'batch_mode': True,    # If true wait for all sims to process before generate more
                        'num_active_gens': 1}  # Only one active generator at a time
               }

libE_specs['save_every_k_sims'] = 100   # Save H to file every N simulation evaluations
libE_specs['sim_input_dir'] = 'sim'     # Sim dir to be copied for each worker

# Maximum number of simulations
sim_max = 6
exit_criteria = {'sim_max': sim_max}

# Create a different random number stream for each worker and the manager
persis_info = add_unique_random_streams({}, nworkers + 1)

H, persis_info, flag = libE(sim_specs, gen_specs, exit_criteria,
                            persis_info, alloc_specs, libE_specs)

# Save results to numpy file
if is_master:
    save_libE_output(H, persis_info, __file__, nworkers)