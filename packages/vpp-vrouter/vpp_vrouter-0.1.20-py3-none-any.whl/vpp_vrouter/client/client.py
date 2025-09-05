"""
Client for VPP configuration server
"""

import time
from typing import Callable, List

from vpp_vrouter.common.utils import configure_pyro5_logging

configure_pyro5_logging()  # must be before any Pyro5 import to configure logging
from Pyro5.api import Proxy

from vpp_vrouter.common import serializers
from vpp_vrouter.common.models import ConfigurationItemDetail


class ExtendedVPPAPIClient(Proxy):
    """Python VPP client based on fd.io VPP client, but with new customized API and additional capabilities.

    This is the basic entry point for configuration using this repository as python VPP configuration solution
    """

    def __init__(self, server_host: str = "0.0.0.0", server_port: int = 9999):
        """Creates and initializes extended VPP client

        :param server_host: hostname/ip address of the Pyro5 nameserver
        :param server_port: port of the Pyro5 nameserver
        """
        serializers.import_pyro5_serializers()  # fix for serializing of custom types
        super().__init__(f"PYRONAME:extended.papi@{server_host}:{server_port}")

    def wait_for_configuration(
        self,
        configuration_check: Callable[[List[ConfigurationItemDetail]], bool],
        retry_count: int = -1,
        delay: float = 0.5,
    ):
        """Waits for configuration to pass the provided configuration check"""
        while retry_count > 0 or retry_count <= -1:
            if configuration_check(self.get_configuration().items):
                return
            time.sleep(delay)
            retry_count = retry_count - 1


class BasicVPPAPIClient(Proxy):
    """Wrapper for original fd.io VPP python client that should have provide the same functionality with the difference
    of using client/server architecture (the Pyro5 library).

    Currently the problem is the serialization of the data sending to/receiving from server that should configure VPP.
    The input/output data from fd.io paython client is not serializable and is received/sent through Pyro5 library that
    uses serialization in garbled state (problem is mostly with the fd.io python client response)
    """

    def __init__(self):
        serializers.import_pyro5_serializers()  # fix for serializing of custom types
        super().__init__("PYRONAME:papi")
