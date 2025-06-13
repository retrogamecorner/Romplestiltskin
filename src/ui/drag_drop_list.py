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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
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
            self.setStyleSheet(self.styleSheet() + """
                QListWidget {
                    border: 3px solid #0078d4;
                    background-color: rgba(0, 120, 212, 0.1);
                }
            """)
        else:
            super().dragEnterEvent(event)
    
    def dragLeaveEvent(self, event):
        # Reset styling when drag leaves
        self.drag_indicator_position = -1
        self.update()
        # Remove drag highlight styling
        style = self.styleSheet()
        if "border: 3px solid #0078d4" in style:
            style = style.replace("border: 3px solid #0078d4;", "")
            style = style.replace("background-color: rgba(0, 120, 212, 0.1);", "")
            self.setStyleSheet(style)
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
            style = self.styleSheet()
            if "border: 3px solid #0078d4" in style:
                style = style.replace("border: 3px solid #0078d4;", "")
                style = style.replace("background-color: rgba(0, 120, 212, 0.1);", "")
                self.setStyleSheet(style)
            
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
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Draw drop indicator line
        if self.drag_indicator_position >= 0:
            painter = QPainter(self.viewport())
            painter.setPen(QPen(QColor(0, 120, 212), 3))
            
            if self.drag_indicator_position < self.count():
                rect = self.visualRect(self.model().index(self.drag_indicator_position, 0))
                y = rect.top()
            else:
                if self.count() > 0:
                    rect = self.visualRect(self.model().index(self.count() - 1, 0))
                    y = rect.bottom()
                else:
                    y = 0
            
            painter.drawLine(0, y, self.width(), y)
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
        'USA': 'us.svg',
        'Europe': 'eu.svg', 
        'Japan': 'jp.svg',
        'World': 'un.svg',  # Using UN flag for world
        'Korea': 'kr.svg',
        'China': 'cn.svg',
        'Taiwan': 'tw.svg',
        'Hong Kong': 'hk.svg',
        'Australia': 'au.svg',
        'Brazil': 'br.svg',
        'Canada': 'ca.svg',
        'France': 'fr.svg',
        'Germany': 'de.svg',
        'Italy': 'it.svg',
        'Spain': 'es.svg',
        'UK': 'gb.svg',
        'Netherlands': 'nl.svg',
        'Sweden': 'se.svg',
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
    
    def __init__(self, settings_manager=None, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🌍 Region Priority Filter")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Main content layout with two columns
        main_content = QHBoxLayout()
        
        # Left column for available regions only
        left_column = QVBoxLayout()
        
        # Available regions label
        left_label = QLabel("Available Regions")
        left_label.setStyleSheet("font-weight: bold;")
        left_column.addWidget(left_label)
        
        # Available regions list
        self.available_list = DragDropListWidget()
        self.available_list.setAcceptDrops(True)
        self.available_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.available_list.setMinimumHeight(150)  # Reduce height to fit interface
        self.available_list.setMaximumHeight(200)  # Set maximum height to prevent overflow
        self.available_list.setMinimumWidth(180)  # Increase width for icons
        self.available_list.setIconSize(QSize(20, 15))  # Set icon size for flags
        self.available_list.setStyleSheet("""
            QListWidget { 
                background-color: #3A3A3A; 
                padding: 5px;
                border: 2px solid #555;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
                background-color: #4A4A4A;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                border: 2px solid #106ebe;
            }
            QListWidget::item:hover {
                background-color: #5A5A5A;
            }
        """)
        left_column.addWidget(self.available_list)
        
        # Add stretch to fill remaining space
        left_column.addStretch()
        
        main_content.addLayout(left_column)
        
        # Transfer buttons (middle column)
        buttons_layout = QVBoxLayout()
        buttons_layout.addStretch()
        
        self.ignore_button = QPushButton("→")
        self.ignore_button.setToolTip("Move to ignore list")
        self.ignore_button.setMaximumWidth(30)
        self.ignore_button.setStyleSheet("QPushButton { color: black; font-weight: bold; font-size: 14px; }")
        self.ignore_button.clicked.connect(self.move_to_ignore)
        buttons_layout.addWidget(self.ignore_button)
        
        self.restore_button = QPushButton("←")
        self.restore_button.setToolTip("Restore from ignore list")
        self.restore_button.setMaximumWidth(30)
        self.restore_button.setStyleSheet("QPushButton { color: black; font-weight: bold; font-size: 14px; }")
        self.restore_button.clicked.connect(self.move_to_available)
        buttons_layout.addWidget(self.restore_button)
        
        buttons_layout.addStretch()
        main_content.addLayout(buttons_layout)
        
        # Right column for ignored regions and controls
        right_column = QVBoxLayout()
        
        # Ignored regions label
        right_label = QLabel("Ignored Regions")
        right_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        right_column.addWidget(right_label)
        
        # Ignored regions list (smaller)
        self.ignored_list = DragDropListWidget()
        self.ignored_list.setAcceptDrops(True)
        self.ignored_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.ignored_list.setMinimumHeight(120)  # Much smaller height
        self.ignored_list.setMaximumHeight(120)  # Prevent expansion
        self.ignored_list.setMinimumWidth(180)  # Same width as available list
        self.ignored_list.setIconSize(QSize(20, 15))  # Set icon size for flags
        self.ignored_list.setStyleSheet("""
            QListWidget { 
                background-color: #8B0000; 
                color: white;
                padding: 5px;
                border: 2px solid #AA0000;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
                background-color: #AA0000;
            }
            QListWidget::item:selected {
                background-color: #CC0000;
                border: 2px solid #FF0000;
            }
            QListWidget::item:hover {
                background-color: #BB0000;
            }
        """)
        right_column.addWidget(self.ignored_list)
        
        # Remove duplicates checkbox below ignored regions
        self.remove_duplicates_cb = QCheckBox("Remove Duplicate Games")
        self.remove_duplicates_cb.setChecked(False)  # Unchecked by default
        self.remove_duplicates_cb.toggled.connect(self.filters_changed)
        right_column.addWidget(self.remove_duplicates_cb)
        
        # Add stretch to fill remaining space
        right_column.addStretch()
        
        main_content.addLayout(right_column)
        
        layout.addLayout(main_content)
        
        # Connect signals
        self.available_list.items_reordered.connect(self.filters_changed.emit)
        self.ignored_list.items_reordered.connect(self.filters_changed.emit)
        
        # Connect drag-drop signals for cross-list transfers
        self.available_list.item_dropped_from_external.connect(self._handle_drop_to_available)
        self.ignored_list.item_dropped_from_external.connect(self._handle_drop_to_ignored)
        
    def set_available_regions(self, regions: List[str]):
        """Set the available regions list with priority sorting from settings."""
        self.available_list.clear()
        
        # Get region priority from settings or use default
        if self.settings_manager:
            priority_order = self.settings_manager.get('region_priority', [])
        else:
            priority_order = ["USA", "Japan", "Europe", "World"]
        
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
        self.filters_changed.emit()
    
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
        self.filters_changed.emit()
    
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
        self.filters_changed.emit()
    
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
        self.filters_changed.emit()