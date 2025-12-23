"""
Map Screen - Displays the procedural hex-grid desert map
Shows player camp, caravans, scouting mechanics
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
import math
import random
import time
import os

from game_data import GameData
from caravan import Caravan
from utils import HexGrid, hex_to_pixel, pixel_to_hex


class MapIcon(Widget):
    """A map icon that can be touched"""
    def __init__(self, icon_type, data=None, **kwargs):
        super().__init__(**kwargs)
        self.icon_type = icon_type
        self.data = data
        self.size_hint = (None, None)
        self.bind(on_touch_down=self.on_icon_touch)

    def on_icon_touch(self, touch):
        """Handle touch on this icon"""
        if self.collide_point(*touch.pos):
            # Find the map screen and handle the touch
            parent = self.parent
            while parent and not isinstance(parent, MapScreen):
                parent = parent.parent
            if parent:
                parent.handle_icon_touch(self.icon_type, self.data)
            return True
        return False


class HexMapWidget(FloatLayout):
    """Widget for rendering the hexagonal map with proper Kivy widgets"""

    def __init__(self, game_data: GameData, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        self.hex_grid = HexGrid(radius=dp(20))  # Smaller hexes for 20x20 grid
        self.map_icons = {}  # Store references to map icons
        self.caravan_update_event = None

        # Add background
        self._add_background()

        # Start caravan movement updates
        self._start_caravan_updates()

    def _add_background(self):
        """Add desert background"""
        # Try to use background image if it exists
        bg_path = 'assets/desert_background.png'
        if os.path.exists(bg_path):
            bg = Image(source=bg_path, allow_stretch=True, keep_ratio=False)
        else:
            # Fallback to colored rectangle
            bg = Widget()
            with bg.canvas.before:
                Color(0.95, 0.85, 0.6, 1)  # Light sandy color
                Rectangle(pos=bg.pos, size=bg.size)
            bg.bind(pos=lambda obj, value: setattr(bg, 'size', bg.size))
            bg.bind(size=lambda obj, value: bg.canvas.ask_update())

        bg.size_hint = (1, 1)
        self.add_widget(bg)

    def _start_caravan_updates(self):
        """Start periodic caravan movement updates"""
        if self.caravan_update_event:
            self.caravan_update_event.cancel()
        self.caravan_update_event = Clock.schedule_interval(self._update_caravans, 1.0)

    def _update_caravans(self, dt):
        """Update caravan positions"""
        current_time = time.time()
        for caravan in self.game_data.visible_caravans:
            caravan.update_movement(current_time)
        self.update_map_display()

    def update_map_display(self):
        """Update all map elements"""
        # Clear existing icons
        icons_to_remove = []
        for child in self.children:
            if isinstance(child, MapIcon):
                icons_to_remove.append(child)

        for icon in icons_to_remove:
            self.remove_widget(icon)

        self.map_icons.clear()

        # Add hex grid (canvas drawing for performance)
        self._draw_hex_grid()

        # Add map features
        self._add_map_features()

        # Add player camp
        self._add_player_camp()

        # Add caravans
        self._add_caravans()

        # Add scouting spies
        self._add_scouting_spies()

    def _draw_hex_grid(self):
        """Draw the hexagonal grid on canvas"""
        with self.canvas.after:
            self.canvas.after.clear()
            Color(0.8, 0.7, 0.5, 0.3)  # Light desert grid lines

            center_x, center_y = self.center_x, self.center_y
            grid_radius = 15  # 31x31 hex grid for 20x20 playable area

            for q in range(-grid_radius, grid_radius + 1):
                r1 = max(-grid_radius, -q - grid_radius)
                r2 = min(grid_radius, -q + grid_radius)
                for r in range(r1, r2 + 1):
                    hex_center = hex_to_pixel(q, r, self.hex_grid.radius)
                    hex_center = (center_x + hex_center[0], center_y + hex_center[1])
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

    def _add_map_features(self):
        """Add map features as widgets"""
        center_x, center_y = self.center_x, self.center_y

        for (q, r), feature_type in self.game_data.map_features.items():
            hex_pos = hex_to_pixel(q, r, self.hex_grid.radius)
            pixel_pos = (center_x + hex_pos[0], center_y + hex_pos[1])

            # Create a widget for this feature
            feature_widget = MapIcon('feature', {'type': feature_type, 'q': q, 'r': r})
            feature_widget.size = (dp(24), dp(24))
            feature_widget.pos = (pixel_pos[0] - dp(12), pixel_pos[1] - dp(12))

            # Add visual representation
            with feature_widget.canvas:
                if feature_type == 'oasis':
                    Color(0.3, 0.6, 0.9, 0.8)
                    Ellipse(pos=feature_widget.pos, size=feature_widget.size)
                elif feature_type == 'dune':
                    Color(0.9, 0.8, 0.4, 0.6)
                    Ellipse(pos=feature_widget.pos, size=feature_widget.size)
                elif feature_type == 'ruins':
                    Color(0.5, 0.5, 0.5, 0.7)
                    Rectangle(pos=feature_widget.pos, size=feature_widget.size)

            self.add_widget(feature_widget)

    def _add_player_camp(self):
        """Add player camp as a widget"""
        center_x, center_y = self.center_x, self.center_y
        camp_pos = hex_to_pixel(0, 0, self.hex_grid.radius)
        pixel_pos = (center_x + camp_pos[0], center_y + camp_pos[1])

        # Create camp widget
        camp_widget = MapIcon('camp', {'q': 0, 'r': 0})
        camp_widget.size = (dp(40), dp(40))
        camp_widget.pos = (pixel_pos[0] - dp(20), pixel_pos[1] - dp(20))

        # Try to use camp image, fallback to colored shape
        camp_image_path = 'assets/camp.png'
        if os.path.exists(camp_image_path):
            camp_img = Image(source=camp_image_path, size=camp_widget.size, pos=camp_widget.pos)
            camp_widget.add_widget(camp_img)
        else:
            # Fallback: draw tent shape
            with camp_widget.canvas:
                # Tent base
                Color(0.6, 0.4, 0.2, 1)  # Brown
                Rectangle(pos=(camp_widget.x + dp(5), camp_widget.y), size=(dp(30), dp(20)))
                # Tent roof (triangle)
                Color(0.7, 0.5, 0.3, 1)  # Lighter brown
                points = [camp_widget.x + dp(20), camp_widget.y + dp(20),  # Top
                         camp_widget.x + dp(5), camp_widget.y,           # Bottom left
                         camp_widget.x + dp(35), camp_widget.y]          # Bottom right
                Line(points=points, width=2, close=True)
                # Door
                Color(0.4, 0.3, 0.1, 1)
                Rectangle(pos=(camp_widget.x + dp(15), camp_widget.y), size=(dp(10), dp(15)))

        self.add_widget(camp_widget)
        self.map_icons['camp'] = camp_widget

    def _add_caravans(self):
        """Add caravan widgets"""
        center_x, center_y = self.center_x, self.center_y

        for caravan in self.game_data.visible_caravans:
            hex_pos = hex_to_pixel(caravan.q, caravan.r, self.hex_grid.radius)
            pixel_pos = (center_x + hex_pos[0], center_y + hex_pos[1])

            # Create caravan widget
            caravan_widget = MapIcon('caravan', caravan)
            caravan_widget.size = (dp(20), dp(20))
            caravan_widget.pos = (pixel_pos[0] - dp(10), pixel_pos[1] - dp(10))

            # Determine size and appearance based on type
            if caravan.caravan_type == 'salt':
                size = dp(12)
                color = (0.8, 0.8, 0.8, 1)  # Silver
                img_path = 'assets/caravan_small.png'
            elif caravan.caravan_type == 'gold':
                size = dp(14)
                color = (1, 0.8, 0, 1)  # Gold
                img_path = 'assets/caravan.png'
            elif caravan.caravan_type == 'spices':
                size = dp(16)
                color = (0.6, 0.2, 0.8, 1)  # Purple
                img_path = 'assets/caravan_large.png'
            elif caravan.caravan_type == 'imperial':
                size = dp(18)
                color = (0.9, 0.1, 0.1, 1)  # Red
                img_path = 'assets/caravan_large.png'
            else:  # sandworm
                size = dp(24)
                color = (0.8, 0.2, 0.2, 1)  # Dark red
                img_path = 'assets/sandworm.png'

            caravan_widget.size = (size, size)
            caravan_widget.pos = (pixel_pos[0] - size/2, pixel_pos[1] - size/2)

            # Try to use caravan image, fallback to colored rectangle
            if os.path.exists(img_path):
                caravan_img = Image(source=img_path, size=caravan_widget.size, pos=caravan_widget.pos)
                caravan_widget.add_widget(caravan_img)
            else:
                # Fallback: colored rectangle with label
                with caravan_widget.canvas:
                    Color(*color)
                    Rectangle(pos=caravan_widget.pos, size=caravan_widget.size)

                # Add text label
                label = Label(
                    text=caravan.caravan_type[:3].upper(),
                    font_size=dp(8),
                    pos=caravan_widget.pos,
                    size=caravan_widget.size,
                    halign='center',
                    valign='middle'
                )
                caravan_widget.add_widget(label)

            # If scouted, add a small green indicator
            if caravan.is_scouted:
                scout_indicator = Widget(size=(dp(6), dp(6)),
                                       pos=(pixel_pos[0] - dp(3), pixel_pos[1] + size/2 - dp(3)))
                with scout_indicator.canvas:
                    Color(0, 1, 0, 0.8)  # Green
                    Ellipse(pos=scout_indicator.pos, size=scout_indicator.size)
                caravan_widget.add_widget(scout_indicator)

            self.add_widget(caravan_widget)

    def _add_scouting_spies(self):
        """Add scouting spy widgets"""
        center_x, center_y = self.center_x, self.center_y

        # Get scouting spies from the parent screen
        parent_screen = self.parent
        if hasattr(parent_screen, 'scouting_spies'):
            for spy in parent_screen.scouting_spies:
                hex_pos = hex_to_pixel(spy['q'], spy['r'], self.hex_grid.radius)
                pixel_pos = (center_x + hex_pos[0], center_y + hex_pos[1])

                # Create spy widget
                spy_widget = MapIcon('spy', spy)
                spy_widget.size = (dp(8), dp(8))
                spy_widget.pos = (pixel_pos[0] - dp(4), pixel_pos[1] - dp(4))

                # Try to use camel image, fallback to colored dot
                camel_path = 'assets/camel.png'
                if os.path.exists(camel_path):
                    spy_img = Image(source=camel_path, size=spy_widget.size, pos=spy_widget.pos)
                    spy_widget.add_widget(spy_img)
                else:
                    with spy_widget.canvas:
                        Color(0.4, 0.6, 0.8, 1)  # Blue
                        Ellipse(pos=spy_widget.pos, size=spy_widget.size)

                self.add_widget(spy_widget)

    def handle_icon_touch(self, icon_type, data):
        """Handle touch on map icons"""
        if icon_type == 'caravan':
            self._start_raid(data)
        elif icon_type == 'camp':
            # Could show camp details or something
            pass
        elif icon_type == 'feature':
            # Could show feature details
            pass
        elif icon_type == 'spy':
            # Spy is already active
            pass

    def on_touch_down(self, touch):
        """Handle touch/click on empty map space"""
        if not self.collide_point(*touch.pos):
            return False

        # Convert touch position to hex coordinates
        center_x, center_y = self.center_x, self.center_y
        relative_pos = (touch.pos[0] - center_x, touch.pos[1] - center_y)
        hex_coords = pixel_to_hex(relative_pos[0], relative_pos[1], self.hex_grid.radius)

        # Check if clicking near existing icons first
        for child in self.children:
            if isinstance(child, MapIcon) and child.collide_point(*touch.pos):
                # Touch was handled by the icon
                return True

        # Otherwise, start scouting mission
        parent_screen = self.parent
        if hasattr(parent_screen, '_start_scouting'):
            parent_screen._start_scouting(hex_coords[0], hex_coords[1])
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
        self.scouting_spies = []  # List of active scouting missions

    def on_enter(self):
        """Called when entering the map screen"""
        if not self.game_data:
            app = App.get_running_app()
            self.game_data = app.game_data

        # Setup UI if not already done
        if not self.hex_map:
            self.setup_ui()

        # Update map display
        self.hex_map.update_map_display()

    def setup_ui(self):
        """Setup the map screen UI"""
        self.clear_widgets()

        # Main layout
        main_layout = BoxLayout(orientation='vertical')

        # Top resource bar
        resource_bar = self.create_resource_bar()
        main_layout.add_widget(resource_bar)

        # Map area (takes most of the space)
        self.hex_map = HexMapWidget(self.game_data, size_hint_y=0.8)
        main_layout.add_widget(self.hex_map)

        # Bottom action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=dp(10), padding=dp(10))

        scout_btn = Button(text='Scout', background_color=(0.4, 0.6, 0.8, 1))
        scout_btn.bind(on_press=self.scout_random_hex)
        button_layout.add_widget(scout_btn)

        camp_btn = Button(text='To Camp', background_color=(0.6, 0.8, 0.4, 1))
        camp_btn.bind(on_press=self.go_to_camp)
        button_layout.add_widget(camp_btn)

        shop_btn = Button(text='Shop', background_color=(0.8, 0.6, 0.4, 1))
        shop_btn.bind(on_press=self.go_to_shop)
        button_layout.add_widget(shop_btn)

        main_layout.add_widget(button_layout)

        self.add_widget(main_layout)

    def create_resource_bar(self):
        """Create the top resource display bar"""
        resource_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.1,
                                   padding=dp(10))

        resources = [
            ('water', 'Water'),
            ('salt', 'Salt'),
            ('gold', 'Gold'),
            ('spices', 'Spices'),
            ('gems', 'Gems')
        ]

        for resource_key, display_name in resources:
            resource_box = BoxLayout(orientation='vertical', size_hint_x=0.2)
            title = Label(text=display_name, font_size=dp(12), bold=True)
            value = Label(text=str(int(self.game_data.resources.get(resource_key, 0))), font_size=dp(14))
            value.id = f'{resource_key}_display'
            resource_box.add_widget(title)
            resource_box.add_widget(value)
            resource_layout.add_widget(resource_box)

        return resource_layout

    def scout_random_hex(self, instance):
        """Scout a random nearby hex"""
        # Find a random hex near the camp
        q = random.randint(-3, 3)
        r = random.randint(-3, 3)
        self._start_scouting(q, r)

    def go_to_camp(self, instance):
        """Go to camp screen"""
        self.manager.current = 'camp'

    def go_to_shop(self, instance):
        """Go to shop screen"""
        self.manager.current = 'shop'

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

        # Trigger map redraw
        if self.hex_map:
            self.hex_map._add_scouting_spies()
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

        # Update map display
        if self.hex_map:
            self.hex_map.update_map_display()

    def _start_raid(self, caravan: Caravan):
        """Initiate raid on selected caravan"""
        # Switch to raid screen with selected caravan
        raid_screen = self.manager.get_screen('raid')
        raid_screen.prepare_raid(caravan)
        self.manager.current = 'raid'

    def on_leave(self):
        """Called when leaving the map screen"""
        pass
