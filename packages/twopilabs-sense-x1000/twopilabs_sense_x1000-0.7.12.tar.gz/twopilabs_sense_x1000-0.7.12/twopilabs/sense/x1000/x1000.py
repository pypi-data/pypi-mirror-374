from typing import *
from twopilabs.utils.scpi import ScpiResource
from .x1000_base import SenseX1000Base
from .x1000_scpi import SenseX1000ScpiDevice


class SenseX1000(SenseX1000Base):
    """Entry class for controlling 2πSENSE X1000 series devices"""

    _RESOURCE_DEVICE_MAP: Dict[Type[ScpiResource], Type[SenseX1000ScpiDevice]] = {
        ScpiResource: SenseX1000ScpiDevice
    }

    @classmethod
    def open_device(cls, resource: Union[ScpiResource], **kwargs) -> Union[SenseX1000ScpiDevice]:
        """Open the connection to a 2πSENSE X1000 series device and return a device object

        :param resource: A resource object to be opened
        :keyword float timeout: Device timeout for read requests
        :return: The device control object
        """
        if type(resource) not in cls._RESOURCE_DEVICE_MAP:
            raise TypeError(f'{type(resource)} is not a supported resource type')

        return cls._RESOURCE_DEVICE_MAP[type(resource)](resource, **kwargs)

    @classmethod
    def find_devices(cls, **kwargs) -> List[Union[ScpiResource]]:
        """Find 2πSENSE X1000 series devices connected to this computer and return a list of resources objects

        :keyword ~typing.List[~typing.Type] transports: List of transports to find devices on
        :keyword ~typing.List[str] dnssd_domains: :class:`~twopilabs.utils.scpi.scpi_transport_tcpip.ScpiTcpIpTransport` DNS-SD domains to search
        :keyword str dnssd_ipversions: :class:`~twopilabs.utils.scpi.scpi_transport_tcpip.ScpiTcpIpTransport` IP protocol versions used for DNS-SD
        :keyword float dnssd_timeout: :class:`~twopilabs.utils.scpi.scpi_transport_tcpip.ScpiTcpIpTransport` Timeout in seconds to wait for DNS-SD responses
        :return: A list of resource objects
        """
        devices = []

        for device_type in cls._RESOURCE_DEVICE_MAP.values():
            devices += device_type.find_devices(**kwargs)

        return devices
