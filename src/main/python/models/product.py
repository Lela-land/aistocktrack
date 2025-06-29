"""
Product data models for aistocktrack system.
Handles merchandise inventory tracking with unified backend structure.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BrandType(Enum):
    """Supported brand types for frontend theming."""
    POP_MART = "pop_mart"
    POKEMON = "pokemon"


class StockStatus(Enum):
    """Stock availability status."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


@dataclass
class Product:
    """
    Core product model for merchandise inventory tracking.
    
    Attributes:
        id: Unique product identifier
        name: Product display name
        brand: Brand type for frontend theming
        source: Data source/retailer name
        purchase_link: Direct purchase URL
        price: Current price in USD
        original_price: Original/MSRP price
        stock_level: Current stock quantity
        stock_status: Stock availability status
        image_url: Primary product image URL
        video_url: Optional product video URL
        description: Product description
        category: Product category
        tags: Product tags for filtering
        last_updated: Last data update timestamp
        metadata: Additional product-specific data
    """
    
    id: str
    name: str
    brand: BrandType
    source: str
    purchase_link: str
    price: float
    stock_level: int
    stock_status: StockStatus
    image_url: str
    
    # Optional fields
    original_price: Optional[float] = None
    video_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_on_sale(self) -> bool:
        """Check if product is currently on sale."""
        return (
            self.original_price is not None 
            and self.price < self.original_price
        )
    
    @property
    def discount_percentage(self) -> Optional[float]:
        """Calculate discount percentage if on sale."""
        if not self.is_on_sale or not self.original_price:
            return None
        return round(((self.original_price - self.price) / self.original_price) * 100, 2)
    
    @property
    def availability_text(self) -> str:
        """Get user-friendly availability text."""
        status_map = {
            StockStatus.IN_STOCK: f"{self.stock_level} available",
            StockStatus.LOW_STOCK: f"Only {self.stock_level} left",
            StockStatus.OUT_OF_STOCK: "Out of stock",
            StockStatus.DISCONTINUED: "Discontinued"
        }
        return status_map.get(self.stock_status, "Unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand.value,
            'source': self.source,
            'purchase_link': self.purchase_link,
            'price': self.price,
            'original_price': self.original_price,
            'stock_level': self.stock_level,
            'stock_status': self.stock_status.value,
            'image_url': self.image_url,
            'video_url': self.video_url,
            'description': self.description,
            'category': self.category,
            'tags': self.tags,
            'last_updated': self.last_updated.isoformat(),
            'metadata': self.metadata,
            'is_on_sale': self.is_on_sale,
            'discount_percentage': self.discount_percentage,
            'availability_text': self.availability_text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Create Product instance from dictionary."""
        # Convert string enums back to enum instances
        data['brand'] = BrandType(data['brand'])
        data['stock_status'] = StockStatus(data['stock_status'])
        
        # Convert ISO timestamp back to datetime
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        # Remove computed properties from data
        computed_fields = ['is_on_sale', 'discount_percentage', 'availability_text']
        for field in computed_fields:
            data.pop(field, None)
        
        return cls(**data)


@dataclass
class PriceHistory:
    """Track price changes over time for trending analysis."""
    
    product_id: str
    price: float
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'product_id': self.product_id,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }


@dataclass
class StockAlert:
    """Stock level alert configuration."""
    
    product_id: str
    alert_type: str  # 'low_stock', 'back_in_stock', 'price_drop'
    threshold: Optional[int] = None  # For stock level alerts
    target_price: Optional[float] = None  # For price drop alerts
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'product_id': self.product_id,
            'alert_type': self.alert_type,
            'threshold': self.threshold,
            'target_price': self.target_price,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }