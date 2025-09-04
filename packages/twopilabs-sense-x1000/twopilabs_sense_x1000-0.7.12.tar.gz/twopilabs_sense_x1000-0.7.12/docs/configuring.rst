.. _section-configuring:

Configuring your device
=======================

The device object returned by :meth:`~sense.x1000.SenseX1000.open_device` can also be used to configure your device's system configuration.

Changing the network configuration
----------------------------------
The network configuration can be changed from the default (DHCPv4/SLAAC plus Zeroconf) by calling the appropriate commands. Use the following commands to change the corresponding setting:

   >>> device.system.comm_lan_ip_address("192.168.12.5")    # set IPv4 address
   >>> device.system.comm_lan_ip_mask("255.255.255.0")      # set IPv4 netmask
   >>> device.system.comm_lan_ip_gateway("192.168.12.1")    # set IPv4 gateway
   >>> device.system.comm_lan_ip_reset() # See below

Changes in the IP-protocol configuration are reloaded on next boot (when they have been stored beforehand as described in :ref:`subsection-storing-loading-sysconf`). The reload process is also triggered when the IP subsystem is reset using :meth:`~sense.x1000.scpi_system.ScpiSystem.comm_lan_ip_reset`.

.. ATTENTION::
   Make sure that you can connect to the device using the newly configured IP address before storing these changes to the non-volatile memory. 
   In case you accidentally configure an invalid IP address/netmask (e.g. 192.168.55.0/255.255.255.0) your device might only be accessible using the IPv6 link-local address, which is always configured.

For more advanced network configuration please see :class:`~sense.x1000.scpi_system.ScpiSystem`.


.. _subsection-storing-loading-sysconf:

Storing/Loading the system configuration
----------------------------------------

In order to store the current system configuration in non-volatile memory use the following command:

   >>> device.memory.config_store() # Store current system configuration

To restore the factory system configuration use this command:

   >>> device.memory.config_preset() # Loads the factory defaults

Note that the defaults are only loaded and not stored. In order to automatically load the factory defaults on next startup you have to either clear the configuration stored in non-volatile memory using :meth:`~sense.x1000.scpi_memory.ScpiMemory.config_clear` and restart the device.
Alternatively you can load the factory defaults using :meth:`~sense.x1000.scpi_memory.ScpiMemory.config_preset` as shown above and then store the new configuration to non-volatile memory using :meth:`~sense.x1000.scpi_memory.ScpiMemory.config_store`.




