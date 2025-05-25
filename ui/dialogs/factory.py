# ui/dialogs/factory.py - VERSION MEJORADA
"""
Factory para crear diálogos de la interfaz de usuario.

Este módulo implementa el patrón Factory para la creación centralizada
de diferentes tipos de diálogos en la aplicación.
"""

from utils.logger import get_logger
from .seccion_dialog import SeccionDialog
from .citation_dialog import CitationDialog
from .help_dialog import HelpDialog

logger = get_logger('DialogFactory')

class DialogFactory:
    """
    Factory para crear diferentes tipos de diálogos.
    
    Methods:
        create_dialog: Crea un diálogo del tipo especificado
    """
    
    @staticmethod
    def create_dialog(dialog_type: str, parent, **kwargs):
        """
        Crea un diálogo del tipo especificado.
        
        Args:
            dialog_type: Tipo de diálogo ('section', 'citation', 'help')
            parent: Ventana padre
            **kwargs: Argumentos adicionales para el diálogo
            
        Returns:
            Instancia del diálogo creado
            
        Raises:
            ValueError: Si el tipo de diálogo no es reconocido
        """
        dialogs = {
            'section': SeccionDialog,
            'citation': CitationDialog,
            'help': HelpDialog
        }
        
        dialog_class = dialogs.get(dialog_type)
        if dialog_class:
            logger.debug(f"Creando diálogo tipo: {dialog_type}")
            return dialog_class(parent, **kwargs)
        
        logger.error(f"Tipo de diálogo desconocido: {dialog_type}")
        raise ValueError(f"Tipo de diálogo desconocido: {dialog_type}")