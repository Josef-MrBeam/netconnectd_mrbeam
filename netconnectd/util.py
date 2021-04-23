from __future__ import print_function, absolute_import

import argparse
import subprocess
import yaml
import os
import re


common_arguments = argparse.ArgumentParser(add_help=False)
common_arguments.add_argument(
    "-a",
    "--address",
    type=str,
    help="Address of Unix Domain Socket used for communication",
)
common_arguments.add_argument(
    "-c", "--config", type=str, help="Location of config file to use"
)


def has_link(logger):
    link = False
    reachable_devs = set()

    output = subprocess.check_output(["/sbin/ip", "address", "show"]).decode("utf-8")

    lines = output.split("\n")
    logger.debug("/sbin/ip address show")
    dev_match = re.compile(r"^\d+:")
    skip_to_next_dev = True
    for line in lines:
        logger.debug(line)
        split_line = line.split()
        if len(split_line) < 2:
            continue

        logger.debug(split_line)
        if dev_match.match(split_line[0]):
            dev = split_line[1][0:-1]   # strip off :
            if dev == "lo" or "no-carrier" in split_line[2].lower():
                skip_to_next_dev = True;
            else:
                skip_to_next_dev = False;
            continue

        if skip_to_next_dev:
            continue

        if split_line[0].startswith("inet"):
            if "scope" in split_line and "global" in split_line:
                address = split_line[1]
                if "/" in address:
                    address = address.split("/")[0]
                if address.startswith("127.") or address.startswith("::1"):
                    continue
                # There's a global address - consider link up
                link = True
                logger.debug("Device {} up".format(dev))
                reachable_devs.add(dev)

    return link, reachable_devs


class InvalidConfig(Exception):
    pass


default_config = dict(
    socket="/var/run/netconnectd.sock",
    interfaces=dict(wifi=None, wired=None),
    link_monitor=dict(enabled=True, max_link_down=3, interval=10),
    ap=dict(
        name="netconnectd_ap",
        driver="nl80211",
        ssid=None,
        psk=None,
        channel=3,
        ip="10.250.250.1",
        network="10.250.250.0/24",
        range=("10.250.250.100", "10.250.250.200"),
        domain=None,
        forwarding_to_wired=False,
        enable_if_wired=False,
    ),
    wifi=dict(
        name="netconnectd_wifi",
        free=False,
        kill=False,
        default_country="DE",
    ),
    paths=dict(
        hostapd="/usr/sbin/hostapd",
        hostapd_conf="/etc/hostapd/conf.d",
        dnsmasq="/usr/sbin/dnsmasq",
        dnsmasq_conf="/etc/dnsmasq.conf.d",
        interfaces="/etc/network/interfaces",
    ),
    ap_list=dict(
        filter_hidden_ssid=False,
    ),
)


def parse_configfile(configfile):
    if not os.path.exists(configfile):
        return None

    mandatory = ("interface.wifi", "ap.ssid")

    try:
        with open(configfile, "r") as f:
            config = yaml.safe_load(f)
    except:
        raise InvalidConfig("error while loading config from file")

    def merge_config(default, config, mandatory, prefix=None):
        result = dict()
        for k, v in list(default.items()):
            result[k] = v

            prefixed_key = "%s.%s" % (prefix, k) if prefix else k
            if isinstance(v, dict):
                result[k] = merge_config(
                    v, config[k] if k in config else dict(), mandatory, prefixed_key
                )
            else:
                if k in config:
                    result[k] = config[k]

            if result[k] is None and prefixed_key in mandatory:
                raise InvalidConfig("mandatory key %s is missing" % k)
        return result

    return merge_config(default_config, config, mandatory)
