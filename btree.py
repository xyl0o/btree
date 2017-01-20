#!/usr/bin/python
from collections import MutableSet
    

class BTree(MutableSet):
    class Node():
        def __init__(self, k, h, parent=None, values=None, children=None):
            self.k = k
            self.h = h

            assert not parent or parent.dist() + 1 < h, "h = %s is too small for this node" % h
            self.parent = parent

            if values is None:
                values = []
            assert self.is_root() or len(values) >= k, "only root may contain less than %i" % k
            assert len(values) <= 2*k, "values must contain <= %i elements" % 2*k
            self.values = values # size: 2k

            assert not children or len(children) is len(values) + 1, "given children list does not fit with given values"
            self.children = children

        # is this root (it has no parent)
        def is_root(self):
            return self.parent is None

        # is this a leaf (it has no children)
        def is_leaf(self):
            return not self.children

        # distance from root
        def dist(self):
            if not self.parent:
                return 0
            return self.parent.dist() + 1

        # descent into subtree
        # do not depend on 'item in subtree' __contains__ depends on you
        def search(self, item):
            if item in self.values:
                return True, self  # item is here
            if self.is_leaf():
                return False, self  # item would but isn't here
            # get index for subtree to search in
            index = 0
            while index < len(self.values) and self.values[index] < item:
                index += 1
            # return node where item belongs
            return self.children[index].search(item)

        # check if rebalancing is necessary
        def rebalance(self):
            if len(self.values) > 2 * self.k:
                self.split()
            elif not self.is_root() and len(self.values) < self.k:
                pass  # TODO

            self.testthis()  # all the asserts

        # split and rebalance an overflowed node recursively
        def split(self):
            values = self.values[:]
            lchild = self.children[:self.k+1] if self.children else None
            rchild = self.children[self.k+1:] if self.children else None
                
            if self.is_root():
                parent = self
                left = BTree.Node(parent.k, parent.h, parent, values[:self.k], lchild)
                parent.values = []
                parent.children = [left]
                index = 0
                if left.children:
                    for child in left.children:
                        child.parent = left
            else:
                parent = self.parent
                left = self
                left.values = values[:self.k]
                left.children = lchild
                index = parent.children.index(left)

            # insert median
            parent.values.insert(index, values[self.k])
            # create right node
            right = BTree.Node(parent.k, parent.h, parent, values[self.k+1:], rchild)
            if right.children:
                for y in right.children:
                    y.parent = right
            # insert right node into parent
            parent.children.insert(index + 1, right)
            # check if parent is balanced
            parent.rebalance()

        # please support:
        #   [valy, valx].sort()
        #   valx < valy
        def insert(self, item):
            if self.is_leaf():  # this should be internal only
                if item in self:
                    return True
                self.values = sorted(self.values+[item])
                self.rebalance()
            elif self.is_root():  # this may be implemented elsewhere (only callable if self.is_root())
                # test if item can be added
                try:
                    found, node = self.search(item)  # find place for item
                    return found or node.insert(item)
                except TypeError as e:
                    raise TypeError('element must be comparable to exisitng items')            
            else:
                return NotImplemented

        def delete(self, item):
            # TODO
            pass

        def __repr__(self):
            state = 'leaf' if self.is_leaf() else 'node'
            state = 'root' if self.is_root() else state
            return "<btree {} {}>".format(state, self.values)

        def __str__(self):
            state = 'leaf' if self.is_leaf() else 'node'
            state = 'root' if self.is_root() else state
            return "<{}{} of btree {}>".format(state, self.values, self.items())

        # support: item in this_subtree
        def __contains__(self, item):
            return self.search(item)[0]

        # iterate over items in this subtree
        def __iter__(self):
            return iter(self.items())

        # get list of items in this subtree
        def items(self):
            if self.is_leaf():
                return self.values[:]
            items = self.children[0].items()
            for index, value in enumerate(self.values):
                items.append(value)
                items.extend(self.children[index + 1].items())
            return items

        def testthis(self):
            node = self
            if not node.is_root():
                assert node in node.parent.children, "i am not in my parent children list"
            
            if not node.is_leaf():
                for x in node.children:
                    assert x.parent is node, "my child has another parent than me"
            assert len(node.values) <= node.k*2, "too many values left in me"
            if not node.is_leaf():
                assert len(node.children) <= node.k*2+1, "too many children left in me"
    # End Node()

    # TODO do it with yield and depth search
    def __init__(self, k, h):
        self.root = BTree.Node(k, h)

    def __contains__(self, item):
        return item in self.root
    
    def __len__(self):
        return len(self.root.items())

    def __iter__(self):
        return iter(self.root)

    def add(self, item):
        if item not in self.root:
            self.root.insert(item)

    def discard(self, item):
        if item in self.root:
            self.root.remove(item)

    def pop(self, last=True):
        if not self.root:
            raise KeyError('BTree is empty')
        item = self.root.items()[-1]
        self.discard(item)
        return item

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    # print this subtree in fancy
    def fancy(self, node=None):
        if not node:
            node = self.root
        print("    "*node.dist() + repr(node))
        if node.children:
            for x in node.children:
                self.fancy(x)
    def foo(self):
        print(set(n))

if __name__ == '__main__':
    if True:
        gdbvalues = [77, 12, 48, 69, 33, 89, 97, 91, 37, 45, 83, 2, 5, 57, 90, 95, 99, 50]
        test = gdbvalues[:18]
        n = BTree(2,20)
    else:
        test = range(1,50)
        n = BTree(1,20)

    for i in test:
        print("insert", i)
        n.add(i)
        assert sorted(n.root.items()) == n.root.items(), "Numbers somehow not in order"
    n.fancy()