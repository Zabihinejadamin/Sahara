"""
Game Data module - Manages global game state, resources, save/load
"""
import json
import os
import random
import time
from typing import Dict, List, Any, Tuple, Optional
from caravan import Caravan


class Hero:
    """Represents a hero with abilities and stats"""

    def __init__(self, name: str, portrait: str, description: str, bonuses: Dict[str, float]):
        self.name = name
        self.portrait = portrait
        self.description = description
        self.bonuses = bonuses  # Dict of stat bonuses (e.g., {'raid_success': 0.2})
        self.level = 1
        self.available = True  # Can be assigned to raids

    def get_raid_bonus(self) -> Dict[str, float]:
        """Get bonuses that apply to raids"""
        return {k: v for k, v in self.bonuses.items() if k.startswith('raid_')}


class Building:
    """Represents a building in the camp"""

    BUILDING_TYPES = {
        'tent': {
            'name': 'Tent',
            'description': 'Housing for raiders',
            'max_level': 3,
            'base_cost': {'gold': 20},
            'effects': {'housing': 5}  # +5 raider capacity per level
        },
        'well': {
            'name': 'Well',
            'description': 'Water production',
            'max_level': 3,
            'base_cost': {'gold': 30},
            'effects': {'water_rate': 0.5}  # +0.5 water per second per level
        },
        'stable': {
            'name': 'Camel Stable',
            'description': 'Auto-raids for small loot',
            'max_level': 3,
            'base_cost': {'gold': 50, 'salt': 10},
            'effects': {'auto_gold': 1, 'auto_salt': 0.5}  # Idle gold/salt generation
        },
        'watchtower': {
            'name': 'Watchtower',
            'description': 'Reduces counter-raid chance',
            'max_level': 3,
            'base_cost': {'gold': 40, 'spices': 5},
            'effects': {'defense': 0.2}  # -20% counter-raid chance per level
        },
        'slave_pen': {
            'name': 'Slave Pen',
            'description': 'Convert slaves to recruits',
            'max_level': 3,
            'base_cost': {'gold': 35},
            'effects': {'recruitment': 0.3}  # +30% slave-to-raider conversion per level
        }
    }

    def __init__(self, building_type: str, level: int = 1):
        self.building_type = building_type
        self.level = level
        self.upgrade_cost = self.calculate_upgrade_cost()

    def calculate_upgrade_cost(self) -> Dict[str, int]:
        """Calculate cost to upgrade this building"""
        base_cost = self.BUILDING_TYPES[self.building_type]['base_cost']
        multiplier = 1.5 ** (self.level - 1)  # Exponential scaling
        return {resource: int(amount * multiplier) for resource, amount in base_cost.items()}

    def get_effects(self) -> Dict[str, float]:
        """Get current effects of this building"""
        base_effects = self.BUILDING_TYPES[self.building_type]['effects']
        return {effect: value * self.level for effect, value in base_effects.items()}


class TechTree:
    """Manages the technology research tree"""

    TECH_BRANCHES = {
        'weapons': {
            'name': 'Weapons',
            'tiers': {
                1: {'name': 'Spears', 'cost': {'gold': 100}, 'description': '+10% raid damage'},
                2: {'name': 'Swords', 'cost': {'gold': 250, 'spices': 50}, 'description': '+25% raid damage'},
                3: {'name': 'Firearms', 'cost': {'gold': 500, 'spices': 150}, 'description': '+40% raid damage'}
            }
        },
        'camels': {
            'name': 'Camels',
            'tiers': {
                1: {'name': 'Riding', 'cost': {'gold': 80}, 'description': '+20% scouting speed'},
                2: {'name': 'War Camels', 'cost': {'gold': 200, 'salt': 100}, 'description': '+30% raiding mobility'},
                3: {'name': 'Armored Camels', 'cost': {'gold': 400, 'spices': 100}, 'description': '+50% raiding mobility'}
            }
        },
        'fortifications': {
            'name': 'Fortifications',
            'tiers': {
                1: {'name': 'Walls', 'cost': {'gold': 120}, 'description': '+15% camp defense'},
                2: {'name': 'Towers', 'cost': {'gold': 300, 'salt': 50}, 'description': '+30% camp defense'},
                3: {'name': 'Fortress', 'cost': {'gold': 600, 'spices': 200}, 'description': '+50% camp defense'}
            }
        }
    }

    def __init__(self):
        self.unlocked_techs: Dict[str, int] = {}  # branch -> tier

    def can_research(self, branch: str, tier: int) -> bool:
        """Check if a tech can be researched"""
        return self.unlocked_techs.get(branch, 0) >= tier - 1

    def research_tech(self, branch: str, tier: int) -> Dict[str, int]:
        """Get cost to research a tech"""
        return self.TECH_BRANCHES[branch]['tiers'][tier]['cost']


class GameData:
    """Central game state management class"""

    SAVE_FILE = "sahara_save.json"

    def __init__(self):
        """Initialize game data with default values"""
        # Resources
        self.resources = {
            'water': 100,
            'salt': 50,
            'gold': 25,
            'spices': 0,
            'slaves': 0  # New slave resource
        }

        self.resource_rates = {
            'water': 1.0,
            'salt': 0.5,
            'gold': 0.1,
            'spices': 0.05,
            'slaves': 0.0  # Slaves don't generate automatically
        }

        self.resource_timers = {
            'water': 0.0,
            'salt': 0.0,
            'gold': 0.0,
            'spices': 0.0,
            'slaves': 0.0
        }

        # Military
        self.raiders_available = 10
        self.max_raiders = 50

        # Heroes system
        self.heroes = self._create_heroes()

        # Building system (8x8 camp grid)
        self.camp_buildings: Dict[Tuple[int, int], Building] = {}  # (x, y) -> Building

        # Tech tree
        self.tech_tree = TechTree()

        # World state
        self.visible_caravans: List[Caravan] = []
        self.explored_hexes: set = set()

        # Map features (oases, dunes, ruins)
        self.map_features: Dict[Tuple[int, int], str] = {}  # (q, r) -> feature_type

        # Player camp location (center of map)
        self.camp_q = 0
        self.camp_r = 0

        # Water consumption (based on population)
        self.last_water_update = time.time()
        self.water_consumption_rate = 0.1  # Water per second per person

        # Sandstorm system
        self.sandstorm_active = False
        self.last_sandstorm_check = time.time()
        self.sandstorm_duration = 0

        # Initialize world if not loading from save
        if not os.path.exists(self.SAVE_FILE):
            self.initialize_world()

        # Load saved game if exists
        self.load_game()

    def _create_heroes(self) -> List[Hero]:
        """Create the starting heroes"""
        return [
            Hero(
                name="The Veil",
                portrait="hero_portrait_1.png",
                description="Stealth assassin: +20% ambush success",
                bonuses={'raid_success': 0.2}
            ),
            Hero(
                name="Iron Camel",
                portrait="hero_portrait_2.png",
                description="Tank: reduces losses on defense",
                bonuses={'raid_defense': 0.3}
            ),
            Hero(
                name="Sand Viper",
                portrait="hero_portrait_3.png",
                description="Archer: +damage in raids",
                bonuses={'raid_damage': 0.25}
            ),
            Hero(
                name="Oasis Scout",
                portrait="hero_portrait_4.png",
                description="Faster scouting missions",
                bonuses={'scouting_speed': 0.4}
            ),
            Hero(
                name="Slave Driver",
                portrait="hero_portrait_5.png",
                description="More recruits from slaves",
                bonuses={'recruitment_efficiency': 0.3}
            )
        ]

    def initialize_world(self):
        """Initialize the game world with procedural features and caravans"""
        from utils import ProceduralGenerator

        # Generate map features
        self.map_features = ProceduralGenerator.generate_desert_features(radius=15)

        # Generate starting caravans
        caravan_positions = ProceduralGenerator.generate_starting_caravans(radius=15)

        # Create caravan objects
        from caravan import Caravan
        for q, r, caravan_type in caravan_positions:
            caravan = Caravan(q, r, caravan_type)
            self.visible_caravans.append(caravan)

        print(f"Initialized world with {len(self.map_features)} features and {len(self.visible_caravans)} caravans")

    def update(self, dt: float):
        """Update game state each frame"""
        current_time = time.time()

        # Generate resources over time
        self.generate_resources(dt)

        # Update water consumption based on population
        self.update_water_consumption(dt)

        # Update sandstorm system
        self.update_sandstorm(current_time)

        # Update idle building production
        self.update_building_production(dt)

    def generate_resources(self, dt: float):
        """Generate resources based on rates and time"""
        for resource, rate in self.resource_rates.items():
            self.resource_timers[resource] += rate * dt

            # Generate resource when timer reaches threshold
            if self.resource_timers[resource] >= 100:  # 100 units = 1 resource
                self.resource_timers[resource] -= 100
                self.resources[resource] += 1

    def update_water_consumption(self, dt: float):
        """Update water consumption based on population"""
        # Calculate population (raiders + slaves)
        population = self.raiders_available + self.resources.get('slaves', 0)

        # Consume water based on population
        water_consumption = population * self.water_consumption_rate * dt
        self.resources['water'] = max(0, self.resources['water'] - water_consumption)

        # Game over if water reaches 0 (for now, just heavy penalty)
        if self.resources['water'] <= 0:
            # Reduce raider efficiency, increased desertion chance
            self.raiders_available = max(1, self.raiders_available - 1)  # Lose 1 raider per update when dehydrated

    def update_sandstorm(self, current_time: float):
        """Update sandstorm system"""
        # Check for sandstorm every 5-15 minutes
        time_since_last_check = current_time - self.last_sandstorm_check

        if time_since_last_check > random.uniform(300, 900):  # 5-15 minutes
            self.last_sandstorm_check = current_time

            # 20% chance of sandstorm
            if random.random() < 0.2:
                self.start_sandstorm()

        # Update active sandstorm
        if self.sandstorm_active:
            self.sandstorm_duration -= (current_time - self.last_water_update)

            if self.sandstorm_duration <= 0:
                self.end_sandstorm()

        self.last_water_update = current_time

    def start_sandstorm(self):
        """Start a sandstorm event"""
        self.sandstorm_active = True
        self.sandstorm_duration = random.uniform(30, 120)  # 30 seconds to 2 minutes

        # Sandstorm effects: damage buildings if not fortified
        defense_bonus = self.get_total_building_effect('defense')
        damage_chance = max(0.1, 0.3 - defense_bonus)  # 30% base chance, reduced by fortifications

        damaged_buildings = []
        for pos, building in self.camp_buildings.items():
            if random.random() < damage_chance:
                # Reduce building level (can't go below 1)
                if building.level > 1:
                    building.level -= 1
                    damaged_buildings.append(building.BUILDING_TYPES[building.building_type]['name'])

        if damaged_buildings:
            print(f"Sandstorm damaged: {', '.join(damaged_buildings)}")

    def end_sandstorm(self):
        """End the current sandstorm"""
        self.sandstorm_active = False
        self.sandstorm_duration = 0

    def update_building_production(self, dt: float):
        """Update idle production from buildings"""
        # Auto-gold from stables
        auto_gold = self.get_total_building_effect('auto_gold')
        if auto_gold > 0:
            self.resource_timers['gold'] += auto_gold * dt

        # Auto-salt from stables
        auto_salt = self.get_total_building_effect('auto_salt')
        if auto_salt > 0:
            self.resource_timers['salt'] += auto_salt * dt

    def get_total_building_effect(self, effect_type: str) -> float:
        """Get total effect from all buildings of a certain type"""
        total = 0.0
        for building in self.camp_buildings.values():
            effects = building.get_effects()
            total += effects.get(effect_type, 0)
        return total

    def place_building(self, x: int, y: int, building_type: str) -> bool:
        """Place a new building at camp coordinates"""
        pos = (x, y)

        # Check if position is valid and empty
        if pos in self.camp_buildings:
            return False

        # Check bounds (8x8 grid)
        if not (0 <= x < 8 and 0 <= y < 8):
            return False

        # Create building
        building = Building(building_type)
        self.camp_buildings[pos] = building

        # Update derived stats
        self.update_derived_stats()
        return True

    def upgrade_building(self, x: int, y: int) -> bool:
        """Upgrade building at camp coordinates"""
        pos = (x, y)

        if pos not in self.camp_buildings:
            return False

        building = self.camp_buildings[pos]
        if building.level >= building.BUILDING_TYPES[building.building_type]['max_level']:
            return False

        # Check if can afford upgrade
        if not self.can_afford(building.upgrade_cost):
            return False

        # Spend resources
        self.spend_resources(building.upgrade_cost)

        # Upgrade building
        building.level += 1
        building.upgrade_cost = building.calculate_upgrade_cost()

        # Update derived stats
        self.update_derived_stats()
        return True

    def update_derived_stats(self):
        """Update derived stats based on buildings"""
        # Update max raiders from housing
        housing_bonus = int(self.get_total_building_effect('housing'))
        self.max_raiders = 50 + housing_bonus

        # Update water production rate
        water_bonus = self.get_total_building_effect('water_rate')
        self.resource_rates['water'] = 1.0 + water_bonus

    def recruit_from_slaves(self, num_slaves: int) -> int:
        """Convert slaves to raiders"""
        available_slaves = self.resources.get('slaves', 0)
        if available_slaves < num_slaves:
            num_slaves = available_slaves

        if num_slaves <= 0:
            return 0

        # Recruitment efficiency bonus from slave driver hero and buildings
        efficiency = 0.5  # Base 50% conversion rate
        efficiency += self.get_hero_bonus('recruitment_efficiency')
        efficiency += self.get_total_building_effect('recruitment')

        # Calculate how many raiders we get
        raiders_gained = int(num_slaves * efficiency)

        # Cap at available housing
        available_housing = self.max_raiders - self.raiders_available
        raiders_gained = min(raiders_gained, available_housing)

        if raiders_gained > 0:
            self.resources['slaves'] -= num_slaves
            self.raiders_available += raiders_gained

        return raiders_gained

    def get_hero_bonus(self, bonus_type: str) -> float:
        """Get total bonus from all heroes for a specific type"""
        total_bonus = 0.0
        for hero in self.heroes:
            if hero.available:  # Only count available heroes
                total_bonus += hero.bonuses.get(bonus_type, 0)
        return total_bonus

    def assign_heroes_to_raid(self, hero_indices: List[int]) -> List[Hero]:
        """Assign heroes to a raid (makes them unavailable)"""
        assigned_heroes = []
        for idx in hero_indices:
            if 0 <= idx < len(self.heroes) and self.heroes[idx].available:
                hero = self.heroes[idx]
                hero.available = False
                assigned_heroes.append(hero)
        return assigned_heroes

    def return_heroes_from_raid(self, heroes: List[Hero]):
        """Return heroes from raid (makes them available again)"""
        for hero in heroes:
            hero.available = True

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
            'resource_timers': self.resource_timers,
            'raiders_available': self.raiders_available,
            'max_raiders': self.max_raiders,

            # Heroes
            'heroes': [
                {
                    'name': h.name,
                    'level': h.level,
                    'available': h.available
                }
                for h in self.heroes
            ],

            # Buildings
            'camp_buildings': {
                f"{x},{y}": {
                    'type': b.building_type,
                    'level': b.level
                }
                for (x, y), b in self.camp_buildings.items()
            },

            # Tech tree
            'tech_unlocked': self.tech_tree.unlocked_techs,

            # World state
            'camp_location': {'q': self.camp_q, 'r': self.camp_r},
            'map_features': {f"{q},{r}": feature for (q, r), feature in self.map_features.items()},
            'visible_caravans': [
                {
                    'q': c.q,
                    'r': c.r,
                    'type': c.caravan_type,
                    'escorts': c.escorts,
                    'loot_value': c.loot_value,
                    'movement_path': c.movement_path,
                    'last_move_time': c.last_move_time
                }
                for c in self.visible_caravans
            ],
            'explored_hexes': list(self.explored_hexes),

            # Game state
            'last_water_update': self.last_water_update,
            'last_sandstorm_check': self.last_sandstorm_check,
            'sandstorm_active': self.sandstorm_active,
            'sandstorm_duration': self.sandstorm_duration
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

            # Load basic resources and stats
            self.resources = save_data.get('resources', self.resources)
            self.resource_rates = save_data.get('resource_rates', self.resource_rates)
            self.resource_timers = save_data.get('resource_timers', self.resource_timers)
            self.raiders_available = save_data.get('raiders_available', self.raiders_available)
            self.max_raiders = save_data.get('max_raiders', self.max_raiders)

            # Load heroes
            if 'heroes' in save_data:
                for i, hero_data in enumerate(save_data['heroes']):
                    if i < len(self.heroes):
                        self.heroes[i].level = hero_data.get('level', 1)
                        self.heroes[i].available = hero_data.get('available', True)

            # Load buildings
            self.camp_buildings = {}
            if 'camp_buildings' in save_data:
                for pos_str, building_data in save_data['camp_buildings'].items():
                    x, y = map(int, pos_str.split(','))
                    building = Building(building_data['type'], building_data['level'])
                    self.camp_buildings[(x, y)] = building

            # Load tech tree
            if 'tech_unlocked' in save_data:
                self.tech_tree.unlocked_techs = save_data['tech_unlocked']

            # Load camp location
            camp_loc = save_data.get('camp_location', {'q': 0, 'r': 0})
            self.camp_q = camp_loc['q']
            self.camp_r = camp_loc['r']

            # Load map features
            self.map_features = {}
            if 'map_features' in save_data:
                for pos_str, feature in save_data['map_features'].items():
                    q, r = map(int, pos_str.split(','))
                    self.map_features[(q, r)] = feature

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
                caravan.movement_path = caravan_data.get('movement_path', [])
                caravan.last_move_time = caravan_data.get('last_move_time', time.time())
                self.visible_caravans.append(caravan)

            self.explored_hexes = set(save_data.get('explored_hexes', []))

            # Load game state
            self.last_water_update = save_data.get('last_water_update', time.time())
            self.last_sandstorm_check = save_data.get('last_sandstorm_check', time.time())
            self.sandstorm_active = save_data.get('sandstorm_active', False)
            self.sandstorm_duration = save_data.get('sandstorm_duration', 0)

            # Update derived stats
            self.update_derived_stats()

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
