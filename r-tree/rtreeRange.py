import Rtree
def isIntersect(range1, range2):
    return not (range1[0] > range2[1] or 
               range1[1] < range2[0] or 
               range1[2] > range2[3] or 
               range1[3] < range2[2])

def searchLeaf(leaf, query_range):
    return [p for p in leaf.childList 
            if (p.x >= query_range[0] and p.x <= query_range[1] and
                p.y >= query_range[2] and p.y <= query_range[3])]

def rangeQuery(node, query_range):
    results = []
    if isinstance(node, Rtree.Leaf):
        results.extend(searchLeaf(node, query_range))
    else:
        for child in node.childList:
            if isIntersect(child.range, query_range):
                results.extend(rangeQuery(child, query_range))
    return results