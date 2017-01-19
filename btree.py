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
            return True, self
        # if this is a leaf, val belongs in here
        if self.is_leaf():
            return False, self
        # get index for subtree to search in
        index = 0
        while index < len(self.values) and self.values[index] < val:
            index += 1
        subtree = self.children[index]
        return subtree.search(val)

    def split(self):
        assert len(self.values) is 2*self.k + 1, "please split only (over-)full nodes"
        leftvalues = self.values[:self.k]
        leftchildren = self.children[:self.k+1] if self.children else None
        median = self.values[self.k]
        rightvalues = self.values[self.k+1:]
        rightchildren = self.children[self.k+1:] if self.children else None

        if self.is_root():
            root = self
            left = Node(root.k,
                        root.h,
                        root,
                        leftvalues,
                        leftchildren)
            right = Node(root.k,
                         root.h,
                         root,
                         rightvalues,
                         rightchildren)
            root.values = [median]
            root.children = [left, right]

            for x in root.children:
                x.parent = root
                # FUCK THIS.
                # NOT HAVING THIS WAS THE BUG:
                if x.children:
                    for y in x.children:
                        y.parent = x

            if len(root.values) > 2*root.k:
                root.split()
        else:
            root = self.parent
            left = self
            left.values = leftvalues
            left.children = leftchildren

            right = Node(left.k,
                       left.h,
                       root,
                       rightvalues,
                       rightchildren)
            if right.children:
                for x in right.children:
                    x.parent = right
            index = root.children.index(left)
            root.values.insert(index, median)
            root.children.insert(index + 1, right)

            if len(root.values) > 2*root.k:
                root.split()

    def insert(self, val):
        if self.is_leaf():
            if val in self.values:
                return True
            self.values.append(val)
            self.values.sort()
            if len(self.values) > 2*self.k:  # overflow (bigger than 2*k)
                self.split()
                testhis(self)
        else:
            found, node = self.search(val)
            if found:
                return True
            return node.insert(val)

    def delete_val(self, val):
        # TODO
        pass

    def __repr__(self):
        text = '<btree node {}> leaf: {}'.format(str(self.values), self.is_leaf())
        return text

    def __str__(self):
        name = 'leaf' if self.is_leaf() else 'node'
        name = 'root' if self.is_root() else name
        text = '{}{} {}'.format('    '*self.root_dist()+'\\', name, str(self.values))
        if self.children:
            for x in self.children:
                text = text + "\n" + str(x)
        return text

def testthis(node):
    if not node.is_root():
        assert node in node.parent.children, "i am not in my parent children list"
    
    if not node.is_leaf():
        for x in node.children:
            assert x.parent is node, "my child has another parent than me"
    self.testrel() #test if my children have me as parent
    self.testrel2() #test if i am in my parents children list
    assert len(self.values) <= self.k*2, "too many values left in me"
    if not self.is_leaf():
        assert len(self.children) <= self.k*2+1, "too many children left in me"

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
        print(n)
