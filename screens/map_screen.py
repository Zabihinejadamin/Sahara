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

from game_data import GameData
from caravan import Caravan
from utils import HexGrid, hex_to_pixel, pixel_to_hex


class HexMapWidget(Widget):
    """Custom widget for rendering the hexagonal map"""

    def __init__(self, game_data: GameData, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        self.hex_grid = HexGrid(radius=dp(30))  # Hex size for mobile
        self.selected_hex = None
        self.scouting_spies = []  # List of active scouting missions

        # Bind to touch events
        self.bind(size=self._update_canvas, pos=self._update_canvas)

    def _update_canvas(self, *args):
        """Redraw the entire map"""
        self.canvas.clear()

        with self.canvas:
            # Draw desert background
            Color(0.9, 0.8, 0.6, 1)  # Sandy color
            Rectangle(pos=self.pos, size=self.size)

            # Draw hex grid
            self._draw_hex_grid()

            # Draw player camp
            self._draw_player_camp()

            # Draw caravans
            self._draw_caravans()

            # Draw scouting spies
            self._draw_scouting_spies()

            # Draw sandstorm overlay (random)
            if random.random() < 0.1:  # 10% chance
                self._draw_sandstorm_overlay()

    def _draw_hex_grid(self):
        """Draw the hexagonal grid"""
        Color(0.8, 0.7, 0.5, 0.3)  # Light desert grid lines

        center_x, center_y = self.center
        grid_radius = 8  # 17x17 hex grid

        for q in range(-grid_radius, grid_radius + 1):
            r1 = max(-grid_radius, -q - grid_radius)
            r2 = min(grid_radius, -q + grid_radius)
            for r in range(r1, r2 + 1):
                hex_center = hex_to_pixel(q, r, self.hex_grid.radius)
                hex_center = (center_x + hex_center[0], center_y + hex_center[1])

                # Draw hex outline
                self._draw_hex_outline(hex_center)

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

            # Caravan icon (circle with type color)
            if caravan.caravan_type == 'gold':
                Color(1, 0.8, 0, 1)  # Gold
            else:  # salt
                Color(0.8, 0.8, 0.8, 1)  # Silver

            Ellipse(pos=(pixel_pos[0] - dp(8), pixel_pos[1] - dp(8)),
                   size=(dp(16), dp(16)))

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
        Color(0.8, 0.7, 0.5, 0.3)  # Semi-transparent sand color
        Rectangle(pos=self.pos, size=self.size)

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

        # Chance to find a caravan
        if random.random() < 0.3:  # 30% chance
            caravan_type = 'gold' if random.random() < 0.5 else 'salt'
            caravan = Caravan(spy['q'], spy['r'], caravan_type)
            self.game_data.visible_caravans.append(caravan)

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
