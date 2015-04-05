#!/bin/env python
"""
Network objects
"""

import re
import struct
from ipaddress import IPv4Network

#
# NextHop Class
#


class NextHop():
    """
    NextHop Class
    """
    def __init__(self, destination):
        pass

    def __equals__(self, other):
        raise NotImplemented()


class NextHopIPInt( NextHop ):
    """
    NextHop composed of an IP and an Interface
    """

    def __init__(self, ip, interface):
        self.ip = ip
        self.interface = interface

    def __eq__(self, other):
        if not isinstance(other, NextHopIPInt):
            return False
        return self.ip == other.ip and self.interface == other.interface

    def __repr__(self):
        return "<NextHopIPInt %s '%s'>" % (self.ip, self.interface)

#
# Route Class
#


class Route():
    """
    Route Class
    """
    def __init__(self, prefix=None, nexthop=None):
        self.prefix = None
        self.nexthops = []

        if isinstance(prefix, str):
            self.prefix = IPv4Network(prefix)
        if isinstance(prefix, IPv4Network):
            self.prefix = prefix

        if nexthop:
            self.nexthops.append(nexthop)

    def add_nexthop(self, nexthop):
        """
        Add a nexthop to this route
        """
        if nexthop not in self.nexthops:
            self.nexthops.append(nexthop)

    def same_nexthop(self, other):
        """
        Check wether this route has the same nexthops as the other route.
        """
        for n in self.nexthops:
            if n not in other.nexthops:
                return False
        for n in other.nexthops:
            if n not in self.nexthops:
                return False
        return True


    def __repr__(self):
        return "<Route %s, %s>" % (self.prefix, self.nexthops)

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
                'nexthop': [nexthop],
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
                count += leaf.count(blank=blank)

        return count

    def all_nodes(self, blank=False):
        """
        Yield all nodes
        """
        for i in range(0, 2):
            leaf = self.leafs[i]
            if leaf:
                for node in leaf.all_nodes(blank=blank):
                    yield node

        if blank or self.route:
            yield self

    def draw(self, level):
        """
        Print a very simple representation of this node.
        Level indicate the indentation level to use
        """
        print("%sNode with route %s" % (level * ' ', self.route))
        for i in (0, 1):
            node = self.leafs[i]
            if node:
                node.draw(level + 1)

    def remove_more_specific(self):
        """
        Remove more specific Nodes that are useless
        """


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

        if path is None:
            raise NameError("prefix or route must be specified")

        return self.root.search(path, create=create)

    def count(self, blank=False):
        """
        Count the number of Nodes on the tree.

        If blank is False (default) only count Node that have a route
        """
        return self.root.count(blank=blank)

    def all_nodes(self, blank=False):
        """
        Return a generator yielding all nodes.

        If blank is False (default) only yield non blank nodes
        """
        for node in self.root.all_nodes(blank=blank):
            yield node

    #
    # Toolbox
    #

    @staticmethod
    def path_from_prefix(prefix):
        addr = struct.unpack(">I", prefix.network_address.packed)[0]
        lenmask = prefix.prefixlen
        return [(addr & 2 ** i) >> i for i in range(31, 32 - lenmask - 1, -1)]

    def draw(self):
        self.root.draw(1)

    def remove_more_specific(self):
        """
        Remove all more specific subnets that have the same next-hop as their parent
        """
        self.root.remove_more_specific()
