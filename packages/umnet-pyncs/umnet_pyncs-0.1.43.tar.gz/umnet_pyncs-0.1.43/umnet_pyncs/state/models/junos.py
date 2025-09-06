import re
from typing import List, Optional
from ipaddress import IPv4Address

from netaddr import EUI, mac_unix_expanded

from .base import BaseDevice, ARPTableEntry, MACTableEntry, Interface, LLDPNeighbor
from ...utils import age_to_timedelta

VALID_PORTS = re.compile(r"^(ge|xe|ae|et)")

ADMIN_STATUS = {
    "up": "enabled",
    "down": "disabled",
}

OPER_STATUS = {"up": "up", "down": "down"}

DUPLEX = {
    "Half-duplex": "half",
    "Full-duplex": "full",
}

SPEED = {
    "Auto": "auto",
    "10mbps": "10",
    "100mbps": "100",
    "1000mbps": "1000",
    "10Gbps": "10G",
    "25000mbps": "25G",
    "40Gbps": "40G",
    "100Gbps": "100G",
}


class Junos(BaseDevice):
    def get_interface_details(self, interface: Optional[str] = None) -> List[Interface]:
        """
        issue the junos RPC <get-interface-information> and return normalized output

        physical-interface {
            name ge-0/0/1
            admin-status up
            oper-status down
            description DEFAULT
            link-mode Half-duplex
            speed Auto
            ...
        """
        output = []

        rpc = (
            self.device.rpc.jrpc__rpc_get_interface_information.get_interface_information
        )
        inp = rpc.get_input()
        inp.statistics.create()

        # First we're getting interface information
        if interface:
            inp.interface_name = interface

        self.log.debug(f"sending <get-inteface-information> to {self.device.name}")
        reply = rpc(inp)

        # save the fields we care about in our output as normalized data
        for i in reply.interface_information.physical_interface:
            if not (VALID_PORTS.match(i.name)):
                continue

            # interface flapped data contains both the actual date/time that it flapped
            # and how long ago - we need to peel out the delta (how long ago)
            m = re.match(r"\((?P<delta>\S+) ago\)$", i.interface_flapped)
            if m:
                i.interface_flapped = m.group("delta")

            if (not (interface)) or (interface and interface == i.name):
                record = Interface(
                    name=i.name,
                    description=i.description,
                    admin_status=ADMIN_STATUS[i.admin_status],
                    oper_status=OPER_STATUS[i.oper_status],
                    speed=SPEED.get(i.speed, "auto"),
                    duplex=DUPLEX.get(i.link_mode, "auto"),
                    input_errors=int(i.input_error_count),
                    output_errors=int(i.output_error_count),
                    last_flapped=age_to_timedelta(i.interface_flapped),
                )
                output.append(record)

        return output

    def get_mac_table(self, mac: Optional[str] = None) -> List[MACTableEntry]:
        """
        issue the junos RPC <get-ethernet-switching-table-information><brief/> and return normalized output

        optionally filter the by the given mac address

        ...
        l2ng-mac-entry {
            l2ng-l2-mac-vlan-name VLAN0009
            l2ng-l2-mac-address cc:88:c7:cc:15:b3
            l2ng-l2-mac-flags D
            l2ng-l2-mac-age -
            l2ng-l2-mac-logical-interface ge-0/0/37.0
            l2ng-l2-mac-fwd-next-hop 0
            l2ng-l2-mac-rtr-id 0
        }
        ...
        """

        rpc = (
            self.device.rpc.jrpc__rpc_get_ethernet_switching_table_information.get_ethernet_switching_table_information
        )
        inp = rpc.get_input()
        inp.brief.create()

        if mac is not None:
            normalized_mac = EUI(mac, dialect=mac_unix_expanded)
            inp.address = str(normalized_mac)

        self.log.debug(
            f"sending <get-ethernet-switching-table-information> to {self.device.name}"
        )
        reply = rpc(inp)
        output = []

        # NB: not all junos devices are consistent in how these data are
        # populated.  in particular EX-series devices appear to only have a
        # single l2ald_mac_entry_vlan yang list that is populated with mac
        # addresses for all VLANs
        for vlan in reply.l2ng_l2ald_rtb_macdb.l2ng_l2ald_mac_entry_vlan:
            for entry in vlan.l2ng_mac_entry:
                entry_interface = entry.l2ng_l2_mac_logical_interface.replace(".0", "")
                if not (VALID_PORTS.match(entry_interface)):
                    continue

                vid = self.device.config.configuration.vlans.vlan[
                    entry.l2ng_l2_mac_vlan_name
                ].vlan_id

                entry_mac = entry.l2ng_l2_mac_address
                normalized_entry_mac = EUI(entry_mac, dialect=mac_unix_expanded)

                if mac is None or normalized_mac == normalized_entry_mac:
                    record = MACTableEntry(
                        address=normalized_entry_mac,
                        vlan_id=vid,
                        interface=entry_interface,
                    )
                    output.append(record)

        return output

    def get_arp_table(
        self, address: Optional[str] = None, vrf: Optional[str] = None
    ) -> List[ARPTableEntry]:
        """
        issue the junos RPC <get-arp-table-information> and return normalized output

        ...
        arp-table-entry {
            mac-address 3c:8b:7f:24:41:67
            ip-address 10.233.0.2
            hostname v-mgmt-arbl.dl-arbl-1.umnet.umich.edu
            interface-name irb.3 [ge-0/2/0.0]
            arp-table-entry-flags {
                none
            }
        }
        ...
        """

        rpc = (
            self.device.rpc.jrpc__rpc_get_arp_table_information.get_arp_table_information
        )
        inp = rpc.get_input()
        if address:
            inp.hostname = address

        self.log.debug(f"sending <get-arp-table-information> to {self.device.name}")
        reply = rpc(inp)

        output = []
        for a in reply.arp_table_information.arp_table_entry:
            if (not (address)) or (address and address == a.ip_address):
                record = ARPTableEntry(
                    ip_address=IPv4Address(a.ip_address),
                    mac_address=EUI(a.mac_address, dialect=mac_unix_expanded),
                    interface=a.interface_name,
                    vrf=vrf,
                )
                output.append(record)

        return output

    def get_lldp_neighbors(self, interface=False) -> List[LLDPNeighbor]:
        """
        Gathers live operational data about other devices physicall connected to a
        JUNOS device by issuing the get-lldp-neighbors-information RPC.

        ...
        lldp-neighbor-information {
            lldp-local-port-id ge-0/2/0
            lldp-local-parent-interface-name -
            lldp-remote-chassis-id-subtype Mac address
            lldp-remote-chassis-id 3c:8b:7f:24:41:8f
            lldp-remote-port-description s-arbl1-1909-9 ge-0/2/0
            lldp-remote-system-name dl-arbl-1.umnet.umich.edu
        }
        """
        ret = []

        rpc = (
            self.device.rpc.jrpc__rpc_get_lldp_neighbors_information.get_lldp_neighbors_information
        )
        inp = rpc.get_input()

        self.log.debug(f"sending <get-lldp-neighbor-information> to {self.device.name}")
        reply = rpc(inp)

        for n in reply.lldp_neighbors_information.lldp_neighbor_information:
            record = LLDPNeighbor(
                local_interface=n.lldp_local_port_id,
                remote_interface=n.lldp_remote_port_description,
                remote_system_name=n.lldp_remote_system_name,
            )
            if interface is False or n.lldp_local_port_id == interface:
                ret.append(record)

        return ret


class Junos12(Junos):
    def get_mac_table(self, mac: Optional[str] = None) -> List[MACTableEntry]:
        """
        issue the junos RPC <get-interface-information> and return normalized output

        ...
        mac-table-entry {
            mac-vlan VLAN0020
            mac-address 00:50:f9:01:3e:94
            mac-type Learn
            mac-age 0
            mac-interfaces-list {
                mac-interfaces ge-0/0/38.0
            }
        }
        ...

        """

        if mac is not None:
            normalized_mac = EUI(mac, dialect=mac_unix_expanded)

        rpc = (
            self.device.rpc.jrpc__rpc_get_ethernet_switching_table_information.get_ethernet_switching_table_information
        )
        inp = rpc.get_input()
        reply = rpc(inp)

        mac_table = (
            reply.ethernet_switching_table_information.ethernet_switching_table.mac_table_entry
        )

        output = []
        for entry in mac_table:
            entry_interface = entry.mac_interfaces_list.mac_interfaces.replace(".0", "")
            if (entry.mac_type != "Learn") or not (VALID_PORTS.match(entry_interface)):
                continue

            normalized_entry_mac = EUI(entry.mac_address, dialect=mac_unix_expanded)
            vid = self.device.config.configuration.vlans.vlan[entry.mac_vlan].vlan_id

            if mac is None or normalized_mac == normalized_entry_mac:
                record = MACTableEntry(
                    address=normalized_entry_mac,
                    vlan_id=vid,
                    interface=entry_interface,
                )
                output.append(record)

        return output

    def get_lldp_neighbors(self, interface=False) -> List[LLDPNeighbor]:
        """
        handle the non-ELS juniper model.

        ...
        lldp-neighbor-information {
            lldp-local-interface ge-0/1/0.0
            lldp-local-parent-interface-name ae0.0
            lldp-remote-chassis-id-subtype Mac address
            lldp-remote-chassis-id 3c:8b:7f:24:41:77
            lldp-remote-port-description s-arbl1-1909-8 ge-0/1/0
            lldp-remote-system-name dl-arbl-1.umnet.umich.edu
        }

        NB: non-ELS junipers append the interface logical unit.  We could strip
        that out but it it will not solve the problem of how a non-ELS device shows
        up as a neighbor for OTHER devices.
        """
        ret = []

        rpc = (
            self.device.rpc.jrpc__rpc_get_lldp_neighbors_information.get_lldp_neighbors_information
        )
        inp = rpc.get_input()

        self.log.debug(f"sending <get-lldp-neighbor-information> to {self.device.name}")
        reply = rpc(inp)

        for n in reply.lldp_neighbors_information.lldp_neighbor_information:
            record = LLDPNeighbor(
                # s/local_port_id/local_interface/
                local_interface=n.lldp_local_interface.replace(".0", ""),
                remote_interface=n.lldp_remote_port_description,
                remote_system_name=n.lldp_remote_system_name,
            )

            if (
                interface is False
                or n.lldp_local_interface.replace(".0", "") == interface
            ):
                ret.append(record)

        return ret
