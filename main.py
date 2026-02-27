"""
Offline Document Finder (ODF)
A smart AI-powered desktop tool for semantic search of local documents.

Main entry point for the application.
"""

import os
import sys
import threading
from ui.search_window import SearchWindow  # Main UI window for search functionality

import keyboard  # Used for registering global hotkeys


def main():
    """Main entry point for the ODF application."""
    
    # Application startup message
    print("Starting Offline Document Finder (ODF)...")
    
    # ------------------------------------------------------------
    # Ensure the 'models' directory exists
    # This directory is used to store AI/embedding models locally
    # ------------------------------------------------------------
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    # ------------------------------------------------------------
    # Initialize the main search window (GUI)
    # ------------------------------------------------------------
    search_window = SearchWindow()
    
    # ------------------------------------------------------------
    # Bind Global Hotkey (Ctrl + K)
    # Allows toggling the search window from anywhere
    # ------------------------------------------------------------
    try:
        keyboard.add_hotkey('ctrl+k', search_window.toggle_window)
        print("✅ Global Hotkey Active: Press 'Ctrl + K' to toggle search")
    except Exception as e:
        # Hotkey registration may fail if not run as administrator
        # or if the OS restricts global keyboard hooks
        print(f"⚠️ Could not bind hotkey: {e}")

    # ------------------------------------------------------------
    # Display usage instructions in terminal
    # ------------------------------------------------------------
    print("\n" + "="*60)
    print("🔍 Offline Document Finder (ODF) is ready!")
    print("="*60)
    print("📂 How to use:")
    print("   1. Press 'Ctrl + K' to toggle the search window")
    print("   2. Add documents using the 'Index Folder' button")
    print("   3. Search your documents with AI-powered semantic search")
    print("\n💡 Tip: You can always restart by running: python main.py")
    print("="*60)
    
    # ------------------------------------------------------------
    # Keep the main thread alive and start the GUI event loop
    # ------------------------------------------------------------
    try:
        # Show the search window initially when the app starts
        search_window.show_window()
        
        # Start the Tkinter main event loop
        # This keeps the application running and responsive
        search_window.root.mainloop()
        
    except KeyboardInterrupt:
        # Graceful shutdown when user presses Ctrl+C in terminal
        print("\n👋 Shutting down ODF...")
        try:
            # Remove all keyboard hooks before exiting
            keyboard.unhook_all()
        except:
            pass
        sys.exit(0)


# ------------------------------------------------------------
# Run the application only if this file is executed directly
# (Not when imported as a module)
# ------------------------------------------------------------
if __name__ == "__main__":
    main()