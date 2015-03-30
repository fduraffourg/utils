#!/bin/env python

import argparse
import re

#
# Prefix Class
#


class Prefix():
    """
    Class used to work on prefixes.

    Each prefix is composed of an address and a mask encoded as int values.

    Here are the operations supported by this class:
        - contains (in): the prefix contains the other prefix
        - addition (+): the result of adding two prefix is the longest prefix
          containing the two prefixes
    """

    #
    # Class variables
    #

    _re_init_from_string = re.compile("(\d+)\.(\d+)\.(\d+)\.(\d+)/(\d+)")
    _all_masks = [0, 2147483648, 3221225472, 3758096384, 4026531840, 4160749568, 4227858432, 4261412864, 4278190080, 4286578688, 4290772992, 4292870144, 4293918720, 4294443008, 4294705152, 4294836224, 4294901760, 4294934528, 4294950912, 4294959104, 4294963200, 4294965248, 4294966272, 4294966784, 4294967040, 4294967168, 4294967232, 4294967264, 4294967280, 4294967288, 4294967292, 4294967294, 4294967295]

    #
    # Init functions
    #

    def __init__(self, string=None, addr=None, mask=None, lenmask=None):
        self.addr = None
        self.mask = None
        self._straddr = None
        self._lenmask = None
        self._str = None

        if string:
            self._init_from_string(string)
            return

        if mask and addr:
            self._init_from_addr_mask(addr, mask)
            return

        if addr and lenmask:
            mask = self.mask_from_lenmask(lenmask)
            self._init_from_addr_mask(addr, mask)
            return

        raise NameError("Bad parameters given")

    def _init_from_string(self, string):
        """
        Create the Prefix from its string representation
        """

        m = self._re_init_from_string.match(string)
        if not m:
            raise NameError("Bad string prefix input %s" % string)

        ablocks = [m.group(i) for i in range(1, 5)]
        iablocks = [i for i in map(int, ablocks)]

        for i in iablocks:
            if i < 0 or i > 255:
                raise NameError("Bad string prefix input %s" % string)

        lenmask = int(m.group(5))

        if lenmask < 0 or lenmask > 32:
            raise NameError("Bad string prefix input %s" % string)

        addr = sum(map(lambda i, j: i * 256**j, iablocks, range(3, -1, -1)))
        mask = self.mask_from_lenmask(lenmask)

        addr = addr & mask

        self.addr = addr
        self.mask = mask
        self._lenmask = lenmask

    def _init_from_addr_mask(self, addr, mask):
        """
        Initialize the Prefix from its address and mask
        """

        if not self.is_mask(mask):
            raise NameError("Bad mask %d -> %s" % (mask, bin(mask)))

        self.addr = addr & mask
        self.mask = mask

    #
    # Toolbox
    #

    @staticmethod
    def mask_from_lenmask(lenmask):
        """
        Return the binary (int value) form of the mask from the mask length
        """
        if lenmask < 0 or lenmask > 32:
            raise NameError("Bad lenmask %d" % lenmask)

        return sum([2**(31-i) for i in range(0, lenmask)])

    @classmethod
    def is_mask(self, mask):
        """
        Check if a mask is correct
        """
        return mask in self._all_masks

    @classmethod
    def lenmask_from_mask(self, mask):
        for l, m in enumerate(self._all_masks):
            if m == mask:
                return l

    #
    # Operation functions
    #

    def __eq__(self, other):
        return self.mask == other.mask and self.addr == other.addr

    def __contains__(self, other):
        """
        Is the 'other' prefix inside this prefix?
        """

        if other.lenmask() < self.lenmask():
            return False

        if self.addr == other.addr & self.mask:
            return True

        return False

    def __add__(self, other):
        """
        The addition of two prefixes returns the longest prefix containing the two prefixes
        """

        if self.lenmask() >= other.lenmask():
            l = self
            s = other
        else:
            l = other
            s = self

        if l in s:
            return s

        for i in range(s.lenmask(), -1, -1):
            mask = self.mask_from_lenmask(i)
            laddr = l.addr & mask
            saddr = s.addr & mask
            if laddr == saddr:
                return Prefix(addr=laddr, mask=mask)

    def is_neighbor_to(self, other):
        """
        Return True if the given prefix is neighbor to this one
        """

        if self.addr + (self.mask ^ 4294967295) + 1 == other.addr:
            return True

        if other.addr + (other.mask ^ 4294967295) + 1 == self.addr:
            return True

        return False

    #
    # String conversion and class display
    #

    def straddr(self):
        if not self._straddr:
            self._compute_straddr()
        return self._straddr

    def _compute_straddr(self):
        ablocks = [self.addr // (256**i) % 256 for i in range(3, -1, -1)]
        self._straddr = '.'.join(map(str, ablocks))

    def lenmask(self):
        if not self._lenmask:
            self._compute_lenmask()
        return self._lenmask

    def _compute_lenmask(self):
        self._lenmask = self.lenmask_from_mask(self.mask)

    def __str__(self):
        return "%s/%d" % (self.straddr(), self.lenmask())

    def __repr__(self):
        return "<Prefix %s>" % self.__str__()

#
# Route Class
#


class Route():
    def __init__(self):
        self.prefix = None
        self.nexthop = None

    def __repr__(self):
        return "<Route %s>" % str(self.prefix)

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
                    'prefix': Prefix(string=prefix),
                    'nexthop': [nexthop]
                    }

    def get_all_routes(self):
        for _, v in self.routes.items():
            yield v

    def get_all_prefixes(self):
        for _, v in self.routes.items():
            yield v['prefix']


#########################
# RoutingTableTree objs #
#########################

#
# RoutingTableNode Class
#

class RoutingTableNode():
    def __init__(self, parent):
        self.parent = parent
        self.leafs = [None, None]
        self.route = None

    def search(self, path, create=False):
        """
        Search for the Node at the given path

        If 'create' is set to False (default) return None at the first none existant Node.
        If 'create' is set to True, create all the Nodes until the destination is found.
        """

        if len(path) == 0:
            return self

        nn = self.leafs[path[0]]
        if not nn:
            if not create:
                return nn

            nn = RoutingTableNode(self)
            self.leafs[path[0]] = nn

        return nn.search(path[1:], create)

    def count(self, blank=False):
        """
        Count nodes

        If blank is False (default), count only non blank nodes
        """
        count = 0

        if blank or self.route:
            count += 1

        for i in range(0, 2):
            leaf = self.leafs[i]
            if leaf:
                count += leaf.count(blank)

        return count

    def draw(self, level):
        """
        Print a very simple representation of this node.
        Level indicate the indentation level to use
        """
        print ("%sNode with route %s" % (level * ' ', self.route))
        for i in (0, 1):
            node = self.leafs[i]
            if node:
                node.draw(level + 1)

#
# RoutingTableTree Class
#


class RoutingTableTree():
    def __init__(self):
        self.root = RoutingTableNode(None)

    def insert(self, route):
        path = self.path_from_prefix(route.prefix)
        node = self.root.search(path, create=True)
        node.route = route
        return node

    def search(self, prefix=None, route=None, create=False):
        """
        Search for a give route or prefix. Returns a RoutingTableNode.

        If create is False (default) returns None if the route does not
        exists. Otherwise create it and return a blank node.
        """
        path = None
        if prefix:
            path = self.path_from_prefix(prefix)
        if route:
            path = self.path_from_prefix(route.prefix)

        if not path:
            raise NameError("prefix or route must be specified")

        return self.root.search(path, create=True)

    def count(self, blank=False):
        """
        Count the number of Nodes on the tree.

        If blank is False (default) only count Node that have a route
        """
        return self.root.count(blank=blank)

    #
    # Toolbox
    #

    @staticmethod
    def path_from_prefix(prefix):
        addr = prefix.addr
        lenmask = prefix.lenmask()
        return [(addr & 2 ** i) >> i for i in range(31, 32 - lenmask - 1, -1)]

    def draw(self):
        self.root.draw(1)

#
# Statistics
#


class Statistics():
    def __init__(self, rt):
        self.rt = rt
        self.rt_len = None
        self.rt_supernet = None
        self.unique_nexthop = None

    # Stats on routing table length

    def get_rt_len(self):
        if not self.rt_len:
            self.rt_len = len(self.rt.routes)
        return self.rt_len

    def print_rt_len(self):
        print("There is %d routes" % self.get_rt_len())

    def get_rt_supernet(self):
        if not self.rt_supernet:
            prefixes = self.rt.get_all_prefixes()
            self.rt_supernet = sum(prefixes, prefixes.__next__())
        return self.rt_supernet

    def print_rt_supernet(self):
        print("The supernet is %s" % self.get_rt_supernet())

    # Stats on unique next hops

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
        for p, route in self.rt.routes.items():
            nexthop = route['nexthop']
            if nexthop not in list_nh:
                list_nh.append(nexthop)

        self.unique_nexthop = list_nh

    # Stats on more specific routes

    def get_more_specific_routes(self):
        msr = []
        msr_dup = []

        routes = list(self.rt.get_all_routes())

        for specific in routes:
            sp = specific['prefix']
            containers = []

            for generic in routes:
                gp = generic['prefix']

                if sp in gp and not sp == gp:
                    containers.append(gp)

                    if specific['nexthop'] == generic['nexthop']:
                        msr_dup.append((sp, gp))

            if len(containers) > 0:
                msr.append((sp, containers))

        return msr, msr_dup

    def print_more_specific_routes(self):
        msr, msr_dup = self.get_more_specific_routes()

        print("There are %d more specific routes" % len(msr))
        print("There are %d more specific routes with same nexthop" % len(msr_dup))
