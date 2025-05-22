"""
Core module for Proyecto Académico Generator
Contains the main application logic and core components
"""

from .app_core import ProyectoAcademicoGenerator
from .config_manager import ConfigManager
from .document_generator import DocumentGenerator

__version__ = "2.0.0"
__author__ = "ZoluGames"

__all__ = [
    'ProyectoAcademicoGenerator',
    'ConfigManager', 
    'DocumentGenerator'
]