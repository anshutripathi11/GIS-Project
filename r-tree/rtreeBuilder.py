
# private libraries
import Rtree

def handleOverFlow(node, Bvalue):
    new_nodes = node.split()  # Now returns a list
    
    if node.paren is None:
        new_root = Rtree.Branch(Bvalue, node.level + 1, None)
        new_root.childList = new_nodes  # Assign list directly
        new_root._calculate_mbr()
        return new_root
    else:
        parent = node.paren
        parent.childList.remove(node)
        parent.childList.extend(new_nodes)  # Extend with list items
        parent._calculate_mbr()
        return handleOverFlow(parent, Bvalue) if parent.isOverFlow() else parent

def insert(node, point, Bvalue):
    if isinstance(node, Rtree.Leaf):
        node.childList.append(point)
        node._calculate_mbr()
        return handleOverFlow(node, Bvalue) if node.isOverFlow() else node
    elif isinstance(node, Rtree.Branch):
        child = node.chooseChild(point)
        updated_child = insert(child, point, Bvalue)
        # Replace child directly using list operations
        index = node.childList.index(child)
        node.childList[index] = updated_child
        node._calculate_mbr()
        return handleOverFlow(node, Bvalue) if node.isOverFlow() else node

def handleOverFlow(node, Bvalue):
    new_nodes = node.split()
    
    if node.paren is None:
        new_root = Rtree.Branch(Bvalue, node.level + 1, None)
        new_root.childList = new_nodes
        new_root._calculate_mbr()
        return new_root
    else:
        parent = node.paren
        parent.childList.remove(node)
        parent.childList.extend(new_nodes)
        parent._calculate_mbr()
        if parent.isOverFlow():
            return handleOverFlow(parent, Bvalue)
        return parent

# check all nodes and points in a r-tree
def checkRtree(rtree):    
    checkBranch(rtree)
    print('Finished checking R-tree')

# check the correctness of a leaf node in r-tree
def checkLeaf(leaf):    
    # check whether a point is inside of a leaf
    def insideLeaf(x, y, parent):
        if x<parent[0] or x>parent[1] or y<parent[2] or y>parent[3]:
            return False
        else:
            return True
    
    # general check
    checkNode(leaf)
    # check whether each child point is inside of leaf's range
    for point in leaf.childList:
        if not insideLeaf(point.x, point.y, leaf.range):
            print('point(', point.x, point.y, 'is not in leaf range:', leaf.range)

# check the correctness of a branch node in r-tree
def checkBranch(branch):    
    # check whether a branch is inside of another branch
    def insideBranch(child, parent):
        if child[0]<parent[0] or child[1]>parent[1] or child[2]<parent[2] or child[3]>parent[3]:
            return False
        else:
            return True
    
    # general check
    checkNode(branch)
    # check whether child's range is inside of this node's range
    for child in branch.childList:
        if not insideBranch(child.range, branch.range):
            print('child range:', child.range, 'is not in node range:', branch.range)
        # check this child
        if isinstance(child, Rtree.Branch):
            # if child is still a branch node, check recursively
            checkBranch(child)
        elif isinstance(child, Rtree.Leaf):
            # if child is a leaf node
            checkLeaf(child)

# general check for both branch and leaf node
def checkNode(node):
    global Bvalue
    
    length = len(node.childList)
    # check whether is empty
    if length == 0:
        print('empty node. node level:', node.level, 'node range:', node.range)
    # check whether overflow
    if length > Bvalue:
        print('overflow. node level:', node.level, 'node range:', node.range)
        
    # check whether the centre is really in the centre of the node's range
    r = node.range
    if (r[0]+r[1])/2 != node.centre[0] or (r[2]+r[3])/2 != node.centre[1]:
        print('wrong centre. node level:', node.level, 'node range:', node.range)
    if r[0]>r[1] or r[2]>r[3]:
        print('wrong range. node level:', node.level, 'node range:', node.range)