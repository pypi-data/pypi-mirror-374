.. _section-examples:

Examples
========
This section contains a list of examples that focus on various aspects of using your 2πSENSE X1000 series device.
The example scripts shown here are directly runnable by a python system where the required packages (see :ref:`section-introduction`) are installed.

.. toctree::
    :maxdepth: 1

    live-plot
    fast-plot
    range-doppler
    hdf5-recorder

------------

* :ref:`examples-live-plot` 

  A simple live plotting demo with basic fft processing and axis calculation. 
  Plotting is handled by ``matplotlib`` and sweep parameters can be customized from command-line

* :ref:`examples-fast-plot`

  An improved version of the live-plot demonstrating a very responsive Qt+PyQtGraph GUI with peak detection and range history.

* :ref:`examples-range-doppler`

  The Range-Dopppler example shows how the 2πSENSE X1000 series devices can be used to perform FMCW sweeps with very precise and reliable timing.
  An entire acquisition of multiple sweeps is processed using a range-doppler algorithm providing a 2D color-coded live image of both distance and recession velocity.

* :ref:`examples-hdf5-recorder`

  This example demonstrates storing/loading AcqData (including metadata) objects to and from disk using the built-in :meth:`~sense.x1000.x1000_base.SenseX1000Base.AcqData.to_hdf5` and :meth:`~sense.x1000.x1000_base.SenseX1000Base.AcqData.from_hdf5` methods. After loading the data from file, the AcqData object is restored to it's original version so that any signal processing is agnostic of whether the data comes from a live sensor or from a file store.


