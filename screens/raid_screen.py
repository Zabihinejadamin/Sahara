"""
Raid Screen - Auto-resolved battle system for raiding caravans
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
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

        # Calculate battle results
        caravan_strength = self.target_caravan.get_combat_strength()
        raider_strength = self.selected_raiders * 3

        # Terrain bonus for dunes
        terrain_bonus = 0.1
        raider_strength *= (1 + terrain_bonus)

        # Roll for success
        total_strength = raider_strength + caravan_strength
        win_roll = random.random() * total_strength

        success = win_roll <= raider_strength

        # Calculate casualties and loot
        if success:
            loot_gained = self.target_caravan.loot_value
            raiders_lost = random.randint(0, max(1, self.selected_raiders // 3))
        else:
            loot_gained = 0
            raiders_lost = random.randint(1, self.selected_raiders)

        # Update game data
        app = self.get_app()
        if success:
            app.game_data.resources['gold'] += loot_gained
            app.game_data.resources['salt'] += loot_gained // 2  # Some salt too
        app.game_data.raiders_available = max(0, app.game_data.raiders_available - raiders_lost)

        # Remove caravan from world
        if self.target_caravan in app.game_data.visible_caravans:
            app.game_data.visible_caravans.remove(self.target_caravan)

        # Show results screen
        self.show_raid_results(success, loot_gained, raiders_lost)

    def show_raid_results(self, success: bool, loot: int, losses: int):
        """Display raid results"""
        result_text = "RAID SUCCESSFUL!\n\n" if success else "RAID FAILED!\n\n"
        result_text += f"Loot Gained: {loot}\n"
        result_text += f"Raiders Lost: {losses}\n\n"

        if success:
            result_text += "The caravan has been captured!"
        else:
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

    def return_to_map(self):
        """Return to map screen"""
        self.manager.current = 'map'

        # Reset raid screen state
        self.target_caravan = None
        for child in self.walk():
            if hasattr(child, 'id') and child.id == 'raid_results':
                child.opacity = 0

    def get_app(self):
        """Get the running Kivy app"""
        from kivy.app import App
        return App.get_running_app()
