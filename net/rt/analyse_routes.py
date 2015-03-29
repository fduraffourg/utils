#!/bin/env python

import argparse
import re

#
# Prefix Class
#

class Prefix():
    """
    Class used to work on prefixes.

    Each prefix is composed of an address and a mask. Each of these items is saved with its string format for printing and with its binary format to operate on it. We also have the full string prefix for printing.

    Here are the operations supported by this class:
        - addition (+): the result of adding two prefix is the longest prefix containing the two prefixes
    """

    def __init__(self, string = None):
        self.string = None
        self.addr = None
        self.mask = None
        self.baddr = None
        self.bmask = None

        if string:
            self._init_from_string(string)


    re_init_from_string = re.compile("(\d+)\.(\d+)\.(\d+)\.(\d+)/(\d+)")
    def _init_from_string(self, string):
        """
        Create the Prefix from its string representation
        """

        m = re_init_from_string.match(string)
        if not m:
            raise NameError("Bad string prefix input %s" % string)

        ablocks = [ m.group(i) for i in range(1,5) ]
        iablocks = map(int, ablocks)

        for i in iablocks:
            if i < 0 or i > 255:
                raise NameError("Bad string prefix input %s" % string)

        mask = m.group(5)
        imask = int(mask)

        if imask < 0 or imask > 32:
            raise NameError("Bad string prefix input %s" % string)

        self.string = string

        self.addr = '.'.join(ablocks)
        self.mask = mask

        self.baddr = sum(map(lambda i,j: i * 256**j, iablocks, range(3, -1, -1)))
        self.bmask = imask
        

    def __add__(self, other):
        """
        The addition of two prefixes returns the longest prefix containing the two prefixes
        """

        if self.bmask >= other.bmask:
            l = self
            s = other
        else:
            l = other
            s = self

    def __contains__(self, other):
        """
        Is the 'other' prefix inside this prefix?
        """

        if other.bmask < self.bmask:
            return False

        if self.baddr == ( other.baddr && self.bmask ):
            return True

        return False


        

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
