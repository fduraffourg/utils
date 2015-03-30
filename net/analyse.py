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
            analyse_line(line, rtable, rtree)

    return rtable, rtree

RELINE = re.compile("^[0-9]*\s*(?P<prefix>[0-9./]+)\s*(?P<nexthop>[0-9.]*)\s*.*$")


def analyse_line(line, rtable, rtree):
    m = RELINE.match(line)
    if m:
        prefix = m.group('prefix')
        nexthop = m.group('nexthop')
        try:
            rtable.add_route(prefix, nexthop)

            p = rt.Prefix(string=prefix)
            node = rtree.search(prefix=p, create=True)
            if not node.route:
                node.route = rt.Route()
                node.route.prefix = p

        except ValueError as e:
            print("Error with line '%s'" % line.rstrip())
            print(e)
    else:
        print(line)


parser = argparse.ArgumentParser(description='Analyse route table dump')
parser.add_argument('files', metavar='F', type=str, nargs='+',
                    help='list of files')

args = parser.parse_args()

for filename in args.files:
    print("\n=========================\nFile %s\n" % filename)
    rtable, rtree = analyse_file(filename)
    stats = rt.Statistics(rtable)
    stats.print_rt_len()
    stats.print_rt_supernet()
    stats.print_unique_nexthop()
    stats.print_more_specific_routes()

    print("\nRoutingTableTree")
    print("There is %d routes" % rtree.count())

