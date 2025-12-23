"""
Caravan module - Defines caravan entities in the game world
"""
import random
import time
from typing import Tuple, List


class Caravan:
    """Represents a trade caravan in the desert"""

    CARAVAN_TYPES = ['salt', 'gold', 'spices', 'imperial', 'sandworm']

    # Type configurations
    TYPE_CONFIGS = {
        'salt': {
            'name': 'Salt Caravan',
            'escorts_range': (3, 8),
            'loot_range': (50, 150),
            'size': 'small',
            'move_interval': 45,  # seconds between moves
            'loot_types': {'salt': 0.8, 'gold': 0.2}  # Distribution of loot types
        },
        'gold': {
            'name': 'Gold Caravan',
            'escorts_range': (8, 15),
            'loot_range': (200, 500),
            'size': 'medium',
            'move_interval': 40,
            'loot_types': {'gold': 0.9, 'spices': 0.1}
        },
        'spices': {
            'name': 'Spice Caravan',
            'escorts_range': (15, 25),
            'loot_range': (500, 1000),
            'size': 'large',
            'move_interval': 35,
            'loot_types': {'spices': 0.7, 'gold': 0.3}
        },
        'imperial': {
            'name': 'Imperial Convoy',
            'escorts_range': (25, 40),
            'loot_range': (1000, 2000),
            'size': 'large',
            'move_interval': 30,
            'loot_types': {'gold': 0.5, 'spices': 0.5},
            'rare': True  # Only appears rarely
        },
        'sandworm': {
            'name': 'Sandworm (World Boss)',
            'escorts_range': (100, 150),
            'loot_range': (5000, 10000),
            'size': 'boss',
            'move_interval': 60,  # Very slow movement
            'loot_types': {'gold': 0.4, 'spices': 0.4, 'slaves': 0.2},
            'boss': True,  # Special world boss
            'health': 10000  # Boss health
        }
    }

    def __init__(self, q: int, r: int, caravan_type: str = None):
        """
        Initialize a caravan

        Args:
            q, r: Hex coordinates
            caravan_type: Type of caravan ('salt', 'gold', 'spices', 'imperial')
        """
        self.q = q
        self.r = r

        # Random type if not specified (weighted to avoid rare imperial convoys and sandworm)
        if caravan_type is None:
            weights = [0.4, 0.35, 0.2, 0.049, 0.001]  # salt, gold, spices, imperial, sandworm
            caravan_type = random.choices(self.CARAVAN_TYPES, weights=weights)[0]
        else:
            caravan_type = caravan_type

        self.caravan_type = caravan_type

        # Generate caravan properties based on type
        self._generate_properties()

        # Movement system
        self.movement_path: List[Tuple[int, int]] = []
        self.last_move_time = time.time()
        self.target_q = q
        self.target_r = r
        self.is_scouted = False  # Whether player has scouted this caravan

        # Boss properties
        config = self.TYPE_CONFIGS[self.caravan_type]
        self.is_boss = config.get('boss', False)
        self.max_health = config.get('health', self.escorts * 10)  # Default health based on escorts
        self.current_health = self.max_health
        self.clan_damage = {}  # clan_id -> damage dealt

        # Generate initial movement path
        self._generate_movement_path()

    def _generate_properties(self):
        """Generate caravan properties based on type"""
        config = self.TYPE_CONFIGS[self.caravan_type]

        self.escorts = random.randint(*config['escorts_range'])
        self.loot_value = random.randint(*config['loot_range'])
        self.size = config['size']
        self.move_interval = config['move_interval']
        self.loot_types = config['loot_types']

    def _generate_movement_path(self):
        """Generate a movement path for the caravan"""
        # Simple random wandering for now
        # Could be expanded to follow trade routes, avoid danger, etc.
        self.movement_path = []

        # Generate 5-10 waypoints
        num_waypoints = random.randint(5, 10)
        current_q, current_r = self.q, self.r

        for _ in range(num_waypoints):
            # Move in a random direction
            directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
            dq, dr = random.choice(directions)

            # Move 1-3 hexes in that direction
            distance = random.randint(1, 3)
            current_q += dq * distance
            current_r += dr * distance

            self.movement_path.append((current_q, current_r))

        # Set first waypoint as immediate target
        if self.movement_path:
            self.target_q, self.target_r = self.movement_path[0]

    def update_movement(self, current_time: float):
        """Update caravan position based on time"""
        if current_time - self.last_move_time >= self.move_interval:
            self._move_to_next_waypoint()
            self.last_move_time = current_time

    def _move_to_next_waypoint(self):
        """Move caravan to next waypoint"""
        if not self.movement_path:
            return

        # Move to next waypoint
        next_q, next_r = self.movement_path[0]
        self.q, self.r = next_q, next_r
        self.target_q, self.target_r = self.q, self.r

        # Remove reached waypoint
        self.movement_path.pop(0)

        # If path is empty, generate new path
        if not self.movement_path:
            self._generate_movement_path()

    def get_loot_distribution(self) -> dict:
        """Get the actual loot distribution for this caravan"""
        if not self.is_scouted:
            # Unscouted caravans show estimated loot
            return {'estimated': self.loot_value}

        # Scouted caravans show real distribution
        loot = {}
        remaining_value = self.loot_value

        for loot_type, proportion in self.loot_types.items():
            amount = int(remaining_value * proportion)
            if amount > 0:
                loot[loot_type] = amount
                remaining_value -= amount

        # Add any remainder to primary loot type
        primary_type = max(self.loot_types.keys(), key=lambda k: self.loot_types[k])
        loot[primary_type] += remaining_value

        return loot

    def get_position(self) -> Tuple[int, int]:
        """Get hex coordinates"""
        return (self.q, self.r)

    def get_combat_strength(self) -> int:
        """Calculate combat strength for raiding"""
        # Base strength from escorts
        base_strength = self.escorts * 2

        # Bonus based on caravan type
        type_bonus = {
            'salt': 1,
            'gold': 3,
            'spices': 5,
            'imperial': 8  # Imperial convoys are much stronger
        }

        return base_strength + type_bonus.get(self.caravan_type, 0)

    def get_raid_difficulty(self) -> str:
        """Get difficulty rating for raiding this caravan"""
        strength = self.get_combat_strength()
        if strength < 15:
            return 'easy'
        elif strength < 30:
            return 'medium'
        elif strength < 50:
            return 'hard'
        else:
            return 'legendary'

    def get_description(self) -> str:
        """Get a description of the caravan"""
        config = self.TYPE_CONFIGS[self.caravan_type]

        desc = config['name']

        if self.is_scouted:
            desc += f" with {self.escorts} escorts"
            loot_dist = self.get_loot_distribution()
            loot_desc = []
            for loot_type, amount in loot_dist.items():
                loot_desc.append(f"{amount} {loot_type}")
            desc += f" (carrying {', '.join(loot_desc)})"
        else:
            desc += f" ({self.size} size, estimated value: {self.loot_value})"

        return desc

    def scout_caravan(self):
        """Mark caravan as scouted"""
        self.is_scouted = True

    def __str__(self) -> str:
        return f"Caravan({self.caravan_type}, escorts={self.escorts}, loot={self.loot_value}, scouted={self.is_scouted})"
