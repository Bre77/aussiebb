#!/usr/bin/env python

""" pulls and lists the IPv6 addresess for your services """

from ipaddress import ip_network,  IPv4Network, IPv6Network
import json

import os
from pathlib import Path
import sys

script_path = Path(__file__)
sys.path.append(script_path.parent.parent.as_posix())


# pylint: disable=import-error,wrong-import-position
from aussiebb.asyncio import AussieBB
from aussiebb.types import AussieBBConfigFile


def configloader():
    """ loads config """
    for filename in [ os.path.expanduser("~/.config/aussiebb.json"), "aussiebb.json" ]:
        filepath = Path(filename).resolve()
        if filepath.exists():
            try:
                return AussieBBConfigFile.parse_file(filepath)
            except json.JSONDecodeError as json_error:
                sys.exit(f"Failed to parse config file: {json_error}")
def main():
    """ Example of getting ipv6 services """
    user = configloader().users[0]
    client = AussieBB(user.username, user.password)

    client.logger.debug("Logging in")
    client.login()


    services = client.get_services()
    found_networks = []
    if services is None:
        return
    for service in services:
        client.logger.debug(service)
        if 'ipAddresses' not in service:
            continue
        client.logger.info(f"Found a service: {service.get('description')}")
        for address in service["ipAddresses"]:
            client.logger.debug(f"address: {address}")
            try:
                parsed = ip_network(address)
            except Exception as error_message: # pylint: disable=broad-except
                client.logger.error(f"Not sure what this was, but it's not an address! {address} - {error_message}")
                continue

            if isinstance(parsed, IPv4Network):
                client.logger.debug("Found IPv4, nobody cares about this old stuff!")
            elif isinstance(parsed, IPv6Network):
                client.logger.debug(f"Found IPv6, woo! {parsed}")
                found_networks.append(parsed)
    client.logger.info("Found the following IPv6 networks:")
    for network in found_networks:
        client.logger.info(f" - {network}")

if __name__ == '__main__':
    main()
