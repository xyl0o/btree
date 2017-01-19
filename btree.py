#!/usr/bin/python

class Node():
    def __init__(self, k, h, parent=None, values=None, children=None):
        self.k = k
        self.h = h

        self.namefoo=""

        assert not parent or parent.root_dist() + 1 < h, "h = %s is too small for this node" % h
        self.parent = parent

        if values is None:
            values = []
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

    def search(self, val):
        if val in self.values:
            return True, self  # then return this node

        # if this is a leaf, val is here or not in the tree at all
        if self.is_leaf():
            return False, self  # val not in tree

        # get index for subtree to search in
        index = 0
        while index < len(self.values) and self.values[index] < val:
            index += 1
        subtree = self.children[index]
        return subtree.search(val)

    # install new relations
    def put(self, origin, median, new):
        index = self.children.index(origin) + 1
        self.values.insert(index, median)
        self.children.insert(index, new)

        # TODO find another way
        if origin.children:
            for x in origin.children:
                    x.parent = origin
        if new.children:
            for x in new.children:
                    x.parent = new

        if len(self.values) > 2*self.k:
            self.split()

    def split(self):
        assert len(self.values) > 2*self.k, "please split only (over-)full nodes"
        leftvalues = self.values[:self.k]
        # TODO why not: leftchildren = self.children[:self.k+1] if self.children else None
        leftchildren = self.children[:self.k] if self.children else None

        median = self.values[self.k]

        rightvalues = self.values[self.k+1:]
        rightchildren = self.children[self.k+1:] if self.children else None

        if self.is_root():
            if self.children:
                leftchildren = self.children[:self.k+1]
            root = self
            self.values = None
            self.children = None
            left = Node(self.k,
                        self.h,
                        self,
                        leftvalues,
                        leftchildren)
            self.values = []
            self.children = [left]

            self.put(left, median, Node(self.k,
                                        self.h,
                                        self,
                                        rightvalues,
                                        rightchildren))
        else:
            self.values = leftvalues
            self.children = leftchildren

            self.parent.put(self, median, Node(self.k,
                                               self.h,
                                               self,
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
        name = 'leaf' if self.is_leaf() else 'node'
        name = 'root' if self.is_root() else name
        text = '{}{} {}'.format('  '*self.root_dist()+'\\', name, str(self.values))
        if self.children:
            for x in self.children:
                text = text + "\n  " + str(x)
        return text

if __name__ == '__main__':
    n = Node(6,20)

    for i in range(1,150):
        print("\ninsert", i)
        n.insert(i)
        print(n)
