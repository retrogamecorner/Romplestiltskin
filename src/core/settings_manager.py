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
            "extra_folder_name": "_extra",
            "broken_folder_name": "broken",
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
            },
            "system_filter_settings": {},
            "ignored_crcs": []  # New setting for ignored CRCs
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
            # Ensure the config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_system_filter_settings(self, system_id: str) -> dict:
        """Get filter settings for a specific system."""
        system_filters = self.settings.get("system_filter_settings", {})
        if str(system_id) in system_filters:
            return system_filters[str(system_id)]
        else:
            # Return default filter settings if no system-specific settings exist
            return self.settings

    def get_ignored_crcs(self, system_id: Optional[str] = None) -> list:
        """Get the list of ignored CRCs, optionally for a specific system."""
        if system_id:
            # This allows for system-specific ignore lists in the future if needed
            # For now, we'll use a global list but structure allows extension
            system_ignores = self.get(f"system_ignored_crcs.{system_id}", [])
            if system_ignores: # If system specific list exists and is not empty
                return system_ignores
        return self.get("ignored_crcs", [])

    def set_ignored_crcs(self, crc_list: list, system_id: Optional[str] = None) -> None:
        """Set the list of ignored CRCs, optionally for a specific system."""
        if system_id:
            self.set(f"system_ignored_crcs.{system_id}", crc_list)
        else:
            self.set("ignored_crcs", crc_list)
        self.save_settings()  # Save settings after modification.get("filter_settings", {}).copy()
    
    def set_system_filter_settings(self, system_id: str, filter_settings: dict) -> None:
        """Set filter settings for a specific system."""
        if "system_filter_settings" not in self.settings:
            self.settings["system_filter_settings"] = {}
        
        self.settings["system_filter_settings"][str(system_id)] = filter_settings.copy()
        self.save_settings()
    
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