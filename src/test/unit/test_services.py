"""
Unit tests for service layer.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.main.python.services.product_service import ProductService
from src.main.python.models.product import Product, BrandType, StockStatus
from src.main.python.core.database import DatabaseManager


class TestProductService(unittest.TestCase):
    """Test ProductService functionality."""
    
    def setUp(self):
        """Set up test data and mocks."""
        self.mock_db = Mock(spec=DatabaseManager)
        self.service = ProductService(self.mock_db)
        
        # Sample product for testing
        self.sample_product = Product(
            id="test_001",
            name="Test Product",
            brand=BrandType.POP_MART,
            source="Test Store",
            purchase_link="https://example.com/test",
            price=12.99,
            stock_level=10,
            stock_status=StockStatus.IN_STOCK,
            image_url="/test/image.jpg"
        )
    
    def test_get_product_by_id(self):
        """Test getting product by ID."""
        # Mock database response
        self.mock_db.get_product_by_id.return_value = self.sample_product
        
        # Call service method
        result = self.service.get_product_by_id("test_001")
        
        # Verify
        self.assertEqual(result, self.sample_product)
        self.mock_db.get_product_by_id.assert_called_once_with("test_001")
    
    def test_get_products_by_brand(self):
        """Test getting products filtered by brand."""
        # Mock database response
        self.mock_db.get_products.return_value = [self.sample_product]
        
        # Call service method
        result = self.service.get_products_by_brand(BrandType.POP_MART, limit=10)
        
        # Verify
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.sample_product)
        self.mock_db.get_products.assert_called_once_with(brand=BrandType.POP_MART, limit=10)
    
    def test_search_products(self):
        """Test product search functionality."""
        # Mock database response
        self.mock_db.search_products.return_value = [self.sample_product]
        
        # Call service method
        result = self.service.search_products(
            brand=BrandType.POP_MART,
            search_term="test",
            sort_by="name",
            page=1,
            per_page=20
        )
        
        # Verify
        self.assertEqual(len(result), 1)
        self.mock_db.search_products.assert_called_once_with(
            brand=BrandType.POP_MART,
            category=None,
            search_term="test",
            sort_by="name",
            page=1,
            per_page=20
        )
    
    def test_get_featured_products(self):
        """Test featured products selection."""
        # Create products with different stock levels
        products = [
            Product(
                id=f"test_{i:03d}",
                name=f"Test Product {i}",
                brand=BrandType.POP_MART,
                source="Test Store",
                purchase_link="https://example.com/test",
                price=12.99,
                stock_level=15 if i % 2 == 0 else 3,  # Alternate high/low stock
                stock_status=StockStatus.IN_STOCK,
                image_url="/test/image.jpg"
            )
            for i in range(1, 11)
        ]
        
        self.mock_db.get_products.return_value = products
        
        # Call service method
        result = self.service.get_featured_products(BrandType.POP_MART, limit=4)
        
        # Verify
        self.assertLessEqual(len(result), 4)
        # Featured products should prioritize high stock levels
        high_stock_products = [p for p in result if p.stock_level > 10]
        self.assertGreater(len(high_stock_products), 0)
    
    def test_update_product_stock(self):
        """Test stock level updates."""
        # Mock existing product
        self.mock_db.get_product_by_id.return_value = self.sample_product
        
        # Call service method
        result = self.service.update_product_stock("test_001", 5)
        
        # Verify
        self.assertIsNotNone(result)
        self.assertEqual(result.stock_level, 5)
        self.assertEqual(result.stock_status, StockStatus.LOW_STOCK)
        self.mock_db.update_product.assert_called_once()
    
    def test_update_product_price(self):
        """Test price updates with history tracking."""
        # Mock existing product
        self.mock_db.get_product_by_id.return_value = self.sample_product
        
        # Call service method with new price
        result = self.service.update_product_price("test_001", 14.99, "Test Update")
        
        # Verify
        self.assertIsNotNone(result)
        self.assertEqual(result.price, 14.99)
        self.mock_db.update_product.assert_called_once()
        # Should have saved price history since price changed
        self.mock_db.save_price_history.assert_called_once()
    
    def test_get_statistics(self):
        """Test statistics generation."""
        # Mock products with different statuses
        products = [
            Product(
                id="test_001",
                name="In Stock Product",
                brand=BrandType.POP_MART,
                source="Test Store",
                purchase_link="https://example.com/test",
                price=12.99,
                stock_level=10,
                stock_status=StockStatus.IN_STOCK,
                image_url="/test/image.jpg",
                category="test_cat"
            ),
            Product(
                id="test_002",
                name="Low Stock Product",
                brand=BrandType.POP_MART,
                source="Test Store",
                purchase_link="https://example.com/test",
                price=15.99,
                stock_level=2,
                stock_status=StockStatus.LOW_STOCK,
                image_url="/test/image.jpg",
                category="test_cat"
            ),
            Product(
                id="test_003",
                name="Out of Stock Product",
                brand=BrandType.POP_MART,
                source="Test Store",
                purchase_link="https://example.com/test",
                price=18.99,
                stock_level=0,
                stock_status=StockStatus.OUT_OF_STOCK,
                image_url="/test/image.jpg",
                category="other_cat"
            )
        ]
        
        self.mock_db.get_products.return_value = products
        
        # Call service method
        stats = self.service.get_statistics(BrandType.POP_MART)
        
        # Verify
        self.assertEqual(stats['total_products'], 3)
        self.assertEqual(stats['in_stock'], 1)
        self.assertEqual(stats['low_stock'], 1)
        self.assertEqual(stats['out_of_stock'], 1)
        self.assertEqual(len(stats['categories']), 2)
        self.assertAlmostEqual(stats['average_price'], 15.99, places=2)


class TestDataCollectionManager(unittest.TestCase):
    """Test data collection functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.mock_db = Mock(spec=DatabaseManager)
    
    @patch('src.main.python.services.data_collector.PopMartCollector')
    @patch('src.main.python.services.data_collector.PokemonCollector')
    def test_collection_manager_initialization(self, mock_pokemon, mock_popmart):
        """Test collection manager setup."""
        from src.main.python.services.data_collector import DataCollectionManager
        
        manager = DataCollectionManager(self.mock_db)
        
        # Verify collectors are initialized
        self.assertEqual(len(manager.collectors), 2)
        mock_popmart.assert_called_once_with(self.mock_db)
        mock_pokemon.assert_called_once_with(self.mock_db)


if __name__ == '__main__':
    unittest.main()