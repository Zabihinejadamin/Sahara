"""
Camp Screen - Player base management with resources and upgrades
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App


class CampScreen(Screen):
    """Screen for managing the player's desert camp"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_data = None
        self.resource_update_event = None

    def on_enter(self):
        """Called when entering camp screen"""
        app = self.get_app()
        self.game_data = app.game_data

        # Start resource generation timer
        if not self.resource_update_event:
            self.resource_update_event = Clock.schedule_interval(self.update_resources, 1.0)

        self.update_display()

    def on_leave(self):
        """Called when leaving camp screen"""
        # Stop resource updates when not on camp screen
        if self.resource_update_event:
            self.resource_update_event.cancel()
            self.resource_update_event = None

    def update_resources(self, dt):
        """Update resource generation over time"""
        if self.game_data:
            self.game_data.generate_resources(dt)
            self.update_display()

    def update_display(self):
        """Update all UI elements with current game state"""
        if not self.game_data:
            return

        # Update resource displays
        resources = self.game_data.resources

        for child in self.walk():
            if hasattr(child, 'id'):
                if child.id == 'water_display':
                    child.text = f"Water: {int(resources.get('water', 0))}"
                elif child.id == 'salt_display':
                    child.text = f"Salt: {int(resources.get('salt', 0))}"
                elif child.id == 'gold_display':
                    child.text = f"Gold: {int(resources.get('gold', 0))}"
                elif child.id == 'spices_display':
                    child.text = f"Spices: {int(resources.get('spices', 0))}"
                elif child.id == 'raiders_display':
                    child.text = f"Available Raiders: {self.game_data.raiders_available}"
                elif child.id == 'water_timer':
                    # Show time until next water generation
                    water_rate = self.game_data.resource_rates.get('water', 1.0)
                    time_remaining = (100 - (self.game_data.resource_timers.get('water', 0) % 100)) / water_rate
                    child.text = f"Next water: {max(0, int(time_remaining))}s"
                elif child.id == 'water_bar':
                    child.value = self.game_data.resource_timers.get('water', 0) % 100

    def upgrade_well(self):
        """Upgrade the water well for better water generation"""
        cost = 50  # Gold cost

        if self.game_data.resources.get('gold', 0) >= cost:
            self.game_data.resources['gold'] -= cost
            self.game_data.resource_rates['water'] += 0.5  # Increase water rate
            self.update_display()

    def recruit_raiders(self):
        """Recruit more raiders"""
        cost = 25  # Gold cost per raider

        if self.game_data.resources.get('gold', 0) >= cost:
            self.game_data.resources['gold'] -= cost
            self.game_data.raiders_available += 1
            self.update_display()

    def upgrade_salt_mine(self):
        """Upgrade salt mining operations"""
        cost = 75  # Gold cost

        if self.game_data.resources.get('gold', 0) >= cost:
            self.game_data.resources['gold'] -= cost
            self.game_data.resource_rates['salt'] += 0.3  # Increase salt rate
            self.update_display()

    def return_to_map(self):
        """Return to the map screen"""
        self.manager.current = 'map'

    def get_app(self):
        """Get the running Kivy app"""
        from kivy.app import App
        return App.get_running_app()
