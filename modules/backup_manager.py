"""
Gestor de respaldos para el Generador de Proyectos Académicos
Maneja respaldos automáticos, manuales y recuperación de proyectos
"""

import os
import json
import shutil
import threading
import time
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog
import customtkinter as ctk

class BackupManager:
    """Gestiona el sistema completo de respaldos"""
    
    def __init__(self, app):
        self.app = app
        self.backup_dir = self.get_backup_directory()
        self.configuracion = self.get_configuracion_respaldos()
        self.auto_backup_thread = None
        self.auto_backup_running = False
        
        # Inicializar directorio de respaldos
        self.inicializar_directorio_respaldos()
        
        # Configurar auto-respaldo si está habilitado
        if self.configuracion['auto_backup_enabled']:
            self.iniciar_auto_backup()
    
    def get_backup_directory(self):
        """Obtiene el directorio de respaldos"""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_dir = os.path.join(script_dir, "data", "backups")
        return backup_dir
    
    def get_configuracion_respaldos(self):
        """Configuración por defecto del sistema de respaldos"""
        return {
            'auto_backup_enabled': True,
            'auto_backup_interval': 300,  # 5 minutos en segundos
            'max_backups': 20,
            'max_auto_backups': 10,
            'backup_on_save': True,
            'backup_on_exit': True,
            'compress_backups': False,
            'include_images': True,
            'retention_days': 30  # Días para conservar respaldos
        }
    
    def inicializar_directorio_respaldos(self):
        """Crea la estructura de directorios de respaldo"""
        try:
            # Crear directorio principal
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['auto', 'manual', 'session', 'emergency']
            for subdir in subdirs:
                os.makedirs(os.path.join(self.backup_dir, subdir), exist_ok=True)
            
            # Crear archivo de configuración si no existe
            config_file = os.path.join(self.backup_dir, 'backup_config.json')
            if not os.path.exists(config_file):
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.configuracion, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error inicializando directorio de respaldos: {e}")
            return False
    
    def crear_respaldo_manual(self, descripcion=""):
        """Crea un respaldo manual del proyecto actual"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"manual_{timestamp}"
            
            if descripcion:
                # Limpiar descripción para nombre de archivo
                desc_clean = "".join(c for c in descripcion if c.isalnum() or c in (' ', '-', '_')).rstrip()
                desc_clean = desc_clean.replace(' ', '_')[:30]  # Máximo 30 caracteres
                backup_name += f"_{desc_clean}"
            
            backup_path = os.path.join(self.backup_dir, 'manual', f"{backup_name}.json")
            
            # Crear datos de respaldo
            backup_data = self.crear_datos_respaldo('manual', descripcion)
            
            # Guardar respaldo
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            # Limpiar respaldos antiguos si es necesario
            self.limpiar_respaldos_antiguos('manual')
            
            return {
                'success': True,
                'backup_path': backup_path,
                'backup_name': backup_name,
                'timestamp': timestamp
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def crear_respaldo_automatico(self):
        """Crea un respaldo automático del proyecto"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"auto_{timestamp}"
            backup_path = os.path.join(self.backup_dir, 'auto', f"{backup_name}.json")
            
            # Crear datos de respaldo
            backup_data = self.crear_datos_respaldo('auto')
            
            # Guardar respaldo
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            # Limpiar respaldos automáticos antiguos
            self.limpiar_respaldos_antiguos('auto')
            
            print(f"Respaldo automático creado: {backup_name}")
            return True
            
        except Exception as e:
            print(f"Error en respaldo automático: {e}")
            return False
    
    def crear_respaldo_sesion(self):
        """Crea un respaldo de la sesión actual"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"session_{timestamp}"
            backup_path = os.path.join(self.backup_dir, 'session', f"{backup_name}.json")
            
            backup_data = self.crear_datos_respaldo('session')
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            return backup_path
            
        except Exception as e:
            print(f"Error en respaldo de sesión: {e}")
            return None
    
    def crear_respaldo_emergencia(self):
        """Crea un respaldo de emergencia"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"emergency_{timestamp}"
            backup_path = os.path.join(self.backup_dir, 'emergency', f"{backup_name}.json")
            
            backup_data = self.crear_datos_respaldo('emergency', "Respaldo de emergencia automático")
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            return backup_path
            
        except Exception as e:
            print(f"Error en respaldo de emergencia: {e}")
            return None
    
    def crear_datos_respaldo(self, tipo_respaldo, descripcion=""):
        """Crea la estructura de datos para el respaldo"""
        try:
            # Obtener datos del proyecto
            project_data = self.app.get_project_data() if hasattr(self.app, 'get_project_data') else {}
            
            # Crear estructura de respaldo
            backup_data = {
                'version': '2.0',
                'backup_info': {
                    'tipo': tipo_respaldo,
                    'timestamp': datetime.now().isoformat(),
                    'descripcion': descripcion,
                    'app_version': getattr(self.app, 'version', '2.0'),
                    'total_size': 0
                },
                'project_data': project_data,
                'content_data': {},
                'configuration': {
                    'formato_config': self.app.formato_config,
                    'secciones_disponibles': self.app.secciones_disponibles,
                    'secciones_activas': self.app.secciones_activas
                },
                'statistics': self.obtener_estadisticas_proyecto(),
                'metadata': {
                    'platform': os.name,
                    'backup_manager_version': '2.0'
                }
            }
            
            # Obtener contenido de secciones
            for seccion_id, text_widget in self.app.content_texts.items():
                try:
                    contenido = text_widget.get("1.0", "end")
                    backup_data['content_data'][seccion_id] = contenido
                except:
                    backup_data['content_data'][seccion_id] = ""
            
            # Calcular tamaño aproximado
            backup_data['backup_info']['total_size'] = len(json.dumps(backup_data, ensure_ascii=False))
            
            return backup_data
            
        except Exception as e:
            print(f"Error creando datos de respaldo: {e}")
            return {
                'version': '2.0',
                'backup_info': {
                    'tipo': tipo_respaldo,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
            }
    
    def obtener_estadisticas_proyecto(self):
        """Obtiene estadísticas del proyecto para el respaldo"""
        try:
            stats = {
                'total_secciones': len(self.app.secciones_activas),
                'secciones_con_contenido': 0,
                'total_palabras': 0,
                'total_caracteres': 0,
                'total_referencias': len(self.app.referencias),
                'fecha_ultima_modificacion': datetime.now().isoformat()
            }
            
            # Calcular estadísticas de contenido
            for seccion_id in self.app.secciones_activas:
                if seccion_id in self.app.content_texts:
                    contenido = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                    if contenido:
                        stats['secciones_con_contenido'] += 1
                        stats['total_palabras'] += len(contenido.split())
                        stats['total_caracteres'] += len(contenido)
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def restaurar_respaldo(self, backup_path):
        """Restaura un proyecto desde un respaldo"""
        try:
            if not os.path.exists(backup_path):
                return {'success': False, 'error': 'Archivo de respaldo no encontrado'}
            
            # Leer datos del respaldo
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validar estructura del respaldo
            if not self.validar_respaldo(backup_data):
                return {'success': False, 'error': 'Estructura de respaldo inválida'}
            
            # Crear respaldo de emergencia del estado actual antes de restaurar
            emergency_backup = self.crear_respaldo_emergencia()
            
            # Restaurar datos del proyecto
            self.restaurar_datos_proyecto(backup_data)
            
            return {
                'success': True,
                'backup_info': backup_data.get('backup_info', {}),
                'emergency_backup': emergency_backup
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validar_respaldo(self, backup_data):
        """Valida que un respaldo tenga la estructura correcta"""
        try:
            # Verificar campos obligatorios
            campos_requeridos = ['version', 'backup_info', 'project_data']
            for campo in campos_requeridos:
                if campo not in backup_data:
                    return False
            
            # Verificar información del respaldo
            backup_info = backup_data['backup_info']
            if 'timestamp' not in backup_info:
                return False
            
            return True
            
        except Exception:
            return False
    
    def restaurar_datos_proyecto(self, backup_data):
        """Restaura los datos del proyecto desde el respaldo"""
        try:
            # Restaurar información general
            if 'project_data' in backup_data:
                project_data = backup_data['project_data'].get('proyecto_data', {})
                for campo, valor in project_data.items():
                    if campo in self.app.proyecto_data and hasattr(self.app.proyecto_data[campo], 'delete'):
                        self.app.proyecto_data[campo].delete(0, "end")
                        self.app.proyecto_data[campo].insert(0, str(valor))
            
            # Restaurar referencias
            if 'project_data' in backup_data and 'referencias' in backup_data['project_data']:
                self.app.referencias = backup_data['project_data']['referencias']
            
            # Restaurar configuración
            if 'configuration' in backup_data:
                config = backup_data['configuration']
                if 'formato_config' in config:
                    self.app.formato_config.update(config['formato_config'])
                if 'secciones_disponibles' in config:
                    self.app.secciones_disponibles = config['secciones_disponibles']
                if 'secciones_activas' in config:
                    self.app.secciones_activas = config['secciones_activas']
            
            # Restaurar contenido de secciones
            if 'content_data' in backup_data:
                # Primero actualizar la interfaz si es necesario
                if hasattr(self.app, 'actualizar_lista_secciones'):
                    self.app.actualizar_lista_secciones()
                if hasattr(self.app, 'crear_pestanas_contenido'):
                    self.app.crear_pestanas_contenido()
                
                # Luego restaurar contenido
                for seccion_id, contenido in backup_data['content_data'].items():
                    if seccion_id in self.app.content_texts:
                        self.app.content_texts[seccion_id].delete("1.0", "end")
                        self.app.content_texts[seccion_id].insert("1.0", contenido)
            
            # Actualizar interfaz final
            if hasattr(self.app, 'actualizar_lista_referencias'):
                self.app.actualizar_lista_referencias()
            
            return True
            
        except Exception as e:
            print(f"Error restaurando datos: {e}")
            return False
    
    def obtener_lista_respaldos(self, tipo=None):
        """Obtiene lista de respaldos disponibles"""
        respaldos = []
        
        try:
            # Buscar en todos los subdirectorios o en uno específico
            if tipo:
                subdirs = [tipo]
            else:
                subdirs = ['manual', 'auto', 'session', 'emergency']
            
            for subdir in subdirs:
                subdir_path = os.path.join(self.backup_dir, subdir)
                if os.path.exists(subdir_path):
                    for filename in os.listdir(subdir_path):
                        if filename.endswith('.json'):
                            filepath = os.path.join(subdir_path, filename)
                            try:
                                # Obtener información del respaldo
                                info_respaldo = self.obtener_info_respaldo(filepath)
                                if info_respaldo:
                                    respaldos.append(info_respaldo)
                            except Exception as e:
                                print(f"Error leyendo respaldo {filename}: {e}")
            
            # Ordenar por fecha (más reciente primero)
            respaldos.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return respaldos
            
        except Exception as e:
            print(f"Error obteniendo lista de respaldos: {e}")
            return []
    
    def obtener_info_respaldo(self, filepath):
        """Obtiene información de un archivo de respaldo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            backup_info = backup_data.get('backup_info', {})
            file_stats = os.stat(filepath)
            
            return {
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'tipo': backup_info.get('tipo', 'unknown'),
                'timestamp': backup_info.get('timestamp', ''),
                'descripcion': backup_info.get('descripcion', ''),
                'size': file_stats.st_size,
                'size_mb': file_stats.st_size / (1024 * 1024),
                'fecha_creacion': datetime.fromtimestamp(file_stats.st_ctime),
                'fecha_modificacion': datetime.fromtimestamp(file_stats.st_mtime),
                'statistics': backup_data.get('statistics', {}),
                'version': backup_data.get('version', '1.0')
            }
            
        except Exception as e:
            return None
    
    def limpiar_respaldos_antiguos(self, tipo=None):
        """Limpia respaldos antiguos según configuración"""
        try:
            config = self.configuracion
            
            if tipo == 'auto':
                max_backups = config['max_auto_backups']
            else:
                max_backups = config['max_backups']
            
            # Obtener respaldos del tipo especificado
            respaldos = self.obtener_lista_respaldos(tipo)
            
            if len(respaldos) > max_backups:
                # Eliminar los más antiguos
                respaldos_a_eliminar = respaldos[max_backups:]
                
                for respaldo in respaldos_a_eliminar:
                    try:
                        os.remove(respaldo['filepath'])
                        print(f"Respaldo eliminado: {respaldo['filename']}")
                    except Exception as e:
                        print(f"Error eliminando respaldo {respaldo['filename']}: {e}")
            
            # Limpiar por fecha si está configurado
            if config['retention_days'] > 0:
                fecha_limite = datetime.now() - timedelta(days=config['retention_days'])
                
                for respaldo in respaldos:
                    if respaldo['fecha_creacion'] < fecha_limite:
                        try:
                            os.remove(respaldo['filepath'])
                            print(f"Respaldo expirado eliminado: {respaldo['filename']}")
                        except Exception as e:
                            print(f"Error eliminando respaldo expirado {respaldo['filename']}: {e}")
            
            return True
            
        except Exception as e:
            print(f"Error limpiando respaldos antiguos: {e}")
            return False
    
    def iniciar_auto_backup(self):
        """Inicia el sistema de respaldo automático"""
        if not self.auto_backup_running:
            self.auto_backup_running = True
            self.auto_backup_thread = threading.Thread(target=self.run_auto_backup, daemon=True)
            self.auto_backup_thread.start()
            print("Sistema de respaldo automático iniciado")
    
    def detener_auto_backup(self):
        """Detiene el sistema de respaldo automático"""
        self.auto_backup_running = False
        if self.auto_backup_thread:
            self.auto_backup_thread.join(timeout=5)
        print("Sistema de respaldo automático detenido")
    
    def run_auto_backup(self):
        """Ejecuta el bucle de respaldo automático"""
        while self.auto_backup_running:
            try:
                time.sleep(self.configuracion['auto_backup_interval'])
                
                if self.auto_backup_running:  # Verificar nuevamente
                    # Solo crear respaldo si hay contenido significativo
                    if self.tiene_contenido_significativo():
                        self.crear_respaldo_automatico()
                
            except Exception as e:
                print(f"Error en bucle de auto-respaldo: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de intentar nuevamente
    
    def tiene_contenido_significativo(self):
        """Verifica si el proyecto tiene contenido significativo para respaldar"""
        try:
            # Verificar si hay contenido en las secciones
            contenido_total = 0
            for seccion_id in self.app.secciones_activas:
                if seccion_id in self.app.content_texts:
                    contenido = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                    contenido_total += len(contenido)
            
            # Verificar información general
            info_completa = 0
            for campo, widget in self.app.proyecto_data.items():
                if hasattr(widget, 'get') and widget.get().strip():
                    info_completa += 1
            
            # Considerar significativo si hay al menos 100 caracteres de contenido
            # o información general completa
            return contenido_total > 100 or info_completa > 3 or len(self.app.referencias) > 0
            
        except Exception:
            return False
    
    def gestionar_respaldos(self, parent_window):
        """Abre ventana de gestión de respaldos"""
        backup_window = ctk.CTkToplevel(parent_window)
        backup_window.title("🛡️ Gestión Avanzada de Respaldos")
        backup_window.geometry("1000x700")
        backup_window.transient(parent_window)
        backup_window.grab_set()
        
        # Centrar ventana
        backup_window.update_idletasks()
        x = (backup_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (backup_window.winfo_screenheight() // 2) - (700 // 2)
        backup_window.geometry(f"1000x700+{x}+{y}")
        
        # Crear interfaz
        self.crear_interfaz_respaldos(backup_window)
    
    def crear_interfaz_respaldos(self, window):
        """Crea la interfaz de gestión de respaldos"""
        main_frame = ctk.CTkFrame(window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título principal
        title_label = ctk.CTkLabel(
            main_frame, text="🛡️ Sistema Avanzado de Respaldos",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Estado del sistema
        self.crear_estado_sistema(main_frame)
        
        # Pestañas principales
        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        
        # Pestaña de respaldos
        respaldos_tab = tabview.add("📋 Respaldos")
        self.crear_tab_respaldos(respaldos_tab, window)
        
        # Pestaña de configuración
        config_tab = tabview.add("⚙️ Configuración")
        self.crear_tab_configuracion(config_tab)
        
        # Pestaña de estadísticas
        stats_tab = tabview.add("📊 Estadísticas")
        self.crear_tab_estadisticas(stats_tab)
        
        # Botones principales
        self.crear_botones_respaldos(main_frame, window)
    
    def crear_estado_sistema(self, parent):
        """Crea la sección de estado del sistema"""
        status_frame = ctk.CTkFrame(parent, height=80, corner_radius=10)
        status_frame.pack(fill="x", pady=(0, 15))
        status_frame.pack_propagate(False)
        
        # Estado del auto-respaldo
        auto_status = "🟢 ACTIVO" if self.auto_backup_running else "🔴 INACTIVO"
        
        # Último respaldo
        respaldos = self.obtener_lista_respaldos()
        ultimo_respaldo = respaldos[0]['fecha_creacion'].strftime("%H:%M:%S") if respaldos else "Nunca"
        
        # Total de respaldos
        total_respaldos = len(respaldos)
        
        status_text = f"Auto-respaldo: {auto_status} | Último respaldo: {ultimo_respaldo} | Total: {total_respaldos}"
        
        status_label = ctk.CTkLabel(
            status_frame, text=status_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_label.pack(expand=True)
    
    def crear_tab_respaldos(self, parent, window):
        """Crea la pestaña de gestión de respaldos"""
        # Frame de controles
        controls_frame = ctk.CTkFrame(parent, height=60)
        controls_frame.pack(fill="x", padx=10, pady=(10, 15))
        controls_frame.pack_propagate(False)
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        btn_frame.pack(expand=True, fill="both", padx=15, pady=10)
        
        manual_backup_btn = ctk.CTkButton(
            btn_frame, text="💾 Respaldo Manual",
            command=lambda: self.crear_respaldo_manual_dialog(window),
            width=140, height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        manual_backup_btn.pack(side="left", padx=(0, 10))
        
        restore_btn = ctk.CTkButton(
            btn_frame, text="📥 Restaurar",
            command=self.restaurar_respaldo_dialog,
            width=120, height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="blue", hover_color="darkblue"
        )
        restore_btn.pack(side="left", padx=(0, 10))
        
        delete_btn = ctk.CTkButton(
            btn_frame, text="🗑️ Limpiar",
            command=self.limpiar_respaldos_dialog,
            width=110, height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="red", hover_color="darkred"
        )
        delete_btn.pack(side="left")
        
        # Filtros
        filter_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(filter_frame, text="Filtrar:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 5))
        
        self.filter_combo = ctk.CTkComboBox(
            filter_frame, values=["Todos", "Manual", "Automático", "Sesión", "Emergencia"],
            width=120, height=25, command=self.filtrar_respaldos
        )
        self.filter_combo.pack(side="left", padx=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            filter_frame, text="🔄", command=self.actualizar_lista_respaldos,
            width=30, height=25
        )
        refresh_btn.pack(side="left")
        
        # Lista de respaldos
        self.respaldos_frame = ctk.CTkScrollableFrame(parent, height=350)
        self.respaldos_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Cargar lista inicial
        self.actualizar_lista_respaldos()
    
    def crear_tab_configuracion(self, parent):
        """Crea la pestaña de configuración de respaldos"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Auto-respaldo
        auto_frame = ctk.CTkFrame(scroll_frame, fg_color="darkgreen", corner_radius=10)
        auto_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            auto_frame, text="🔄 Respaldo Automático",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        ).pack(pady=(15, 10))
        
        # Controles de auto-respaldo
        auto_controls = ctk.CTkFrame(auto_frame, fg_color="transparent")
        auto_controls.pack(fill="x", padx=15, pady=(0, 15))
        
        self.auto_backup_enabled = ctk.CTkCheckBox(
            auto_controls, text="Habilitar respaldo automático",
            font=ctk.CTkFont(size=12)
        )
        if self.configuracion['auto_backup_enabled']:
            self.auto_backup_enabled.select()
        self.auto_backup_enabled.pack(anchor="w", pady=5)
        
        # Intervalo
        interval_frame = ctk.CTkFrame(auto_controls, fg_color="transparent")
        interval_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(interval_frame, text="Intervalo (minutos):", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.interval_entry = ctk.CTkEntry(interval_frame, width=80, height=25)
        self.interval_entry.pack(side="left", padx=(10, 0))
        self.interval_entry.insert(0, str(self.configuracion['auto_backup_interval'] // 60))
        
        # Límites de respaldos
        limits_frame = ctk.CTkFrame(scroll_frame, fg_color="darkblue", corner_radius=10)
        limits_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            limits_frame, text="📊 Límites de Almacenamiento",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        ).pack(pady=(15, 10))
        
        limits_controls = ctk.CTkFrame(limits_frame, fg_color="transparent")
        limits_controls.pack(fill="x", padx=15, pady=(0, 15))
        
        # Máximo respaldos manuales
        max_manual_frame = ctk.CTkFrame(limits_controls, fg_color="transparent")
        max_manual_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(max_manual_frame, text="Máx. respaldos manuales:", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.max_manual_entry = ctk.CTkEntry(max_manual_frame, width=60, height=25)
        self.max_manual_entry.pack(side="left", padx=(10, 0))
        self.max_manual_entry.insert(0, str(self.configuracion['max_backups']))
        
        # Máximo respaldos automáticos
        max_auto_frame = ctk.CTkFrame(limits_controls, fg_color="transparent")
        max_auto_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(max_auto_frame, text="Máx. respaldos automáticos:", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.max_auto_entry = ctk.CTkEntry(max_auto_frame, width=60, height=25)
        self.max_auto_entry.pack(side="left", padx=(10, 0))
        self.max_auto_entry.insert(0, str(self.configuracion['max_auto_backups']))
        
        # Días de retención
        retention_frame = ctk.CTkFrame(limits_controls, fg_color="transparent")
        retention_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(retention_frame, text="Días de retención:", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.retention_entry = ctk.CTkEntry(retention_frame, width=60, height=25)
        self.retention_entry.pack(side="left", padx=(10, 0))
        self.retention_entry.insert(0, str(self.configuracion['retention_days']))
        
        # Opciones adicionales
        options_frame = ctk.CTkFrame(scroll_frame, fg_color="darkorange", corner_radius=10)
        options_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            options_frame, text="⚙️ Opciones Adicionales",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        ).pack(pady=(15, 10))
        
        options_controls = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_controls.pack(fill="x", padx=15, pady=(0, 15))
        
        self.backup_on_save = ctk.CTkCheckBox(
            options_controls, text="Respaldo al guardar proyecto",
            font=ctk.CTkFont(size=12)
        )
        if self.configuracion['backup_on_save']:
            self.backup_on_save.select()
        self.backup_on_save.pack(anchor="w", pady=2)
        
        self.backup_on_exit = ctk.CTkCheckBox(
            options_controls, text="Respaldo al cerrar aplicación",
            font=ctk.CTkFont(size=12)
        )
        if self.configuracion['backup_on_exit']:
            self.backup_on_exit.select()
        self.backup_on_exit.pack(anchor="w", pady=2)
        
        # Botón aplicar configuración
        apply_btn = ctk.CTkButton(
            scroll_frame, text="✅ Aplicar Configuración",
            command=self.aplicar_configuracion_respaldos,
            width=200, height=40, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        apply_btn.pack(pady=20)
    
    def crear_tab_estadisticas(self, parent):
        """Crea la pestaña de estadísticas de respaldos"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Obtener estadísticas
        stats = self.obtener_estadisticas_respaldos()
        
        # Estadísticas generales
        general_frame = ctk.CTkFrame(scroll_frame, fg_color="darkgreen", corner_radius=10)
        general_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            general_frame, text="📊 Estadísticas Generales",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        ).pack(pady=(15, 10))
        
        stats_text = f"""Total de respaldos: {stats['total_respaldos']}
Respaldos manuales: {stats['manuales']}
Respaldos automáticos: {stats['automaticos']}
Respaldos de sesión: {stats['sesion']}
Respaldos de emergencia: {stats['emergencia']}

Tamaño total: {stats['tamaño_total_mb']:.1f} MB
Respaldo más antiguo: {stats['mas_antiguo']}
Respaldo más reciente: {stats['mas_reciente']}"""
        
        stats_label = ctk.CTkLabel(
            general_frame, text=stats_text,
            font=ctk.CTkFont(size=11), text_color="white", justify="left"
        )
        stats_label.pack(padx=15, pady=(0, 15))
    
    def obtener_estadisticas_respaldos(self):
        """Obtiene estadísticas del sistema de respaldos"""
        respaldos = self.obtener_lista_respaldos()
        
        stats = {
            'total_respaldos': len(respaldos),
            'manuales': len([r for r in respaldos if r['tipo'] == 'manual']),
            'automaticos': len([r for r in respaldos if r['tipo'] == 'auto']),
            'sesion': len([r for r in respaldos if r['tipo'] == 'session']),
            'emergencia': len([r for r in respaldos if r['tipo'] == 'emergency']),
            'tamaño_total_mb': sum(r['size_mb'] for r in respaldos),
            'mas_antiguo': respaldos[-1]['fecha_creacion'].strftime("%Y-%m-%d %H:%M") if respaldos else "N/A",
            'mas_reciente': respaldos[0]['fecha_creacion'].strftime("%Y-%m-%d %H:%M") if respaldos else "N/A"
        }
        
        return stats
    
    def crear_botones_respaldos(self, parent, window):
        """Crea botones principales de la ventana de respaldos"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        help_btn = ctk.CTkButton(
            btn_frame, text="❓ Ayuda",
            command=self.mostrar_ayuda_respaldos,
            width=100, height=35
        )
        help_btn.pack(side="left")
        
        close_btn = ctk.CTkButton(
            btn_frame, text="✅ Cerrar",
            command=window.destroy,
            width=120, height=35
        )
        close_btn.pack(side="right")
    
    def crear_respaldo_manual_dialog(self, parent_window):
        """Abre diálogo para crear respaldo manual"""
        dialog = ctk.CTkInputDialog(
            text="Descripción del respaldo (opcional):",
            title="💾 Crear Respaldo Manual"
        )
        
        descripcion = dialog.get_input()
        if descripcion is not None:  # Usuario no canceló
            resultado = self.crear_respaldo_manual(descripcion)
            
            if resultado['success']:
                messagebox.showinfo(
                    "✅ Respaldo Creado",
                    f"Respaldo manual creado exitosamente:\n{resultado['backup_name']}"
                )
                self.actualizar_lista_respaldos()
            else:
                messagebox.showerror(
                    "❌ Error",
                    f"Error al crear respaldo:\n{resultado['error']}"
                )
    
    def restaurar_respaldo_dialog(self):
        """Abre diálogo para restaurar respaldo"""
        # Implementar selección de respaldo para restaurar
        messagebox.showinfo(
            "📥 Restaurar Respaldo",
            "🚧 Función en desarrollo\n\n"
            "La funcionalidad de restauración completa estará disponible próximamente.\n"
            "Incluirá:\n"
            "• Selección de respaldo específico\n"
            "• Vista previa de contenido\n"
            "• Restauración parcial o completa"
        )
    
    def limpiar_respaldos_dialog(self):
        """Abre diálogo para limpiar respaldos"""
        respuesta = messagebox.askyesno(
            "🗑️ Limpiar Respaldos",
            "¿Deseas limpiar respaldos antiguos según la configuración?\n\n"
            "Esto eliminará:\n"
            "• Respaldos que excedan los límites configurados\n"
            "• Respaldos más antiguos que el período de retención\n\n"
            "¿Continuar?"
        )
        
        if respuesta:
            try:
                self.limpiar_respaldos_antiguos()
                self.actualizar_lista_respaldos()
                messagebox.showinfo("✅ Limpieza Completa", "Respaldos antiguos eliminados")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al limpiar respaldos:\n{str(e)}")
    
    def filtrar_respaldos(self, filtro=None):
        """Filtra la lista de respaldos mostrados"""
        if filtro is None:
            filtro = self.filter_combo.get()
        
        # Limpiar lista actual
        for widget in self.respaldos_frame.winfo_children():
            widget.destroy()
        
        # Obtener respaldos filtrados
        if filtro == "Todos":
            respaldos = self.obtener_lista_respaldos()
        else:
            tipo_map = {
                "Manual": "manual",
                "Automático": "auto", 
                "Sesión": "session",
                "Emergencia": "emergency"
            }
            tipo = tipo_map.get(filtro, "manual")
            respaldos = self.obtener_lista_respaldos(tipo)
        
        # Mostrar respaldos filtrados
        for respaldo in respaldos:
            self.crear_item_respaldo(self.respaldos_frame, respaldo)
    
    def actualizar_lista_respaldos(self):
        """Actualiza la lista de respaldos mostrados"""
        self.filtrar_respaldos()
    
    def crear_item_respaldo(self, parent, respaldo):
        """Crea un item visual para mostrar un respaldo"""
        item_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=8)
        item_frame.pack(fill="x", padx=5, pady=3)
        
        # Información principal
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # Nombre y tipo
        name_label = ctk.CTkLabel(
            info_frame, text=respaldo['filename'],
            font=ctk.CTkFont(size=12, weight="bold")
        )
        name_label.pack(side="left")
        
        # Badges
        badges_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        badges_frame.pack(side="right")
        
        # Tipo
        tipo_colors = {
            'manual': 'blue',
            'auto': 'green', 
            'session': 'orange',
            'emergency': 'red'
        }
        
        tipo_badge = ctk.CTkLabel(
            badges_frame, text=respaldo['tipo'].title(),
            font=ctk.CTkFont(size=10), text_color=tipo_colors.get(respaldo['tipo'], 'gray')
        )
        tipo_badge.pack(side="right", padx=(0, 5))
        
        # Tamaño
        size_badge = ctk.CTkLabel(
            badges_frame, text=f"{respaldo['size_mb']:.1f}MB",
            font=ctk.CTkFont(size=10), text_color="gray60"
        )
        size_badge.pack(side="right", padx=(0, 5))
        
        # Información adicional
        fecha_str = respaldo['fecha_creacion'].strftime("%Y-%m-%d %H:%M:%S")
        info_text = f"📅 {fecha_str}"
        
        if respaldo['descripcion']:
            info_text += f" | 📝 {respaldo['descripcion']}"
        
        detail_label = ctk.CTkLabel(
            item_frame, text=info_text,
            font=ctk.CTkFont(size=10), text_color="gray70"
        )
        detail_label.pack(anchor="w", padx=15, pady=(0, 10))
    
    def aplicar_configuracion_respaldos(self):
        """Aplica la configuración de respaldos"""
        try:
            # Obtener valores de la interfaz
            nueva_config = {
                'auto_backup_enabled': self.auto_backup_enabled.get(),
                'auto_backup_interval': int(self.interval_entry.get()) * 60,  # Convertir a segundos
                'max_backups': int(self.max_manual_entry.get()),
                'max_auto_backups': int(self.max_auto_entry.get()),
                'retention_days': int(self.retention_entry.get()),
                'backup_on_save': self.backup_on_save.get(),
                'backup_on_exit': self.backup_on_exit.get(),
                'compress_backups': self.configuracion['compress_backups'],  # Mantener valor actual
                'include_images': self.configuracion['include_images']  # Mantener valor actual
            }
            
            # Validar valores
            if nueva_config['auto_backup_interval'] < 60:  # Mínimo 1 minuto
                raise ValueError("El intervalo mínimo es 1 minuto")
            
            if nueva_config['max_backups'] < 1 or nueva_config['max_auto_backups'] < 1:
                raise ValueError("Debe haber al menos 1 respaldo de cada tipo")
            
            # Aplicar configuración
            auto_backup_cambio = self.configuracion['auto_backup_enabled'] != nueva_config['auto_backup_enabled']
            self.configuracion.update(nueva_config)
            
            # Reiniciar auto-backup si es necesario
            if auto_backup_cambio:
                if nueva_config['auto_backup_enabled']:
                    if not self.auto_backup_running:
                        self.iniciar_auto_backup()
                else:
                    if self.auto_backup_running:
                        self.detener_auto_backup()
            
            # Guardar configuración
            config_file = os.path.join(self.backup_dir, 'backup_config.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.configuracion, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("✅ Configuración Aplicada", 
                "La configuración de respaldos se ha aplicado correctamente")
            
        except ValueError as e:
            messagebox.showerror("❌ Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al aplicar configuración:\n{str(e)}")
    
    def mostrar_ayuda_respaldos(self):
        """Muestra ayuda del sistema de respaldos"""
        messagebox.showinfo(
            "❓ Ayuda - Sistema de Respaldos",
            "🛡️ SISTEMA DE RESPALDOS AUTOMÁTICO\n\n"
            "TIPOS DE RESPALDO:\n"
            "• Manual: Creados por el usuario\n"
            "• Automático: Cada X minutos automáticamente\n"
            "• Sesión: Al inicio de cada sesión\n"
            "• Emergencia: Antes de operaciones críticas\n\n"
            "CARACTERÍSTICAS:\n"
            "• Respaldo completo del proyecto\n"
            "• Limpieza automática de archivos antiguos\n"
            "• Configuración personalizable\n"
            "• Restauración completa o parcial\n\n"
            "¡Tu trabajo está siempre protegido!"
        )
    
    def respaldo_al_cerrar(self):
        """Crea respaldo al cerrar la aplicación si está configurado"""
        if self.configuracion['backup_on_exit']:
            try:
                self.crear_respaldo_sesion()
                print("Respaldo de cierre creado")
            except Exception as e:
                print(f"Error en respaldo de cierre: {e}")
        
        # Detener auto-respaldo
        self.detener_auto_backup()
    
    def __del__(self):
        """Destructor para limpiar recursos"""
        if hasattr(self, 'auto_backup_running'):
            self.detener_auto_backup()