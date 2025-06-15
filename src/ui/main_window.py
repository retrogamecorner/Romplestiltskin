#!/usr/bin/env python3
"""
Main Window for Romplestiltskin

Provides the primary user interface for ROM collection management.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QComboBox, QLabel, QPushButton,
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
    
    progress = pyqtSignal(int, int)  # current file, total files
    file_progress = pyqtSignal(str, int, int) # current_file_name, current_game_in_file, total_games_in_file
    finished = pyqtSignal(int, int)  # successful files, total files
    error = pyqtSignal(str)
    
    def __init__(self, dat_processor: DATProcessor, dat_file_paths: list[str]):
        super().__init__()
        self.dat_processor = dat_processor
        self.dat_file_paths = dat_file_paths
    
    def run(self):
        total_files = len(self.dat_file_paths)
        successful_files = 0
        for i, file_path in enumerate(self.dat_file_paths):
            self.progress.emit(i + 1, total_files)
            try:
                # Assuming dat_processor will have a method to import a single DAT file
                # and potentially a way to report progress within that file.
                # For now, we'll assume import_dat_file returns True on success.
                # This method will need to be created or adapted in DATProcessor.
                def single_file_progress_callback(current_game, total_games):
                    self.file_progress.emit(Path(file_path).name, current_game, total_games)
                
                # Modify DATProcessor to accept this callback in import_dat_file
                if self.dat_processor.import_dat_file(file_path, progress_callback=single_file_progress_callback):
                    successful_files += 1
            except Exception as e:
                # Emit an error for this specific file, or collect errors
                print(f"Error importing {file_path}: {e}") # Log or handle more gracefully
                # Optionally, emit a specific error signal per file or accumulate
        self.finished.emit(successful_files, total_files)

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
        self.ignored_crcs = set()  # Initialize as an empty set
        
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
        self.scan_button.clicked.connect(lambda: self.scan_rom_folder(prompt_for_folder=True))
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
        self.missing_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.missing_tree.customContextMenuRequested.connect(self.show_missing_tree_context_menu)
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

        # Ignored ROMs tab
        ignored_tab = QWidget()
        ignored_layout = QVBoxLayout(ignored_tab)

        # Ignored ROMs tree
        self.ignored_tree = QTreeWidget()
        self.ignored_tree.setHeaderLabels([
            "#", "Game Name", "Region", "Language", "CRC32"
        ])
        self.ignored_tree.setAlternatingRowColors(True)
        self.ignored_tree.setSortingEnabled(True)
        self.ignored_tree.setMinimumHeight(250)  # Reduced height
        self.ignored_tree.setMaximumHeight(300)  # Prevent excessive growth
        self.ignored_tree.setColumnWidth(0, 50)  # # column
        self.ignored_tree.setColumnWidth(1, 300)  # Game name column
        self.ignored_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)  # Allow multiple selection
        self.ignored_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ignored_tree.customContextMenuRequested.connect(self.show_ignored_tree_context_menu)
        ignored_layout.addWidget(self.ignored_tree)
        
        # Add tabs to the tab widget
        self.rom_tabs.addTab(correct_tab, "✔️ Correct")
        self.rom_tabs.addTab(missing_tab, "❓ Missing")
        # Add Ignored ROMs tab using its parent widget (the QWidget 'ignored_tab' we created)
        self.rom_tabs.addTab(ignored_tab, "🚫 Ignored") 
        self.rom_tabs.addTab(unrecognized_tab, "⚠️ Unrecognized")
        self.rom_tabs.addTab(broken_tab, "💔 Broken")
        layout.addWidget(self.rom_tabs)
        
        # Stats with detailed feedback
        self.rom_stats_label = QLabel("Total DAT: 0 | Matching: 0 | Missing: 0 | Unrecognised: 0 | Broken: 0 | Total ROMs: 0")
        self.rom_stats_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.rom_stats_label)
        
        return panel
    
    def show_missing_tree_context_menu(self, position):
        menu = QMenu()
        move_to_ignore_action = menu.addAction("Move to Ignore List")
        action = menu.exec(self.missing_tree.mapToGlobal(position))
        if action == move_to_ignore_action:
            self.move_selected_to_ignore_list()

    def show_ignored_tree_context_menu(self, position):
        menu = QMenu()
        unignore_action = menu.addAction("Remove from Ignore List (Unignore)")
        action = menu.exec(self.ignored_tree.mapToGlobal(position))
        if action == unignore_action:
            self.unignore_selected_items()

    def move_selected_to_ignore_list(self):
        selected_items = self.missing_tree.selectedItems()
        if not selected_items: return

        moved_crcs = []
        items_to_remove_from_missing = []

        for item in selected_items:
            # Assuming CRC32 is in the 5th column (index 4)
            crc32 = item.text(4) 
            if crc32 and crc32 not in self.ignored_crcs:
                self.ignored_crcs.add(crc32)
                moved_crcs.append(crc32)
                
                # Prepare item for ignored_tree
                cloned_item_texts = [item.text(i) for i in range(item.columnCount())]
                new_ignored_item = NumericTreeWidgetItem(cloned_item_texts)
                # If UserRole had original game data, you might want to transfer it
                # game_data = item.data(0, Qt.ItemDataRole.UserRole) # Example if it was set
                # if game_data: new_ignored_item.setData(0, Qt.ItemDataRole.UserRole, game_data)
                self.ignored_tree.addTopLevelItem(new_ignored_item)
                items_to_remove_from_missing.append(item)

        if moved_crcs:
            # Remove items from missing_tree (iterate backwards if removing by index)
            for item in items_to_remove_from_missing:
                self.missing_tree.takeTopLevelItem(self.missing_tree.indexOfTopLevelItem(item))
            
            self.settings_manager.set_ignored_crcs(list(self.ignored_crcs), self.current_system_id)
            self.update_rom_stats()
            self.apply_filters() # This should re-populate DAT and missing, excluding newly ignored

    def unignore_selected_items(self):
        selected_items = self.ignored_tree.selectedItems()
        if not selected_items: return

        unignored_crcs = []
        items_to_remove_from_ignored = []

        for item in selected_items:
            # Assuming CRC32 is in the 5th column (index 4)
            crc32 = item.text(4)
            if crc32 and crc32 in self.ignored_crcs:
                self.ignored_crcs.remove(crc32)
                unignored_crcs.append(crc32)
                items_to_remove_from_ignored.append(item)
        
        if unignored_crcs:
            for item in items_to_remove_from_ignored:
                self.ignored_tree.takeTopLevelItem(self.ignored_tree.indexOfTopLevelItem(item))
            
            self.settings_manager.set_ignored_crcs(list(self.ignored_crcs), self.current_system_id)
            self.update_rom_stats()
            self.apply_filters() # This will re-evaluate DAT and missing lists

    def populate_ignored_tree(self):
        """Populate the ignored ROMs tree based on self.ignored_crcs."""
        self.ignored_tree.clear()
        if not self.all_games or not self.ignored_crcs:
            return

        row_number = 0
        for crc in self.ignored_crcs:
            game_details = next((g for g in self.all_games if g.get('crc32') == crc), None)
            if game_details:
                row_number += 1
                item = NumericTreeWidgetItem([
                    str(row_number),
                    game_details['major_name'],
                    game_details.get('region', ''),
                    game_details.get('languages', ''),
                    game_details['crc32']
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, row_number) # For sorting
                self.ignored_tree.addTopLevelItem(item)
        self.ignored_tree.sortItems(0, Qt.SortOrder.AscendingOrder)

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
        
        # Save current filter settings for the previous system
        if hasattr(self, 'current_system_id') and self.current_system_id is not None:
            self.save_current_filter_settings()
        
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
        
        # Restore filter settings for the new system
        self.restore_filter_settings()

        # Load ignored CRCs for the current system
        self.ignored_crcs = set(self.settings_manager.get_ignored_crcs(self.current_system_id))
        self.populate_ignored_tree()
        
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
        self.all_games = [game for game in self.all_games if game.get('crc32') not in self.ignored_crcs]

        # Initial display of all games (excluding ignored)
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
        """Import selected DAT files."""
        dat_folder = self.settings_manager.get_dat_folder_path()
        if not dat_folder:
            # If no last DAT folder, default to home directory or a sensible default
            dat_folder = str(Path.home())
        
        # Open file dialog to select one or more DAT files
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select DAT Files to Import",
            dat_folder,  # Initial directory
            "DAT Files (*.dat);;All Files (*)"  # Filter for .dat files
        )
        
        if file_paths:
            # Save the directory of the first selected file as the new default DAT folder
            if file_paths:
                new_dat_folder = str(Path(file_paths[0]).parent)
                self.settings_manager.set_dat_folder_path(new_dat_folder)
                self.settings_manager.save_settings()
            
            # Start import in background thread with the list of file paths
            self.import_thread = DATImportThread(self.dat_processor, file_paths)
            self.import_thread.progress.connect(self._on_dat_overall_import_progress) # Overall file progress
            self.import_thread.file_progress.connect(self._on_dat_file_import_progress) # Game progress within a file
            self.import_thread.finished.connect(self.on_import_finished)
            self.import_thread.error.connect(self.on_import_error)
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(file_paths)) # For overall file progress
            self.progress_bar.setValue(0)
            self.status_bar.showMessage(f"Starting import of {len(file_paths)} DAT file(s)...")
            
            self.import_thread.start()
    
    def on_import_finished(self, successful: int, total: int):
        """Handle DAT import completion."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0,1) # Reset progress bar after completion
        self.progress_bar.setValue(1)
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

    def _on_dat_overall_import_progress(self, current_file_num: int, total_files: int):
        """Update progress for overall DAT file import."""
        self.progress_bar.setRange(0, total_files)
        self.progress_bar.setValue(current_file_num)
        # Status message for overall progress is handled by _on_dat_file_import_progress or initial message

    def _on_dat_file_import_progress(self, file_name: str, current_game: int, total_games: int):
        """Update status for game import progress within a single DAT file."""
        if total_games > 0: # Avoid division by zero if a DAT is empty or unparseable
            percentage = int((current_game / total_games) * 100)
            self.status_bar.showMessage(f"Processing {file_name}: {current_game}/{total_games} games ({percentage}%)...")
        else:
            self.status_bar.showMessage(f"Processing {file_name} (0 games)..." )
    
    def _start_rom_scan_process(self, folder_to_scan: str, system_id: str):
        """Internal method to initiate the ROM scan with a progress dialog."""
        self.settings_manager.add_system_rom_folder(system_id, folder_to_scan)
        self.settings_manager.save_settings()

        # Use the custom ProgressDialog from ui.progress_dialog
        self.scan_progress_dialog = ProgressDialog(title="Scanning ROMs...", parent=self)
        self.scan_progress_dialog.status_label.setText("Scanning in progress, please wait.")
        self.scan_progress_dialog.cancel_button.setEnabled(False) # Or True if you implement cancellation
        self.scan_progress_dialog.setModal(True)
        self.scan_progress_dialog.set_progress(0) # Start at 0%

        self.scan_thread = ROMScanThread(self.rom_scanner, folder_to_scan, system_id)
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)

        self.progress_bar.setVisible(True) # Main window progress bar can still be used
        self.progress_bar.setRange(0, 0)   # Set to indeterminate initially
        self.status_bar.showMessage(f"Scanning folder: {Path(folder_to_scan).name}...")

        self.scan_thread.start()
        self.scan_progress_dialog.exec() # Show modally and block until accepted or rejected

    def scan_rom_folder(self, prompt_for_folder=True):
        """Scan ROM folder for current system."""
        if not self.current_system_id:
            QMessageBox.warning(self, "No System Selected", "Please select a system first.")
            return

        system_folders = self.settings_manager.get_system_rom_folders(str(self.current_system_id))
        folder_to_scan = None

        if prompt_for_folder:
            # Manual scan mode (from button): always prompt for a folder.
            default_folder_path = system_folders[0] if system_folders and Path(system_folders[0]).is_dir() else str(Path.home())
            selected_folder = QFileDialog.getExistingDirectory(self, "Select ROM Folder", default_folder_path)
            if selected_folder:
                folder_to_scan = selected_folder
            else:
                self.status_bar.showMessage("Scan cancelled: No folder selected.")
                return
        else:
            # Automatic rescan mode (e.g., after moving broken files).
            # Use existing folder if valid, otherwise prompt (initial setup for system).
            if system_folders and Path(system_folders[0]).is_dir():
                folder_to_scan = system_folders[0]
            else:
                current_system_name = self.systems_combo.currentText()
                QMessageBox.information(self, "Initial Folder Setup", 
                                        f"No ROM folder is currently set for the system '{current_system_name}'. "
                                        f"Please select a folder to scan.")
                default_folder_path = str(Path.home())
                selected_folder = QFileDialog.getExistingDirectory(self, f"Select ROM Folder for {current_system_name}", default_folder_path)
                if selected_folder:
                    folder_to_scan = selected_folder
                else:
                    self.status_bar.showMessage("Scan cancelled: No folder selected for system setup.")
                    return

        if folder_to_scan:
            self._start_rom_scan_process(folder_to_scan, str(self.current_system_id))
        # If folder_to_scan is None here, it means the user cancelled a dialog, and a message was already shown.

    def rescan_current_rom_folder(self):
        """Automatically rescans the current system's ROM folder."""
        self.scan_rom_folder(prompt_for_folder=False)
    
    def on_scan_progress(self, current: int, total: int):
        """Handle scan progress update for both dialog and main progress bar."""
        if hasattr(self, 'scan_progress_dialog') and self.scan_progress_dialog.isVisible():
            if total > 0:
                progress_percentage = int((current / total) * 100)
                self.scan_progress_dialog.set_progress(progress_percentage)
                self.scan_progress_dialog.set_status(f"Scanning: {current}/{total} items...")
                # Update main progress bar as well
                self.progress_bar.setRange(0, 100) # Assuming percentage for main bar
                self.progress_bar.setValue(progress_percentage)
            else: # Indeterminate state
                self.scan_progress_dialog.set_progress(0) # Or handle indeterminate in ProgressDialog
                self.scan_progress_dialog.set_status("Scanning...")
                self.progress_bar.setRange(0, 0) # Indeterminate for main bar
        else: # Fallback if dialog is not active (should not happen with modal dialog)
            if total > 0:
                progress = int((current / total) * 100)
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(progress)
            else:
                self.progress_bar.setRange(0, 0)
    
    def on_scan_finished(self, results: List[ROMScanResult]):
        """Handle scan completion."""
        if hasattr(self, 'scan_progress_dialog') and self.scan_progress_dialog.isVisible():
            self.scan_progress_dialog.accept() # Close the modal dialog

        self.progress_bar.setVisible(False)
        self.current_scan_results = results
        
        if self.current_system_id:
            self.scanned_roms_manager.store_scan_results(self.current_system_id, results)
        
        self.update_correct_roms()
        self.update_missing_roms()
        self.update_unrecognized_roms()
        self.update_broken_roms()
        self.update_rom_stats()
        
        self.status_bar.showMessage(f"Scan complete. Found {len(results)} relevant files.")
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
        if hasattr(self, 'scan_progress_dialog') and self.scan_progress_dialog.isVisible():
            self.scan_progress_dialog.reject() # Close the modal dialog

        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Scan failed")
        
        QMessageBox.critical(
            self, "Scan Error",
            f"An error occurred during scanning:\n{error_message}"
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
                # Include correct ROMs and ROMs with wrong filenames (they have correct CRC)
                if rom_data['status'] in ['correct', 'wrong_filename']:
                    matched_crc32 = rom_data.get('matched_game_crc32')
                    # Only show if the matched game is visible in current filters
                    if matched_crc32 and matched_crc32 in visible_crcs:
                        # Find the full game details from self.all_games for display
                        game_details = next((g for g in self.all_games if g.get('crc32') == matched_crc32), None)
                        if game_details:
                            correct_games.append(game_details)
                            row_number += 1
                            
                            # For wrong filename ROMs, show the actual filename instead of DAT name
                            if rom_data['status'] == 'wrong_filename':
                                display_name = Path(rom_data['file_path']).stem  # Show actual filename without extension
                            else:
                                display_name = game_details['major_name']  # Show DAT name for correct ROMs
                            
                            item = NumericTreeWidgetItem([
                                str(row_number),  # Display without leading zeros
                                display_name,
                                game_details.get('region', ''),
                                game_details.get('languages', ''),
                                game_details['crc32']
                            ])
                            # Store numeric value for proper sorting
                            item.setData(0, Qt.ItemDataRole.UserRole, row_number)
                            self.correct_tree.addTopLevelItem(item)
        elif hasattr(self, 'current_scan_results') and self.current_scan_results:
            for result in self.current_scan_results:
                # Include correct ROMs and ROMs with wrong filenames (they have correct CRC)
                if result.status.value in ['correct', 'wrong_filename'] and result.matched_game:
                    matched_crc32 = result.matched_game.get('crc32')
                    # Only show if the matched game is visible in current filters
                    if matched_crc32 and matched_crc32 in visible_crcs:
                        game_details = result.matched_game
                        correct_games.append(game_details)
                        row_number += 1
                        
                        # For wrong filename ROMs, show the actual filename instead of DAT name
                        if result.status.value == 'wrong_filename':
                            display_name = Path(result.file_path).stem  # Show actual filename without extension
                        else:
                            display_name = game_details['major_name']  # Show DAT name for correct ROMs
                        
                        item = NumericTreeWidgetItem([
                            str(row_number),  # Display without leading zeros
                            display_name,
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
        # and check if they are missing from the scan results AND not in the ignore list.
        row_number = 0
        for game_name, crc32 in visible_games:
            if crc32 and crc32 not in matched_crcs and crc32 not in self.ignored_crcs:
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
            
            # Check if game is in ignored list
            game_crc = game.get('crc32', '')
            if game_crc in self.ignored_crcs:
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

        # Save the current filter settings for this system
        self.save_current_filter_settings()
    
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
        
        system_results_dicts = []
        if hasattr(self, 'scanned_roms_manager'):
            system_results_dicts = self.scanned_roms_manager.get_all_scanned_roms(current_system_id)
            
        if not system_results_dicts:
            # Try current_scan_results as a fallback if DB is empty or manager not fully ready
            if hasattr(self, 'current_scan_results') and self.current_scan_results:
                # Convert ROMScanResult objects to dicts for consistent processing
                system_results_dicts = [
                    {
                        'system_id': r.system_id,
                        'file_path': r.file_path,
                        'file_size': r.file_size,
                        'calculated_crc32': r.calculated_crc32,
                        'status': r.status.value if isinstance(r.status, ROMStatus) else r.status, # Handle ROMStatus enum or string
                        'matched_game': r.matched_game, # This is already a dict
                        'matched_game_crc32': r.matched_game.get('crc32') if r.matched_game else None, # Extract CRC from matched_game dict
                        'similarity_score': getattr(r, 'similarity_score', None),
                        'error_message': getattr(r, 'error_message', None)
                    }
                    for r in self.current_scan_results if r.system_id == current_system_id
                ]

        matching_count = 0
        missing_count = total_dat_games 
        unrecognised_count = 0
        broken_count = 0
        total_roms = 0

        if system_results_dicts:
            current_unrecognised = 0
            current_broken = 0
            matched_crcs = set()

            for result_dict in system_results_dicts:
                status_val = result_dict.get('status')
                if status_val == ROMStatus.NOT_RECOGNIZED.value or status_val == 'not_recognized':
                    current_unrecognised += 1
                elif status_val == ROMStatus.BROKEN.value or status_val == 'broken':
                    current_broken += 1
                elif status_val == ROMStatus.CORRECT.value or status_val == 'correct' or \
                     status_val == ROMStatus.WRONG_FILENAME.value or status_val == 'wrong_filename':
                    rom_crc = result_dict.get('matched_game_crc32') 
                    if rom_crc and rom_crc in visible_crcs:
                        matched_crcs.add(rom_crc)
            
            matching_count = len(matched_crcs)
            missing_count = total_dat_games - matching_count
            unrecognised_count = current_unrecognised
            broken_count = current_broken
            total_roms = len(system_results_dicts)
        elif not system_results_dicts and hasattr(self, 'scanned_roms_manager'):
            scan_summary = self.scanned_roms_manager.get_scan_summary(current_system_id)
            if scan_summary and scan_summary.get('total', 0) > 0:
                all_scanned_roms_from_db = self.scanned_roms_manager.get_all_scanned_roms(current_system_id)
                db_matched_crcs = set()
                for rom_data in all_scanned_roms_from_db:
                    status = rom_data.get('status')
                    rom_status_correct = ROMStatus.CORRECT.value
                    rom_status_wrong_filename = ROMStatus.WRONG_FILENAME.value
                    
                    is_correct_or_wrong_filename = (status == rom_status_correct or status == 'correct' or
                                                    status == rom_status_wrong_filename or status == 'wrong_filename')

                    if is_correct_or_wrong_filename:
                        matched_crc = rom_data.get('matched_game_crc32')
                        if matched_crc and matched_crc in visible_crcs:
                            db_matched_crcs.add(matched_crc)
                
                matching_count = len(db_matched_crcs)
                missing_count = total_dat_games - matching_count
                unrecognised_count = scan_summary.get('not_recognized', 0)
                broken_count = scan_summary.get('broken', 0)
                total_roms = scan_summary.get('total', 0)
        # If both system_results_dicts is empty and the elif condition is false (e.g., no scan_summary or it's empty),
        # the stats will remain at their initial zero/default values.
        # The final self.rom_stats_label.setText outside this block will handle displaying these.
        
        # Update the stats label with the new format: Total DAT | Matching | Missing | Unrecognised | Broken | Total ROMs
        self.rom_stats_label.setText(f"<b>Total DAT:</b> {total_dat_games} | <b>Matching:</b> {matching_count} | <b>Missing:</b> {missing_count} | <b>Unrecognised:</b> {unrecognised_count} | <b>Broken:</b> {broken_count} | <b>Total ROMs:</b> {total_roms}")
        self.rom_stats_label.repaint()  # Force immediate repaint
    
    def save_current_filter_settings(self):
        """Save current filter settings for the current system."""
        if not self.current_system_id:
            return
        
        # Collect current filter settings
        filter_settings = {
            "show_beta": self.show_beta_cb.isChecked(),
            "show_demo": self.show_demo_cb.isChecked(),
            "show_proto": self.show_proto_cb.isChecked(),
            "show_unlicensed": self.show_unlicensed_cb.isChecked(),
            "show_unofficial_translation": self.show_translation_cb.isChecked(),
            "show_modified_release": self.show_modified_cb.isChecked(),
            "show_overdump": self.show_overdump_cb.isChecked(),
            "preferred_languages": [lang for lang, cb in self.language_checkboxes.items() if cb.isChecked()],
            "preferred_regions": self.region_filter.get_region_priority(),
            "ignored_regions": self.region_filter.get_ignored_regions(),
            "remove_duplicates": self.region_filter.should_remove_duplicates()
        }
        
        # Save to settings manager
        self.settings_manager.set_system_filter_settings(str(self.current_system_id), filter_settings)
    
    def restore_filter_settings(self):
        """Restore filter settings for the current system."""
        if not self.current_system_id:
            return
        
        # Get filter settings for this system
        filter_settings = self.settings_manager.get_system_filter_settings(str(self.current_system_id))
        
        # Temporarily disconnect signals to avoid triggering apply_filters multiple times
        self.show_beta_cb.toggled.disconnect()
        self.show_demo_cb.toggled.disconnect()
        self.show_proto_cb.toggled.disconnect()
        self.show_unlicensed_cb.toggled.disconnect()
        self.show_translation_cb.toggled.disconnect()
        self.show_modified_cb.toggled.disconnect()
        self.show_overdump_cb.toggled.disconnect()
        
        # Restore type filter settings
        self.show_beta_cb.setChecked(filter_settings.get("show_beta", True))
        self.show_demo_cb.setChecked(filter_settings.get("show_demo", True))
        self.show_proto_cb.setChecked(filter_settings.get("show_proto", True))
        self.show_unlicensed_cb.setChecked(filter_settings.get("show_unlicensed", True))
        self.show_translation_cb.setChecked(filter_settings.get("show_unofficial_translation", True))
        self.show_modified_cb.setChecked(filter_settings.get("show_modified_release", True))
        self.show_overdump_cb.setChecked(filter_settings.get("show_overdump", True))
        
        # Restore language filter settings
        # If no preferred_languages are saved (e.g., after a reset or for a new system),
        # default to all available languages for the current system.
        # Otherwise, use the saved preferred_languages.
        saved_preferred_languages = filter_settings.get("preferred_languages")

        if not self.language_checkboxes:
            # This can happen if filter options haven't been updated yet for a new system
            self.update_filter_options() # Ensure checkboxes are created

        if saved_preferred_languages is None:
            # No saved preference, default to all available languages
            if self.language_checkboxes: # Ensure it's not empty after update_filter_options
                preferred_languages = list(self.language_checkboxes.keys())
            else:
                # Fallback if still no languages (e.g., DAT has no language info at all)
                # Though update_filter_options should add 'English' in this case.
                preferred_languages = ["English"] 
        else:
            # Saved preference exists, use it
            preferred_languages = saved_preferred_languages

        for lang, checkbox in self.language_checkboxes.items():
            # Temporarily disconnect to avoid triggering apply_filters during this loop
            try:
                checkbox.stateChanged.disconnect(self.apply_filters)
            except TypeError:
                pass # Signal was not connected
            checkbox.setChecked(lang in preferred_languages)
            # Reconnect the signal
            checkbox.stateChanged.connect(self.apply_filters)
        
        # Restore region filter settings
        if "preferred_regions" in filter_settings:
            self.region_filter.set_region_priority(filter_settings["preferred_regions"])
        if "ignored_regions" in filter_settings:
            self.region_filter.set_ignored_regions(filter_settings["ignored_regions"])
        if "remove_duplicates" in filter_settings:
            self.region_filter.set_remove_duplicates(filter_settings["remove_duplicates"])
        
        # Rebuild available regions list based on current DAT games
        if hasattr(self, 'all_games') and self.all_games:
            all_regions = set()
            for game in self.all_games:
                if game.get('region'):
                    all_regions.add(game['region'])
            self.region_filter.rebuild_available_list(list(all_regions))
        
        # Reconnect signals
        self.show_beta_cb.toggled.connect(self.apply_filters)
        self.show_demo_cb.toggled.connect(self.apply_filters)
        self.show_proto_cb.toggled.connect(self.apply_filters)
        self.show_unlicensed_cb.toggled.connect(self.apply_filters)
        self.show_translation_cb.toggled.connect(self.apply_filters)
        self.show_modified_cb.toggled.connect(self.apply_filters)
        self.show_overdump_cb.toggled.connect(self.apply_filters)
    
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
        """Rename files with wrong filenames to their correct DAT names."""
        if not self.current_system_id:
            QMessageBox.warning(
                self, "No System Selected",
                "Please select a system first."
            )
            return
        
        # Get ROMs with wrong filenames for current system
        wrong_filename_roms = []
        current_system_id = self.current_system_id
        
        if hasattr(self, 'scanned_roms_manager'):
            # Get from database
            scanned_roms = self.scanned_roms_manager.get_scanned_roms_by_status(
                current_system_id, ROMStatus.WRONG_FILENAME
            )
            wrong_filename_roms = scanned_roms
        elif hasattr(self, 'current_scan_results') and self.current_scan_results:
            # Get from memory
            for result in self.current_scan_results:
                if result.status == ROMStatus.WRONG_FILENAME:
                    wrong_filename_roms.append({
                        'file_path': result.file_path,
                        'matched_game_crc32': result.matched_game.get('crc32') if result.matched_game else None,
                        'matched_game': result.matched_game
                    })
        
        if not wrong_filename_roms:
            QMessageBox.information(
                self, "No Files to Rename",
                "No ROMs with wrong filenames found for the current system."
            )
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self, "Rename Wrong Filenames",
            f"Found {len(wrong_filename_roms)} ROM(s) with wrong filenames.\n\n"
            "Do you want to rename them to their correct DAT names?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        renamed_count = 0
        failed_renames = []
        
        print(f"DEBUG: Found {len(wrong_filename_roms)} ROMs with wrong filenames")
        
        for i, rom_data in enumerate(wrong_filename_roms):
            print(f"DEBUG: Processing ROM {i+1}/{len(wrong_filename_roms)}: {rom_data}")
            try:
                old_path = Path(rom_data['file_path'])
                print(f"DEBUG: Checking if file exists: {old_path}")
                if not old_path.exists():
                    failed_renames.append(f"{old_path.name}: File not found")
                    print(f"DEBUG: File not found: {old_path}")
                    continue
                
                # Get the correct filename from the matched game
                print(f"DEBUG: Available keys in rom_data: {list(rom_data.keys())}")
                print(f"DEBUG: calculated_crc32 value: {rom_data.get('calculated_crc32')}")
                print(f"DEBUG: calculated_crc32 type: {type(rom_data.get('calculated_crc32'))}")
                
                matched_crc32 = rom_data.get('calculated_crc32')
                print(f"DEBUG: Matched CRC32: {matched_crc32}")
                if not matched_crc32:
                    failed_renames.append(f"{old_path.name}: No matched game found")
                    print(f"DEBUG: No matched CRC32 found")
                    continue
                
                # Get game details from database
                print(f"DEBUG: Getting game details for CRC32: {matched_crc32}, size: {old_path.stat().st_size}")
                game_details = self.db_manager.get_game_by_crc(current_system_id, matched_crc32, old_path.stat().st_size)
                print(f"DEBUG: Game details: {game_details}")
                if not game_details:
                    failed_renames.append(f"{old_path.name}: Game details not found in DAT")
                    print(f"DEBUG: Game details not found in database")
                    continue
                
                # Construct new filename using the DAT ROM name (which includes region info)
                dat_rom_name = game_details.get('dat_rom_name', game_details['major_name'])
                print(f"DEBUG: DAT ROM name: {dat_rom_name}")
                
                # Remove the extension from dat_rom_name if it exists, we'll use the original file's extension
                if '.' in dat_rom_name:
                    correct_name = dat_rom_name.rsplit('.', 1)[0]
                else:
                    correct_name = dat_rom_name
                    
                print(f"DEBUG: Correct name without extension: {correct_name}")
                # Sanitize filename for Windows (remove invalid characters)
                invalid_chars = '<>:"/\\|?*'
                for char in invalid_chars:
                    correct_name = correct_name.replace(char, '_')
                print(f"DEBUG: Sanitized correct name: {correct_name}")
                
                # Keep the original file extension
                new_filename = f"{correct_name}{old_path.suffix}"
                new_path = old_path.parent / new_filename
                
                print(f"DEBUG: Attempting to rename '{old_path.name}' to '{new_filename}'")
                print(f"DEBUG: Full paths - Old: {old_path}, New: {new_path}")
                
                # Check if target file already exists
                if new_path.exists() and new_path != old_path:
                    failed_renames.append(f"{old_path.name}: Target file already exists ({new_filename})")
                    print(f"DEBUG: Target file already exists: {new_path}")
                    continue
                
                # Rename the file
                print(f"DEBUG: Executing rename from {old_path} to {new_path}")
                old_path.rename(new_path)
                print(f"DEBUG: File rename successful")
                
                # Update database with new path and status
                if hasattr(self, 'scanned_roms_manager'):
                    print(f"DEBUG: Updating database - old path: {str(old_path)}, new path: {str(new_path)}")
                    self.scanned_roms_manager.update_rom_path(
                        current_system_id, str(old_path), str(new_path)
                    )
                    print(f"DEBUG: Database path updated")
                    self.scanned_roms_manager.update_rom_status(
                        current_system_id, str(new_path), ROMStatus.CORRECT
                    )
                    print(f"DEBUG: Database status updated to CORRECT")
                else:
                    print(f"DEBUG: No scanned_roms_manager available")
                
                renamed_count += 1
                print(f"DEBUG: Successfully renamed file {i+1}")
                
            except Exception as e:
                error_msg = f"{Path(rom_data['file_path']).name}: {str(e)}"
                failed_renames.append(error_msg)
                print(f"DEBUG: Exception occurred: {error_msg}")
                import traceback
                print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        
        # Show results
        message = f"Successfully renamed {renamed_count} file(s)."
        if failed_renames:
            message += f"\n\nFailed to rename {len(failed_renames)} file(s):\n"
            message += "\n".join(failed_renames[:10])  # Show first 10 failures
            if len(failed_renames) > 10:
                message += f"\n... and {len(failed_renames) - 10} more."
        
        if renamed_count > 0:
            QMessageBox.information(self, "Rename Complete", message)
            # Refresh the UI to reflect changes
            self.update_correct_roms()
            self.update_rom_stats()
        else:
            QMessageBox.warning(self, "Rename Failed", message)
    
    def move_extra_files(self):
        """Move extra/unrecognized files to subfolder."""
        if not self.current_system_id:
            QMessageBox.warning(
                self, "No System Selected",
                "Please select a system first."
            )
            return

        # Get unrecognized ROMs for current system
        unrecognized_roms = []
        current_system_id = self.current_system_id

        if hasattr(self, 'scanned_roms_manager'):
            # Get from database
            scanned_roms = self.scanned_roms_manager.get_scanned_roms_by_status(
                current_system_id, ROMStatus.NOT_RECOGNIZED
            )
            unrecognized_roms = [rom_data['file_path'] for rom_data in scanned_roms]
        elif hasattr(self, 'current_scan_results') and self.current_scan_results:
            # Get from memory results (these should be from the current session's scan)
            for result in self.current_scan_results:
                if result.status == ROMStatus.NOT_RECOGNIZED and result.system_id == current_system_id:
                    unrecognized_roms.append(result.file_path)
        
        if not unrecognized_roms:
            QMessageBox.information(
                self, "No Unrecognized ROMs",
                "No unrecognized ROM files found for the current system. This might be because a fresh scan is needed after clearing cached data."
            )
            return

        # Get ROM folders for current system
        system_folders = self.settings_manager.get_system_rom_folders(str(current_system_id))
        if not system_folders:
            QMessageBox.warning(
                self, "No ROM Folders",
                "No ROM folders configured for the current system."
            )
            return

        # Filter unrecognized_roms to only include files directly in a configured ROM folder
        system_folders_paths = [Path(folder).resolve() for folder in system_folders]
        filtered_unrecognized_roms = []
        for rom_path_str in unrecognized_roms:
            rom_path = Path(rom_path_str).resolve()
            if rom_path.parent in system_folders_paths:
                filtered_unrecognized_roms.append(rom_path_str)
        
        unrecognized_roms = filtered_unrecognized_roms

        if not unrecognized_roms:
            QMessageBox.information(
                self, "No Unrecognized ROMs",
                "No unrecognized ROM files found in the root of the configured ROM folders for the current system after filtering."
            )
            return
        
        # Confirm with user
        extra_folder_name = "extra" # Define the folder name for extra files
        
        reply = QMessageBox.question(
            self, "Move Unrecognized Files",
            f"Move {len(unrecognized_roms)} unrecognized ROM file(s) to '{extra_folder_name}' subfolder(s)?\n\n"
            f"This will create an '{extra_folder_name}' folder in each ROM directory and move the files there.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        moved_files_count = 0
        failed_moves_details = []
        
        progress_dialog = ProgressDialog("Moving unrecognized files...", self)
        progress_dialog.progress_bar.setRange(0, len(unrecognized_roms))
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.progress_bar.setValue(0)

        for i, file_path_str in enumerate(unrecognized_roms):
            if progress_dialog.cancelled:
                break
            progress_dialog.progress_bar.setValue(i)
            progress_dialog.status_label.setText(f"Moving {Path(file_path_str).name}...")
            QApplication.processEvents() # Keep UI responsive

            source_path = Path(file_path_str)
            if not source_path.exists():
                error_msg = f"{source_path.name} (File not found at: {source_path})"
                failed_moves_details.append(error_msg)
                print(f"Error moving file: {error_msg}")
                continue
            
            # Determine which ROM folder this file belongs to and create target dir
            target_dir = None
            for folder_str in system_folders:
                folder_path = Path(folder_str).resolve()
                if source_path.parent == folder_path:
                    target_dir = folder_path / extra_folder_name
                    break
            
            if not target_dir:
                error_msg = f"{source_path.name} (Could not determine base ROM folder)"
                failed_moves_details.append(error_msg)
                print(f"Error moving file: {error_msg}")
                continue

            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                target_file_path = target_dir / source_path.name
                
                # Handle potential file conflicts (e.g., if file already exists in target)
                if target_file_path.exists():
                    # Simple conflict resolution: append a number
                    count = 1
                    base_name = target_file_path.stem
                    extension = target_file_path.suffix
                    while target_file_path.exists():
                        target_file_path = target_dir / f"{base_name}_{count}{extension}"
                        count += 1
                
                shutil.move(str(source_path), str(target_file_path))
                moved_files_count += 1
                # Optionally, update status in DB or internal lists if needed
                if hasattr(self, 'scanned_roms_manager'):
                    self.scanned_roms_manager.update_rom_status(self.current_system_id, str(source_path), ROMStatus.MOVED_EXTRA)
                    self.scanned_roms_manager.update_rom_path(str(self.current_system_id), str(source_path), str(target_file_path))

            except Exception as e:
                error_msg = f"{source_path.name} (Error: {e})"
                failed_moves_details.append(error_msg)
                print(f"Error moving file: {error_msg}")

        progress_dialog.progress_bar.setValue(len(unrecognized_roms))

        summary_message = f"Moved {moved_files_count} unrecognized file(s) to '{extra_folder_name}' subfolder(s)."
        if failed_moves_details:
            summary_message += "\n\nFailed to move some files:\n" + "\n".join(failed_moves_details)
            print("Move Complete with Errors:")
            print(summary_message) # Log the full error summary to terminal
            QMessageBox.warning(self, "Move Complete with Errors", summary_message)
        else:
            QMessageBox.information(self, "Move Complete", summary_message)
        
        # After moving, rescan the system to update the lists and database
        if self.current_system_id:
            print(f"Rescanning system {self.current_system_id} after moving extra files.")
            self.scan_rom_folder(prompt_for_folder=False)
        
        # self.update_rom_stats() # Refresh the displayed stats - This is now handled by on_scan_finished
    
    def move_broken_files(self):
        """Move broken files to subfolder."""
        if not self.current_system_id:
            QMessageBox.warning(
                self, "No System Selected",
                "Please select a system first."
            )
            return
        
        # Get broken ROMs for current system
        broken_roms = []
        current_system_id = self.current_system_id

        if hasattr(self, 'scanned_roms_manager'):
            # Get from database
            scanned_roms = self.scanned_roms_manager.get_scanned_roms_by_status(
                current_system_id, ROMStatus.BROKEN
            )
            broken_roms = [rom_data['file_path'] for rom_data in scanned_roms]
        elif hasattr(self, 'current_scan_results') and self.current_scan_results:
            # Get from memory results (these should be from the current session's scan)
            for result in self.current_scan_results:
                if result.status == ROMStatus.BROKEN and result.system_id == current_system_id:
                    broken_roms.append(result.file_path)
        
        if not broken_roms:
            QMessageBox.information(
                self, "No Broken ROMs",
                "No broken ROM files found for the current system. This might be because a fresh scan is needed after clearing cached data."
            )
            return

        # Get ROM folders from scanned ROM file paths
        system_folders = set()
        for rom_path_str in broken_roms:
            rom_path = Path(rom_path_str)
            system_folders.add(str(rom_path.parent))
        
        system_folders = list(system_folders)
        if not system_folders:
            QMessageBox.warning(
                self, "No ROM Folders",
                "No ROM folders found from scanned ROMs."
            )
            return

        # Filter broken_roms to only include files directly in a ROM folder
        system_folders_paths = [Path(folder).resolve() for folder in system_folders]
        filtered_broken_roms = []
        for rom_path_str in broken_roms:
            rom_path = Path(rom_path_str).resolve()
            if rom_path.parent in system_folders_paths:
                filtered_broken_roms.append(rom_path_str)
        
        broken_roms = filtered_broken_roms

        if not broken_roms:
            QMessageBox.information(
                self, "No Broken ROMs",
                "No broken ROM files found in the root of the configured ROM folders for the current system after filtering."
            )
            return
        
        # Confirm with user
        broken_folder_name = 'broken' # Ensure 'broken' is used, overriding any settings
        
        reply = QMessageBox.question(
            self, "Move Broken Files",
            f"Move {len(broken_roms)} broken ROM file(s) to '{broken_folder_name}' subfolder(s)?\n\n"
            f"This will create a '{broken_folder_name}' folder in each ROM directory and move the files there.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        moved_files = []
        failed_moves = []
        
        try:
            for file_path in broken_roms:
                source_path = Path(file_path)
                if not source_path.exists():
                    failed_moves.append(f"{source_path.name} (file not found at: {source_path})")
                    continue
                
                # Find which ROM folder this file belongs to
                rom_folder = None
                for folder in system_folders:
                    folder_path = Path(folder)
                    try:
                        # Check if file is within this ROM folder
                        source_path.relative_to(folder_path)
                        rom_folder = folder_path
                        break
                    except ValueError:
                        # File is not in this folder
                        continue
                
                if not rom_folder:
                    failed_moves.append(f"{source_path.name} (not in ROM folder - checked: {[str(Path(f)) for f in system_folders]})")
                    continue
                
                # Create broken subfolder
                # broken_folder_name is already defined and hardcoded earlier
                broken_folder = rom_folder / broken_folder_name
                try:
                    broken_folder.mkdir(exist_ok=True)
                    print(f"Created/verified broken folder: {broken_folder}")
                except Exception as e:
                    failed_moves.append(f"{source_path.name} (failed to create broken folder: {e})")
                    continue
                
                # Move file
                dest_path = broken_folder / source_path.name
                
                # Handle duplicate names
                counter = 1
                original_dest = dest_path
                while dest_path.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    dest_path = broken_folder / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                try:
                    print(f"Moving file from {source_path} to {dest_path}")
                    source_path.rename(dest_path)
                    moved_files.append(source_path.name)
                    print(f"Successfully moved: {source_path.name}")
                except Exception as e:
                    failed_moves.append(f"{source_path.name} (failed to move: {e})")
                    continue
                
        except Exception as e:
            QMessageBox.critical(
                self, "Error Moving Files",
                f"An error occurred while moving files:\n{str(e)}"
            )
            return
        
        # Show results
        if moved_files:
            message = f"Successfully moved {len(moved_files)} file(s) to '{broken_folder_name}' subfolder(s)."
            if failed_moves:
                message += f"\n\nFailed to move {len(failed_moves)} file(s):\n" + "\n".join(failed_moves)
            
            QMessageBox.information(self, "Move Complete", message)
            
            # Refresh the ROM scan to update the lists
            self.status_bar.showMessage("Refreshing ROM scan...")
            # QTimer.singleShot(100, self._refresh_rom_scan) # Removed old refresh
            self.rescan_current_rom_folder() # Added direct call to scan_rom_folder
        else:
            error_message = "No files were moved."
            if failed_moves:
                error_message += f"\n\nErrors:\n" + "\n".join(failed_moves)
            QMessageBox.warning(self, "Move Failed", error_message)
            # Also scan if move failed but there were attempts, to reflect any partial changes or state
            if failed_moves or moved_files: # Check if any operation was attempted
                self.scan_rom_folder()
    
    # def _refresh_rom_scan(self): # Removed unused method
    #     """Refresh the ROM scan for the current system."""
    #     if not self.current_system_id:
    #         return
    #     
    #     # Clear existing scan results from database to ensure moved files are removed
    #     self.scanned_roms_manager.clear_system_scans(self.current_system_id)
    #     
    #     # Get ROM folders for current system
    #     system_folders = self.settings_manager.get_system_rom_folders(str(self.current_system_id))
    #     if not system_folders:
    #         self.status_bar.showMessage("No ROM folders to scan")
    #         return
    #     
    #     # Use the first ROM folder for scanning (rglob will scan subdirectories recursively)
    #     folder = system_folders[0]
    #     folder_path = Path(folder)
    #     
    #     # Check if folder exists
    #     if not folder_path.exists():
    #         self.status_bar.showMessage(f"ROM folder not found: {folder_path}")
    #         QMessageBox.critical(
    #             self, "ROM Folder Not Found",
    #             f"The ROM folder does not exist:\n{folder_path}"
    #         )
    #         return
    #     
    #     # Start scan thread
    #     self.scan_thread = ROMScanThread(
    #         self.rom_scanner, folder, self.current_system_id
    #     )
    #     self.scan_thread.finished.connect(self.on_scan_finished)
    #     self.scan_thread.error.connect(self.on_scan_error)
    #     self.scan_thread.start()
    #     
    #     self.status_bar.showMessage(f"Scanning ROM folder: {folder_path}")
    
    def export_missing_list(self):
        """Export list of missing ROMs based on current filters."""
        if not self.current_system_id:
            QMessageBox.warning(self, "No System Selected", "Please select a system first.")
            return

        # Get ROM folder path from scanned ROMs (same logic as move_broken_files)
        rom_folder_path = None
        current_system_id = self.current_system_id
        
        # Get any scanned ROM to determine the ROM folder path
        if hasattr(self, 'scanned_roms_manager'):
            scanned_roms = self.scanned_roms_manager.get_all_scanned_roms(current_system_id)
            if scanned_roms:
                # Use the parent directory of the first scanned ROM as the ROM folder
                first_rom_path = Path(scanned_roms[0]['file_path'])
                rom_folder_path = str(first_rom_path.parent)
        elif hasattr(self, 'current_scan_results') and self.current_scan_results:
            # Get from memory results
            for result in self.current_scan_results:
                if result.system_id == current_system_id:
                    rom_folder_path = str(Path(result.file_path).parent)
                    break
        
        if not rom_folder_path:
            QMessageBox.warning(self, "ROM Path Not Configured", "No ROM path is configured for the current system. Please scan a ROM folder first.")
            return
        missing_folder_path = os.path.join(rom_folder_path, 'missing')
        output_file_path = os.path.join(missing_folder_path, 'missing_roms.txt')

        try:
            os.makedirs(missing_folder_path, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, "Error Creating Directory", f"Could not create directory {missing_folder_path}: {e}")
            return

        visible_missing_games_info = []
        # Iterate through the items in the missing_tree, which is what the user sees in the "Missing ROMs" tab
        for i in range(self.missing_tree.topLevelItemCount()):
            item = self.missing_tree.topLevelItem(i)
            if not item.isHidden(): # Should always be visible if in this tree
                # Column 1 is 'Game Name', Column 4 is 'CRC32' in missing_tree
                # Based on update_missing_roms: NumericTreeWidgetItem([
                # str(row_number), game_details['major_name'], game_details.get('region', ''), 
                # game_details.get('languages', ''), game_details['crc32'] ])
                game_name = item.text(1) 
                crc32 = item.text(4) 
                if game_name and crc32: # Ensure we have valid data
                    visible_missing_games_info.append({'name': game_name, 'crc32': crc32})

        if not visible_missing_games_info:
            QMessageBox.information(self, "No Missing ROMs", "No ROMs are currently listed in the 'Missing ROMs' tab to export.")
            return

        # The rest of the function uses this list, so rename the variable for clarity
        visible_dat_games_info = visible_missing_games_info

        scanned_roms_data = self.scanned_roms_manager.get_all_scanned_roms(self.current_system_id)
        found_rom_crcs = set()
        if scanned_roms_data:
            for rom_entry in scanned_roms_data:
                status = rom_entry.get('status')
                # Consider ROMStatus.CORRECT and ROMStatus.WRONG_FILENAME as found
                if status == ROMStatus.CORRECT.value or status == 'correct' or \
                   status == ROMStatus.WRONG_FILENAME.value or status == 'wrong_filename':
                    crc = rom_entry.get('matched_game_crc32') or rom_entry.get('crc32') # Prefer matched_game_crc32 if available
                    if crc:
                        found_rom_crcs.add(crc)
        
        filtered_missing_games = []
        for game_info in visible_dat_games_info:
            if game_info['crc32'] not in found_rom_crcs:
                filtered_missing_games.append(game_info['name'])

        if not filtered_missing_games:
            QMessageBox.information(self, "No Missing ROMs", "No missing ROMs found in the currently filtered list.")
            return

        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Missing ROMs for {self.system_combo.currentText()} (Filtered List)\n")
                f.write("=" * 50 + "\n\n")
                for game_name in filtered_missing_games:
                    f.write(f"{game_name}\n")
            
            QMessageBox.information(
                self, "Export Complete",
                f"Missing ROMs list saved to {output_file_path}"
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
        # Save current filter settings before closing
        if hasattr(self, 'current_system_id') and self.current_system_id is not None:
            self.save_current_filter_settings()
        
        # Save window state - convert QByteArray to base64 string for JSON serialization
        geometry = self.saveGeometry()
        geometry_str = base64.b64encode(geometry.data()).decode('utf-8')
        self.settings_manager.set("window_geometry", geometry_str)
        
        state = self.saveState()
        state_str = base64.b64encode(state.data()).decode('utf-8')
        self.settings_manager.set("window_state", state_str)
        
        self.settings_manager.save_settings()
        
        event.accept()