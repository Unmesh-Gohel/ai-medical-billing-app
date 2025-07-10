#!/usr/bin/env python3
"""
Entry point for AI Medical Billing System
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now we can import the app
from app.main import app
from app.config import settings

if __name__ == "__main__":
    print("🏥 Starting AI Medical Billing System...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"🚀 Server starting on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        access_log=True
    ) 