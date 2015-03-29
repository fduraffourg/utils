#!/bin/env python

import argparse
import re

#
# RoutingTable Class
#

class RoutingTable():
    def __init__(self):
        self.routes = dict()


    def add_route(self, prefix, nexthop):
        if prefix in self.routes:
            route = self.routes[prefix]
            route['nexthop'].append(nexthop)

        else:
            self.routes[prefix] = {
                    'prefix': prefix,
                    'nexthop': [nexthop]
                    }

#
# File parsing
#

def analyse_file(filename):
    rt = RoutingTable()
    with open(filename, 'r') as fd:
        for line in fd:
            analyse_line(line, rt)

    return rt

RELINE = re.compile("^[0-9]*\s*(?P<prefix>[0-9./]+)\s*(?P<nexthop>[0-9.]*)\s*.*$")
def analyse_line(line, rt):
    m = RELINE.match(line)
    if m:
        prefix = m.group('prefix')
        nexthop = m.group('nexthop')
        rt.add_route(prefix, nexthop)
    else:
        print(line)


#
# Statistics
#

class Statistics():
    def __init__(self, rt):
        self.rt = rt
        self.rt_len = None
        self.unique_nexthop = None

    ## Stats on routing table length
    
    def get_rt_len(self):
        if not self.rt_len:
            self.rt_len = len(self.rt.routes)
        return self.rt_len

    def print_rt_len(self):
        print("There is %d routes" % self.get_rt_len())


    ## Stats on unique next hops

    def get_unique_nexthop(self):
        if not self.unique_nexthop:
            self._compute_unique_nexthop()
        return self.unique_nexthop

    def print_unique_nexthop(self):
        unh = self.get_unique_nexthop()
        print("There is %d unique next-hops:" % len(unh))
        for nh in unh:
            print("    - %s" % nh)

    def _compute_unique_nexthop(self):
        list_nh = []
        for p, route in rt.routes.items():
            nexthop = route['nexthop']
            if nexthop not in list_nh:
                list_nh.append(nexthop)

        self.unique_nexthop = list_nh


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyse route table dump')
    parser.add_argument('files', metavar='F', type=str, nargs='+',
                               help='list of files')

    args = parser.parse_args()


    for filename in args.files:
        print("\n=========================\nFile %s\n" % filename)
        rt = analyse_file(filename)
        stats = Statistics(rt)
        stats.print_rt_len()
        stats.print_unique_nexthop()
