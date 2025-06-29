"""
Database manager for aistocktrack application.
Handles product data storage and retrieval using SQLite with in-memory fallback.
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ..models.product import Product, BrandType, StockStatus, PriceHistory, StockAlert


class DatabaseManager:
    """SQLite database manager for product data."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses in-memory database.
        """
        if db_path is None:
            # Use in-memory database for development
            self.db_path = ":memory:"
        else:
            self.db_path = db_path
            # Ensure directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        self._create_tables()
        self._populate_sample_data()  # Add sample data for development
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.connection.cursor()
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                source TEXT NOT NULL,
                purchase_link TEXT NOT NULL,
                price REAL NOT NULL,
                original_price REAL,
                stock_level INTEGER NOT NULL,
                stock_status TEXT NOT NULL,
                image_url TEXT NOT NULL,
                video_url TEXT,
                description TEXT,
                category TEXT,
                tags TEXT,  -- JSON array
                last_updated TEXT NOT NULL,
                metadata TEXT  -- JSON object
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Stock alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                threshold INTEGER,
                target_price REAL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_brand ON products (brand)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_stock_status ON products (stock_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history (product_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history (timestamp)')
        
        self.connection.commit()
    
    def _populate_sample_data(self):
        """Add sample data for development and testing."""
        # Check if we already have data
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        
        if count > 0:
            return  # Data already exists
        
        # Sample Pop Mart products
        pop_mart_products = [
            Product(
                id="pm_001",
                name="SKULLPANDA The Sound Series",
                brand=BrandType.POP_MART,
                source="Pop Mart Official",
                purchase_link="https://www.popmart.com/skullpanda-sound",
                price=12.99,
                original_price=14.99,
                stock_level=25,
                stock_status=StockStatus.IN_STOCK,
                image_url="/static/images/skullpanda-sound.jpg",
                description="Limited edition SKULLPANDA figure with sound effects",
                category="blind_box",
                tags=["limited", "sound", "skull"]
            ),
            Product(
                id="pm_002",
                name="Molly Chess Club Series",
                brand=BrandType.POP_MART,
                source="Pop Mart Official",
                purchase_link="https://www.popmart.com/molly-chess",
                price=13.50,
                stock_level=3,
                stock_status=StockStatus.LOW_STOCK,
                image_url="/static/images/molly-chess.jpg",
                description="Molly figure in chess-themed outfit",
                category="blind_box",
                tags=["molly", "chess", "classic"]
            ),
            Product(
                id="pm_003",
                name="HIRONO Little Matchgirl Series",
                brand=BrandType.POP_MART,
                source="Pop Mart Official",
                purchase_link="https://www.popmart.com/hirono-matchgirl",
                price=15.99,
                stock_level=0,
                stock_status=StockStatus.OUT_OF_STOCK,
                image_url="/static/images/hirono-matchgirl.jpg",
                description="Emotional storytelling figure series",
                category="blind_box",
                tags=["hirono", "story", "emotional"]
            )
        ]
        
        # Sample Pokémon products
        pokemon_products = [
            Product(
                id="pk_001",
                name="Pokémon TCG Scarlet & Violet Booster Pack",
                brand=BrandType.POKEMON,
                source="Pokémon Center",
                purchase_link="https://www.pokemoncenter.com/sv-booster",
                price=4.99,
                stock_level=150,
                stock_status=StockStatus.IN_STOCK,
                image_url="/static/images/sv-booster.jpg",
                description="Latest Scarlet & Violet series booster pack",
                category="booster",
                tags=["scarlet", "violet", "booster"]
            ),
            Product(
                id="pk_002",
                name="Charizard ex Premium Collection",
                brand=BrandType.POKEMON,
                source="Pokémon Center",
                purchase_link="https://www.pokemoncenter.com/charizard-premium",
                price=79.99,
                original_price=89.99,
                stock_level=8,
                stock_status=StockStatus.LOW_STOCK,
                image_url="/static/images/charizard-premium.jpg",
                description="Premium collection featuring Charizard ex card",
                category="box",
                tags=["charizard", "premium", "ex"]
            ),
            Product(
                id="pk_003",
                name="Professor's Research Theme Deck",
                brand=BrandType.POKEMON,
                source="Local Game Store",
                purchase_link="https://example.com/professor-deck",
                price=19.99,
                stock_level=45,
                stock_status=StockStatus.IN_STOCK,
                image_url="/static/images/professor-deck.jpg",
                description="Ready-to-play theme deck for beginners",
                category="deck",
                tags=["theme", "beginner", "professor"]
            )
        ]
        
        # Insert sample products
        all_products = pop_mart_products + pokemon_products
        for product in all_products:
            self.save_product(product)
        
        # Add some sample price history
        sample_history = [
            PriceHistory("pm_001", 14.99, datetime.now()),
            PriceHistory("pm_001", 13.99, datetime.now()),
            PriceHistory("pm_001", 12.99, datetime.now()),
            PriceHistory("pk_002", 89.99, datetime.now()),
            PriceHistory("pk_002", 84.99, datetime.now()),
            PriceHistory("pk_002", 79.99, datetime.now()),
        ]
        
        for history in sample_history:
            self.save_price_history(history)
    
    def save_product(self, product: Product):
        """Save or update a product in the database."""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO products (
                id, name, brand, source, purchase_link, price, original_price,
                stock_level, stock_status, image_url, video_url, description,
                category, tags, last_updated, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product.id,
            product.name,
            product.brand.value,
            product.source,
            product.purchase_link,
            product.price,
            product.original_price,
            product.stock_level,
            product.stock_status.value,
            product.image_url,
            product.video_url,
            product.description,
            product.category,
            json.dumps(product.tags),
            product.last_updated.isoformat(),
            json.dumps(product.metadata)
        ))
        
        self.connection.commit()
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a single product by ID."""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_product(row)
        return None
    
    def get_products(
        self,
        brand: Optional[BrandType] = None,
        stock_status: Optional[StockStatus] = None,
        limit: Optional[int] = None
    ) -> List[Product]:
        """Get products with optional filtering."""
        cursor = self.connection.cursor()
        
        query = 'SELECT * FROM products WHERE 1=1'
        params = []
        
        if brand:
            query += ' AND brand = ?'
            params.append(brand.value)
        
        if stock_status:
            query += ' AND stock_status = ?'
            params.append(stock_status.value)
        
        query += ' ORDER BY last_updated DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_product(row) for row in rows]
    
    def search_products(
        self,
        brand: Optional[BrandType] = None,
        category: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_by: str = 'name',
        page: int = 1,
        per_page: int = 50
    ) -> List[Product]:
        """Search products with multiple filters and pagination."""
        cursor = self.connection.cursor()
        
        query = 'SELECT * FROM products WHERE 1=1'
        params = []
        
        if brand:
            query += ' AND brand = ?'
            params.append(brand.value)
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if search_term:
            query += ' AND (name LIKE ? OR description LIKE ?)'
            search_pattern = f'%{search_term}%'
            params.extend([search_pattern, search_pattern])
        
        # Add sorting
        sort_mapping = {
            'name': 'name ASC',
            'price': 'price ASC',
            'price_desc': 'price DESC',
            'stock_level': 'stock_level DESC',
            'last_updated': 'last_updated DESC'
        }
        order_clause = sort_mapping.get(sort_by, 'name ASC')
        query += f' ORDER BY {order_clause}'
        
        # Add pagination
        offset = (page - 1) * per_page
        query += ' LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_product(row) for row in rows]
    
    def get_categories(self, brand: Optional[BrandType] = None) -> List[str]:
        """Get available categories, optionally filtered by brand."""
        cursor = self.connection.cursor()
        
        if brand:
            cursor.execute(
                'SELECT DISTINCT category FROM products WHERE brand = ? AND category IS NOT NULL',
                (brand.value,)
            )
        else:
            cursor.execute('SELECT DISTINCT category FROM products WHERE category IS NOT NULL')
        
        rows = cursor.fetchall()
        return sorted([row[0] for row in rows])
    
    def update_product(self, product: Product):
        """Update an existing product."""
        self.save_product(product)  # INSERT OR REPLACE handles updates
    
    def save_price_history(self, price_history: PriceHistory):
        """Save a price history entry."""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO price_history (product_id, price, timestamp, source)
            VALUES (?, ?, ?, ?)
        ''', (
            price_history.product_id,
            price_history.price,
            price_history.timestamp.isoformat(),
            price_history.source
        ))
        
        self.connection.commit()
    
    def get_price_history(
        self, 
        product_id: str, 
        since_date: Optional[datetime] = None
    ) -> List[PriceHistory]:
        """Get price history for a product."""
        cursor = self.connection.cursor()
        
        query = 'SELECT * FROM price_history WHERE product_id = ?'
        params = [product_id]
        
        if since_date:
            query += ' AND timestamp >= ?'
            params.append(since_date.isoformat())
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_price_history(row) for row in rows]
    
    def save_stock_alert(self, alert: StockAlert):
        """Save a stock alert."""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO stock_alerts (
                product_id, alert_type, threshold, target_price, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            alert.product_id,
            alert.alert_type,
            alert.threshold,
            alert.target_price,
            alert.is_active,
            alert.created_at.isoformat()
        ))
        
        self.connection.commit()
    
    def _row_to_product(self, row: sqlite3.Row) -> Product:
        """Convert database row to Product object."""
        return Product(
            id=row['id'],
            name=row['name'],
            brand=BrandType(row['brand']),
            source=row['source'],
            purchase_link=row['purchase_link'],
            price=row['price'],
            original_price=row['original_price'],
            stock_level=row['stock_level'],
            stock_status=StockStatus(row['stock_status']),
            image_url=row['image_url'],
            video_url=row['video_url'],
            description=row['description'],
            category=row['category'],
            tags=json.loads(row['tags']) if row['tags'] else [],
            last_updated=datetime.fromisoformat(row['last_updated']),
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def _row_to_price_history(self, row: sqlite3.Row) -> PriceHistory:
        """Convert database row to PriceHistory object."""
        return PriceHistory(
            product_id=row['product_id'],
            price=row['price'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            source=row['source']
        )
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()