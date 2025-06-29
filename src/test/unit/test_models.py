"""
Unit tests for data models.
"""

import unittest
from datetime import datetime
from src.main.python.models.product import Product, BrandType, StockStatus, PriceHistory
from src.main.python.models.brand_config import get_brand_config, ColorScheme, Typography


class TestProduct(unittest.TestCase):
    """Test Product model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.product = Product(
            id="test_001",
            name="Test Product",
            brand=BrandType.POP_MART,
            source="Test Store",
            purchase_link="https://example.com/test",
            price=12.99,
            original_price=15.99,
            stock_level=10,
            stock_status=StockStatus.IN_STOCK,
            image_url="/test/image.jpg",
            description="Test description",
            category="test_category",
            tags=["test", "sample"]
        )
    
    def test_product_creation(self):
        """Test product creation with all fields."""
        self.assertEqual(self.product.id, "test_001")
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.brand, BrandType.POP_MART)
        self.assertEqual(self.product.price, 12.99)
        self.assertEqual(self.product.stock_level, 10)
    
    def test_is_on_sale(self):
        """Test sale detection."""
        self.assertTrue(self.product.is_on_sale)
        
        # Test product not on sale
        product_no_sale = Product(
            id="test_002",
            name="Regular Product",
            brand=BrandType.POP_MART,
            source="Test Store",
            purchase_link="https://example.com/test",
            price=12.99,
            stock_level=10,
            stock_status=StockStatus.IN_STOCK,
            image_url="/test/image.jpg"
        )
        self.assertFalse(product_no_sale.is_on_sale)
    
    def test_discount_percentage(self):
        """Test discount calculation."""
        expected_discount = round(((15.99 - 12.99) / 15.99) * 100, 2)
        self.assertEqual(self.product.discount_percentage, expected_discount)
        
        # Test no discount
        product_no_discount = Product(
            id="test_003",
            name="No Discount Product",
            brand=BrandType.POP_MART,
            source="Test Store",
            purchase_link="https://example.com/test",
            price=12.99,
            stock_level=10,
            stock_status=StockStatus.IN_STOCK,
            image_url="/test/image.jpg"
        )
        self.assertIsNone(product_no_discount.discount_percentage)
    
    def test_availability_text(self):
        """Test availability text generation."""
        self.assertEqual(self.product.availability_text, "10 available")
        
        # Test low stock
        low_stock_product = Product(
            id="test_004",
            name="Low Stock Product",
            brand=BrandType.POP_MART,
            source="Test Store",
            purchase_link="https://example.com/test",
            price=12.99,
            stock_level=3,
            stock_status=StockStatus.LOW_STOCK,
            image_url="/test/image.jpg"
        )
        self.assertEqual(low_stock_product.availability_text, "Only 3 left")
        
        # Test out of stock
        out_of_stock_product = Product(
            id="test_005",
            name="Out of Stock Product",
            brand=BrandType.POP_MART,
            source="Test Store",
            purchase_link="https://example.com/test",
            price=12.99,
            stock_level=0,
            stock_status=StockStatus.OUT_OF_STOCK,
            image_url="/test/image.jpg"
        )
        self.assertEqual(out_of_stock_product.availability_text, "Out of stock")
    
    def test_to_dict(self):
        """Test product serialization to dictionary."""
        product_dict = self.product.to_dict()
        
        self.assertEqual(product_dict['id'], "test_001")
        self.assertEqual(product_dict['name'], "Test Product")
        self.assertEqual(product_dict['brand'], "pop_mart")
        self.assertEqual(product_dict['price'], 12.99)
        self.assertTrue(product_dict['is_on_sale'])
        self.assertIsNotNone(product_dict['discount_percentage'])
    
    def test_from_dict(self):
        """Test product creation from dictionary."""
        product_dict = self.product.to_dict()
        reconstructed_product = Product.from_dict(product_dict)
        
        self.assertEqual(reconstructed_product.id, self.product.id)
        self.assertEqual(reconstructed_product.name, self.product.name)
        self.assertEqual(reconstructed_product.brand, self.product.brand)
        self.assertEqual(reconstructed_product.price, self.product.price)


class TestPriceHistory(unittest.TestCase):
    """Test PriceHistory model."""
    
    def setUp(self):
        """Set up test data."""
        self.price_history = PriceHistory(
            product_id="test_001",
            price=12.99,
            source="Test Store"
        )
    
    def test_price_history_creation(self):
        """Test price history creation."""
        self.assertEqual(self.price_history.product_id, "test_001")
        self.assertEqual(self.price_history.price, 12.99)
        self.assertEqual(self.price_history.source, "Test Store")
        self.assertIsInstance(self.price_history.timestamp, datetime)
    
    def test_to_dict(self):
        """Test price history serialization."""
        history_dict = self.price_history.to_dict()
        
        self.assertEqual(history_dict['product_id'], "test_001")
        self.assertEqual(history_dict['price'], 12.99)
        self.assertEqual(history_dict['source'], "Test Store")
        self.assertIn('timestamp', history_dict)


class TestBrandConfig(unittest.TestCase):
    """Test brand configuration functionality."""
    
    def test_get_pop_mart_config(self):
        """Test Pop Mart configuration retrieval."""
        config = get_brand_config(BrandType.POP_MART)
        
        self.assertEqual(config.brand_type, BrandType.POP_MART)
        self.assertEqual(config.display_name, "Pop Mart Tracker")
        self.assertEqual(config.product_term, "figure")
        self.assertIsInstance(config.colors, ColorScheme)
        self.assertIsInstance(config.typography, Typography)
    
    def test_get_pokemon_config(self):
        """Test Pokémon configuration retrieval."""
        config = get_brand_config(BrandType.POKEMON)
        
        self.assertEqual(config.brand_type, BrandType.POKEMON)
        self.assertEqual(config.display_name, "Pokémon Card Tracker")
        self.assertEqual(config.product_term, "card")
    
    def test_brand_config_to_dict(self):
        """Test brand configuration serialization."""
        config = get_brand_config(BrandType.POP_MART)
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict['brand_type'], "pop_mart")
        self.assertEqual(config_dict['display_name'], "Pop Mart Tracker")
        self.assertIn('colors', config_dict)
        self.assertIn('typography', config_dict)
        self.assertIn('assets', config_dict)
    
    def test_color_scheme_to_dict(self):
        """Test color scheme CSS variable generation."""
        colors = ColorScheme(
            primary="#FF6B9D",
            secondary="#4ECDC4",
            accent="#FFE66D",
            background="#FFFFFF",
            text="#2D3436",
            text_secondary="#636E72"
        )
        
        css_vars = colors.to_dict()
        
        self.assertEqual(css_vars['--color-primary'], "#FF6B9D")
        self.assertEqual(css_vars['--color-secondary'], "#4ECDC4")
        self.assertEqual(css_vars['--color-accent'], "#FFE66D")


if __name__ == '__main__':
    unittest.main()