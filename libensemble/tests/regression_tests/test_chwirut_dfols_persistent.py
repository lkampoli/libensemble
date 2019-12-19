# """
# Runs libEnsemble with APOSMM+POUNDERS on the chwirut least squares problem.
# All 214 residual calculations for a given point are performed as a single
# simulation evaluation.
#
# Execute via one of the following commands (e.g. 3 workers):
#    mpiexec -np 4 python3 test_chwirut_pounders.py
#
# The number of concurrent evaluations of the objective function will be 4-1=3.
# """

# Do not change these lines - they are parsed by run-tests.sh
# TESTSUITE_COMMS: local
# TESTSUITE_NPROCS: 4

import sys
import numpy as np

# Import libEnsemble items for this test
from libensemble.libE import libE
from libensemble.sim_funcs.chwirut1 import chwirut_eval as sim_f
from libensemble.gen_funcs.persistent_aposmm import aposmm as gen_f
from libensemble.alloc_funcs.persistent_aposmm_alloc import persistent_aposmm_alloc as alloc_f
from libensemble.utils import parse_args, save_libE_output, add_unique_random_streams

nworkers, is_master, libE_specs, _ = parse_args()

if nworkers < 2:
    sys.exit("Cannot run with a persistent worker if only one worker -- aborting...")

# Declare the run parameters/functions
m = 214
n = 3
budget = 10

sim_specs = {'sim_f': sim_f,
             'in': ['x'],
             'out': [('f', float), ('fvec', float, m)],
             'user': {'combine_component_func': lambda x: np.sum(np.power(x, 2))}
             }

gen_out = [('x', float, n), ('x_on_cube', float, n), ('sim_id', int),
           ('local_min', bool), ('local_pt', bool)]

# lb tries to avoid x[1]=-x[2], which results in division by zero in chwirut.
gen_specs = {'gen_f': gen_f,
             'in': [],
             'out': gen_out,
             'user': {'initial_sample_size': 100,
                      'localopt_method': 'dfols',
                      'components': m,
                      'lb': (-2-np.pi/10)*np.ones(n),
                      'ub': 2*np.ones(n)}
             }

alloc_specs = {'alloc_f': alloc_f, 'out': [('given_back', bool)], 'user': {}}

persis_info = add_unique_random_streams({}, nworkers + 1)

exit_criteria = {'sim_max': 1000}

# Perform the run
H, persis_info, flag = libE(sim_specs, gen_specs, exit_criteria, persis_info,
                            alloc_specs, libE_specs)

if is_master:
    assert flag == 0
    assert len(H) >= budget

    save_libE_output(H, persis_info, __file__, nworkers)

    # # Calculating the Jacobian at local_minima (though this information was not used by DFO-LS)
    # from libensemble.sim_funcs.chwirut1 import EvaluateFunction, EvaluateJacobian
    # for i in np.where(H['local_min'])[0]:

    #     F = EvaluateFunction(H['x'][i])
    #     J = EvaluateJacobian(H['x'][i])
    #     u = gen_specs['user']['ub']-H['x'][i]
    #     l = H['x'][i]-gen_specs['user']['lb']
    #     if np.any(u <= 1e-7) or np.any(l <= 1e-7):
    #         grad = -2*np.dot(J.T,F)
    #         assert np.all(grad[u<=1e-7] >= 0)
    #         assert np.all(grad[l<=1e-7] <= 0)

    #         if not np.all(grad[np.logical_and(u>=1e-7,l>=1e-7)] <= 1e-5):
    #             import ipdb; ipdb.set_trace()
    #     else:
    #         d = np.linalg.solve(np.dot(J.T,J),np.dot(J.T,F))
    #         assert np.linalg.norm(d) <= 1e-5
