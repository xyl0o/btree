import unittest
from Tree import BTree, Node


class TestBTree(unittest.TestCase):
    def setUp(self):
        #      .____[4]____.
        #  .__[2]__.   .__[6]__.
        # [1]     [3] [5]     [7]
        self.tree1 = BTree(1, it=range(1, 8))

        #   .____[3]____.
        # [1,2]     [4,5,6,7]
        self.tree2 = BTree(2, it=range(1, 8))

        self.treestring = BTree(2, it=["a", "b", "c", "d", "afga", "13", "asdf"])

    def tearDown(self):
        self.tree1 = None
        self.tree2 = None
        self.treestring = None

    def test_newtau(self):
        items = list(self.tree1.items())
        self.tree1.newtau(2)
        newitems = list(self.tree1.items())

        self.assertSequenceEqual(items, newitems)
        self.assertSequenceEqual(self.tree1.root.values, self.tree2.root.values)
        self.assertSequenceEqual(self.tree1.root.children[0].values, self.tree2.root.children[0].values)
        self.assertSequenceEqual(self.tree1.root.children[1].values, self.tree2.root.children[1].values)
        self.assertTrue(self.tree1.root.children[0].isleaf())
        self.assertTrue(self.tree1.root.children[1].isleaf())

    def test_search(self):
        for x in [0, 500, -1]:
            found, node = self.tree1.search(x)
            self.assertEqual(False, found)
            self.assertEqual(False, found)

        for x in [4, 6, 1]:
            self.assertEqual(True, self.tree1.search(x)[0])
            self.assertEqual(True, self.tree2.search(x)[0])

        for x in ["a", "b", "c", "d", "afga", "13", "asdf"]:
            found, node = self.treestring.search(x)
            self.assertEqual(True, found)
            self.assertIsInstance(node, Node)
            self.assertIn(x, node.values)
        self.assertFalse(self.treestring.search("z")[0])

        self.assertEqual(self.tree1.root, self.tree1.search(4)[1])
        self.assertEqual(self.tree1.root.children[1], self.tree1.search(6)[1])
        self.assertEqual(self.tree1.root.children[1].children[0], self.tree1.search(5)[1])

    def test_items(self):
        self.assertSequenceEqual(range(1, 8), list(self.tree1.items()))
        self.assertSequenceEqual(range(1, 8), list(self.tree2.items()))
        self.assertSequenceEqual(sorted(["a", "b", "c", "d", "afga", "13", "asdf"]), list(self.treestring.items()))

    def test_nodes(self):
        nodes = self.tree1.nodes()

        root = next(nodes)
        self.assertIs(self.tree1.root, root)
        self.assertIs(self.tree1.root.children[0], next(nodes))

        leaf1 = next(nodes)
        self.assertIs(self.tree1.root.children[0].children[0], leaf1)
        self.assertEqual([1], leaf1.values)

        leaf3 = next(nodes)
        self.assertIs(self.tree1.root.children[0].children[1], leaf3)
        self.assertEqual([3], leaf3.values)

        node6 = next(nodes)
        self.assertIs(self.tree1.root.children[1], node6)
        self.assertEqual([6], node6.values)
        # maybe test list(nodes)

    def test_add(self):
        self.assertNotIn(100, self.tree1)
        self.assertNotIn(-100, self.tree1)
        self.tree1.add(100)
        self.assertIn(100, self.tree1)
        items = list(self.tree1)
        self.tree1.add(100)
        self.assertIn(100, self.tree1)
        self.assertSequenceEqual(items, list(self.tree1))
        with self.assertRaises(TypeError):
            self.tree1.add("foo")
        with self.assertRaises(TypeError):
            self.treestring.add(1)

    def test_discard(self):
        self.assertIn(7, self.tree1)
        self.tree1.discard(7)
        self.assertNotIn(7, self.tree1)
        items = list(self.tree1.items())
        for x in [1, 4, 2, 3, 5]:
            self.tree1.discard(x)
            items.remove(x)
            self.assertSequenceEqual(items, list(self.tree1.items()))

    def test_pop(self):
        self.assertIn(7, self.tree1)
        self.assertEqual(7, self.tree1.pop())
        self.assertNotIn(7, self.tree1)

    def test_consistency(self):
        for tree in [self.tree1, self.tree2, self.treestring]:
            for node in tree.nodes():
                if not node.isroot():
                    assert node.values and len(node.values) >= node.k, "only root may contain less than k values"
                    assert node.h <= 0 or node.height() < node.h, "distance to root not smaller than h"
                assert len(node.values) <= 2 * node.k, "node.values has more than 2*k elements"
                if not node.isleaf():
                    assert len(node.children) is len(node.values) + 1, "children count is not len(values) + 1"
                assert node.isroot() or node in node.parent.children, "my parent does not know me"
                if not node.isleaf():
                    for child in node.children:
                        assert node is child.parent, "my child has another parent than me"


if __name__ == '__main__':
    unittest.main()
