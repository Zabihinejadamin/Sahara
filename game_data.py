"""
Game Data module - Manages global game state, resources, save/load
"""
import json
import os
from typing import Dict, List, Any
from caravan import Caravan


class GameData:
    """Central game state management class"""

    SAVE_FILE = "sahara_save.json"

    def __init__(self):
        """Initialize game data with default values"""
        self.resources = {
            'water': 100,
            'salt': 50,
            'gold': 25,
            'spices': 0
        }

        self.resource_rates = {
            'water': 1.0,  # Units per second
            'salt': 0.5,
            'gold': 0.1,
            'spices': 0.05
        }

        self.resource_timers = {
            'water': 0.0,
            'salt': 0.0,
            'gold': 0.0,
            'spices': 0.0
        }

        # Military
        self.raiders_available = 10
        self.max_raiders = 50

        # World state
        self.visible_caravans: List[Caravan] = []
        self.explored_hexes = set()

        # Player camp location (center of map)
        self.camp_q = 0
        self.camp_r = 0

        # Tech tree/progress (stub for future expansion)
        self.tech_unlocked = set()

        # Load saved game if exists
        self.load_game()

    def update(self, dt: float):
        """Update game state each frame"""
        # Generate resources over time
        self.generate_resources(dt)

        # Update caravan positions (future expansion)
        # self.update_caravans(dt)

    def generate_resources(self, dt: float):
        """Generate resources based on rates and time"""
        for resource, rate in self.resource_rates.items():
            self.resource_timers[resource] += rate * dt

            # Generate resource when timer reaches threshold
            if self.resource_timers[resource] >= 100:  # 100 units = 1 resource
                self.resource_timers[resource] -= 100
                self.resources[resource] += 1

    def can_afford(self, cost: Dict[str, int]) -> bool:
        """Check if player can afford a cost"""
        for resource, amount in cost.items():
            if self.resources.get(resource, 0) < amount:
                return False
        return True

    def spend_resources(self, cost: Dict[str, int]) -> bool:
        """Spend resources if affordable"""
        if not self.can_afford(cost):
            return False

        for resource, amount in cost.items():
            self.resources[resource] -= amount
        return True

    def add_caravan(self, caravan: Caravan):
        """Add a caravan to the visible list"""
        self.visible_caravans.append(caravan)

    def remove_caravan(self, caravan: Caravan):
        """Remove a caravan from the visible list"""
        if caravan in self.visible_caravans:
            self.visible_caravans.remove(caravan)

    def save_game(self):
        """Save game state to JSON file"""
        save_data = {
            'resources': self.resources,
            'resource_rates': self.resource_rates,
            'raiders_available': self.raiders_available,
            'camp_location': {'q': self.camp_q, 'r': self.camp_r},
            'tech_unlocked': list(self.tech_unlocked),
            'visible_caravans': [
                {
                    'q': c.q,
                    'r': c.r,
                    'type': c.caravan_type,
                    'escorts': c.escorts,
                    'loot_value': c.loot_value
                }
                for c in self.visible_caravans
            ],
            'explored_hexes': list(self.explored_hexes)
        }

        try:
            with open(self.SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"Game saved to {self.SAVE_FILE}")
        except Exception as e:
            print(f"Failed to save game: {e}")

    def load_game(self):
        """Load game state from JSON file"""
        if not os.path.exists(self.SAVE_FILE):
            print("No save file found, starting new game")
            return

        try:
            with open(self.SAVE_FILE, 'r') as f:
                save_data = json.load(f)

            # Load basic resources and rates
            self.resources = save_data.get('resources', self.resources)
            self.resource_rates = save_data.get('resource_rates', self.resource_rates)
            self.raiders_available = save_data.get('raiders_available', self.raiders_available)

            # Load camp location
            camp_loc = save_data.get('camp_location', {'q': 0, 'r': 0})
            self.camp_q = camp_loc['q']
            self.camp_r = camp_loc['r']

            # Load tech and exploration
            self.tech_unlocked = set(save_data.get('tech_unlocked', []))

            # Load visible caravans
            self.visible_caravans = []
            for caravan_data in save_data.get('visible_caravans', []):
                caravan = Caravan(
                    caravan_data['q'],
                    caravan_data['r'],
                    caravan_data['type']
                )
                # Override generated properties with saved ones
                caravan.escorts = caravan_data['escorts']
                caravan.loot_value = caravan_data['loot_value']
                self.visible_caravans.append(caravan)

            self.explored_hexes = set(save_data.get('explored_hexes', []))

            print(f"Game loaded from {self.SAVE_FILE}")

        except Exception as e:
            print(f"Failed to load game: {e}")
            print("Starting with default values")

    def reset_game(self):
        """Reset game to initial state"""
        if os.path.exists(self.SAVE_FILE):
            os.remove(self.SAVE_FILE)

        # Reinitialize
        self.__init__()

    def get_game_stats(self) -> Dict[str, Any]:
        """Get current game statistics"""
        return {
            'total_resources': sum(self.resources.values()),
            'active_caravans': len(self.visible_caravans),
            'explored_area': len(self.explored_hexes),
            'military_strength': self.raiders_available * 3,  # Rough estimate
            'resource_generation_rate': sum(self.resource_rates.values())
        }
