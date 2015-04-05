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
            route = rt.Route(prefix=prefix, nexthop=nexthop)
            node = rtree.search(route=route, create=True)
            if not node.route:
                node.route = route

            route = node.route
            route.add_nexthop(nexthop)

    return rtable, rtree

RELINE = re.compile(r"^[0-9]*\s*(?P<prefix>[0-9./]+)\s*(?P<nexthop>.*)$")
RENHIPINT = re.compile(r"^(?P<ip>[0-9.]+)\s*(?P<int>\w* [0-9/a-zA-Z]*).*$")

def analyse_line(line, rtable, rtree):
    mline = RELINE.match(line)
    if mline:
        prefix = mline.group('prefix')
        nexthop = mline.group('nexthop')

        mnh = RENHIPINT.match(nexthop)
        if mnh:
            ip = IPv4Address(mnh.group('ip'))
            nexthop = rt.NextHopIPInt(ip, mnh.group('int'))

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

    rtree.draw()

    all_prefixes = (node.route.prefix for node in rtree.all_nodes())

