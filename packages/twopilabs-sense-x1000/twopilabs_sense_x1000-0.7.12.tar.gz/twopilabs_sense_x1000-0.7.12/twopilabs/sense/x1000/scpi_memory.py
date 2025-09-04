from twopilabs.utils.scpi import *


class ScpiMemory(object):
    """Class containing SCPI commands concerning MEMORY subsystem"""

    def __init__(self, device: ScpiDevice) -> None:
        self.device = device

    def config_store(self, slot: int = 0) -> None:
        """Save system configuration to non-volatile memory

        :param slot: System configuration register slot
        """
        self.device.execute('MEM:CONF:STORE', param=ScpiNumber(int(slot)))
        self.device.raise_error()

    def config_load(self, slot: int = 0) -> None:
        """Recall system configuration from non-volatile memory

        :param slot: System configuration register slot
        """
        self.device.execute('MEM:CONF:LOAD', param=ScpiNumber(int(slot)))
        self.device.raise_error()

    def config_clear(self, slot: int = 0) -> None:
        """Reset system configuration in non-volatile memory to defaults

        :param slot: System configuration register slot
        """
        self.device.execute('MEM:CONF:CLEAR', param=ScpiNumber(int(slot)))
        self.device.raise_error()

    def config_preset(self) -> None:
        """Load default system configuration without altering non-volatile memory"""
        self.device.execute('MEM:CONF:PRESET')
        self.device.raise_error()

    def state_store(self, slot: int = 0) -> None:
        """Save system state to given slot in non-volatile memory

        :param slot: System state register slot
        """
        self.device.execute('MEM:STATE:STORE', param=ScpiNumber(int(slot)))
        self.device.raise_error()

    def state_load(self, slot: int = 0) -> None:
        """Recall system state from given slot in non-volatile memory

        :param slot: System state register slot
        """
        self.device.execute('MEM:STATE:LOAD', param=ScpiNumber(int(slot)))
        self.device.raise_error()

    def state_clear(self, slot: int = 0) -> None:
        """Reset system state in given slot in non-volatile memory to defaults

        :param slot: System state register slot
        """
        self.device.execute('MEM:STATE:CLEAR', param=ScpiNumber(int(slot)))
        self.device.raise_error()

    def state_preset(self, slot) -> None:
        """Load default system state without altering non-volatile memory

        :param slot: System state register slot
        """
        self.device.execute('MEM:STATE:PRESET')
        self.device.raise_error()
