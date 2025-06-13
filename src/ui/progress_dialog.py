#!/usr/bin/env python3
"""
Progress Dialog for Romplestiltskin

Provides a progress dialog for long-running operations.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class ProgressDialog(QDialog):
    """Progress dialog for long-running operations."""
    
    def __init__(self, title: str = "Progress", parent=None):
        super().__init__(parent)
        
        self.cancelled = False
        self.setup_ui(title)
    
    def setup_ui(self, title: str):
        """Set up the user interface."""
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Details label
        self.details_label = QLabel("")
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.details_label)
        
        # Log text (initially hidden)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setVisible(False)
        layout.addWidget(self.log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.show_log_button = QPushButton("Show Log")
        self.show_log_button.clicked.connect(self.toggle_log)
        button_layout.addWidget(self.show_log_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_operation)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def set_status(self, status: str):
        """Set the status message."""
        self.status_label.setText(status)
    
    def set_progress(self, current: int, total: int = 100):
        """Set the progress value."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.details_label.setText(f"{current} / {total}")
        else:
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.details_label.setText("")
    
    def set_indeterminate(self, indeterminate: bool = True):
        """Set progress bar to indeterminate mode."""
        if indeterminate:
            self.progress_bar.setRange(0, 0)
            self.details_label.setText("")
        else:
            self.progress_bar.setRange(0, 100)
    
    def add_log_message(self, message: str):
        """Add a message to the log."""
        self.log_text.append(message)
    
    def toggle_log(self):
        """Toggle log visibility."""
        if self.log_text.isVisible():
            self.log_text.setVisible(False)
            self.show_log_button.setText("Show Log")
            self.resize(400, 200)
        else:
            self.log_text.setVisible(True)
            self.show_log_button.setText("Hide Log")
            self.resize(400, 300)
    
    def cancel_operation(self):
        """Cancel the current operation."""
        self.cancelled = True
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
        self.set_status("Cancelling operation...")
    
    def is_cancelled(self) -> bool:
        """Check if the operation was cancelled."""
        return self.cancelled
    
    def operation_completed(self, success: bool = True):
        """Mark operation as completed."""
        if success:
            self.set_status("Operation completed successfully")
            self.progress_bar.setValue(100)
        else:
            self.set_status("Operation failed")
        
        self.cancel_button.setText("Close")
        self.cancel_button.clicked.disconnect()
        self.cancel_button.clicked.connect(self.accept)
        self.cancel_button.setEnabled(True)
    
    def closeEvent(self, event):
        """Handle close event."""
        if not self.cancelled:
            self.cancel_operation()
        event.accept()