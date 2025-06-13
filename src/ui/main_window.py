#!/usr/bin/env python3
"""
Main Window for Romplestiltskin

Provides the primary user interface for ROM collection management.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QComboBox, QLabel, QPushButton,
    QProgressBar, QStatusBar, QMenuBar, QMenu, QFileDialog,
    QMessageBox, QGroupBox, QCheckBox, QListWidget, QListWidgetItem,
    QTabWidget, QTextEdit, QSpinBox, QLineEdit, QScrollArea, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QByteArray
from PyQt6.QtGui import QAction, QIcon, QColor, QFont

class NumericTreeWidgetItem(QTreeWidgetItem):
    """Custom QTreeWidgetItem that sorts numerically using UserRole data for the first column."""
    
    def __lt__(self, other):
        column = self.treeWidget().sortColumn() if self.treeWidget() else 0
        
        # For the first column (row numbers), use UserRole data for numeric sorting
        if column == 0:
            self_data = self.data(0, Qt.ItemDataRole.UserRole)
            other_data = other.data(0, Qt.ItemDataRole.UserRole)
            
            # If both have UserRole data, compare numerically
            if self_data is not None and other_data is not None:
                return self_data < other_data
        
        # For other columns or if no UserRole data, use default text comparison
        return super().__lt__(other)
import base64

from core.settings_manager import SettingsManager
from core.db_manager import DatabaseManager
from core.dat_processor import DATProcessor
from core.rom_scanner import ROMScanner, ROMStatus, ROMScanResult
from core.scanned_roms_manager import ScannedROMsManager
from ui.settings_dialog import SettingsDialog
from ui.progress_dialog import ProgressDialog
from ui.drag_drop_list import DragDropListWidget, RegionFilterWidget

class DATImportThread(QThread):
    """Thread for importing DAT files."""
    
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(int, int)  # successful, total
    error = pyqtSignal(str)
    
    def __init__(self, dat_processor: DATProcessor, dat_folder: str):
        super().__init__()
        self.dat_processor = dat_processor
        self.dat_folder = dat_folder
    
    def run(self):
        try:
            successful, total = self.dat_processor.import_dat_folder(self.dat_folder)
            self.finished.emit(successful, total)
        except Exception as e:
            self.error.emit(str(e))

class ROMScanThread(QThread):
    """Thread for scanning ROM folders."""
    
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(list)  # scan results
    error = pyqtSignal(str)
    
    def __init__(self, rom_scanner: ROMScanner, folder_path: str, system_id: int):
        super().__init__()
        self.rom_scanner = rom_scanner
        self.folder_path = folder_path
        self.system_id = system_id
    
    def run(self):
        try:
            def progress_callback(current, total):
                self.progress.emit(current, total)
            
            results = self.rom_scanner.scan_folder(
                self.folder_path, 
                self.system_id, 
                progress_callback
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, settings_manager: SettingsManager, db_manager: DatabaseManager):
        super().__init__()
        
        self.settings_manager = settings_manager
        self.db_manager = db_manager
        self.dat_processor = DATProcessor(db_manager)
        self.rom_scanner = ROMScanner(db_manager, settings_manager.get_chunk_size_bytes())
        self.scanned_roms_manager = ScannedROMsManager(settings_manager.get_database_path())
        
        self.current_system_id = None
        self.current_scan_results = []
        
        self.apply_adobe_theme()
        self.setup_ui()
        self.setup_menus()
        self.setup_status_bar()
        self.load_systems()
        self.restore_window_state()
        
    def apply_adobe_theme(self):
        """Apply an Adobe-like theme to the application."""
        # Define Adobe-like color palette
        self.colors = {
            'background': '#2E2E2E',
            'dark_gray': '#252525',
            'medium_gray': '#3A3A3A',
            'light_gray': '#4A4A4A',
            'highlight': '#2D8CEB',  # Adobe blue
            'highlight_hover': '#1A73E8',
            'text': '#E6E6E6',
            'secondary_text': '#BBBBBB',
            'border': '#555555',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'error': '#F44336',
            'button_text': '#FFFFFF'
        }
        
        # Create application-wide stylesheet
        self.qss = f"""
        /* Global styles */
        QWidget {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        /* Main window */
        QMainWindow {{  
            background-color: {self.colors['background']};
        }}
        
        /* Menu bar */
        QMenuBar {{  
            background-color: {self.colors['dark_gray']};
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
            color: black;
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
        }}
        
        QGroupBox::title {{  
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
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
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: bold;
            min-height: 36px;
            font-size: 13px;
        }}
        
        #premium_button:hover {{  
            background-color: {self.colors['highlight_hover']};
            /* Remove box-shadow property */
        }}
        
        /* Tree widgets */
        QTreeWidget {{  
            background-color: {self.colors['dark_gray']};
            alternate-background-color: {self.colors['medium_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
        }}
        
        QTreeWidget::item {{  
            padding: 4px;
        }}
        
        QTreeWidget::item:selected {{  
            background-color: {self.colors['highlight']};
            color: black;
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
        }}
        
        /* Tabs */
        QTabWidget::pane {{  
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
        }}
        
        QTabBar::tab {{  
            background-color: {self.colors['medium_gray']};
            color: {self.colors['text']};
            border: 1px solid {self.colors['border']};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 12px;
            min-width: 100px;
        }}
        
        QTabBar::tab:selected {{  
            background-color: {self.colors['highlight']};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{  
            background-color: {self.colors['dark_gray']};
            width: 12px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{  
            background-color: {self.colors['light_gray']};
            min-height: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{  
            height: 0px;
        }}
        
        QScrollBar:horizontal {{  
            background-color: {self.colors['dark_gray']};
            height: 12px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{  
            background-color: {self.colors['light_gray']};
            min-width: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{  
            width: 0px;
        }}
        
        /* Checkboxes */
        QCheckBox {{  
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{  
            width: 18px;
            height: 18px;
            border: 1px solid {self.colors['border']};
            border-radius: 3px;
            background-color: {self.colors['medium_gray']};
        }}
        
        QCheckBox::indicator:checked {{  
            background-color: {self.colors['highlight']};
        }}
        
        /* Progress bar */
        QProgressBar {{  
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            background-color: {self.colors['dark_gray']};
            text-align: center;
            color: {self.colors['text']};
        }}
        
        QProgressBar::chunk {{  
            background-color: {self.colors['highlight']};
            width: 10px;
            margin: 0.5px;
        }}
        
        /* Text edit */
        QTextEdit {{  
            background-color: {self.colors['dark_gray']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
        }}
        """
    
    def get_stylesheet(self):
        """Get the application stylesheet."""
        return self.qss
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Romplestiltskin - ROM Collection Manager")
        self.setMinimumSize(1400, 900)  # Increased size to accommodate larger region filter
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # System selection
        controls_layout.addWidget(QLabel("System:"))
        self.system_combo = QComboBox()
        self.system_combo.setMinimumWidth(300)  # Set minimum width for longer system names
        self.system_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.system_combo.currentTextChanged.connect(self.on_system_changed)
        controls_layout.addWidget(self.system_combo)
        
        controls_layout.addStretch()
        
        # Action buttons with premium styling
        self.scan_button = QPushButton("📂 Scan ROM Folder")
        self.scan_button.setObjectName("premium_button")
        self.scan_button.clicked.connect(self.scan_rom_folder)
        controls_layout.addWidget(self.scan_button)
        
        self.import_dat_button = QPushButton("📥 Import DAT Files")
        self.import_dat_button.setObjectName("premium_button")
        self.import_dat_button.clicked.connect(self.import_dat_files)
        controls_layout.addWidget(self.import_dat_button)
        
        self.clear_rom_data_button = QPushButton("🗑️ Clear ROM Data")
        self.clear_rom_data_button.setObjectName("premium_button")
        self.clear_rom_data_button.clicked.connect(self.clear_rom_data)
        controls_layout.addWidget(self.clear_rom_data_button)
        
        main_layout.addLayout(controls_layout)
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - DAT games
        left_panel = self.create_dat_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - User ROMs
        right_panel = self.create_rom_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([600, 600])
        main_layout.addWidget(content_splitter)
        
        # Bottom panel - Filters and actions
        bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(bottom_panel)
    
    def create_dat_panel(self) -> QWidget:
        """Create the DAT games panel."""
        panel = QGroupBox("DAT Games")
        layout = QVBoxLayout(panel)
        
        # Games tree
        self.dat_tree = QTreeWidget()
        self.dat_tree.setHeaderLabels([
            "#", "Game Name", "Region", "Language", "Size", "CRC32"
        ])
        self.dat_tree.setAlternatingRowColors(True)
        self.dat_tree.setSortingEnabled(True)
        self.dat_tree.setMinimumHeight(300)  # Reduced height
        self.dat_tree.setMaximumHeight(350)  # Prevent excessive growth
        # Make game name column wider (now at index 1)
        self.dat_tree.setColumnWidth(1, 300)
        # Make # column narrower
        self.dat_tree.setColumnWidth(0, 50)
        layout.addWidget(self.dat_tree)
        
        # Stats with detailed feedback
        self.dat_stats_label = QLabel("Total: 0 | Filtered Out: 0 | Showing: 0")
        self.dat_stats_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.dat_stats_label)
        
        return panel
    
    def create_rom_panel(self) -> QWidget:
        """Create the user ROMs panel with tabs for current and missing ROMs."""
        panel = QGroupBox("User ROMs")
        layout = QVBoxLayout(panel)
        
        # Create tab widget
        self.rom_tabs = QTabWidget()
        
        # Correct ROMs tab
        correct_tab = QWidget()
        correct_layout = QVBoxLayout(correct_tab)
        
        # Correct ROMs tree
        self.correct_tree = QTreeWidget()
        self.correct_tree.setHeaderLabels([
            "#", "Game Name", "Region", "Language", "CRC32"
        ])
        self.correct_tree.setAlternatingRowColors(True)
        self.correct_tree.setSortingEnabled(True)
        self.correct_tree.setMinimumHeight(250)  # Reduced height
        self.correct_tree.setMaximumHeight(300)  # Prevent excessive growth
        self.correct_tree.setColumnWidth(0, 50)  # # column
        self.correct_tree.setColumnWidth(1, 300)  # Game name column
        self.correct_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)  # Allow multiple selection
        correct_layout.addWidget(self.correct_tree)
        
        # Missing ROMs tab
        missing_tab = QWidget()
        missing_layout = QVBoxLayout(missing_tab)
        
        # Missing ROMs tree
        self.missing_tree = QTreeWidget()
        self.missing_tree.setHeaderLabels([
            "#", "Game Name", "Region", "Language", "CRC32"
        ])
        self.missing_tree.setAlternatingRowColors(True)
        self.missing_tree.setSortingEnabled(True)
        self.missing_tree.setMinimumHeight(250)  # Reduced height
        self.missing_tree.setMaximumHeight(300)  # Prevent excessive growth
        self.missing_tree.setColumnWidth(0, 50)  # # column
        self.missing_tree.setColumnWidth(1, 300)  # Game name column
        self.missing_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)  # Allow multiple selection
        missing_layout.addWidget(self.missing_tree)
        
        # Unrecognized ROMs tab
        unrecognized_tab = QWidget()
        unrecognized_layout = QVBoxLayout(unrecognized_tab)
        
        # Unrecognized ROMs tree
        self.unrecognized_tree = QTreeWidget()
        self.unrecognized_tree.setHeaderLabels([
            "#", "File Name", "CRC32"
        ])
        self.unrecognized_tree.setAlternatingRowColors(True)
        self.unrecognized_tree.setSortingEnabled(True)
        self.unrecognized_tree.setMinimumHeight(250)  # Reduced height
        self.unrecognized_tree.setMaximumHeight(300)  # Prevent excessive growth
        self.unrecognized_tree.setColumnWidth(0, 50)  # # column
        self.unrecognized_tree.setColumnWidth(1, 300)  # Filename column
        self.unrecognized_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        unrecognized_layout.addWidget(self.unrecognized_tree)
        
        # Broken ROMs tab
        broken_tab = QWidget()
        broken_layout = QVBoxLayout(broken_tab)
        
        # Broken ROMs tree
        self.broken_tree = QTreeWidget()
        self.broken_tree.setHeaderLabels([
            "#", "File Name", "Error"
        ])
        self.broken_tree.setAlternatingRowColors(True)
        self.broken_tree.setSortingEnabled(True)
        self.broken_tree.setMinimumHeight(250)  # Reduced height
        self.broken_tree.setMaximumHeight(300)  # Prevent excessive growth
        self.broken_tree.setColumnWidth(0, 50)  # # column
        self.broken_tree.setColumnWidth(1, 300)  # Filename column
        self.broken_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        broken_layout.addWidget(self.broken_tree)
        
        # Add tabs to the tab widget
        self.rom_tabs.addTab(correct_tab, "Correct ROMs")
        self.rom_tabs.addTab(missing_tab, "Missing ROMs")
        self.rom_tabs.addTab(unrecognized_tab, "Unrecognized ROMs")
        self.rom_tabs.addTab(broken_tab, "Broken ROMs")
        layout.addWidget(self.rom_tabs)
        
        # Stats with detailed feedback
        self.rom_stats_label = QLabel("Total DAT: 0 | Matching: 0 | Missing: 0 | Unrecognised: 0 | Broken: 0 | Total ROMs: 0")
        self.rom_stats_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.rom_stats_label)
        
        return panel
    
    def create_bottom_panel(self) -> QWidget:
        """Create the bottom panel with filters and actions."""
        panel = QWidget()
        panel.setMaximumHeight(300)  # Limit height to prevent overlap
        layout = QHBoxLayout(panel)
        layout.setSpacing(10)
        
        # Filter panel with improved styling
        filter_group = QGroupBox("🔍 Filters")
        filter_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        filter_layout = QHBoxLayout(filter_group)  # Changed to horizontal
        filter_layout.setSpacing(15)
        
        # Region filters with drag-and-drop
        self.region_filter = RegionFilterWidget(self.settings_manager)
        self.region_filter.filters_changed.connect(self.apply_filters)
        filter_layout.addWidget(self.region_filter)
        
        # Language filters with scroll area and controls
        language_group = QGroupBox("🗣️ Languages")
        language_scroll = QScrollArea()
        language_scroll.setMaximumHeight(120)
        language_scroll.setWidgetResizable(True)
        language_widget = QWidget()
        self.language_filter_layout = QVBoxLayout(language_widget)
        self.language_filter_layout.setSpacing(2)
        self.language_checkboxes = {}
        language_scroll.setWidget(language_widget)
        
        language_layout = QVBoxLayout(language_group)
        language_layout.addWidget(language_scroll)
        
        # Language control buttons
        lang_button_layout = QHBoxLayout()
        self.select_all_languages_button = QPushButton("✅ Select All")
        self.select_all_languages_button.clicked.connect(self.select_all_languages)
        self.select_all_languages_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.clear_all_languages_button = QPushButton("❌ Clear All")
        self.clear_all_languages_button.clicked.connect(self.clear_all_languages)
        self.clear_all_languages_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        lang_button_layout.addWidget(self.select_all_languages_button)
        lang_button_layout.addWidget(self.clear_all_languages_button)
        lang_button_layout.addStretch()
        language_layout.addLayout(lang_button_layout)
        
        filter_layout.addWidget(language_group)
        
        # Type filter checkboxes - all start checked
        type_group = QGroupBox("🎮 Game Types")
        type_layout = QVBoxLayout(type_group)
        type_layout.setSpacing(5)
        
        filter_row1 = QHBoxLayout()
        filter_row1.setSpacing(10)
        self.show_beta_cb = QCheckBox("Beta")
        self.show_demo_cb = QCheckBox("Demo")
        self.show_proto_cb = QCheckBox("Proto")
        self.show_unlicensed_cb = QCheckBox("Unlicensed")
        
        # Set all checkboxes to checked by default
        self.show_beta_cb.setChecked(True)
        self.show_demo_cb.setChecked(True)
        self.show_proto_cb.setChecked(True)
        self.show_unlicensed_cb.setChecked(True)
        
        # Connect checkboxes to auto-apply filters
        self.show_beta_cb.toggled.connect(self.apply_filters)
        self.show_demo_cb.toggled.connect(self.apply_filters)
        self.show_proto_cb.toggled.connect(self.apply_filters)
        self.show_unlicensed_cb.toggled.connect(self.apply_filters)
        
        filter_row1.addWidget(self.show_beta_cb)
        filter_row1.addWidget(self.show_demo_cb)
        filter_row1.addWidget(self.show_proto_cb)
        filter_row1.addWidget(self.show_unlicensed_cb)
        type_layout.addLayout(filter_row1)
        
        filter_row2 = QHBoxLayout()
        filter_row2.setSpacing(10)
        self.show_translation_cb = QCheckBox("Translations")
        self.show_modified_cb = QCheckBox("Modified")
        self.show_overdump_cb = QCheckBox("Overdumps")
        
        # Set all checkboxes to checked by default
        self.show_translation_cb.setChecked(True)
        self.show_modified_cb.setChecked(True)
        self.show_overdump_cb.setChecked(True)
        
        # Connect checkboxes to auto-apply filters
        self.show_translation_cb.toggled.connect(self.apply_filters)
        self.show_modified_cb.toggled.connect(self.apply_filters)
        self.show_overdump_cb.toggled.connect(self.apply_filters)
        
        filter_row2.addWidget(self.show_translation_cb)
        filter_row2.addWidget(self.show_modified_cb)
        filter_row2.addWidget(self.show_overdump_cb)
        type_layout.addLayout(filter_row2)
        
        # Game type control buttons
        button_layout = QHBoxLayout()
        
        self.select_all_types_button = QPushButton("✅ Select All Types")
        self.select_all_types_button.clicked.connect(self.select_all_game_types)
        self.select_all_types_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.clear_all_types_button = QPushButton("❌ Clear All Types")
        self.clear_all_types_button.clicked.connect(self.clear_all_game_types)
        self.clear_all_types_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        button_layout.addWidget(self.select_all_types_button)
        button_layout.addWidget(self.clear_all_types_button)
        button_layout.addStretch()
        type_layout.addLayout(button_layout)
        
        filter_layout.addWidget(type_group)
        
        layout.addWidget(filter_group)
        
        # Actions panel with premium styling
        actions_group = QGroupBox("🛠️ Actions")
        actions_group.setStyleSheet(f"""
            QGroupBox {{{{  
                font-weight: bold;
                border: 2px solid {{self.colors['border']}};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}}}
            QGroupBox::title {{{{  
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}}}
        """)
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)
        
        self.rename_button = QPushButton("✏️ Rename Wrong Filenames")
        self.rename_button.setObjectName("premium_button")
        self.rename_button.clicked.connect(self.rename_wrong_filenames)
        actions_layout.addWidget(self.rename_button)
        
        self.move_extra_button = QPushButton("📦 Move Extra Files")
        self.move_extra_button.setObjectName("premium_button")
        self.move_extra_button.clicked.connect(self.move_extra_files)
        actions_layout.addWidget(self.move_extra_button)
        
        self.move_broken_button = QPushButton("🔧 Move Broken Files")
        self.move_broken_button.setObjectName("premium_button")
        self.move_broken_button.clicked.connect(self.move_broken_files)
        actions_layout.addWidget(self.move_broken_button)
        
        self.export_missing_button = QPushButton("📋 Export Missing List")
        self.export_missing_button.setObjectName("premium_button")
        self.export_missing_button.clicked.connect(self.export_missing_list)
        actions_layout.addWidget(self.export_missing_button)
        
        layout.addWidget(actions_group)
        
        return panel
    
    def setup_menus(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        import_action = QAction("Import DAT Files...", self)
        import_action.triggered.connect(self.import_dat_files)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        scan_action = QAction("Scan ROM Folder...", self)
        scan_action.triggered.connect(self.scan_rom_folder)
        tools_menu.addAction(scan_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Ready")
    
    def load_systems(self):
        """Load systems from database into combo box."""
        self.system_combo.clear()
        systems = self.db_manager.get_all_systems()
        
        for system in systems:
            self.system_combo.addItem(system['system_name'], system['id'])
        
        if systems:
            # Try to restore last selected system
            last_system = self.settings_manager.get("last_selected_system")
            if last_system:
                index = self.system_combo.findText(last_system)
                if index >= 0:
                    self.system_combo.setCurrentIndex(index)
    
    def on_system_changed(self, system_name: str):
        """Handle system selection change."""
        if not system_name:
            return
        
        # Save selection
        self.settings_manager.set("last_selected_system", system_name)
        self.settings_manager.save_settings()
        
        # Get system ID
        system_data = self.system_combo.currentData()
        if system_data:
            self.current_system_id = system_data
            
            # Clear ROM tree and scan results when changing systems
        self.correct_tree.clear()
        self.missing_tree.clear()
        self.unrecognized_tree.clear()
        self.broken_tree.clear()
        self.current_scan_results = []
        
        # Load DAT games and update filters
        self.load_dat_games()
        self.update_filter_options()
        self.apply_filters()
        
        # Check if there are existing scan results in database for this system
        if hasattr(self, 'scanned_roms_manager'):
            scan_summary = self.scanned_roms_manager.get_scan_summary(self.current_system_id)
            if scan_summary['total'] > 0:
                # Load existing scan results from database
                self.update_correct_roms()
                self.update_missing_roms()
                self.update_unrecognized_roms()
                self.update_broken_roms()
                self.update_rom_stats()
            else:
                self.rom_stats_label.setText("No ROMs scanned")
        else:
            self.rom_stats_label.setText("No ROMs scanned")
    
    def load_dat_games(self):
        """Load DAT games for current system."""
        if not self.current_system_id:
            return
        
        # Store all games for filtering
        self.all_games = self.db_manager.get_games_by_system(self.current_system_id)
        
        # Initial display of all games
        self.dat_tree.clear()
        for i, game in enumerate(self.all_games, 1):
            item = NumericTreeWidgetItem([
                str(i),  # Display without leading zeros
                game['major_name'],
                game['region'] or '',
                game['languages'] or '',
                str(game['size']),
                game['crc32']
            ])
            # Store numeric value for proper sorting
            item.setData(0, Qt.ItemDataRole.UserRole, i)
            
            # Color coding based on status
            if game['is_verified_dump']:
                item.setBackground(0, QColor(200, 255, 200))  # Light green
                item.setForeground(0, QColor(0, 0, 0))  # Black text
            
            self.dat_tree.addTopLevelItem(item)
        
        # Update stats with detailed feedback
        total_count = len(self.all_games)
        self.dat_stats_label.setText(f"<b>Total:</b> {total_count} | <b>Filtered out:</b> 0 | <b>Showing:</b> {total_count}")
    
    def import_dat_files(self):
        """Import DAT files from folder."""
        dat_folder = self.settings_manager.get_dat_folder_path()
        if not dat_folder:
            dat_folder = str(Path.home())
        
        folder = QFileDialog.getExistingDirectory(
            self, "Select DAT Folder", dat_folder
        )
        
        if folder:
            self.settings_manager.set_dat_folder_path(folder)
            self.settings_manager.save_settings()
            
            # Start import in background thread
            self.import_thread = DATImportThread(self.dat_processor, folder)
            self.import_thread.finished.connect(self.on_import_finished)
            self.import_thread.error.connect(self.on_import_error)
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.status_bar.showMessage("Importing DAT files...")
            
            self.import_thread.start()
    
    def on_import_finished(self, successful: int, total: int):
        """Handle DAT import completion."""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Imported {successful}/{total} DAT files")
        
        # Reload systems
        self.load_systems()
        
        # Update filters if a system is selected
        if self.current_system_id:
            self.update_filter_options()
            self.apply_filters()
        
        QMessageBox.information(
            self, "Import Complete",
            f"Successfully imported {successful} out of {total} DAT files."
        )
    
    def on_import_error(self, error_message: str):
        """Handle DAT import error."""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Import failed")
        
        QMessageBox.critical(
            self, "Import Error",
            f"Error importing DAT files:\n{error_message}"
        )
    
    def scan_rom_folder(self):
        """Scan ROM folder for current system."""
        if not self.current_system_id:
            QMessageBox.warning(
                self, "No System Selected",
                "Please select a system first."
            )
            return
        
        # Get previously used folder for this system, if any
        system_folders = self.settings_manager.get_system_rom_folders(str(self.current_system_id))
        default_folder = system_folders[0] if system_folders else str(Path.home())
        
        folder = QFileDialog.getExistingDirectory(
            self, "Select ROM Folder", default_folder
        )
        
        if folder:
            # Save the folder path for this system
            self.settings_manager.add_system_rom_folder(str(self.current_system_id), folder)
            self.settings_manager.save_settings()
            
            # Start scan in background thread
            self.scan_thread = ROMScanThread(
                self.rom_scanner, folder, self.current_system_id
            )
            self.scan_thread.progress.connect(self.on_scan_progress)
            self.scan_thread.finished.connect(self.on_scan_finished)
            self.scan_thread.error.connect(self.on_scan_error)
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
            self.status_bar.showMessage("Scanning ROM folder...")
            
            self.scan_thread.start()
    
    def on_scan_progress(self, current: int, total: int):
        """Handle scan progress update."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
    
    def on_scan_finished(self, results: List[ROMScanResult]):
        """Handle scan completion."""
        self.progress_bar.setVisible(False)
        self.current_scan_results = results
        
        # Store scan results in database for persistent filtering
        if self.current_system_id:
            self.scanned_roms_manager.store_scan_results(self.current_system_id, results)
        
        # Update ROM tree
        self.update_correct_roms()
        
        # Update missing ROMs tab
        self.update_missing_roms()
        
        # Update unrecognized and broken ROM tabs (they will use database now)
        self.update_unrecognized_roms()
        self.update_broken_roms()
        
        # Update stats using the proper ROM stats method
        self.update_rom_stats()
        
        self.status_bar.showMessage(f"Scanned {len(results)} files")
        
        # Switch to the Correct ROMs tab
        self.rom_tabs.setCurrentIndex(0)
    
    def clear_rom_data(self):
        """Clear all ROM data for the current system."""
        if not self.current_system_id:
            QMessageBox.warning(
                self, "No System Selected",
                "Please select a system first."
            )
            return
        
        # Get system name for confirmation dialog
        system_name = self.system_combo.currentText()
        
        # Confirm the action
        reply = QMessageBox.question(
            self, "Clear ROM Data",
            f"Are you sure you want to clear all ROM data for {system_name}?\n\n"
            f"This will remove all scanned ROM information and cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear ROM data from database
                self.scanned_roms_manager.clear_system_scans(self.current_system_id)
                
                # Clear current scan results
                self.current_scan_results = []
                
                # Update all ROM-related UI elements
                self.update_correct_roms()
                self.update_missing_roms()
                self.update_unrecognized_roms()
                self.update_broken_roms()
                
                # Reset stats
                self.rom_stats_label.setText("No ROMs scanned")
                
                # Update status
                self.status_bar.showMessage(f"Cleared ROM data for {system_name}")
                
                QMessageBox.information(
                    self, "ROM Data Cleared",
                    f"All ROM data for {system_name} has been cleared."
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Error clearing ROM data: {str(e)}"
                )
    
    def on_scan_error(self, error_message: str):
        """Handle scan error."""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Scan failed")
        
        QMessageBox.critical(
            self, "Scan Error",
            f"Error scanning ROM folder:\n{error_message}"
        )
    

            
    def update_correct_roms(self):
        """Update the correct ROMs tab based on current DAT filters."""
        self.correct_tree.clear()
        
        current_system_id = self.system_combo.currentData()
        if current_system_id is None:
            return
        
        # Get the currently visible games in the DAT tree (filtered games)
        visible_crcs = set()
        for i in range(self.dat_tree.topLevelItemCount()):
            item = self.dat_tree.topLevelItem(i)
            crc32 = item.text(5)  # CRC is in column 5 (#, Game Name, Region, Language, Size, CRC32)
            if crc32:
                visible_crcs.add(crc32)
        
        # Get correct ROMs that match visible games
        correct_games = []
        row_number = 0
        
        # Use database if available, otherwise fall back to memory results
        if hasattr(self, 'scanned_roms_manager') and self.scanned_roms_manager.get_all_scanned_roms(current_system_id):
            all_scanned_roms = self.scanned_roms_manager.get_all_scanned_roms(current_system_id)
            for rom_data in all_scanned_roms:
                # Only include correct ROMs
                if rom_data['status'] == 'correct':
                    matched_crc32 = rom_data.get('matched_game_crc32')
                    # Only show if the matched game is visible in current filters
                    if matched_crc32 and matched_crc32 in visible_crcs:
                        # Find the full game details from self.all_games for display
                        game_details = next((g for g in self.all_games if g.get('crc32') == matched_crc32), None)
                        if game_details:
                            correct_games.append(game_details)
                            row_number += 1
                            item = NumericTreeWidgetItem([
                                str(row_number),  # Display without leading zeros
                                game_details['major_name'],
                                game_details.get('region', ''),
                                game_details.get('languages', ''),
                                game_details['crc32']
                            ])
                            # Store numeric value for proper sorting
                            item.setData(0, Qt.ItemDataRole.UserRole, row_number)
                            self.correct_tree.addTopLevelItem(item)
        elif hasattr(self, 'current_scan_results') and self.current_scan_results:
            for result in self.current_scan_results:
                # Only include correct ROMs
                if result.status.value == 'correct' and result.matched_game:
                    matched_crc32 = result.matched_game.get('crc32')
                    # Only show if the matched game is visible in current filters
                    if matched_crc32 and matched_crc32 in visible_crcs:
                        game_details = result.matched_game
                        correct_games.append(game_details)
                        row_number += 1
                        item = NumericTreeWidgetItem([
                            str(row_number),  # Display without leading zeros
                            game_details['major_name'],
                            game_details.get('region', ''),
                            game_details.get('languages', ''),
                            game_details['crc32']
                        ])
                        # Store numeric value for proper sorting
                        item.setData(0, Qt.ItemDataRole.UserRole, row_number)
                        self.correct_tree.addTopLevelItem(item)
        
        # Sort by game name alphabetically
        self.correct_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
    
    def update_missing_roms(self):
        """Update the missing ROMs tab with games that are in the DAT but not found in the scan."""
        if not hasattr(self, 'all_games') or not self.all_games:
            return
            
        self.missing_tree.clear()
        
        current_system_id = self.system_combo.currentData()
        if current_system_id is None:
            return
        
        # Get all matched games from scan results
        matched_crcs = set()
        if hasattr(self, 'scanned_roms_manager'):
            # Use database to get matched CRCs
            all_scanned_roms = self.scanned_roms_manager.get_all_scanned_roms(current_system_id)
            for rom_data in all_scanned_roms:
                if rom_data.get('matched_game_crc32'):
                    matched_crcs.add(rom_data['matched_game_crc32'])
        elif self.current_scan_results:
            # Fallback to memory results
            for result in self.current_scan_results:
                if result.matched_game and result.matched_game.get('crc32'):
                    matched_crcs.add(result.matched_game['crc32'])
        
        # Find missing games - only include games that pass the current filters
        missing_games = []
        visible_games = []
        
        # Get the currently visible games in the DAT tree
        for i in range(self.dat_tree.topLevelItemCount()):
            item = self.dat_tree.topLevelItem(i)
            game_name = item.text(1)  # Game name is now in column 1 (#, Game Name, Region, Language, Size, CRC32)
            crc32 = item.text(5)  # CRC is in column 5 (#, Game Name, Region, Language, Size, CRC32)
            visible_games.append((game_name, crc32))
        
        # Iterate through games currently visible in the DAT tree
        # and check if they are missing from the scan results.
        row_number = 0
        for game_name, crc32 in visible_games:
            if crc32 and crc32 not in matched_crcs:
                # Find the full game details from self.all_games for display
                # This assumes crc32 is unique enough for a quick lookup if needed,
                # or that visible_games could store more complete game objects.
                # For now, we'll retrieve it; consider optimizing if self.all_games is huge.
                game_details = next((g for g in self.all_games if g.get('crc32') == crc32), None)
                if game_details:
                    missing_games.append(game_details)
                    row_number += 1
                    item = NumericTreeWidgetItem([
                        str(row_number),  # Display without leading zeros
                        game_details['major_name'],
                        game_details.get('region', ''),
                        game_details.get('languages', ''),
                        game_details['crc32']
                    ])
                    # Store numeric value for proper sorting
                    item.setData(0, Qt.ItemDataRole.UserRole, row_number)
                    self.missing_tree.addTopLevelItem(item)
        
        # Sort by game name alphabetically
        self.missing_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
            
        # Update summary with missing count
        if hasattr(self, 'rom_scanner') and hasattr(self, 'current_scan_results'):
            summary = self.rom_scanner.get_scan_summary(self.current_scan_results)
            summary['missing'] = len(missing_games)
            
            # Note: ROM stats label is now updated by update_rom_stats() method
            # which is called after this method in apply_filters()
            pass
    
    def apply_filters(self):
        """Apply filters to DAT games list and update feedback counters."""
        if not hasattr(self, 'all_games') or not self.all_games:
            return
        
        # Get region filtering configuration
        priority_regions = self.region_filter.get_region_priority()
        ignored_regions = self.region_filter.get_ignored_regions()
        remove_duplicates = self.region_filter.should_remove_duplicates()
        
        # Initialize duplicate tracking if needed
        if remove_duplicates:
            self.seen_games = set()
        
        checked_languages = set()
        for language, checkbox in self.language_checkboxes.items():
            if checkbox.isChecked():
                checked_languages.add(language)
        
        # Get type filter settings
        show_beta = self.show_beta_cb.isChecked()
        show_demo = self.show_demo_cb.isChecked()
        show_proto = self.show_proto_cb.isChecked()
        show_unlicensed = self.show_unlicensed_cb.isChecked()
        show_translation = self.show_translation_cb.isChecked()
        show_modified = self.show_modified_cb.isChecked()
        show_overdump = self.show_overdump_cb.isChecked()
        
        # Clear and repopulate DAT tree
        self.dat_tree.clear()
        total_games = len(self.all_games)
        filtered_out = 0
        showing = 0
        
        # Sort games by region priority if removing duplicates
        games_to_process = self.all_games
        if remove_duplicates:
            # Create a priority map for regions
            region_priority_map = {region: idx for idx, region in enumerate(priority_regions)}
            # Sort games by region priority (lower index = higher priority)
            games_to_process = sorted(self.all_games, key=lambda g: region_priority_map.get(g.get('region', 'Unknown'), 999))
        
        for game in games_to_process:
            # Extract game info
            game_name = game.get('major_name', '')
            region = game.get('region', 'Unknown')
            languages = game.get('languages', 'Unknown')
            
            # Apply region filter - filter out if region is in ignored list
            if region in ignored_regions:
                filtered_out += 1
                continue
                
            # If we're removing duplicates, check if we've already seen this game name in a higher priority region
            if remove_duplicates and hasattr(self, 'seen_games'):
                game_name_base = game_name.split(' (')[0] if ' (' in game_name else game_name  # Get base name without region
                if game_name_base in self.seen_games:
                    filtered_out += 1
                    continue
                self.seen_games.add(game_name_base)
            
            # Apply language filter - filter out if no languages match
            game_languages = set()
            if languages and languages != 'Unknown':
                # Split multiple languages if comma-separated
                game_languages = set(lang.strip() for lang in languages.split(','))
            else:
                # Use default language based on region instead of Unknown
                region_defaults = {
                    'USA': 'English',
                    'Europe': 'English', 
                    'Japan': 'Japanese',
                    'World': 'English',
                    'Asia': 'English',
                    'Korea': 'Korean',
                    'China': 'Chinese',
                    'Taiwan': 'Chinese',
                    'Brazil': 'Portuguese',
                    'Spain': 'Spanish',
                    'France': 'French',
                    'Germany': 'German',
                    'Italy': 'Italian'
                }
                default_lang = region_defaults.get(region, 'English')
                game_languages.add(default_lang)
            
            # Check if any of the game's languages are checked
            if not game_languages.intersection(checked_languages):
                filtered_out += 1
                continue
            
            # Apply type filters - filter out based on database fields
            if not show_beta and game.get('is_beta', False):
                filtered_out += 1
                continue
            
            if not show_demo and game.get('is_demo', False):
                filtered_out += 1
                continue
            
            if not show_proto and game.get('is_proto', False):
                filtered_out += 1
                continue
            
            if not show_unlicensed and game.get('is_unlicensed', False):
                filtered_out += 1
                continue
            
            if not show_translation and game.get('is_unofficial_translation', False):
                filtered_out += 1
                continue
            
            if not show_modified and game.get('is_modified_release', False):
                filtered_out += 1
                continue
            
            if not show_overdump and game.get('is_overdump', False):
                filtered_out += 1
                continue
            
            # Game passes all filters, add to tree
            showing += 1
            item = NumericTreeWidgetItem([
                str(showing),  # Display without leading zeros
                game_name,
                region,
                languages,
                str(game.get('size', 0)),
                game.get('crc32', '')
            ])
            # Store numeric value for proper sorting
            item.setData(0, Qt.ItemDataRole.UserRole, showing)
            
            # No color coding - remove green highlighting
            
            self.dat_tree.addTopLevelItem(item)
        
        # Sort by game name alphabetically
        self.dat_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
        
        # Update DAT stats with bold formatting
        self.dat_stats_label.setText(f"<b>Total:</b> {total_games} | <b>Filtered out:</b> {filtered_out} | <b>Showing:</b> {showing}")
        
        # Update ROM stats if we have scan results (either in memory or database)
        current_system_id = self.system_combo.currentData()
        has_scan_results = (hasattr(self, 'current_scan_results') and self.current_scan_results) or \
                          (hasattr(self, 'scanned_roms_manager') and current_system_id)
        
        if has_scan_results:
            # Update all ROM tabs to reflect the new filter settings
            scan_results = getattr(self, 'current_scan_results', None)
            self.update_correct_roms()  # Update Correct ROMs tab
            self.update_rom_stats()
            self.update_missing_roms()
            
            # Update unrecognized and broken ROM tabs (they will use database if available)
            self.update_unrecognized_roms()
            self.update_broken_roms()
            
            # Force UI update to ensure all trees refresh
            QApplication.processEvents()
    
    def update_unrecognized_roms(self, results: List[ROMScanResult] = None):
        """Update the unrecognized ROMs tab with ROMs that are not in the DAT.
        
        Filters unrecognized ROMs by the currently selected system.
        """
        self.unrecognized_tree.clear()
        current_system_id = self.system_combo.currentData()
        if current_system_id is None:
            return # No system selected, so nothing to show

        # Use database if available, otherwise fall back to memory results
        row_number = 0
        if hasattr(self, 'scanned_roms_manager'):
            scanned_roms = self.scanned_roms_manager.get_scanned_roms_by_status(
                current_system_id, ROMStatus.NOT_RECOGNIZED
            )
            
            for rom_data in scanned_roms:
                filename = Path(rom_data['file_path']).name
                row_number += 1
                item = NumericTreeWidgetItem([
                    str(row_number),  # Display without leading zeros
                    filename,
                    rom_data['calculated_crc32'] or ''
                ])
                # Store numeric value for proper sorting
                item.setData(0, Qt.ItemDataRole.UserRole, row_number)
                self.unrecognized_tree.addTopLevelItem(item)
        elif results:
            # Fallback to memory results
            for result in results:
                if result.status == ROMStatus.NOT_RECOGNIZED and result.system_id == current_system_id:
                    filename = Path(result.file_path).name
                    row_number += 1
                    item = NumericTreeWidgetItem([
                        str(row_number),  # Display without leading zeros
                        filename,
                        result.calculated_crc32 or ''
                    ])
                    # Store numeric value for proper sorting
                    item.setData(0, Qt.ItemDataRole.UserRole, row_number)
                    self.unrecognized_tree.addTopLevelItem(item)
        
        # Sort by file name alphabetically
        self.unrecognized_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
    
    def update_broken_roms(self, results: List[ROMScanResult] = None):
        """Update the broken ROMs tab with ROMs that are corrupted or unreadable.

        Filters broken ROMs by the currently selected system.
        """
        self.broken_tree.clear()
        current_system_id = self.system_combo.currentData()
        if current_system_id is None:
            return # No system selected, so nothing to show

        # Use database if available, otherwise fall back to memory results
        row_number = 0
        if hasattr(self, 'scanned_roms_manager'):
            scanned_roms = self.scanned_roms_manager.get_scanned_roms_by_status(
                current_system_id, ROMStatus.BROKEN
            )
            
            for rom_data in scanned_roms:
                filename = Path(rom_data['file_path']).name
                error_msg = rom_data.get('error_message') or "Corrupted or unreadable"
                row_number += 1
                
                item = NumericTreeWidgetItem([
                    str(row_number),  # Display without leading zeros
                    filename,
                    error_msg
                ])
                # Store numeric value for proper sorting
                item.setData(0, Qt.ItemDataRole.UserRole, row_number)
                self.broken_tree.addTopLevelItem(item)
        elif results:
            # Fallback to memory results
            for result in results:
                if result.status == ROMStatus.BROKEN and result.system_id == current_system_id:
                    filename = Path(result.file_path).name
                    error_msg = "Corrupted or unreadable"
                    if hasattr(result, 'error_message') and result.error_message:
                        error_msg = result.error_message
                    row_number += 1
                    
                    item = NumericTreeWidgetItem([
                        str(row_number),  # Display without leading zeros
                        filename,
                        error_msg
                    ])
                    # Store numeric value for proper sorting
                    item.setData(0, Qt.ItemDataRole.UserRole, row_number)
                    self.broken_tree.addTopLevelItem(item)
        
        # Sort by file name alphabetically
        self.broken_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
    
    def update_rom_stats(self):
        """Update ROM statistics display."""
        current_system_id = self.system_combo.currentData()
        if current_system_id is None:
            self.rom_stats_label.setText("<b>No system selected</b>")
            return
        
        # Get the currently visible games in the DAT tree (filtered games)
        visible_crcs = set()
        for i in range(self.dat_tree.topLevelItemCount()):
            item = self.dat_tree.topLevelItem(i)
            crc32 = item.text(5)  # CRC is in column 5 (#, Game Name, Region, Language, Size, CRC32)
            if crc32:
                visible_crcs.add(crc32)
        
        total_dat_games = len(visible_crcs)
        
        # Prioritize memory results over database results
        if hasattr(self, 'current_scan_results') and self.current_scan_results:
            # Use memory results
            system_results = [r for r in self.current_scan_results if r.system_id == current_system_id]
            
            if not system_results:
                self.rom_stats_label.setText(f"<b>Total DAT:</b> {total_dat_games} | <b>Matching:</b> 0 | <b>Missing:</b> {total_dat_games} | <b>Unrecognised:</b> 0 | <b>Broken:</b> 0 | <b>Total ROMs:</b> 0")
                return
            
            matching_count = 0
            matched_crcs = set()
            unrecognised_count = 0
            broken_count = 0
            
            # First count all ROMs by status (independent of filtering)
            for result in system_results:
                if result.status == 'not_recognized':
                    unrecognised_count += 1
                elif result.status == 'broken':
                    broken_count += 1
                elif result.status == 'correct' or result.status == 'wrong_filename':
                    # For matching ROMs, collect unique CRC32s that are in the filtered DAT
                    if result.matched_game and 'crc32' in result.matched_game:
                        rom_crc = result.matched_game['crc32']
                        if rom_crc in visible_crcs:
                            matched_crcs.add(rom_crc)
            
            # Matching count is the number of unique CRC32s matched (same logic as missing count)
            matching_count = len(matched_crcs)
            
            # Calculate missing ROMs (those in filtered DAT but not matched)
            missing_count = total_dat_games - len(matched_crcs)
            
            # Total ROMs is the count of in-memory results for the system
            total_roms = len(system_results)
            
        elif hasattr(self, 'scanned_roms_manager'):
            # Fall back to database results
            scan_summary = self.scanned_roms_manager.get_scan_summary(current_system_id)
            
            if scan_summary['total'] == 0:
                # No ROMs scanned yet in database
                self.rom_stats_label.setText(f"<b>Total DAT:</b> {total_dat_games} | <b>Matching:</b> 0 | <b>Missing:</b> {total_dat_games} | <b>Unrecognised:</b> 0 | <b>Broken:</b> 0 | <b>Total ROMs:</b> 0")
                return
            
            # Get all scanned ROMs to filter by visible DAT games
            all_scanned_roms = self.scanned_roms_manager.get_all_scanned_roms(current_system_id)
            
            # Count matching ROMs (correct + wrong_filename) that are in the filtered DAT
            matched_crcs = set()
            
            for rom_data in all_scanned_roms:
                status = rom_data.get('status')
                matched_crc = rom_data.get('matched_game_crc32')
                
                if status == 'correct' or status == 'wrong_filename':
                    # Collect unique CRC32s that are in the filtered DAT
                    if matched_crc:
                        if matched_crc in visible_crcs:
                            matched_crcs.add(matched_crc)
            
            # Matching count is the number of unique CRC32s matched (same logic as missing count)
            matching_count = len(matched_crcs)
            
            # Calculate missing ROMs (those in filtered DAT but not matched)
            missing_count = total_dat_games - len(matched_crcs)
            
            # Use scan summary for unrecognised, broken, and total counts
            # These counts are independent of DAT filtering
            unrecognised_count = scan_summary['not_recognized']
            broken_count = scan_summary['broken']
            
            # Total ROMs is all scanned ROMs (independent of filtering)
            total_roms = scan_summary['total']
            
        else:
            # No scan results yet
            self.rom_stats_label.setText(f"<b>Total DAT:</b> {total_dat_games} | <b>Matching:</b> 0 | <b>Missing:</b> {total_dat_games} | <b>Unrecognised:</b> 0 | <b>Broken:</b> 0 | <b>Total ROMs:</b> 0")
            return
        
        # Update the stats label with the new format: Total DAT | Matching | Missing | Unrecognised | Broken | Total ROMs
        self.rom_stats_label.setText(f"<b>Total DAT:</b> {total_dat_games} | <b>Matching:</b> {matching_count} | <b>Missing:</b> {missing_count} | <b>Unrecognised:</b> {unrecognised_count} | <b>Broken:</b> {broken_count} | <b>Total ROMs:</b> {total_roms}")
        self.rom_stats_label.repaint()  # Force immediate repaint
    
    def update_filter_options(self):
        """Update region and language filter options based on current DAT."""
        if not hasattr(self, 'all_games') or not self.all_games:
            return
        
        # Collect unique regions and languages
        regions = set()
        languages = set()
        
        for game in self.all_games:
            region = game.get('region', 'Unknown')
            game_languages = game.get('languages', 'Unknown')
            
            if region:
                regions.add(region)
            
            # Handle multiple languages (comma-separated)
            if game_languages and game_languages != 'Unknown':
                for lang in game_languages.split(','):
                    languages.add(lang.strip())
            else:
                # Use default language based on region instead of Unknown
                region_defaults = {
                    'USA': 'English',
                    'Europe': 'English', 
                    'Japan': 'Japanese',
                    'World': 'English',
                    'Asia': 'English',
                    'Korea': 'Korean',
                    'China': 'Chinese',
                    'Taiwan': 'Chinese',
                    'Brazil': 'Portuguese',
                    'Spain': 'Spanish',
                    'France': 'French',
                    'Germany': 'German',
                    'Italy': 'Italian'
                }
                default_lang = region_defaults.get(region, 'English')
                languages.add(default_lang)
        
        # Clear existing language checkboxes
        for checkbox in self.language_checkboxes.values():
            checkbox.setParent(None)
        
        self.language_checkboxes.clear()
        
        # Update region filter widget
        self.region_filter.set_available_regions(list(regions))
        
        # Create language checkboxes
        for language in sorted(languages):
            checkbox = QCheckBox(language)
            checkbox.setChecked(True)  # Start with all checked
            checkbox.stateChanged.connect(self.apply_filters)
            self.language_filter_layout.addWidget(checkbox)
            self.language_checkboxes[language] = checkbox
    
    def select_all_languages(self):
        """Select all language checkboxes."""
        for checkbox in self.language_checkboxes.values():
            checkbox.setChecked(True)
    
    def clear_all_languages(self):
        """Clear all language checkboxes."""
        for checkbox in self.language_checkboxes.values():
            checkbox.setChecked(False)
    
    def select_all_game_types(self):
        """Select all game type checkboxes."""
        self.show_beta_cb.setChecked(True)
        self.show_demo_cb.setChecked(True)
        self.show_proto_cb.setChecked(True)
        self.show_unlicensed_cb.setChecked(True)
        self.show_translation_cb.setChecked(True)
        self.show_modified_cb.setChecked(True)
        self.show_overdump_cb.setChecked(True)
    
    def clear_all_game_types(self):
        """Clear all game type checkboxes."""
        self.show_beta_cb.setChecked(False)
        self.show_demo_cb.setChecked(False)
        self.show_proto_cb.setChecked(False)
        self.show_unlicensed_cb.setChecked(False)
        self.show_translation_cb.setChecked(False)
        self.show_modified_cb.setChecked(False)
        self.show_overdump_cb.setChecked(False)
    
    def rename_wrong_filenames(self):
        """Rename files with wrong filenames."""
        # TODO: Implement rename functionality
        pass
    
    def move_extra_files(self):
        """Move extra/unrecognized files to subfolder."""
        # TODO: Implement move functionality
        pass
    
    def move_broken_files(self):
        """Move broken files to subfolder."""
        # TODO: Implement move functionality
        pass
    
    def export_missing_list(self):
        """Export list of missing ROMs."""
        if not self.current_system_id:
            QMessageBox.warning(
                self, "No System Selected",
                "Please select a system first."
            )
            return
        
        # Find missing ROMs
        missing_games = self.rom_scanner.find_missing_roms(
            self.current_system_id, self.current_scan_results
        )
        
        if not missing_games:
            QMessageBox.information(
                self, "No Missing ROMs",
                "No missing ROMs found for the current system."
            )
            return
        
        # Save to file
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Missing ROMs List", "missing_roms.txt", "Text Files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Missing ROMs for {self.system_combo.currentText()}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for game in missing_games:
                        f.write(f"{game['dat_rom_name']}\n")
                
                QMessageBox.information(
                    self, "Export Complete",
                    f"Missing ROMs list saved to {filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error",
                    f"Error saving file:\n{str(e)}"
                )
    
    def show_settings(self):
        """Show settings dialog."""
        # Set db_manager on settings_manager so it can be accessed in SettingsDialog
        self.settings_manager.db_manager = self.db_manager
        dialog = SettingsDialog(self.settings_manager, self)
        
        # Connect system removal signal
        dialog.system_removed.connect(self.on_system_removed)
        
        dialog.exec()
        
    def on_system_removed(self, system_id: int):
        """Handle system removal."""
        # Clear current system if it was the one removed
        if self.current_system_id == system_id:
            self.current_system_id = None
            self.current_scan_results = []
            self.all_games = []
            
            # Clear UI elements
            self.dat_tree.clear()
            self.correct_tree.clear()
            self.dat_stats_label.setText("Total: 0 | Filtered Out: 0 | Showing: 0")
            self.rom_stats_label.setText("Total DAT: 0 | Matching: 0 | Missing: 0 | Unrecognised: 0 | Broken: 0 | Total ROMs: 0")
            
            # Clear filter options
            self.region_filter.set_available_regions([])
            
            # Clear language checkboxes
            for checkbox in self.language_checkboxes.values():
                checkbox.setParent(None)
                checkbox.deleteLater()  # Ensure proper cleanup of Qt widgets
            self.language_checkboxes.clear()
            
            # Reset game type checkboxes to default state
            self.show_beta_cb.setChecked(True)
            self.show_demo_cb.setChecked(True)
            self.show_proto_cb.setChecked(True)
            self.show_unlicensed_cb.setChecked(True)
            self.show_translation_cb.setChecked(True)
            self.show_modified_cb.setChecked(True)
            self.show_overdump_cb.setChecked(True)
        
        # Reload systems list
        self.load_systems()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About Romplestiltskin",
            "Romplestiltskin v1.0.0\n\n"
            "ROM Collection Management and Verification Tool\n\n"
            "Helps you curate and complete your game ROM collections "
            "by comparing local files against official DAT files."
        )
    
    def restore_window_state(self):
        """Restore window geometry and state."""
        geometry = self.settings_manager.get("window_geometry")
        if geometry:
            # Convert base64 string back to QByteArray
            geometry_bytes = base64.b64decode(geometry.encode('utf-8'))
            self.restoreGeometry(QByteArray(geometry_bytes))
        
        state = self.settings_manager.get("window_state")
        if state:
            # Convert base64 string back to QByteArray
            state_bytes = base64.b64decode(state.encode('utf-8'))
            self.restoreState(QByteArray(state_bytes))
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window state - convert QByteArray to base64 string for JSON serialization
        geometry = self.saveGeometry()
        geometry_str = base64.b64encode(geometry.data()).decode('utf-8')
        self.settings_manager.set("window_geometry", geometry_str)
        
        state = self.saveState()
        state_str = base64.b64encode(state.data()).decode('utf-8')
        self.settings_manager.set("window_state", state_str)
        
        self.settings_manager.save_settings()
        
        event.accept()