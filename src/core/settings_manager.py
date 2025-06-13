#!/usr/bin/env python3
"""
Settings Manager for Romplestiltskin

Handles loading and saving user settings from/to JSON configuration file.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class SettingsManager:
    """Manages application settings and configuration."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize settings manager.
        
        Args:
            config_file: Path to configuration file. If None, uses default location.
        """
        if config_file is None:
            # Use application data directory
            app_data = Path.home() / ".romplestiltskin"
            app_data.mkdir(exist_ok=True)
            self.config_file = app_data / "config.json"
        else:
            self.config_file = Path(config_file)
            
        self.settings = self._load_default_settings()
        self.load_settings()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings.
        
        Returns:
            Dictionary containing default settings.
        """
        return {
            "dat_folder_path": "",
            "database_path": str(Path.home() / ".romplestiltskin" / "romplestiltskin.db"),
            "rom_folders": [],
            "system_rom_folders": {},  # Store ROM folders per system
            "extra_folder_name": "_extra",
            "broken_folder_name": "_broken",
            "filtered_folder_name": "_filtered",
            "multi_disc_folder_name": "_multi",
            "region_priority": [
                "USA", "Japan", "Europe", "World",
                # EU Countries
                "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
                "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
                "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
                "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
                "Slovenia", "Spain", "Sweden",
                # Other priority countries
                "Canada", "Australia"
            ],
            "language_priority": ["En", "Es", "Fr", "De", "It", "Pt", "Ja"],
            "auto_create_folders": True,
            "backup_before_operations": False,  # Changed default to False
            "duplicate_handling": "Keep All",  # New setting with default "Keep All"
            "chunk_size_mb": 64,  # For CRC calculation
            "max_threads": 4,
            "window_geometry": None,
            "window_state": None,
            "last_selected_system": None,
            "filter_settings": {
                "show_beta": True,
                "show_demo": True,
                "show_proto": True,
                "show_unlicensed": True,
                "show_unofficial_translation": True,
                "show_modified_release": True,
                "show_overdump": True,
                "preferred_languages": ["En"],
                "preferred_regions": ["USA", "Europe", "Japan", "World"]
            }
        }
    
    def load_settings(self) -> None:
        """Load settings from configuration file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to handle new settings
                    self.settings.update(loaded_settings)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load settings from {self.config_file}: {e}")
            print("Using default settings.")
    
    def save_settings(self) -> None:
        """Save current settings to configuration file."""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not save settings to {self.config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value.
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            value: Value to set
        """
        keys = key.split('.')
        setting_dict = self.settings
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in setting_dict:
                setting_dict[k] = {}
            setting_dict = setting_dict[k]
        
        # Set the final value
        setting_dict[keys[-1]] = value
    
    def get_dat_folder_path(self) -> str:
        """Get DAT folder path."""
        return self.get("dat_folder_path", "")
    
    def set_dat_folder_path(self, path: str) -> None:
        """Set DAT folder path."""
        self.set("dat_folder_path", path)
    
    def get_database_path(self) -> str:
        """Get database file path."""
        return self.get("database_path")
    
    def set_database_path(self, path: str) -> None:
        """Set database file path."""
        self.set("database_path", path)
    
    def get_rom_folders(self) -> list:
        """Get list of ROM folder paths (legacy method)."""
        return self.get("rom_folders", [])
    
    def add_rom_folder(self, path: str) -> None:
        """Add a ROM folder path (legacy method)."""
        folders = self.get_rom_folders()
        if path not in folders:
            folders.append(path)
            self.set("rom_folders", folders)
    
    def remove_rom_folder(self, path: str) -> None:
        """Remove a ROM folder path (legacy method)."""
        folders = self.get_rom_folders()
        if path in folders:
            folders.remove(path)
            self.set("rom_folders", folders)
            
    def get_system_rom_folders(self, system_id: str) -> list:
        """Get list of ROM folder paths for a specific system.
        
        Args:
            system_id: The system ID to get ROM folders for
            
        Returns:
            List of ROM folder paths for the system
        """
        system_folders = self.get("system_rom_folders", {})
        return system_folders.get(system_id, [])
    
    def set_system_rom_folders(self, system_id: str, folders: list) -> None:
        """Set ROM folder paths for a specific system.
        
        Args:
            system_id: The system ID to set ROM folders for
            folders: List of ROM folder paths
        """
        system_folders = self.get("system_rom_folders", {})
        system_folders[system_id] = folders
        self.set("system_rom_folders", system_folders)
    
    def add_system_rom_folder(self, system_id: str, path: str) -> None:
        """Add a ROM folder path for a specific system.
        
        Args:
            system_id: The system ID to add a ROM folder for
            path: ROM folder path to add
        """
        folders = self.get_system_rom_folders(system_id)
        if path not in folders:
            folders.append(path)
            self.set_system_rom_folders(system_id, folders)
    
    def remove_system_rom_folder(self, system_id: str, path: str) -> None:
        """Remove a ROM folder path for a specific system.
        
        Args:
            system_id: The system ID to remove a ROM folder from
            path: ROM folder path to remove
        """
        folders = self.get_system_rom_folders(system_id)
        if path in folders:
            folders.remove(path)
            self.set_system_rom_folders(system_id, folders)
    
    def get_region_priority(self) -> list:
        """Get region priority list."""
        return self.get("region_priority", ["USA", "Europe", "Japan", "World"])
    
    def set_region_priority(self, priority_list: list) -> None:
        """Set region priority list."""
        self.set("region_priority", priority_list)
    
    def get_chunk_size_bytes(self) -> int:
        """Get chunk size for file operations in bytes."""
        return self.get("chunk_size_mb", 64) * 1024 * 1024
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as a dictionary.
        
        Returns:
            Dictionary containing all current settings.
        """
        return self.settings