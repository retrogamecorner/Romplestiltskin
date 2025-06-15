#!/usr/bin/env python3
"""
Theme management module for Romplestiltskin.
Separates styling from application logic.
"""

class Theme:
    """Theme class to manage application styling."""
    
    def __init__(self):
        """Initialize theme with default dark colors."""
        self.colors = {
            'background': '#1a1a1a',
            'central_widget': '#2c2c2c',
            'dark_gray': '#0f0f0f',
            'medium_gray': '#2a2a2a',
            'light_gray': '#3a3a3a',
            'highlight': '#4a9eff',
            'highlight_hover': '#3a8eef',
            'highlight_pressed': '#2a7edf',
            'secondary': '#757575',
            'secondary_hover': '#616161',
            'secondary_pressed': '#424242',
            'text': '#d1d1d1',
            'secondary_text': '#a1a1a1',
            'border': '#404040',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'warning_hover': '#f57c00',
            'warning_pressed': '#ef6c00',
            'error': '#F44336',
            'error_hover': '#d32f2f',
            'error_pressed': '#b71c1c',
            'button_text': '#ffffff'
        }
    
    def get_stylesheet(self):
        """Get the complete application stylesheet."""
        return f"""
        /* Global styles */
        QWidget {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        /* Main window */
        QMainWindow {{
            background-color: {self.colors['background']};
            padding: 1%;
        }}
        
        /* Dialog windows */
        QDialog {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
        }}
        
        /* Menu bar */
        QMenuBar {{
            background-color: transparent;
            color: {self.colors['text']};
            border-bottom: 1px solid {self.colors['border']};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 10px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.colors['highlight']};
        }}
        
        QMenu {{
            background-color: {self.colors['medium_gray']};
            border: 1px solid {self.colors['border']};
        }}
        
        QMenu::item {{
            padding: 6px 20px 6px 20px;
        }}
        
        QMenu::item:selected {{
            background-color: {self.colors['highlight']};
            color: {self.colors['text']};
        }}
        
        /* Status bar */
        QStatusBar {{
            background-color: {self.colors['dark_gray']};
            color: {self.colors['secondary_text']};
            border-top: 1px solid {self.colors['border']};
        }}
        
        /* Group boxes */
        QGroupBox {{
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            margin-top: 12px;
            font-weight: bold;
            padding-top: 10px;
            color: {self.colors['text']};
        }}
        
        /* Filter group boxes with enhanced styling */
        QGroupBox[objectName="filter_group"] {{
            border: 2px solid {self.colors['border']};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        
        /* Labels */
        QLabel {{
            color: {self.colors['text']};
            background-color: transparent;
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {self.colors['medium_gray']};
            color: {self.colors['button_text']};
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 30px;
        }}
        
        QPushButton:hover {{
            background-color: {self.colors['light_gray']};
        }}
        
        QPushButton:pressed {{
            background-color: {self.colors['highlight']};
        }}
        
        /* Premium action buttons */
        #premium_button {{
            background-color: {self.colors['highlight']};
            color: {self.colors['text']};
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: bold;
            min-height: 36px;
            font-size: 13px;
        }}
        
        #premium_button:hover {{
            background-color: {self.colors['highlight_hover']};
        }}
        
        /* Tree widgets */
        QTreeWidget {{
            background-color: {self.colors['dark_gray']};
            alternate-background-color: {self.colors['medium_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            color: {self.colors['text']};
        }}
        
        QTreeWidget::item {{
            padding: 4px;
        }}
        
        QTreeWidget::item:selected {{
            background-color: {self.colors['highlight']};
            color: {self.colors['text']};
        }}
        
        QHeaderView::section {{
            background-color: {self.colors['medium_gray']};
            color: {self.colors['text']};
            padding: 6px;
            border: none;
            border-right: 1px solid {self.colors['border']};
            border-bottom: 1px solid {self.colors['border']};
        }}
        
        /* Combo box */
        QComboBox {{
            background-color: {self.colors['medium_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            padding: 6px;
            min-height: 30px;
            color: {self.colors['text']};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {self.colors['border']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {self.colors['medium_gray']};
            border: 1px solid {self.colors['border']};
            color: {self.colors['text']};
        }}
        
        /* Line edit */
        QLineEdit {{
            background-color: {self.colors['medium_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            padding: 6px;
            color: {self.colors['text']};
        }}
        
        QLineEdit:focus {{
            border: 2px solid {self.colors['highlight']};
        }}
        
        /* Text edit */
        QTextEdit {{
            background-color: {self.colors['dark_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            color: {self.colors['text']};
        }}
        
        /* List widgets */
        QListWidget {{
            background-color: {self.colors['dark_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            color: {self.colors['text']};
        }}
        
        QListWidget::item {{
            padding: 4px;
        }}
        
        QListWidget::item:selected {{
            background-color: {self.colors['highlight']};
            color: {self.colors['text']};
        }}
        
        /* Progress bar */
        QProgressBar {{
            background-color: {self.colors['medium_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            text-align: center;
            color: {self.colors['text']};
        }}
        
        QProgressBar::chunk {{
            background-color: {self.colors['highlight']};
            border-radius: 3px;
        }}
        
        /* Tab widget */
        QTabWidget::pane {{
            border: 1px solid {self.colors['border']};
            background-color: {self.colors['background']};
        }}
        
        QTabBar::tab {{
            background-color: {self.colors['medium_gray']};
            color: {self.colors['text']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.colors['background']};
            border-bottom: 2px solid {self.colors['highlight']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {self.colors['light_gray']};
        }}
        
        /* Scroll bars */
        QScrollBar:vertical {{
            background-color: {self.colors['medium_gray']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.colors['light_gray']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.colors['highlight']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {self.colors['medium_gray']};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {self.colors['light_gray']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {self.colors['highlight']};
        }}
        
        /* Spin box */
        QSpinBox {{
            background-color: {self.colors['medium_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            padding: 6px;
            color: {self.colors['text']};
        }}
        
        /* Check box */
        QCheckBox {{
            color: {self.colors['text']};
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {self.colors['border']};
            border-radius: 3px;
            background-color: {self.colors['medium_gray']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {self.colors['highlight']};
        }}
        
        /* Radio button */
        QRadioButton {{
            color: {self.colors['text']};
        }}
        
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            background-color: {self.colors['medium_gray']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {self.colors['highlight']};
        }}
        """
    
    def get_button_style(self, style_type="default"):
        """Get specific button styles for consistency."""
        if style_type == "modern":
            return f"""
                QPushButton {{
                    background-color: {self.colors['highlight']};
                    color: {self.colors['text']};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                    min-height: 16px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['highlight_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['light_gray']};
                }}
            """
        elif style_type == "danger":
            return f"""
                QPushButton {{
                    background-color: {self.colors['error']};
                    color: {self.colors['text']};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                    min-height: 16px;
                }}
                QPushButton:hover {{
                    background-color: #d32f2f;
                }}
                QPushButton:pressed {{
                    background-color: #b71c1c;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {self.colors['medium_gray']};
                    color: {self.colors['button_text']};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-height: 30px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['light_gray']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['highlight']};
                }}
            """
    
    def get_colors(self):
        """Get the color palette."""
        return self.colors.copy()