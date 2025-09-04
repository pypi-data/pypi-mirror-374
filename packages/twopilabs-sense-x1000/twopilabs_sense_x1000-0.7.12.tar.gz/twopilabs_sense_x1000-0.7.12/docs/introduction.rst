.. _section-introduction:

Introduction
============


License
-------
The 2πSENSE X1000 series control packages are release under a free software license (LGPLv3) which grants you the following rights:
  - Install and use this package by installing from the Python Packaging Index (PyPI, e.g. via ``pip``)
  - Distribute your own (possibly closed-source) application using this package as long as the package is not included with it
In addition these are your obligations:
  - When you distribute the package with your application (or on its own), you need to include source code for the library.
  - In case you modify (and redistribute) the package, We would like you to feed-back your modifications upstream to 2π-LABS GmbH.

You can find more information on the websites of the FSF `here <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_.

Requirements
------------
This package is tested under Windows, MacOS and Linux operating systems and requires Python 3.7 or later.

Installation
------------
Use ``pip`` to install the package from the Python Packaging Index (PyPI) on the command line::

    python -m pip install twopilabs-sense-x1000 # or 'python3'

.. important:: At present, the ``libusb`` PyPI package does not provide a library for ARM based processors (such as the most current Apple Macbook M1/M2 Lineup). 
   On these systems, it is therefore necessary to install ``libusb`` system-wide using the appropriate system utilities.
   For MacOS based products, this can be achieved by installing ``libusb`` using ``homebrew`` (or using ``apt`` on Ubuntu derivatives).
   For more information see `here <https://stackoverflow.com/questions/70729330/python-on-m1-mbp-trying-to-connect-to-usb-devices-nobackenderror-no-backend-a>`_.

Non-Root USB Access (Linux)
---------------------------
This library uses a libusb based implementation of USBtmc for communicating with the 2πSENSE X1000 series device.
By default only the root user is allowed to directly access USB devices using libusb on Linux based systems.
In order to allow other non-root users to control the device a ``udev`` rule needs to be added to the system and the user needs to be added to this group:

    >>> echo SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"1fc9\", ATTRS{idProduct}==\"8271\", GROUP=\"plugdev\", MODE=\"0660\" | sudo tee -a /etc/udev/rules.d/99-twopilabs-sense-x1000.rules
    >>> sudo udevadm control --reload && sudo udevadm trigger
    >>> sudo adduser <user> plugdev # Or add user to 'plugdev' group via GUI

Then the device needs to be replugged in order for the udev rules to be processed and the user needs to logout/login for the group membership to update. 
Alternatively a system reboot can be performed to achieve both or the udev rule can be modified to allow access for all users on the system, regardless of their group membership by changing ``MODE=\"0666\"`` in the udev rule.

Basic Usage
-----------
The package is imported as follows:

    >>> from twopilabs.sense.x1000 import SenseX1000

Discover and open the first found device:


    >>> devices = SenseX1000.find_devices() # Discover devices using mDNS, USB, etc...
    >>> with SenseX1000.open_device(devices[0]) as device:
    >>>     print(device.core.idn()) # Print the SCPI *IDN? output

See :ref:`section-controlling` and :ref:`section-examples` for more complex usage patterns and the :ref:`API reference <section-apiref>`.
