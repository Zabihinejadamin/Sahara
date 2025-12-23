"""
Firebase configuration for Sahara Raiders
Contains placeholder config - replace with real Firebase project details
"""
import os
from typing import Dict, Any

# Firebase Realtime Database configuration
# Replace these values with your actual Firebase project config
FIREBASE_CONFIG = {
    "apiKey": "your-api-key-here",
    "authDomain": "sahara-raiders.firebaseapp.com",
    "databaseURL": "https://sahara-raiders-default-rtdb.firebaseio.com/",
    "projectId": "sahara-raiders",
    "storageBucket": "sahara-raiders.appspot.com",
    "messagingSenderId": "123456789",
    "appId": "1:123456789:web:abcdef123456"
}

# Database paths
DB_PATHS = {
    "players": "players",
    "clans": "clans",
    "leaderboards": "leaderboards",
    "events": "events",
    "world_boss": "world_boss"
}

# Firebase initialization flag
firebase_initialized = False
firebase_db = None

def initialize_firebase():
    """
    Initialize Firebase connection
    Returns True if successful, False if offline/fallback mode
    """
    global firebase_initialized, firebase_db

    try:
        import pyrebase

        firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        firebase_db = firebase.database()
        firebase_initialized = True
        print("Firebase initialized successfully")
        return True

    except ImportError:
        print("Pyrebase not installed - running in offline mode")
        firebase_initialized = False
        return False

    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        print("Running in offline mode")
        firebase_initialized = False
        return False

def is_online() -> bool:
    """Check if Firebase is connected"""
    return firebase_initialized

def get_database():
    """Get Firebase database reference"""
    return firebase_db if firebase_initialized else None

def safe_firebase_operation(operation_func, fallback_result=None):
    """
    Safely execute Firebase operations with offline fallback

    Args:
        operation_func: Function that performs Firebase operation
        fallback_result: Result to return if offline

    Returns:
        Result of operation or fallback
    """
    if not is_online():
        return fallback_result

    try:
        return operation_func()
    except Exception as e:
        print(f"Firebase operation failed: {e}")
        return fallback_result
