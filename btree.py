#!/usr/bin/python

class Node():
    def __init__(self, k, h, parent, values, children):
        self.k = k
        self.h = h

        self.namefoo=""

        assert not parent or parent.root_dist() + 1 < h, "h = %s is too small for this node" % h
        self.parent = parent

        assert len(values) > 0, "give at least one item"
        assert self.is_root() or len(values) >= k, "only root may contain less than %i" % k
        assert len(values) <= 2*k, "values must contain <= %i elements" % 2*k
        self.values = values # size: 2k

        assert not children or len(children) is len(values) + 1, "given children list does not fit with given values"
        self.children = children

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return not self.children

    def root_dist(self):
        if not self.parent:
            return 0
        return self.parent.root_dist() + 1

    def is_full(self):
        return len(self.values) is 2*self.k

    def search(self, val):
        if val in self.values:
            return True, self  # then return this node

        # if this is a leaf, val is here or not in the tree at all
        if self.is_leaf():
            return False, self  # val not in tree

        # get subtree to search
        index = 0
        while index < len(self.values) and self.values[index] < val:
            index += 1
        # now index points to the item to big for val
        # so it is the correct index for children
        subtree = self.children[index]
        return subtree.search(val)

    def put(self, origin, median, new):
        index = self.children.index(origin) + 1
        self.values.insert(index, median)
        self.children.insert(index, new)
        if len(self.values) > 2*self.k:
            self.split()

    def split(self):
        assert len(self.values) > 2*self.k, "please split only (over-)full nodes"
        # A single median is chosen from among the leaf's elements and the new element.
        median = self.values[self.k]
        # Values less than the median are put in the new left node
        # and values greater than the median are put in the new right node,
        # with the median acting as a separation value.
        leftvalues = self.values[:self.k]
        rightvalues = self.values[self.k+1:]
        if self.children:
            leftchildren = self.children[:self.k]  # TODO copy also childen
            rightchildren = self.children[self.k+1:]  # TODO copy also childen
        else:
            leftchildren = None
            rightchildren = None
        # The separation value is inserted in the node's parent,
        # which may cause it to be split, and so on.
        # If the node has no parent (i.e., the node was the root),
        # create a new root above this node (increasing the height of the tree)
        self.values = leftvalues 
        self.children = leftchildren
        if self.is_root():
            # TODO
            pass
        else:
            self.parent.put(self, median, Node(self.k,
                                               self.h,
                                               self.parent,
                                               rightvalues,
                                               rightchildren))
        
    def insert(self, val):
        if self.is_leaf():
            if val in self.values:
                return True
            self.values.append(val)
            self.values.sort()
            if len(self.values) > 2*self.k:  # overflow (bigger than 2*k)
                self.split()
        else:
            found, node = self.search(val)
            if found:
                return True
            return node.insert(val)

    def delete_val(self, val):
        # TODO
        pass

    def __repr__(self):
        text = '<{} {}>'.format('BTree Node', str(self.values))
        if self.children:
            for x in enumerate(self.children):
                text = text + "\n  " + str(x) + "  " + str(x[1].namefoo)
        return text

def main():
    #root = Node(k=2, h=1, parent=None, values=[2], children=None)
    pass

if __name__ == '__main__':
    k = 2
    h = 2
    n = Node(k, h, None, [5], None)
    child1 = Node(k, h, n, [1, 2, 3, 4], None)
    child1.namefoo = "child1"
    child2 = Node(k, h, n, [6, 7, 8], None)
    n.children = [child1, child2]
    child2.namefoo = "child2"

    for i in range(9,20):
        n.insert(i)
        print("insert: {}\n{}".format(i,n))
