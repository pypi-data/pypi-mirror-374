from typing import List, Dict, Optional, Tuple
from ipaddress import IPv4Address


from ntc_templates.parse import parse_output
from netaddr import EUI, mac_unix_expanded

from .base import (
    BaseDevice,
    ARPTableEntry,
    MACTableEntry,
    Interface,
    LLDPNeighbor,
    EVPNMacIPEntry,
)
from ...utils import NXOS_ABBRS, age_to_timedelta

SPEED = {
    "Auto-speed": "auto",
    "10 Mb/s": "10",
    "100 Mb/s": "100",
    "1000 Mb/s": "1000",
    "10 Gb/s": "10G",
    "25 Gb/s": "25G",
    "40 Gb/s": "40G",
    "100 Gb/s": "100G",
}
DUPLEX = {
    "half": "half",
    "full": "full",
}


def _normalize_ifname(name: str) -> str:
    """
    Some IOS platforms return fully-qualified interface identifiers, e.g.
    'GigabitEthernet1/1' whereas others use abbreviated names e.g. 'Gi1\1'.
    Since the NCS switchport services uses abbreviated versions for IOS,
    this function will convert the names returned by the device to the
    shortened version
    """
    for abbr, full in NXOS_ABBRS.items():

        if name.startswith(full):
            return abbr + name.split(full)[1]

    return name


class NXOS(BaseDevice):
    def _run_cmd(self, command: str) -> str:
        """
        use NCS live-status exec to issue a raw show command towards a device.
        platform-specific models are expected to parse this output and return
        structured data.

        :param command: string CLI command, minus the 'show', e.g. 'interface status'
        :returns: raw string output from the device
        """
        show = self.device.live_status.__getitem__("exec").show
        inp = show.get_input()
        inp.args = [command]

        return show.request(inp)

    def get_interface_details(self, interface: Optional[str] = None) -> List[Interface]:
        """
        Gathers interface operational data from an NXOS device by parsing 'show interface'

        see the ntc_templates test data for this template for details on output structure:
        https://github.com/networktocode/ntc-templates/tree/master/tests/cisco_nxos/show_interface

        parsed_sample:
        - interface: "Ethernet1/1"
            link_status: "up"
            admin_state: ""
            hardware_type: "1000/10000 Ethernet"
            address: "8c60.4f4e.93a8"
            bia: "8c60.4f4e.93a8"
            description: "Uplink Fex131"
            ...
        """
        # ncs automatically adds the 'show' to the front of the cmd
        self.log.debug(f"sending 'show interface' to {self.device.name}")
        command = f"interface {interface}" if interface else "interface"
        reply = self._run_cmd(command)
        # self.log.debug(f" <<<{ self.device.name }>>>: {reply.result}")

        parsed = parse_output(
            platform="cisco_nxos",
            command="show interfaces",
            data=reply.result,
        )

        output = []
        for entry in parsed:
            input_errors = (
                0 if entry["input_errors"] == "" else int(entry["input_errors"])
            )
            output_errors = (
                0 if entry["output_errors"] == "" else int(entry["output_errors"])
            )

            i_name = _normalize_ifname(entry["interface"])
            interface = Interface(
                name=i_name,
                description=entry["description"],
                admin_status="enabled" if "up" in entry["admin_state"] else "disabled",
                oper_status="up" if "up" in entry["link_status"] else "down",
                duplex=DUPLEX.get(entry["duplex"], "auto"),
                speed=SPEED.get(entry["speed"], "auto"),
                input_errors=input_errors,
                output_errors=output_errors,
                last_flapped=age_to_timedelta(entry["last_link_flapped"]),
            )

            if interface.name.startswith("Vlan"):
                interface.is_logical = True

            output.append(interface)

        return output

    def get_bfd_neighbors(self, interface: Optional[str] = None) -> List[Dict]:
        """
        Gathers bfd operational data from an NXOS device by parsing 'show bfd neighbors'

        see the ntc_templates test data for this template for details on output structure:
        https://gitlab.umich.edu/grundler/ntc-templates/-/tree/add-nxos-show-bfd-neighbors/tests/cisco_nxos/show_bfd_neighbors

        ---
        parsed_sample:
          - our_addr: "172.23.0.18"
            neigh_addr: "172.23.0.19"
            ld_rd: "1090540255/1090566886"
            rh_rs: "Up"
            holddown: "862(3)"
            state: "Up"
            interface: "Eth1/10"
            vrf: "default"
            type: "SH"
        """
        self.log.debug(f"sending 'show bfd neighbors' to {self.device.name}")
        command = "bfd neighbors"
        reply = self._run_cmd(command)
        # self.log.debug(f" <<<{ self.device.name }>>>: {reply.result}")

        return parse_output(
            platform="cisco_nxos",
            command="show " + command,
            data=reply.result,
        )

    def get_ospf_neighbors(self, interface: Optional[str] = None) -> List[Dict]:
        """
        Gathers live ospf operational data from an NXOS device by parsing 'show
        ip ospf neighbor'

        see the ntc_templates test data for this template for details on output structure:
        https://github.com/networktocode/ntc-templates/tree/master/tests/cisco_nxos/show_ip_ospf_neighbor

        ---
        parsed_sample:
          - interface: "Vlan999"
            local_ipaddr: "11.11.11.11"
            neighbor_ipaddr: "10.0.0.1"
            ospf_pid: "1111"
            state: "FULL/ -"
            uptime: "8w6d"
            vrf: "CUSTVRF1"
        """
        self.log.debug(f"sending 'show ip ospf neighbor' to {self.device.name}")
        command = "ip ospf neighbor"
        reply = self._run_cmd(command)
        # self.log.debug(f" <<<{ self.device.name }>>>: {reply.result}")

        return parse_output(
            platform="cisco_nxos",
            command="show " + command,
            data=reply.result,
        )

    def get_lldp_neighbors(self, interface: Optional[str] = None) -> List[LLDPNeighbor]:
        """
        Gathers live operational data about physically connected devices from an
        NXOS device by parsing 'show lldp neighbors'

        see the ntc_templates test data for this template for details on output structure:
        https://github.com/networktocode/ntc-templates/tree/master/tests/cisco_nxos/show_lldp_neighbors

        ---
        parsed_sample:
          - neighbor: "nx-osv9000-3-long-name.com"
            local_interface: "Eth1/1"
            neighbor_interface: "Ethernet1/1"
        """
        self.log.debug(f"sending 'show lldp neighbors' to {self.device.name}")
        command = "lldp neighbors detail"
        reply = self._run_cmd(command)
        # self.log.debug(f" <<<{ self.device.name }>>>: {reply.result}")

        parsed = parse_output(
            platform="cisco_nxos",
            command="show lldp neighbors detail",
            data=reply.result,
        )

        ret = []
        for entry in parsed:
            record = LLDPNeighbor(
                local_interface=entry["local_interface"],
                remote_interface=entry["neighbor_interface"],
                remote_system_name=entry["neighbor"],
                remote_system_description=entry.get("system_description"),
            )
            if interface is None or entry["local_interface"] == interface:
                ret.append(record)

        return ret

    def get_transceiver_details(self, interface: Optional[str] = None) -> List[Dict]:
        """
        Gathers live operational state DOM information from an NXOS device by
        parsing 'show interface tranceiver details'

        see the ntc_templates test data for this template for details on output structure:
        https://github.com/networktocode/ntc-templates/tree/master/tests/cisco_nxos/show_interface_transceiver_details

        ---
        parsed_sample:
          - interface: "Ethernet3/1"
            lane: ""
            temperature_value: "35.66"
            temperature_alarm_high: "75.00"
            temperature_alarm_low: "-5.00"
            temperature_warn_high: "70.00"
            temperature_warn_low: "0.00"
            voltage_value: "3.29"
            voltage_alarm_high: "3.63"
            voltage_alarm_low: "2.97"
            voltage_warn_high: "3.46"
            voltage_warn_low: "3.13"
            amps_value: "N/A"
            amps_alarm_high: "11.80"
            amps_alarm_low: "4.00"
            amps_warn_high: "10.80"
            amps_warn_low: "5.00"
            rx_value: "-30.45"
            rx_alarm_high: "2.00"
            rx_alarm_low: "-13.90"
            rx_warn_high: "-1.00"
            rx_warn_low: "-9.90"
            tx_value: "-14.05"
            tx_alarm_high: "1.69"
            tx_alarm_low: "-11.30"
            tx_warn_high: "-1.30"
            tx_warn_low: "-7.30"
        """
        self.log.debug(
            f"sending 'show interface transceiver details' to {self.device.name}"
        )
        command = "interface transceiver details"
        reply = self._run_cmd(command)
        # self.log.debug(f" <<<{ self.device.name }>>>: {reply.result}")

        return parse_output(
            platform="cisco_nxos",
            command="show " + command,
            data=reply.result,
        )

    def get_arp_table(
        self, address: Optional[str] = None, vrf: Optional[str] = None
    ) -> List[ARPTableEntry]:
        """
        Gathers live operational state ARP information from an NXOS device by
        parsing 'show ip arp detail vrf all'

        see the ntc_templates test data for this template for details on output structure:
        https://github.com/networktocode/ntc-templates/tree/master/tests/cisco_nxos/show_ip_arp_detail

        NB: see https://github.com/networktocode/ntc-templates/pull/1204 -- this PR adds support for
        adding 'vrf all' to the CLI command which is required for our use case.

        ---
        parsed_sample:
          - address: "192.168.56.2"
            age: "00:17:02"
            mac: "5087.89a1.d8d5"
            interface: "Ethernet1/2"
            physical_interface: "Ethernet1/2"
            flags: "+"
            vrf: "PRIMARY"
          - address: "90.10.10.2"
            age: "00:02:55"
            mac: "000d.ece7.df7c"
            interface: "Vlan900"
            physical_interface: "Ethernet1/12"
            flags: ""
            vrf: "PRIMARY"
        """
        self.log.debug(f"sending 'show ip arp detail vrf all' to {self.device.name}")
        command = "ip arp detail vrf all"
        reply = self._run_cmd(command)
        # self.log.debug(f" <<<{ self.device.name }>>>: {reply.result}")

        parsed = self._parse_textfsm(
            "cisco_nxos_show_ip_arp_detail_vrf_all", reply.result
        )

        if address is not None:
            normalized_address = IPv4Address(address)

        output = []
        for entry in parsed:
            if entry["mac"] == "INCOMPLETE":
                continue

            if entry["physical_interface"] == "":
                interface = entry["interface"]
            else:
                interface = entry["physical_interface"]

            entry_vrf = None if entry["vrf"] == "" else entry["vrf"]
            normalized_entry_address = IPv4Address(entry["address"])

            if address is None or normalized_address == normalized_entry_address:
                arp = ARPTableEntry(
                    ip_address=IPv4Address(entry["address"]),
                    mac_address=EUI(entry["mac"], dialect=mac_unix_expanded),
                    interface=interface,
                    vrf=entry_vrf,
                )
                output.append(arp)

        return output

    def get_mac_table(self, mac: Optional[str] = None) -> List[MACTableEntry]:
        """
        Gathers learned MAC addresses from an NXOS device by parsing 'show mac address-table dynamic'.

        :mac: optionally filter device output by MAC address

        see the ntc_templates test data for this template for details on output structure:
        https://github.com/networktocode/ntc-templates/tree/master/tests/cisco_nxos/show_mac_address-table

        ---
        parsed_sample:
          - vlan: "100"
            mac: "5087.89a1.de75"
            type: "static"
            age: "-"
            secure: "F"
            ntfy: "F"
            ports: "sup-eth1(R)"
        """
        command = "mac address-table dynamic"
        if mac is not None:
            normalized_mac = EUI(mac, dialect=mac_unix_expanded)
            command = command + f" address {mac}"

        self.log.debug(f"sending 'show {command}' to {self.device.name}")
        reply = self._run_cmd(command)
        # self.log.debug(f" <<<{ self.device.name }>>>: {reply.result}")

        parsed = parse_output(
            platform="cisco_nxos",
            command="show mac address-table",
            data=reply.result,
        )

        output = []
        for entry in parsed:
            try:
                vid = int(entry["vlan"])
            except ValueError:
                vid = None

            normalized_entry_mac = EUI(entry["mac"], dialect=mac_unix_expanded)

            if mac is None or normalized_mac == normalized_entry_mac:
                mac_entry = MACTableEntry(
                    address=normalized_entry_mac,
                    vlan_id=vid,
                    interface=entry["ports"],
                )
                output.append(mac_entry)

        return output

    def get_evpn_mac_ip(self, mac_or_ip: str = None) -> List[EVPNMacIPEntry]:
        """
        Parses "show bgp l2vpn evpn [route-type 2 | [mac_or_ip]]" and returns
        a list of evpn mac IP Entries.

        Note - this function doesn't validate the mac_or_ip input, we assume
        that it is well-formatted.
        """

        if mac_or_ip:
            command = f"bgp l2vpn evpn {mac_or_ip}"
        else:
            command = f"bgp l2vpn evpn route-type 2"

        reply = self._run_cmd(command)
        parsed = self._parse_textfsm(
            "cisco_nxos_show_bgp_l2vpn_evpn_macip", reply.result
        )

        # textfsm template returns a list of lists [mac, ip, vtep]
        # because of ecmp there will be duplicate entries.
        output = []
        for host in parsed:
            entry = EVPNMacIPEntry(
                mac_address=self.normalize_mac(host["mac_address"]),
                ip_address=host["ip"],
                remote_vtep=host["vtep_ip"],
            )
            if entry not in output:
                output.append(entry)

        return output
