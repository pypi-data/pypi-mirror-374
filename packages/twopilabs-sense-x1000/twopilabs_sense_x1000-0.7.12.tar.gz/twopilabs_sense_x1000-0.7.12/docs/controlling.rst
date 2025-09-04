.. _section-controlling:

Controlling your device
=======================

The device object returned by :meth:`~sense.x1000.SenseX1000.open_device` is the main entry point for controlling your 2πSENSE X1000 series device. 
It is used to set up the device configuration, trigger acquisitions and retrieve acquired measurement data.

The command structure of the device object closely follows the implemented SCPI command structure, where the top-level subsystems are implemented as attributes: ``device.<subsystem>.<command>``.

Setting up the device configuration
-----------------------------------
.. note::
   Once opened, the device can be configured. Note that due to frequency band regulations, the allowed configuration for your Sense X1000 may be limited.

2πSENSE X1000 series are operating using a technique called *frequency modulated continuous wave* (or FMCW for short). Using this technique a frequency sweep (or *chirp*) is generated at the RF port of the system.
The emitted radio waves are, for example, reflected off of objects and a delayed version of the generated frequency sweep is received by the system. 
The received signal is downconverted by the transmitted signal resulting in the intermediate frequency (IF) signal as the frequency difference between the two. 
Due to the linear relationship between the momentary frequency and delay time, reflections from further distances result in higher beat frequencies in the IF signal than reflections closer to the system.

Several FMCW sweep parameters can be configured using the device object in the :class:`sense <sense.x1000.scpi_sense>` subsystem. 
This example shows a configuration of 4 consecutive sweeps with a 60ms sweep period in one acquisition where each sweep starts at 182GHz and linearly sweeps to 126GHz in 1ms::

   >>> device.sense.frequency_start(182E9)   # Sets the frequency where the sweep starts
   >>> device.sense.frequency_stop(126E9)    # Sets the frequency where the sweep stops
   >>> device.sense.sweep_time(1E-3)         # Sets the sweep duration in seconds
   >>> device.sense.sweep_count(4)           # Sets the number of consecutive sweeps to perform per acqusition
   >>> device.sense.sweep_period(60E-3)      # Sets the "pulse repetition period", i.e. the inverse of the sweep reptition rate, in seconds

The system follows the SCPI standard model of *initiating* (arming) and *triggering* sweeps, where a single acquisition is run for each trigger event.
For trigger events to be of effect, the device has to be manually moved from its idle state (entered on power-up) into the initiated state.
Once initiated, the trigger is armed and the sweep is started once the trigger is commenced.
By default, the trigger source is selected as *IMMEDIATE* resulting in an always-true trigger state. 
Thus the default behaviour of the device is to immediately trigger and run a sweep after initiating.

Running a simple acquisition
----------------------------
The most simple way to manually run a single acquisition is to immediately initiate the system for a single trigger event, after which the device automatically returns back to its idle state. 
In SCPI terms, exactly this is performed by running the ``INITIATE:IMMEDIATE`` command. Once the acquisition starts, the resulting sweep data can be read from the ``CALCULATE:DATA`` subsystem.
Fortunately, running a single acquisition and returning the data is handled by the convenience method :meth:`~sense.x1000.scpi_initiate.ScpiInitiate.immediate_and_receive` of the device object.
This method directly returns a :class:`~sense.x1000.x1000_base.SenseX1000Base.Acquisition` object that allows direct access to the sweep data as it becomes available in the radar system.

The following example shows running a simple acquisition::

   >>> # Initiates, triggers, waits for initial data and returns acquisition object
   >>> acq = device.initiate.immediate_and_receive()
   >>> # Read data for all sweeps in one go (by default)
   >>> # This waits for all data to be available and then returns the data container object
   >>> data = acq.read()
   >>> # Access the data as a multidimensional numpy array
   >>> # The array dimensions are as follows
   >>> # N_sweeps x N_traces x N_points
   >>> print(f'numpy array: {type(data.array)}')
   >>> print(f'numpy array.shape: {data.array.shape}')
   >>> # The data container holds additional metadata about the measurement
   >>> # For example the information already seen in the header
   >>> print(f'n_sweeps: {data.n_sweeps}') # Number of sweeps in this data container (corresponds to array.shape[0])
   >>> print(f'n_traces: {data.n_traces}') # Number of traces for each sweep in this container (corresponds to array.shape[1])
   >>> print(f'n_points: {data.n_points}') # Number of points for each trace in this container (corresponds to array.shape[2])

.. important::
   Reading of acquisition data (using ``acq.read()`` above) needs to be executed directly following the device initiation (``device.initiate.immediate_and_receive()``) to avoid overflowing the internal buffers of the device.

Plotting the raw data
---------------------
The data container returned by the :meth:`~sense.x1000.x1000_base.SenseX1000Base.Acquisition.read` method is a container object of type :class:`~sense.x1000.x1000_base.SenseX1000Base.AcqData`. 
As shown above it can be used to access the returned acquisition information and data using various attributes and properties.
The raw acquisition data is returned by the :attr:`~sense.x1000.x1000_base.SenseX1000Base.AcqData.array` attribute which is a :class:`Numpy Array <numpy.ndarray>` and thus can be easily plotted as follows::

   >>> # Plot the raw data of the first trace in all sweeps of numpy array using matplotlib
   >>> # Note that the amplitude of the data is a 16-bit signed integer
   >>> import matplotlib.pyplot as plt
   >>> plt.figure(figsize=(15, 10))
   >>> plt.plot(data.array[:,0,:].T);
   >>> plt.xlabel('ADC Sample Points');
   >>> plt.ylabel('Amplitude (16-bit Signed Integer)');   






