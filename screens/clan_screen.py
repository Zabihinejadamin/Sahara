"""
Clan Screen - Clan management, chat, and multiplayer features
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
import uuid
import time
from typing import Dict, List, Any, Optional

from firebase_config import safe_firebase_operation, get_database, DB_PATHS


class Clan:
    """Represents a clan"""

    def __init__(self, clan_id: str, name: str, tag: str, leader_id: str,
                 member_ids: List[str] = None, chat_messages: List[Dict] = None):
        self.id = clan_id
        self.name = name
        self.tag = tag
        self.leader_id = leader_id
        self.member_ids = member_ids or [leader_id]
        self.chat_messages = chat_messages or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert clan to dictionary for Firebase"""
        return {
            "id": self.id,
            "name": self.name,
            "tag": self.tag,
            "leader_id": self.leader_id,
            "member_ids": self.member_ids,
            "chat_messages": self.chat_messages,
            "created_at": time.time()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Clan':
        """Create clan from Firebase data"""
        return cls(
            clan_id=data["id"],
            name=data["name"],
            tag=data["tag"],
            leader_id=data["leader_id"],
            member_ids=data.get("member_ids", []),
            chat_messages=data.get("chat_messages", [])
        )


class ClanScreen(Screen):
    """Screen for clan management and social features"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_id = None
        self.current_clan = None
        self.chat_messages = []
        self.chat_update_event = None

    def on_enter(self):
        """Called when entering clan screen"""
        app = self.get_app()
        self.player_id = app.game_data.player_id

        if not self.player_id:
            self.player_id = str(uuid.uuid4())
            app.game_data.player_id = self.player_id

        self.setup_ui()
        self.load_clan_data()
        self.start_chat_updates()

    def on_leave(self):
        """Called when leaving clan screen"""
        if self.chat_update_event:
            self.chat_update_event.cancel()
            self.chat_update_event = None

    def setup_ui(self):
        """Setup the clan screen UI"""
        self.clear_widgets()

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # Header with clan status
        header = self.create_header()
        main_layout.add_widget(header)

        # Main content area (tabs)
        content_layout = BoxLayout(orientation='vertical', size_hint_y=0.8)

        # Tab buttons
        tab_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=dp(5))
        overview_btn = Button(text='Overview', background_color=(0.4, 0.6, 0.8, 1))
        overview_btn.bind(on_press=self.show_overview)
        chat_btn = Button(text='Chat', background_color=(0.6, 0.8, 0.4, 1))
        chat_btn.bind(on_press=self.show_chat)
        members_btn = Button(text='Members', background_color=(0.8, 0.6, 0.4, 1))
        members_btn.bind(on_press=self.show_members)
        leaderboards_btn = Button(text='Leaderboards', background_color=(0.6, 0.4, 0.8, 1))
        leaderboards_btn.bind(on_press=self.show_leaderboards)

        tab_layout.add_widget(overview_btn)
        tab_layout.add_widget(chat_btn)
        tab_layout.add_widget(members_btn)
        tab_layout.add_widget(leaderboards_btn)
        content_layout.add_widget(tab_layout)

        # Content area
        self.content_area = BoxLayout(orientation='vertical')
        content_layout.add_widget(self.content_area)

        main_layout.add_widget(content_layout)

        # Back button
        back_btn = Button(text='BACK TO CAMP', size_hint_y=0.08)
        back_btn.bind(on_press=self.return_to_camp)
        main_layout.add_widget(back_btn)

        self.add_widget(main_layout)

        # Show overview by default
        self.show_overview()

    def create_header(self) -> BoxLayout:
        """Create header showing clan status"""
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))

        if self.current_clan:
            clan_name = f"[{self.current_clan.tag}] {self.current_clan.name}"
            member_count = len(self.current_clan.member_ids)
            status_text = f"Clan: {clan_name} ({member_count}/50 members)"
        else:
            status_text = "Not in a clan"

        status_label = Label(text=status_text, halign='left', valign='middle', text_size=(self.width, None))
        header.add_widget(status_label)

        return header

    def show_overview(self, instance=None):
        """Show clan overview tab"""
        self.content_area.clear_widgets()

        if self.current_clan:
            # Clan overview
            overview = BoxLayout(orientation='vertical', spacing=dp(10))

            info_label = Label(
                text=f"Welcome to {self.current_clan.name}!\n\n"
                     f"Tag: {self.current_clan.tag}\n"
                     f"Members: {len(self.current_clan.member_ids)}/50\n"
                     f"Leader: {self.current_clan.leader_id[:8]}...",
                halign='center', valign='middle'
            )
            overview.add_widget(info_label)

            # Joint raid button
            raid_btn = Button(text='CALL CLAN FOR RAID HELP', size_hint_y=0.3,
                             background_color=(0.8, 0.3, 0.3, 1))
            raid_btn.bind(on_press=self.call_clan_help)
            overview.add_widget(raid_btn)

            # Leave clan button (if not leader)
            if self.current_clan.leader_id != self.player_id:
                leave_btn = Button(text='LEAVE CLAN', background_color=(0.8, 0.4, 0.4, 1))
                leave_btn.bind(on_press=self.leave_clan)
                overview.add_widget(leave_btn)

            self.content_area.add_widget(overview)
        else:
            # Not in clan - show create/join options
            overview = BoxLayout(orientation='vertical', spacing=dp(10))

            title = Label(text='Join the Desert Brotherhood!', font_size=dp(20), bold=True)
            overview.add_widget(title)

            # Create clan section
            create_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=0.4)
            create_title = Label(text='Create New Clan', font_size=dp(16), bold=True)

            name_input = TextInput(hint_text='Clan Name', multiline=False, size_hint_y=0.3)
            tag_input = TextInput(hint_text='Clan Tag (3-5 chars)', multiline=False, size_hint_y=0.3)
            create_btn = Button(text='CREATE CLAN (500 Gems)', background_color=(0.4, 0.8, 0.4, 1))
            create_btn.bind(on_press=lambda x: self.create_clan(name_input.text, tag_input.text))

            create_layout.add_widget(create_title)
            create_layout.add_widget(name_input)
            create_layout.add_widget(tag_input)
            create_layout.add_widget(create_btn)
            overview.add_widget(create_layout)

            # Join clan section
            join_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=0.4)
            join_title = Label(text='Join Existing Clan', font_size=dp(16), bold=True)

            search_input = TextInput(hint_text='Clan Tag', multiline=False, size_hint_y=0.3)
            join_btn = Button(text='SEARCH & JOIN', background_color=(0.4, 0.6, 0.8, 1))
            join_btn.bind(on_press=lambda x: self.search_clan(search_input.text))

            join_layout.add_widget(join_title)
            join_layout.add_widget(search_input)
            join_layout.add_widget(join_btn)
            overview.add_widget(join_layout)

            self.content_area.add_widget(overview)

    def show_chat(self, instance=None):
        """Show clan chat tab"""
        self.content_area.clear_widgets()

        if not self.current_clan:
            no_clan_label = Label(text='Join a clan to access chat!')
            self.content_area.add_widget(no_clan_label)
            return

        chat_layout = BoxLayout(orientation='vertical', spacing=dp(5))

        # Chat messages area
        chat_scroll = ScrollView(size_hint_y=0.7)
        chat_container = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        chat_container.bind(minimum_height=chat_container.setter('height'))

        for message in self.chat_messages[-20:]:  # Show last 20 messages
            timestamp = time.strftime('%H:%M', time.localtime(message['timestamp']))
            sender = message['sender'][:8] + '...' if len(message['sender']) > 8 else message['sender']
            msg_label = Label(
                text=f'[{timestamp}] {sender}: {message["text"]}',
                halign='left', valign='top', text_size=(self.width * 0.9, None),
                size_hint_y=None, height=dp(30)
            )
            chat_container.add_widget(msg_label)

        chat_scroll.add_widget(chat_container)
        chat_layout.add_widget(chat_scroll)

        # Message input
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(5))
        message_input = TextInput(hint_text='Type message...', multiline=False)
        send_btn = Button(text='SEND', size_hint_x=0.3)
        send_btn.bind(on_press=lambda x: self.send_chat_message(message_input))

        input_layout.add_widget(message_input)
        input_layout.add_widget(send_btn)
        chat_layout.add_widget(input_layout)

        self.content_area.add_widget(chat_layout)

    def show_members(self, instance=None):
        """Show clan members tab"""
        self.content_area.clear_widgets()

        if not self.current_clan:
            no_clan_label = Label(text='Join a clan to see members!')
            self.content_area.add_widget(no_clan_label)
            return

        members_layout = BoxLayout(orientation='vertical', spacing=dp(5))

        title = Label(text=f'{self.current_clan.name} Members', font_size=dp(18), bold=True)
        members_layout.add_widget(title)

        # Member list
        scroll = ScrollView()
        member_container = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        member_container.bind(minimum_height=member_container.setter('height'))

        for member_id in self.current_clan.member_ids:
            is_online = member_id == self.player_id  # Simplified - only show current player as online
            online_status = "[ONLINE]" if is_online else "[OFFLINE]"

            member_btn = Button(
                text=f'{member_id[:12]}... {online_status}',
                size_hint_y=None, height=dp(40),
                background_color=(0.2, 0.8, 0.2, 1) if is_online else (0.5, 0.5, 0.5, 1)
            )
            member_container.add_widget(member_btn)

        scroll.add_widget(member_container)
        members_layout.add_widget(scroll)

        self.content_area.add_widget(members_layout)

    def show_leaderboards(self, instance=None):
        """Show clan and player leaderboards"""
        self.content_area.clear_widgets()

        leaderboards_layout = BoxLayout(orientation='vertical', spacing=dp(10))

        title = Label(text='LEADERBOARDS', font_size=dp(20), bold=True)
        leaderboards_layout.add_widget(title)

        # Player leaderboard
        player_title = Label(text='Top Players (Power Level)', font_size=dp(16), bold=True)
        leaderboards_layout.add_widget(player_title)

        player_scroll = ScrollView(size_hint_y=0.3)
        player_container = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None)
        player_container.bind(minimum_height=player_container.setter('height'))

        # Mock leaderboard data
        mock_players = [
            ("Player_123456", 15420),
            ("Desert_Warrior", 14850),
            ("Sand_Viper", 13990),
            ("Oasis_Lord", 12750),
            ("Camel_Master", 11500)
        ]

        for i, (name, power) in enumerate(mock_players, 1):
            player_label = Label(
                text=f'{i}. {name} - {power} power',
                size_hint_y=None, height=dp(25)
            )
            player_container.add_widget(player_label)

        player_scroll.add_widget(player_container)
        leaderboards_layout.add_widget(player_scroll)

        # Clan leaderboard
        clan_title = Label(text='Top Clans', font_size=dp(16), bold=True)
        leaderboards_layout.add_widget(clan_title)

        clan_scroll = ScrollView(size_hint_y=0.3)
        clan_container = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None)
        clan_container.bind(minimum_height=clan_container.setter('height'))

        # Mock clan leaderboard
        mock_clans = [
            ("Sandstorm", 125000),
            ("Desert Foxes", 118900),
            ("Oasis Raiders", 112300),
            ("Dune Warriors", 108700),
            ("Camel Lords", 98700)
        ]

        for i, (name, power) in enumerate(mock_clans, 1):
            clan_label = Label(
                text=f'{i}. {name} - {power} power',
                size_hint_y=None, height=dp(25)
            )
            clan_container.add_widget(clan_label)

        clan_scroll.add_widget(clan_container)
        leaderboards_layout.add_widget(clan_scroll)

        self.content_area.add_widget(leaderboards_layout)

    def create_clan(self, name: str, tag: str):
        """Create a new clan"""
        if not name or not tag:
            print("Clan name and tag required")
            return

        if len(tag) < 3 or len(tag) > 5:
            print("Clan tag must be 3-5 characters")
            return

        # Check if player has enough gems
        from monetization import spend_gems
        if not spend_gems(500):
            print("Not enough gems to create clan")
            return

        clan_id = str(uuid.uuid4())
        new_clan = Clan(clan_id, name, tag.upper(), self.player_id)

        # Save to Firebase
        def save_clan():
            db = get_database()
            if db:
                db.child(DB_PATHS["clans"]).child(clan_id).set(new_clan.to_dict())
                # Update player profile
                db.child(DB_PATHS["players"]).child(self.player_id).update({
                    "clan_id": clan_id,
                    "clan_tag": tag.upper()
                })
            return new_clan

        self.current_clan = safe_firebase_operation(save_clan, new_clan)

        # Update local game data
        app = self.get_app()
        app.game_data.clan_id = clan_id
        app.game_data.save_game()

        print(f"Created clan: {name} [{tag}]")
        self.setup_ui()  # Refresh UI

    def search_clan(self, tag: str):
        """Search for and join a clan by tag"""
        if not tag:
            return

        def find_clan():
            db = get_database()
            if db:
                # Search clans by tag (simplified - in real app would need indexing)
                clans = db.child(DB_PATHS["clans"]).get().val()
                if clans:
                    for clan_id, clan_data in clans.items():
                        if clan_data.get("tag", "").upper() == tag.upper():
                            return Clan.from_dict(clan_data)
            return None

        found_clan = safe_firebase_operation(find_clan)

        if found_clan and len(found_clan.member_ids) < 50:
            # Join clan
            found_clan.member_ids.append(self.player_id)

            def join_clan():
                db = get_database()
                if db:
                    db.child(DB_PATHS["clans"]).child(found_clan.id).update({
                        "member_ids": found_clan.member_ids
                    })
                    # Update player profile
                    db.child(DB_PATHS["players"]).child(self.player_id).update({
                        "clan_id": found_clan.id,
                        "clan_tag": found_clan.tag
                    })
                return found_clan

            self.current_clan = safe_firebase_operation(join_clan, found_clan)

            # Update local game data
            app = self.get_app()
            app.game_data.clan_id = found_clan.id
            app.game_data.save_game()

            print(f"Joined clan: {found_clan.name}")
            self.setup_ui()  # Refresh UI
        else:
            print("Clan not found or full")

    def leave_clan(self, instance=None):
        """Leave current clan"""
        if not self.current_clan:
            return

        # Remove from clan
        if self.player_id in self.current_clan.member_ids:
            self.current_clan.member_ids.remove(self.player_id)

        def update_clan():
            db = get_database()
            if db:
                if len(self.current_clan.member_ids) == 0:
                    # Delete empty clan
                    db.child(DB_PATHS["clans"]).child(self.current_clan.id).remove()
                else:
                    db.child(DB_PATHS["clans"]).child(self.current_clan.id).update({
                        "member_ids": self.current_clan.member_ids
                    })
                # Update player profile
                db.child(DB_PATHS["players"]).child(self.player_id).update({
                    "clan_id": None,
                    "clan_tag": None
                })
            return None

        safe_firebase_operation(update_clan)

        # Update local game data
        app = self.get_app()
        app.game_data.clan_id = None
        app.game_data.save_game()

        self.current_clan = None
        print("Left clan")
        self.setup_ui()  # Refresh UI

    def call_clan_help(self, instance=None):
        """Call clan members for help with raid"""
        if not self.current_clan:
            return

        print(f"Calling {len(self.current_clan.member_ids) - 1} clan members for help!")

        # In a real implementation, this would send push notifications
        # For now, just show an alert
        app = self.get_app()
        # You could add a notification system here

    def send_chat_message(self, message_input):
        """Send a chat message"""
        if not self.current_clan or not message_input.text.strip():
            return

        message = {
            "sender": self.player_id,
            "text": message_input.text.strip(),
            "timestamp": time.time()
        }

        self.chat_messages.append(message)
        message_input.text = ""

        # Save to Firebase
        def save_message():
            db = get_database()
            if db:
                db.child(DB_PATHS["clans"]).child(self.current_clan.id).child("chat_messages").push(message)

        safe_firebase_operation(save_message)

        # Refresh chat display
        self.show_chat()

    def load_clan_data(self):
        """Load clan data from Firebase"""
        app = self.get_app()

        if app.game_data.clan_id:
            def load_clan():
                db = get_database()
                if db:
                    clan_data = db.child(DB_PATHS["clans"]).child(app.game_data.clan_id).get().val()
                    if clan_data:
                        clan = Clan.from_dict(clan_data)
                        self.chat_messages = clan.chat_messages
                        return clan
                return None

            self.current_clan = safe_firebase_operation(load_clan)

    def start_chat_updates(self):
        """Start periodic chat updates"""
        if self.chat_update_event:
            self.chat_update_event.cancel()

        self.chat_update_event = Clock.schedule_interval(self.update_chat, 5)  # Update every 5 seconds

    def update_chat(self, dt):
        """Update chat messages from Firebase"""
        if self.current_clan:
            def get_messages():
                db = get_database()
                if db:
                    messages = db.child(DB_PATHS["clans"]).child(self.current_clan.id).child("chat_messages").get().val()
                    if messages:
                        return list(messages.values())
                return []

            new_messages = safe_firebase_operation(get_messages, [])
            if len(new_messages) > len(self.chat_messages):
                self.chat_messages = new_messages
                # Could update chat display here if currently viewing chat

    def return_to_camp(self, instance=None):
        """Return to camp screen"""
        self.manager.current = 'camp'

    def get_app(self):
        """Get the running Kivy app"""
        return App.get_running_app()
