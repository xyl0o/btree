#!/usr/bin/python

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

        testthis(self)  # all the asserts

    # split and rebalance an overflowed node recursively
    def split(self):
        values = self.values[:]
        lchild = self.children[:self.k+1] if self.children else None
        rchild = self.children[self.k+1:] if self.children else None
            
        if self.is_root():
            parent = self
            left = Node(parent.k, parent.h, parent, values[:self.k], lchild)
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
        right = Node(parent.k, parent.h, parent, values[self.k+1:], rchild)
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

    # print this subtree in fancy
    def fancy(self):
        print("    "*self.dist() + repr(self))
        if self.children:
            for x in self.children:
                x.fancy()

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

def testthis(node):
    if not node.is_root():
        assert node in node.parent.children, "i am not in my parent children list"
    
    if not node.is_leaf():
        for x in node.children:
            assert x.parent is node, "my child has another parent than me"
    assert len(node.values) <= node.k*2, "too many values left in me"
    if not node.is_leaf():
        assert len(node.children) <= node.k*2+1, "too many children left in me"

if __name__ == '__main__':
    if True:
        gdbvalues = [77, 12, 48, 69, 33, 89, 97, 91, 37, 45, 83, 2, 5, 57, 90, 95, 99, 50]
        test = gdbvalues[:18]
        n = Node(2,20)
    else:
        test = range(1,500)
        n = Node(1,20)

    for i in test:
        print("\ninsert", i)
        n.insert(i)
        n.fancy()
        assert sorted(n.items()) == n.items(), "Numbers somehow not in order"

