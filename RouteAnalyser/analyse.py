#!/bin/env python
import argparse
import re

import rt
from ipaddress import IPv4Address


#
# File parsing
#


def analyse_file(filename):
    rtree = rt.RoutingTableTree()

    i = 0
    with open(filename, 'r') as fd:
        for line in fd:
            prefix, nexthop = analyse_line(line, rtree)
            if prefix is None:
                continue
            route = rt.Route(prefix=prefix, nexthop=nexthop)
            node = rtree.search(route=route, create=True)
            if not node.route:
                node.route = route

            route = node.route
            route.add_nexthop(nexthop)

            if i % 1000 == 0:
                print("%d" % i, end="\r", flush=True)
            i += 1

    return rtree

RELINE = re.compile(r"^[0-9]*\s*(?P<prefix>[0-9./]+)\s*(?P<nexthop>.*)$")
RENHIPINT = re.compile(r"^(?P<ip>[0-9.]+)\s*(?P<int>\w* [0-9/a-zA-Z]*).*$")
RENHLDP = re.compile(r"^DIRECT\s*LDP \((?P<id>\d*)\).*$")

def analyse_line(line, rtree):
    mline = RELINE.match(line)
    if mline:
        prefix = mline.group('prefix')
        nexthop = mline.group('nexthop')

        mnh = RENHIPINT.match(nexthop)
        if mnh:
            ip = IPv4Address(mnh.group('ip'))
            nexthop = rt.NextHopIPInt(ip, mnh.group('int'))
            return prefix, nexthop

        mnh = RENHLDP.match(nexthop)
        if mnh:
            tunnel_id = int(mnh.group('id'))
            nexthop = rt.NextHopLDP(tunnel_id)
            return prefix, nexthop

        return prefix, "Unknown"

    else:
        print(line)
        return None, None


parser = argparse.ArgumentParser(description='Analyse route table dump')
parser.add_argument('files', metavar='F', type=str, nargs='+',
                    help='list of files')

args = parser.parse_args()

for filename in args.files:
    print("\n=========================\nFile %s\n" % filename)
    rtree = analyse_file(filename)

    print("\nRoutingTableTree")
    num_routes = rtree.count()
    print("There is %d routes" % num_routes)

#    list_nh = rtree.list_nexthops()
#    print("There are %d nexthops" % len(list_nh))
#    for nh in list_nh:
#        print("    - %s" % nh)

    print("")
    print("Remove more specific routes")
    rtree.remove_more_specific()
    num_routes_2 = rtree.count()
    print("There is %d routes left (%d removed)" % (num_routes_2, num_routes - num_routes_2))

    print("")
    print("Aggregate prefixes")
    rtree.aggregate_with_empty()
    num_routes_3 = rtree.count()
    print("There is %d routes left (%d removed)" % (num_routes_3, num_routes - num_routes_3))
