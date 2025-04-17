# standard libraries


# private libraries
import Rtree

# the nearest distance
global distance
# the nearest neighbors
global results

# the nearest distance from a query point to a node
def nDis(node, query):
    distance = 0
    if query[0] < node.range[0]:
        distance += (node.range[0] - query[0])**2
    elif query[0] > node.range[1]:
        distance += (query[0] - node.range[1])**2
    if query[1] < node.range[2]:
        distance += (node.range[2] - query[1])**2
    elif query[1] > node.range[3]:
        distance += (query[1] - node.range[3])**2
    return distance

# in a leaf, find all points which have the least distance from the query point
def getNN(leaf, query):
    global distance
    global results
    
    for point in leaf.childList:
        newDis = (point.x-query[0])**2 + (point.y-query[1])**2
        if newDis < distance:
            distance = newDis
            results.clear()
            results.append(point)
        elif newDis == distance:
            results.append(point)

# answer a NN query using "Best First" algorithm
def bestFirst(tupleList, query):
    global distance

    if isinstance(tupleList[0][1], Rtree.Branch):
        node = tupleList[0][1]
        # remove the first element in the tuple list
        del tupleList[0]
        # add all children of the first node to the tuple list
        for child in node.childList:
            tupleList.append((nDis(child, query), child))
        # sort the tuple list by distance
        tupleList = sorted(tupleList, key=lambda t:t[0])
    elif isinstance(tupleList[0][1], Rtree.Leaf):
        node = tupleList[0][1]
        # remove the first element in the tuple list
        del tupleList[0]
        getNN(node, query)
        
    # in this case, the NN has been found
    if distance < tupleList[0][0]:
        return
    # implement Best First algorithm resursively
    bestFirst(tupleList, query)


