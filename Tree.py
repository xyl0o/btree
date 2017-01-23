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
        return self.search(item, node=node.child(item))

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
            self.root = node.getroot()  # root might have changed

    def pop(self):
        if not self.root:
            raise KeyError('BTree is empty')
        item = list(self)[-1]
        self.discard(item)
        return item

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
        elif not self.isleaf():
            return len(self.values) < 1
        else:
            return False  # tree of one node cant underflow

    def child(self, item):
        index = 0
        while index < len(self.values) and self.values[index] < item:
            index += 1
        return self.children[index]

    def insert(self, item):
        assert self.isleaf()
        if item in self:
            return True
        self.values = sorted(self.values + [item])
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

    def adopt(self, child, median, new):
        assert not self.isleaf()
        index = self.children.index(child)
        self.values.insert(index, median)
        self.children.insert(index + 1, new)
        if self.overflow():
            self.split()

    def remove(self, item):
        assert item in self
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
            node.remove(self.values[index])

    def rebalance(self):
        assert self.underflow()

        if self.isroot():  # it we land here, the root node is empty except one child (the new root)
            self.children[0].parent = None
            self.children = self.values = None  # isolate this one
            return

        assert self.rotate() or \
               self.merge() or \
               self.rotate(right=True) or \
               self.merge(right=True), \
            "No rebalancing possible"

    def rotate(self, right=False):
        myindex = self.parent.children.index(self)
        if myindex is 0 and not right:
            return False
        elif myindex + 1 is len(self.parent.children) and right:
            return False
        siblingindex = pvalindex = myindex - 1
        if right:
            siblingindex = myindex + 1
            pvalindex = myindex
        sibling = self.parent.children[siblingindex]
        if len(sibling.values) <= self.k:
            return False

        if right:
            self.values.append(self.parent.values[pvalindex])
            self.parent.values[myindex] = sibling.values.pop(0)
            if not self.isleaf():
                child = sibling.children.pop(0)
                child.parent = self
                self.children.append(child)
        else:
            self.values.insert(0, self.parent.values[pvalindex])
            self.parent.values[pvalindex] = sibling.values.pop()
            if not self.isleaf():
                child = sibling.children.pop()
                child.parent = self
                self.children.insert(0, child)

        return True

    def merge(self, right=False):
        myindex = self.parent.children.index(self)
        if myindex is 0 and not right:
            return False
        siblingindex = pvalindex = myindex - 1
        if right:
            siblingindex = myindex + 1
            pvalindex = myindex

        sibling = self.parent.children[siblingindex]
        if len(sibling.values) is not self.k:
            return False
        self.parent.children.pop(siblingindex)
        self.values = sorted(self.values + [self.parent.values.pop(pvalindex)] + sibling.values)
        if not self.isleaf():
            for child in sibling.children:
                child.parent = self
            self.children = sorted(self.children + sibling.children)
        if self.parent.underflow():
            self.parent.rebalance()
        return True

    def __eq__(self, other):
        return NotImplemented

    def __ne__(self, other):
        return NotImplemented
        # return not self.__eq__(self, other)

    def __lt__(self, other):
        return self.values[-1] < other.values[0]

    def __le__(self, other):
        return self.__lt__(self, other)

    def __gt__(self, other):
        return self.values[-1] > other.values[0]

    def __ge__(self, other):
        return self.__gt__(self, other)

    def __contains__(self, item):
        return item in self.values

    def __repr__(self):
        state = 'leaf' if self.isleaf() else 'node'
        state = 'root' if self.isroot() else state
        return "<btree {} {}>".format(state, self.values)
