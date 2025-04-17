import Rtree
import rtreeBuilder
import rtreeRange
import rtreeNN

class RTree:
    def __init__(self, B=25):
        self.Bvalue = B
        self.root = None

    def build_from_points(self, points):
        if not points:
            raise ValueError("Cannot build from empty point list")
            
        for _, point in enumerate(points):
            point = Rtree.Point(point)
            if self.root is None:
                self.root = Rtree.Leaf(self.Bvalue, 1, point)
                continue
            self.root = rtreeBuilder.insert(self.root, point, self.Bvalue)

    def range_search(self, mbr):
        return [(p.ident, p.x, p.y) for p in rtreeRange.rangeQuery(self.root, mbr)]

    def nearest_neighbors(self, query, k=1):
        class SearchState:
            def __init__(self):
                self.best = []
                self.max_dist = float('inf')
                
        state = SearchState()
        
        def search(nodes):
            while nodes:
                dist, node = nodes.pop(0)
                if dist > state.max_dist:
                    continue
                    
                if isinstance(node, Rtree.Leaf):
                    for point in node.childList:
                        point_dist = (point.x - query[0])**2 + (point.y - query[1])**2
                        if point_dist < state.max_dist or len(state.best) < k:
                            state.best.append((point_dist, point))
                            state.best.sort()
                            state.best = state.best[:k]
                            state.max_dist = state.best[-1][0] if len(state.best) >= k else float('inf')
                else:
                    nodes.extend((rtreeNN.nDis(child, query), child) for child in node.childList)
                    nodes.sort(key=lambda x: x[0])
        
        search([(0, self.root)])
        return [(p.ident, p.x, p.y) for _, p in state.best[:k]]

    def point_query(self, point, epsilon=1e-6):
        """Find exact point using tiny range"""
        return self.range_search([
            point[0] - epsilon,
            point[0] + epsilon,
            point[1] - epsilon,
            point[1] + epsilon
        ])  