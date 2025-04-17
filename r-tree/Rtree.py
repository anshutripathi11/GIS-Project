import math

def euclidean_compare(ref_point, check_point):
    dx = max(ref_point.x, check_point.x) - min(ref_point.x, check_point.x)
    dy = max(ref_point.y, check_point.y) - min(ref_point.y, check_point.y)
    return dx ** 2 + dy ** 2

def euclidean_distance(ref_point, check_point):
    return math.sqrt(euclidean_compare(ref_point, check_point))

class Point:
    def __init__(self, pointInfo):
        self.ident = self.x = self.y = None
        if isinstance(pointInfo, Point):
            self.ident = pointInfo.ident
            self.x = pointInfo.x
            self.y = pointInfo.y
        else:
            if len(pointInfo) < 3:
                raise ValueError("Point info requires (id, x, y)")
            self.ident = pointInfo[0]
            self.x = pointInfo[1]
            self.y = pointInfo[2]

    def position(self, index):
        return self.x if index == 1 else self.y

class Node:
    def __init__(self, Bvalue, level):
        self.childList = []
        self.range = []
        self.centre = []
        self.Bvalue = Bvalue
        self.paren = None
        self.level = level

    def addChild(self, child):
        self.childList.append(child)
        self.update(child)
        if isinstance(child, Node):
            child.paren = self

    def update(self, child):
        if isinstance(child, Point):
            self.updateRange([child.x, child.x, child.y, child.y])
        elif isinstance(child, Node):
            self.updateRange(child.range)
        
        self._calculate_mbr()

    def updateRange(self, newRange):
        self.range = [
            min(self.range[0], newRange[0]) if self.range else newRange[0],
            max(self.range[1], newRange[1]) if self.range else newRange[1],
            min(self.range[2], newRange[2]) if self.range else newRange[2],
            max(self.range[3], newRange[3]) if self.range else newRange[3]
        ]

    def _calculate_mbr(self):
        if not self.childList:
            return
        
        x_coords = []
        y_coords = []
        
        for child in self.childList:
            if isinstance(child, Point):
                x_coords.append(child.x)
                y_coords.append(child.y)
            else:
                x_coords.extend([child.range[0], child.range[1]])
                y_coords.extend([child.range[2], child.range[3]])
        
        self.range = [
            min(x_coords), max(x_coords),
            min(y_coords), max(y_coords)
        ]
        self.centre = [
            (self.range[0] + self.range[1])/2,
            (self.range[2] + self.range[3])/2
        ]

    def isOverFlow(self):
        return len(self.childList) > self.Bvalue

    def getIncrease(self, point):
        increase = 0
        if point.x < self.range[0]:
            increase += self.range[0] - point.x
        elif point.x > self.range[1]:
            increase += point.x - self.range[1]
        if point.y < self.range[2]:
            increase += self.range[2] - point.y
        elif point.y > self.range[3]:
            increase += point.y - self.range[3]
        return increase

    def getPerimeter(self):
        return (self.range[1] - self.range[0]) + (self.range[3] - self.range[2])

class Leaf(Node):
    def __init__(self, Bvalue, level, point):
        super().__init__(Bvalue, level)
        self.addChild(point)

    def split(self):
        min_entries = max(1, math.floor(0.4 * self.Bvalue))
        best_split = None
        min_perimeter = float('inf')
        
        # Try all possible splits that respect B-value
        for split_idx in range(min_entries, len(self.childList) - min_entries + 1):
            left = Leaf(self.Bvalue, self.level, self.childList[0])
            right = Leaf(self.Bvalue, self.level, self.childList[0])
            
            # Use slicing to avoid cascading inserts
            left.childList = self.childList[:split_idx]
            right.childList = self.childList[split_idx:]
            left._calculate_mbr()
            right._calculate_mbr()
            
            # Enforce B-value constraint
            if len(left.childList) > self.Bvalue or len(right.childList) > self.Bvalue:
                continue  # Skip invalid splits
                
            current_perim = left.getPerimeter() + right.getPerimeter()
            if current_perim < min_perimeter:
                min_perimeter = current_perim
                best_split = [left, right]
        
        # Fallback split with forced B-value compliance
        if not best_split:
            mid = min(self.Bvalue, len(self.childList) - 1)  # Never exceed B
            left = Leaf(self.Bvalue, self.level, self.childList[0])
            right = Leaf(self.Bvalue, self.level, self.childList[0])
            left.childList = self.childList[:mid]
            right.childList = self.childList[mid:]
            left._calculate_mbr()
            right._calculate_mbr()
            best_split = [left, right]
        
        return best_split

    def sortChildren(self, index):
        self.childList.sort(key=lambda p: p.position(index))

class Branch(Node):
    def __init__(self, Bvalue, level, node):
        super().__init__(Bvalue, level)
        if node is not None:
            self.addChild(node)

    def chooseChild(self, point):
        return min(self.childList, key=lambda c: c.getIncrease(point))

    def split(self):
        min_entries = math.floor(0.4 * self.Bvalue)
        best_split = None
        min_perim = float('inf')
        
        # Axis-aligned split with B-value enforcement
        for axis in [0, 1, 2, 3]:
            self.childList.sort(key=lambda c: c.range[axis])
            for i in range(min_entries, len(self.childList) - min_entries + 1):
                left = Branch(self.Bvalue, self.level, None)
                right = Branch(self.Bvalue, self.level, None)
                left.childList = self.childList[:i]
                right.childList = self.childList[i:]
                left._calculate_mbr()
                right._calculate_mbr()
                
                if len(left.childList) > self.Bvalue or len(right.childList) > self.Bvalue:
                    continue
                    
                current_perim = left.getPerimeter() + right.getPerimeter()
                if current_perim < min_perim:
                    min_perim = current_perim
                    best_split = [left, right]
        
        # Guaranteed valid split
        if not best_split:
            mid = min(self.Bvalue, len(self.childList) - 1)
            left = Branch(self.Bvalue, self.level, None)
            right = Branch(self.Bvalue, self.level, None)
            left.childList = self.childList[:mid]
            right.childList = self.childList[mid:]
            left._calculate_mbr()
            right._calculate_mbr()
            best_split = [left, right]
        
        return best_split