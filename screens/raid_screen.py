"""
Raid Screen - Auto-resolved battle system for raiding caravans
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.app import App
import random


class RaidScreen(Screen):
    """Screen for raiding caravans with auto-resolved battles"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_caravan = None
        self.selected_raiders = 5  # Default squad size

    def prepare_raid(self, caravan):
        """Prepare raid interface for specific caravan"""
        self.target_caravan = caravan
        self.selected_heroes = []  # Reset hero selection

        # Setup hero selection UI
        self.setup_hero_selection()

        # Update UI elements with caravan info
        self.update_caravan_info()

        # Calculate and display win chance
        self.update_win_chance()

    def update_caravan_info(self):
        """Update UI with caravan details"""
        if not self.target_caravan:
            return

        # Find and update labels (these are defined in KV)
        for child in self.walk():
            if hasattr(child, 'id'):
                if child.id == 'caravan_info':
                    child.text = self.target_caravan.get_description()
                elif child.id == 'caravan_strength':
                    child.text = f"Combat Strength: {self.target_caravan.get_combat_strength()}"
                elif child.id == 'caravan_loot':
                    child.text = f"Potential Loot: {self.target_caravan.loot_value}"

    def update_win_chance(self):
        """Calculate and display win chance"""
        if not self.target_caravan:
            return

        # Simple win chance calculation
        caravan_strength = self.target_caravan.get_combat_strength()
        raider_strength = self.selected_raiders * 3  # Each raider has strength 3

        # Terrain bonus (dunes give advantage to raiders)
        terrain_bonus = 0.1  # Assume dunes terrain

        # Calculate win probability
        strength_ratio = raider_strength / max(caravan_strength, 1)
        win_chance = min(0.95, strength_ratio * (1 + terrain_bonus))

        # Find and update win chance label
        for child in self.walk():
            if hasattr(child, 'id') and child.id == 'win_chance':
                child.text = f"Win Chance: {int(win_chance * 100)}%"

    def on_raider_slider_change(self, value):
        """Handle raider count slider change"""
        self.selected_raiders = int(value)

        # Update raider count display
        for child in self.walk():
            if hasattr(child, 'id') and child.id == 'raider_count':
                child.text = f"Raiders: {self.selected_raiders}"

        # Recalculate win chance
        self.update_win_chance()

    def execute_raid(self):
        """Execute the raid with auto-resolution"""
        if not self.target_caravan:
            return

        app = self.get_app()
        game_data = app.game_data

        # Assign selected heroes to raid
        assigned_heroes = game_data.assign_heroes_to_raid(self.selected_heroes)

        # Haptic feedback for raid start
        self.vibrate_device()

        # Calculate battle results
        caravan_strength = self.target_caravan.get_combat_strength()
        raider_strength = self.selected_raiders * 3

        # Apply hero bonuses
        raid_success_bonus = game_data.get_hero_bonus('raid_success')
        raid_damage_bonus = game_data.get_hero_bonus('raid_damage')

        raider_strength *= (1 + raid_damage_bonus)

        # Terrain bonus for dunes
        terrain_bonus = 0.1
        raider_strength *= (1 + terrain_bonus)

        # Apply success chance modifier
        raider_strength *= (1 + raid_success_bonus)

        # Roll for success
        total_strength = raider_strength + caravan_strength
        win_roll = random.random() * total_strength

        success = win_roll <= raider_strength

        # Calculate casualties and loot
        if success:
            loot_distribution = self.target_caravan.get_loot_distribution()
            loot_gained = loot_distribution
            raiders_lost = random.randint(0, max(1, self.selected_raiders // 3))

            # Add loot to resources
            for resource, amount in loot_gained.items():
                if resource != 'estimated':  # Skip estimated values
                    game_data.resources[resource] += amount

            # Chance to capture slaves
            slave_chance = 0.3
            if random.random() < slave_chance:
                slaves_captured = random.randint(1, 3)
                game_data.resources['slaves'] += slaves_captured
                print(f"Captured {slaves_captured} slaves!")
        else:
            loot_gained = {}
            raiders_lost = random.randint(1, self.selected_raiders)

        game_data.raiders_available = max(0, game_data.raiders_available - raiders_lost)

        # Return heroes from raid
        game_data.return_heroes_from_raid(assigned_heroes)

        # Remove caravan from world
        if self.target_caravan in game_data.visible_caravans:
            game_data.visible_caravans.remove(self.target_caravan)

        # Show results screen
        self.show_raid_results(success, loot_gained, raiders_lost)

    def show_raid_results(self, success: bool, loot: dict, losses: int):
        """Display raid results"""
        result_text = "RAID SUCCESSFUL!\n\n" if success else "RAID FAILED!\n\n"

        if success:
            result_text += "Loot Gained:\n"
            for resource, amount in loot.items():
                if isinstance(amount, int) and amount > 0:
                    result_text += f"  {amount} {resource.capitalize()}\n"
            result_text += f"\nRaiders Lost: {losses}\n\n"
            result_text += "The caravan has been captured!"
        else:
            result_text += f"Raiders Lost: {losses}\n\n"
            result_text += "Your raiders were repelled..."

        # Find results label and update
        for child in self.walk():
            if hasattr(child, 'id') and child.id == 'raid_results':
                child.text = result_text
                child.opacity = 1

        # Show results layout, hide raid prep
        self.show_results_layout()

    def show_results_layout(self):
        """Switch to results display"""
        # This would be handled by KV rules, but for now we'll use opacity
        pass

    def setup_hero_selection(self):
        """Setup hero selection buttons"""
        app = self.get_app()
        heroes = app.game_data.heroes

        # Find the hero grid layout
        hero_grid = None
        for child in self.walk():
            if isinstance(child, GridLayout) and child.cols == 5:
                hero_grid = child
                break

        if hero_grid:
            hero_grid.clear_widgets()

            # Create a button for each hero
            for i, hero in enumerate(heroes):
                hero_button = Button(
                    text=f"{hero.name[:8]}...",  # Truncate long names
                    font_size=dp(12),
                    background_color=(0.4, 0.4, 0.8, 1) if hero.available else (0.6, 0.6, 0.6, 1),
                    disabled=not hero.available
                )
                hero_button.bind(on_press=lambda btn, idx=i: self.toggle_hero_selection(idx))
                hero_grid.add_widget(hero_button)

    def toggle_hero_selection(self, hero_index):
        """Toggle hero selection for raid"""
        app = self.get_app()
        hero = app.game_data.heroes[hero_index]

        if hero_index in self.selected_heroes:
            # Deselect hero
            self.selected_heroes.remove(hero_index)
            print(f"Deselected {hero.name}")
        elif len(self.selected_heroes) < 3 and hero.available:
            # Select hero
            self.selected_heroes.append(hero_index)
            print(f"Selected {hero.name}")
        else:
            print("Cannot select more than 3 heroes or hero is unavailable")

        # Update UI and win chance
        self.update_hero_buttons()
        self.update_win_chance()

    def update_hero_buttons(self):
        """Update hero button appearances based on selection"""
        app = self.get_app()

        # Find hero grid
        hero_grid = None
        for child in self.walk():
            if isinstance(child, GridLayout) and child.cols == 5:
                hero_grid = child
                break

        if hero_grid:
            for i, button in enumerate(hero_grid.children):
                hero_index = len(app.game_data.heroes) - 1 - i  # Reverse order due to kivy layout
                if hero_index < len(app.game_data.heroes):
                    hero = app.game_data.heroes[hero_index]
                    is_selected = hero_index in self.selected_heroes

                    if is_selected:
                        button.background_color = (0.2, 0.8, 0.2, 1)  # Green for selected
                    elif hero.available:
                        button.background_color = (0.4, 0.4, 0.8, 1)  # Blue for available
                    else:
                        button.background_color = (0.6, 0.6, 0.6, 1)  # Gray for unavailable

    def return_to_map(self):
        """Return to map screen"""
        # Return heroes to available pool
        app = self.get_app()
        app.game_data.return_heroes_from_raid([])  # Return any assigned heroes

        self.manager.current = 'map'

        # Reset raid screen state
        self.target_caravan = None
        for child in self.walk():
            if hasattr(child, 'id') and child.id == 'raid_results':
                child.opacity = 0

    def vibrate_device(self):
        """Trigger haptic feedback if available"""
        try:
            from plyer import vibrator
            vibrator.vibrate(0.5)  # Vibrate for 0.5 seconds
        except ImportError:
            # Plyer not available or no vibrator support
            pass
        except Exception:
            # Any other vibration error
            pass

    def get_app(self):
        """Get the running Kivy app"""
        from kivy.app import App
        return App.get_running_app()
