import ncs, _ncs
from _ncs.maapi import get_authorization_info, get_rollback_id
import re
from datetime import timedelta

from typing import Union

DC_VNI_PREFIXES = {
    "mdc": 10000,
    "macc": 20000,
}

IOS_ABBRS = {
    "Fa": "FastEthernet",
    "Gi": "GigabitEthernet",
    "Te": "TenGigabitEthernet",
    "Twe": "TwentyFiveGigE",
    "Tw": "TwoGigabitEthernet",
    "Po": "Port-channel",
}

NXOS_ABBRS = {
    "Eth": "Ethernet",
    "Po": "port-channel",
}

EQDB_MODEL_TO_NED = {
    "^EX[234]200": "juniper-junos12-nc-4.7",
    "^EX3300": "juniper-junos12-nc-4.7",
    "^EX45[05]0": "juniper-junos12-nc-4.7",
    "^EX2300": "juniper-junos17-nc-4.7",
    "^EX3400": "juniper-junos17-nc-4.7",
    "^QFX": "juniper-junos17-nc-4.7",
    "^EX4600": "juniper-junos17-nc-4.7",
    "^WS-C": "cisco-ios-cli-6.106",
    "^CDB-8U$": "cisco-ios-cli-6.106",
    "^C9[23]00": "cisco-ios-cli-6.106",
    "^ME-3800X": "cisco-ios-cli-6.106",
    "^C1000": "cisco-ios-cli-6.106",
    "^N[39]K": "cisco-nx-cli-5.23",
}

ISL_TRUNK_PLATFORMS = [
    "WS-C3560-24TS",
    "WS-C3560-48PS",
    "WS-C3560-48TS",
    "WS-C3560E-48TD",
    "WS-C3560-24PS",
    "WS-C3560G-24PS",
    "WS-C3560G-24TS",
    "WS-C3560G-48PS",
    "WS-C3560G-48TS",
    "WS-C3560G-48TS-S",
    "WS-C3560V2-48TS",
    "WS-C3560X-48",
    "WS-C3560X-48P",
    "WS-C3650-48PD",
    "WS-C3750-48P",
    "WS-C3750-48TS",
    "WS-C3750E-24PD",
    "WS-C3750E-48PD",
    "WS-C3750E-48TD",
    "WS-C3750G-12S",
    "WS-C3750G-24PS",
    "WS-C3750G-24TS",
    "WS-C3750G-24TS-1U",
    "WS-C3750G-48PS",
    "WS-C3750G-48TS",
    "WS-C3750X-48",
    "WS-C3750X-48P",
    "WS-C4503",
    "WS-C4506",
    "WS-C4506-E",
    "WS-C4507R",
    "WS-C4948-10GE",
    "WS-C4948E-F",
    "WS-C6504-E",
    "WS-C6506-E",
    "WS-C6509-E",
]

VPC_PORT_ASSIGNMENTS = {
    "C93360YC-FX2": ["Eth1/99", "Eth1/100"],
    "C93180YC-FX": ["Eth1/51", "Eth1/52"],
    "N3K-C36180YC-R": ["Eth1/51", "Eth1/52"],
    "C9504": ["Eth1/50", "Eth2/50"],
    "N3K-C3636C-R": ["Eth1/35", "Eth1/36"],
}


def model_to_ned_id(model):
    """
    Returns ned-id for a specific rancid platform
    """
    for pattern, ned_id in EQDB_MODEL_TO_NED.items():
        if re.match(pattern, model):
            return ned_id

    raise LookupError(f"No valid ned id for rancid device model {model}")


def get_users_groups(trans, uinfo):
    # Get the maapi socket
    s = trans.maapi.msock
    auth = get_authorization_info(s, uinfo.usid)
    return list(auth.groups)


def dns_to_device_name(dns_name: str) -> str:
    """Converts a DNS name to a device hostname"""

    return dns_name.replace(".umnet.umich.edu", "").lower()


def handle_commit(
    t, input, output, logging=None, commit_queue=False, no_networking=False
):
    """
    Generates the appropriate commit commands based on the umnet-action
    input - refer to dlzone-action-input grouping in actions.yang
    """
    if logging is not None:
        output.messages = logging.get_output_logs()

    if output.result == None:
        output.result = ""

    commit_params = ncs.maapi.CommitParams()

    if hasattr(input, "reconcile") and input.reconcile.exists():
        commit_params.reconcile_keep_non_service_config()

    if input.dry_run.exists():
        if input.dry_run.outformat == "native":
            commit_params.dry_run_native()
            result = t.apply_params(True, params=commit_params)

            dry_run_output = result.get("device")
            if dry_run_output:
                # it's ugly - but would rather hand-build the string
                # then mess with the yang structure of the output to figure
                # out how to get the native data to look nice
                output.result += "device {\n"
                for device, cmds in dry_run_output.items():
                    output.result += f"\t{device}" + " {\n"
                    for cmd in cmds.split("\n"):
                        output.result += f"\t\t{cmd}\n"
                    output.result += "\t}\n"

                output.result += "}"

        elif input.dry_run.outformat == "xml":
            commit_params.dry_run_xml()
            result = t.apply_params(True, params=commit_params)
            output.result += str(result.get("local-node"))
        else:
            commit_params.dry_run_cli()
            result = t.apply_params(True, params=commit_params)
            output.result += str(result.get("local-node"))

    elif ("no_networking" in input and input.no_networking) or no_networking:
        commit_params.no_networking()
        result = t.apply_params(True, params=commit_params)
        output.result = f"true: rollback ID {get_rollback_id(t.maapi.msock, t.th)}"

    elif commit_queue:
        commit_params.commit_queue_non_atomic()
        commit_params.commit_queue_async()
        result = t.apply_params(True, params=commit_params)
        output.result = f"true: commit queue ID: {result.get('id',False)}"

    else:
        result = t.apply()
        output.result = f"true: rollback ID {get_rollback_id(t.maapi.msock, t.th)}"


def hostname_to_codename(hostname: str) -> str:
    """
    generates a short codename from the provided hostname to be used in netnames

    'dl-arbl-1' -> 'ARBL1'
    """
    prefix, shortname, instance = hostname.split("-")
    return shortname.upper() + instance


def validate_existing_port(port: str, device: ncs.maagic.Node, log) -> bool:
    """
    Validates a port name against a device in the device tree.
    The inputted port should follow the abbreviation standards we use for cisco.
    The device should be a maagic node at /root/devices/device
    - look at /packages/umnet-ifconfig/python/umnet_ifconfig/validate.py

    """

    log.info(f"validating {device.name} {port}")
    ned_id = ncs.application.get_ned_id(device)

    # for junos all the ports are just keys into
    # /interfaces/interface
    if ned_id.startswith("juniper-junos"):
        port_list = device.config.configuration.interfaces.interface

    # for nxos and ios each interface type is its own container, and we
    # have to expand the interface name to match the right container name
    else:
        if ned_id.startswith("cisco-ios"):
            ABBRS = IOS_ABBRS
        elif ned_id.startswith("cisco-nx"):
            ABBRS = NXOS_ABBRS
        else:
            raise NotImplementedError(f"unsupported ned-id {ned_id}")

        for short, long in ABBRS.items():
            if port.startswith(short):
                port = port.replace(short, long)

        m = re.match("([A-Za-z_]+)(\d.*)$", port)
        if m:
            prefix = m.group(1)
            port = m.group(2)
            log.info(f"prefix and port: {prefix} {port}")
            port_list = getattr(device.config.interface, prefix)
        else:
            raise ValueError(f"Invalid port {port} for {device.name} (ned-id {ned_id})")

    if port in port_list:
        return True
    else:
        return False


def cli_write(trans: ncs.maapi.Transaction, msg: str):
    """
    output string to user CLI session.  trans must be the 'outtermost'
    transaction that the user opened when they invoked the action.
    """
    sock = trans.maapi.msock
    session_id = trans.maapi.get_my_user_session_id()
    return _ncs.maapi.cli_write(sock, session_id, msg + "\n")


def age_to_timedelta(age: str) -> Union[timedelta, str]:
    """
    Across platforms age strings can be:
    10y5w, 5w4d, 05d04h, 01:10:12, 3w4d 01:02:03
    37week(s), 4day(s), Never (for last flapped)
    """
    days = 0
    hours = 0
    minutes = 0
    seconds = 0

    m = re.search(r"[Nn]ever", age)
    if m:
        return "Never"

    # year match (eg "10y" or "10year(s)")
    m = re.search(r"(?P<years>\d+)y(ear\(s\))*", age)
    if m:
        days += int(m.group("years")) * 365
    # weeks match (eg "5w" or "5week(s)")
    m = re.search(r"(?P<weeks>\d+)w(eek\(s\))*", age)
    if m:
        days += int(m.group("weeks")) * 7
    # days match (eg "10d" or "10day(s)")
    m = re.search(r"(?P<days>\d+)d(ay\(s\))*", age)
    if m:
        days += int(m.group("days"))
    # hours match
    m = re.search(r"(?P<hours>\d+)h(our\(s\))*", age)
    if m:
        hours += int(m.group("hours"))

    # hours/minutes/seconds timestamp match
    m = re.search(r"(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)$", age)
    if m:
        if m.group("hours"):
            hours += int(m.group("hours"))
        if m.group("minutes"):
            minutes += int(m.group("minutes"))
        if m.group("seconds"):
            seconds += int(m.group("seconds"))

    return timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )
