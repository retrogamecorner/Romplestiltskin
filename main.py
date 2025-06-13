#!/usr/bin/env python3
"""
Romplestiltskin - ROM Collection Management and Verification Tool

Main entry point for the application.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDir
from ui.main_window import MainWindow
from core.settings_manager import SettingsManager
from core.db_manager import DatabaseManager

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Romplestiltskin")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Romplestiltskin")
    
    # Initialize core components
    settings_manager = SettingsManager()
    db_manager = DatabaseManager(settings_manager.get_database_path())
    
    # Create main window and apply theme globally
    main_window = MainWindow(settings_manager, db_manager)
    
    # Apply the theme to the entire application
    stylesheet = main_window.get_stylesheet()
    app.setStyleSheet(stylesheet)
    
    main_window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())