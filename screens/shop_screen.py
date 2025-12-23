"""
Shop Screen - In-app purchases and premium content
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.metrics import dp

from monetization import get_gems, purchase_gems, IAP_PRODUCTS


class ShopScreen(Screen):
    """Screen for in-app purchases"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        """Called when entering shop screen"""
        self.setup_ui()

    def setup_ui(self):
        """Setup the shop screen UI"""
        self.clear_widgets()

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Header with gem balance
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        title = Label(text='PREMIUM SHOP', font_size=dp(24), bold=True, halign='center')
        gem_display = Label(text=f'Gems: {get_gems()}', font_size=dp(18), halign='right')
        header.add_widget(title)
        header.add_widget(gem_display)
        main_layout.add_widget(header)

        # Shop categories
        categories_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.8)

        # Gem Packs
        gem_packs = BoxLayout(orientation='vertical', spacing=dp(10))
        gem_title = Label(text='GEM PACKS', font_size=dp(18), bold=True, size_hint_y=0.1)

        gem_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=0.9)

        for product_id, product in IAP_PRODUCTS.items():
            if "gem_pack" in product_id or product_id == "oasis_bundle":
                pack_layout = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10),
                                       size_hint_y=None, height=dp(120))

                pack_name = Label(text=product["name"], font_size=dp(16), bold=True)
                pack_desc = Label(text=product["description"], font_size=dp(14))
                pack_price = Label(text=f'${product["price_usd"]:.2f}', font_size=dp(16),
                                 color=(0, 0.8, 0, 1))

                buy_btn = Button(text='PURCHASE', background_color=(0.2, 0.8, 0.2, 1))
                buy_btn.bind(on_press=lambda x, pid=product_id: self.purchase_product(pid))

                pack_layout.add_widget(pack_name)
                pack_layout.add_widget(pack_desc)
                pack_layout.add_widget(pack_price)
                pack_layout.add_widget(buy_btn)

                gem_grid.add_widget(pack_layout)

        gem_packs.add_widget(gem_title)
        gem_packs.add_widget(gem_grid)
        categories_layout.add_widget(gem_packs)

        # Premium Features
        premium_features = BoxLayout(orientation='vertical', spacing=dp(10))
        premium_title = Label(text='PREMIUM FEATURES', font_size=dp(18), bold=True, size_hint_y=0.1)

        features_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=0.9)

        # Rewarded Ad Features
        ad_features = [
            ("Double Loot", "double_loot", "Watch ad to double raid loot"),
            ("Revive Raiders", "revive_raiders", "Watch ad to revive lost raiders"),
            ("Speed Up", "speed_upgrade", "Watch ad to speed up building upgrades")
        ]

        for feature_name, reward_type, description in ad_features:
            feature_layout = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10),
                                      size_hint_y=None, height=dp(100))

            feature_label = Label(text=feature_name, font_size=dp(16), bold=True)
            desc_label = Label(text=description, font_size=dp(12))
            watch_btn = Button(text='WATCH AD', background_color=(0.8, 0.6, 0.2, 1))
            watch_btn.bind(on_press=lambda x, rt=reward_type: self.watch_rewarded_ad(rt))

            feature_layout.add_widget(feature_label)
            feature_layout.add_widget(desc_label)
            feature_layout.add_widget(watch_btn)

            features_grid.add_widget(feature_layout)

        premium_features.add_widget(premium_title)
        premium_features.add_widget(features_grid)
        categories_layout.add_widget(premium_features)

        main_layout.add_widget(categories_layout)

        # Back button
        back_btn = Button(text='BACK TO CAMP', size_hint_y=0.08)
        back_btn.bind(on_press=self.return_to_camp)
        main_layout.add_widget(back_btn)

        self.add_widget(main_layout)

    def purchase_product(self, product_id):
        """Handle product purchase"""
        def on_purchase_success(gems_received):
            print(f"Purchase successful! Received {gems_received} gems")
            self.setup_ui()  # Refresh UI with new gem balance

        def on_purchase_failure(error_msg):
            print(f"Purchase failed: {error_msg}")

        purchase_gems(product_id, on_purchase_success, on_purchase_failure)

    def watch_rewarded_ad(self, reward_type):
        """Handle rewarded ad watch"""
        def on_ad_complete(success):
            if success:
                print(f"Ad completed successfully for reward: {reward_type}")
                self.apply_ad_reward(reward_type)
                self.show_reward_popup(reward_type)
            else:
                print("Ad failed or was skipped")

        from monetization import show_rewarded_ad
        show_rewarded_ad(reward_type, on_ad_complete)

    def apply_ad_reward(self, reward_type):
        """Apply the reward from watching an ad"""
        app = self.get_app()

        if reward_type == "double_loot":
            # Store double loot flag for next raid
            app.game_data.double_loot_active = True
            print("Double loot activated for next raid!")

        elif reward_type == "revive_raiders":
            # Revive 50% of lost raiders
            revived = int(app.game_data.last_raid_losses * 0.5)
            app.game_data.raiders_available += revived
            print(f"Revived {revived} raiders!")

        elif reward_type == "speed_upgrade":
            # Speed up current building upgrades
            app.game_data.upgrade_speed_multiplier = 2.0
            print("Building upgrade speed doubled!")

    def show_reward_popup(self, reward_type):
        """Show reward confirmation popup"""
        reward_messages = {
            "double_loot": "Double loot activated for your next raid!",
            "revive_raiders": "Your fallen raiders have been revived!",
            "speed_upgrade": "Building upgrades are now 2x faster!"
        }

        message = reward_messages.get(reward_type, "Reward claimed!")

        # In a real app, you'd show a proper popup/modal
        print(f"REWARD: {message}")

    def return_to_camp(self, instance=None):
        """Return to camp screen"""
        self.manager.current = 'camp'

    def get_app(self):
        """Get the running Kivy app"""
        return App.get_running_app()
