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

class NextHopLDP( NextHop ):
    """
    NextHop composed of an LDP tunnel
    """

    def __init__(self, tunnel_id):
        self.tunnel_id = tunnel_id

    def __eq__(self, other):
        if not isinstance(other, NextHopLDP):
            return False
        return self.tunnel_id == other.tunnel_id

    def __repr__(self):
        return "<NextHopLDP LDP(%d)>" % self.tunnel_id

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

    def clean(self, recursive=True):
        """
        Clean this Node by removing references to leafs Node is they are empty
        """
        if recursive:
            for i in (0, 1):
                node = leafs[i]
                if node:
                    node.clean()

        for i in (0, 1):
            node = self.leafs[i]
            if node:
                if node.leafs[0] is None and node.leafs[1] is None:
                    if node.route is None:
                        self.leafs[i] = None


    def remove_more_specific(self):
        """
        Remove more specific Nodes that are useless
        """
        for i in (0, 1):
            if self.leafs[i]:
                if self.leafs[i].remove_more_specific():
                    self.leafs[i] = None

        # If this node is a leaf, check whether we can remove it
        if self.leafs[0] is None and self.leafs[1] is None:
            if self.route is None:
                return True

            current = self
            while current.parent is not None:
                current = current.parent
                if current.route is not None:
                    if current.route.nexthops == self.route.nexthops:
                        return True

        return False

    def aggregate(self):
        """
        Aggregate prefixes
        """
        for i in (0, 1):
            if self.leafs[i]:
                self.leafs[i].aggregate()

        if None in [self.leafs[i] for i in (0, 1)]:
            return

        routes = [self.leafs[i].route for i in (0,1)]
        if None in routes:
            return

        if routes[0].nexthops == routes[1].nexthops:
            if self.route is None:
                prefix = routes[0].prefix.supernet()
                nexthops = routes[0].nexthops
                route = Route(prefix=prefix)
                route.nexthops = nexthops
                self.route = route
            else:
                self.route.nexthops = routes[0].nexthops

            for i in (0, 1):
                self.leafs[i].route = None

            self.clean(recursive=False)

    def _do_aggregation(self, model):
        """
        Do the aggregation work.
        Take the nexthop from the 'model' leaf and create or update this node nexthop informations.
        Then clean the leafs
        """
        if self.route is None:
            prefix = model.route.prefix.supernet()
            nexthops = model.route.nexthops
            route = Route(prefix=prefix)
            route.nexthops = nexthops
            self.route = route
        else:
            self.route.nexthops = model.route.nexthops

        for i in (0, 1):
            if self.leafs[i] is not None:
                self.leafs[i].route = None

        self.clean(recursive=False)

    def aggregate_with_empty(self):
        """
        Aggregate prefixes including empty prefixes
        """
        for i in (0, 1):
            if self.leafs[i]:
                self.leafs[i].aggregate_with_empty()

        if self.leafs[0] is None and self.leafs[1] is None:
            return

        for i in (0, 1):
            leafi = self.leafs[i]
            leafj = self.leafs[1-i]

            if leafi is None or leafi.route is None:
                continue

            if leafj is not None:
                if leafj.route is not None:
                    continue

            self._do_aggregation(leafi)
            return

        if self.leafs[0] is not None and self.leafs[1] is not None:
            if self.leafs[0].route.same_nexthop(self.leafs[1].route):
                self._do_aggregation(self.leafs[0])





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

    def aggregate(self):
        """
        Aggregate prefixes that are contigus and that have the same nexthops
        """
        self.root.aggregate()

    def aggregate_with_empty(self):
        """
        Aggregate prefixes that are contigus and that have the same nexthops

        If an empty prefix is near a given prefix, aggregate them as if the
        empty prefix had the same attributes as the none empty one.
        """
        self.root.aggregate_with_empty()

    def list_nexthops(self):
        """
        Return a list of all NextHops used
        """
        list_nh = []
        for node in self.all_nodes():
            nh = node.route.nexthops
            if nh not in list_nh:
                list_nh.append(nh)

        return list_nh
