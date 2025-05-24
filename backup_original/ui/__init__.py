"""
UI - Interfaz de usuario del generador de proyectos académicos
"""

from .main_window import ProyectoAcademicoGenerator
from .dialogs import SeccionDialog
from .components import StatsPanel, FormatPanel

__all__ = [
    'ProyectoAcademicoGenerator',
    'SeccionDialog',
    'StatsPanel',
    'FormatPanel'
]