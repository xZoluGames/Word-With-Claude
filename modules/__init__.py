"""
Módulos funcionales para el Generador de Proyectos Académicos
Contiene las funcionalidades específicas del sistema
"""

from .image_manager import ImageManager
from .reference_manager import ReferenceManager
from .template_manager import TemplateManager
from .validator import ProjectValidator
from .backup_manager import BackupManager

__version__ = "2.0.0"

__all__ = [
    'ImageManager',
    'ReferenceManager', 
    'TemplateManager',
    'ProjectValidator',
    'BackupManager'
]