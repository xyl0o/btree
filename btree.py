#!/usr/bin/python
from collections import MutableSet


class BTree(MutableSet):

    @classmethod
    def _from_iterable(cls, it):
        return cls(4, it=it)

    def __init__(self, k, h=0, it=None):
        self.k = k
        self.h = h
        self.root = Node(k, h)
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
            self.root.consistent(family=True)  # testing

    def discard(self, item):
        found, node = self.search(item)
        if found:
            node.remove(item)
            self.root = node.getroot()  # root might have changed
            self.root.consistent(family=True)  # testing

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
            assert self.values and len(self.values) >= self.k, "only root may contain less than k values"
            assert self.h <= 0 or self.height() < self.h, "distance to root not smaller than h"
        assert len(self.values) <= 2 * self.k, "node.values has more than 2*k elements"
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

    def overflow(self):
        return len(self.values) > 2 * self.k

    def underflow(self):
        if not self.isroot():
            return len(self.values) < self.k
        if self.isleaf():
            return False  # tree of one node cant underflow
        return len(self.values) < 1

    def childfor(self, item):
        index = 0
        while index < len(self.values) and self.values[index] < item:
            index += 1
        return self.children[index]

    def rebalance(self):
        if self.underflow():
            if self.isroot():  # it we land here, the root node is empty except one child (the new root)
                self.children[0].parent = None
                self.children = self.values = None  # isolate this one (help gc)
                return
            # get the index for value and left sibling
            index = self.parent.children.index(self) - 1
            leftsibling = self.parent.children[index]
            if len(leftsibling.values) > self.k:
                #  rotate
                # b = k - 1 in P und b > k in P’: gleiche Unterlauf über P’ aus,
                #   take parent index val as new leftmost val for self
                self.values.insert(0, self.parent.values[index])
                #   take last val and child from sibling
                #   put taken sibling val as parent index val
                self.parent.value[index] = leftsibling.values.pop()
                #   put taken sibling child as leftmost child
                self.children.insert(0, leftsibling.children.pop())
            elif len(leftsibling.values) is self.k:
                #  merge
                # b = k - 1 in P und b = k in P’: mische P und P’
                #   take left sibling
                #   append parent index val into self (from left)
                #   append all values and children from sibling into self (from left)
                self.values = leftsibling.values + [self.parent.values[index]] + self.values
                if not self.isleaf():
                    for child in leftsibling.children:
                        child.parent = self
                    self.children = leftsibling.children + self.children
                # remove parent index val from parent
                #   remove sibling as child in parent
                self.parent.values.pop(index)
                self.parent.children.pop(index)
                self.parent.rebalance()

    def remove(self, item):
        if item in self:
            if self.isleaf():
                self.values.remove(item)
                if self.underflow():
                    self.rebalance()
            else:
                # Each element in an internal node acts as a separation value for two subtrees,
                # therefore we need to find a replacement for separation.
                index = self.values.index(item)
                node = self.children[index]
                while not node.isleaf():
                    node = node.children[-1]
                self.values[index] = node.values[-1]
                node.remove(item)
                node.rebalance()

    def insert(self, item):
        assert self.isleaf()
        if item in self:
            return True
        self.values = sorted(self.values + [item])
        if self.overflow():
            self.split()

    def adopt(self, child, median, new):
        assert not self.isleaf()
        index = self.children.index(child)
        self.values.insert(index, median)
        self.children.insert(index + 1, new)
        if self.overflow():
            self.split()

    # handle overflow
    def split(self):
        assert self.overflow()
        if self.isroot():
            self.parent = Node(self.k, self.h)
            self.parent.children = [self]  # cheat a bit

        median = self.values[self.k]
        right = Node(self.k, self.h, values=self.values[self.k + 1:],
                     children=self.children[self.k + 1:], parent=self.parent)
        self.values = self.values[:self.k]
        self.children = self.children[:self.k + 1]

        self.parent.adopt(self, median, right)  # cheat gets removed in adopt()

    def __contains__(self, item):
        return item in self.values

    def __repr__(self):
        state = 'leaf' if self.isleaf() else 'node'
        state = 'root' if self.isroot() else state
        return "<btree {} {}>".format(state, self.values)


if __name__ == '__main__':
    if False:
        testvalues = [77, 12, 48, 69, 33, 89, 97, 91, 37, 45, 83, 2, 5, 57, 90, 95, 99, 50]
        n = BTree(2, it=testvalues)
        print(n)
        n.fancy()
    else:
        # testvalues = [1, 3, 9, 11, 15, 17, 18, 19, 25]
        testvalues = range(1, 8)
        n = BTree(1, it=testvalues)
        print(n)
        n.fancy()
        n.discard(7)
        print(n)
        n.fancy()
        n.discard(6)
        print(n)
        n.fancy()
        n.discard(5)
        print(n)
        n.fancy()
        n.discard(4)
        print(n)
        n.fancy()
