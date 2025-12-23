"""
Utilities module - Hex math, procedural generation, pathfinding
"""
import math
import random
from typing import Tuple, List, Set
from collections import deque


class HexGrid:
    """Hexagonal grid coordinate system utilities"""

    def __init__(self, radius: float = 30.0):
        """
        Initialize hex grid with given hex radius

        Args:
            radius: Distance from center to corner of hex
        """
        self.radius = radius
        # Calculate other hex dimensions
        self.width = radius * 2
        self.height = radius * math.sqrt(3)
        self.horizontal_spacing = self.width * 3/4
        self.vertical_spacing = self.height

    def get_hex_vertices(self, q: int, r: int) -> List[Tuple[float, float]]:
        """Get the 6 vertices of a hex at coordinates (q, r)"""
        center_x, center_y = self.hex_to_pixel(q, r)
        vertices = []

        for i in range(6):
            angle = math.pi / 3 * i
            vx = center_x + self.radius * math.cos(angle)
            vy = center_y + self.radius * math.sin(angle)
            vertices.append((vx, vy))

        return vertices

    def hex_to_pixel(self, q: int, r: int) -> Tuple[float, float]:
        """Convert hex coordinates to pixel coordinates"""
        x = self.radius * (3/2 * q)
        y = self.radius * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        return (x, y)

    def pixel_to_hex(self, x: float, y: float) -> Tuple[int, int]:
        """Convert pixel coordinates to hex coordinates"""
        q = (2/3 * x) / self.radius
        r = (-1/3 * x + math.sqrt(3)/3 * y) / self.radius
        return self.hex_round(q, r)

    def hex_round(self, q: float, r: float) -> Tuple[int, int]:
        """Round fractional hex coordinates to nearest hex"""
        s = -q - r
        rq = round(q)
        rr = round(r)
        rs = round(s)

        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)

        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs

        return (rq, rr)

    def get_hex_distance(self, q1: int, r1: int, q2: int, r2: int) -> int:
        """Get distance between two hexes"""
        return (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

    def get_hex_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        """Get coordinates of all 6 neighboring hexes"""
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]

        neighbors = []
        for dq, dr in directions:
            neighbors.append((q + dq, r + dr))

        return neighbors


def hex_to_pixel(q: int, r: int, radius: float = 30.0) -> Tuple[float, float]:
    """Convert hex coordinates to pixel coordinates (convenience function)"""
    grid = HexGrid(radius)
    return grid.hex_to_pixel(q, r)


def pixel_to_hex(x: float, y: float, radius: float = 30.0) -> Tuple[int, int]:
    """Convert pixel coordinates to hex coordinates (convenience function)"""
    grid = HexGrid(radius)
    return grid.pixel_to_hex(x, y)


def hex_distance(q1: int, r1: int, q2: int, r2: int) -> int:
    """Get distance between two hexes (convenience function)"""
    grid = HexGrid()
    return grid.get_hex_distance(q1, r1, q2, r2)


class ProceduralGenerator:
    """Simple procedural generation utilities"""

    @staticmethod
    def generate_desert_features(radius: int = 10) -> List[Tuple[int, int, str]]:
        """
        Generate desert features like oases, ruins, etc.

        Returns:
            List of (q, r, feature_type) tuples
        """
        features = []

        # Generate some oases
        num_oases = random.randint(2, 5)
        for _ in range(num_oases):
            q = random.randint(-radius, radius)
            r = random.randint(-radius, radius)
            features.append((q, r, 'oasis'))

        # Generate some ruins
        num_ruins = random.randint(1, 3)
        for _ in range(num_ruins):
            q = random.randint(-radius, radius)
            r = random.randint(-radius, radius)
            features.append((q, r, 'ruins'))

        return features

    @staticmethod
    def generate_caravan_route(start_q: int, start_r: int, length: int = 5) -> List[Tuple[int, int]]:
        """Generate a caravan route from start position"""
        route = [(start_q, start_r)]
        current_q, current_r = start_q, start_r

        for _ in range(length):
            # Move in a somewhat random direction
            directions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
            dq, dr = random.choice(directions)

            current_q += dq
            current_r += dr
            route.append((current_q, current_r))

        return route

    @staticmethod
    def simple_noise(x: float, y: float, seed: int = 42) -> float:
        """Simple pseudo-random noise function"""
        # Very basic noise - for production, use a proper noise library
        random.seed(int(x * 73856093 + y * 19349663 + seed))
        return random.random()


class AStarPathfinder:
    """A* pathfinding for hex grids"""

    def __init__(self, grid_radius: HexGrid):
        self.grid = grid_radius

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  obstacles: Set[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """
        Find path from start to goal using A*

        Args:
            start: Starting hex coordinates (q, r)
            goal: Goal hex coordinates (q, r)
            obstacles: Set of hexes that cannot be traversed

        Returns:
            List of hex coordinates forming the path, or empty list if no path found
        """
        if obstacles is None:
            obstacles = set()

        if start in obstacles or goal in obstacles:
            return []

        # Priority queue for open set
        open_set = []
        # Dictionary to store g_score (cost from start)
        g_score = {start: 0}
        # Dictionary to store f_score (estimated total cost)
        f_score = {start: self._heuristic(start, goal)}
        # Dictionary to store came_from
        came_from = {}

        open_set.append((f_score[start], start))

        while open_set:
            # Get node with lowest f_score
            current_f, current = min(open_set)
            open_set.remove((current_f, current))

            if current == goal:
                return self._reconstruct_path(came_from, current)

            # Check all neighbors
            for neighbor in self.grid.get_hex_neighbors(*current):
                if neighbor in obstacles:
                    continue

                tentative_g = g_score[current] + 1  # Assume cost of 1 for each step

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal)

                    # Add to open set if not already there
                    if not any(neighbor == item[1] for item in open_set):
                        open_set.append((f_score[neighbor], neighbor))

        return []  # No path found

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Heuristic function for A* (hex distance)"""
        return self.grid.get_hex_distance(*a, *b)

    def _reconstruct_path(self, came_from: dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
