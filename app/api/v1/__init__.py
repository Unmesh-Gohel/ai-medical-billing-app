"""
API v1 package for Medical Billing System
"""

from fastapi import APIRouter
from .router import api_router

__all__ = ["api_router"] 