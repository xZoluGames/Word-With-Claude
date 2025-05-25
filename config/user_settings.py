"""
Sistema de configuración de usuario persistente

Gestiona preferencias del usuario, configuraciones personalizadas
y perfiles de trabajo.
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import shutil
from utils.logger import get_logger

logger = get_logger('UserSettings')

class UserSettingsManager:
    """Gestor de configuración de usuario"""
    
    def __init__(self, app_data_dir: Optional[str] = None):
        """
        Inicializa el gestor de configuración
        
        Args:
            app_data_dir: Directorio de datos de la aplicación
        """
        # Determinar directorio de configuración
        if app_data_dir:
            self.config_dir = Path(app_data_dir)
        else:
            # Usar directorio estándar según el SO
            if os.name == 'nt':  # Windows
                self.config_dir = Path(os.environ.get('APPDATA', '')) / 'ProyectoAcademico'
            else:  # Linux/Mac
                self.config_dir = Path.home() / '.proyecto_academico'
        
        # Crear directorio si no existe
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos de configuración
        self.settings_file = self.config_dir / 'settings.json'
        self.profiles_dir = self.config_dir / 'profiles'
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Configuración actual
        self.current_settings = self._load_or_create_settings()
        self.current_profile = self.current_settings.get('active_profile', 'default')
        
        logger.info(f"UserSettingsManager inicializado en: {self.config_dir}")
    
    def _load_or_create_settings(self) -> Dict[str, Any]:
        """Carga o crea la configuración principal"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                logger.info("Configuración cargada exitosamente")
                return settings
            except Exception as e:
                logger.error(f"Error cargando configuración: {e}")
                return self._get_default_settings()
        else:
            logger.info("Creando configuración por defecto")
            settings = self._get_default_settings()
            self._save_settings(settings)
            return settings
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Retorna la configuración por defecto"""
        return {
            'version': '2.0',
            'active_profile': 'default',
            'theme': 'dark',
            'language': 'es',
            'auto_save': {
                'enabled': True,
                'interval': 300  # 5 minutos
            },
            'ui': {
                'window_size': '1200x700',
                'window_position': None,
                'sidebar_width': 320,
                'font_scale': 1.0,
                'show_tooltips': True,
                'animations_enabled': True
            },
            'editor': {
                'font_family': 'Georgia',
                'font_size': 12,
                'line_spacing': 1.5,
                'spell_check': True,
                'auto_complete': True,
                'highlight_citations': True,
                'word_wrap': True
            },
            'document': {
                'default_format': {
                    'font': 'Times New Roman',
                    'size': 12,
                    'line_spacing': 2.0,
                    'margins': 2.54,
                    'justify': True,
                    'first_line_indent': True
                },
                'include_header': True,
                'include_footer': True,
                'page_numbers': True,
                'watermark': {
                    'enabled': True,
                    'opacity': 0.3,
                    'mode': 'watermark'
                }
            },
            'citations': {
                'default_style': 'APA',
                'auto_format': True,
                'check_consistency': True
            },
            'validation': {
                'min_section_words': 50,
                'required_sections': ['introduccion', 'objetivos', 'marco_teorico', 'metodologia', 'conclusiones'],
                'check_grammar': True,
                'check_plagiarism': False
            },
            'recent_files': [],
            'recent_projects': [],
            'shortcuts': self._get_default_shortcuts(),
            'plugins': {
                'enabled': [],
                'settings': {}
            },
            'advanced': {
                'debug_mode': False,
                'log_level': 'INFO',
                'cache_size': 100,
                'backup_count': 5
            },
            'statistics': {
                'projects_created': 0,
                'documents_generated': 0,
                'total_words_written': 0,
                'app_usage_hours': 0.0,
                'favorite_sections': {}
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_default_shortcuts(self) -> Dict[str, str]:
        """Retorna atajos de teclado por defecto"""
        return {
            'save_project': 'Ctrl+S',
            'load_project': 'Ctrl+O',
            'new_project': 'Ctrl+N',
            'generate_document': 'F9',
            'validate_project': 'F5',
            'show_help': 'F1',
            'toggle_preview': 'F4',
            'undo': 'Ctrl+Z',
            'redo': 'Ctrl+Y',
            'find': 'Ctrl+F',
            'replace': 'Ctrl+H',
            'bold': 'Ctrl+B',
            'italic': 'Ctrl+I',
            'insert_citation': 'Ctrl+Shift+C',
            'zoom_in': 'Ctrl+Plus',
            'zoom_out': 'Ctrl+Minus',
            'reset_zoom': 'Ctrl+0'
        }
    
    def _save_settings(self, settings: Dict[str, Any]):
        """Guarda la configuración en disco"""
        try:
            settings['last_updated'] = datetime.now().isoformat()
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            logger.info("Configuración guardada exitosamente")
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    # Métodos públicos para gestión de configuración
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración
        
        Args:
            key: Clave de configuración (soporta notación punto: 'ui.theme')
            default: Valor por defecto si no existe
            
        Returns:
            Valor de configuración o default
        """
        keys = key.split('.')
        value = self.current_settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Establece un valor de configuración
        
        Args:
            key: Clave de configuración (soporta notación punto)
            value: Valor a establecer
        """
        keys = key.split('.')
        settings = self.current_settings
        
        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        
        # Establecer el valor
        settings[keys[-1]] = value
        
        # Guardar cambios
        self._save_settings(self.current_settings)
        logger.debug(f"Configuración actualizada: {key} = {value}")
    
    def update(self, updates: Dict[str, Any]):
        """
        Actualiza múltiples valores de configuración
        
        Args:
            updates: Diccionario con actualizaciones
        """
        def deep_update(base: dict, updates: dict):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(self.current_settings, updates)
        self._save_settings(self.current_settings)
        logger.info(f"Configuración actualizada con {len(updates)} cambios")
    
    def reset_to_defaults(self, section: Optional[str] = None):
        """
        Restablece configuración a valores por defecto
        
        Args:
            section: Sección específica a restablecer (None = toda la configuración)
        """
        defaults = self._get_default_settings()
        
        if section:
            if section in defaults:
                self.current_settings[section] = defaults[section]
                logger.info(f"Sección '{section}' restablecida a valores por defecto")
            else:
                logger.warning(f"Sección '{section}' no encontrada")
        else:
            # Preservar algunos valores
            preserved = {
                'recent_files': self.current_settings.get('recent_files', []),
                'recent_projects': self.current_settings.get('recent_projects', []),
                'statistics': self.current_settings.get('statistics', {})
            }
            
            self.current_settings = defaults
            self.current_settings.update(preserved)
            logger.info("Configuración completa restablecida a valores por defecto")
        
        self._save_settings(self.current_settings)
    
    # Gestión de perfiles
    
    def create_profile(self, name: str, base_on_current: bool = True) -> bool:
        """
        Crea un nuevo perfil de configuración
        
        Args:
            name: Nombre del perfil
            base_on_current: Si basar en la configuración actual
            
        Returns:
            bool: True si se creó exitosamente
        """
        profile_file = self.profiles_dir / f"{name}.json"
        
        if profile_file.exists():
            logger.warning(f"El perfil '{name}' ya existe")
            return False
        
        try:
            if base_on_current:
                profile_settings = self.current_settings.copy()
            else:
                profile_settings = self._get_default_settings()
            
            profile_settings['profile_name'] = name
            profile_settings['created_at'] = datetime.now().isoformat()
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_settings, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Perfil '{name}' creado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando perfil: {e}")
            return False
    
    def load_profile(self, name: str) -> bool:
        """
        Carga un perfil de configuración
        
        Args:
            name: Nombre del perfil
            
        Returns:
            bool: True si se cargó exitosamente
        """
        profile_file = self.profiles_dir / f"{name}.json"
        
        if not profile_file.exists():
            logger.warning(f"El perfil '{name}' no existe")
            return False
        
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_settings = json.load(f)
            
            # Preservar estadísticas y archivos recientes
            preserved = {
                'recent_files': self.current_settings.get('recent_files', []),
                'recent_projects': self.current_settings.get('recent_projects', []),
                'statistics': self.current_settings.get('statistics', {})
            }
            
            self.current_settings = profile_settings
            self.current_settings.update(preserved)
            self.current_settings['active_profile'] = name
            self.current_profile = name
            
            self._save_settings(self.current_settings)
            logger.info(f"Perfil '{name}' cargado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando perfil: {e}")
            return False
    
    def delete_profile(self, name: str) -> bool:
        """
        Elimina un perfil
        
        Args:
            name: Nombre del perfil
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        if name == 'default':
            logger.warning("No se puede eliminar el perfil por defecto")
            return False
        
        profile_file = self.profiles_dir / f"{name}.json"
        
        if not profile_file.exists():
            logger.warning(f"El perfil '{name}' no existe")
            return False
        
        try:
            profile_file.unlink()
            
            # Si es el perfil activo, cambiar a default
            if self.current_profile == name:
                self.load_profile('default')
            
            logger.info(f"Perfil '{name}' eliminado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando perfil: {e}")
            return False
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        Lista todos los perfiles disponibles
        
        Returns:
            Lista de información de perfiles
        """
        profiles = []
        
        # Perfil default siempre existe
        profiles.append({
            'name': 'default',
            'active': self.current_profile == 'default',
            'created_at': None
        })
        
        # Perfiles personalizados
        for profile_file in self.profiles_dir.glob('*.json'):
            try:
                name = profile_file.stem
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                profiles.append({
                    'name': name,
                    'active': self.current_profile == name,
                    'created_at': data.get('created_at')
                })
            except Exception as e:
                logger.error(f"Error leyendo perfil {profile_file}: {e}")
        
        return profiles
    
    # Gestión de archivos recientes
    
    def add_recent_file(self, filepath: str, file_type: str = 'project'):
        """
        Agrega un archivo a la lista de recientes
        
        Args:
            filepath: Ruta del archivo
            file_type: Tipo de archivo ('project' o 'document')
        """
        recent_list = 'recent_projects' if file_type == 'project' else 'recent_files'
        recent = self.current_settings.get(recent_list, [])
        
        # Crear entrada
        entry = {
            'path': filepath,
            'name': os.path.basename(filepath),
            'accessed': datetime.now().isoformat()
        }
        
        # Remover si ya existe
        recent = [r for r in recent if r.get('path') != filepath]
        
        # Agregar al inicio
        recent.insert(0, entry)
        
        # Limitar a 10 elementos
        recent = recent[:10]
        
        self.set(recent_list, recent)
        logger.debug(f"Archivo agregado a recientes: {filepath}")
    
    def get_recent_files(self, file_type: str = 'project') -> List[Dict[str, str]]:
        """
        Obtiene la lista de archivos recientes
        
        Args:
            file_type: Tipo de archivo
            
        Returns:
            Lista de archivos recientes
        """
        recent_list = 'recent_projects' if file_type == 'project' else 'recent_files'
        return self.get(recent_list, [])
    
    def clear_recent_files(self, file_type: Optional[str] = None):
        """
        Limpia la lista de archivos recientes
        
        Args:
            file_type: Tipo específico o None para todos
        """
        if file_type:
            recent_list = 'recent_projects' if file_type == 'project' else 'recent_files'
            self.set(recent_list, [])
        else:
            self.set('recent_files', [])
            self.set('recent_projects', [])
        
        logger.info("Lista de archivos recientes limpiada")
    
    # Estadísticas de uso
    
    def update_statistics(self, stat_name: str, value: Any = 1):
        """
        Actualiza una estadística de uso
        
        Args:
            stat_name: Nombre de la estadística
            value: Valor a agregar (o establecer si no es numérico)
        """
        stats = self.current_settings.get('statistics', {})
        
        if stat_name in stats and isinstance(stats[stat_name], (int, float)):
            stats[stat_name] += value
        else:
            stats[stat_name] = value
        
        self.set('statistics', stats)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene todas las estadísticas de uso"""
        return self.get('statistics', {})
    
    # Exportar/Importar configuración
    
    def export_settings(self, filepath: str, include_profiles: bool = True) -> bool:
        """
        Exporta toda la configuración
        
        Args:
            filepath: Ruta del archivo de exportación
            include_profiles: Si incluir perfiles
            
        Returns:
            bool: True si se exportó exitosamente
        """
        try:
            export_data = {
                'version': self.current_settings.get('version'),
                'settings': self.current_settings,
                'exported_at': datetime.now().isoformat()
            }
            
            if include_profiles:
                profiles = {}
                for profile_file in self.profiles_dir.glob('*.json'):
                    try:
                        with open(profile_file, 'r', encoding='utf-8') as f:
                            profiles[profile_file.stem] = json.load(f)
                    except:
                        pass
                export_data['profiles'] = profiles
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Configuración exportada a: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando configuración: {e}")
            return False
    
    def import_settings(self, filepath: str, merge: bool = False) -> bool:
        """
        Importa configuración desde archivo
        
        Args:
            filepath: Ruta del archivo
            merge: Si combinar con configuración actual
            
        Returns:
            bool: True si se importó exitosamente
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'settings' not in import_data:
                logger.error("Archivo de importación inválido")
                return False
            
            # Backup actual
            backup_file = self.config_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(self.settings_file, backup_file)
            
            if merge:
                # Combinar configuraciones
                self.update(import_data['settings'])
            else:
                # Reemplazar configuración
                preserved = {
                    'recent_files': self.current_settings.get('recent_files', []),
                    'recent_projects': self.current_settings.get('recent_projects', []),
                    'statistics': self.current_settings.get('statistics', {})
                }
                
                self.current_settings = import_data['settings']
                self.current_settings.update(preserved)
                self._save_settings(self.current_settings)
            
            # Importar perfiles si existen
            if 'profiles' in import_data:
                for name, profile_data in import_data['profiles'].items():
                    profile_file = self.profiles_dir / f"{name}.json"
                    with open(profile_file, 'w', encoding='utf-8') as f:
                        json.dump(profile_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Configuración importada desde: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error importando configuración: {e}")
            return False
    
    # Métodos de utilidad
    
    def get_config_info(self) -> Dict[str, Any]:
        """Obtiene información sobre la configuración"""
        return {
            'config_dir': str(self.config_dir),
            'settings_file': str(self.settings_file),
            'profiles_dir': str(self.profiles_dir),
            'current_profile': self.current_profile,
            'profiles_count': len(list(self.profiles_dir.glob('*.json'))),
            'settings_size': self.settings_file.stat().st_size if self.settings_file.exists() else 0,
            'last_updated': self.current_settings.get('last_updated')
        }
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """
        Limpia backups antiguos
        
        Args:
            keep_count: Número de backups a mantener
        """
        backup_files = sorted(self.config_dir.glob('backup_*.json'), 
                            key=lambda f: f.stat().st_mtime, 
                            reverse=True)
        
        for backup in backup_files[keep_count:]:
            try:
                backup.unlink()
                logger.debug(f"Backup eliminado: {backup.name}")
            except Exception as e:
                logger.error(f"Error eliminando backup: {e}")


# Singleton global
_settings_manager = None

def get_settings_manager() -> UserSettingsManager:
    """Obtiene la instancia singleton del gestor de configuración"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = UserSettingsManager()
    return _settings_manager