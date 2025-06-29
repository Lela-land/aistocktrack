"""
Data collection service for scraping product information from retailers.
Handles Pop Mart and Pokémon card data collection with rate limiting and error handling.
"""

import requests
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict
import random

from ..models.product import Product, BrandType, StockStatus
from ..core.database import DatabaseManager


class DataCollector:
    """Base class for data collection from retail websites."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'aistocktrack/1.0 (Educational Project)'
        })
        self.rate_limit_delay = 2.0  # Seconds between requests
        self.logger = logging.getLogger(__name__)
    
    def collect_data(self) -> List[Product]:
        """Override in subclasses to implement specific collection logic."""
        raise NotImplementedError
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        time.sleep(self.rate_limit_delay + random.uniform(0, 1))
    
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with error handling and rate limiting."""
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
    
    def update_database(self, products: List[Product]):
        """Update database with collected products."""
        for product in products:
            try:
                # Check if product exists and update price history
                existing = self.db.get_product_by_id(product.id)
                if existing and existing.price != product.price:
                    # Record price change
                    from ..models.product import PriceHistory
                    price_history = PriceHistory(
                        product_id=product.id,
                        price=product.price,
                        source=product.source
                    )
                    self.db.save_price_history(price_history)
                
                # Save/update product
                self.db.save_product(product)
                self.logger.info(f"Updated product: {product.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to update product {product.id}: {e}")


class PopMartCollector(DataCollector):
    """Data collector for Pop Mart products."""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.brand = BrandType.POP_MART
    
    def collect_data(self) -> List[Product]:
        """
        Collect Pop Mart product data.
        In a real implementation, this would scrape the Pop Mart website.
        For now, this simulates data collection with sample updates.
        """
        products = []
        
        # Simulate Pop Mart API or scraping
        sample_products = [
            {
                'id': 'pm_004',
                'name': 'SKULLPANDA City of Night Series',
                'source': 'Pop Mart Official',
                'purchase_link': 'https://www.popmart.com/skullpanda-night',
                'price': 13.99,
                'stock_level': 42,
                'image_url': '/static/images/skullpanda-night.jpg',
                'description': 'Limited edition night theme SKULLPANDA',
                'category': 'blind_box',
                'tags': ['limited', 'night', 'skull']
            },
            {
                'id': 'pm_005',
                'name': 'Molly Space Travel Series',
                'source': 'Pop Mart Official',
                'purchase_link': 'https://www.popmart.com/molly-space',
                'price': 14.50,
                'stock_level': 18,
                'image_url': '/static/images/molly-space.jpg',
                'description': 'Molly exploring the cosmos',
                'category': 'blind_box',
                'tags': ['molly', 'space', 'travel']
            },
            {
                'id': 'pm_006',
                'name': 'DIMOO Underwater Series',
                'source': 'Pop Mart Official',
                'purchase_link': 'https://www.popmart.com/dimoo-underwater',
                'price': 12.99,
                'original_price': 15.99,
                'stock_level': 0,
                'image_url': '/static/images/dimoo-underwater.jpg',
                'description': 'DIMOO diving into ocean adventures',
                'category': 'blind_box',
                'tags': ['dimoo', 'underwater', 'ocean']
            }
        ]
        
        for product_data in sample_products:
            # Determine stock status
            stock_level = product_data['stock_level']
            if stock_level == 0:
                stock_status = StockStatus.OUT_OF_STOCK
            elif stock_level <= 5:
                stock_status = StockStatus.LOW_STOCK
            else:
                stock_status = StockStatus.IN_STOCK
            
            product = Product(
                id=product_data['id'],
                name=product_data['name'],
                brand=self.brand,
                source=product_data['source'],
                purchase_link=product_data['purchase_link'],
                price=product_data['price'],
                original_price=product_data.get('original_price'),
                stock_level=stock_level,
                stock_status=stock_status,
                image_url=product_data['image_url'],
                description=product_data['description'],
                category=product_data['category'],
                tags=product_data['tags'],
                last_updated=datetime.now()
            )
            products.append(product)
        
        self.logger.info(f"Collected {len(products)} Pop Mart products")
        return products
    
    def _scrape_product_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual product page.
        In a real implementation, this would parse HTML/JSON responses.
        """
        response = self._make_request(url)
        if not response:
            return None
        
        # Simulated parsing logic
        # In reality, you'd use BeautifulSoup or similar
        return {
            'name': 'Sample Product',
            'price': 12.99,
            'stock_level': 10,
            'image_url': '/static/images/sample.jpg'
        }


class PokemonCollector(DataCollector):
    """Data collector for Pokémon card products."""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.brand = BrandType.POKEMON
    
    def collect_data(self) -> List[Product]:
        """
        Collect Pokémon card product data.
        Simulates data collection from multiple sources.
        """
        products = []
        
        # Simulate multiple retailer data
        sample_products = [
            {
                'id': 'pk_004',
                'name': 'Pokémon TCG Paldea Evolved Booster Box',
                'source': 'TCG Player',
                'purchase_link': 'https://www.tcgplayer.com/paldea-evolved-box',
                'price': 144.99,
                'original_price': 159.99,
                'stock_level': 12,
                'image_url': '/static/images/paldea-evolved-box.jpg',
                'description': '36 booster packs of Paldea Evolved',
                'category': 'box',
                'tags': ['paldea', 'evolved', 'booster', 'box']
            },
            {
                'id': 'pk_005',
                'name': 'Pikachu VMAX Premium Collection',
                'source': 'Pokémon Center',
                'purchase_link': 'https://www.pokemoncenter.com/pikachu-vmax',
                'price': 49.99,
                'stock_level': 3,
                'image_url': '/static/images/pikachu-vmax.jpg',
                'description': 'Special collection featuring Pikachu VMAX',
                'category': 'tin',
                'tags': ['pikachu', 'vmax', 'premium']
            },
            {
                'id': 'pk_006',
                'name': 'Scarlet & Violet Elite Trainer Box',
                'source': 'Amazon',
                'purchase_link': 'https://amazon.com/sv-elite-trainer',
                'price': 39.99,
                'stock_level': 28,
                'image_url': '/static/images/sv-elite-trainer.jpg',
                'description': 'Complete training package with accessories',
                'category': 'box',
                'tags': ['scarlet', 'violet', 'elite', 'trainer']
            }
        ]
        
        for product_data in sample_products:
            # Determine stock status
            stock_level = product_data['stock_level']
            if stock_level == 0:
                stock_status = StockStatus.OUT_OF_STOCK
            elif stock_level <= 5:
                stock_status = StockStatus.LOW_STOCK
            else:
                stock_status = StockStatus.IN_STOCK
            
            product = Product(
                id=product_data['id'],
                name=product_data['name'],
                brand=self.brand,
                source=product_data['source'],
                purchase_link=product_data['purchase_link'],
                price=product_data['price'],
                original_price=product_data.get('original_price'),
                stock_level=stock_level,
                stock_status=stock_status,
                image_url=product_data['image_url'],
                description=product_data['description'],
                category=product_data['category'],
                tags=product_data['tags'],
                last_updated=datetime.now()
            )
            products.append(product)
        
        self.logger.info(f"Collected {len(products)} Pokémon products")
        return products


class DataCollectionManager:
    """Manages data collection from all sources."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.collectors = [
            PopMartCollector(db_manager),
            PokemonCollector(db_manager)
        ]
        self.logger = logging.getLogger(__name__)
    
    def run_collection(self) -> Dict[str, Any]:
        """Run data collection from all sources."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'collections': {},
            'total_products': 0,
            'errors': []
        }
        
        for collector in self.collectors:
            try:
                self.logger.info(f"Starting collection for {collector.brand.value}")
                products = collector.collect_data()
                collector.update_database(products)
                
                results['collections'][collector.brand.value] = {
                    'success': True,
                    'products_collected': len(products),
                    'timestamp': datetime.now().isoformat()
                }
                results['total_products'] += len(products)
                
            except Exception as e:
                error_msg = f"Collection failed for {collector.brand.value}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
                results['collections'][collector.brand.value] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        self.logger.info(f"Collection completed. Total products: {results['total_products']}")
        return results
    
    def run_scheduled_collection(self):
        """Run collection suitable for scheduled tasks."""
        try:
            results = self.run_collection()
            
            # Log summary
            if results['errors']:
                self.logger.warning(f"Collection completed with {len(results['errors'])} errors")
            else:
                self.logger.info("Collection completed successfully")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Scheduled collection failed: {e}")
            return {'success': False, 'error': str(e)}


# Utility functions for manual data collection
def collect_all_data(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Manually trigger data collection."""
    db_manager = DatabaseManager(db_path)
    collection_manager = DataCollectionManager(db_manager)
    return collection_manager.run_collection()


def simulate_stock_changes(db_path: Optional[str] = None):
    """Simulate stock level and price changes for testing."""
    db_manager = DatabaseManager(db_path)
    products = db_manager.get_products()
    
    for product in products[:3]:  # Update first 3 products
        # Simulate stock change
        old_stock = product.stock_level
        product.stock_level = max(0, old_stock + random.randint(-5, 10))
        
        # Simulate price change (small fluctuation)
        price_change = random.uniform(-2.0, 2.0)
        new_price = max(0.99, product.price + price_change)
        
        if new_price != product.price:
            # Record price history
            from ..models.product import PriceHistory
            price_history = PriceHistory(
                product_id=product.id,
                price=new_price,
                source="Simulated Update"
            )
            db_manager.save_price_history(price_history)
            product.price = new_price
        
        # Update stock status
        if product.stock_level == 0:
            product.stock_status = StockStatus.OUT_OF_STOCK
        elif product.stock_level <= 5:
            product.stock_status = StockStatus.LOW_STOCK
        else:
            product.stock_status = StockStatus.IN_STOCK
        
        product.last_updated = datetime.now()
        db_manager.update_product(product)
    
    logging.info("Stock simulation completed")


if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    results = collect_all_data()
    print(f"Collection results: {results}")