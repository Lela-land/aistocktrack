#!/usr/bin/env python3
"""
Main entry point for aistocktrack application.
Runs the Flask development server.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src" / "main" / "python"))

from api.app import create_app

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/app.log') if Path('logs').exists() else logging.NullHandler()
        ]
    )

if __name__ == '__main__':
    setup_logging()
    
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting aistocktrack server on http://{host}:{port}")
    print(f"📱 Pop Mart interface: http://{host}:{port}/pop_mart")
    print(f"🎮 Pokémon interface: http://{host}:{port}/pokemon")
    print(f"🔧 API health check: http://{host}:{port}/api/health")
    
    app.run(host=host, port=port, debug=debug)