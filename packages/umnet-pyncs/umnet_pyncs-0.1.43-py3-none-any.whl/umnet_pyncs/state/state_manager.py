import os
import logging
import multiprocessing
from typing import List, Dict
from functools import partial
from dataclasses import dataclass

import ncs
import multiprocessing_logging

from .models.junos import Junos, Junos12
from .models.nxos import NXOS
from .models.ios import IOS


def get_model(device: ncs.maagic.Node, log: logging.Logger) -> "BaseDevice":
    """
    returns the relevant state parsing model based on ned-id
    """
    ned_id = ncs.application.get_ned_id(device)
    root = ncs.maagic.get_root(device)
    if ned_id.startswith("cisco-ios"):
        return IOS(device, log)
    elif ned_id.startswith("juniper-junos12"):
        return Junos12(device, log)
    elif ned_id.startswith("juniper-junos17"):
        return Junos(device, log)
    elif ned_id.startswith("cisco-nx"):
        return NXOS(device, log)
    else:
        raise NotImplementedError(f"Unsupported ned-id {ned_id}")


def exec_cmds(dev_name: str, commands: List[str], results_q: multiprocessing.Queue):
    """
    open a new read transaction to query dev_name and save results to the
    multiproccessing queue.  Assumes that the calling application has verified
    /devices/device{dev_name} exists and is valid.

    :param dev_name: string name of an NCS device
    :param commands: list of model methods to call
    :param results: multiprocessing.Queue to save results to
    """
    pid = os.getpid()

    logger = logging.getLogger()
    ret = {"name": dev_name, "results": {}}

    with ncs.maapi.single_read_trans("admin", "system") as t:
        root = ncs.maagic.get_root(t)
        device = root.devices.device[dev_name]
        model = get_model(device, logger)  ## e.g. ../models/nxos.py

        # test and see if we're able to connect to the device before attempting
        # to issue any commands
        connection = device.connect()
        if not connection.result:
            logger.error(
                f"pid: {pid}: ERROR unable to connect to {dev_name}: {connection.info}"
            )
            err_str = f"Unable to connect to {dev_name}: {connection.info}"
            for cmd in commands:
                ret["results"].update({cmd: {"errors": err_str}})
            results_q.put(ret)
            return

        for cmd in commands:
            method = cmd.replace("-", "_")
            if hasattr(model, method):
                try:
                    ret["results"][cmd] = {}
                    invoke = getattr(model, method)
                    logger.debug(f"pid: {pid}: invoking {cmd} against {dev_name}")
                    data = invoke()
                    ret["results"][cmd]["data"] = data
                except Exception as e:
                    logger.error(
                        f"pid: {pid}: ERROR issuing {cmd} against {dev_name}: {e}"
                    )
                    ret["results"][cmd]["errors"] = str(e)
            else:
                ret["results"][cmd]["errors"] = f"{model}.{cmd} unsupported"

        # logger.debug(f"return results for {dev_name}: {ret}")
        results_q.put(ret)


class StateManager:
    """
    simple class to manage multiprocessing state when issuing commands to many devices.

    uses https://github.com/jruere/multiprocessing-logging to safely handle logging
    from child processes.

    USAGE:
        import umnet_pyncs

        with umnet_pyncs.state.StateManager() as m:
            interfaces = m.get_state(al_devices, ["get-interface-details"])
            arp = m.get_state(dl_devices, ["get-arp-table"])
            ...
    """

    def __init__(self):
        self.log = logging.getLogger()  ## root ncs pyvm logger object
        self.manager = multiprocessing.Manager()
        self.results_q = self.manager.Queue()

    def __enter__(self):
        # wrap root ncs logger instance with a queue
        multiprocessing_logging.install_mp_handler()
        return self

    def __exit__(self, *args, **kwargs):
        # unwrap the original ncs pyvm file handler now that we're done
        multiprocessing_logging.uninstall_mp_handler()

    def get_state(self, devices: List[ncs.maagic.Node], commands: List[str]) -> Dict:
        """
        returns results for all devices/commands as a dict keyed by device
        name, e.g.:

        { 'name': 'pe-ilab-1',
          'results': {
              'get-interface-details': [...],
              'get-bfd-neighbors':     [...],
              ...
          }
          'errors': None,
        },
        ...
        """

        ret = {}
        num_procs = len(devices) if len(devices) < os.cpu_count() else os.cpu_count()
        dev_names = [d.name for d in devices]

        with multiprocessing.Pool(processes=num_procs) as pool:
            self.log.info(f"submitting commands to worker pool ({num_procs})")
            pool.map(
                partial(exec_cmds, commands=commands, results_q=self.results_q),
                dev_names,
            )
            pool.close()

        # read results from the queue and structure return data for easier access
        while not self.results_q.empty():
            result = self.results_q.get()
            dev_name = result["name"]
            ret[dev_name] = {}
            ret[dev_name] = result["results"]

        return ret
