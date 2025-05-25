#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de Proyectos Académicos - Punto de entrada principal
Versión: 2.0
Autor: xZoluGames
"""

import sys
import logging
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import customtkinter as ctk
    from ui.main_window import ProyectoAcademicoGenerator
    from utils.logger import get_logger
    from config.settings import APP_CONFIG
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Asegúrate de que todas las dependencias estén instaladas:")
    print("pip install customtkinter pillow python-docx")
    sys.exit(1)

logger = get_logger("main")

def setup_application():
    """Configura la aplicación con manejo de errores"""
    try:
        # Configuración del tema desde settings
        ctk.set_appearance_mode(APP_CONFIG.get('theme', 'dark'))
        ctk.set_default_color_theme(APP_CONFIG.get('color_theme', 'blue'))
        
        logger.info(f"Iniciando {APP_CONFIG['name']} v{APP_CONFIG['version']}")
        return True
    except Exception as e:
        logger.error(f"Error configurando aplicación: {e}")
        return False

def main():
    """Función principal con manejo robusto de errores"""
    try:
        if not setup_application():
            sys.exit(1)
            
        app = ProyectoAcademicoGenerator()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Aplicación cerrada por el usuario")
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}", exc_info=True)
        print(f"❌ Error crítico: {e}")
        sys.exit(1)
    finally:
        logger.info("Aplicación finalizada")

if __name__ == "__main__":
    main()