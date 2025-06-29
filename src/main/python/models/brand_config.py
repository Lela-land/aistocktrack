"""
Brand configuration models for frontend theming and customization.
Handles Pop Mart and Pokémon card brand-specific settings.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .product import BrandType


@dataclass
class ColorScheme:
    """Color scheme configuration for brand theming."""
    
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    text_secondary: str
    success: str = "#10B981"
    warning: str = "#F59E0B"
    error: str = "#EF4444"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for CSS generation."""
        return {
            '--color-primary': self.primary,
            '--color-secondary': self.secondary,
            '--color-accent': self.accent,
            '--color-background': self.background,
            '--color-text': self.text,
            '--color-text-secondary': self.text_secondary,
            '--color-success': self.success,
            '--color-warning': self.warning,
            '--color-error': self.error
        }


@dataclass
class Typography:
    """Typography configuration for brand theming."""
    
    font_family_primary: str
    font_family_secondary: str
    font_size_base: str = "16px"
    font_size_large: str = "24px"
    font_size_small: str = "14px"
    line_height: str = "1.5"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for CSS generation."""
        return {
            '--font-family-primary': self.font_family_primary,
            '--font-family-secondary': self.font_family_secondary,
            '--font-size-base': self.font_size_base,
            '--font-size-large': self.font_size_large,
            '--font-size-small': self.font_size_small,
            '--line-height': self.line_height
        }


@dataclass
class BrandAssets:
    """Brand asset URLs and configurations."""
    
    logo_url: str
    favicon_url: str
    background_pattern: Optional[str] = None
    hero_image: Optional[str] = None
    placeholder_image: str = "/static/images/placeholder.jpg"
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert to dictionary for template rendering."""
        return {
            'logo_url': self.logo_url,
            'favicon_url': self.favicon_url,
            'background_pattern': self.background_pattern,
            'hero_image': self.hero_image,
            'placeholder_image': self.placeholder_image
        }


@dataclass
class BrandConfig:
    """
    Complete brand configuration for frontend theming.
    
    Handles all brand-specific customization including:
    - Visual styling (colors, typography)
    - Assets (logos, images)
    - Content (text, messaging)
    - Layout preferences
    """
    
    brand_type: BrandType
    display_name: str
    tagline: str
    colors: ColorScheme
    typography: Typography
    assets: BrandAssets
    
    # Content customization
    product_term: str = "item"  # "figure", "card", etc.
    category_labels: Dict[str, str] = field(default_factory=dict)
    
    # Layout preferences
    grid_columns: int = 4
    show_price_history: bool = True
    show_stock_alerts: bool = True
    enable_wishlist: bool = True
    
    # SEO and metadata
    meta_description: str = ""
    meta_keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert complete configuration to dictionary."""
        return {
            'brand_type': self.brand_type.value,
            'display_name': self.display_name,
            'tagline': self.tagline,
            'colors': self.colors.to_dict(),
            'typography': self.typography.to_dict(),
            'assets': self.assets.to_dict(),
            'product_term': self.product_term,
            'category_labels': self.category_labels,
            'grid_columns': self.grid_columns,
            'show_price_history': self.show_price_history,
            'show_stock_alerts': self.show_stock_alerts,
            'enable_wishlist': self.enable_wishlist,
            'meta_description': self.meta_description,
            'meta_keywords': self.meta_keywords
        }


# Predefined brand configurations
POP_MART_CONFIG = BrandConfig(
    brand_type=BrandType.POP_MART,
    display_name="Pop Mart Tracker",
    tagline="Stay updated with the latest Pop Mart releases and restocks",
    colors=ColorScheme(
        primary="#FF6B9D",      # Pop Mart pink
        secondary="#4ECDC4",    # Teal accent
        accent="#FFE66D",       # Yellow highlight
        background="#FFFFFF",   # Clean white
        text="#2D3436",         # Dark gray
        text_secondary="#636E72" # Light gray
    ),
    typography=Typography(
        font_family_primary="'Inter', 'Helvetica Neue', sans-serif",
        font_family_secondary="'Poppins', 'Inter', sans-serif"
    ),
    assets=BrandAssets(
        logo_url="/static/images/popmart-logo.png",
        favicon_url="/static/images/popmart-favicon.ico",
        background_pattern="/static/images/popmart-pattern.svg",
        hero_image="/static/images/popmart-hero.jpg"
    ),
    product_term="figure",
    category_labels={
        "blind_box": "Blind Box Series",
        "mega": "Mega Collection",
        "diy": "DIY Series",
        "plush": "Plush Collection"
    },
    meta_description="Track Pop Mart figure availability, prices, and restocks across multiple retailers",
    meta_keywords=["pop mart", "blind box", "figures", "collectibles", "stock tracker"]
)

POKEMON_CONFIG = BrandConfig(
    brand_type=BrandType.POKEMON,
    display_name="Pokémon Card Tracker",
    tagline="Catch the best deals on Pokémon trading cards",
    colors=ColorScheme(
        primary="#FFCB05",      # Pokémon yellow
        secondary="#3B4CCA",    # Pokémon blue
        accent="#FF0000",       # Pokémon red
        background="#F8F9FA",   # Light background
        text="#212529",         # Dark text
        text_secondary="#6C757D" # Gray text
    ),
    typography=Typography(
        font_family_primary="'Roboto', 'Arial', sans-serif",
        font_family_secondary="'Roboto Condensed', 'Roboto', sans-serif"
    ),
    assets=BrandAssets(
        logo_url="/static/images/pokemon-logo.png",
        favicon_url="/static/images/pokemon-favicon.ico",
        background_pattern="/static/images/pokemon-pattern.svg",
        hero_image="/static/images/pokemon-hero.jpg"
    ),
    product_term="card",
    category_labels={
        "booster": "Booster Packs",
        "box": "Booster Boxes",
        "deck": "Theme Decks",
        "tin": "Collector Tins",
        "single": "Single Cards"
    },
    grid_columns=3,
    meta_description="Track Pokémon trading card prices, availability, and deals from top retailers",
    meta_keywords=["pokemon", "trading cards", "booster packs", "tcg", "price tracker"]
)


def get_brand_config(brand_type: BrandType) -> BrandConfig:
    """Get brand configuration by brand type."""
    configs = {
        BrandType.POP_MART: POP_MART_CONFIG,
        BrandType.POKEMON: POKEMON_CONFIG
    }
    return configs.get(brand_type, POP_MART_CONFIG)