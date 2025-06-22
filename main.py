#!/usr/bin/env python3
"""
Romplestiltskin - ROM Collection Management and Verification Tool

Main entry point for the application.
"""

import sys
import os
import logging
from pathlib import Path

# Configure logging only once
root_logger = logging.getLogger()
if not root_logger.handlers:
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Set up logging
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler('romplestiltskin_debug.log')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    root_logger.setLevel(logging.DEBUG)

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDir
from ui.main_window import MainWindow
from ui.theme import Theme
from core.settings_manager import SettingsManager
from core.db_manager import DatabaseManager

def main():
    """Main application entry point."""
    print("Starting application...")
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    app.setApplicationName("Romplestiltskin")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Romplestiltskin")
    
    # Initialize core components
    settings_manager = SettingsManager()
    db_manager = DatabaseManager(settings_manager.get_database_path())
    
    # Apply theme globally to the entire application
    theme = Theme()
    app.setStyleSheet(theme.get_stylesheet())
    
    # Create main window
    print("Creating MainWindow...")
    main_window = MainWindow(settings_manager, db_manager)
    print("MainWindow created.")
    
    print("Showing MainWindow...")
    main_window.show()
    print("MainWindow shown.")
    
    print("Starting event loop...")
    exit_code = app.exec()
    print(f"Event loop finished with exit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())