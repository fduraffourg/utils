#!/bin/env python
import argparse
import re

import rt
from ipaddress import IPv4Address


#
# File parsing
#


def analyse_file(filename):
    rtable = rt.RoutingTable()
    rtree = rt.RoutingTableTree()

    with open(filename, 'r') as fd:
        for line in fd:
            prefix, nexthop = analyse_line(line, rtable, rtree)
            route = rt.Route(prefix=prefix)
            node = rtree.search(route=route, create=True)
            if not node.route:
                node.route = route

    return rtable, rtree

RELINE = re.compile(r"^[0-9]*\s*(?P<prefix>[0-9./]+)\s*(?P<nexthop>.*)$")
RENHIPINT = re.compile(r"^(?P<ip>[0-9.]+)\s*(?P<int>\w* [0-9\a-zA-Z]*).*$")

def analyse_line(line, rtable, rtree):
    m = RELINE.match(line)
    if m:
        prefix = m.group('prefix')
        nexthop = m.group('nexthop')
        m = RENHIPINT.match(nexthop)
        destination = None
        if m:
            ip = IPv4Address(m.group('ip'))
            destination = rt.DestinationIPInt(ip, m.group('int'))

        nexthop = rt.NextHop(destination)

        return prefix, nexthop
    else:
        print(line)


parser = argparse.ArgumentParser(description='Analyse route table dump')
parser.add_argument('files', metavar='F', type=str, nargs='+',
                    help='list of files')

args = parser.parse_args()

for filename in args.files:
    print("\n=========================\nFile %s\n" % filename)
    rtable, rtree = analyse_file(filename)

    print("\nRoutingTableTree")
    print("There is %d routes" % rtree.count())


    all_prefixes = (node.route.prefix for node in rtree.all_nodes())

