"""
Global Shortcut Registration

This module:
- Registers global keyboard shortcuts
- Manages lifecycle of shortcut listeners
- Provides safe wrapper functions for application-level usage
- Supports registering/unregistering shortcuts dynamically

Uses the `keyboard` library for system-wide hotkey detection.
"""

import keyboard     # Library for global keyboard hook
import threading    # Used to run listener in background thread
import time         # Keeps listener thread alive with sleep loop


class ShortcutManager:
    """
    Core class responsible for managing global shortcuts.

    Responsibilities:
    - Register new shortcuts
    - Remove existing shortcuts
    - Maintain active shortcut registry
    - Control background listener lifecycle
    """

    def __init__(self):
        """Initialize the shortcut manager."""
        self.shortcuts = {}          # Dictionary: hotkey -> keyboard handler ID
        self.is_running = False      # Listener state flag
        self.listener_thread = None  # Background listener thread reference
    
    def register_shortcut(self, hotkey, callback):
        """
        Register a global shortcut.

        Args:
            hotkey (str): Hotkey combination (e.g., 'ctrl+alt+f')
            callback (function): Function to call when shortcut is pressed

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # -------------------------------------------------
            # Remove existing shortcut if already registered
            # Prevents duplicate hotkey bindings
            # -------------------------------------------------
            if hotkey in self.shortcuts:
                keyboard.remove_hotkey(self.shortcuts[hotkey])
            
            # -------------------------------------------------
            # Register new global hotkey
            # Store handler reference for future removal
            # -------------------------------------------------
            self.shortcuts[hotkey] = keyboard.add_hotkey(hotkey, callback)

            print(f"Registered global shortcut: {hotkey}")
            return True

        except Exception as e:
            print(f"Error registering shortcut {hotkey}: {e}")
            return False
    
    def unregister_shortcut(self, hotkey):
        """
        Unregister a global shortcut.

        Args:
            hotkey (str): Hotkey combination to unregister

        Returns:
            bool: True if removed, False otherwise
        """
        try:
            if hotkey in self.shortcuts:
                keyboard.remove_hotkey(self.shortcuts[hotkey])
                del self.shortcuts[hotkey]
                print(f"Unregistered shortcut: {hotkey}")
                return True
            return False

        except Exception as e:
            print(f"Error unregistering shortcut {hotkey}: {e}")
            return False
    
    def start_listener(self):
        """
        Start the keyboard listener in a background daemon thread.

        The keyboard library internally hooks events, but we keep
        a lightweight thread alive to maintain lifecycle control.
        """
        if self.is_running:
            return
        
        self.is_running = True
        
        def listener():
            """
            Background loop to keep listener active.
            Runs until `is_running` is set to False.
            """
            try:
                while self.is_running:
                    time.sleep(0.1)  # Small delay to reduce CPU usage
            except Exception as e:
                print(f"Error in shortcut listener: {e}")
        
        # Create daemon thread (auto-stops when main program exits)
        self.listener_thread = threading.Thread(target=listener, daemon=True)
        self.listener_thread.start()
    
    def stop_listener(self):
        """
        Stop the keyboard listener and remove all shortcuts.
        """
        self.is_running = False
        
        # -------------------------------------------------
        # Safely unregister all currently active shortcuts
        # -------------------------------------------------
        for hotkey in list(self.shortcuts.keys()):
            self.unregister_shortcut(hotkey)
    
    def list_shortcuts(self):
        """
        Return list of currently registered hotkeys.
        """
        return list(self.shortcuts.keys())


# ---------------------------------------------------------
# Global Shortcut Manager Instance (Singleton Style)
# ---------------------------------------------------------
_shortcut_manager = ShortcutManager()


def register_global_shortcut(callback, hotkey='ctrl+alt+f'):
    """
    Register the default global shortcut for the application.

    This function:
    - Wraps callback in safe error handler
    - Registers shortcut
    - Starts listener automatically

    Args:
        callback (function): Function to call when shortcut is pressed
        hotkey (str): Hotkey combination (default: 'ctrl+alt+f')

    Returns:
        bool: True if successful, False otherwise
    """

    def safe_callback():
        """
        Wrapper function to prevent application crash
        if callback throws an exception.
        """
        try:
            callback()
        except Exception as e:
            print(f"Error in shortcut callback: {e}")
    
    success = _shortcut_manager.register_shortcut(hotkey, safe_callback)

    if success:
        _shortcut_manager.start_listener()
        print(f"Global shortcut {hotkey} registered successfully")
        print("Press the shortcut to open the search window")
    else:
        print(f"Failed to register global shortcut {hotkey}")
        print("You may need to run the application as administrator")
    
    return success


def unregister_global_shortcut(hotkey='ctrl+alt+f'):
    """
    Unregister the global shortcut.

    Args:
        hotkey (str): Hotkey combination to unregister
    """
    return _shortcut_manager.unregister_shortcut(hotkey)


def stop_all_shortcuts():
    """
    Stop all keyboard shortcuts and terminate listener.
    """
    _shortcut_manager.stop_listener()


def list_active_shortcuts():
    """
    Retrieve list of active shortcuts currently registered.
    """
    return _shortcut_manager.list_shortcuts()


# ---------------------------------------------------------
# Safe Registration Wrapper (Fallback Option)
# ---------------------------------------------------------
def register_global_shortcut_safe(callback, hotkey='ctrl+alt+f'):
    """
    Safely register global shortcut with fallback handling.

    This version prevents application crash if:
    - System blocks global hooks
    - Insufficient permissions
    - Keyboard library fails

    Args:
        callback (function): Function to call when shortcut is pressed
        hotkey (str): Hotkey combination

    Returns:
        bool: True if registration successful, False otherwise
    """
    try:
        return register_global_shortcut(callback, hotkey)
    except Exception as e:
        print(f"Could not register global shortcut: {e}")
        print("Global shortcuts may not be available on this system")
        print("You can still use the application by running main.py directly")
        return False