"""Placeholder for default doc """
from __future__ import division
from __future__ import absolute_import

import numpy as np
import subprocess
import os
import time

# @profile
def call_branin(H,sim_out,obj_params,info):
    """ Evaluates the Branin function """

    batch = len(H['x'])

    O = np.zeros(batch,dtype=sim_out)

    for i,x in enumerate(H['x']):
        devnull = open(os.devnull, 'w')
        np.savetxt('./x.in', x, fmt='%16.16f', delimiter=' ', newline=" ")
        p = subprocess.call(['python', 'branin.py'], cwd='./', stdout=devnull)

        O['f'][i] = np.loadtxt('./f.out',dtype=float)

        if 'uniform_random_pause_ub' in obj_params: 
            time.sleep(obj_params['uniform_random_pause_ub']*np.random.uniform())

        # if not H['local_pt'][i]:
        #     if np.random.uniform(0,1) < 0.1:
        #         print('blam')
        #         O['f'][i] = np.nan

    return O