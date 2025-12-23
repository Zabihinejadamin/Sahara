"""
Camp Screen - Building placement and camp management
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.app import App


class CampGridWidget(BoxLayout):
    """8x8 grid for building placement"""

    def __init__(self, camp_screen, **kwargs):
        super().__init__(**kwargs)
        self.camp_screen = camp_screen
        self.cols = 8
        self.spacing = dp(2)
        self.building_buttons = {}

        # Create 8x8 grid of buttons
        for y in range(8):
            for x in range(8):
                button = Button(
                    text='',
                    background_color=(0.8, 0.7, 0.6, 1),  # Desert sand color
                    size_hint=(None, None),
                    size=(dp(40), dp(40))
                )
                button.bind(on_press=lambda btn, x=x, y=y: self.on_grid_click(x, y))
                self.building_buttons[(x, y)] = button
                self.add_widget(button)

        self.update_grid_display()

    def on_grid_click(self, x, y):
        """Handle clicking on a grid cell"""
        game_data = self.camp_screen.game_data

        # Check if there's already a building here
        if (x, y) in game_data.camp_buildings:
            # Try to upgrade existing building
            if game_data.upgrade_building(x, y):
                print(f"Upgraded building at ({x}, {y})")
        else:
            # Show building selection menu
            self.show_building_menu(x, y)

        self.update_grid_display()
        self.camp_screen.update_resource_display()

    def show_building_menu(self, x, y):
        """Show menu to select which building to place"""
        # For simplicity, auto-place a tent if possible
        game_data = self.camp_screen.game_data

        # Check if can afford a tent
        tent_cost = {'gold': 20}
        if game_data.can_afford(tent_cost):
            if game_data.place_building(x, y, 'tent'):
                game_data.spend_resources(tent_cost)
                print(f"Placed tent at ({x}, {y})")

        self.update_grid_display()

    def update_grid_display(self):
        """Update the visual display of buildings on the grid"""
        game_data = self.camp_screen.game_data

        for (x, y), button in self.building_buttons.items():
            if (x, y) in game_data.camp_buildings:
                building = game_data.camp_buildings[(x, y)]
                building_type = building.building_type
                level = building.level

                # Set button text and color based on building type
                if building_type == 'tent':
                    button.text = f'T{level}'
                    button.background_color = (0.6, 0.4, 0.2, 1)  # Brown
                elif building_type == 'well':
                    button.text = f'W{level}'
                    button.background_color = (0.3, 0.6, 0.9, 1)  # Blue
                elif building_type == 'stable':
                    button.text = f'S{level}'
                    button.background_color = (0.8, 0.6, 0.4, 1)  # Tan
                elif building_type == 'watchtower':
                    button.text = f'Tw{level}'
                    button.background_color = (0.7, 0.7, 0.7, 1)  # Gray
                elif building_type == 'slave_pen':
                    button.text = f'Sp{level}'
                    button.background_color = (0.5, 0.3, 0.1, 1)  # Dark brown
            else:
                button.text = ''
                button.background_color = (0.8, 0.7, 0.6, 1)  # Empty sand color


class CampScreen(Screen):
    """Screen for building placement and camp management"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_data = None
        self.camp_grid = None

    def on_enter(self):
        """Called when entering camp screen"""
        app = self.get_app()
        self.game_data = app.game_data

        self.setup_ui()

    def setup_ui(self):
        """Set up the camp screen UI"""
        self.clear_widgets()

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # Top resource bar
        resource_bar = self.create_resource_bar()
        main_layout.add_widget(resource_bar)

        # Camp grid (takes most of the space)
        self.camp_grid = CampGridWidget(self, size_hint_y=0.6)
        main_layout.add_widget(self.camp_grid)

        # Bottom action buttons
        action_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.2)

        # Slave management
        slave_layout = BoxLayout(orientation='vertical', size_hint_x=0.4)
        slave_title = Label(text='SLAVE MANAGEMENT', font_size=dp(16), bold=True)
        slave_info = Label(text=f"Slaves: {self.game_data.resources.get('slaves', 0)}")
        recruit_button = Button(text='Recruit from Slaves\n(Converts to Raiders)')
        recruit_button.bind(on_press=self.recruit_from_slaves)

        slave_layout.add_widget(slave_title)
        slave_layout.add_widget(slave_info)
        slave_layout.add_widget(recruit_button)
        action_layout.add_widget(slave_layout)

        # Navigation buttons
        nav_layout = BoxLayout(orientation='vertical', size_hint_x=0.6, spacing=dp(5))

        map_button = Button(text='RETURN TO MAP', size_hint_y=0.4)
        map_button.bind(on_press=self.return_to_map)

        tech_button = Button(text='TECHNOLOGY TREE', size_hint_y=0.4)
        tech_button.bind(on_press=self.go_to_tech)

        nav_layout.add_widget(map_button)
        nav_layout.add_widget(tech_button)
        action_layout.add_widget(nav_layout)

        main_layout.add_widget(action_layout)

        self.add_widget(main_layout)
        self.update_resource_display()

    def create_resource_bar(self):
        """Create the top resource display bar"""
        resource_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=0.1)

        resources = [
            ('water', 'Water'),
            ('salt', 'Salt'),
            ('gold', 'Gold'),
            ('spices', 'Spices'),
            ('slaves', 'Slaves')
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

    def update_resource_display(self):
        """Update resource display values"""
        for child in self.walk():
            if hasattr(child, 'id'):
                resource_key = child.id.replace('_display', '')
                if resource_key in self.game_data.resources:
                    child.text = str(int(self.game_data.resources[resource_key]))

    def recruit_from_slaves(self, instance):
        """Convert slaves to raiders"""
        # Convert 5 slaves at a time for simplicity
        slaves_to_convert = min(5, self.game_data.resources.get('slaves', 0))

        if slaves_to_convert > 0:
            raiders_gained = self.game_data.recruit_from_slaves(slaves_to_convert)
            print(f"Converted {slaves_to_convert} slaves to {raiders_gained} raiders")

        self.update_resource_display()

    def return_to_map(self, instance):
        """Return to the map screen"""
        self.manager.current = 'map'

    def go_to_tech(self, instance):
        """Go to technology screen"""
        self.manager.current = 'tech'

    def get_app(self):
        """Get the running Kivy app"""
        return App.get_running_app()
