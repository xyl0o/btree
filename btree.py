#!/usr/bin/python
from collections import MutableSet


class BTree(MutableSet):

    @classmethod
    def _from_iterable(cls, it):
        return cls(4, it=it)

    def __init__(self, k, h=0, it=None):
        self.k = k
        self.h = h
        self.root = BTree.Node(k, h)
        if it:
            for item in it:
                self.add(item)

    def newtau(self, k, h=0):
        self.__init__(k, h, it=list(self.items()))

    def search(self, item, node=None):
        node = node if node else self.root
        if item in node:
            return True, node
        if node.isleaf():
            return False, node
        return self.search(item, node=node.childfor(item))

    # generator function for values in tree
    # in order item depth-first items
    def items(self, node=None):
        node = node if node else self.root
        if node.isleaf():
            yield from node.values
        else:
            yield from self.items(node.children[0])
            for index, value in enumerate(node.values):
                yield value
                yield from self.items(node.children[index + 1])

    # pre-order node depth-first items
    def nodes(self, node=None):
        node = node if node else self.root
        yield node
        if not node.isleaf():
            for child in node.children:
                yield from self.nodes(child)

    # print tree in fancy
    def fancy(self, node=None):
        node = node if node else self.root
        print("    " * node.height() + repr(node))
        if node.children:
            for child in node.children:
                self.fancy(child)

    def add(self, item):
        try:
            found, node = self.search(item)  # find place for item
        except TypeError as e:
            raise TypeError('element must be comparable to exisitng items')
        if not found:
            node.insert(item)
            self.root = node.getroot()  # root might have changed

    def discard(self, item):
        found, node = self.search(item)
        if found:
            node.remove(item)

    def pop(self):
        raise NotImplementedError
        # if not self.root:
        #     raise KeyError('BTree is empty')
        # item = reversed(self.root)[0]
        # self.discard(item)
        # return item

    def __contains__(self, item):
        return self.search(item)[0]

    def __len__(self):
        return len(list(self.items()))

    def __iter__(self):
        return self.items()

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    class Node():
        def __init__(self, k, h=0, values=None, children=None, parent=None):
            if not values:
                values = []
            if children:
                for child in children:
                    child.parent = self
            else:
                children = []

            self.k, self.h, self.values, self.children, self.parent = k, h, values, children, parent

            self.consistent(family=False)  # Testing every Node

        def consistent(self, family=False):
            if not self.isroot():
                assert self.values and len(self.values) >= self.k, "only root may contain less than %i values".format(
                    self.k)
                assert self.h <= 0 or self.height() < self.h, "distance to root not smaller than h"
            assert len(self.values) <= 2 * self.k, "node.values must contain <= %i elements".format(2 * self.k)
            if not self.isleaf():
                assert len(self.children) is len(self.values) + 1, "children count is not len(values) + 1"
            if family:
                assert self.isroot() or self in self.parent.children, "my parent does not know me"
                if not self.isleaf():
                    for child in self.children:
                        assert self is child.parent, "my child has another parent than me"

        # is this root (it has no parent)
        def isroot(self):
            return not self.parent

        # is this a leaf (it has no children)
        def isleaf(self):
            return not self.children

        # give root node (has
        def getroot(self):
            return self if self.isroot() else self.parent.getroot()

        # distance to root respectively the tree height
        def height(self):
            return 0 if self.isroot() else self.parent.height() + 1

        def childfor(self, item):
            index = 0
            while index < len(self.values) and self.values[index] < item:
                index += 1
            return self.children[index]

        def insert(self, item):
            assert self.isleaf(), "no insert on nodes other than leafes"
            if item in self:
                return True
            self.values = sorted(self.values + [item])
            self.check()

        # check if rebalancing is necessary
        def check(self):
            if len(self.values) > 2 * self.k:
                self.split()
            elif not self.isroot() and len(self.values) < self.k:
                pass  # TODO handle underflow

            self.getroot().consistent(family=True)  # testing

        # handle overflow
        def split(self):
            if self.isroot():
                self.parent = BTree.Node(self.k, self.h, values=[self.values[self.k]],
                                         children=None, parent=None)
                self.parent.children = [self]
                index = 0
            else:
                index = self.parent.children.index(self)
                self.parent.values.insert(index, self.values[self.k])

            right = BTree.Node(self.k, self.h, values=self.values[self.k + 1:],
                               children=self.children[self.k + 1:], parent=self.parent)
            self.parent.children.insert(index + 1, right)
            self.values = self.values[:self.k]
            self.children = self.children[:self.k + 1]

            self.parent.check()

        def remove(self, item):
            # TODO implement
            raise NotImplementedError

        def __contains__(self, item):
            return item in self.values

        def __repr__(self):
            state = 'leaf' if self.isleaf() else 'node'
            state = 'root' if self.isroot() else state
            return "<btree {} {}>".format(state, self.values)


if __name__ == '__main__':
    if True:
        testvalues = [77, 12, 48, 69, 33, 89, 97, 91, 37, 45, 83, 2, 5, 57, 90, 95, 99, 50]
        test = testvalues[:18]
        n = BTree(2, it=testvalues)
    else:
        n = BTree(1, it=range(1, 50))
    print(n)
    n.fancy()
