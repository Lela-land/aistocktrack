# aistocktrack API Documentation

## Overview

The aistocktrack API provides a unified interface for accessing merchandise inventory data across multiple brands. The API supports both programmatic access and powers the brand-specific web interfaces.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, no authentication is required for read-only endpoints. This is suitable for the current public data model.

## Response Format

All API responses follow this format:

```json
{
  "success": true|false,
  "data": {},
  "error": "Error message (if success=false)",
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 100
  }
}
```

## Endpoints

### Health Check

#### GET /api/health

Check API status and uptime.

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Products

#### GET /api/products

Get products with filtering and pagination.

**Query Parameters:**
- `brand` (string, optional): Filter by brand (`pop_mart`, `pokemon`)
- `category` (string, optional): Filter by product category
- `search` (string, optional): Search in product name and description
- `sort` (string, optional): Sort field (`name`, `price`, `price_desc`, `stock_level`, `last_updated`)
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Items per page (default: 50, max: 100)

**Example Request:**
```
GET /api/products?brand=pop_mart&category=blind_box&sort=price&page=1&per_page=20
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "pm_001",
      "name": "SKULLPANDA The Sound Series",
      "brand": "pop_mart",
      "source": "Pop Mart Official",
      "purchase_link": "https://www.popmart.com/skullpanda-sound",
      "price": 12.99,
      "original_price": 14.99,
      "stock_level": 25,
      "stock_status": "in_stock",
      "image_url": "/static/images/skullpanda-sound.jpg",
      "video_url": null,
      "description": "Limited edition SKULLPANDA figure with sound effects",
      "category": "blind_box",
      "tags": ["limited", "sound", "skull"],
      "last_updated": "2024-01-15T10:30:00Z",
      "metadata": {},
      "is_on_sale": true,
      "discount_percentage": 13.34,
      "availability_text": "25 available"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1
  }
}
```

#### GET /api/products/{product_id}

Get single product details.

**Path Parameters:**
- `product_id` (string, required): Product identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "pm_001",
    "name": "SKULLPANDA The Sound Series",
    "brand": "pop_mart",
    "source": "Pop Mart Official",
    "purchase_link": "https://www.popmart.com/skullpanda-sound",
    "price": 12.99,
    "original_price": 14.99,
    "stock_level": 25,
    "stock_status": "in_stock",
    "image_url": "/static/images/skullpanda-sound.jpg",
    "video_url": null,
    "description": "Limited edition SKULLPANDA figure with sound effects",
    "category": "blind_box",
    "tags": ["limited", "sound", "skull"],
    "last_updated": "2024-01-15T10:30:00Z",
    "metadata": {},
    "is_on_sale": true,
    "discount_percentage": 13.34,
    "availability_text": "25 available"
  }
}
```

#### GET /api/products/{product_id}/history

Get product price history.

**Path Parameters:**
- `product_id` (string, required): Product identifier

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "product_id": "pm_001",
      "price": 12.99,
      "timestamp": "2024-01-15T10:30:00Z",
      "source": "Pop Mart Official"
    },
    {
      "product_id": "pm_001",
      "price": 13.99,
      "timestamp": "2024-01-14T10:30:00Z",
      "source": "Pop Mart Official"
    }
  ]
}
```

### Brands

#### GET /api/brands

Get available brands and their configurations.

**Response:**
```json
{
  "success": true,
  "data": {
    "pop_mart": {
      "display_name": "Pop Mart Tracker",
      "tagline": "Stay updated with the latest Pop Mart releases and restocks",
      "product_term": "figure"
    },
    "pokemon": {
      "display_name": "Pokémon Card Tracker",
      "tagline": "Catch the best deals on Pokémon trading cards",
      "product_term": "card"
    }
  }
}
```

### Categories

#### GET /api/categories

Get available product categories.

**Query Parameters:**
- `brand` (string, optional): Filter categories by brand

**Response:**
```json
{
  "success": true,
  "data": [
    "blind_box",
    "mega",
    "diy",
    "plush"
  ]
}
```

### Stock Alerts

#### POST /api/stock-alerts

Create a stock alert for a product.

**Request Body:**
```json
{
  "product_id": "pm_001",
  "alert_type": "back_in_stock",
  "threshold": 5,
  "target_price": 10.99
}
```

**Alert Types:**
- `back_in_stock`: Notify when product comes back in stock
- `low_stock`: Notify when stock level reaches threshold
- `price_drop`: Notify when price drops to target price

**Response:**
```json
{
  "success": true,
  "data": {
    "product_id": "pm_001",
    "alert_type": "back_in_stock",
    "threshold": null,
    "target_price": null,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Detailed error message"
}
```

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (product/endpoint not found)
- `500`: Internal Server Error

### Common Error Messages

- "Product not found": The requested product ID doesn't exist
- "Invalid brand": Brand parameter must be 'pop_mart' or 'pokemon'
- "Invalid sort parameter": Sort field is not supported
- "per_page too large": Maximum per_page is 100

## Rate Limiting

No rate limiting is currently implemented, but it's recommended to limit requests to avoid overwhelming the service.

## Web Interface Routes

The API also powers brand-specific web interfaces:

### Homepage
- `GET /` - Brand selection page
- `GET /{brand_type}` - Brand-specific homepage
- `GET /{brand_type}/products` - Product listing page
- `GET /{brand_type}/product/{product_id}` - Product detail page

### Supported Brand Types
- `pop_mart` - Pop Mart figures interface
- `pokemon` - Pokémon trading cards interface

## Data Collection

The system includes automated data collection services:

### Manual Collection
```bash
python scripts/collect_data.py
```

### Simulation (for testing)
```bash
python scripts/simulate_updates.py
```

## Deployment

### Development
```bash
python run.py
```

### Docker
```bash
docker-compose up
```

### Production with nginx
```bash
docker-compose --profile production up
```

## Data Models

### Product Model
```python
{
  "id": "string",                    # Unique identifier
  "name": "string",                  # Product name
  "brand": "pop_mart|pokemon",       # Brand type
  "source": "string",                # Retailer/source name
  "purchase_link": "string",         # Direct purchase URL
  "price": "number",                 # Current price (USD)
  "original_price": "number|null",   # Original/MSRP price
  "stock_level": "integer",          # Current stock quantity
  "stock_status": "string",          # in_stock|low_stock|out_of_stock|discontinued
  "image_url": "string",             # Product image URL
  "video_url": "string|null",        # Product video URL
  "description": "string|null",      # Product description
  "category": "string|null",         # Product category
  "tags": ["string"],                # Product tags
  "last_updated": "string",          # ISO timestamp
  "metadata": "object",              # Additional data
  "is_on_sale": "boolean",           # Computed: on sale status
  "discount_percentage": "number|null", # Computed: discount %
  "availability_text": "string"     # Computed: user-friendly availability
}
```

### Stock Status Values
- `in_stock`: Product is available
- `low_stock`: Low inventory (typically ≤5 items)
- `out_of_stock`: No inventory available
- `discontinued`: Product no longer available

### Brand Types
- `pop_mart`: Pop Mart figures and collectibles
- `pokemon`: Pokémon trading card products

## Examples

### Get all Pop Mart figures on sale
```bash
curl "http://localhost:5000/api/products?brand=pop_mart" | \
  jq '.data[] | select(.is_on_sale == true)'
```

### Get low stock Pokémon products
```bash
curl "http://localhost:5000/api/products?brand=pokemon" | \
  jq '.data[] | select(.stock_status == "low_stock")'
```

### Search for specific products
```bash
curl "http://localhost:5000/api/products?search=charizard&brand=pokemon"
```

### Get price history for a product
```bash
curl "http://localhost:5000/api/products/pk_001/history"
```