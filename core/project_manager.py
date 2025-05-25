"""
Gestor de proyectos - Versión completa corregida
"""

import json
import os
import hashlib
from datetime import datetime
from tkinter import filedialog, messagebox
from copy import deepcopy
from pathlib import Path
from utils.logger import get_logger
from config.settings import AUTOSAVE_CONFIG

logger = get_logger('ProjectManager')

class ProjectManager:
    """Gestor completo de proyectos con auto-guardado y validación"""
    
    def __init__(self):
        self.auto_save_enabled = True
        self.last_save_time = None
        self.last_save_hash = None
        self.auto_save_timer = None
        
        # Configurar directorio de auto-guardado
        self.autosave_dir = Path(AUTOSAVE_CONFIG.get('backup_dir', 'backups'))
        self.autosave_dir.mkdir(exist_ok=True)
        
        logger.info("ProjectManager inicializado")

    def guardar_proyecto(self, app_instance):
        """Guarda el proyecto completo en un archivo JSON"""
        try:
            # Recopilar todos los datos del proyecto
            proyecto_completo = self._recopilar_datos_proyecto(app_instance)
            
            # Solicitar ubicación de archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("Proyecto Académico", "*.json"), 
                    ("Todos los archivos", "*.*")
                ],
                title="Guardar Proyecto Académico",
                initialname=self._generar_nombre_archivo(app_instance)
            )
            
            if filename:
                # Guardar archivo
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(proyecto_completo, f, ensure_ascii=False, indent=2)
                
                # Actualizar estado
                self.last_save_time = datetime.now()
                self.last_save_hash = self._calcular_hash_proyecto(proyecto_completo)
                
                # Crear backup automático
                self._crear_backup_automatico(proyecto_completo)
                
                logger.info(f"Proyecto guardado exitosamente: {filename}")
                messagebox.showinfo("💾 Guardado Exitoso", 
                    f"Proyecto guardado correctamente:\n{os.path.basename(filename)}")
                
                return True
                
        except PermissionError:
            error_msg = "No se tiene permiso para escribir en la ubicación seleccionada"
            logger.error(error_msg)
            messagebox.showerror("❌ Error de Permisos", error_msg)
        except Exception as e:
            error_msg = f"Error al guardar proyecto: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("❌ Error al Guardar", error_msg)
        
        return False
    
    def cargar_proyecto(self, app_instance):
        """Carga un proyecto desde archivo JSON - MÉTODO COMPLETO"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[
                    ("Proyecto Académico", "*.json"), 
                    ("Todos los archivos", "*.*")
                ],
                title="Cargar Proyecto Académico"
            )
            
            if not filename:
                return False
            
            # Verificar que el archivo existe
            if not os.path.exists(filename):
                messagebox.showerror("❌ Error", "El archivo seleccionado no existe")
                return False
            
            # Cargar archivo JSON
            with open(filename, 'r', encoding='utf-8') as f:
                proyecto_completo = json.load(f)
            
            # Validar estructura del proyecto
            if not self._validar_estructura_proyecto(proyecto_completo):
                return False
            
            # Verificar versión
            version = proyecto_completo.get('version', '1.0')
            if version != '2.0' and version != '2.1.0':
                respuesta = messagebox.askyesno("⚠️ Versión Anterior", 
                    f"Este proyecto fue creado con la versión {version}.\n"
                    "Algunas características pueden no funcionar correctamente.\n\n"
                    "¿Desea continuar cargando el proyecto?")
                if not respuesta:
                    return False
            
            # Cargar información general
            self._cargar_informacion_general(proyecto_completo, app_instance)
            
            # Cargar contenido de secciones
            self._cargar_contenido_secciones(proyecto_completo, app_instance)
            
            # Cargar referencias
            self._cargar_referencias(proyecto_completo, app_instance)
            
            # Cargar configuración de formato
            self._cargar_configuracion_formato(proyecto_completo, app_instance)
            
            # Cargar imágenes personalizadas
            self._cargar_imagenes_personalizadas(proyecto_completo, app_instance)
            
            # Cargar secciones disponibles y activas
            self._cargar_configuracion_secciones(proyecto_completo, app_instance)
            
            # Actualizar interfaz
            self._actualizar_interfaz_despues_carga(app_instance)
            
            # Actualizar estado
            self.last_save_time = datetime.now()
            self.last_save_hash = self._calcular_hash_proyecto(proyecto_completo)
            
            logger.info(f"Proyecto cargado exitosamente: {filename}")
            messagebox.showinfo("📂 Carga Exitosa", 
                f"Proyecto cargado correctamente:\n{os.path.basename(filename)}")
            
            return True
            
        except json.JSONDecodeError as e:
            error_msg = f"El archivo no es un JSON válido: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("❌ Error de Formato", error_msg)
        except KeyError as e:
            error_msg = f"El archivo no contiene los datos necesarios: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("❌ Archivo Incompleto", error_msg)
        except Exception as e:
            error_msg = f"Error al cargar proyecto: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("❌ Error al Cargar", error_msg)
        
        return False
    
    def nuevo_proyecto(self, app_instance):
        """Crea un nuevo proyecto limpio"""
        try:
            if self._hay_cambios_sin_guardar(app_instance):
                respuesta = messagebox.askyesnocancel("💾 Guardar Cambios", 
                    "Hay cambios sin guardar. ¿Desea guardarlos antes de crear un nuevo proyecto?")
                
                if respuesta is None:  # Cancelar
                    return False
                elif respuesta:  # Sí, guardar
                    if not self.guardar_proyecto(app_instance):
                        return False
            
            # Limpiar todos los datos
            self._limpiar_proyecto(app_instance)
            
            # Reinicializar valores por defecto
            self._inicializar_valores_defecto(app_instance)
            
            # Actualizar interfaz
            self._actualizar_interfaz_despues_carga(app_instance)
            
            self.last_save_time = None
            self.last_save_hash = None
            
            logger.info("Nuevo proyecto creado")
            messagebox.showinfo("📄 Nuevo Proyecto", "Nuevo proyecto creado correctamente")
            
            return True
            
        except Exception as e:
            error_msg = f"Error creando nuevo proyecto: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("❌ Error", error_msg)
            return False
    
    def auto_save_project(self, app_instance):
        """Realiza auto-guardado automático"""
        try:
            if not self.auto_save_enabled:
                return
            
            # Verificar si hay cambios
            if not self._hay_cambios_desde_ultimo_guardado(app_instance):
                # Programar próximo auto-guardado
                self._programar_auto_guardado(app_instance)
                return
            
            # Recopilar datos
            proyecto_completo = self._recopilar_datos_proyecto(app_instance)
            
            # Crear archivo de auto-guardado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.autosave_dir / f"autosave_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(proyecto_completo, f, ensure_ascii=False, indent=2)
            
            # Actualizar hash
            self.last_save_hash = self._calcular_hash_proyecto(proyecto_completo)
            
            # Limpiar auto-guardados antiguos
            self._limpiar_autosaves_antiguos()
            
            logger.info(f"Auto-guardado realizado: {filename}")
            
        except Exception as e:
            logger.warning(f"Error en auto-guardado: {e}")
        finally:
            # Programar próximo auto-guardado
            self._programar_auto_guardado(app_instance)
    
    def exportar_configuracion(self, app_instance):
        """Exporta solo la configuración del proyecto"""
        try:
            configuracion = {
                'version': '2.1.0',
                'tipo': 'configuracion',
                'formato_config': app_instance.formato_config,
                'secciones_disponibles': app_instance.secciones_disponibles,
                'secciones_activas': app_instance.secciones_activas,
                'fecha_exportacion': datetime.now().isoformat()
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Configuración", "*.json")],
                title="Exportar Configuración"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(configuracion, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Configuración exportada: {filename}")
                messagebox.showinfo("📤 Exportado", 
                    f"Configuración exportada:\n{os.path.basename(filename)}")
                return True
                
        except Exception as e:
            error_msg = f"Error exportando configuración: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("❌ Error", error_msg)
        
        return False
    
    def importar_configuracion(self, app_instance):
        """Importa configuración desde archivo"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Configuración", "*.json")],
                title="Importar Configuración"
            )
            
            if not filename:
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                configuracion = json.load(f)
            
            # Validar que es un archivo de configuración
            if configuracion.get('tipo') != 'configuracion':
                messagebox.showerror("❌ Error", 
                    "El archivo seleccionado no es una configuración válida")
                return False
            
            # Aplicar configuración
            if 'formato_config' in configuracion:
                app_instance.formato_config.update(configuracion['formato_config'])
            
            if 'secciones_disponibles' in configuracion:
                app_instance.secciones_disponibles.update(configuracion['secciones_disponibles'])
            
            if 'secciones_activas' in configuracion:
                app_instance.secciones_activas = configuracion['secciones_activas']
            
            # Actualizar interfaz
            self._actualizar_interfaz_despues_carga(app_instance)
            
            logger.info(f"Configuración importada: {filename}")
            messagebox.showinfo("📥 Importado", 
                f"Configuración importada:\n{os.path.basename(filename)}")
            return True
            
        except Exception as e:
            error_msg = f"Error importando configuración: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("❌ Error", error_msg)
        
        return False
    
    # ==================== MÉTODOS PRIVADOS ====================
    
    def _recopilar_datos_proyecto(self, app_instance):
        """Recopila todos los datos del proyecto"""
        proyecto_completo = {
            'version': '2.1.0',
            'fecha_creacion': datetime.now().isoformat(),
            'informacion_general': {},
            'contenido_secciones': {},
            'referencias': getattr(app_instance, 'referencias', []),
            'secciones_activas': getattr(app_instance, 'secciones_activas', []),
            'secciones_disponibles': getattr(app_instance, 'secciones_disponibles', {}),
            'formato_config': getattr(app_instance, 'formato_config', {}),
            'imagenes': {
                'encabezado_personalizado': getattr(app_instance, 'encabezado_personalizado', None),
                'insignia_personalizada': getattr(app_instance, 'insignia_personalizada', None),
                'ruta_encabezado': getattr(app_instance, 'ruta_encabezado', None),
                'ruta_insignia': getattr(app_instance, 'ruta_insignia', None)
            },
            'estadisticas': getattr(app_instance, 'stats', {}),
            'configuracion_ui': {
                'tema': getattr(app_instance, 'tema_actual', 'dark'),
                'escala_fuente': getattr(app_instance.font_manager, 'scale', 1.0) if hasattr(app_instance, 'font_manager') else 1.0
            }
        }
        
        # Información general
        if hasattr(app_instance, 'proyecto_data'):
            for key, entry in app_instance.proyecto_data.items():
                if hasattr(entry, 'get'):
                    proyecto_completo['informacion_general'][key] = entry.get()
        
        # Contenido de secciones
        if hasattr(app_instance, 'content_texts'):
            for key, text_widget in app_instance.content_texts.items():
                if hasattr(text_widget, 'get'):
                    proyecto_completo['contenido_secciones'][key] = text_widget.get("1.0", "end")
        
        return proyecto_completo
    
    def _validar_estructura_proyecto(self, proyecto):
        """Valida que el proyecto tenga la estructura correcta"""
        campos_requeridos = ['version', 'informacion_general', 'contenido_secciones']
        
        for campo in campos_requeridos:
            if campo not in proyecto:
                messagebox.showerror("❌ Archivo Inválido", 
                    f"El archivo no contiene el campo requerido: {campo}")
                return False
        
        return True
    
    def _cargar_informacion_general(self, proyecto, app_instance):
        """Carga la información general del proyecto"""
        if 'informacion_general' in proyecto and hasattr(app_instance, 'proyecto_data'):
            for key, value in proyecto['informacion_general'].items():
                if key in app_instance.proyecto_data and hasattr(app_instance.proyecto_data[key], 'delete'):
                    app_instance.proyecto_data[key].delete(0, "end")
                    app_instance.proyecto_data[key].insert(0, str(value))
    
    def _cargar_contenido_secciones(self, proyecto, app_instance):
        """Carga el contenido de las secciones"""
        if 'contenido_secciones' in proyecto and hasattr(app_instance, 'content_texts'):
            for key, content in proyecto['contenido_secciones'].items():
                if key in app_instance.content_texts and hasattr(app_instance.content_texts[key], 'delete'):
                    app_instance.content_texts[key].delete("1.0", "end")
                    app_instance.content_texts[key].insert("1.0", content)
    
    def _cargar_referencias(self, proyecto, app_instance):
        """Carga las referencias bibliográficas"""
        if 'referencias' in proyecto:
            app_instance.referencias = proyecto['referencias']
            if hasattr(app_instance, 'actualizar_lista_referencias'):
                app_instance.actualizar_lista_referencias()
    
    def _cargar_configuracion_formato(self, proyecto, app_instance):
        """Carga la configuración de formato"""
        if 'formato_config' in proyecto:
            app_instance.formato_config.update(proyecto['formato_config'])
    
    def _cargar_imagenes_personalizadas(self, proyecto, app_instance):
        """Carga las rutas de imágenes personalizadas"""
        if 'imagenes' in proyecto:
            imagenes = proyecto['imagenes']
            for attr in ['encabezado_personalizado', 'insignia_personalizada', 'ruta_encabezado', 'ruta_insignia']:
                if attr in imagenes:
                    setattr(app_instance, attr, imagenes[attr])
    
    def _cargar_configuracion_secciones(self, proyecto, app_instance):
        """Carga la configuración de secciones"""
        if 'secciones_disponibles' in proyecto:
            app_instance.secciones_disponibles.update(proyecto['secciones_disponibles'])
        
        if 'secciones_activas' in proyecto:
            app_instance.secciones_activas = proyecto['secciones_activas']
    
    def _actualizar_interfaz_despues_carga(self, app_instance):
        """Actualiza la interfaz después de cargar un proyecto"""
        try:
            # Actualizar lista de referencias
            if hasattr(app_instance, 'actualizar_lista_referencias'):
                app_instance.actualizar_lista_referencias()
            
            # Recrear pestañas de contenido
            if hasattr(app_instance, 'crear_pestanas_contenido'):
                app_instance.crear_pestanas_contenido()
            
            # Actualizar estadísticas
            if hasattr(app_instance, '_actualizar_estadisticas'):
                app_instance._actualizar_estadisticas()
            
        except Exception as e:
            logger.warning(f"Error actualizando interfaz: {e}")
    
    def _hay_cambios_sin_guardar(self, app_instance):
        """Verifica si hay cambios sin guardar"""
        if self.last_save_hash is None:
            return True  # Proyecto nuevo
        
        proyecto_actual = self._recopilar_datos_proyecto(app_instance)
        hash_actual = self._calcular_hash_proyecto(proyecto_actual)
        
        return hash_actual != self.last_save_hash
    
    def _hay_cambios_desde_ultimo_guardado(self, app_instance):
        """Verifica si hay cambios desde el último guardado/auto-guardado"""
        return self._hay_cambios_sin_guardar(app_instance)
    
    def _calcular_hash_proyecto(self, proyecto):
        """Calcula hash MD5 del proyecto para detectar cambios"""
        try:
            # Crear copia sin campos que cambian automáticamente
            proyecto_limpio = deepcopy(proyecto)
            if 'fecha_creacion' in proyecto_limpio:
                del proyecto_limpio['fecha_creacion']
            if 'estadisticas' in proyecto_limpio:
                del proyecto_limpio['estadisticas']
            
            proyecto_str = json.dumps(proyecto_limpio, sort_keys=True, ensure_ascii=False)
            return hashlib.md5(proyecto_str.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.warning(f"Error calculando hash: {e}")
            return None
    
    def _generar_nombre_archivo(self, app_instance):
        """Genera un nombre de archivo sugerido"""
        try:
            if hasattr(app_instance, 'proyecto_data') and 'titulo' in app_instance.proyecto_data:
                titulo = app_instance.proyecto_data['titulo'].get()
                if titulo:
                    # Limpiar título para nombre de archivo
                    titulo_limpio = "".join(c for c in titulo if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    return f"{titulo_limpio[:50]}.json"
        except:
            pass
        
        return f"proyecto_academico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    def _limpiar_proyecto(self, app_instance):
        """Limpia todos los datos del proyecto"""
        # Limpiar información general
        if hasattr(app_instance, 'proyecto_data'):
            for entry in app_instance.proyecto_data.values():
                if hasattr(entry, 'delete'):
                    entry.delete(0, "end")
        
        # Limpiar contenido de secciones
        if hasattr(app_instance, 'content_texts'):
            for text_widget in app_instance.content_texts.values():
                if hasattr(text_widget, 'delete'):
                    text_widget.delete("1.0", "end")
        
        # Limpiar referencias
        app_instance.referencias = []
        
        # Limpiar imágenes personalizadas
        app_instance.encabezado_personalizado = None
        app_instance.insignia_personalizada = None
    
    def _inicializar_valores_defecto(self, app_instance):
        """Inicializa valores por defecto para nuevo proyecto"""
        # Restaurar secciones por defecto
        if hasattr(app_instance, '_get_secciones_iniciales'):
            app_instance.secciones_disponibles = app_instance._get_secciones_iniciales()
            app_instance.secciones_activas = list(app_instance.secciones_disponibles.keys())
    
    def _crear_backup_automatico(self, proyecto_completo):
        """Crea un backup automático al guardar"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = self.autosave_dir / f"backup_{timestamp}.json"
            
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(proyecto_completo, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Backup automático creado: {backup_filename}")
            
        except Exception as e:
            logger.warning(f"Error creando backup automático: {e}")
    
    def _programar_auto_guardado(self, app_instance):
        """Programa el próximo auto-guardado"""
        if hasattr(app_instance, 'root'):
            interval = AUTOSAVE_CONFIG.get('interval', 300000)  # 5 minutos por defecto
            app_instance.root.after(interval, lambda: self.auto_save_project(app_instance))
    
    def _limpiar_autosaves_antiguos(self):
        """Limpia auto-guardados antiguos para ahorrar espacio"""
        try:
            max_backups = AUTOSAVE_CONFIG.get('max_backups', 10)
            
            # Obtener archivos de auto-guardado ordenados por fecha
            autosave_files = sorted(
                self.autosave_dir.glob("autosave_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Eliminar archivos excedentes
            for file_to_delete in autosave_files[max_backups:]:
                file_to_delete.unlink()
                logger.debug(f"Auto-guardado antiguo eliminado: {file_to_delete}")
                
        except Exception as e:
            logger.warning(f"Error limpiando auto-guardados antiguos: {e}")