"""
Sistema de logging mejorado para el proyecto
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
import threading

class ProjectLogger:
    """Gestor de logging singleton con configuración avanzada"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.setup_logger()
    
    def setup_logger(self):
        """Configura el sistema de logging con rotación y múltiples handlers"""
        try:
            # Crear directorio de logs si no existe
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            # Configurar formato detallado
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            formatter = logging.Formatter(log_format)
            
            # Logger principal
            self.logger = logging.getLogger('ProyectoAcademico')
            self.logger.setLevel(logging.DEBUG)
            
            # Limpiar handlers existentes
            self.logger.handlers.clear()
            
            # Handler para archivo principal con rotación por tamaño
            main_handler = RotatingFileHandler(
                log_dir / 'proyecto_academico.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=10,
                encoding='utf-8'
            )
            main_handler.setLevel(logging.DEBUG)
            main_handler.setFormatter(formatter)
            
            # Handler para errores críticos con rotación diaria
            error_handler = TimedRotatingFileHandler(
                log_dir / 'errors.log',
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            
            # Handler para consola con nivel configurable
            console_handler = logging.StreamHandler(sys.stdout)
            console_level = os.getenv('LOG_LEVEL', 'INFO').upper()
            console_handler.setLevel(getattr(logging, console_level, logging.INFO))
            
            # Formato más simple para consola
            console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            console_formatter = logging.Formatter(console_format)
            console_handler.setFormatter(console_formatter)
            
            # Agregar handlers
            self.logger.addHandler(main_handler)
            self.logger.addHandler(error_handler)
            self.logger.addHandler(console_handler)
            
            # Log inicial
            self.logger.info("Sistema de logging inicializado correctamente")
            
        except Exception as e:
            # Fallback a logging básico
            logging.basicConfig(level=logging.INFO)
            logging.error(f"Error configurando logger avanzado: {e}")
    
    def get_logger(self, module_name):
        """Obtiene un logger para un módulo específico"""
        return logging.getLogger(f'ProyectoAcademico.{module_name}')
    
    def set_level(self, level):
        """Cambia el nivel de logging globalmente"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level)

# Singleton global
project_logger = ProjectLogger()

# Funciones de conveniencia mejoradas
def get_logger(module_name):
    """Obtiene un logger para un módulo"""
    return project_logger.get_logger(module_name)

def log_error(module_name, error, context="", exc_info=True):
    """Registra un error con contexto detallado"""
    logger = get_logger(module_name)
    if context:
        logger.error(f"{context}: {str(error)}", exc_info=exc_info)
    else:
        logger.error(str(error), exc_info=exc_info)

def log_action(module_name, action, details="", level="INFO"):
    """Registra una acción del usuario con nivel configurable"""
    logger = get_logger(module_name)
    message = f"Acción: {action}"
    if details:
        message += f" - {details}"
    
    getattr(logger, level.lower())(message)

def log_performance(module_name, operation, duration, details=""):
    """Registra métricas de rendimiento"""
    logger = get_logger(module_name)
    message = f"Performance: {operation} - {duration:.3f}s"
    if details:
        message += f" - {details}"
    logger.info(message)

def configure_module_logging(module_name, level=logging.INFO):
    """Configura nivel de logging específico por módulo"""
    logger = logging.getLogger(f'ProyectoAcademico.{module_name}')
    logger.setLevel(level)
    return logger

def get_log_files():
    """Retorna lista de archivos de log disponibles"""
    log_dir = Path('logs')
    if log_dir.exists():
        return list(log_dir.glob('*.log'))
    return []

def cleanup_old_logs(days=30):
    """Limpia logs antiguos"""
    try:
        log_dir = Path('logs')
        if not log_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        for log_file in log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                
        get_logger('logger').info(f"Limpieza de logs completada - archivos > {days} días eliminados")
        
    except Exception as e:
        get_logger('logger').error(f"Error en limpieza de logs: {e}")