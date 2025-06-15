#!/usr/bin/env python3
"""
Settings Dialog for Romplestiltskin

Provides a user interface for configuring application settings.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QLabel, QLineEdit, QPushButton, QSpinBox,
    QCheckBox, QComboBox, QFileDialog, QDialogButtonBox,
    QFormLayout, QSlider, QTextEdit, QMessageBox, QListWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from core.settings_manager import SettingsManager
from ui.drag_drop_list import DragDropListWidget
from ui.theme import Theme

class SettingsDialog(QDialog):
    """Settings configuration dialog."""
    
    # Signal to notify when a system is removed
    system_removed = pyqtSignal(int)  # system_id
    
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        
        self.settings_manager = settings_manager
        self.temp_settings = settings_manager.get_all_settings().copy()
        
        # Initialize theme
        self.theme = Theme()
        self.setStyleSheet(self.theme.get_stylesheet())
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_general_tab()
        self.create_folders_tab()
        self.create_filters_tab()
        self.create_advanced_tab()
        self.create_system_management_tab()
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        layout.addWidget(button_box)
    
    def create_general_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Region Priority
        region_group = QGroupBox("Region Priority")
        region_layout = QVBoxLayout(region_group)
        
        region_help = QLabel(
            "Drag and drop to reorder regions by preference.\n"
            "Used when multiple versions of the same game are available."
        )
        region_help.setWordWrap(True)
        region_help.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 10px;")
        region_layout.addWidget(region_help)
        
        self.region_priority_list = DragDropListWidget()
        self.region_priority_list.setMaximumHeight(120)
        region_layout.addWidget(self.region_priority_list)
        
        # Buttons for region management
        region_buttons = QHBoxLayout()
        region_buttons.setSpacing(10)
        
        # Get theme colors for button styles
        colors = self.theme.get_colors()
        
        modern_button_style = f"""
            QPushButton {{
                background-color: {colors['highlight']};
                color: {colors['button_text']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['highlight_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['highlight_pressed']};
            }}
        """
        
        secondary_button_style = f"""
            QPushButton {{
                background-color: {colors['medium_gray']};
                color: {colors['button_text']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['light_gray']};
            }}
            QPushButton:pressed {{
                background-color: {colors['border']};
            }}
        """
        
        self.add_region_edit = QLineEdit()
        self.add_region_edit.setPlaceholderText("Add new region...")
        region_buttons.addWidget(self.add_region_edit)
        
        self.add_region_button = QPushButton("➕ Add")
        self.add_region_button.setStyleSheet(modern_button_style)
        self.add_region_button.clicked.connect(self.add_region)
        region_buttons.addWidget(self.add_region_button)
        
        self.remove_region_button = QPushButton("➖ Remove")
        self.remove_region_button.setStyleSheet(secondary_button_style)
        self.remove_region_button.clicked.connect(self.remove_region)
        region_buttons.addWidget(self.remove_region_button)
        
        region_layout.addLayout(region_buttons)
        layout.addWidget(region_group)
        
        # Language Priority
        language_group = QGroupBox("Language Priority")
        language_layout = QVBoxLayout(language_group)
        
        language_help = QLabel(
            "Drag and drop to reorder languages by preference.\n"
            "Used when multiple language versions are available."
        )
        language_help.setWordWrap(True)
        language_help.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 10px;")
        language_layout.addWidget(language_help)
        
        self.language_priority_list = DragDropListWidget()
        self.language_priority_list.setMaximumHeight(120)
        language_layout.addWidget(self.language_priority_list)
        
        # Buttons for language management
        language_buttons = QHBoxLayout()
        language_buttons.setSpacing(10)
        
        self.add_language_edit = QLineEdit()
        self.add_language_edit.setPlaceholderText("Add new language...")
        language_buttons.addWidget(self.add_language_edit)
        
        self.add_language_button = QPushButton("➕ Add")
        self.add_language_button.setStyleSheet(modern_button_style)
        self.add_language_button.clicked.connect(self.add_language)
        language_buttons.addWidget(self.add_language_button)
        
        self.remove_language_button = QPushButton("➖ Remove")
        self.remove_language_button.setStyleSheet(secondary_button_style)
        self.remove_language_button.clicked.connect(self.remove_language)
        language_buttons.addWidget(self.remove_language_button)
        
        language_layout.addLayout(language_buttons)
        
        layout.addWidget(language_group)
        
        # Performance
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(1, 100)
        self.chunk_size_spin.setSuffix(" MB")
        performance_layout.addRow("Chunk Size:", self.chunk_size_spin)
        
        chunk_help = QLabel(
            "Size of data chunks when calculating CRC32 checksums.\n"
            "Larger values use more memory but may be faster."
        )
        chunk_help.setWordWrap(True)
        chunk_help.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 10px;")
        performance_layout.addRow(chunk_help)
        
        layout.addWidget(performance_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "General")
    
    def create_folders_tab(self):
        """Create the folders configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Define button styles for this tab
        modern_button_style = f"""
            QPushButton {{
                background-color: {colors['highlight']};
                color: {colors['button_text']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['highlight_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['highlight_pressed']};
            }}
        """
        
        # DAT Files
        dat_group = QGroupBox("DAT Files")
        dat_layout = QFormLayout(dat_group)
        
        dat_row = QHBoxLayout()
        self.dat_folder_edit = QLineEdit()
        self.dat_folder_edit.setReadOnly(True)
        dat_row.addWidget(self.dat_folder_edit)
        
        self.dat_browse_button = QPushButton("📁 Browse...")
        self.dat_browse_button.setStyleSheet(modern_button_style)
        self.dat_browse_button.clicked.connect(self.browse_dat_folder)
        dat_row.addWidget(self.dat_browse_button)
        
        dat_layout.addRow("DAT Folder:", dat_row)
        
        dat_help = QLabel(
            "Folder containing No-Intro DAT files.\n"
            "These files define the official ROM sets for each system."
        )
        dat_help.setWordWrap(True)
        dat_help.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 10px;")
        dat_layout.addRow(dat_help)
        
        layout.addWidget(dat_group)
        
        # Output Folders
        output_group = QGroupBox("Output Folders")
        output_layout = QFormLayout(output_group)
        
        # Extra files folder
        extra_row = QHBoxLayout()
        self.extra_folder_edit = QLineEdit()
        extra_row.addWidget(self.extra_folder_edit)
        
        self.extra_browse_button = QPushButton("📁 Browse...")
        self.extra_browse_button.setStyleSheet(modern_button_style)
        self.extra_browse_button.clicked.connect(self.browse_extra_folder)
        extra_row.addWidget(self.extra_browse_button)
        
        output_layout.addRow("Extra Files:", extra_row)
        
        # Broken files folder
        broken_row = QHBoxLayout()
        self.broken_folder_edit = QLineEdit()
        broken_row.addWidget(self.broken_folder_edit)
        
        self.broken_browse_button = QPushButton("📁 Browse...")
        self.broken_browse_button.setStyleSheet(modern_button_style)
        self.broken_browse_button.clicked.connect(self.browse_broken_folder)
        broken_row.addWidget(self.broken_browse_button)
        
        output_layout.addRow("Broken Files:", broken_row)
        
        output_help = QLabel(
            "Folders where unrecognized and broken files will be moved.\n"
            "Leave empty to create subfolders in the ROM directory."
        )
        output_help.setWordWrap(True)
        output_help.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 10px;")
        output_layout.addRow(output_help)
        
        layout.addWidget(output_group)


        layout.addStretch()
        self.tab_widget.addTab(tab, "Folders")
    
    def create_filters_tab(self):
        """Create the filters settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Default Filters
        filter_group = QGroupBox("Default Filter Settings")
        filter_layout = QVBoxLayout(filter_group)
        
        filter_help = QLabel(
            "These settings control which types of ROMs are shown by default.\n"
            "You can always change these filters in the main window."
        )
        filter_help.setWordWrap(True)
        filter_help.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 10px;")
        filter_layout.addWidget(filter_help)
        
        # Checkboxes for each filter
        self.show_beta_cb = QCheckBox("Show Beta versions")
        filter_layout.addWidget(self.show_beta_cb)
        
        self.show_demo_cb = QCheckBox("Show Demo versions")
        filter_layout.addWidget(self.show_demo_cb)
        
        self.show_proto_cb = QCheckBox("Show Prototype versions")
        filter_layout.addWidget(self.show_proto_cb)
        
        self.show_unlicensed_cb = QCheckBox("Show Unlicensed games")
        filter_layout.addWidget(self.show_unlicensed_cb)
        
        self.show_translation_cb = QCheckBox("Show Translations")
        filter_layout.addWidget(self.show_translation_cb)
        
        self.show_modified_cb = QCheckBox("Show Modified/Hacked games")
        filter_layout.addWidget(self.show_modified_cb)
        
        self.show_overdump_cb = QCheckBox("Show Overdumps")
        filter_layout.addWidget(self.show_overdump_cb)
        
        layout.addWidget(filter_group)
        
        # Duplicate Handling
        duplicate_group = QGroupBox("Duplicate Handling")
        duplicate_layout = QFormLayout(duplicate_group)
        
        self.duplicate_action_combo = QComboBox()
        self.duplicate_action_combo.addItems([
            "Keep Best (by region/language priority)",
            "Keep All",
            "Ask Each Time"
        ])
        duplicate_layout.addRow("When duplicates found:", self.duplicate_action_combo)
        
        layout.addWidget(duplicate_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Filters")
    
    def create_advanced_tab(self):
        """Create the advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File Operations
        file_ops_group = QGroupBox("File Operations")
        file_ops_layout = QVBoxLayout(file_ops_group)
        
        self.backup_before_rename_cb = QCheckBox("Create backup before renaming files")
        file_ops_layout.addWidget(self.backup_before_rename_cb)
        
        self.confirm_file_operations_cb = QCheckBox("Confirm before moving/renaming files")
        file_ops_layout.addWidget(self.confirm_file_operations_cb)
        
        layout.addWidget(file_ops_group)
        
        # Matching Algorithm
        matching_group = QGroupBox("Matching Algorithm")
        matching_layout = QFormLayout(matching_group)
        
        self.similarity_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.similarity_threshold_slider.setRange(50, 100)
        self.similarity_threshold_slider.valueChanged.connect(self.update_similarity_label)
        
        self.similarity_label = QLabel("80%")
        
        threshold_row = QHBoxLayout()
        threshold_row.addWidget(self.similarity_threshold_slider)
        threshold_row.addWidget(self.similarity_label)
        
        matching_layout.addRow("Similarity Threshold:", threshold_row)
        
        threshold_help = QLabel(
            "Minimum similarity percentage for fuzzy filename matching.\n"
            "Lower values find more matches but may include false positives."
        )
        threshold_help.setWordWrap(True)
        threshold_help.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 10px;")
        matching_layout.addRow(threshold_help)
        
        layout.addWidget(matching_group)
        
        # Debug Options
        debug_group = QGroupBox("Debug Options")
        debug_layout = QVBoxLayout(debug_group)
        
        self.enable_debug_logging_cb = QCheckBox("Enable debug logging")
        debug_layout.addWidget(self.enable_debug_logging_cb)
        
        self.log_file_operations_cb = QCheckBox("Log file operations")
        debug_layout.addWidget(self.log_file_operations_cb)
        
        layout.addWidget(debug_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Advanced")
    
    def browse_dat_folder(self):
        """Browse for DAT folder."""
        current = self.dat_folder_edit.text() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Select DAT Folder", current)
        if folder:
            self.dat_folder_edit.setText(folder)
            self.temp_settings['dat_folder_path'] = folder
    
    def browse_extra_folder(self):
        """Browse for extra files folder."""
        current = self.extra_folder_edit.text() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Select Extra Files Folder", current)
        if folder:
            self.extra_folder_edit.setText(folder)
            self.temp_settings['extra_files_folder'] = folder
    
    def browse_broken_folder(self):
        """Browse for broken files folder."""
        current = self.broken_folder_edit.text() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Select Broken Files Folder", current)
        if folder:
            self.broken_folder_edit.setText(folder)
            self.temp_settings['broken_files_folder'] = folder
    
    def get_button_styles(self):
        """Helper to provide consistent button styles."""
        # These styles are copied from create_general_tab for consistency
        colors = self.theme.get_colors()
        modern_button_style = f"""
            QPushButton {{
                background-color: {colors['highlight']};
                color: {colors['button_text']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['highlight_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['highlight_pressed']};
            }}
        """
        secondary_button_style = f"""
            QPushButton {{
                background-color: {colors['secondary']};
                color: {colors['button_text']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['secondary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['secondary_pressed']};
            }}
        """
        return {"modern": modern_button_style, "secondary": secondary_button_style}



    def remove_general_rom_folder(self):
        selected_items = self.rom_folders_list.selectedItems()
        if not selected_items: 
            QMessageBox.warning(self, "No Selection", "Please select a folder to remove.")
            return
        for item in selected_items:
            self.rom_folders_list.takeItem(self.rom_folders_list.row(item))

    def update_similarity_label(self, value: int):
        """Update similarity threshold label."""
        self.similarity_label.setText(f"{value}%")
        self.temp_settings['similarity_threshold'] = value / 100.0
    
    def load_settings(self):
        """Load current settings into the UI."""
        # General tab
        region_priority = self.temp_settings.get('region_priority', [
            # Top priority regions in specified order
            "USA", "Japan", "Europe", "World", "UK",
            # Other regions in alphabetical order
            "Australia", "Austria", "Belgium", "Bulgaria", "Canada", "Croatia", 
            "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", 
            "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", 
            "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", 
            "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"
        ])
        self.region_priority_list.set_items(region_priority)
        
        language_priority = self.temp_settings.get('language_priority', ['En', 'Es', 'Fr', 'De', 'It', 'Pt', 'Ja'])
        self.language_priority_list.set_items(language_priority)
        self.chunk_size_spin.setValue(
            self.temp_settings.get('chunk_size_mb', 16)
        )
        
        # Folders tab
        self.dat_folder_edit.setText(
            self.temp_settings.get('dat_folder_path', '')
        )
        self.extra_folder_edit.setText(
            self.temp_settings.get('extra_files_folder', '')
        )
        self.broken_folder_edit.setText(
            self.temp_settings.get('broken_files_folder', '')
        )

        # Filters tab
        filters = self.temp_settings.get('default_filters', {})
        self.show_beta_cb.setChecked(filters.get('show_beta', False))
        self.show_demo_cb.setChecked(filters.get('show_demo', False))
        self.show_proto_cb.setChecked(filters.get('show_proto', False))
        self.show_unlicensed_cb.setChecked(filters.get('show_unlicensed', True))
        self.show_translation_cb.setChecked(filters.get('show_translation', False))
        self.show_modified_cb.setChecked(filters.get('show_modified', False))
        self.show_overdump_cb.setChecked(filters.get('show_overdump', False))
        
        duplicate_action = self.temp_settings.get('duplicate_action', 'keep_best')
        if duplicate_action == 'keep_best':
            self.duplicate_action_combo.setCurrentIndex(0)
        elif duplicate_action == 'keep_all':
            self.duplicate_action_combo.setCurrentIndex(1)
        else:
            self.duplicate_action_combo.setCurrentIndex(2)
        
        # Advanced tab
        self.backup_before_rename_cb.setChecked(
            self.temp_settings.get('backup_before_operations', False)
        )
        self.confirm_file_operations_cb.setChecked(
            self.temp_settings.get('confirm_file_operations', True)
        )
        
        threshold = int(self.temp_settings.get('similarity_threshold', 0.8) * 100)
        self.similarity_threshold_slider.setValue(threshold)
        self.update_similarity_label(threshold)

        self.enable_debug_logging_cb.setChecked(
            self.temp_settings.get('enable_debug_logging', False)
        )
        self.log_file_operations_cb.setChecked(
            self.temp_settings.get('log_file_operations', False)
        )
    
    def save_settings_from_ui(self):
        """Save settings from UI to temp settings."""
        # General tab
        self.temp_settings['region_priority'] = self.region_priority_list.get_items()
        self.temp_settings['language_priority'] = self.language_priority_list.get_items()
        
        self.temp_settings['chunk_size_mb'] = self.chunk_size_spin.value()
        
        # Folders tab
        self.temp_settings['dat_folder_path'] = self.dat_folder_edit.text()
        self.temp_settings['extra_files_folder'] = self.extra_folder_edit.text()
        self.temp_settings['broken_files_folder'] = self.broken_folder_edit.text()
        
        # Filters tab
        self.temp_settings['default_filters'] = {
            'show_beta': self.show_beta_cb.isChecked(),
            'show_demo': self.show_demo_cb.isChecked(),
            'show_proto': self.show_proto_cb.isChecked(),
            'show_unlicensed': self.show_unlicensed_cb.isChecked(),
            'show_translation': self.show_translation_cb.isChecked(),
            'show_modified': self.show_modified_cb.isChecked(),
            'show_overdump': self.show_overdump_cb.isChecked()
        }
        
        duplicate_index = self.duplicate_action_combo.currentIndex()
        if duplicate_index == 0:
            self.temp_settings['duplicate_action'] = 'keep_best'
        elif duplicate_index == 1:
            self.temp_settings['duplicate_action'] = 'keep_all'
        else:
            self.temp_settings['duplicate_action'] = 'ask'
        
        # Advanced tab
        self.temp_settings['backup_before_rename'] = self.backup_before_rename_cb.isChecked()
        self.temp_settings['confirm_file_operations'] = self.confirm_file_operations_cb.isChecked()
        self.temp_settings['similarity_threshold'] = self.similarity_threshold_slider.value() / 100.0
        self.temp_settings['enable_debug_logging'] = self.enable_debug_logging_cb.isChecked()
        self.temp_settings['log_file_operations'] = self.log_file_operations_cb.isChecked()

    def add_region(self):
        """Add a new region to the priority list."""
        text = self.add_region_edit.text().strip()
        if text:
            self.region_priority_list.add_item(text)
            self.add_region_edit.clear()
    
    def remove_region(self):
        """Remove the selected region from the priority list."""
        self.region_priority_list.remove_selected()
    
    def add_language(self):
        """Add a new language to the priority list."""
        text = self.add_language_edit.text().strip()
        if text:
            self.language_priority_list.add_item(text)
            self.add_language_edit.clear()
    
    def remove_language(self):
        """Remove the selected language from the priority list."""
        self.language_priority_list.remove_selected()
    
    def apply_settings(self):
        """Apply settings without closing dialog."""
        self.save_settings_from_ui()
        
        # Apply settings from temp_settings to actual settings_manager
        for key, value in self.temp_settings.items():
            if key == 'system_filter_settings':
                # value is a dict like {system_id: settings_dict}
                for sys_id, settings_val in value.items():
                    self.settings_manager.set_system_filter_settings(sys_id, settings_val)
            elif key == 'system_rom_folders':
                # value is a dict like {system_id: folder_paths_list}
                for sys_id, folder_paths in value.items():
                    self.settings_manager.set_system_rom_folders(sys_id, folder_paths)
            elif hasattr(self.settings_manager, f"set_{key}"):
                getattr(self.settings_manager, f"set_{key}")(value)
            # Add other special cases if necessary

        self.settings_manager.save_settings()
    
    def accept_settings(self):
        """Accept and apply settings, then close dialog."""
        self.apply_settings()
        self.accept()
    
    def restore_defaults(self):
        """Restore default settings."""
        self.temp_settings = self.settings_manager.get_default_settings().copy()
        self.load_settings()
    
    def create_system_management_tab(self):
        """Create the system management tab with reset options."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Warning section
        warning_group = QGroupBox("⚠️ Danger Zone")
        warning_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {colors['error']};
                border: 2px solid {colors['error']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }}
        """)
        warning_layout = QVBoxLayout(warning_group)
        warning_layout.setSpacing(15)
        
        warning_text = QLabel(
            "These operations cannot be undone. Please make sure you have backups "
            "of any important data before proceeding."
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet(f"color: {colors['secondary_text']}; font-weight: normal; font-size: 12px;")
        warning_layout.addWidget(warning_text)
        
        # Reset buttons with improved styling
        button_style = f"""
            QPushButton {{
                background-color: {colors['error']};
                color: {colors['button_text']};
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {colors['error_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['error_pressed']};
            }}
        """
        
        # Reset Program button
        reset_program_btn = QPushButton("🔄 Reset Entire Program")
        reset_program_btn.setStyleSheet(button_style)
        reset_program_btn.clicked.connect(self.reset_entire_program)
        warning_layout.addWidget(reset_program_btn)
        
        reset_program_desc = QLabel(
            "Deletes all databases, settings, and cached data. "
            "ROM files in your ROM folders will NOT be deleted."
        )
        reset_program_desc.setWordWrap(True)
        reset_program_desc.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 11px; margin-left: 20px;")
        warning_layout.addWidget(reset_program_desc)
        
        # System selection for partial reset
        system_reset_group = QGroupBox("Remove Specific System")
        system_reset_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                border: 1px solid {colors['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }}
        """)
        system_reset_layout = QVBoxLayout(system_reset_group)
        system_reset_layout.setSpacing(10)
        
        # System selection combo
        system_combo_layout = QHBoxLayout()
        system_combo_layout.setSpacing(10)
        
        system_label = QLabel("System:")
        system_label.setStyleSheet("font-weight: normal;")
        system_combo_layout.addWidget(system_label)
        
        self.system_combo = QComboBox()
        self.system_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                min-width: 200px;
            }}
            QComboBox:focus {{
                border-color: {colors['highlight']};
            }}
        """)
        self.populate_system_combo()
        system_combo_layout.addWidget(self.system_combo)
        system_combo_layout.addStretch()
        
        system_reset_layout.addLayout(system_combo_layout)
        
        # Remove system button
        remove_system_btn = QPushButton("🗑️ Remove Selected System")
        remove_system_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['warning']};
                color: {colors['button_text']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['warning_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['warning_pressed']};
            }}
        """)
        remove_system_btn.clicked.connect(self.remove_selected_system)
        system_reset_layout.addWidget(remove_system_btn)
        
        remove_system_desc = QLabel(
            "Removes the selected system and all its games from the database. "
            "ROM files will NOT be deleted."
        )
        remove_system_desc.setWordWrap(True)
        remove_system_desc.setStyleSheet(f"color: {colors['secondary_text']}; font-size: 11px; margin-left: 20px;")
        system_reset_layout.addWidget(remove_system_desc)
        
        warning_layout.addWidget(system_reset_group)
        layout.addWidget(warning_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔧 System Management")
    
    def populate_system_combo(self):
        """Populate the system combo box with available systems."""
        self.system_combo.clear()
        self.system_combo.addItem("Select a system...", None)
        
        # Get database manager from settings manager if available
        if hasattr(self.settings_manager, 'db_manager'):
            try:
                systems = self.settings_manager.db_manager.get_all_systems()
                for system in systems:
                    self.system_combo.addItem(system['system_name'], system['id'])
            except Exception as e:
                print(f"Error loading systems: {e}")
    
    def reset_entire_program(self):
        """Reset the entire program - database, settings, and cache."""
        reply = QMessageBox.question(
            self,
            "Reset Entire Program",
            "Are you sure you want to reset the entire program?\n\n"
            "This will delete:\n"
            "• All system databases\n"
            "• All settings and preferences\n"
            "• All cached data\n\n"
            "ROM files in your ROM folders will NOT be deleted.\n\n"
            "This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            errors = []
            
            try:
                # Clear all ignored CRCs from settings before deletion
                self.settings_manager.set("ignored_crcs", [])
                # Clear all system-specific ignored CRCs
                if "system_ignored_crcs" in self.settings_manager.settings:
                    self.settings_manager.settings["system_ignored_crcs"] = {}
                # Clear all system-specific filter settings
                if "system_filter_settings" in self.settings_manager.settings:
                    self.settings_manager.settings["system_filter_settings"] = {}
                # Clear global filter settings that serve as defaults
                if "filter_settings" in self.settings_manager.settings:
                    self.settings_manager.settings["filter_settings"] = {}
                
                if not self.settings_manager.save_settings():
                    errors.append("Failed to save cleared settings during reset.")
                
                # Force garbage collection to release any database file handles
                # The DatabaseManager uses context managers so connections are auto-closed
                
                # Force garbage collection to release any file handles
                import gc
                gc.collect()
                
                # Get paths before attempting deletion
                app_data = Path.home() / ".romplestiltskin"
                db_path = None
                config_path = None
                
                if hasattr(self.settings_manager, 'db_manager'):
                    db_path = self.settings_manager.db_manager.db_path
                
                config_path = self.settings_manager.config_file
                
                # Try to delete individual files first
                if db_path and db_path.exists():
                    try:
                        db_path.unlink()
                        if db_path.exists():
                            errors.append(f"Database file still exists: {db_path}")
                    except Exception as e:
                        errors.append(f"Could not delete database: {e}")
                
                if config_path and config_path.exists():
                    try:
                        config_path.unlink()
                        if config_path.exists():
                            errors.append(f"Config file still exists: {config_path}")
                    except Exception as e:
                        errors.append(f"Could not delete config: {e}")
                
                # Try to remove the entire directory as a fallback
                if app_data.exists():
                    try:
                        shutil.rmtree(app_data, ignore_errors=True)
                        # Verify deletion
                        if app_data.exists():
                            # Try force deletion on Windows
                            import os
                            import stat
                            def handle_remove_readonly(func, path, exc):
                                os.chmod(path, stat.S_IWRITE)
                                func(path)
                            
                            shutil.rmtree(app_data, onerror=handle_remove_readonly)
                            
                            if app_data.exists():
                                errors.append(f"Could not completely remove directory: {app_data}")
                    except Exception as e:
                        errors.append(f"Could not remove app data directory: {e}")
                
                if errors:
                    error_msg = "Reset completed with warnings:\n\n" + "\n".join(errors)
                    error_msg += "\n\nSome files may need to be manually deleted.\nPlease restart the application."
                    QMessageBox.warning(
                        self,
                        "Reset Complete with Warnings",
                        error_msg
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Reset Complete",
                        "Program has been reset successfully.\n\n"
                        "Please restart the application."
                    )
                
                # Close the dialog and signal parent to restart
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Reset Failed",
                    f"Failed to reset program: {str(e)}\n\n"
                    f"You may need to manually delete:\n"
                    f"• {Path.home() / '.romplestiltskin'}"
                )
    
    def remove_selected_system(self):
        """Remove the selected system from the database."""
        system_id = self.system_combo.currentData()
        system_name = self.system_combo.currentText()
        
        if system_id is None:
            QMessageBox.warning(
                self,
                "No System Selected",
                "Please select a system to remove."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Remove System",
            f"Are you sure you want to remove the system '{system_name}'?\n\n"
            "This will delete:\n"
            f"• All games in the {system_name} database\n"
            f"• All {system_name} system data\n\n"
            "ROM files will NOT be deleted.\n\n"
            "This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if hasattr(self.settings_manager, 'db_manager'):
                    self.settings_manager.db_manager.delete_system(system_id)
                    
                    # Emit signal that system was removed
                    self.system_removed.emit(system_id)
                    
                    QMessageBox.information(
                        self,
                        "System Removed",
                        f"System '{system_name}' has been removed successfully."
                    )
                    
                    # Refresh the combo box
                    self.populate_system_combo()
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Remove Failed",
                    f"Failed to remove system: {str(e)}"
                )