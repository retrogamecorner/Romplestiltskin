#!/usr/bin/env python3
"""Drag and Drop List Widget for Romplestiltskin

Provides a reorderable list widget for priority settings and region filtering.
"""

from typing import List, Dict
from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, 
    QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDrag, QPixmap, QPainter, QIcon, QPen, QColor
from PyQt6.QtSvg import QSvgRenderer
import os

class DragDropListWidget(QListWidget):
    """A list widget that supports drag and drop reordering."""
    
    items_reordered = pyqtSignal()  # Emitted when items are reordered
    item_dropped_from_external = pyqtSignal(str, int)  # Emitted when item is dropped from another list with position
    
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.original_style = None  # Will be set by parent widget
        
        # Enable drag and drop
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.drag_indicator_position = -1
        
        # Connect to model changes to emit our signal
        self.model().rowsMoved.connect(self.items_reordered.emit)
    
    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # Highlight the widget
            self.setStyleSheet(self.theme.get_drag_drop_highlight_style())
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        # Reset styling when drag leaves
        self.drag_indicator_position = -1
        self.update()
        # Remove drag highlight styling - restore original style
        self.restore_original_style()
        super().dragLeaveEvent(event)
    
    def dragMoveEvent(self, event):
        """Handle drag move events."""
        if event.mimeData().hasText():
            # Calculate drop position
            index = self.indexAt(event.position().toPoint())
            if index.isValid():
                rect = self.visualRect(index)
                if event.position().y() < rect.center().y():
                    self.drag_indicator_position = index.row()
                else:
                    self.drag_indicator_position = index.row() + 1
            else:
                self.drag_indicator_position = self.count()
            
            self.update()  # Trigger repaint to show indicator
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        """Handle drop events."""
        if event.mimeData().hasText():
            # Get the dropped text
            dropped_text = event.mimeData().text()
            
            # Store the drop position before resetting
            drop_position = self.drag_indicator_position if self.drag_indicator_position >= 0 else self.count()
            
            # Reset drag indicator and styling
            self.drag_indicator_position = -1
            self.restore_original_style()
            
            # Check if this is an external drop (from another widget)
            if event.source() != self:
                # Check if item already exists in this list
                existing_items = self.get_items()
                if dropped_text not in existing_items:
                    # Only emit signal - let the RegionFilterWidget handle the actual addition
                    self.item_dropped_from_external.emit(dropped_text, drop_position)
                
                event.acceptProposedAction()
            else:
                # This is an internal drag - handle with default behavior for reordering
                super().dropEvent(event)
        else:
            # Handle internal moves
            super().dropEvent(event)
    
    def set_original_style(self, style):
        """Set the original style to restore after drag operations."""
        self.original_style = style
    
    def restore_original_style(self):
        """Restore the original style after drag operations."""
        if self.original_style:
            self.setStyleSheet(self.original_style)
        else:
            # Fallback to normal style if no original style is set
            self.setStyleSheet(self.theme.get_drag_drop_normal_style())
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Draw drop indicator line
        if self.drag_indicator_position >= 0:
            painter = QPainter(self.viewport())
            painter.setPen(QPen(QColor(self.theme.colors['drag_drop']['highlight_border']), 2))
            
            if self.drag_indicator_position < self.count():
                rect = self.visualItemRect(self.item(self.drag_indicator_position))
                y = rect.top()
            else:
                if self.count() > 0:
                    rect = self.visualItemRect(self.item(self.count() - 1))
                    y = rect.bottom()
                else:
                    y = 0
            
            painter.drawLine(0, y, self.viewport().width(), y)
            painter.end()
    
    def startDrag(self, supportedActions):
        """Start drag operation."""
        # Get the selected item text
        current_item = self.currentItem()
        if current_item:
            drag = QDrag(self)
            mimeData = QMimeData()
            mimeData.setText(current_item.text())
            drag.setMimeData(mimeData)
            
            # Execute the drag
            result = drag.exec()
            
            # If the drag was successful and moved to another widget, remove from this list
            if result == Qt.DropAction.MoveAction:
                # Check if the item still exists in this list (it shouldn't if moved externally)
                row = self.row(current_item)
                if row >= 0:
                    # Only remove if the drop was external (item still exists here)
                    # We'll let the parent widget handle the removal logic
                    pass
    
    def set_items(self, items: List[str]) -> None:
        """Set the list items.
        
        Args:
            items: List of strings to display
        """
        self.clear()
        for item in items:
            self.addItem(item)
    
    def get_items(self) -> List[str]:
        """Get the current list items in order.
        
        Returns:
            List of strings in current order
        """
        items = []
        for i in range(self.count()):
            items.append(self.item(i).text())
        return items
    
    def add_item(self, text: str) -> None:
        """Add a new item to the list.
        
        Args:
            text: Text for the new item
        """
        if text and text not in self.get_items():
            self.addItem(text)
            self.items_reordered.emit()
    
    def remove_selected(self) -> None:
        """Remove the currently selected item."""
        current_row = self.currentRow()
        if current_row >= 0:
            self.takeItem(current_row)
            self.items_reordered.emit()
    
    def remove_item(self, text: str) -> None:
        """Remove an item by text.
        
        Args:
            text: Text of the item to remove
        """
        for i in range(self.count()):
            item = self.item(i)
            if item and item.text() == text:
                self.takeItem(i)
                self.items_reordered.emit()
                break
    
    def move_up(self) -> None:
        """Move the selected item up one position."""
        current_row = self.currentRow()
        if current_row > 0:
            item = self.takeItem(current_row)
            self.insertItem(current_row - 1, item)
            self.setCurrentRow(current_row - 1)
            self.items_reordered.emit()
    
    def move_down(self) -> None:
        """Move the selected item down one position."""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < self.count() - 1:
            item = self.takeItem(current_row)
            self.insertItem(current_row + 1, item)
            self.setCurrentRow(current_row + 1)
            self.items_reordered.emit()


class RegionFilterWidget(QWidget):
    """A dual-list widget for region filtering with drag-and-drop support."""
    
    filters_changed = pyqtSignal()  # Emitted when filter configuration changes
    
    # Region flag SVG mapping
    REGION_FLAGS = {
        # Priority regions in correct order
        'USA': 'us.svg',
        'Japan': 'jp.svg',
        'Europe': 'eu.svg', 
        'World': 'un.svg',  # Using UN flag for world
        'UK': 'gb.svg',
        # Other regions in alphabetical order
        'Australia': 'au.svg',
        'Brazil': 'br.svg',
        'Canada': 'ca.svg',
        'China': 'cn.svg',
        'France': 'fr.svg',
        'Germany': 'de.svg',
        'Hong Kong': 'hk.svg',
        'Italy': 'it.svg',
        'Korea': 'kr.svg',
        'Netherlands': 'nl.svg',
        'Spain': 'es.svg',
        'Sweden': 'se.svg',
        'Taiwan': 'tw.svg',
        'Unknown': 'xx.svg'  # Using unknown flag
    }
    
    def get_flag_icon(self, region: str) -> QIcon:
        """Get QIcon for a region's flag."""
        flag_file = self.REGION_FLAGS.get(region, 'xx.svg')
        flag_path = os.path.join(os.path.dirname(__file__), 'flags', flag_file)
        
        if os.path.exists(flag_path):
            # Create QIcon from SVG
            icon = QIcon(flag_path)
            return icon
        else:
            # Fallback to empty icon if SVG not found
            return QIcon()
    
    def __init__(self, theme, settings_manager=None, system_id=None, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)  # Ensure background color is applied
        self.theme = theme
        self.settings_manager = settings_manager
        self.current_system_id = system_id
        self.all_known_regions = list(self.REGION_FLAGS.keys()) # Keep a list of all possible regions
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus border on main widget
        self.setup_ui()
        self.load_region_settings() # Load settings after UI is set up

        # Connect signals for drag/drop between lists - use consistent method names
        self.available_list.item_dropped_from_external.connect(self._handle_drop_to_available)
        self.ignored_list.item_dropped_from_external.connect(self._handle_drop_to_ignored)
        self.available_list.items_reordered.connect(self.save_and_emit_changes)
        self.ignored_list.items_reordered.connect(self.save_and_emit_changes)
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🌍 Region Priority Filter")
        title.setStyleSheet(self.theme.get_drag_drop_title_style())
        title.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus border
        title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)  # Prevent mouse events that could trigger focus
        layout.addWidget(title)
        
        # Main content layout with two columns
        main_content = QHBoxLayout()
        
        # Left column for available regions only
        left_column = QVBoxLayout()
        
        # Available regions label
        left_label = QLabel("Available Regions")
        left_label.setStyleSheet(self.theme.get_drag_drop_label_style())
        left_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus border
        left_column.addWidget(left_label)
        
        # Available regions list
        self.available_list = DragDropListWidget(self.theme)
        self.available_list.setObjectName("drag_drop_list")
        self.available_list.setAcceptDrops(True)
        self.available_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.available_list.setMinimumHeight(150)  # Reduce height to fit interface
        self.available_list.setMaximumHeight(200)  # Set maximum height to prevent overflow
        self.available_list.setMinimumWidth(180)  # Increase width for icons
        self.available_list.setIconSize(QSize(20, 15))  # Set icon size for flags
        available_style = self.theme.get_drag_drop_available_list_style()
        self.available_list.setStyleSheet(available_style)
        self.available_list.set_original_style(available_style)
        left_column.addWidget(self.available_list)
        
        # Add stretch to fill remaining space
        left_column.addStretch()
        
        main_content.addLayout(left_column)
        
        # Transfer buttons (middle column)
        buttons_layout = QVBoxLayout()
        buttons_layout.addStretch()
        
        self.ignore_button = QPushButton("⮞")
        self.ignore_button.setToolTip("Move to ignore list")
        self.ignore_button.setStyleSheet(self.theme.get_button_style("CircularMoveButton"))
        self.ignore_button.clicked.connect(self.move_to_ignore)
        buttons_layout.addWidget(self.ignore_button)
        
        self.restore_button = QPushButton("⮜")
        self.restore_button.setToolTip("Restore from ignore list")
        self.restore_button.setStyleSheet(self.theme.get_button_style("CircularMoveButton"))
        self.restore_button.clicked.connect(self.move_to_available)
        buttons_layout.addWidget(self.restore_button)
        
        buttons_layout.addStretch()
        main_content.addLayout(buttons_layout)
        
        # Right column for ignored regions and controls
        right_column = QVBoxLayout()
        
        # Ignored regions label
        right_label = QLabel("Ignored Regions")
        right_label.setStyleSheet(self.theme.get_drag_drop_label_style())
        right_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent focus border
        right_column.addWidget(right_label)
        
        # Ignored regions list (smaller)
        self.ignored_list = DragDropListWidget(self.theme)
        self.ignored_list.setObjectName("drag_drop_list")
        self.ignored_list.setAcceptDrops(True)
        self.ignored_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.ignored_list.setMinimumHeight(120)  # Much smaller height
        self.ignored_list.setMaximumHeight(120)  # Prevent expansion
        self.ignored_list.setMinimumWidth(180)  # Same width as available list
        self.ignored_list.setIconSize(QSize(20, 15))  # Set icon size for flags
        ignored_style = self.theme.get_drag_drop_ignored_list_style()
        self.ignored_list.setStyleSheet(ignored_style)
        self.ignored_list.set_original_style(ignored_style)
        right_column.addWidget(self.ignored_list)
        
        # Remove duplicates checkbox below ignored regions
        self.remove_duplicates_cb = QCheckBox("Remove Duplicate Games")
        self.remove_duplicates_cb.setChecked(False)  # Unchecked by default
        self.remove_duplicates_cb.toggled.connect(self.save_and_emit_changes) # Connect to save method
        right_column.addWidget(self.remove_duplicates_cb)
        
        # Add stretch to fill remaining space
        right_column.addStretch()
        
        main_content.addLayout(right_column)
        
        layout.addLayout(main_content)

    def load_region_settings(self, emit_signal=True):
        """Load region priority and ignored regions from settings for the current system."""
        if self.settings_manager and self.current_system_id is not None:
            priority = self.settings_manager.get_region_priority()
            ignored = self.get_ignored_regions()
            remove_duplicates = self.should_remove_duplicates()
            
            self.available_list.clear()
            self.ignored_list.clear()
            
            # Populate available list (priority order)
            for region in priority:
                if region in self.all_known_regions:
                    item = QListWidgetItem(self.get_flag_icon(region), region)
                    self.available_list.addItem(item)
            
            # Populate ignored list
            for region in ignored:
                if region in self.all_known_regions:
                    item = QListWidgetItem(self.get_flag_icon(region), region)
                    self.ignored_list.addItem(item)
            
            # Add any remaining known regions to available if not in priority or ignored
            current_listed_regions = set(priority + ignored)
            for region in self.all_known_regions:
                if region not in current_listed_regions:
                    item = QListWidgetItem(self.get_flag_icon(region), region)
                    self.available_list.addItem(item) # Add to end of available by default

            self.remove_duplicates_cb.setChecked(remove_duplicates)
        else:
            # Default: use global region priority order if no system-specific settings
            self.available_list.clear()
            self.ignored_list.clear()
            
            if self.settings_manager:
                # Use global region priority as default order
                global_priority = self.settings_manager.get('region_priority', [])
                
                # Add regions in priority order first
                for region in global_priority:
                    if region in self.all_known_regions:
                        item = QListWidgetItem(self.get_flag_icon(region), region)
                        self.available_list.addItem(item)
                
                # Add any remaining regions not in priority list
                priority_set = set(global_priority)
                for region in self.all_known_regions:
                    if region not in priority_set:
                        item = QListWidgetItem(self.get_flag_icon(region), region)
                        self.available_list.addItem(item)
            else:
                # Fallback: add all known regions in their natural order
                for region in self.all_known_regions:
                    item = QListWidgetItem(self.get_flag_icon(region), region)
                    self.available_list.addItem(item)
                    
            self.remove_duplicates_cb.setChecked(False)

    def save_region_settings(self):
        """Save the current region filter configuration to settings."""
        if self.settings_manager and self.current_system_id is not None:
            priority = self.available_list.get_items()
            ignored = self.ignored_list.get_items()
            remove_duplicates = self.remove_duplicates_cb.isChecked()
            
            self.settings_manager.set_region_priority(priority)
            # Note: ignored regions and remove_duplicates are UI state, not persisted settings

    def save_and_emit_changes(self):
        """Save settings and emit the filters_changed signal."""
        self.save_region_settings()
        self.filters_changed.emit()

    def move_to_ignore(self):
        """Move selected items from available to ignored list."""
        selected_items = self.available_list.selectedItems()
        for item in selected_items:
            region_text = item.text()
            # Remove from available list without emitting signal
            for i in range(self.available_list.count()):
                list_item = self.available_list.item(i)
                if list_item and list_item.text() == region_text:
                    self.available_list.takeItem(i)
                    break
            # Add to ignored list with icon
            new_item = QListWidgetItem(self.get_flag_icon(region_text), region_text)
            self.ignored_list.addItem(new_item)
        self.save_and_emit_changes()

    def move_to_available(self):
        """Move selected items from ignored to available list."""
        selected_items = self.ignored_list.selectedItems()
        for item in selected_items:
            region_text = item.text()
            # Remove from ignored list without emitting signal
            for i in range(self.ignored_list.count()):
                list_item = self.ignored_list.item(i)
                if list_item and list_item.text() == region_text:
                    self.ignored_list.takeItem(i)
                    break
            # Add to available list with icon
            new_item = QListWidgetItem(self.get_flag_icon(region_text), region_text)
            self.available_list.addItem(new_item)
        self.save_and_emit_changes()

    def handle_drop_on_available(self, text: str, position: int):
        """Handle item dropped onto the available list from ignored list."""
        # Ensure it's removed from ignored list if it was there
        self.ignored_list.remove_item(text)
        # Add to available list at the specified position with icon
        item = QListWidgetItem(self.get_flag_icon(text), text)
        self.available_list.insertItem(position, item)
        self.save_and_emit_changes()

    def handle_drop_on_ignored(self, text: str, position: int):
        """Handle item dropped onto the ignored list from available list."""
        # Ensure it's removed from available list if it was there
        self.available_list.remove_item(text)
        # Add to ignored list at the specified position with icon
        item = QListWidgetItem(self.get_flag_icon(text), text)
        self.ignored_list.insertItem(position, item)
        self.save_and_emit_changes()

    def update_system(self, system_id: int):
        """Update the filter for a new system ID."""
        self.current_system_id = system_id
        self.load_region_settings(emit_signal=False)
        # Don't emit filters_changed here - on_system_changed will call apply_filters
        
        # Disconnect existing signals to prevent duplicates
        try:
            self.available_list.items_reordered.disconnect(self.save_and_emit_changes)
            self.ignored_list.items_reordered.disconnect(self.save_and_emit_changes)
            self.available_list.item_dropped_from_external.disconnect(self._handle_drop_to_available)
            self.ignored_list.item_dropped_from_external.disconnect(self._handle_drop_to_ignored)
            # Disconnect button signals
            self.ignore_button.clicked.disconnect(self.move_to_ignore)
            self.restore_button.clicked.disconnect(self.move_to_available)
        except TypeError:
            # Signals weren't connected yet, which is fine
            pass
        
        # Connect signals - but don't emit during system change
        self.available_list.items_reordered.connect(self.save_and_emit_changes)
        self.ignored_list.items_reordered.connect(self.save_and_emit_changes)
        
        # Connect drag-drop signals for cross-list transfers
        self.available_list.item_dropped_from_external.connect(self._handle_drop_to_available)
        self.ignored_list.item_dropped_from_external.connect(self._handle_drop_to_ignored)
        
        # Reconnect button signals
        self.ignore_button.clicked.connect(self.move_to_ignore)
        self.restore_button.clicked.connect(self.move_to_available)
        
    def set_available_regions(self, regions: List[str]):
        """Set the available regions list with priority sorting from settings."""
        self.available_list.clear()
        self.ignored_list.clear()  # Clear ignored regions to prevent cross-system contamination
        
        # Get region priority from settings or use default
        if self.settings_manager:
            priority_order = self.settings_manager.get('region_priority', [])
        else:
            priority_order = ["USA", "Japan", "Europe", "World", "UK"]
        
        # Sort regions by priority, then alphabetically for unlisted regions
        def sort_key(region):
            try:
                return (0, priority_order.index(region))
            except ValueError:
                return (1, region)  # Unlisted regions go after priority ones, sorted alphabetically
        
        sorted_regions = sorted(regions, key=sort_key)
        
        for region in sorted_regions:
            icon = self.get_flag_icon(region)
            self.available_list.addItem(region)
            item = self.available_list.item(self.available_list.count() - 1)
            item.setIcon(icon)
            
    def get_region_priority(self) -> List[str]:
        """Get regions in priority order (available list order)."""
        regions = []
        for i in range(self.available_list.count()):
            item_text = self.available_list.item(i).text()
            # Extract region name (remove flag emoji)
            region = item_text.split(' ', 1)[1] if ' ' in item_text else item_text
            regions.append(region)
        return regions
        
    def get_ignored_regions(self) -> List[str]:
        """Get list of ignored regions."""
        regions = []
        for i in range(self.ignored_list.count()):
            item_text = self.ignored_list.item(i).text()
            # Extract region name (remove flag emoji)
            region = item_text.split(' ', 1)[1] if ' ' in item_text else item_text
            regions.append(region)
        return regions
        
    def should_remove_duplicates(self) -> bool:
        """Check if duplicates should be removed."""
        return self.remove_duplicates_cb.isChecked()
    
    def set_region_priority(self, priority_list: List[str]):
        """Set the region priority order (available regions)."""
        # Clear current available list
        self.available_list.clear()
        
        # Add regions in the specified order
        for region in priority_list:
            icon = self.get_flag_icon(region)
            self.available_list.addItem(region)
            new_item = self.available_list.item(self.available_list.count() - 1)
            new_item.setIcon(icon)
    
    def set_ignored_regions(self, ignored_list: List[str]):
        """Set the ignored regions list."""
        # Clear current ignored list
        self.ignored_list.clear()
        
        # Add ignored regions
        for region in ignored_list:
            icon = self.get_flag_icon(region)
            self.ignored_list.addItem(region)
            new_item = self.ignored_list.item(self.ignored_list.count() - 1)
            new_item.setIcon(icon)
    
    def set_remove_duplicates(self, remove_duplicates: bool):
        """Set the remove duplicates checkbox state."""
        self.remove_duplicates_cb.setChecked(remove_duplicates)

    def reset_preferred_regions(self):
        """Reset preferred regions to all available regions, maintaining their current order in available_list."""
        # This method assumes available_list is already populated by set_available_regions
        # No direct action needed here if set_available_regions correctly populates the list
        # and it's intended to be the default preferred order.
        # If a different default order is needed, it should be implemented here.
        # For now, we'll assume set_available_regions handles the default state correctly.
        # If the available_list itself needs to be repopulated from a master list of all possible regions:
        # self.set_available_regions(self.master_region_list_if_any) # Requires master_region_list
        if emit_signal:
            self.filters_changed.emit() # Emit signal as the state might be considered 'reset'

    def set_preferred_to_available(self):
        """Sets the preferred regions list to match the current available_list content and order."""
        # This is effectively what set_available_regions does if it's called with all unique regions from DAT.
        # If available_list is already the source of truth for preferred order, no specific action here
        # beyond ensuring it's correctly populated by update_filter_options -> set_available_regions.
        # This method is a placeholder for clarity in main_window.py logic.
        # Actual repopulation of preferred (available_list) happens in set_available_regions.
        self.filters_changed.emit()

    def reset_ignored_regions(self):
        """Clear all regions from the ignored list."""
        self.ignored_list.clear()
        self.filters_changed.emit()
    
    def rebuild_available_list(self, all_regions_from_dat: List[str]):
        """Rebuild the available regions list, preserving existing order and adding new DAT regions."""
        # Get the set of currently displayed available regions (maintaining their order is implicit
        # as we only append new ones)
        existing_available_texts = set()
        for i in range(self.available_list.count()):
            existing_available_texts.add(self.available_list.item(i).text())

        # Get the set of ignored regions from the UI list
        ignored_texts = set()
        for i in range(self.ignored_list.count()):
            ignored_texts.add(self.ignored_list.item(i).text())

        # Determine new regions from the DAT that are not already in available or ignored lists
        new_regions_to_add = []
        all_regions_from_dat_set = set(all_regions_from_dat)

        for region in all_regions_from_dat_set:
            if region not in existing_available_texts and region not in ignored_texts:
                new_regions_to_add.append(region)
        
        # Sort new regions according to priority order: top priority regions first, then others alphabetically
        priority_order = ["USA", "Japan", "Europe", "World", "UK"]
        
        # Separate new regions into priority and non-priority groups
        priority_regions = []
        other_regions = []
        
        for region in new_regions_to_add:
            if region in priority_order:
                priority_regions.append(region)
            else:
                other_regions.append(region)
        
        # Sort priority regions by their position in priority_order
        priority_regions.sort(key=lambda x: priority_order.index(x) if x in priority_order else len(priority_order))
        
        # Sort other regions alphabetically
        other_regions.sort()
        
        # Add regions in correct order: priority regions first, then alphabetical
        for region in priority_regions + other_regions:
            icon = self.get_flag_icon(region)
            self.available_list.addItem(region)
            new_item = self.available_list.item(self.available_list.count() - 1)
            new_item.setIcon(icon)
        
        # Ensure all items in available_list have icons (might be redundant if set_region_priority handles it)
        # This also helps if items were moved from ignored_list without icons being set immediately.
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if not item.icon(): # Add icon if missing
                icon = self.get_flag_icon(item.text())
                item.setIcon(icon)
        
    def move_to_ignore(self):
        """Move selected items from available to ignored list."""
        selected_items = self.available_list.selectedItems()
        for item in selected_items:
            region = item.text()
            icon = self.get_flag_icon(region)
            self.ignored_list.addItem(region)
            new_item = self.ignored_list.item(self.ignored_list.count() - 1)
            new_item.setIcon(icon)
            self.available_list.takeItem(self.available_list.row(item))
        self.save_and_emit_changes()
    
    def move_to_available(self):
        """Move selected items from ignored to available list."""
        selected_items = self.ignored_list.selectedItems()
        for item in selected_items:
            region = item.text()
            icon = self.get_flag_icon(region)
            self.available_list.addItem(region)
            new_item = self.available_list.item(self.available_list.count() - 1)
            new_item.setIcon(icon)
            self.ignored_list.takeItem(self.ignored_list.row(item))
        self.save_and_emit_changes()
    
    def _handle_drop_to_available(self, item_text: str, position: int = -1):
        """Handle dropping an item to the available list."""
        # Remove from ignored list if it exists there
        for i in range(self.ignored_list.count()):
            if self.ignored_list.item(i).text() == item_text:
                self.ignored_list.takeItem(i)
                break
        
        # Add to available list with flag icon at specific position
        icon = self.get_flag_icon(item_text)
        if position >= 0 and position <= self.available_list.count():
            self.available_list.insertItem(position, item_text)
            new_item = self.available_list.item(position)
        else:
            self.available_list.addItem(item_text)
            new_item = self.available_list.item(self.available_list.count() - 1)
        new_item.setIcon(icon)
        self.save_and_emit_changes()
    
    def get_available_regions_list(self) -> List[str]:
        """Returns the current list of items in the available regions list."""
        return [self.available_list.item(i).text() for i in range(self.available_list.count())]

    def _handle_drop_to_ignored(self, item_text: str, position: int = -1):
        """Handle dropping an item to the ignored list."""
        # Remove from available list if it exists there
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item.text() == item_text:
                self.available_list.takeItem(i)
                break
        
        # Add to ignored list with flag icon at specific position
        icon = self.get_flag_icon(item_text)
        if position >= 0 and position <= self.ignored_list.count():
            self.ignored_list.insertItem(position, item_text)
            new_item = self.ignored_list.item(position)
        else:
            self.ignored_list.addItem(item_text)
            new_item = self.ignored_list.item(self.ignored_list.count() - 1)
        new_item.setIcon(icon)
        self.save_and_emit_changes()