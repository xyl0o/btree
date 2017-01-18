#!/usr/bin/python

class Node():
    def __init__(self, k, h, parent, values, children):
        self.k = k
        self.h = h

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
        # if this is a leaf, val is here or not in the tree at all
        if self.is_leaf():
            # is it in this node?
            if val in self.values:
                return True, self  # then return this node
            else:
                return False, self  # val not in tree

        # get subtree to search
        index = 0
        while index < len(self.values) and self.values[index] < val:
            ++index
        # now index points to the item to big for val
        # so it is the correct index for children
        subtree = self.children[index]
        return subtree.search(val)

    # TODO
    def split(self):
        assert len(self.values) > 2*self.k, "please split only (over-)full nodes"
        # A single median is chosen from among the leaf's elements and the new element.
        median = self.values[self.k]
        # Values less than the median are put in the new left node
        # and values greater than the median are put in the new right node,
        # with the median acting as a separation value.
        leftvalues = self.values[:self.k]
        rightvalues = self.values[self.k+1:]
        # The separation value is inserted in the node's parent,
        # which may cause it to be split, and so on.
        # If the node has no parent (i.e., the node was the root),
        # create a new root above this node (increasing the height of the tree)
        if self.is_root():
            # keep it root
            # TODO --children--
            newleft = Node(self.k, self.h, self, leftvalues, --children--)
            newright = Node(self.k, self.h, self, rightvalues, --children--)
            newvalues = [median]
            newchildren = [newleft, newright]
        else:
            # TODO
            index = self.parent.children.index(self)
            # is there room?
            #  -> self.values(index) is free
            #  -> self.children(index + 1) is free
            #  -> no overflow will occur
            if self.parent.thereisroom():
                parent.values.insert(index, median)
                parent.children.insert(index + 1, rightnode)
            else:
                #split parent node:
                #  values + median
                #  get new left, median, right
                #  preserve children
                #  if needed create new root
            # self.parent.split(self, median, Node(self.k,
            #                                      self.h,
            #                                      self.parent,
            #                                      right,
            #                                      None))

    def insert(self, val):
        if self.is_leaf():
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

def main():
    #root = Node(k=2, h=1, parent=None, values=[2], children=None)

if __name__ == '__main__':
    main()
