"""
Product service layer for business logic and data operations.
Handles product retrieval, filtering, and stock management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models.product import Product, BrandType, StockStatus, PriceHistory, StockAlert
from ..core.database import DatabaseManager


class ProductService:
    """Service class for product-related operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_all_products(self, limit: Optional[int] = None) -> List[Product]:
        """Get all products with optional limit."""
        return self.db.get_products(limit=limit)
    
    def get_products_by_brand(self, brand: BrandType, limit: Optional[int] = None) -> List[Product]:
        """Get products filtered by brand."""
        return self.db.get_products(brand=brand, limit=limit)
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get single product by ID."""
        return self.db.get_product_by_id(product_id)
    
    def search_products(
        self,
        brand: Optional[BrandType] = None,
        category: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_by: str = 'name',
        page: int = 1,
        per_page: int = 50
    ) -> List[Product]:
        """
        Search products with multiple filters.
        
        Args:
            brand: Filter by brand type
            category: Filter by product category
            search_term: Search in product name and description
            sort_by: Sort field ('name', 'price', 'stock_level', 'last_updated')
            page: Page number for pagination
            per_page: Items per page
        """
        return self.db.search_products(
            brand=brand,
            category=category,
            search_term=search_term,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
    
    def get_categories_by_brand(self, brand: BrandType) -> List[str]:
        """Get available categories for a specific brand."""
        return self.db.get_categories(brand=brand)
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories across all brands."""
        return self.db.get_categories()
    
    def get_featured_products(self, brand: BrandType, limit: int = 6) -> List[Product]:
        """
        Get featured products for homepage display.
        Returns products that are in stock and have good availability.
        """
        products = self.db.get_products(
            brand=brand,
            stock_status=StockStatus.IN_STOCK,
            limit=limit * 2  # Get more to filter from
        )
        
        # Prioritize products with good stock levels
        featured = []
        for product in products:
            if len(featured) >= limit:
                break
            if product.stock_level > 10 or product.is_on_sale:
                featured.append(product)
        
        # Fill remaining slots with any in-stock products
        if len(featured) < limit:
            for product in products:
                if len(featured) >= limit:
                    break
                if product not in featured:
                    featured.append(product)
        
        return featured[:limit]
    
    def get_related_products(
        self, 
        product_id: str, 
        brand: BrandType, 
        limit: int = 4
    ) -> List[Product]:
        """Get products related to the given product."""
        current_product = self.get_product_by_id(product_id)
        if not current_product:
            return []
        
        # Get products from same category first
        related = self.db.search_products(
            brand=brand,
            category=current_product.category,
            limit=limit * 2
        )
        
        # Remove current product from results
        related = [p for p in related if p.id != product_id]
        
        # If not enough from same category, fill with brand products
        if len(related) < limit:
            additional = self.db.get_products(brand=brand, limit=limit * 2)
            for product in additional:
                if len(related) >= limit:
                    break
                if product.id != product_id and product not in related:
                    related.append(product)
        
        return related[:limit]
    
    def get_price_history(
        self, 
        product_id: str, 
        days: int = 30
    ) -> List[PriceHistory]:
        """Get price history for a product over specified days."""
        since_date = datetime.now() - timedelta(days=days)
        return self.db.get_price_history(product_id, since_date)
    
    def add_price_point(
        self, 
        product_id: str, 
        price: float, 
        source: Optional[str] = None
    ) -> PriceHistory:
        """Add a new price point to history."""
        price_point = PriceHistory(
            product_id=product_id,
            price=price,
            source=source
        )
        self.db.save_price_history(price_point)
        return price_point
    
    def create_stock_alert(
        self,
        product_id: str,
        alert_type: str,
        threshold: Optional[int] = None,
        target_price: Optional[float] = None
    ) -> StockAlert:
        """Create a new stock alert."""
        alert = StockAlert(
            product_id=product_id,
            alert_type=alert_type,
            threshold=threshold,
            target_price=target_price
        )
        self.db.save_stock_alert(alert)
        return alert
    
    def get_low_stock_products(self, threshold: int = 5) -> List[Product]:
        """Get products with low stock levels."""
        all_products = self.db.get_products()
        return [
            p for p in all_products 
            if p.stock_level <= threshold and p.stock_status != StockStatus.OUT_OF_STOCK
        ]
    
    def get_price_drop_products(self, days: int = 7) -> List[Product]:
        """Get products that have had recent price drops."""
        price_drops = []
        products = self.db.get_products(limit=100)  # Check recent products
        
        for product in products:
            history = self.get_price_history(product.id, days)
            if len(history) >= 2:
                # Check if price has decreased from earliest to latest
                earliest_price = history[-1].price  # Oldest entry
                latest_price = history[0].price     # Newest entry
                
                if latest_price < earliest_price:
                    price_drops.append(product)
        
        return price_drops
    
    def update_product_stock(
        self, 
        product_id: str, 
        stock_level: int,
        stock_status: Optional[StockStatus] = None
    ) -> Optional[Product]:
        """Update product stock information."""
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        
        # Auto-determine stock status if not provided
        if stock_status is None:
            if stock_level == 0:
                stock_status = StockStatus.OUT_OF_STOCK
            elif stock_level <= 5:
                stock_status = StockStatus.LOW_STOCK
            else:
                stock_status = StockStatus.IN_STOCK
        
        product.stock_level = stock_level
        product.stock_status = stock_status
        product.last_updated = datetime.now()
        
        self.db.update_product(product)
        return product
    
    def update_product_price(
        self, 
        product_id: str, 
        new_price: float,
        source: Optional[str] = None
    ) -> Optional[Product]:
        """Update product price and record in history."""
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        
        # Record price change in history if different
        if product.price != new_price:
            self.add_price_point(product_id, new_price, source)
        
        product.price = new_price
        product.last_updated = datetime.now()
        
        self.db.update_product(product)
        return product
    
    def get_statistics(self, brand: Optional[BrandType] = None) -> Dict[str, Any]:
        """Get general statistics about products."""
        products = self.db.get_products(brand=brand)
        
        if not products:
            return {
                'total_products': 0,
                'in_stock': 0,
                'low_stock': 0,
                'out_of_stock': 0,
                'average_price': 0,
                'categories': []
            }
        
        # Count by status
        status_counts = {}
        for status in StockStatus:
            status_counts[status.value] = len([
                p for p in products if p.stock_status == status
            ])
        
        # Calculate average price
        prices = [p.price for p in products if p.price > 0]
        avg_price = sum(prices) / len(prices) if prices else 0
        
        # Get categories
        categories = list(set(p.category for p in products if p.category))
        
        return {
            'total_products': len(products),
            'in_stock': status_counts.get('in_stock', 0),
            'low_stock': status_counts.get('low_stock', 0),
            'out_of_stock': status_counts.get('out_of_stock', 0),
            'discontinued': status_counts.get('discontinued', 0),
            'average_price': round(avg_price, 2),
            'categories': sorted(categories)
        }