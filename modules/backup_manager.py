"""
Sistema de backup automático con versionado - Versión Completa
"""

import os
import json
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from typing import Dict, List, Optional, Union
from utils.logger import get_logger
from config.settings import AUTOSAVE_CONFIG

logger = get_logger('BackupManager')

class BackupManager:
    """Gestor de backups con versionado y compresión avanzada"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.versions_file = self.backup_dir / "versions.json"
        self.versions = self._load_versions()
        
        # Configuración avanzada
        self.max_backups = AUTOSAVE_CONFIG.get('max_backups', 20)
        self.compression_level = zipfile.ZIP_DEFLATED
        self.auto_backup_interval = 3600  # 1 hora
        self.max_backup_size = 100 * 1024 * 1024  # 100MB
        
        logger.info(f"BackupManager inicializado en: {self.backup_dir}")
    
    def _load_versions(self) -> Dict:
        """Carga el registro de versiones con validación"""
        if self.versions_file.exists():
            try:
                with open(self.versions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Validar estructura
                if isinstance(data, dict) and 'versions' in data:
                    return data
                else:
                    logger.warning("Archivo de versiones inválido, creando nuevo")
                    
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error cargando versiones: {e}")
        
        return {
            'versions': [],
            'current_version': 0,
            'last_backup': None,
            'total_backups': 0,
            'total_size': 0
        }
    
    def _save_versions(self):
        """Guarda el registro de versiones con manejo de errores"""
        try:
            # Crear backup del archivo de versiones
            if self.versions_file.exists():
                backup_versions = self.versions_file.with_suffix('.json.bak')
                shutil.copy2(self.versions_file, backup_versions)
            
            with open(self.versions_file, 'w', encoding='utf-8') as f:
                json.dump(self.versions, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando versiones: {e}")
            # Intentar restaurar backup
            backup_versions = self.versions_file.with_suffix('.json.bak')
            if backup_versions.exists():
                shutil.copy2(backup_versions, self.versions_file)
    
    def create_backup(self, project_data: Dict, backup_type: str = "auto", 
                     description: str = "", include_attachments: bool = True) -> Optional[str]:
        """
        Crea un backup completo del proyecto
        
        Args:
            project_data: Datos del proyecto a respaldar
            backup_type: Tipo de backup ('auto', 'manual', 'milestone', 'daily')
            description: Descripción opcional del backup
            include_attachments: Si incluir archivos adjuntos
            
        Returns:
            Ruta del backup creado o None si falla
        """
        try:
            # Validar datos de entrada
            if not isinstance(project_data, dict):
                raise ValueError("project_data debe ser un diccionario")
            
            # Incrementar versión
            self.versions['current_version'] += 1
            version = self.versions['current_version']
            
            # Crear nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_v{version:04d}_{timestamp}_{backup_type}.zip"
            backup_path = self.backup_dir / filename
            
            # Verificar espacio disponible
            if not self._check_disk_space(backup_path.parent):
                raise IOError("Espacio insuficiente en disco")
            
            # Crear backup comprimido
            total_size = 0
            with zipfile.ZipFile(backup_path, 'w', self.compression_level, compresslevel=9) as zf:
                
                # Guardar datos principales del proyecto
                project_json = json.dumps(project_data, indent=2, ensure_ascii=False)
                zf.writestr('project_data.json', project_json)
                total_size += len(project_json.encode('utf-8'))
                
                # Crear y guardar metadatos completos
                metadata = {
                    'version': version,
                    'timestamp': datetime.now().isoformat(),
                    'type': backup_type,
                    'description': description,
                    'checksum': hashlib.sha256(project_json.encode('utf-8')).hexdigest(),
                    'size': len(project_json),
                    'created_by': 'ProyectoAcademico v2.1.0',
                    'compression': 'ZIP_DEFLATED',
                    'includes_attachments': include_attachments,
                    'project_title': project_data.get('informacion_general', {}).get('titulo', 'Sin título'),
                    'sections_count': len(project_data.get('secciones_activas', [])),
                    'references_count': len(project_data.get('referencias', []))
                }
                
                metadata_json = json.dumps(metadata, indent=2, ensure_ascii=False)
                zf.writestr('metadata.json', metadata_json)
                total_size += len(metadata_json.encode('utf-8'))
                
                # Incluir archivos adjuntos si están disponibles
                if include_attachments and 'imagenes' in project_data:
                    total_size += self._add_attachments_to_backup(zf, project_data['imagenes'])
                
                # Agregar archivos adicionales si existen
                if 'archivos_adjuntos' in project_data:
                    for archivo_path in project_data['archivos_adjuntos']:
                        if isinstance(archivo_path, str) and os.path.exists(archivo_path):
                            try:
                                file_size = os.path.getsize(archivo_path)
                                if file_size < self.max_backup_size:  # Límite de tamaño por archivo
                                    zf.write(archivo_path, f"attachments/{os.path.basename(archivo_path)}")
                                    total_size += file_size
                                else:
                                    logger.warning(f"Archivo muy grande omitido: {archivo_path}")
                            except Exception as e:
                                logger.warning(f"Error agregando archivo {archivo_path}: {e}")
                
                # Agregar configuración del sistema
                system_config = {
                    'app_version': '2.1.0',
                    'backup_created': datetime.now().isoformat(),
                    'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                    'platform': os.name
                }
                zf.writestr('system_config.json', json.dumps(system_config, indent=2))
            
            # Validar que el backup se creó correctamente
            if not backup_path.exists() or backup_path.stat().st_size == 0:
                raise IOError("El backup no se creó correctamente")
            
            # Actualizar registro de versiones
            backup_info = {
                'version': version,
                'filename': filename,
                'path': str(backup_path),
                'timestamp': datetime.now().isoformat(),
                'type': backup_type,
                'description': description,
                'size': backup_path.stat().st_size,
                'checksum': self._calculate_file_checksum(backup_path),
                'compressed_size': total_size,
                'project_title': metadata.get('project_title', 'Sin título')
            }
            
            self.versions['versions'].append(backup_info)
            self.versions['last_backup'] = datetime.now().isoformat()
            self.versions['total_backups'] += 1
            self.versions['total_size'] += backup_path.stat().st_size
            
            # Guardar registro actualizado
            self._save_versions()
            
            # Limpiar backups antiguos si es necesario
            self._cleanup_old_backups()
            
            logger.info(f"Backup creado exitosamente: {backup_path} ({self._format_size(backup_path.stat().st_size)})")
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}", exc_info=True)
            
            # Limpiar archivo parcial si existe
            if 'backup_path' in locals() and backup_path.exists():
                try:
                    backup_path.unlink()
                except:
                    pass
            
            return None
    
    def restore_backup(self, backup_path: Union[str, Path]) -> Optional[Dict]:
        """
        Restaura un proyecto desde un backup
        
        Args:
            backup_path: Ruta al archivo de backup
            
        Returns:
            Datos del proyecto restaurado o None si falla
        """
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup no encontrado: {backup_path}")
            
            logger.info(f"Restaurando backup: {backup_path}")
            
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # Verificar estructura del backup
                required_files = ['project_data.json', 'metadata.json']
                available_files = zf.namelist()
                
                for required_file in required_files:
                    if required_file not in available_files:
                        raise ValueError(f"Backup inválido: falta {required_file}")
                
                # Cargar metadatos
                metadata_content = zf.read('metadata.json').decode('utf-8')
                metadata = json.loads(metadata_content)
                
                # Verificar integridad
                project_content = zf.read('project_data.json').decode('utf-8')
                calculated_checksum = hashlib.sha256(project_content.encode('utf-8')).hexdigest()
                
                if metadata.get('checksum') != calculated_checksum:
                    logger.warning("El checksum del backup no coincide, el archivo puede estar corrupto")
                
                # Cargar datos del proyecto
                project_data = json.loads(project_content)
                
                # Restaurar archivos adjuntos si existen
                if metadata.get('includes_attachments', False):
                    self._restore_attachments_from_backup(zf, project_data)
                
                logger.info(f"Backup restaurado exitosamente desde {backup_path}")
                
                return {
                    'project_data': project_data,
                    'metadata': metadata,
                    'restored_from': str(backup_path),
                    'restored_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}", exc_info=True)
            return None
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict]:
        """
        Lista todos los backups disponibles
        
        Args:
            backup_type: Filtrar por tipo de backup (opcional)
            
        Returns:
            Lista de información de backups
        """
        try:
            backups = self.versions.get('versions', [])
            
            if backup_type:
                backups = [b for b in backups if b.get('type') == backup_type]
            
            # Verificar que los archivos aún existen
            valid_backups = []
            for backup in backups:
                backup_path = Path(backup.get('path', ''))
                if backup_path.exists():
                    # Agregar información adicional
                    backup_copy = backup.copy()
                    backup_copy['size_formatted'] = self._format_size(backup.get('size', 0))
                    backup_copy['age_days'] = self._calculate_age_days(backup.get('timestamp'))
                    valid_backups.append(backup_copy)
                else:
                    logger.warning(f"Backup no encontrado: {backup_path}")
            
            return sorted(valid_backups, key=lambda x: x.get('timestamp', ''), reverse=True)
            
        except Exception as e:
            logger.error(f"Error listando backups: {e}")
            return []
    
    def delete_backup(self, version: int) -> bool:
        """
        Elimina un backup específico
        
        Args:
            version: Número de versión del backup a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            backups = self.versions.get('versions', [])
            backup_to_delete = None
            
            for i, backup in enumerate(backups):
                if backup.get('version') == version:
                    backup_to_delete = backup
                    backup_index = i
                    break
            
            if not backup_to_delete:
                logger.warning(f"Backup versión {version} no encontrado")
                return False
            
            # Eliminar archivo
            backup_path = Path(backup_to_delete.get('path', ''))
            if backup_path.exists():
                backup_path.unlink()
                logger.info(f"Archivo de backup eliminado: {backup_path}")
            
            # Actualizar registro
            self.versions['versions'].pop(backup_index)
            self.versions['total_backups'] -= 1
            self.versions['total_size'] -= backup_to_delete.get('size', 0)
            
            self._save_versions()
            
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando backup: {e}")
            return False
    
    def get_backup_statistics(self) -> Dict:
        """Obtiene estadísticas de backups"""
        try:
            backups = self.versions.get('versions', [])
            
            if not backups:
                return {
                    'total_backups': 0,
                    'total_size': 0,
                    'total_size_formatted': '0 B',
                    'oldest_backup': None,
                    'newest_backup': None,
                    'backup_types': {}
                }
            
            # Calcular estadísticas
            total_size = sum(b.get('size', 0) for b in backups)
            backup_types = {}
            
            for backup in backups:
                backup_type = backup.get('type', 'unknown')
                backup_types[backup_type] = backup_types.get(backup_type, 0) + 1
            
            oldest = min(backups, key=lambda x: x.get('timestamp', ''))
            newest = max(backups, key=lambda x: x.get('timestamp', ''))
            
            return {
                'total_backups': len(backups),
                'total_size': total_size,
                'total_size_formatted': self._format_size(total_size),
                'oldest_backup': oldest.get('timestamp'),
                'newest_backup': newest.get('timestamp'),
                'backup_types': backup_types,
                'average_size': total_size // len(backups) if backups else 0,
                'average_size_formatted': self._format_size(total_size // len(backups) if backups else 0)
            }
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas: {e}")
            return {}
    
    # ==================== MÉTODOS PRIVADOS ====================
    
    def _add_attachments_to_backup(self, zipfile_obj: zipfile.ZipFile, imagenes: Dict) -> int:
        """Agrega archivos de imágenes al backup"""
        total_size = 0
        
        for key, path in imagenes.items():
            if isinstance(path, str) and os.path.exists(path):
                try:
                    file_size = os.path.getsize(path)
                    if file_size < 50 * 1024 * 1024:  # Límite de 50MB por imagen
                        zipfile_obj.write(path, f"images/{key}_{os.path.basename(path)}")
                        total_size += file_size
                    else:
                        logger.warning(f"Imagen muy grande omitida: {path}")
                except Exception as e:
                    logger.warning(f"Error agregando imagen {path}: {e}")
        
        return total_size
    
    def _restore_attachments_from_backup(self, zipfile_obj: zipfile.ZipFile, project_data: Dict):
        """Restaura archivos adjuntos desde el backup"""
        try:
            # Crear directorio temporal para imágenes restauradas
            restore_dir = Path('restored_images')
            restore_dir.mkdir(exist_ok=True)
            
            # Extraer imágenes
            for file_info in zipfile_obj.filelist:
                if file_info.filename.startswith('images/'):
                    extracted_path = restore_dir / os.path.basename(file_info.filename)
                    with zipfile_obj.open(file_info) as source, open(extracted_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    logger.info(f"Imagen restaurada: {extracted_path}")
            
        except Exception as e:
            logger.warning(f"Error restaurando archivos adjuntos: {e}")
    
    def _cleanup_old_backups(self):
        """Limpia backups antiguos según la configuración"""
        try:
            backups = self.versions.get('versions', [])
            
            if len(backups) <= self.max_backups:
                return
            
            # Ordenar por timestamp (más antiguos primero)
            backups_sorted = sorted(backups, key=lambda x: x.get('timestamp', ''))
            
            # Eliminar excedentes
            to_delete = backups_sorted[:-self.max_backups]
            
            for backup in to_delete:
                self.delete_backup(backup.get('version'))
            
            logger.info(f"Limpieza completada: {len(to_delete)} backups antiguos eliminados")
            
        except Exception as e:
            logger.error(f"Error en limpieza de backups: {e}")
    
    def _check_disk_space(self, path: Path, min_space_mb: int = 100) -> bool:
        """Verifica que hay suficiente espacio en disco"""
        try:
            stat = shutil.disk_usage(path)
            free_space_mb = stat.free / (1024 * 1024)
            return free_space_mb >= min_space_mb
        except Exception as e:
            logger.warning(f"No se pudo verificar espacio en disco: {e}")
            return True  # Asumir que hay espacio si no se puede verificar
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcula checksum SHA256 de un archivo"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Error calculando checksum: {e}")
            return ""
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatea tamaño en bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _calculate_age_days(self, timestamp_str: str) -> int:
        """Calcula la edad en días de un backup"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age = datetime.now() - timestamp.replace(tzinfo=None)
            return age.days
        except Exception:
            return 0