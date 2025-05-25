"""
Configuración centralizada del proyecto - Versión Corregida
"""

import os
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("settings")

# Configuración de la aplicación
APP_CONFIG = {
    'name': 'Generador de Proyectos Académicos',
    'version': '2.1.0',
    'window_size': '1200x700',
    'min_window_size': (1000, 600),
    'theme': 'dark',
    'color_theme': 'blue',
    'author': 'xZoluGames',
    'description': 'Generador profesional de proyectos académicos con formato Word'
}

# Configuración de auto-guardado
AUTOSAVE_CONFIG = {
    'enabled': True,
    'interval': 300000,  # 5 minutos en milisegundos
    'filename': 'auto_save.json',
    'backup_dir': 'backups',
    'max_backups': 10
}

# Configuración de formato por defecto (estándar académico)
DEFAULT_FORMAT = {
    'fuente_texto': 'Times New Roman',
    'tamaño_texto': 12,
    'fuente_titulo': 'Times New Roman',
    'tamaño_titulo': 14,
    'interlineado': 2.0,
    'margen': 2.54,  # Margen estándar en cm
    'justificado': True,
    'sangria': True,
    'sangria_primera_linea': 1.27  # 0.5 pulgadas en cm
}

# Configuración de validación
VALIDATION_CONFIG = {
    'min_section_length': 50,
    'min_references': 3,
    'max_references': 100,
    'required_fields': ['titulo', 'estudiantes', 'tutores'],
    'optional_fields': ['institucion', 'curso', 'enfasis', 'director'],
    'min_words_project': 1000,
    'max_words_project': 50000
}

# Rutas de recursos
RESOURCES_PATHS = {
    'images': 'resources/images',
    'templates': 'plantillas',
    'exports': 'exports',
    'cache': 'cache',
    'logs': 'logs',
    'backups': 'backups'
}

# Colores corregidos para botones
BUTTON_COLORS = {
    'default': {'fg': None, 'hover': None},
    'green': {'fg': '#228B22', 'hover': '#006400'},
    'darkgreen': {'fg': '#006400', 'hover': '#004000'},
    'blue': {'fg': '#4682B4', 'hover': '#191970'},
    'darkblue': {'fg': '#191970', 'hover': '#000080'},
    'purple': {'fg': '#9370DB', 'hover': '#7B68EE'},
    'darkpurple': {'fg': '#7B68EE', 'hover': '#6A5ACD'},
    'orange': {'fg': '#FF8C00', 'hover': '#FF6347'},
    'darkorange': {'fg': '#FF6347', 'hover': '#FF4500'},
    'red': {'fg': '#DC143C', 'hover': '#8B0000'},
    'darkred': {'fg': '#8B0000', 'hover': '#640000'},
    'indigo': {'fg': '#4B0082', 'hover': '#8B008B'},
    'darkindigo': {'fg': '#8B008B', 'hover': '#800080'},
    'gray': {'fg': '#808080', 'hover': '#696969'},
    'success': {'fg': '#28a745', 'hover': '#218838'},
    'warning': {'fg': '#ffc107', 'hover': '#e0a800'},
    'danger': {'fg': '#dc3545', 'hover': '#c82333'},
    'info': {'fg': '#17a2b8', 'hover': '#138496'}
}

# Secciones que permiten citas
CITATION_SECTIONS = [
    'marco_teorico', 
    'introduccion', 
    'desarrollo', 
    'discusion',
    'antecedentes',
    'fundamentacion_teorica'
]

# Límites de texto por sección
TEXT_LIMITS = {
    'resumen_min': 150,
    'resumen_max': 300,
    'titulo_max': 200,
    'titulo_min': 10,
    'palabras_proyecto_min': 1000,
    'palabras_proyecto_max': 50000,
    'introduccion_min': 200,
    'objetivos_min': 100,
    'metodologia_min': 150,
    'conclusiones_min': 200
}

# Colores de la interfaz
UI_COLORS = {
    'primary': '#4682B4',      # Steel Blue
    'secondary': '#6c757d',    # Gray
    'success': '#228B22',      # Forest Green
    'danger': '#DC143C',       # Crimson
    'warning': '#FFA500',      # Orange
    'info': '#4B0082',         # Indigo
    'light': '#f8f9fa',        # Light Gray
    'dark': '#343a40',         # Dark Gray
    'background': {
        'dark': '#212121',
        'medium': '#424242',
        'light': '#616161'
    },
    'text': {
        'primary': '#FFFFFF',
        'secondary': '#B0B0B0',
        'disabled': '#707070',
        'muted': '#6c757d'
    },
    'border': {
        'primary': '#dee2e6',
        'secondary': '#e9ecef'
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_size_mb': 10,
    'backup_count': 10,
    'console_level': 'INFO'
}

# Tipos de archivos soportados
SUPPORTED_FILE_TYPES = {
    'images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
    'documents': ['.docx', '.pdf', '.txt'],
    'projects': ['.json'],
    'exports': ['.docx', '.pdf'],
    'templates': ['.docx', '.json']
}

# Configuración de exportación
EXPORT_CONFIG = {
    'default_format': 'docx',
    'include_metadata': True,
    'compress_images': True,
    'max_image_size': (1920, 1080),
    'quality': 85
}

# Plantillas predefinidas
TEMPLATE_CONFIGS = {
    'academico_basico': {
        'name': 'Académico Básico',
        'sections': ['introduccion', 'objetivos', 'metodologia', 'desarrollo', 'conclusiones'],
        'required_fields': ['titulo', 'estudiantes', 'tutores'],
        'format': DEFAULT_FORMAT
    },
    'tesis_pregrado': {
        'name': 'Tesis de Pregrado',
        'sections': ['resumen', 'introduccion', 'marco_teorico', 'metodologia', 'resultados', 'discusion', 'conclusiones'],
        'required_fields': ['titulo', 'estudiantes', 'tutores', 'director'],
        'min_words': 5000
    },
    'proyecto_investigacion': {
        'name': 'Proyecto de Investigación',
        'sections': ['planteamiento', 'objetivos', 'justificacion', 'marco_teorico', 'metodologia', 'cronograma'],
        'required_fields': ['titulo', 'investigadores', 'director'],
        'min_words': 3000
    }
}

# Funciones de utilidad para configuración
def get_resource_path(resource_type):
    """Obtiene la ruta absoluta de un tipo de recurso"""
    try:
        base_path = Path(__file__).parent.parent
        return base_path / RESOURCES_PATHS.get(resource_type, '')
    except Exception as e:
        logger.error(f"Error obteniendo ruta de recurso {resource_type}: {e}")
        return Path('.')

def ensure_directories():
    """Crea los directorios necesarios si no existen"""
    try:
        for resource_type in RESOURCES_PATHS.values():
            path = get_resource_path(resource_type)
            path.mkdir(parents=True, exist_ok=True)
        logger.info("Directorios de recursos verificados/creados")
    except Exception as e:
        logger.error(f"Error creando directorios: {e}")

def get_button_color(color_name, variant='fg'):
    """Obtiene un color de botón de forma segura"""
    if color_name in BUTTON_COLORS:
        return BUTTON_COLORS[color_name].get(variant)
    return BUTTON_COLORS['default'][variant]

def validate_config():
    """Valida la configuración al inicio"""
    errors = []
    
    # Validar colores
    for color_name, color_data in BUTTON_COLORS.items():
        if not isinstance(color_data, dict):
            errors.append(f"Color {color_name} mal configurado")
    
    # Validar límites
    for limit_name, limit_value in TEXT_LIMITS.items():
        if not isinstance(limit_value, (int, float)) or limit_value < 0:
            errors.append(f"Límite {limit_name} inválido")
    
    if errors:
        logger.warning(f"Errores en configuración: {errors}")
    else:
        logger.info("Configuración validada correctamente")
    
    return len(errors) == 0

# Inicialización
if __name__ != "__main__":
    ensure_directories()
    validate_config()