"""
Cargador de configuración desde archivos externos.
"""

import json
from pathlib import Path
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger('ConfigLoader')

class ConfigLoader:
    """Carga configuración desde archivos JSON."""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.user_config_file = self.config_dir / "user_config.json"
        self.default_config = self._get_default_config()
    
    def load_user_config(self) -> Dict[str, Any]:
        """Carga configuración del usuario."""
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Fusionar con configuración por defecto
                config = self.default_config.copy()
                config.update(user_config)
                return config
            except Exception as e:
                logger.error(f"Error cargando configuración de usuario: {e}")
        
        return self.default_config
    
    def save_user_config(self, config: Dict[str, Any]):
        """Guarda configuración del usuario."""
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info("Configuración de usuario guardada")
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")