"""
File Opener Utility

This module provides cross-platform utilities to:
- Open files using the system's default application
- Open folders in the system file manager
- Retrieve basic file metadata information

Supported platforms:
- Windows
- macOS
- Linux
"""

import os            # Provides file system utilities
import sys           # System-specific parameters (reserved for future use)
import subprocess    # Executes system-level commands
import platform      # Detects operating system


def open_file(file_path):
    """
    Open a file using the default system application.

    This function detects the operating system and uses the
    appropriate command to launch the file.

    Args:
        file_path (str): Path to the file to open

    Returns:
        bool: True if successful, False otherwise
    """

    # ---------------------------------------------------------
    # Validate file existence before attempting to open
    # ---------------------------------------------------------
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        # Detect current operating system
        system = platform.system()
        
        # -----------------------------------------------------
        # OS-Specific Handling
        # -----------------------------------------------------
        if system == "Windows":
            # Native Windows method
            os.startfile(file_path)

        elif system == "Darwin":  # macOS
            # macOS uses the "open" command
            subprocess.run(["open", file_path])

        elif system == "Linux":
            # Linux typically uses xdg-open
            subprocess.run(["xdg-open", file_path])

        else:
            # Unsupported or unknown OS
            print(f"Unsupported operating system: {system}")
            return False
        
        print(f"Opened file: {file_path}")
        return True
        
    except Exception as e:
        # Catch unexpected runtime errors
        print(f"Error opening file {file_path}: {e}")
        return False


def open_folder(folder_path):
    """
    Open a folder in the default system file manager.

    Args:
        folder_path (str): Path to the folder to open

    Returns:
        bool: True if successful, False otherwise
    """

    # ---------------------------------------------------------
    # Validate folder existence
    # ---------------------------------------------------------
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return False
    
    try:
        # Detect operating system
        system = platform.system()
        
        # -----------------------------------------------------
        # OS-Specific Folder Opening Logic
        # -----------------------------------------------------
        if system == "Windows":
            # Windows File Explorer
            subprocess.run(["explorer", folder_path])

        elif system == "Darwin":  # macOS
            subprocess.run(["open", folder_path])

        elif system == "Linux":
            subprocess.run(["xdg-open", folder_path])

        else:
            print(f"Unsupported operating system: {system}")
            return False
        
        print(f"Opened folder: {folder_path}")
        return True
        
    except Exception as e:
        print(f"Error opening folder {folder_path}: {e}")
        return False


def get_file_info(file_path):
    """
    Retrieve basic metadata about a file or directory.

    Information returned includes:
    - File size (in bytes)
    - Last modified timestamp
    - Creation timestamp
    - Whether it is a file or directory
    - File extension
    - Base filename

    Args:
        file_path (str): Path to the file

    Returns:
        dict | None:
            Dictionary containing file metadata if successful,
            None if the file does not exist or an error occurs.
    """

    # ---------------------------------------------------------
    # Ensure the path exists before retrieving metadata
    # ---------------------------------------------------------
    if not os.path.exists(file_path):
        return None
    
    try:
        # Retrieve file statistics
        stat = os.stat(file_path)

        # Return structured file metadata
        return {
            'size': stat.st_size,                        # File size in bytes
            'modified': stat.st_mtime,                   # Last modified timestamp
            'created': stat.st_ctime,                    # Creation timestamp
            'is_file': os.path.isfile(file_path),        # True if regular file
            'is_directory': os.path.isdir(file_path),    # True if directory
            'extension': os.path.splitext(file_path)[1], # File extension
            'basename': os.path.basename(file_path)      # Filename without path
        }

    except Exception as e:
        print(f"Error getting file info for {file_path}: {e}")
        return None