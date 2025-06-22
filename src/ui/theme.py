#!/usr/bin/env python3
"""
Theme management module for Romplestiltskin.
Separates styling from application logic.
"""

class Theme:
    """Theme class to manage application styling."""
    
    def __init__(self):
        """Initialize theme with default dark colors, dimensions, and layout properties."""
        self.colors = {
            'background': '#1a1a1a',
            'main_window': '#1a1a1a',  # Same as background
            'central_widget': '#2c2c2c',
            'dark_gray': '#0f0f0f',
            'medium_gray': '#2a2a2a',
            'light_gray': '#3a3a3a',
            'highlight': '#4a9eff',
            'highlight_hover': '#3a8eef',
            'highlight_pressed': '#2a7edf',
            'primary': '#4a9eff',  # Same as highlight
            'secondary': '#757575',
            'secondary_hover': '#616161',
            'secondary_pressed': '#424242',
            'text': '#d1d1d1',
            'secondary_text': '#a1a1a1',
            'muted_text': '#757575',  # Same as secondary
            'border': '#404040',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'warning_hover': '#f57c00',
            'warning_pressed': '#ef6c00',
            'error': '#F44336',
            'error_hover': '#d32f2f',
            'error_pressed': '#b71c1c',
            'button': '#2a2a2a',  # Same as medium_gray
            'button_hover': '#3a3a3a',  # Same as light_gray
            'button_text': '#ffffff',
            'selection': '#4a9eff',  # Same as highlight
            'shadow': '#1a1a1a',  # Dark shadow color for button effects
            'group_bg': '#3e3e3e',  # Added missing group background color
            # Tree item colors
            'tree_item_correct_bg': '#c8ffc8',  # Light green (200, 255, 200)
            'tree_item_correct_text': '#000000',  # Black text (0, 0, 0)
            # Drag and drop colors
            'drag_drop': {
                'highlight_border': '#d6d6d6',  # Color for the drop indicator line
                'highlight_background': 'rgba(0, 120, 212, 0.1)', # Retained for now, might be unused
                'available_bg': '#3A3A3A',
                'available_item': 'transparent',
                'available_text': '#d6d6d6',
                'available_selected_bg': '#3A3A3A',  # Same as available_bg
                'available_hover_bg': '#3A3A3A', # Same as available_bg to avoid color change
                'available_hover_text': '#d6d6d6', # Same as available_text to avoid color change
                'ignored_hover_bg': '#4b3737',  # Same as ignored_bg to avoid color change
                'ignored_hover_text': '#d99595', # Same as ignored_text to avoid color change
                'ignored_bg': '#4b3737',
                'ignored_item': 'transparent',
                'ignored_selected_bg': '#4b3737',  # Same as ignored_bg
                'ignored_text': '#d99595'
            },
            # Progress dialog colors
            'progress_dialog': {
                'details_text': '#757575',  # Gray color for details text
                'details_font_size': '10px'
            }
        }
        
        # Dimensions for widgets (organized by category)
        self.dimensions = {
            'widget': {
                'button_min_height': 30,
                'button_min_width': 80,
                'premium_button_min_height': 36,
                'input_min_height': 30,
                'combo_min_height': 30,
                'tree_header_height': 25,
                'list_item_height': 24,
                'checkbox_size': 16,
                'radio_size': 16,
                'scrollbar_width': 12,
                'scrollbar_handle_min': 20
            },
            'border': {
                'radius': 4,
                'radius_large': 8,
                'radius_medium': 6,
                'radius_small': 3,
                'width': 1,
                'width_thick': 2
            },
            'main_window': {
                'combo_minimum_width': 300,
                'tree_minimum_height': 250,
                'tree_maximum_height': 300,
                'dat_tree_minimum_height': 300,
                'dat_tree_maximum_height': 350,
                'panel_maximum_height': 300,
                'language_scroll_maximum_height': 120,
                'min_width': 1400,
                'min_height': 900
            },
            'settings_dialog': {
                'list_maximum_height': 120,
                'width': 600,
                'height': 500
            },
            'progress_dialog': {
                'log_max_height': 100,
                'width': 400,
                'height': 200,
                'expanded_height': 300
            },
            # Legacy flat structure for backward compatibility
            'button_min_height': 30,
            'button_min_width': 80,
            'premium_button_min_height': 36,
            'input_min_height': 30,
            'combo_min_height': 30,
            'tree_header_height': 25,
            'list_item_height': 24,
            'checkbox_size': 16,
            'radio_size': 16,
            'scrollbar_width': 12,
            'scrollbar_handle_min': 20,
            'border_radius': 4,
            'border_radius_large': 8,
            'border_radius_medium': 6,
            'border_radius_small': 3,
            'border_width': 1,
            'border_width_thick': 2,
            'combo_minimum_width': 300,
            'tree_minimum_height': 250,
            'tree_maximum_height': 300,
            'dat_tree_minimum_height': 300,
            'dat_tree_maximum_height': 350,
            'panel_maximum_height': 300,
            'language_scroll_maximum_height': 120,
            'settings_list_maximum_height': 120,
            'settings_dialog_width': 600,
            'settings_dialog_height': 500,
            'progress_log_max_height': 100,
            'main_window_min_width': 1400,
            'main_window_min_height': 900,
            'progress_dialog_width': 400,
            'progress_dialog_height': 200,
            'progress_dialog_expanded_height': 300
        }
        
        # Spacing and padding values
        self.spacing = {
            'tiny': 2,
            'small': 4,
            'medium': 6,
            'large': 8,
            'xlarge': 10,
            'xxlarge': 12,
            'huge': 16,
            'massive': 20
        }
        
        # Layout margins and padding
        self.layout = {
            'window_padding': '1%',
            'main_window_margins': 15,
            'dialog_margin': 10,
            'group_margin_top': 12,
            'filter_group_margin_top': 10,
            'title_padding': '0 5px',
            'title_left_offset': 10,
            'button_padding': '8px 16px',
            'premium_button_padding': '10px 20px',
            'input_padding': '6px',
            'item_padding': '4px',
            'menu_item_padding': '6px 10px',
            'menu_item_full_padding': '6px 20px 6px 20px',
            'tab_padding': '8px 16px',
            'header_padding': '6px',
            # Column widths for tree widgets
            'tree_index_column_width': 50,
            'tree_name_column_width': 300,
            # Stats label styling
            'stats_label_padding': '5px',
            # Settings dialog specific layout
            'settings_contents_margins': '20px 20px 20px 20px',
            'settings_tab_spacing': 20,
            'settings_group_spacing': 15,
            'settings_button_spacing': 10,
            'settings_modern_button_padding': '8px 16px',
            'settings_secondary_button_padding': '8px 16px',
            'settings_danger_button_padding': '12px 24px',
            'settings_warning_button_padding': '10px 20px',
            'help_text_font_size': '10px',
            'help_text_margin': '20px'
        }
        
        # Font properties
        self.fonts = {
            'family': "'Segoe UI', Arial, sans-serif",
            'size_small': 11,
            'size_normal': 12,
            'size_medium': 13,
            'size_large': 14,
            'weight_normal': 'normal',
            'weight_bold': 'bold'
        }
    
    def get_stylesheet(self):
        """Get the complete application stylesheet."""
        return f"""
        /* Global styles */
        QWidget {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
            font-family: {self.fonts['family']};
            font-size: {self.fonts['size_normal']}px;
        }}
        
        /* Main window */
        QMainWindow {{
            background-color: {self.colors['main_window']};
            border: 2px solid {self.colors['border']};
        }}
        
        /* Central widget to show padding */
        QMainWindow > QWidget {{
            background-color: {self.colors['background']};
            border-radius: {self.dimensions['border_radius']}px;
        }}
        
        /* Dialog windows */
        QDialog {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
        }}
        
        /* Menu bar */
        QMenuBar {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
            margin: 0px;
            padding-left: 0px;
            padding-right: 0px;
            padding-top: 0px;
            padding-bottom: 0px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: {self.layout['menu_item_padding']};
            margin: 0px;
            border: none;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.colors['highlight']};
        }}
        
        QMenu {{
            background-color: {self.colors['medium_gray']};
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
        }}
        
        QMenu::item {{
            padding: {self.layout['menu_item_full_padding']};
        }}
        
        QMenu::item:selected {{
            background-color: {self.colors['highlight']};
            color: {self.colors['text']};
        }}
        
        /* Status bar */
        QStatusBar {{
            background-color: {self.colors['dark_gray']};
            color: {self.colors['secondary_text']};
            border-top: {self.dimensions['border_width']}px solid {self.colors['border']};
        }}
        
        /* Group boxes */
        QGroupBox {{
            background: {self.colors['group_bg']}; /* Ensure this is #3e3e3e */
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            border-radius: {self.dimensions['border_radius']}px;
            margin-top: {self.layout['group_margin_top']}px;
            font-weight: {self.fonts['weight_bold']};
            padding-top: {self.spacing['xlarge']}px;
            color: {self.colors['text']};
        }}
        
        /* Filter group boxes with enhanced styling */
        QGroupBox[objectName="filter_group"] {{
            background: {self.colors['group_bg']}; /* Ensure this is #3e3e3e */
            border: {self.dimensions['border_width_thick']}px solid #484848;
            border-radius: {self.dimensions['border_radius_large']}px;
            margin-top: {self.layout['filter_group_margin_top']}px;
            padding-top: {self.spacing['xlarge']}px;
            font-weight: {self.fonts['weight_bold']};
        }}


        /* Language and Type group box styling will now be primarily determined by get_actions_group_style or general QGroupBox styling */
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {self.layout['title_left_offset']}px;
            padding: {self.layout['title_padding']};
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
            border-radius: {self.dimensions['border_radius']}px;
            padding: {self.layout['button_padding']};
            font-weight: {self.fonts['weight_bold']};
            min-height: {self.dimensions['button_min_height']}px;
            min-width: {self.dimensions['button_min_width']}px;
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
            border-radius: {self.dimensions['border_radius']}px;
            padding: {self.layout['premium_button_padding']};
            font-weight: {self.fonts['weight_bold']};
            min-height: {self.dimensions['premium_button_min_height']}px;
            font-size: {self.fonts['size_medium']}px;
        }}
        
        #premium_button:hover {{
            background-color: {self.colors['highlight_hover']};
        }}
        
        /* Tree widgets */
        QTreeWidget {{
            background-color: #3e3e3e;
            border: none;
            color: {self.colors['text']};
        }}

        QTreeWidget::item:alternate {{
            background-color: #3e3e3e;
        }}

        QTreeWidget::item {{
            background-color: #3e3e3e;
            border-bottom: 2px solid #4e4e4e;
            padding: {self.spacing['small']}px;
            min-height: {self.dimensions['list_item_height']}px;
        }}

        QTreeWidget::item:hover {{
            background-color: #4a4a4a;
        }}

        QTreeWidget::item:selected {{
            background-color: {self.colors['highlight']};
            color: {self.colors['text']};
        }}

        QHeaderView::section {{
            background-color: #2c2c2c;
            color: {self.colors['text']};
            padding: {self.layout['header_padding']};
            border: none;
            min-height: {self.dimensions['tree_header_height']}px;
        }}
        
        /* Combo box */
        QComboBox {{
            background-color: {self.colors['medium_gray']};
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            border-radius: {self.dimensions['border_radius']}px;
            padding: {self.layout['input_padding']};
            min-height: {self.dimensions['combo_min_height']}px;
            color: {self.colors['text']};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: {self.spacing['massive']}px;
            border-left: {self.dimensions['border_width']}px solid {self.colors['border']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {self.colors['medium_gray']};
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            color: {self.colors['text']};
        }}
        
        /* Line edit */
        QLineEdit {{
            background-color: {self.colors['medium_gray']};
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            border-radius: {self.dimensions['border_radius']}px;
            padding: {self.layout['input_padding']};
            min-height: {self.dimensions['input_min_height']}px;
            color: {self.colors['text']};
        }}
        
        QLineEdit:focus {{
            border: {self.dimensions['border_width_thick']}px solid {self.colors['highlight']};
        }}
        
        /* Text edit */
        QTextEdit {{
            background-color: {self.colors['dark_gray']};
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            border-radius: {self.dimensions['border_radius']}px;
            color: {self.colors['text']};
            padding: {self.layout['input_padding']};
        }}
        
        /* List widgets */
        QListWidget {{
            background-color: {self.colors['dark_gray']};
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            border-radius: {self.dimensions['border_radius']}px;
            color: {self.colors['text']};
        }}
        
        QListWidget::item {{
            padding: {self.spacing['small']}px;
            min-height: {self.dimensions['list_item_height']}px;
        }}
        
        QListWidget::item:selected {{
            background-color: {self.colors['highlight']};
            color: {self.colors['text']};
        }}
        
        /* Override for drag-drop lists to prevent blue highlighting */
        QListWidget[objectName="drag_drop_list"]::item:selected {{
              background-color: transparent; 
        }}
        
        QListWidget[objectName="drag_drop_list"]::item:selected:active {{
             background-color: transparent; 
        }}
        
        QListWidget[objectName="drag_drop_list"]::item:selected:focus {{
             background-color: transparent; 
        }}
        
        /* Progress bar */
        QProgressBar {{
            background-color: {self.colors['medium_gray']};
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            border-radius: {self.dimensions['border_radius']}px;
            text-align: center;
            color: {self.colors['text']};
            min-height: {self.dimensions['input_min_height']}px;
        }}
        
        QProgressBar::chunk {{
            background-color: {self.colors['highlight']};
            border-radius: {self.dimensions['border_radius_small']}px;
        }}
        
        /* Tab widget */
        QTabWidget::pane {{
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            background-color: {self.colors['background']};
        }}
        
        QTabBar::tab {{
            background-color: {self.colors['medium_gray']};
            color: {self.colors['text']};
            padding: {self.layout['tab_padding']};
            margin-right: {self.spacing['tiny']}px;
            border-top-left-radius: {self.dimensions['border_radius']}px;
            border-top-right-radius: {self.dimensions['border_radius']}px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.colors['background']};
            border-bottom: {self.dimensions['border_width_thick']}px solid {self.colors['highlight']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {self.colors['light_gray']};
        }}
        
        /* Scroll bars */
        QScrollBar:vertical {{
            background-color: {self.colors['medium_gray']};
            width: {self.dimensions['scrollbar_width']}px;
            border-radius: {self.dimensions['scrollbar_width']//2}px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.colors['light_gray']};
            border-radius: {self.dimensions['scrollbar_width']//2}px;
            min-height: {self.dimensions['scrollbar_handle_min']}px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.colors['highlight']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {self.colors['medium_gray']};
            height: {self.dimensions['scrollbar_width']}px;
            border-radius: {self.dimensions['scrollbar_width']//2}px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {self.colors['light_gray']};
            border-radius: {self.dimensions['scrollbar_width']//2}px;
            min-width: {self.dimensions['scrollbar_handle_min']}px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {self.colors['highlight']};
        }}
        
        /* Spin box */
        QSpinBox {{
            background-color: {self.colors['medium_gray']};
            border: {self.dimensions['border_width']}px solid {self.colors['border']};
            border-radius: {self.dimensions['border_radius']}px;
            padding: {self.layout['input_padding']};
            min-height: {self.dimensions['input_min_height']}px;
            color: {self.colors['text']};
        }}
        
        /* Checkbox */
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {self.colors['group_bg']};
            border-radius: 3px;
            /* background-color: {self.colors['medium_gray']}; */
            background: none !important;
            border: 2px solid #484848;
        }}
        
        QCheckBox::indicator:checked {{
            width: 16px;
            height: 16px;
            /* border: 1px solid {self.colors['group_bg']}; */
            border: 2px solid #484848;
            border-radius: 3px;
            /* background-color: {self.colors['medium_gray']}; */
            background: none !important;
            image: url(src/ui/flags/checkmark.svg);
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
                    border-radius: {self.dimensions['border_radius']}px;
                    padding: {self.layout['button_padding']};
                    font-size: {self.fonts['size_normal']}px;
                    font-weight: {self.fonts['weight_bold']};
                    min-height: {self.dimensions['button_min_height']}px;
                    min-width: {self.dimensions['button_min_width']}px;
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
                    border-radius: {self.dimensions['border_radius']}px;
                    padding: {self.layout['button_padding']};
                    font-size: {self.fonts['size_normal']}px;
                    font-weight: {self.fonts['weight_bold']};
                    min-height: {self.dimensions['button_min_height']}px;
                    min-width: {self.dimensions['button_min_width']}px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['error_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['error_pressed']};
                }}
            """
        elif style_type == "QMainButton":
            return f"""
                QPushButton {{
                    background-color: #383838;
                    color: {self.colors['button_text']};
                    border: 1px solid {self.colors['border']};
                    border-radius: 8px;
                    padding: 5px 15px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-weight: normal;
                    font-size: {self.fonts['size_normal']}px;
                }}
                QPushButton:hover {{
                    background-color: #484848;
                }}
                QPushButton:pressed {{
                    background-color: #282828;
                }}
            """
        elif style_type == "ScanButton":
            base_style = self.get_button_style("QMainButton")
            return base_style.replace(f"background-color: {self.colors['button']};", f"background-color: {self.colors['button_hover']};")
        elif style_type == "ClearButton":
            return f"""
                QPushButton {{
                    background-color: #6b211e;
                    color: {self.colors['button_text']};
                    border: 1px solid #6b211e;
                    border-radius: 8px;
                    padding: 5px 15px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-weight: normal;
                    font-size: {self.fonts['size_normal']}px;
                }}
                QPushButton:hover {{
                    background-color: #7a2622;
                }}
                QPushButton:pressed {{
                    background-color: #5c1e1a;
                }}
            """
        elif style_type == "SelectAllButton":
            return f"""
                QPushButton {{
                    background-color: {self.colors['button']};
                    color: {self.colors['button_text']};
                    border: 1px solid {self.colors['border']};
                    border-radius: 8px;
                    padding: 0px 5px 3px 5px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-weight: normal;
                    font-size: {self.fonts['size_normal']}px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['button_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['button_hover']};
                }}
            """
        elif style_type == "ClearAllButton":
            return f"""
                QPushButton {{
                    background-color: #6b211e;
                    color: {self.colors['button_text']};
                    border: 1px solid #6b211e;
                    border-radius: 8px;
                    padding: 0px 5px 3px 5px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-weight: normal;
                    font-size: {self.fonts['size_normal']}px;
                }}
                QPushButton:hover {{
                    background-color: #7a2622;
                }}
                QPushButton:pressed {{
                    background-color: #5c1e1a;
                }}
            """
        elif style_type == "CircularMoveButton":
            return f"""
                QPushButton {{
                    background-color: #6b211e;
                    color: {self.colors['button_text']};
                    border: none;
                    border-radius: 10px !important;
                    padding: 0px;
                    width: 20px;
                    height: 20px;
                    max-width: 20px;
                    max-height: 20px;
                    min-width: 20px;
                    min-height: 20px;
                    margin: 0px;
                    font-size: 10px;
                    font-weight: normal;
                }}
                QPushButton:hover {{
                    background-color: #7a2622;
                }}
                QPushButton:pressed {{
                    background-color: #5c1e1a;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {self.colors['medium_gray']};
                    color: {self.colors['button_text']};
                    border: none;
                    border-radius: {self.dimensions['border_radius']}px;
                    padding: {self.layout['button_padding']};
                    font-weight: {self.fonts['weight_bold']};
                    min-height: {self.dimensions['button_min_height']}px;
                    min-width: {self.dimensions['button_min_width']}px;
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
    
    def get_dimensions(self):
        """Get the dimensions dictionary."""
        return self.dimensions.copy()
    
    def get_spacing(self):
        """Get the spacing dictionary."""
        return self.spacing.copy()
    
    def get_layout(self):
        """Get the layout dictionary."""
        return self.layout.copy()
    
    def get_fonts(self):
        """Get the fonts dictionary."""
        return self.fonts.copy()
    
    def get_dimension(self, key, default=None):
        """Get a specific dimension value."""
        return self.dimensions.get(key, default)
    
    def get_spacing_value(self, key, default=None):
        """Get a specific spacing value."""
        return self.spacing.get(key, default)
    
    def get_layout_value(self, key, default=None):
        """Get a specific layout value."""
        return self.layout.get(key, default)
    
    def get_font_property(self, key, default=None):
        """Get a specific font property."""
        return self.fonts.get(key, default)
    
    def get_color(self, key, default=None):
        """Get a specific color value."""
        return self.colors.get(key, default)
    
    def create_widget_style(self, widget_type, **overrides):
        """Create a custom widget style with theme properties and optional overrides."""
        base_styles = {
            'button': {
                'background-color': self.colors['medium_gray'],
                'color': self.colors['button_text'],
                'border': 'none',
                'border-radius': f"{self.dimensions['border_radius']}px",
                'padding': self.layout['button_padding'],
                'font-weight': self.fonts['weight_bold'],
                'min-height': f"{self.dimensions['button_min_height']}px",
                'min-width': f"{self.dimensions['button_min_width']}px"
            },
            'input': {
                'background-color': self.colors['medium_gray'],
                'border': f"{self.dimensions['border_width']}px solid {self.colors['border']}",
                'border-radius': f"{self.dimensions['border_radius']}px",
                'padding': self.layout['input_padding'],
                'min-height': f"{self.dimensions['input_min_height']}px",
                'color': self.colors['text']
            },
            'list': {
                'background-color': self.colors['dark_gray'],
                'border': f"{self.dimensions['border_width']}px solid {self.colors['border']}",
                'border-radius': f"{self.dimensions['border_radius']}px",
                'color': self.colors['text']
            }
        }
        
        if widget_type not in base_styles:
            return ""
        
        style_dict = base_styles[widget_type].copy()
        style_dict.update(overrides)
        
        style_parts = [f"{prop}: {value};" for prop, value in style_dict.items()]
        return " ".join(style_parts)
    
    def get_settings_modern_button_style(self):
        """Get modern button style for settings dialog."""
        return f"""
            QPushButton {{
                background-color: {self.colors['highlight']};
                color: {self.colors['button_text']};
                border: none;
                border-radius: {self.dimensions['border_radius']}px;
                padding: {self.layout['settings_modern_button_padding']};
                font-size: 12px;
                font-weight: {self.fonts['weight_bold']};
                min-height: {self.dimensions['button_min_height']}px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['highlight_hover']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['highlight_pressed']};
            }}
        """
    
    def get_settings_secondary_button_style(self):
        """Get secondary button style for settings dialog."""
        return f"""
            QPushButton {{
                background-color: {self.colors['medium_gray']};
                color: {self.colors['button_text']};
                border: none;
                border-radius: {self.dimensions['border_radius']}px;
                padding: {self.layout['settings_secondary_button_padding']};
                font-size: 12px;
                font-weight: {self.fonts['weight_bold']};
                min-height: {self.dimensions['button_min_height']}px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['light_gray']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['highlight']};
            }}
        """
    
    def get_settings_help_text_style(self):
        """Get help text style for settings dialog."""
        return f"""
            QLabel {{
                color: {self.colors['muted_text']};
                font-size: {self.layout['help_text_font_size']};
            }}
        """
    
    def get_settings_danger_group_style(self):
        """Get danger zone group box style for settings dialog."""
        return f"""
            QGroupBox {{{{
                background: {self.colors['group_bg']};
                font-weight: {self.fonts['weight_bold']};
                font-size: 14px;
                color: {self.colors['error']};
                border: 2px solid {self.colors['error']};
                border-radius: {self.dimensions['border_radius_large']}px;
                margin-top: 10px;
                padding-top: 10px;
                subcontrol-origin: margin;
                left: {self.layout['title_left_offset']}px;
                padding: {self.layout['settings_contents_margins']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.layout['title_left_offset']}px;
                padding: {self.layout['title_padding']};
            }}
        """
    
    def get_settings_danger_button_style(self):
        """Get danger button style for settings dialog."""
        return f"""
            QPushButton {{
                background-color: {self.colors['error']};
                color: {self.colors['button_text']};
                border: none;
                border-radius: {self.dimensions['border_radius']}px;
                padding: {self.layout['settings_danger_button_padding']};
                font-size: 12px;
                font-weight: {self.fonts['weight_bold']};
                min-height: {self.dimensions['button_min_height']}px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['error_hover']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['error_pressed']};
            }}
        """
    
    def get_settings_warning_button_style(self):
        """Get warning button style for settings dialog."""
        return f"""
            QPushButton {{
                background-color: {self.colors['warning']};
                color: {self.colors['button_text']};
                border: none;
                border-radius: {self.dimensions['border_radius']}px;
                padding: {self.layout['settings_warning_button_padding']};
                font-size: 12px;
                font-weight: {self.fonts['weight_bold']};
                min-height: {self.dimensions['button_min_height']}px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['warning_hover']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['warning_pressed']};
            }}
        """
    
    def get_settings_group_box_style(self):
        """Get standard group box style for settings dialog."""
        return f"""
            QGroupBox {{
                background: {self.colors['group_bg']};
                font-weight: {self.fonts['weight_bold']};
                font-size: 14px;
                border: 2px solid {self.colors['border']};
                border-radius: {self.dimensions['border_radius_large']}px;
                margin-top: 10px;
                padding-top: 10px;
                subcontrol-origin: margin;
                left: {self.layout['title_left_offset']}px;
                padding: {self.layout['settings_contents_margins']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.layout['title_left_offset']}px;
                padding: {self.layout['title_padding']};
            }}
        """
    
    def get_settings_combo_box_style(self):
        """Get combo box style for settings dialog."""
        return f"""
            QComboBox {{
                border: {self.dimensions['border_width']}px solid {self.colors['border']};
                border-radius: {self.dimensions['border_radius']}px;
                padding: {self.layout['input_padding']};
                font-size: 12px;
                min-width: 150px;
            }}
            QComboBox:focus {{
                border-color: {self.colors['primary']};
            }}
        """
    
    def get_system_combo_box_style(self):
        """Get combo box style for system selection."""
        return f"""
            QComboBox {{
                background-color: {self.colors['group_bg']};
                border: 1px solid {self.colors['border']};
                border-radius: {self.dimensions['border']['radius']}px;
                padding: {self.layout['input_padding']};
                color: {self.colors['text']};
                min-height: {self.dimensions['widget']['combo_min_height']}px;
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
                background-color: {self.colors['group_bg']};
            }}
            
            QComboBox::down-arrow {{
                image: url(n:/Romplestiltskin/Romplestiltskin/src/ui/flags/down_arrow.svg);
                width: 10px;
                height: 10px;
                border: none; /* Remove any border that might interfere */
                background: transparent; /* Ensure background is transparent */
                subcontrol-position: center;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {self.colors['group_bg']};
                border: 1px solid {self.colors['border']};
                color: {self.colors['text']};
                selection-background-color: {self.colors['selection']};
            }}
        """
    
    # Drag and Drop Styling Methods
    
    def get_drag_drop_highlight_style(self):
        """Get drag and drop highlight style for DragDropListWidget."""
        # This style is applied directly to the DragDropListWidget instance.
        return f"""
            QListWidget {{
                border: none !important;
                outline: none !important;
                background-color: rgba(0, 120, 255, 0.05) !important; /* Subtle highlight or transparent */
                font-family: {self.fonts['family']};
                font-size: {self.fonts['size_medium']}px;
                font-weight: normal;
            }}
            QListWidget::item {{
                padding: {self.spacing['small']}px;
                border: none;
                outline: none;
                font-family: {self.fonts['family']};
                font-size: {self.fonts['size_medium']}px;
                font-weight: normal;
            }}
        """
    
    def get_drag_drop_normal_style(self):
        """Get normal style for DragDropListWidget."""
        # This style is applied directly to the DragDropListWidget instance.
        return f"""
            QListWidget {{
                border: {self.dimensions['border_width']}px solid {self.colors['border']};
                background-color: {self.colors['medium_gray']};
                outline: none !important;
                font-family: {self.fonts['family']};
                font-size: {self.fonts['size_medium']}px;
                font-weight: normal;
            }}
            QListWidget::item {{
                padding: {self.spacing['small']}px;
                border: none;
                outline: none;
                font-family: {self.fonts['family']};
                font-size: {self.fonts['size_medium']}px;
                font-weight: normal;
            }}
        """
    
    def get_drag_drop_available_list_style(self):
        """Get available regions list style."""
        return f"""
            QListWidget {{
                border: none;
                outline: none;
                background-color: {self.colors['drag_drop']['available_bg']};
                color: {self.colors['drag_drop']['available_text']};
                font-family: {self.fonts['family']};
                font-size: {self.fonts['size_medium']}px;
                font-weight: normal;
            }}
            QListWidget::item {{
                padding: {self.spacing['small']}px;
                border: none;
                outline: none;
                font-family: {self.fonts['family']};
                font-size: {self.fonts['size_medium']}px;
                font-weight: normal;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['drag_drop']['available_bg']}; /* Keep same as item background */
                color: {self.colors['drag_drop']['available_text']};
                border: none;
                outline: none;
                font-family: {self.fonts['family']};
                font-size: {self.fonts['size_medium']}px;
                font-weight: normal;
            }}
            QListWidget::item:selected:active {{
                background-color: {self.colors['drag_drop']['available_bg']};
                color: {self.colors['drag_drop']['available_text']};
                border: none;
                outline: none;
            }}
            QListWidget::item:selected:focus {{
                background-color: {self.colors['drag_drop']['available_bg']};
                color: {self.colors['drag_drop']['available_text']};
                border: none;
                outline: none;
            }}
            QListWidget::item:hover {{
                background-color: {self.colors['drag_drop']['available_hover_bg']};
                color: {self.colors['drag_drop']['available_hover_text']};
                border: none;
                outline: none;
            }}
        """
    
    def get_drag_drop_ignored_list_style(self):
        """Get ignored regions list style."""
        return f"""
            QListWidget {{
                border: none;
                outline: none;
                background-color: {self.colors['drag_drop']['ignored_bg']};
                color: {self.colors['drag_drop']['ignored_text']};
                font-family: {self.fonts['family']};
                font-size: {self.fonts['size_medium']}px;
                font-weight: normal;
            }}
            QListWidget::item {{
                padding: {self.spacing['small']}px;
                border: none;
                outline: none;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['drag_drop']['ignored_bg']}; /* Keep same as item background */
                color: {self.colors['drag_drop']['ignored_text']};
                border: none;
                outline: none;
            }}
            QListWidget::item:selected:active {{
                background-color: {self.colors['drag_drop']['ignored_bg']};
                color: {self.colors['drag_drop']['ignored_text']};
                border: none;
                outline: none;
            }}
            QListWidget::item:selected:focus {{
                background-color: {self.colors['drag_drop']['ignored_bg']};
                color: {self.colors['drag_drop']['ignored_text']};
                border: none;
                outline: none;
            }}
            QListWidget::item:hover {{
                background-color: {self.colors['drag_drop']['ignored_hover_bg']};
                color: {self.colors['drag_drop']['ignored_hover_text']};
                border: none;
                outline: none;
            }}
        """
    
    def get_drag_drop_title_style(self):
        """Get title label style for drag and drop widgets."""
        return f"""
            QLabel {{
                font-weight: {self.fonts['weight_bold']};
                font-size: {self.fonts['size_medium']}px;
                margin-bottom: {self.spacing['medium']}px;
                border: none !important;
                outline: none !important;
                background-color: transparent !important;
                selection-background-color: transparent !important;
                selection-color: inherit !important;
            }}
            QLabel:focus {{
                border: none !important;
                outline: none !important;
                background-color: transparent !important;
            }}
        """
    
    def get_drag_drop_label_style(self):
        """Get label style for drag and drop widgets."""
        return f"""
            QLabel {{
                font-weight: {self.fonts['weight_bold']};
            }}
        """
    
    def get_drag_drop_button_style(self):
        """Get button style for drag and drop widgets."""
        return f"""
            QPushButton {{
                color: {self.colors['text']};
                font-weight: {self.fonts['weight_bold']};
                font-size: {self.fonts['size_normal']}px;
                background-color: transparent;
                border: none;
                padding: {self.spacing['medium']}px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['light_gray']};
                border-radius: {self.dimensions['border_radius_small']}px;
            }}
        """
    
    def get_progress_dialog_details_style(self):
        """Get details label style for progress dialog."""
        return f"""
            QLabel {{
                color: {self.colors['progress_dialog']['details_text']};
                font-size: {self.colors['progress_dialog']['details_font_size']};
            }}
        """
    
    def get_progress_dialog_log_max_height(self):
        """Get maximum height for progress dialog log text."""
        return self.dimensions['progress_log_max_height']
    
    def get_language_button_style(self):
        """Get style for language selection buttons."""
        return f"""
            QPushButton {{
                background-color: {self.colors['highlight']};
                color: {self.colors['button_text']};
                border: none;
                padding: {self.spacing['small']}px {self.spacing['medium']}px;
                border-radius: {self.dimensions['border_radius_small']}px;
                font-size: {self.fonts['size_small']}px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['highlight_hover']};
            }}
        """
    
    def get_clear_language_button_style(self):
        """Get style for clear language selection buttons."""
        return f"""
            QPushButton {{
                background-color: {self.colors['error']};
                color: {self.colors['button_text']};
                border: none;
                padding: {self.spacing['small']}px {self.spacing['medium']}px;
                border-radius: {self.dimensions['border_radius_small']}px;
                font-size: {self.fonts['size_small']}px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['error_hover']};
            }}
        """
    
    def get_type_button_style(self):
        """Get style for game type selection buttons."""
        return f"""
            QPushButton {{
                background-color: {self.colors['highlight']};
                color: {self.colors['button_text']};
                border: none;
                padding: {self.spacing['medium']}px {self.spacing['large']}px;
                border-radius: {self.dimensions['border_radius_small']}px;
                font-weight: {self.fonts['weight_bold']};
            }}
            QPushButton:hover {{
                background-color: {self.colors['highlight_hover']};
            }}
        """
    
    def get_clear_type_button_style(self):
        """Get style for clear game type selection buttons."""
        return f"""
            QPushButton {{
                background-color: {self.colors['error']};
                color: {self.colors['button_text']};
                border: none;
                padding: {self.spacing['medium']}px {self.spacing['large']}px;
                border-radius: {self.dimensions['border_radius_small']}px;
                font-weight: {self.fonts['weight_bold']};
            }}
            QPushButton:hover {{
                background-color: {self.colors['error_hover']};
            }}
        """
    
    def get_actions_group_style(self):
        """Get style for actions group box."""
        return f"""
            QGroupBox {{
                background: {self.colors['group_bg']};
                font-weight: {self.fonts['weight_bold']};
                border: 2px solid #484848; /* Changed to #484848 */
                border-radius: {self.dimensions['border_radius_medium']}px;
                padding: 30px 0px 10px 0px; /* Increased top padding to 40px */
            }}
            QGroupBox::title {{
                top:25px;  
                left:5px;           
            }}
            QFrame#horizontalLine {{
                min-height: 2px;
                max-height: 2px;
                background-color: #484848;
                margin-left: 0px;
                margin-right: 0px;
            }}
            QFrame#filtersHorizontalLine {{
                min-height: 2px;
                max-height: 2px;
                background-color: #484848;
                margin-left: 10px;
                margin-right: 10px;
            }}
        """
    
    def get_main_window_minimum_size(self):
        """Get minimum size for main window."""
        return (self.dimensions.get('main_window_min_width', 1400), 
                self.dimensions.get('main_window_min_height', 900))
    
    def get_progress_dialog_size(self):
        """Get default size for progress dialog."""
        return (self.dimensions.get('progress_dialog_width', 400), 
                self.dimensions.get('progress_dialog_height', 200))
    
    def get_progress_dialog_expanded_size(self):
        """Get expanded size for progress dialog with log."""
        return (self.dimensions.get('progress_dialog_width', 400), 
                self.dimensions.get('progress_dialog_expanded_height', 300))
    
    def get_settings_dialog_size(self):
        """Get default size for settings dialog."""
        return (self.dimensions.get('settings_dialog_width', 600), 
                self.dimensions.get('settings_dialog_height', 500))
    
    def get_menu_columns_widget_style(self):
        """Get style for menu columns widget with bottom padding."""
        return f"""
            QWidget#menu_columns_widget {{
                padding-bottom: 15px;
            }}
        """
    
    # Helper methods for theme system enhancement
    def get_dimension(self, category, key):
        """Get dimension value by category and key.
        
        Args:
            category (str): The dimension category (e.g., 'widget', 'border', 'main_window')
            key (str): The specific dimension key within the category
            
        Returns:
            The dimension value, or None if not found
        """
        if category in self.dimensions and isinstance(self.dimensions[category], dict):
            return self.dimensions[category].get(key)
        return None
    
    def get_widget_style(self, widget_type, variant='default'):
        """Return complete stylesheet for widget types.
        
        Args:
            widget_type (str): The type of widget (e.g., 'button', 'input', 'combo')
            variant (str): The style variant (default: 'default')
            
        Returns:
            str: Complete CSS stylesheet for the widget
        """
        if widget_type == 'button':
            if variant == 'premium':
                return self.get_premium_button_style()
            elif variant == 'drag_drop':
                return self.get_drag_drop_button_style()
            else:
                return self.get_button_style()
        elif widget_type == 'input':
            return self.get_input_style()
        elif widget_type == 'combo':
            return self.get_combo_style()
        elif widget_type == 'tree':
            return self.get_tree_style()
        elif widget_type == 'list':
            if variant == 'drag_drop':
                return self.get_drag_drop_list_style()
            else:
                return self.get_list_style()
        elif widget_type == 'label':
            if variant == 'drag_drop':
                return self.get_drag_drop_label_style()
            elif variant == 'progress_dialog_details':
                return self.get_progress_dialog_details_style()
            else:
                return self.get_label_style()
        elif widget_type == 'scrollbar':
            return self.get_scrollbar_style()
        elif widget_type == 'progress':
            return self.get_progress_bar_style()
        else:
            return ""
    
    def apply_dimensions(self, widget, dimension_key):
        """Helper to apply dimensions to widgets.
        
        Args:
            widget: The Qt widget to apply dimensions to
            dimension_key (str): The dimension key to apply
        """
        from PyQt5.QtWidgets import QWidget
        
        if not isinstance(widget, QWidget):
            return
            
        # Handle legacy flat dimension keys
        if dimension_key in self.dimensions and not isinstance(self.dimensions[dimension_key], dict):
            value = self.dimensions[dimension_key]
            
            # Apply based on dimension key naming convention
            if 'min_height' in dimension_key:
                widget.setMinimumHeight(value)
            elif 'min_width' in dimension_key:
                widget.setMinimumWidth(value)
            elif 'maximum_height' in dimension_key or 'max_height' in dimension_key:
                widget.setMaximumHeight(value)
            elif 'maximum_width' in dimension_key or 'max_width' in dimension_key:
                widget.setMaximumWidth(value)
            elif 'minimum_width' in dimension_key:
                widget.setMinimumWidth(value)
            elif 'minimum_height' in dimension_key:
                widget.setMinimumHeight(value)
            elif 'width' in dimension_key:
                widget.setFixedWidth(value)
            elif 'height' in dimension_key:
                widget.setFixedHeight(value)
    
    def get_dat_stats_label_style(self):
        """Get style for DAT stats label."""
        return f"font-weight: {self.fonts['weight_bold']}; font-size: {self.fonts['size_small']}px; color: #909090; padding: {self.layout['stats_label_padding']}; background-color: #3e3e3e;"
    
    def get_rom_stats_label_style(self):
        """Get style for ROM stats label."""
        return f"font-weight: {self.fonts['weight_bold']}; font-size: {self.fonts['size_small']}px; color: #909090; padding: {self.layout['stats_label_padding']}; background-color: #3e3e3e;"