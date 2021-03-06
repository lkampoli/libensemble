Simulator Functions
===================

As described in the :ref:`API<api_sim_f>`, the ``sim_f`` is called by a
libEnsemble worker via a similar interface to the ``gen_f``::

    out = sim_f(H[sim_specs['in']][sim_ids_from_allocf], persis_info, sim_specs, libE_info)

In practice, most ``sim_f`` function definitions written by users resemble::

    def my_simulator(H, persis_info, sim_specs, libE_info):

Where :doc:`sim_specs<../data_structures/sim_specs>` is a
dictionary containing pre-defined parameters for the ``sim_f``, and the other
parameters serve similar purposes to those in the ``gen_f``.

The pattern of setting up a local ``H``, parsing out parameters from
``sim_specs``, performing calculations, and returning the local ``H``
with ``persis_info`` should be familiar::

    batch_size = sim_specs['user']['batch_size']
    local_H_out = np.zeros(batch_size, dtype=sim_specs['out'])

    ... # Perform simulation calculations

    return local_H_out, persis_info

Simulator functions can also return a :doc:`calc_status<../data_structures/calc_status>`
integer attribute from the ``libensemble.message_numbers`` module to be logged.

Descriptions of included simulator functions can be found :doc:`here<../examples/sim_funcs>`.

The :doc:`Simple Sine tutorial<../tutorials/local_sine_tutorial>` is an
excellent introduction for writing simple user functions and using them
with libEnsemble.

Executor
--------

libEnsemble's Executor is commonly used within simulator functions to launch
and monitor applications. An excellent overview is already available
:doc:`here<../executor/overview>`.

See the :doc:`Executor with Electrostatic Forces tutorial<../tutorials/executor_forces_tutorial>`
for an additional example to try out.
