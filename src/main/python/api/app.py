"""
Flask application for aistocktrack API and web interface.
Provides unified backend with brand-specific frontend rendering.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime

from ..models.product import Product, BrandType, StockStatus
from ..models.brand_config import get_brand_config
from ..services.product_service import ProductService
from ..core.database import DatabaseManager


def create_app(config_name: str = 'development') -> Flask:
    """Create and configure Flask application."""
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Enable CORS for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize services
    db_manager = DatabaseManager()
    product_service = ProductService(db_manager)
    
    # Template globals for brand theming
    @app.template_global()
    def get_brand_theme(brand_type: str) -> Dict[str, Any]:
        """Get brand configuration for template rendering."""
        try:
            brand_enum = BrandType(brand_type)
            return get_brand_config(brand_enum).to_dict()
        except ValueError:
            return get_brand_config(BrandType.POP_MART).to_dict()
    
    @app.template_filter('currency')
    def currency_filter(value: float) -> str:
        """Format currency values."""
        return f"${value:.2f}"
    
    @app.template_filter('stock_class')
    def stock_class_filter(status: str) -> str:
        """Get CSS class for stock status."""
        class_map = {
            'in_stock': 'text-success',
            'low_stock': 'text-warning',
            'out_of_stock': 'text-danger',
            'discontinued': 'text-muted'
        }
        return class_map.get(status, 'text-muted')
    
    # Web Routes - Brand-specific frontends
    @app.route('/')
    def index():
        """Homepage with brand selection."""
        return render_template('index.html')
    
    @app.route('/<brand_type>')
    def brand_home(brand_type: str):
        """Brand-specific homepage."""
        try:
            brand_enum = BrandType(brand_type)
            products = product_service.get_products_by_brand(brand_enum, limit=12)
            return render_template(
                'brand_home.html',
                brand_type=brand_type,
                products=[p.to_dict() for p in products],
                featured_products=products[:4]
            )
        except ValueError:
            return redirect(url_for('index'))
    
    @app.route('/<brand_type>/products')
    def brand_products(brand_type: str):
        """Brand-specific product listing page."""
        try:
            brand_enum = BrandType(brand_type)
            
            # Get query parameters
            category = request.args.get('category')
            search = request.args.get('search', '').strip()
            sort_by = request.args.get('sort', 'name')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 24))
            
            # Get filtered products
            products = product_service.search_products(
                brand=brand_enum,
                category=category,
                search_term=search,
                sort_by=sort_by,
                page=page,
                per_page=per_page
            )
            
            # Get available categories for filter
            categories = product_service.get_categories_by_brand(brand_enum)
            
            return render_template(
                'products.html',
                brand_type=brand_type,
                products=[p.to_dict() for p in products],
                categories=categories,
                current_category=category,
                current_search=search,
                current_sort=sort_by,
                page=page
            )
        except ValueError:
            return redirect(url_for('index'))
    
    @app.route('/<brand_type>/product/<product_id>')
    def product_detail(brand_type: str, product_id: str):
        """Individual product detail page."""
        try:
            brand_enum = BrandType(brand_type)
            product = product_service.get_product_by_id(product_id)
            
            if not product or product.brand != brand_enum:
                return redirect(url_for('brand_products', brand_type=brand_type))
            
            # Get price history
            price_history = product_service.get_price_history(product_id)
            
            # Get related products
            related_products = product_service.get_related_products(
                product_id, brand_enum, limit=4
            )
            
            return render_template(
                'product_detail.html',
                brand_type=brand_type,
                product=product.to_dict(),
                price_history=[ph.to_dict() for ph in price_history],
                related_products=[p.to_dict() for p in related_products]
            )
        except ValueError:
            return redirect(url_for('index'))
    
    # API Routes - Unified backend interface
    @app.route('/api/products')
    def api_products():
        """Get products with filtering and pagination."""
        try:
            # Parse query parameters
            brand = request.args.get('brand')
            category = request.args.get('category')
            search = request.args.get('search', '').strip()
            sort_by = request.args.get('sort', 'name')
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 50)), 100)  # Limit max per_page
            
            brand_enum = BrandType(brand) if brand else None
            
            products = product_service.search_products(
                brand=brand_enum,
                category=category,
                search_term=search,
                sort_by=sort_by,
                page=page,
                per_page=per_page
            )
            
            return jsonify({
                'success': True,
                'data': [p.to_dict() for p in products],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': len(products)  # In a real app, get total count
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.route('/api/products/<product_id>')
    def api_product_detail(product_id: str):
        """Get single product details."""
        try:
            product = product_service.get_product_by_id(product_id)
            if not product:
                return jsonify({'success': False, 'error': 'Product not found'}), 404
            
            return jsonify({
                'success': True,
                'data': product.to_dict()
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.route('/api/products/<product_id>/history')
    def api_price_history(product_id: str):
        """Get product price history."""
        try:
            history = product_service.get_price_history(product_id)
            return jsonify({
                'success': True,
                'data': [h.to_dict() for h in history]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.route('/api/brands')
    def api_brands():
        """Get available brands and their configurations."""
        try:
            brands = {}
            for brand_type in BrandType:
                config = get_brand_config(brand_type)
                brands[brand_type.value] = {
                    'display_name': config.display_name,
                    'tagline': config.tagline,
                    'product_term': config.product_term
                }
            
            return jsonify({
                'success': True,
                'data': brands
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.route('/api/categories')
    def api_categories():
        """Get available categories by brand."""
        try:
            brand = request.args.get('brand')
            if brand:
                brand_enum = BrandType(brand)
                categories = product_service.get_categories_by_brand(brand_enum)
            else:
                categories = product_service.get_all_categories()
            
            return jsonify({
                'success': True,
                'data': categories
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.route('/api/stock-alerts', methods=['POST'])
    def api_create_stock_alert():
        """Create a stock alert for a product."""
        try:
            data = request.get_json()
            product_id = data.get('product_id')
            alert_type = data.get('alert_type')
            threshold = data.get('threshold')
            target_price = data.get('target_price')
            
            if not product_id or not alert_type:
                return jsonify({
                    'success': False, 
                    'error': 'product_id and alert_type are required'
                }), 400
            
            alert = product_service.create_stock_alert(
                product_id, alert_type, threshold, target_price
            )
            
            return jsonify({
                'success': True,
                'data': alert.to_dict()
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    # Health check endpoint
    @app.route('/api/health')
    def api_health():
        """Health check endpoint."""
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        return render_template('500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)