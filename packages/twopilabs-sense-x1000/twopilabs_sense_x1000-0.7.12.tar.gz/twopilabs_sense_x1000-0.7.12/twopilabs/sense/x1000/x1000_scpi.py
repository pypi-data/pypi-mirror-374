from twopilabs.utils.scpi import ScpiDevice, ScpiResource
from .scpi_core import ScpiCore
from .scpi_system import ScpiSystem
from .scpi_memory import ScpiMemory
from .scpi_control import ScpiControl
from .scpi_sense import ScpiSense
from .scpi_calc import ScpiCalc
from .scpi_trigger import ScpiTrigger
from .scpi_initiate import ScpiInitiate
from .x1000_base import SenseX1000Base

class SenseX1000ScpiDevice(ScpiDevice):
    """Device interface class for controlling Sense X1000 series devices using SCPI Interface"""

    # SCPI Subsystems as attributes as easy-to-use application interface
    core: ScpiCore
    """SCPI core subsystem for mandatory and optional common commands"""
    system: ScpiSystem
    """SCPI SYSTEM subsystem for general housekeeping and functions related to global configurations"""
    control: ScpiControl
    """SCPI CONTROL subsystem for control of low-level hardware functionality"""
    sense: ScpiSense
    """SCPI SENSE subsystem for device-specific high-level configuration"""
    calc: ScpiCalc
    """SCPI CALCULATE subsystem for postacquisition data processing"""
    trigger: ScpiTrigger
    """SCPI TRIGGER subsystem for synchronizing device actions with events"""
    initiate: ScpiInitiate
    """SCPI INITIATE subsystem for controlling the initiation of the trigger subsystem"""

    def __init__(self, resource: ScpiResource, **kwargs):
        """Instantiate a SenseX1000ScpiDevice from a SCPI resource

        :param resource: A scpi.ScpiResource object representing the SCPI resource of the device
        :kwargs: Optional keyword arguments passed to the transport layer of the used SCPI resource
        """
        ScpiDevice.__init__(self, resource, **kwargs)
        self.core       = ScpiCore(self)
        self.system     = ScpiSystem(self)
        self.memory     = ScpiMemory(self)
        self.control    = ScpiControl(self)
        self.sense      = ScpiSense(self)
        self.calc       = ScpiCalc(self)
        self.trigger    = ScpiTrigger(self)
        self.initiate   = ScpiInitiate(self)

    def get_info(self):
        """Return a dictionary with information about the device"""
        return self.system.info()

    def get_state(self):
        """Return a dictionary with the current state of the device"""
        return {'SENSE': self.sense.dump()}

    @classmethod
    def find_devices(cls, **kwargs):
        # Set search constraints and discover SCPI resources
        kwargs.update({'usb_vid': SenseX1000Base.USB_VID})
        kwargs.update({'usb_pid': SenseX1000Base.USB_PID})
        kwargs.update({'dnssd_services': ['_scpi-raw._tcp']})
        kwargs.update({'dnssd_names': ['2πSENSE X1000.*']})
        kwargs.setdefault('dnssd_domains', ['local'])

        resources = ScpiResource.discover(**kwargs)

        return resources
