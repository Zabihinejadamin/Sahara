"""
Monetization module for Sahara Raiders
Handles rewarded ads, in-app purchases, and premium currency
"""
import time
from typing import Callable, Optional, Dict, Any
from kivy.clock import Clock

# Premium currency
GEMS_CURRENCY = "gems"

# IAP Product IDs (for future Google Play/Apple integration)
IAP_PRODUCTS = {
    "small_gem_pack": {
        "id": "small_gem_pack",
        "gems": 500,
        "price_usd": 0.99,
        "name": "Small Gem Pack",
        "description": "500 Gems"
    },
    "medium_gem_pack": {
        "id": "medium_gem_pack",
        "gems": 3000,
        "price_usd": 4.99,
        "name": "Medium Gem Pack",
        "description": "3000 Gems + 10% Bonus"
    },
    "oasis_bundle": {
        "id": "oasis_bundle",
        "gems": 0,  # Special bundle
        "price_usd": 99.00,
        "name": "Oasis Bundle",
        "description": "Legendary Skin + 10k Resources"
    }
}

class MonetizationManager:
    """Manages all monetization features"""

    def __init__(self):
        self.gems = 0
        self.last_ad_watch = 0
        self.ad_cooldown = 300  # 5 minutes between ads

    def get_gems(self) -> int:
        """Get current gem balance"""
        return self.gems

    def add_gems(self, amount: int):
        """Add gems to balance"""
        self.gems += amount
        print(f"Added {amount} gems. Total: {self.gems}")

    def spend_gems(self, amount: int) -> bool:
        """Spend gems if available"""
        if self.gems >= amount:
            self.gems -= amount
            print(f"Spent {amount} gems. Remaining: {self.gems}")
            return True
        return False

    def can_watch_ad(self) -> bool:
        """Check if player can watch a rewarded ad"""
        return time.time() - self.last_ad_watch >= self.ad_cooldown

    def show_rewarded_ad(self, reward_type: str, callback: Callable[[bool], None]):
        """
        Show rewarded ad with specified reward type

        Args:
            reward_type: Type of reward ('double_loot', 'revive_raiders', 'speed_upgrade')
            callback: Function called with success status
        """
        if not self.can_watch_ad():
            print("Ad cooldown active")
            callback(False)
            return

        print(f"Showing rewarded ad for: {reward_type}")

        # Check platform and show appropriate ad
        try:
            from plyer import platform
            current_platform = platform

            if current_platform == "android":
                # TODO: Replace with real AdMob integration
                # from kivy.core.window import Window
                # # Real AdMob code would go here
                # admob.show_rewarded_ad(on_rewarded=lambda: callback(True))
                print("AdMob rewarded ad would show here")

            elif current_platform == "ios":
                # TODO: Replace with real iOS ad network integration
                print("iOS rewarded ad would show here")

            else:
                # Desktop - simulate ad
                print("Desktop mode: Simulating ad watch...")

        except ImportError:
            print("Plyer not available - simulating ad")

        # Simulate ad completion after 3 seconds
        def simulate_ad_completion(dt):
            self.last_ad_watch = time.time()
            success = True  # Simulate success
            print(f"Ad completed with success: {success}")
            callback(success)

        Clock.schedule_once(simulate_ad_completion, 3)

    def purchase_gems(self, product_id: str, on_success: Callable[[int], None],
                     on_failure: Callable[[str], None] = None):
        """
        Initiate gem purchase

        Args:
            product_id: ID of the product to purchase
            on_success: Callback with amount of gems received
            on_failure: Optional callback for failure with error message
        """
        if product_id not in IAP_PRODUCTS:
            if on_failure:
                on_failure("Invalid product")
            return

        product = IAP_PRODUCTS[product_id]

        print(f"Initiating purchase: {product['name']} for ${product['price_usd']}")

        try:
            from plyer import platform
            current_platform = platform

            if current_platform == "android":
                # TODO: Replace with real Google Play Billing
                # from kivy.core.window import Window
                # # Real Google Play Billing code would go here
                # billing.purchase(product_id, lambda success, data: handle_purchase(success, data))
                print("Google Play Billing purchase would initiate here")

            elif current_platform == "ios":
                # TODO: Replace with real Apple IAP
                print("Apple IAP purchase would initiate here")

            else:
                # Desktop - simulate purchase
                print("Desktop mode: Simulating purchase...")

        except ImportError:
            print("Plyer not available - simulating purchase")

        # Simulate purchase completion after 2 seconds
        def simulate_purchase(dt):
            success = True  # Simulate success
            if success:
                gems_received = product["gems"]
                if product_id == "medium_gem_pack":
                    gems_received = int(gems_received * 1.1)  # 10% bonus

                self.add_gems(gems_received)
                on_success(gems_received)
                print(f"Purchase completed: {gems_received} gems")
            else:
                error_msg = "Purchase failed"
                if on_failure:
                    on_failure(error_msg)

        Clock.schedule_once(simulate_purchase, 2)

    def get_product_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a product"""
        return IAP_PRODUCTS.get(product_id)

    def get_all_products(self) -> Dict[str, Dict[str, Any]]:
        """Get all available products"""
        return IAP_PRODUCTS.copy()

# Global monetization manager instance
monetization_manager = MonetizationManager()

# Convenience functions
def get_gems() -> int:
    """Get current gem balance"""
    return monetization_manager.get_gems()

def add_gems(amount: int):
    """Add gems to balance"""
    monetization_manager.add_gems(amount)

def spend_gems(amount: int) -> bool:
    """Spend gems if available"""
    return monetization_manager.spend_gems(amount)

def show_rewarded_ad(reward_type: str, callback: Callable[[bool], None]):
    """Show rewarded ad"""
    monetization_manager.show_rewarded_ad(reward_type, callback)

def purchase_gems(product_id: str, on_success: Callable[[int], None],
                 on_failure: Callable[[str], None] = None):
    """Purchase gems"""
    monetization_manager.purchase_gems(product_id, on_success, on_failure)
