import math

def euclidean_compare(ref_point, check_point):
    dx = max(ref_point.x, check_point.x) - min(ref_point.x, check_point.x)
    dy = max(ref_point.y, check_point.y) - min(ref_point.y, check_point.y)
    return dx ** 2 + dy ** 2

def euclidean_distance(ref_point, check_point):
    return math.sqrt(euclidean_compare(ref_point, check_point))


class Point(object):
    """
    An object representing X/Y cartesean coordinates.
    """

    def __init__(self, x, y, data=None):
        """
        Constructs a `Point` object.

        Args:
            x (int|float): The X coordinate.
            y (int|float): The Y coordinate.
            data (any): Optional. Corresponding data for that point. Default
                is `None`.
        """
        self.x = x
        self.y = y
        self.data = data
        self.structure_name = None
        structure_name_new_name, structure_name_old_name = None, None
        if self.data is not None:
            structure_name_new_name = self.data.get("name")
            structure_name_old_name = self.data.get("old_name")

        if structure_name_old_name and len(structure_name_old_name) > 0:
            self.structure_name = structure_name_old_name
        else:
            self.structure_name = structure_name_new_name

    def __repr__(self):
        return "<Point: ({}, {}, {})>".format(self.x, self.y, self.structure_name)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))


class BoundingBox(object):
    """
    A object representing a bounding box.
    """

    def __init__(self, min_x, min_y, max_x, max_y):
        """
        Constructs a `Bounding Box` object.

        Args:
            min_x (int|float): The minimum X coordinate.
            min_y (int|float): The minimum Y coordinate.
            max_x (int|float): The maximum X coordinate.
            max_y (int|float): The maximum Y coordinate.
        """
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

        self.width = self.max_x - self.min_x
        self.height = self.max_y - self.min_y
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.center = Point(self.half_width, self.half_height)

    def __repr__(self):
        return "<BoundingBox: ({}, {}) to ({}, {})>".format(
            self.min_x, self.min_y, self.max_x, self.max_y
        )

    def contains(self, point):
        return (
            self.min_x <= point.x <= self.max_x
            and self.min_y <= point.y <= self.max_y
        )

    def intersects(self, other_bb):
        return not (
            other_bb.min_x > self.max_x
            or other_bb.max_x < self.min_x
            or other_bb.max_y < self.min_y
            or other_bb.min_y > self.max_y
        )


class QuadNode(object):
    POINT_CAPACITY = 4
    point_class = Point
    bb_class = BoundingBox

    def __init__(self, center, width, height, capacity=None):
        self.center = center
        self.width = width
        self.height = height
        self.points = []

        self.ul = None
        self.ur = None
        self.ll = None
        self.lr = None

        if capacity is None:
            capacity = self.POINT_CAPACITY

        self.capacity = capacity
        self.bounding_box = self._calc_bounding_box()

    def __repr__(self):
        return "<QuadNode: ({}, {}) {}x{}>".format(
            self.center.x, self.center.y, self.width, self.height
        )

    def __contains__(self, point):
        return self.find(point) is not None

    def __len__(self):
        """
        Returns a count of how many points are in the node.

        Returns:
            int: A count of all the points.
        """
        count = len(self.points)

        if self.ul is not None:
            count += len(self.ul)

        if self.ur is not None:
            count += len(self.ur)

        if self.ll is not None:
            count += len(self.ll)

        if self.lr is not None:
            count += len(self.lr)

        return count

    def __iter__(self):
        """
        Iterates (lazily) over all the points located within a node &
        its children.

        Returns:
            iterable: All the `Point` objects.
        """
        # Make sure we slice it, so that we copy the whole list & don't
        # risk modifying the original.
        for pnt in self.points[:]:
            yield pnt

        if self.ul is not None:
            yield from self.ul

        if self.ur is not None:
            yield from self.ur

        if self.ll is not None:
            yield from self.ll

        if self.lr is not None:
            yield from self.lr

    def _calc_bounding_box(self):
        half_width = self.width / 2
        half_height = self.height / 2

        min_x = self.center.x - half_width
        min_y = self.center.y - half_height
        max_x = self.center.x + half_width
        max_y = self.center.y + half_height

        return self.bb_class(
            min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y
        )

    def contains_point(self, point):
        """
        Checks if a point would be within the bounding box of the node.

        This is a bounding check, not verification the point is present in
        the data.

        Args:
            point (Point): The point to check.

        Returns:
            bool: `True` if it is within the bounds, otherwise `False`.
        """
        bb = self.bounding_box

        if bb.min_x <= point.x <= bb.max_x:
            if bb.min_y <= point.y <= bb.max_y:
                return True

        return False

    def is_ul(self, point):
        return point.x < self.center.x and point.y >= self.center.y

    def is_ur(self, point):
        return point.x >= self.center.x and point.y >= self.center.y

    def is_ll(self, point):
        return point.x < self.center.x and point.y < self.center.y

    def is_lr(self, point):
        return point.x >= self.center.x and point.y < self.center.y

    def subdivide(self):
        half_width = self.width / 2
        half_height = self.height / 2
        quarter_width = half_width / 2
        quarter_height = half_height / 2

        ul_center = self.point_class(
            self.center.x - quarter_width, self.center.y + quarter_height
        )
        self.ul = self.__class__(
            ul_center, half_width, half_height, capacity=self.capacity
        )

        ur_center = self.point_class(
            self.center.x + quarter_width, self.center.y + quarter_height
        )
        self.ur = self.__class__(
            ur_center, half_width, half_height, capacity=self.capacity
        )

        ll_center = self.point_class(
            self.center.x - quarter_width, self.center.y - quarter_height
        )
        self.ll = self.__class__(
            ll_center, half_width, half_height, capacity=self.capacity
        )

        lr_center = self.point_class(
            self.center.x + quarter_width, self.center.y - quarter_height
        )
        self.lr = self.__class__(
            lr_center, half_width, half_height, capacity=self.capacity
        )

        # Redistribute the points.
        # Manually call `append` here, as calling `.insert()` creates an
        # infinite recursion situation.
        for pnt in self.points:
            if self.is_ul(pnt):
                self.ul.points.append(pnt)
            elif self.is_ur(pnt):
                self.ur.points.append(pnt)
            elif self.is_ll(pnt):
                self.ll.points.append(pnt)
            else:
                self.lr.points.append(pnt)

        self.points = []

    def insert(self, point):
        if not self.contains_point(point):
            raise ValueError(
                "Point {} is not within this node ({} - {}).".format(
                    point, self.center, self.bounding_box
                )
            )

        # Check to ensure we're not going to go over capacity.
        if (len(self.points) + 1) > self.capacity:
            # We're over capacity. Subdivide, then insert into the new child.
            self.subdivide()

        if self.ul is not None:
            if self.is_ul(point):
                return self.ul.insert(point)
            elif self.is_ur(point):
                return self.ur.insert(point)
            elif self.is_ll(point):
                return self.ll.insert(point)
            elif self.is_lr(point):
                return self.lr.insert(point)

        # There are no child nodes & we're under capacity. Add it to `points`.
        self.points.append(point)
        return True

    def find(self, point):
        found_node, _ = self.find_node(point)

        if found_node is None:
            return None

        # Try the points on this node first.
        for pnt in found_node.points:
            if pnt.x == point.x and pnt.y == point.y:
                return pnt

        return None

    def find_node(self, point, searched=None):
        if searched is None:
            searched = []

        if not self.contains_point(point):
            return None, searched

        searched.append(self)

        # Check the children.
        if self.is_ul(point):
            if self.ul is not None:
                return self.ul.find_node(point, searched)
        elif self.is_ur(point):
            if self.ur is not None:
                return self.ur.find_node(point, searched)
        elif self.is_ll(point):
            if self.ll is not None:
                return self.ll.find_node(point, searched)
        elif self.is_lr(point):
            if self.lr is not None:
                return self.lr.find_node(point, searched)

        # Not found in any children. Return this node.
        return self, searched

    def all_points(self):
        return list(iter(self))

    def within_bb(self, bb):
        points = []

        # If we don't intersect with the bounding box, return an empty list.
        if not self.bounding_box.intersects(bb):
            return points

        # Check if any of the points on this instance are within the BB.
        for pnt in self.points:
            if bb.contains(pnt):
                points.append(pnt)

        if self.ul is not None:
            points += self.ul.within_bb(bb)

        if self.ur is not None:
            points += self.ur.within_bb(bb)

        if self.ll is not None:
            points += self.ll.within_bb(bb)

        if self.lr is not None:
            points += self.lr.within_bb(bb)

        return points


class QuadTree(object):
    node_class = QuadNode
    point_class = Point

    def __init__(self, center, width, height, capacity=None):
        """
        Constructs a `QuadTree` object.

        Args:
            center (tuple|Point): The center point of the quadtree.
            width (int|float): The width of the point space.
            height (int|float): The height of the point space.
            capacity (int): Optional. The number of points per quad before
                subdivision occurs. Default is `None`.
        """
        self.width = width
        self.height = height
        self.center = self.convert_to_point(center)
        self._root = self.node_class(
            self.center, self.width, self.height, capacity=capacity
        )

    def __repr__(self):
        return "<QuadTree: ({}, {}) {}x{}>".format(
            self.center.x, self.center.y, self.width, self.height,
        )

    def convert_to_point(self, val):
        """
        Converts a value to a `Point` object.

        This is to allow shortcuts, like providing a tuple for a point.

        Args:
            val (Point|tuple|None): The value to convert.

        Returns:
            Point: A point object.
        """
        if isinstance(val, self.point_class):
            return val
        elif isinstance(val, (tuple, list)):
            return self.point_class(val[0], val[1])
        elif val is None:
            return self.point_class(0, 0)
        else:
            raise ValueError(
                "Unknown data provided for point. Please use one of: "
                "quads.Point | tuple | list | None"
            )

    def __contains__(self, point):
        """
        Checks if a `Point` is found in the quadtree.

        > Note: This doesn't check if a point is within the bounds of the
        > tree, but if that *specific point* is in the tree.

        Args:
            point (Point|tuple|None): The point to check for.

        Returns:
            bool: `True` if found, otherwise `False`.
        """
        pnt = self.convert_to_point(point)
        return self.find(pnt) is not None

    def __len__(self):
        """
        Returns a count of how many points are in the tree.

        Returns:
            int: A count of all the points.
        """
        return len(self._root)

    def __iter__(self):
        """
        Returns an iterator for all the points in the tree.

        Returns:
            iterator: An iterator of all the points.
        """
        return iter(self._root)

    def insert(self, point, data=None):
        """
        Inserts a `Point` into the quadtree.

        Args:
            point (Point|tuple|None): The point to insert.
            data (any): Optional. Corresponding data for that point. Default
                is `None`.

        Returns:
            bool: `True` if insertion succeeded, otherwise `False`.
        """
        pnt = self.convert_to_point(point)
        # pnt.data = data
        return self._root.insert(pnt)

    def find(self, point):
        """
        Searches for a `Point` within the quadtree.

        Args:
            point (Point|tuple|None): The point to search for.

        Returns:
            Point|None: Returns the `Point` (including it's data) if found.
                `None` if the point is not found.
        """
        pnt = self.convert_to_point(point)
        return self._root.find(pnt)

    def within_bb(self, bb):
        """
        Checks if a bounding box is within the quadtree's bounding box.

        Primarily for internal use, but stable API if you need it.

        Args:
            bb (BoundingBox): The bounding box to check.

        Returns:
            bool: `True` if the bounding boxes intersect, otherwise `False`.
        """
        return self._root.within_bb(bb)

    def nearest_neighbors(self, point, count=10):
        """
        Returns the nearest points of a given point, sorted by distance
        (closest first).

        The desired point does not need to exist within the quadtree, but
        does need to be within the tree's boundaries.

        Args:
            point (Point): The desired location to search around.
            count (int): Optional. The number of neighbors to return. Default
                is `10`.

        Returns:
            list: The nearest `Point` neighbors.
        """
       

        point = self.convert_to_point(point)
        nearest_results = []

        # Check to see if it's within our bounds first.
        if not self._root.contains_point(point):
            return nearest_results

        # First, find the target node.
        node, searched_nodes = self._root.find_node(point)

        # Reverse the order, as they come back in coarse-to-fine order, which
        # is the opposite of nearby points.
        searched_nodes.reverse()
        seen_nodes = set()
        seen_points = set()

        # From here, we'll work our way backwards out through the nodes.
        for node in searched_nodes:
            # Mark the node as already checked.
            seen_nodes.add(node)
            local_points = []

            for pnt in node.all_points():
                if pnt in seen_points:
                    continue

                seen_points.add(pnt)
                local_points.append(pnt)

            local_points = sorted(
                local_points, key=lambda lpnt: euclidean_compare(point, lpnt)
            )
            nearest_results.extend(local_points)

            if len(nearest_results) >= count:
                break

        # Slice off any extras.
        nearest_results = nearest_results[:count]

        if len(seen_nodes) == len(searched_nodes):
            # We've exhausted everything. Return what we've got.
            return nearest_results[:count]

        search_radius = euclidean_distance(point, nearest_results[-1])
        search_bb = BoundingBox(
            point.x - search_radius,
            point.y - search_radius,
            point.x + search_radius,
            point.y + search_radius,
        )
        bb_results = self._root.within_bb(search_bb)
        nearest_results = sorted(
            bb_results, key=lambda lpnt: euclidean_compare(point, lpnt)
        )

        return nearest_results[:count]