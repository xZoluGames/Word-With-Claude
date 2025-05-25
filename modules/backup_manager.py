"""
Sistema de backup automático con versionado
Gestiona copias de seguridad incrementales y completas
"""

import os
import json
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from typing import Dict, List, Optional
from utils.logger import get_logger
from config.settings import AUTOSAVE_CONFIG

logger = get_logger('BackupManager')

class BackupManager:
    """Gestor de backups con versionado"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.versions_file = self.backup_dir / "versions.json"
        self.versions = self._load_versions()
        
        # Configuración
        self.max_backups = 20
        self.compression_level = zipfile.ZIP_DEFLATED
        self.auto_backup_interval = 3600  # 1 hora
        
        logger.info(f"BackupManager inicializado en: {self.backup_dir}")
    
    def _load_versions(self) -> Dict:
        """Carga el registro de versiones"""
        if self.versions_file.exists():
            try:
                with open(self.versions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando versiones: {e}")
        
        return {
            'versions': [],
            'current_version': 0,
            'last_backup': None
        }
    
    def _save_versions(self):
        """Guarda el registro de versiones"""
        try:
            with open(self.versions_file, 'w', encoding='utf-8') as f:
                json.dump(self.versions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando versiones: {e}")
    
    def create_backup(self, project_data: Dict, backup_type: str = "auto") -> Optional[str]:
        """
        Crea un backup del proyecto
        
        Args:
            project_data: Datos del proyecto a respaldar
            backup_type: Tipo de backup ('auto', 'manual', 'milestone')
            
        Returns:
            Ruta del backup creado o None si falla
        """
        try:
            # Incrementar versión
            self.versions['current_version'] += 1
            version = self.versions['current_version']
            
            # Crear nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_v{version}_{timestamp}_{backup_type}.zip"
            backup_path = self.backup_dir / filename
            
            # Crear backup comprimido
            with zipfile.ZipFile(backup_path, 'w', self.compression_level) as zf:
                # Guardar datos del proyecto
                project_json = json.dumps(project_data, indent=2, ensure_ascii=False)
                zf.writestr('project_data.json', project_json)
                
                # Guardar metadatos
                metadata = {
                    'version': version,
                    'timestamp': datetime.now().isoformat(),
                    'type': backup_type,
                    'checksum': hashlib.md5(project_json.encode()).hexdigest(),
                    'size': len(project_json)
                }
                zf.writestr('metadata.json', json.dumps(metadata, indent=2))
                
                # Si hay archivos adjuntos (imágenes, etc.)
                if 'archivos_adjuntos' in project_data:
                    for archivo in project_data['archivos_adjuntos']:
                        if os.path.exists(archivo):
                            zf.write(archivo, os.path.basename(archivo))
            
            # Actualizar registro
            version_info = {
                'version': version,
                'timestamp': timestamp,
                'type': backup_type,
                'filename': filename,
                'size': backup_path.stat().st_size,
                'checksum': metadata['checksum']
            }
            
            self.versions['versions'].append(version_info)
            self.versions['last_backup'] = datetime.now().isoformat()
            self._save_versions()
            
            # Limpiar backups antiguos
            self._cleanup_old_backups()
            
            logger.info(f"Backup creado: {filename} (v{version})")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return None
    
    def restore_backup(self, version: Optional[int] = None, filename: Optional[str] = None) -> Optional[Dict]:
        """
        Restaura un backup específico
        
        Args:
            version: Número de versión a restaurar
            filename: Nombre del archivo de backup
            
        Returns:
            Datos del proyecto restaurados o None si falla
        """
        try:
            # Determinar archivo a restaurar
            if filename:
                backup_path = self.backup_dir / filename
            elif version:
                # Buscar por versión
                for v in self.versions['versions']:
                    if v['version'] == version:
                        backup_path = self.backup_dir / v['filename']
                        break
                else:
                    logger.error(f"Versión {version} no encontrada")
                    return None
            else:
                # Usar el más reciente
                if not self.versions['versions']:
                    logger.error("No hay backups disponibles")
                    return None
                    
                latest = self.versions['versions'][-1]
                backup_path = self.backup_dir / latest['filename']
            
            if not backup_path.exists():
                logger.error(f"Archivo de backup no encontrado: {backup_path}")
                return None
            
            # Extraer y cargar datos
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # Leer datos del proyecto
                project_data = json.loads(zf.read('project_data.json').decode('utf-8'))
                
                # Verificar integridad
                metadata = json.loads(zf.read('metadata.json').decode('utf-8'))
                checksum = hashlib.md5(json.dumps(project_data, indent=2, ensure_ascii=False).encode()).hexdigest()
                
                if checksum != metadata['checksum']:
                    logger.warning("Checksum no coincide - datos posiblemente corruptos")
                
                # Extraer archivos adjuntos si existen
                temp_dir = Path("temp_restore")
                temp_dir.mkdir(exist_ok=True)
                
                for file_info in zf.filelist:
                    if file_info.filename not in ['project_data.json', 'metadata.json']:
                        zf.extract(file_info, temp_dir)
                
                logger.info(f"Backup restaurado: {backup_path.name}")
                return project_data
                
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return None
    
    def get_versions_list(self) -> List[Dict]:
        """Obtiene lista de versiones disponibles"""
        return sorted(self.versions['versions'], key=lambda x: x['version'], reverse=True)
    
    def get_version_diff(self, version1: int, version2: int) -> Dict:
        """
        Compara dos versiones y muestra diferencias
        
        Args:
            version1: Primera versión
            version2: Segunda versión
            
        Returns:
            Diccionario con las diferencias
        """
        try:
            data1 = self.restore_backup(version=version1)
            data2 = self.restore_backup(version=version2)
            
            if not data1 or not data2:
                return {'error': 'No se pudieron cargar las versiones'}
            
            # Analizar diferencias
            diff = {
                'version1': version1,
                'version2': version2,
                'changes': []
            }
            
            # Comparar secciones
            secciones1 = set(data1.get('contenido_secciones', {}).keys())
            secciones2 = set(data2.get('contenido_secciones', {}).keys())
            
            # Secciones añadidas/eliminadas
            added = secciones2 - secciones1
            removed = secciones1 - secciones2
            
            if added:
                diff['changes'].append({'type': 'added_sections', 'sections': list(added)})
            if removed:
                diff['changes'].append({'type': 'removed_sections', 'sections': list(removed)})
            
            # Comparar contenido
            for seccion in secciones1 & secciones2:
                content1 = data1['contenido_secciones'].get(seccion, '')
                content2 = data2['contenido_secciones'].get(seccion, '')
                
                if content1 != content2:
                    diff['changes'].append({
                        'type': 'modified_section',
                        'section': seccion,
                        'words_before': len(content1.split()),
                        'words_after': len(content2.split())
                    })
            
            # Comparar referencias
            refs1 = len(data1.get('referencias', []))
            refs2 = len(data2.get('referencias', []))
            
            if refs1 != refs2:
                diff['changes'].append({
                    'type': 'references_changed',
                    'before': refs1,
                    'after': refs2
                })
            
            return diff
            
        except Exception as e:
            logger.error(f"Error comparando versiones: {e}")
            return {'error': str(e)}
    
    def _cleanup_old_backups(self):
        """Limpia backups antiguos manteniendo el límite"""
        if len(self.versions['versions']) > self.max_backups:
            # Mantener backups manuales y milestones
            auto_backups = [v for v in self.versions['versions'] if v['type'] == 'auto']
            
            # Eliminar los más antiguos
            while len(self.versions['versions']) > self.max_backups and auto_backups:
                oldest = min(auto_backups, key=lambda x: x['timestamp'])
                
                # Eliminar archivo
                backup_file = self.backup_dir / oldest['filename']
                if backup_file.exists():
                    backup_file.unlink()
                
                # Eliminar del registro
                self.versions['versions'].remove(oldest)
                auto_backups.remove(oldest)
                
                logger.info(f"Backup antiguo eliminado: {oldest['filename']}")
            
            self._save_versions()
    
    def schedule_auto_backup(self, app_instance):
        """Programa backups automáticos"""
        from datetime import datetime
        
        def do_backup():
            try:
                # Verificar si es necesario
                if self.versions['last_backup']:
                    last = datetime.fromisoformat(self.versions['last_backup'])
                    if (datetime.now() - last).seconds < self.auto_backup_interval:
                        # Muy pronto para otro backup
                        return
                
                # Recopilar datos del proyecto
                from core.project_manager import ProjectManager
                pm = ProjectManager()
                
                project_data = {
                    'version': '2.0',
                    'fecha_creacion': datetime.now().isoformat(),
                    'informacion_general': {},
                    'contenido_secciones': {},
                    'referencias': app_instance.referencias,
                    'secciones_activas': app_instance.secciones_activas,
                    'formato_config': app_instance.formato_config
                }
                
                # Recopilar información
                for key, entry in app_instance.proyecto_data.items():
                    if hasattr(entry, 'get'):
                        project_data['informacion_general'][key] = entry.get()
                
                for key, text_widget in app_instance.content_texts.items():
                    project_data['contenido_secciones'][key] = text_widget.get("1.0", "end")
                
                # Crear backup
                self.create_backup(project_data, backup_type='auto')
                
            except Exception as e:
                logger.error(f"Error en backup automático: {e}")
            
            finally:
                # Programar siguiente backup
                app_instance.root.after(
                    self.auto_backup_interval * 1000, 
                    lambda: self.schedule_auto_backup(app_instance)
                )
        
        # Ejecutar primer backup
        app_instance.root.after(5000, do_backup)  # Esperar 5 segundos al inicio