from twopilabs.utils.scpi import *
from .x1000_base import SenseX1000Base
import yaml
import datetime


class ScpiSystem(object):
    """Class containing SCPI commands concerning SYSTEM subsystem"""

    def __init__(self, device: ScpiDevice) -> None:
        self.device = device

    def error_next(self) -> ScpiEvent:
        return self.device.execute('SYST:ERR:NEXT?', result=ScpiEvent)

    def info(self) -> dict:
        """returns a system information dictionary"""
        config = self.device.execute('SYST:INFO?', result=ScpiString).as_bytes()

        self.device.raise_error()
        return yaml.load(config, Loader=yaml.FullLoader)

    def version(self) -> str:
        """returns supported SCPI version"""
        version = self.device.execute('SYST:VERSION?', result=ScpiChars).as_string()

        self.device.raise_error()
        return version

    def preset(self) -> None:
        """Loads the system defaults"""
        self.device.execute('SYST:PRESET')

    def license_list(self) -> dict:
        """returns a list of software licenses of libraries used in the firmware"""
        licenses = self.device.execute('SYST:LICENSE:LIST?', result=ScpiString).as_bytes()

        self.device.raise_error()
        return yaml.load(licenses, Loader=yaml.FullLoader)

    def time(self, time: Optional[datetime.time] = None) -> datetime.time:
        """Sets or gets the radar system time"""
        if time is not None:
            self.device.execute('SYST:TIME', param=ScpiNumberArray([time.hour, time.minute, time.second]))
        else:
            time = datetime.time(*self.device.execute('SYST:TIME?', result=ScpiNumberArray).as_int_list())

        self.device.raise_error()
        return time

    def date(self, date: Optional[datetime.date] = None) -> datetime.date:
        """Sets or gets the radar system date"""
        if date is not None:
            self.device.execute('SYST:DATE', param=ScpiNumberArray([date.year, date.month, date.day]))
        else:
            date = datetime.date(*self.device.execute('SYST:DATE?', result=ScpiNumberArray).as_int_list())

        self.device.raise_error()
        return date

    def timezone(self, posix: Optional[str] = None) -> str:
        """Sets or gets the local timezone in POSIX1003.1 format"""
        if posix is not None:
            self.device.execute('SYST:TZONE', param=ScpiString(posix))
        else:
            posix = self.device.execute('SYST:TZONE?', result=ScpiString).as_string()

        self.device.raise_error()
        return posix

    def utc(self, timestamp: Optional[float] = None):
        """Sets or gets the radar system clock as UTC POSIX timestamp"""
        if timestamp is not None:
            self.device.execute('SYST:UTC', param=ScpiNumber(timestamp))
        else:
            timestamp = self.device.execute('SYST:UTC?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return timestamp

    def comm_lan_ip_reset(self):
        """Resets the IP subsystem (required to update changes in IP configuration)"""
        self.device.execute(f'SYST:COMM:LAN:IP:RESET')
        # No raise_error check, it might be possible that the connection is interrupted from here on

    def comm_lan_ip_enable(self, enabled: Optional[bool] = None,
                           ipversion: Optional[SenseX1000Base.IPVersion] = SenseX1000Base.IPVersion.IPV4) -> bool:
        """Sets or gets administrative status of IPv4/IPv6 interface"""
        if enabled is not None:
            self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}', param=ScpiBool(enabled))
        else:
            enabled = self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}?', result=ScpiBool).as_bool()

        self.device.raise_error()
        return enabled

    def comm_lan_ip_address(self, address: Optional[str] = None,
                            ipversion: Optional[SenseX1000Base.IPVersion] = SenseX1000Base.IPVersion.IPV4) -> str:
        """Sets or gets IPv4/IPv6 address"""
        if address is not None:
            self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:ADDR', param=ScpiString(address))
        else:
            address = self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:ADDR?', result=ScpiString).as_string()

        self.device.raise_error()
        return address

    def comm_lan_ip_mask(self, mask: Optional[str] = None,
                         ipversion: Optional[SenseX1000Base.IPVersion] = SenseX1000Base.IPVersion.IPV4) -> str:
        """Sets or gets IPv4 subnet mask """
        if mask is not None:
            self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:MASK', param=ScpiString(mask))
        else:
            mask = self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:MASK?', result=ScpiString).as_string()

        self.device.raise_error()
        return mask

    def comm_lan_ip_gateway(self, gateway: Optional[str] = None,
                            ipversion: Optional[SenseX1000Base.IPVersion] = SenseX1000Base.IPVersion.IPV4) -> str:
        """Sets or gets IPv4/IPv6 gateway address"""
        if gateway is not None:
            self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:GATEWAY', param=ScpiString(gateway))
        else:
            gateway = self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:GATEWAY?', result=ScpiString).as_string()

        self.device.raise_error()
        return gateway

    def comm_lan_ip_autoconf_enable(self, enabled: Optional[bool] = None,
                                    ipversion: Optional[SenseX1000Base.IPVersion] = SenseX1000Base.IPVersion.IPV4) -> bool:
        """Enables or disables IPv4 AutoIP (Zeroconf) or IPv6 Autoconfiguration (SLAAC-RA)"""
        if enabled is not None:
            self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:AUTOCONF', param=ScpiBool(enabled))
        else:
            enabled = self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:AUTOCONF?', result=ScpiBool).as_bool()

        self.device.raise_error()
        return enabled

    def comm_lan_ip_autoconf_status(self,
                                    ipversion: Optional[SenseX1000Base.IPVersion] = SenseX1000Base.IPVersion.IPV4) -> Union[SenseX1000Base.IPv4AutoconfStatus,
                                                                                                                            SenseX1000Base.IPv6AutoconfStatus]:
        """Returns the current IPv4 AutoIP (Zeroconf) or IPv6 Autoconfiguration (SLAAC-RA) status"""
        status = self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:AUTOCONF:STATUS?', result=ScpiChars).as_string()
        self.device.raise_error()

        return SenseX1000Base.IPv4AutoconfStatus[status] if ipversion == SenseX1000Base.IPVersion.IPV4 else \
            SenseX1000Base.IPv6AutoconfStatus[status]

    def comm_lan_ip_dhcp_enable(self, enabled: Optional[bool] = None, ipversion: Optional[SenseX1000Base.IPVersion] = SenseX1000Base.IPVersion.IPV4) -> bool:
        """Enables or disables IPv4 or IPv6 DHCP"""
        if enabled is not None:
            self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:DHCP', param=ScpiBool(enabled))
        else:
            enabled = self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:DHCP?', result=ScpiBool)

        self.device.raise_error()
        return enabled

    def comm_lan_ip_dhcp_status(self, ipversion: Optional[SenseX1000Base.IPVersion] = SenseX1000Base.IPVersion.IPV4) -> Union[SenseX1000Base.IPv4DHCPStatus,
                                                                                                                              SenseX1000Base.IPv6DHCPStatus]:
        """Returns the current IPv4/IPv6 DHCP status"""
        status = self.device.execute(f'SYST:COMM:LAN:IP{ipversion.value}:DHCP:STATUS?', result=ScpiChars).as_string()
        self.device.raise_error()

        return SenseX1000Base.IPv4DHCPStatus[status] if ipversion == SenseX1000Base.IPVersion.IPV4 else \
            SenseX1000Base.IPv6DHCPStatus[status]

    def comm_lan_dns_servers(self, servers: Optional[Iterable[str]] = None) -> Iterable[str]:
        """Sets or gets a list of system-wide DNS servers"""
        if servers is not None:
            self.device.execute('SYST:COMM:LAN:DNS:SERVERS', param=ScpiString(','.join(servers)))
        else:
            servers = self.device.execute('SYST:COMM:LAN:DNS:SERVERS?', result=ScpiString).as_string().split(',')

        self.device.raise_error()
        return servers

    def comm_lan_ntp_servers(self, servers: Optional[Iterable[str]] = None) -> Iterable[str]:
        """Set or get a list of system-wide NTP servers"""
        if servers is not None:
            self.device.execute('SYST:COMM:LAN:NTP:SERVERS', param=ScpiString(','.join(servers)))
        else:
            servers = self.device.execute('SYST:COMM:LAN:NTP:SERVERS?', result=ScpiString).as_string().split(',')

        self.device.raise_error()
        return servers

    def comm_lan_ntp_sync(self) -> datetime.date:
        """Returns the date and time of last successful (S)NTP synchronization"""
        sync = self.device.execute('SYST:COMM:LAN:NTP:SYNC?', result=ScpiNumberArray).as_int_list()

        self.device.raise_error()
        return datetime.datetime(*sync) if sync != ([0] * len(sync)) else None

    def comm_lan_hostname(self, hostname: Optional[str] = None) -> str:
        """Sets or gets system hostname"""
        if hostname is not None:
            self.device.execute('SYST:COMM:LAN:HOSTNAME', param=ScpiString(hostname))
        else:
            hostname = self.device.execute('SYST:COMM:LAN:HOSTNAME?', result=ScpiString).as_string()

        self.device.raise_error()
        return hostname

    def comm_lan_eui48(self) -> bytes:
        """Returns EUI-48 hardware address (MAC address)"""
        eui48 = self.device.execute('SYST:COMM:LAN:EUI48?', result=ScpiNumberArray).as_int_list()

        self.device.raise_error()
        return bytes(eui48)

    def comm_lan_eui64(self) -> bytes:
        """Returns EUI-64 hardware address"""
        eui64 = self.device.execute('SYST:COMM:LAN:EUI64?', result=ScpiNumberArray).as_int_list()

        self.device.raise_error()
        return bytes(eui64)

    def comm_lan_mdns_sd(self, enabled: Optional[bool] = None) -> bool:
        """Enables or disables mDNS-SD (Service Discovery) advertising"""
        if enabled is not None:
            self.device.execute('SYST:COMM:LAN:MDNS:SD', param=ScpiBool(enabled))
        else:
            enabled = self.device.execute('SYST:COMM:LAN:MDNS:SD?', result=ScpiBool).as_bool()

        self.device.raise_error()
        return enabled

    def comm_lan_lldp_advertising(self, enabled: Optional[bool] = None) -> bool:
        """Enables or disables LLDP capabilities advertising"""
        if enabled is not None:
            self.device.execute('SYST:COMM:LAN:LLDP:ADV', param=ScpiBool(enabled))
        else:
            enabled = self.device.execute('SYST:COMM:LAN:LLDP:ADV?', result=ScpiBool).as_bool()

        self.device.raise_error()
        return enabled