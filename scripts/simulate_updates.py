#!/usr/bin/env python3
"""
Simulate stock and price updates for testing.
Useful for demonstrating real-time features.
"""

import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "main" / "python"))

from services.data_collector import simulate_stock_changes

def main():
    """Run stock simulation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🎲 Simulating stock and price changes...")
    simulate_stock_changes()
    print("✅ Simulation completed!")

if __name__ == "__main__":
    main()