"""
Gestor de configuraciones para el Proyecto Académico Generator
Maneja guardado, carga, configuraciones por defecto y auto-guardado
"""

import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox

class ConfigManager:
    """Maneja todas las configuraciones del sistema"""
    
    def __init__(self, app):
        self.app = app
        self.config_dir = self.get_config_directory()
        self.auto_save_path = os.path.join(self.config_dir, "auto_save.json")
        self.config_path = os.path.join(self.config_dir, "config.json")
        
        # Crear directorio de configuración si no existe
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Cargar configuración principal
        self.main_config = self.load_main_config()
    
    def get_config_directory(self):
        """Obtiene el directorio de configuración"""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(script_dir, "data")
    
    def get_default_format_config(self):
        """Configuración de formato por defecto"""
        return {
            'fuente_texto': 'Times New Roman',
            'tamaño_texto': 12,
            'fuente_titulo': 'Times New Roman', 
            'tamaño_titulo': 14,
            'interlineado': 2.0,
            'margen': 2.54,
            'justificado': True,
            'sangria': True,
            'salto_pagina_secciones': True,
            'conservar_siguiente': True,
            'control_lineas_viudas': True
        }
    
    def get_default_sections(self):
        """Secciones por defecto del sistema"""
        return {
            "resumen": {
                "titulo": "📄 Resumen", 
                "instruccion": "Resumen ejecutivo del proyecto (150-300 palabras)",
                "requerida": False,
                "capitulo": False,
                "orden": 1
            },
            "introduccion": {
                "titulo": "🔍 Introducción", 
                "instruccion": "Presenta el tema, contexto e importancia del proyecto",
                "requerida": True,
                "capitulo": False,
                "orden": 2
            },
            "planteamiento": {
                "titulo": "❓ Planteamiento del Problema", 
                "instruccion": "Define claramente el problema a investigar",
                "requerida": True,
                "capitulo": False,
                "orden": 3
            },
            "preguntas": {
                "titulo": "❔ Preguntas de Investigación", 
                "instruccion": "Pregunta general y preguntas específicas",
                "requerida": True,
                "capitulo": False,
                "orden": 4
            },
            "justificacion": {
                "titulo": "💡 Justificación", 
                "instruccion": "Explica por qué es importante investigar este tema",
                "requerida": True,
                "capitulo": False,
                "orden": 5
            },
            "objetivos": {
                "titulo": "🎯 Objetivos", 
                "instruccion": "Objetivo general y específicos (verbos en infinitivo)",
                "requerida": True,
                "capitulo": False,
                "orden": 6
            },
            "marco_teorico": {
                "titulo": "📖 Marco Teórico", 
                "instruccion": "Base teórica y antecedentes (INCLUIR CITAS)",
                "requerida": True,
                "capitulo": False,
                "orden": 7
            },
            "metodologia": {
                "titulo": "⚙️ Metodología", 
                "instruccion": "Tipo de estudio y técnicas de recolección de datos",
                "requerida": True,
                "capitulo": False,
                "orden": 8
            },
            "desarrollo": {
                "titulo": "⚙️ Desarrollo", 
                "instruccion": "Proceso de investigación paso a paso",
                "requerida": False,
                "capitulo": False,
                "orden": 9
            },
            "resultados": {
                "titulo": "📊 Resultados", 
                "instruccion": "Datos obtenidos (incluir gráficos, tablas)",
                "requerida": False,
                "capitulo": False,
                "orden": 10
            },
            "discusion": {
                "titulo": "💬 Discusión", 
                "instruccion": "Confronta resultados con la teoría del marco teórico",
                "requerida": False,
                "capitulo": False,
                "orden": 11
            },
            "conclusiones": {
                "titulo": "✅ Conclusiones", 
                "instruccion": "Hallazgos principales y respuestas a los objetivos",
                "requerida": True,
                "capitulo": False,
                "orden": 12
            }
        }
    
    def load_main_config(self):
        """Carga configuración principal del sistema"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_main_config()
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return self.get_default_main_config()
    
    def get_default_main_config(self):
        """Configuración principal por defecto"""
        return {
            'version': '2.0',
            'auto_save_enabled': True,
            'auto_save_interval': 300,  # 5 minutos en segundos
            'theme': 'dark',
            'color_theme': 'blue',
            'show_tips': True,
            'compact_mode': False,
            'language': 'es',
            'backup_enabled': True,
            'max_backups': 10
        }
    
    def save_main_config(self):
        """Guarda configuración principal"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.main_config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def auto_save(self, project_data):
        """Realiza auto-guardado del proyecto"""
        try:
            auto_save_data = {
                'version': '2.0',
                'tipo': 'auto_save',
                'timestamp': datetime.now().isoformat(),
                'project_data': project_data
            }
            
            with open(self.auto_save_path, 'w', encoding='utf-8') as f:
                json.dump(auto_save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error en auto-guardado: {e}")
            return False
    
    def load_auto_save(self):
        """Carga el auto-guardado si existe"""
        try:
            if os.path.exists(self.auto_save_path):
                with open(self.auto_save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('project_data')
            return None
        except Exception as e:
            print(f"Error cargando auto-guardado: {e}")
            return None
    
    def save_project(self, project_data):
        """Guarda proyecto con diálogo de archivo"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("Proyecto Académico", "*.json"), 
                    ("Todos los archivos", "*.*")
                ],
                title="Guardar Proyecto Académico"
            )
            
            if filename:
                save_data = {
                    'version': '2.0',
                    'tipo': 'proyecto_completo',
                    'fecha_guardado': datetime.now().isoformat(),
                    'project_data': project_data
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo(
                    "💾 Guardado", 
                    f"Proyecto guardado exitosamente:\n{os.path.basename(filename)}"
                )
                return True
            return False
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar proyecto:\n{str(e)}")
            return False
    
    def load_project(self):
        """Carga proyecto con diálogo de archivo"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[
                    ("Proyecto Académico", "*.json"), 
                    ("Todos los archivos", "*.*")
                ],
                title="Cargar Proyecto Académico"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Verificar versión
                version = data.get('version', '1.0')
                if version != '2.0':
                    messagebox.showwarning(
                        "⚠️ Versión", 
                        "Este proyecto fue creado con una versión anterior.\n"
                        "Algunas características pueden no funcionar correctamente."
                    )
                
                messagebox.showinfo(
                    "📂 Cargado", 
                    f"Proyecto cargado exitosamente:\n{os.path.basename(filename)}"
                )
                
                return data.get('project_data')
            
            return None
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar proyecto:\n{str(e)}")
            return None
    
    def export_configuration(self, config_data):
        """Exporta configuración a archivo"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Configuración", "*.json")],
                title="Exportar Configuración"
            )
            
            if filename:
                export_data = {
                    'version': '2.0',
                    'tipo': 'configuracion',
                    'fecha_export': datetime.now().isoformat(),
                    'configuracion': config_data
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("📤 Exportado", "Configuración exportada exitosamente")
                return True
            return False
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al exportar:\n{str(e)}")
            return False
    
    def import_configuration(self):
        """Importa configuración desde archivo"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Configuración", "*.json")],
                title="Importar Configuración"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('tipo') != 'configuracion':
                    messagebox.showerror("❌ Error", "El archivo no es una configuración válida")
                    return None
                
                messagebox.showinfo("📥 Importado", "Configuración importada exitosamente")
                return data.get('configuracion')
            
            return None
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al importar:\n{str(e)}")
            return None
    
    def create_backup(self, project_data):
        """Crea respaldo del proyecto"""
        try:
            backup_dir = os.path.join(self.config_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            backup_data = {
                'version': '2.0',
                'tipo': 'backup',
                'timestamp': datetime.now().isoformat(),
                'project_data': project_data
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            # Limpiar backups antiguos
            self.cleanup_old_backups(backup_dir)
            
            return backup_path
            
        except Exception as e:
            print(f"Error creando backup: {e}")
            return None
    
    def cleanup_old_backups(self, backup_dir):
        """Limpia backups antiguos manteniendo solo los más recientes"""
        try:
            max_backups = self.main_config.get('max_backups', 10)
            
            # Obtener lista de backups
            backups = []
            for filename in os.listdir(backup_dir):
                if filename.startswith('backup_') and filename.endswith('.json'):
                    filepath = os.path.join(backup_dir, filename)
                    backups.append((filepath, os.path.getctime(filepath)))
            
            # Ordenar por fecha y eliminar los más antiguos
            backups.sort(key=lambda x: x[1], reverse=True)
            
            for filepath, _ in backups[max_backups:]:
                try:
                    os.remove(filepath)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error limpiando backups: {e}")
    
    def get_recent_backups(self):
        """Obtiene lista de backups recientes"""
        try:
            backup_dir = os.path.join(self.config_dir, "backups")
            if not os.path.exists(backup_dir):
                return []
            
            backups = []
            for filename in os.listdir(backup_dir):
                if filename.startswith('backup_') and filename.endswith('.json'):
                    filepath = os.path.join(backup_dir, filename)
                    timestamp = os.path.getctime(filepath)
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'timestamp': timestamp,
                        'date_str': datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # Ordenar por fecha (más reciente primero)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            return backups
            
        except Exception as e:
            print(f"Error obteniendo backups: {e}")
            return []
    
    def update_config(self, key, value):
        """Actualiza un valor en la configuración principal"""
        self.main_config[key] = value
        self.save_main_config()
    
    def get_config(self, key, default=None):
        """Obtiene un valor de la configuración principal"""
        return self.main_config.get(key, default)