#!/usr/bin/env python3
"""
Test script to verify color coding functionality in ignored ROMs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.scanned_roms_manager import ScannedROMsManager, ROMStatus
from core.db_manager import DatabaseManager
from pathlib import Path

def test_color_coding():
    """Test the color coding functionality."""
    
    # Initialize database
    db_path = "test_roms.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db_manager = DatabaseManager(db_path)
    scanned_roms_manager = ScannedROMsManager(db_path)
    
    # Create a test system
    system_id = 1
    
    # Test 1: Insert a ROM and move it to ignored with original_status = missing
    print("Test 1: Testing missing -> ignored color coding")
    scanned_roms_manager.insert_missing_rom(system_id, "test_crc_missing", {
        'major_name': 'Test Missing Game',
        'region': 'USA',
        'languages': 'En'
    })
    
    # Move to ignored with original status missing
    scanned_roms_manager.update_rom_status(
        system_id, 
        ROMStatus.IGNORED, 
        crc32="test_crc_missing",
        original_status=ROMStatus.MISSING
    )
    
    # Check the result
    rom_data = scanned_roms_manager.get_rom_by_crc32(system_id, "test_crc_missing")
    print(f"ROM data: {rom_data}")
    print(f"Original status: {rom_data.get('original_status')}")
    
    # Test 2: Insert a ROM and move it to ignored with original_status = not_recognized
    print("\nTest 2: Testing not_recognized -> ignored color coding")
    
    # First insert as a scanned ROM
    scanned_roms_manager.insert_scanned_rom(
        system_id=system_id,
        file_path="/test/path/unrecognized_rom.zip",
        file_size=1024,
        calculated_crc32="test_crc_unrecognized",
        status=ROMStatus.NOT_RECOGNIZED
    )
    
    # Move to ignored with original status not_recognized
    scanned_roms_manager.update_rom_status(
        system_id,
        ROMStatus.IGNORED,
        crc32="test_crc_unrecognized",
        original_status=ROMStatus.NOT_RECOGNIZED
    )
    
    # Check the result
    rom_data = scanned_roms_manager.get_rom_by_crc32(system_id, "test_crc_unrecognized")
    print(f"ROM data: {rom_data}")
    print(f"Original status: {rom_data.get('original_status')}")
    
    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_color_coding()