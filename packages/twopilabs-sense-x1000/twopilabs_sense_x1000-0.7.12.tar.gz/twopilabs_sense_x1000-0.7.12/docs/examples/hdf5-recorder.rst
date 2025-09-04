.. _examples-hdf5-recorder:

HDF5 Record & Replay
--------------------------------------
.. image:: /_images/examples-hdf5-record-screenshot.png

In this example we demonstrate the use of the built-in :meth:`~sense.x1000.x1000_base.SenseX1000Base.AcqData.to_hdf5` and :meth:`~sense.x1000.x1000_base.SenseX1000Base.AcqData.from_hdf5` methods to store acquisition data into a hdf5 file and later restore it.

These two tasks are separated into two different python scripts called ``hdf5-record.py`` and ``hdf5-replay.py``. In this example, the data is simply plotted after it was loaded.

HDF5 Record
^^^^^^^^^^^
**Source code:** :source:`examples/hdf5-record.py`

.. literalinclude:: /../examples/hdf5-record.py

HDF5 Replay
^^^^^^^^^^^
**Source code:** :source:`examples/hdf5-replay.py`

.. literalinclude:: /../examples/hdf5-replay.py
