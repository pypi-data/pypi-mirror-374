from ..models.junos import Junos, Junos12
from ..models.nxos import NXOS
from ..models.ios import IOS

from ncs.application import get_ned_id


def get_parser(device):
    """
    instantiate and return the appropriate device state parsing model.
    """
    ned_id = get_ned_id(device)
    if ned_id.startswith("cisco-ios"):
        return IOSParser(root, device, log)
    elif ned_id.startswith("juniper-junos12"):
        return Junos12Parser(root, device, log)
    elif ned_id.startswith("juniper-junos17"):
        return Junos17Parser(root, device, log)
    else:
        raise NotImplementedError(f"Unsupported ned-id {ned_id}")
