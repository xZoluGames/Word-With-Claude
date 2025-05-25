"""
Configuración principal de la aplicación
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger('AppConfig')

class AppConfig:
    """Gestor centralizado de configuración de la aplicación"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path('config') / 'app_config.json'
        self.config_dir = self.config_path.parent
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuración por defecto
        self.default_config = {
            "app": {
                "name": "Generador de Proyectos Académicos",
                "version": "2.1.0",
                "author": "xZoluGames",
                "debug": False,
                "auto_update": True
            },
            "ui": {
                "theme": "dark",
                "color_theme": "blue",
                "window_size": "1200x700",
                "min_window_size": [1000, 600],
                "font_scale": 1.0,
                "compact_mode": False
            },
            "document": {
                "default_format": {
                    "fuente_texto": "Times New Roman",
                    "tamaño_texto": 12,
                    "fuente_titulo": "Times New Roman",
                    "tamaño_titulo": 14,
                    "interlineado": 2.0,
                    "margen": 2.54,
                    "justificado": True,
                    "sangria": True
                },
                "auto_save_interval": 300000,
                "include_metadata": True,
                "max_image_size": [1920, 1080]
            },
            "validation": {
                "min_section_length": 50,
                "min_references": 3,
                "required_fields": ["titulo", "estudiantes", "tutores"],
                "strict_mode": False
            },
            "backup": {
                "enabled": True,
                "max_backups": 20,
                "auto_backup_interval": 3600,
                "backup_dir": "backups"
            },
            "logging": {
                "level": "INFO",
                "file_size_mb": 10,
                "backup_count": 10,
                "console_output": True
            },
            "paths": {
                "resources": "resources",
                "templates": "plantillas",
                "exports": "exports",
                "cache": "cache"
            }
        }
        
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde archivo o crea una nueva"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Fusionar con configuración por defecto
                config = self._merge_configs(self.default_config, user_config)
                logger.info(f"Configuración cargada desde: {self.config_path}")
                return config
            else:
                # Crear configuración por defecto
                self.save_config(self.default_config)
                logger.info("Configuración por defecto creada")
                return self.default_config.copy()
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Guarda la configuración actual"""
        try:
            config_to_save = config or self.config
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuración guardada en: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de puntos
        Ej: get('ui.theme') -> 'dark'
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.warning(f"Error obteniendo configuración {key_path}: {e}")
            return default
    
    def set(self, key_path: str, value: Any, save: bool = True):
        """
        Establece un valor de configuración usando notación de puntos
        """
        try:
            keys = key_path.split('.')
            config = self.config
            
            # Navegar hasta el penúltimo nivel
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Establecer el valor
            config[keys[-1]] = value
            
            if save:
                self.save_config()
            
            logger.debug(f"Configuración actualizada: {key_path} = {value}")
            
        except Exception as e:
            logger.error(f"Error estableciendo configuración {key_path}: {e}")
    
    def reset_to_default(self, section: Optional[str] = None):
        """Restablece configuración por defecto"""
        try:
            if section:
                if section in self.default_config:
                    self.config[section] = self.default_config[section].copy()
                    logger.info(f"Sección {section} restablecida")
            else:
                self.config = self.default_config.copy()
                logger.info("Configuración completamente restablecida")
            
            self.save_config()
            
        except Exception as e:
            logger.error(f"Error restableciendo configuración: {e}")
    
    def validate_config(self) -> bool:
        """Valida la configuración actual"""
        try:
            errors = []
            
            # Validar estructura básica
            required_sections = ['app', 'ui', 'document', 'validation']
            for section in required_sections:
                if section not in self.config:
                    errors.append(f"Sección faltante: {section}")
            
            # Validar valores específicos
            window_size = self.get('ui.window_size', '')
            if not isinstance(window_size, str) or 'x' not in window_size:
                errors.append("ui.window_size debe tener formato 'WIDTHxHEIGHT'")
            
            font_scale = self.get('ui.font_scale', 1.0)
            if not isinstance(font_scale, (int, float)) or font_scale <= 0:
                errors.append("ui.font_scale debe ser un número positivo")
            
            if errors:
                logger.warning(f"Errores de validación: {errors}")
                return False
            
            logger.info("Configuración validada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error validando configuración: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """Exporta la configuración actual"""
        try:
            export_path = Path(export_path)
            
            export_data = {
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'app_version': self.get('app.version'),
                    'export_version': '1.0'
                },
                'config': self.config
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuración exportada a: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando configuración: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Importa configuración desde archivo"""
        try:
            import_path = Path(import_path)
            
            if not import_path.exists():
                logger.error(f"Archivo de configuración no encontrado: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validar estructura
            if 'config' not in import_data:
                logger.error("Archivo de configuración inválido")
                return False
            
            # Fusionar con configuración actual
            imported_config = import_data['config']
            self.config = self._merge_configs(self.config, imported_config)
            
            # Validar y guardar
            if self.validate_config():
                self.save_config()
                logger.info(f"Configuración importada desde: {import_path}")
                return True
            else:
                logger.error("La configuración importada no es válida")
                return False
                
        except Exception as e:
            logger.error(f"Error importando configuración: {e}")
            return False
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Fusiona dos diccionarios de configuración recursivamente"""
        result = base.copy()
        
        for key, value in override.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_paths(self) -> Dict[str, Path]:
        """Obtiene todas las rutas configuradas como objetos Path"""
        try:
            paths = {}
            base_paths = self.get('paths', {})
            
            for key, path_str in base_paths.items():
                paths[key] = Path(path_str)
                # Crear directorio si no existe
                paths[key].mkdir(exist_ok=True)
            
            return paths
            
        except Exception as e:
            logger.error(f"Error obteniendo rutas: {e}")
            return {}

# Instancia global de configuración
app_config = AppConfig()

# Funciones de conveniencia
def get_config(key_path: str, default: Any = None) -> Any:
    """Función de conveniencia para obtener configuración"""
    return app_config.get(key_path, default)

def set_config(key_path: str, value: Any, save: bool = True):
    """Función de conveniencia para establecer configuración"""
    app_config.set(key_path, value, save)