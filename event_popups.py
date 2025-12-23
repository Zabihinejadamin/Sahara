"""
Event popup widgets for notifications and alerts
"""
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock


class EventPopup(ModalView):
    """Base class for event notification popups"""

    def __init__(self, title: str, message: str, button_text: str = "OK",
                 on_close=None, auto_dismiss_time=None, **kwargs):
        super().__init__(size_hint=(0.8, 0.4), **kwargs)

        self.on_close_callback = on_close

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Title
        title_label = Label(text=title, font_size=dp(24), bold=True, size_hint_y=0.3)
        layout.add_widget(title_label)

        # Message
        message_label = Label(text=message, font_size=dp(16), halign='center',
                             valign='middle', text_size=(self.width * 0.9, None))
        layout.add_widget(message_label)

        # Button
        button = Button(text=button_text, size_hint_y=0.3, background_color=(0.4, 0.8, 0.4, 1))
        button.bind(on_press=self.dismiss_popup)
        layout.add_widget(button)

        self.add_widget(layout)

        # Auto-dismiss if specified
        if auto_dismiss_time:
            Clock.schedule_once(lambda dt: self.dismiss(), auto_dismiss_time)

    def dismiss_popup(self, instance=None):
        """Dismiss the popup and call callback if provided"""
        self.dismiss()
        if self.on_close_callback:
            self.on_close_callback()


class WorldBossPopup(EventPopup):
    """Popup for world boss events"""

    def __init__(self, boss_status, **kwargs):
        health_percent = int(boss_status["health_percentage"])
        time_remaining = int(boss_status["time_remaining"] / 3600)  # Hours

        title = "🐛 SANDWORM APPEARS!"
        message = f"The legendary Sandworm has emerged!\n\n" \
                 f"Health: {health_percent}%\n" \
                 f"Time Remaining: {time_remaining} hours\n\n" \
                 f"Damage Dealt: {boss_status['player_damage']}\n\n" \
                 f"Join your clan to battle this epic foe!"

        super().__init__(title, message, "TO BATTLE!", **kwargs)


class DailyEventPopup(EventPopup):
    """Popup for daily events"""

    def __init__(self, event_type, **kwargs):
        event_messages = {
            'caravan_alert': "🚨 CARAVAN ALERT!\n\nA high-value caravan has been spotted nearby!",
            'resource_boost': "📈 RESOURCE BOOST!\n\nAll resource generation doubled for 24 hours!",
            'raid_bonus': "⚔️ RAID BONUS!\n\nAll raids give bonus loot today!"
        }

        title = "🎉 DAILY EVENT"
        message = event_messages.get(event_type, "A special daily event is active!")

        super().__init__(title, message, "LET'S GO!", **kwargs)


class WeeklyEventPopup(EventPopup):
    """Popup for weekly events"""

    def __init__(self, **kwargs):
        title = "🏆 BLACK GOLD RUSH"
        message = "🎊 WEEKLY EVENT STARTED!\n\n" \
                 "Double loot from all raids!\n" \
                 "Special mega-caravans spawning!\n\n" \
                 "Duration: 7 days"

        super().__init__(title, message, "CHARGE!", **kwargs)


class RewardPopup(EventPopup):
    """Popup for showing rewards"""

    def __init__(self, reward_type, amount, **kwargs):
        reward_messages = {
            'gems': f"💎 GEM REWARD!\n\nYou received {amount} gems!",
            'loot': f"💰 LOOT BONUS!\n\nDouble loot activated for your next raid!",
            'raiders': f"⚔️ RAIDERS REVIVED!\n\n{amount} fallen raiders have been revived!",
            'speed': f"⚡ SPEED BOOST!\n\nBuilding upgrades are now 2x faster!"
        }

        title = "🎁 REWARD CLAIMED"
        message = reward_messages.get(reward_type, f"You received: {amount}")

        super().__init__(title, message, "AWESOME!", **kwargs)


class ClanHelpPopup(EventPopup):
    """Popup for clan raid assistance requests"""

    def __init__(self, requester_name, caravan_type, **kwargs):
        title = "🤝 CLAN ASSISTANCE REQUEST"
        message = f"🏹 {requester_name} needs help raiding a {caravan_type}!\n\n" \
                 f"Will you send reinforcements?"

        super().__init__(title, message, "SEND HELP", **kwargs)


def show_event_popup(popup_type: str, **kwargs):
    """
    Convenience function to show different types of event popups

    Args:
        popup_type: Type of popup ('world_boss', 'daily_event', 'weekly_event', 'reward', 'clan_help')
        **kwargs: Arguments specific to each popup type
    """
    popup_classes = {
        'world_boss': WorldBossPopup,
        'daily_event': DailyEventPopup,
        'weekly_event': WeeklyEventPopup,
        'reward': RewardPopup,
        'clan_help': ClanHelpPopup
    }

    if popup_type in popup_classes:
        popup = popup_classes[popup_type](**kwargs)
        popup.open()
    else:
        print(f"Unknown popup type: {popup_type}")


# Example usage functions
def show_world_boss_notification(boss_status):
    """Show world boss notification"""
    show_event_popup('world_boss', boss_status=boss_status)


def show_daily_event_notification(event_type):
    """Show daily event notification"""
    show_event_popup('daily_event', event_type=event_type)


def show_weekly_event_notification():
    """Show weekly event notification"""
    show_event_popup('weekly_event')


def show_reward_notification(reward_type, amount):
    """Show reward notification"""
    show_event_popup('reward', reward_type=reward_type, amount=amount)


def show_clan_help_request(requester_name, caravan_type):
    """Show clan help request"""
    show_event_popup('clan_help', requester_name=requester_name, caravan_type=caravan_type)
