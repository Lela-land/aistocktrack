#!/usr/bin/env python3
"""
Data collection script for aistocktrack.
Can be run manually or scheduled via cron.
"""

import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "main" / "python"))

from services.data_collector import DataCollectionManager
from core.database import DatabaseManager

def main():
    """Run data collection."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🔄 Starting data collection...")
    
    # Initialize database and collector
    db_manager = DatabaseManager()
    collector = DataCollectionManager(db_manager)
    
    # Run collection
    results = collector.run_collection()
    
    # Print results
    print(f"✅ Collection completed!")
    print(f"📊 Total products collected: {results['total_products']}")
    
    for brand, data in results['collections'].items():
        if data['success']:
            print(f"  {brand}: {data['products_collected']} products")
        else:
            print(f"  {brand}: FAILED - {data['error']}")
    
    if results['errors']:
        print(f"⚠️  {len(results['errors'])} errors occurred:")
        for error in results['errors']:
            print(f"    {error}")
    
    db_manager.close()

if __name__ == "__main__":
    main()