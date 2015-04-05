#!/bin/env python
import argparse
import re

import rt


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

RELINE = re.compile("^[0-9]*\s*(?P<prefix>[0-9./]+)\s*(?P<nexthop>[0-9.]*)\s*.*$")


def analyse_line(line, rtable, rtree):
    m = RELINE.match(line)
    if m:
        prefix = m.group('prefix')
        nexthop = m.group('nexthop')
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
    supernet = sum(all_prefixes, all_prefixes.__next__())
    print("The supernet is %s" % supernet)

