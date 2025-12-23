"""
Sahara Raiders - A 2D top-down 4X survival strategy game
Main entry point with Kivy App and ScreenManager
"""
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.config import Config
from kivy.clock import Clock
from kivy.core.window import Window

# Set minimum Kivy version
kivy.require('2.1.0')

# Configure window for desktop testing (remove for mobile)
Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '960')
Config.set('graphics', 'resizable', True)

# Set consistent desert background color
Window.clearcolor = (0.95, 0.85, 0.6, 1)  # Light sandy desert color

# Import our custom screens
from screens.map_screen import MapScreen
from screens.camp_screen import CampScreen
from screens.raid_screen import RaidScreen
from screens.tech_screen import TechScreen
from screens.clan_screen import ClanScreen
from screens.shop_screen import ShopScreen

# Import Firebase and monetization
from firebase_config import initialize_firebase
from monetization import monetization_manager


class SaharaRaidersApp(App):
    """Main Kivy application class for Sahara Raiders"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Sahara Raiders'
        self.icon = 'assets/icon.png'  # Will be added later

        # Initialize Firebase
        initialize_firebase()

        # Game state will be managed by GameData class
        self.game_data = None

    def build(self):
        """Build the main screen manager with all game screens"""
        # Initialize game data
        from game_data import GameData
        self.game_data = GameData()

        # Create screen manager with fade transitions
        sm = ScreenManager(transition=FadeTransition())

        # Add all game screens
        sm.add_widget(MapScreen(name='map'))
        sm.add_widget(CampScreen(name='camp'))
        sm.add_widget(RaidScreen(name='raid'))
        sm.add_widget(TechScreen(name='tech'))
        sm.add_widget(ClanScreen(name='clan'))
        sm.add_widget(ShopScreen(name='shop'))

        # Start on map screen
        sm.current = 'map'

        # Schedule game updates (60 FPS)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

        return sm

    def update(self, dt: float):
        """Main game update loop called at 60 FPS"""
        # Update game data (timers, resources, etc.)
        if self.game_data:
            self.game_data.update(dt)

    def on_pause(self):
        """Handle app pause (mobile)"""
        # Auto-save game state
        if self.game_data:
            self.game_data.save_game()
        return True

    def on_resume(self):
        """Handle app resume (mobile)"""
        pass

    def on_stop(self):
        """Handle app stop"""
        # Save game before exit
        if self.game_data:
            self.game_data.save_game()


if __name__ == '__main__':
    SaharaRaidersApp().run()