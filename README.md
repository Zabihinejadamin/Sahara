# Sahara Raiders

A 2D top-down 4X survival strategy game set in a procedural Sahara desert with raiding mechanics. Built with pure Python and Kivy for cross-platform mobile gaming.

## Features

- **Hex-grid desert map** with procedural generation
- **Scouting mechanics** with spy camels that reveal hidden caravans
- **Raid battles** with auto-resolution based on squad size and terrain
- **Resource management** (Water, Salt, Gold, Spices) with survival timers
- **Camp upgrades** and military recruitment
- **Save/load system** with JSON persistence
- **Mobile-optimized** touch controls and 60 FPS gameplay

## Project Structure

```
sahara-raiders/
├── main.py                 # Entry point with Kivy App and ScreenManager
├── game_data.py           # Global game state management
├── caravan.py             # Caravan entity classes
├── utils.py               # Hex math, procedural generation, pathfinding
├── screens/               # Screen modules
│   ├── map_screen.py/.kv  # Main hex-grid map with scouting
│   ├── camp_screen.py/.kv # Base management and upgrades
│   └── raid_screen.py/.kv # Battle system and loot
├── assets/                # Game assets (placeholders)
│   ├── icon.png           # App icon
│   ├── camel.png          # Spy/scouting icon
│   ├── caravan.png        # Caravan sprite
│   └── README.md          # Asset requirements
├── buildozer.spec         # Android build configuration
└── requirements.txt       # Python dependencies
```

## Getting Started

### Desktop Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Mobile Development

```bash
# Install buildozer
pip install buildozer

# Build for Android
buildozer android debug
```

## Gameplay

1. **Map Screen**: Explore the desert hex-grid, scout for caravans, tap to raid
2. **Camp Screen**: Manage resources, upgrade facilities, recruit raiders
3. **Raid Screen**: Assemble squads, execute auto-resolved battles, collect loot

## Technical Details

- **Framework**: Kivy 2.3.0 for cross-platform GUI
- **Architecture**: ScreenManager with separate modules for game logic
- **Rendering**: Custom Canvas drawing for hex-grid and game entities
- **Persistence**: JSON-based save system
- **Performance**: 60 FPS target with optimized mobile rendering

## Asset Requirements

Replace placeholder files in `assets/` with actual game graphics:
- Desert hex tiles from Kenney.nl or itch.io
- Camel/caravan sprites
- UI elements optimized for touch

## Controls

- **Touch/Click**: Navigate map, select targets, interact with UI
- **Portrait/Landscape**: Automatic orientation support
- **One-handed**: Mobile-optimized button placement

## Development Notes

- Pure Python implementation with no external game engines
- Modular design for easy feature expansion
- Type hints and comments for maintainability
- Mobile-first design with desktop compatibility
