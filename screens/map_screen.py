"""
Map Screen - Displays the procedural hex-grid desert map
Shows player camp, caravans, scouting mechanics
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
import math
import random
import time

from game_data import GameData
from caravan import Caravan
from utils import HexGrid, hex_to_pixel, pixel_to_hex


class HexMapWidget(Widget):
    """Custom widget for rendering the hexagonal map"""

    def __init__(self, game_data: GameData, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        self.hex_grid = HexGrid(radius=dp(20))  # Smaller hexes for 20x20 grid
        self.selected_hex = None
        self.scouting_spies = []  # List of active scouting missions
        self.caravan_update_event = None

        # Start caravan movement updates
        self._start_caravan_updates()

        # Bind to touch events
        self.bind(size=self._update_canvas, pos=self._update_canvas)

    def _start_caravan_updates(self):
        """Start periodic caravan movement updates"""
        if self.caravan_update_event:
            self.caravan_update_event.cancel()
        self.caravan_update_event = Clock.schedule_interval(self._update_caravans, 1.0)  # Update every second

    def _update_caravans(self, dt):
        """Update caravan positions"""
        current_time = time.time()
        for caravan in self.game_data.visible_caravans:
            caravan.update_movement(current_time)
        self._update_canvas()  # Redraw map

    def _update_canvas(self, *args):
        """Redraw the entire map"""
        self.canvas.clear()

        with self.canvas:
            # Draw desert background
            Color(0.9, 0.8, 0.6, 1)  # Sandy color
            Rectangle(pos=self.pos, size=self.size)

            # Draw hex grid
            self._draw_hex_grid()

            # Draw map features (oases, dunes, ruins)
            self._draw_map_features()

            # Draw player camp
            self._draw_player_camp()

            # Draw caravans
            self._draw_caravans()

            # Draw scouting spies
            self._draw_scouting_spies()

            # Draw sandstorm overlay if active
            if self.game_data.sandstorm_active:
                self._draw_sandstorm_overlay()

    def _draw_hex_grid(self):
        """Draw the hexagonal grid"""
        Color(0.8, 0.7, 0.5, 0.2)  # Light desert grid lines

        center_x, center_y = self.center
        grid_radius = 15  # 31x31 hex grid for 20x20 playable area

        for q in range(-grid_radius, grid_radius + 1):
            r1 = max(-grid_radius, -q - grid_radius)
            r2 = min(grid_radius, -q + grid_radius)
            for r in range(r1, r2 + 1):
                hex_center = hex_to_pixel(q, r, self.hex_grid.radius)
                hex_center = (center_x + hex_center[0], center_y + hex_center[1])

                # Draw hex outline
                self._draw_hex_outline(hex_center)

    def _draw_map_features(self):
        """Draw map features like oases, dunes, ruins"""
        center_x, center_y = self.center

        for (q, r), feature_type in self.game_data.map_features.items():
            hex_pos = hex_to_pixel(q, r, self.hex_grid.radius)
            pixel_pos = (center_x + hex_pos[0], center_y + hex_pos[1])

            if feature_type == 'oasis':
                # Blue oasis
                Color(0.3, 0.6, 0.9, 0.8)
                Ellipse(pos=(pixel_pos[0] - dp(12), pixel_pos[1] - dp(12)),
                       size=(dp(24), dp(24)))
            elif feature_type == 'dune':
                # Yellow dune
                Color(0.9, 0.8, 0.4, 0.6)
                Ellipse(pos=(pixel_pos[0] - dp(10), pixel_pos[1] - dp(10)),
                       size=(dp(20), dp(20)))
            elif feature_type == 'ruins':
                # Gray ruins
                Color(0.5, 0.5, 0.5, 0.7)
                # Draw as a small square
                Rectangle(pos=(pixel_pos[0] - dp(8), pixel_pos[1] - dp(8)),
                         size=(dp(16), dp(16)))

    def _draw_hex_outline(self, center):
        """Draw a single hex outline"""
        x, y = center
        radius = self.hex_grid.radius

        # Calculate hex vertices
        vertices = []
        for i in range(6):
            angle = math.pi / 3 * i
            vx = x + radius * math.cos(angle)
            vy = y + radius * math.sin(angle)
            vertices.extend([vx, vy])

        # Draw hex outline
        Line(points=vertices + [vertices[0], vertices[1]], width=1, close=True)

    def _draw_player_camp(self):
        """Draw the player's camp at center"""
        center_x, center_y = self.center

        # Camp base
        Color(0.6, 0.4, 0.2, 1)  # Brown
        Ellipse(pos=(center_x - dp(20), center_y - dp(20)),
               size=(dp(40), dp(40)))

        # Camp marker
        Color(1, 1, 1, 1)  # White
        Ellipse(pos=(center_x - dp(5), center_y - dp(5)),
               size=(dp(10), dp(10)))

    def _draw_caravans(self):
        """Draw visible caravans on the map"""
        center_x, center_y = self.center

        for caravan in self.game_data.visible_caravans:
            hex_pos = hex_to_pixel(caravan.q, caravan.r, self.hex_grid.radius)
            pixel_pos = (center_x + hex_pos[0], center_y + hex_pos[1])

            # Caravan icon based on type
            if caravan.caravan_type == 'salt':
                Color(0.8, 0.8, 0.8, 1)  # Silver
                size = dp(12)
            elif caravan.caravan_type == 'gold':
                Color(1, 0.8, 0, 1)  # Gold
                size = dp(14)
            elif caravan.caravan_type == 'spices':
                Color(0.6, 0.2, 0.8, 1)  # Purple
                size = dp(16)
            elif caravan.caravan_type == 'imperial':
                Color(0.9, 0.1, 0.1, 1)  # Red
                size = dp(18)

            # Draw caravan with size based on type
            Ellipse(pos=(pixel_pos[0] - size/2, pixel_pos[1] - size/2),
                   size=(size, size))

            # If scouted, add a small indicator
            if caravan.is_scouted:
                Color(0, 1, 0, 0.8)  # Green indicator
                Ellipse(pos=(pixel_pos[0] - dp(3), pixel_pos[1] + size/2 - dp(3)),
                       size=(dp(6), dp(6)))

    def _draw_scouting_spies(self):
        """Draw active scouting spies"""
        center_x, center_y = self.center

        for spy in self.scouting_spies:
            hex_pos = hex_to_pixel(spy['q'], spy['r'], self.hex_grid.radius)
            pixel_pos = (center_x + hex_pos[0], center_y + hex_pos[1])

            # Spy icon (small camel)
            Color(0.4, 0.6, 0.8, 1)  # Blue
            Ellipse(pos=(pixel_pos[0] - dp(4), pixel_pos[1] - dp(4)),
                   size=(dp(8), dp(8)))

    def _draw_sandstorm_overlay(self):
        """Draw semi-transparent sandstorm effect"""
        # More intense overlay when sandstorm is active
        Color(0.8, 0.7, 0.5, 0.5)  # Semi-transparent sand color
        Rectangle(pos=self.pos, size=self.size)

        # Add some swirling particles effect (simplified)
        Color(0.9, 0.8, 0.6, 0.3)
        for _ in range(20):
            x = random.uniform(self.pos[0], self.pos[0] + self.size[0])
            y = random.uniform(self.pos[1], self.pos[1] + self.size[1])
            Ellipse(pos=(x - dp(2), y - dp(2)), size=(dp(4), dp(4)))

    def on_touch_down(self, touch):
        """Handle touch/click on map"""
        if not self.collide_point(*touch.pos):
            return False

        # Convert touch position to hex coordinates
        center_x, center_y = self.center
        relative_pos = (touch.pos[0] - center_x, touch.pos[1] - center_y)
        hex_coords = pixel_to_hex(relative_pos[0], relative_pos[1], self.hex_grid.radius)

        # Check if clicking on a caravan
        for caravan in self.game_data.visible_caravans:
            if caravan.q == hex_coords[0] and caravan.r == hex_coords[1]:
                # Start raid preparation
                self._start_raid(caravan)
                return True

        # Otherwise, start scouting mission
        self._start_scouting(hex_coords[0], hex_coords[1])
        return True

    def _start_scouting(self, q: int, r: int):
        """Send a spy to scout the hex"""
        spy = {
            'q': q,
            'r': r,
            'progress': 0,
            'duration': 3.0  # 3 seconds to scout
        }
        self.scouting_spies.append(spy)

        # Schedule spy movement and completion
        Clock.schedule_interval(lambda dt: self._update_scout(spy), 1.0/60.0)

    def _update_scout(self, spy):
        """Update scouting spy movement"""
        spy['progress'] += 1.0/60.0

        if spy['progress'] >= spy['duration']:
            # Scouting complete - reveal caravan if present
            self._complete_scouting(spy)
            return False  # Stop the clock

        # Trigger canvas redraw
        self._update_canvas()
        return True

    def _complete_scouting(self, spy):
        """Complete scouting mission"""
        # Remove spy
        if spy in self.scouting_spies:
            self.scouting_spies.remove(spy)

        # Check if there's already a caravan at this location
        existing_caravan = None
        for caravan in self.game_data.visible_caravans:
            if caravan.q == spy['q'] and caravan.r == spy['r']:
                existing_caravan = caravan
                break

        if existing_caravan:
            # Scout existing caravan
            existing_caravan.scout_caravan()
            print(f"Scouted caravan: {existing_caravan.get_description()}")
        else:
            # Chance to find a new caravan
            if random.random() < 0.4:  # 40% chance to find new caravan
                caravan = Caravan(spy['q'], spy['r'])
                self.game_data.visible_caravans.append(caravan)
                print(f"Found new caravan: {caravan.get_description()}")

        # Mark hex as explored
        self.game_data.explored_hexes.add((spy['q'], spy['r']))

        self._update_canvas()

    def _start_raid(self, caravan: Caravan):
        """Initiate raid on selected caravan"""
        # Switch to raid screen with selected caravan
        app = App.get_running_app()
        raid_screen = app.root.get_screen('raid')
        raid_screen.prepare_raid(caravan)
        app.root.current = 'raid'


class MapScreen(Screen):
    """Main map screen showing the desert world"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_data = None
        self.hex_map = None

    def on_enter(self):
        """Called when entering the map screen"""
        if not self.game_data:
            app = App.get_running_app()
            self.game_data = app.game_data

        if not self.hex_map:
            self.hex_map = HexMapWidget(self.game_data)
            self.add_widget(self.hex_map)

        # Update map display
        self.hex_map._update_canvas()

    def on_leave(self):
        """Called when leaving the map screen"""
        pass
