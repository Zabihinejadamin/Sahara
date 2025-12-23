"""
Caravan module - Defines caravan entities in the game world
"""
import random
from typing import Tuple


class Caravan:
    """Represents a trade caravan in the desert"""

    CARAVAN_TYPES = ['salt', 'gold', 'spices']

    def __init__(self, q: int, r: int, caravan_type: str = None):
        """
        Initialize a caravan

        Args:
            q, r: Hex coordinates
            caravan_type: Type of caravan ('salt', 'gold', 'spices')
        """
        self.q = q
        self.r = r

        # Random type if not specified
        if caravan_type is None:
            self.caravan_type = random.choice(self.CARAVAN_TYPES)
        else:
            self.caravan_type = caravan_type

        # Generate caravan properties based on type
        self._generate_properties()

    def _generate_properties(self):
        """Generate caravan properties based on type"""
        if self.caravan_type == 'salt':
            self.escorts = random.randint(3, 8)  # Small caravans
            self.loot_value = random.randint(50, 150)
            self.size = 'small'
        elif self.caravan_type == 'gold':
            self.escorts = random.randint(8, 15)  # Medium caravans
            self.loot_value = random.randint(200, 500)
            self.size = 'medium'
        elif self.caravan_type == 'spices':
            self.escorts = random.randint(15, 25)  # Large caravans
            self.loot_value = random.randint(500, 1000)
            self.size = 'large'
        else:
            # Default
            self.escorts = 5
            self.loot_value = 100
            self.size = 'small'

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
            'spices': 5
        }

        return base_strength + type_bonus.get(self.caravan_type, 0)

    def get_raid_difficulty(self) -> str:
        """Get difficulty rating for raiding this caravan"""
        strength = self.get_combat_strength()
        if strength < 10:
            return 'easy'
        elif strength < 20:
            return 'medium'
        else:
            return 'hard'

    def get_description(self) -> str:
        """Get a description of the caravan"""
        type_descriptions = {
            'salt': 'Salt caravan',
            'gold': 'Gold caravan',
            'spices': 'Spice caravan'
        }

        desc = type_descriptions.get(self.caravan_type, 'Unknown caravan')
        desc += f" with {self.escorts} escorts"
        desc += f" (worth {self.loot_value} loot)"

        return desc

    def __str__(self) -> str:
        return f"Caravan({self.caravan_type}, escorts={self.escorts}, loot={self.loot_value})"
