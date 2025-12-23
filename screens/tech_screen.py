"""
Tech Screen - Technology research tree
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.app import App


class TechScreen(Screen):
    """Screen for researching technologies"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        """Called when entering tech screen"""
        self.update_display()

    def update_display(self):
        """Update the tech tree display"""
        app = self.get_app()
        tech_tree = app.game_data.tech_tree

        # Clear existing layout
        self.clear_widgets()

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Title
        title = Label(text='TECHNOLOGY TREE', font_size=24, bold=True, size_hint_y=0.1)
        main_layout.add_widget(title)

        # Tech branches in a grid
        tech_grid = GridLayout(cols=1, spacing=20, size_hint_y=0.8)

        for branch_name, branch_data in tech_tree.TECH_BRANCHES.items():
            branch_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)

            # Branch title
            branch_title = Label(text=branch_data['name'], font_size=18, bold=True)
            branch_layout.add_widget(branch_title)

            # Tech tiers
            tiers_layout = BoxLayout(orientation='horizontal', spacing=10)

            for tier in range(1, 4):
                tier_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_x=0.3)

                tech_data = branch_data['tiers'][tier]
                current_tier = tech_tree.unlocked_techs.get(branch_name, 0)

                # Tech button
                if current_tier >= tier:
                    # Already researched
                    tech_button = Button(
                        text=f"{tech_data['name']}\n✓",
                        background_color=(0.2, 0.8, 0.2, 1),
                        disabled=True
                    )
                elif current_tier >= tier - 1:
                    # Can research
                    tech_button = Button(
                        text=f"{tech_data['name']}\nResearch",
                        background_color=(0.8, 0.6, 0.2, 1)
                    )
                    tech_button.bind(on_press=lambda btn, b=branch_name, t=tier: self.research_tech(b, t))
                else:
                    # Locked
                    tech_button = Button(
                        text=f"Tier {tier}\nLocked",
                        background_color=(0.5, 0.5, 0.5, 1),
                        disabled=True
                    )

                tech_button.text_size = (tech_button.width, None)
                tech_button.valign = 'center'
                tech_button.halign = 'center'

                # Description
                desc_label = Label(
                    text=tech_data['description'],
                    font_size=12,
                    size_hint_y=0.6
                )

                tier_layout.add_widget(tech_button)
                tier_layout.add_widget(desc_label)
                tiers_layout.add_widget(tier_layout)

            branch_layout.add_widget(tiers_layout)
            tech_grid.add_widget(branch_layout)

        main_layout.add_widget(tech_grid)

        # Back button
        back_button = Button(text='BACK TO CAMP', size_hint_y=0.1)
        back_button.bind(on_press=self.return_to_camp)
        main_layout.add_widget(back_button)

        self.add_widget(main_layout)

    def research_tech(self, branch, tier):
        """Research a technology"""
        app = self.get_app()
        tech_tree = app.game_data.tech_tree

        if tech_tree.can_research(branch, tier):
            cost = tech_tree.research_tech(branch, tier)

            if app.game_data.can_afford(cost):
                app.game_data.spend_resources(cost)
                tech_tree.unlocked_techs[branch] = tier
                print(f"Researched {tech_tree.TECH_BRANCHES[branch]['tiers'][tier]['name']}")
                self.update_display()
            else:
                print("Cannot afford technology")
        else:
            print("Cannot research this technology yet")

    def return_to_camp(self, instance):
        """Return to camp screen"""
        self.manager.current = 'camp'

    def get_app(self):
        """Get the running Kivy app"""
        return App.get_running_app()
