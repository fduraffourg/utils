import unittest
from ipaddress import IPv4Network


import rt


def rtree_contains_prefixes(rtree, prefixes):
    """
    Check that the given RoutingTableTree contains only
    the prefixes from the given list
    """
    if rtree.count(blank=False) != len(prefixes):
        return False

    for prefix in prefixes:
        node = rtree.search(prefix=prefix, create=False)
        if node is None:
            return False
        elif node.route is None:
            return False

    return True


class TestRoutingTableTree(unittest.TestCase):
    def test_aggregate_with_empty(self):
        test_cases = [
                # Case 1
                (
                    # Input
                    [ ("1.0.0.0/24", rt.NextHopLDP(12)) ],
                    # Result
                    ["0.0.0.0/0"]
                ),
                # Case 2
                (
                    # Input
                    [ ("1.0.0.0/8", rt.NextHopLDP(12)),
                       ("2.0.0.0/32", rt.NextHopLDP(12)) ] ,
                    # Result
                    ["0.0.0.0/0"]
                ),
                # Case 3
                (
                    # Input
                    [ ("192.168.32.0/25", rt.NextHopLDP(1)),
                       ("192.168.32.128/25", rt.NextHopLDP(12)) ] ,
                    # Result
                    ["192.168.32.0/25", "192.168.32.128/25"]
                ),
                ]

        for case in test_cases:
            input = case[0]
            result = [ IPv4Network(p) for p in case[1] ]

            rtree = rt.RoutingTableTree()

            for item in input:
                route = rt.Route(prefix=item[0], nexthop=item[1])
                rtree.insert(route)

            rtree.aggregate_with_empty()

            self.assertTrue(rtree_contains_prefixes(rtree, result))


if __name__ == '__main__':
        unittest.main()
