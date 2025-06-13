#!/usr/bin/env python3
"""
Test script to debug theme application
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

def create_test_stylesheet():
    """Create a simple test stylesheet."""
    colors = {
        'background': '#2E2E2E',
        'text': '#E6E6E6',
        'highlight': '#2D8CEB'
    }
    
    return f"""
    QWidget {{
        background-color: {colors['background']};
        color: {colors['text']};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    
    QMainWindow {{
        background-color: {colors['background']};
    }}
    """

def main():
    app = QApplication(sys.argv)
    
    # Test simple stylesheet
    stylesheet = create_test_stylesheet()
    print("Testing stylesheet:")
    print(stylesheet)
    
    try:
        app.setStyleSheet(stylesheet)
        print("✓ Simple stylesheet applied successfully")
    except Exception as e:
        print(f"✗ Error applying stylesheet: {e}")
        return 1
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Theme Test")
    window.resize(400, 300)
    
    label = QLabel("Theme Test - If you see dark background, theme is working!")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)
    
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())