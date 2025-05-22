"""
Gestor de plantillas para el Generador de Proyectos Académicos
Maneja plantillas predefinidas y personalizadas con estructura académica profesional
"""

import os
import json
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import copy

class TemplateManager:
    """Gestiona plantillas académicas predefinidas y personalizadas"""
    
    def __init__(self, app):
        self.app = app
        self.templates_dir = self.get_templates_directory()
        self.plantillas_predefinidas = self.get_plantillas_predefinidas()
        self.plantillas_personalizadas = []
        
        # Inicializar directorio y cargar plantillas
        self.inicializar_sistema_plantillas()
        self.cargar_plantillas_personalizadas()
    
    def get_templates_directory(self):
        """Obtiene el directorio de plantillas"""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(script_dir, "resources", "templates")
    
    def get_plantillas_predefinidas(self):
        """Define las plantillas predefinidas del sistema"""
        return {
            "academico_basico": {
                "nombre": "📚 Académico Básico",
                "descripcion": "Estructura estándar para proyectos académicos de grado",
                "categoria": "Grado",
                "autor": "Sistema",
                "version": "1.0",
                "fecha_creacion": "2025-01-01",
                "formato": {
                    'fuente_texto': 'Times New Roman',
                    'tamaño_texto': 12,
                    'fuente_titulo': 'Times New Roman',
                    'tamaño_titulo': 14,
                    'interlineado': 2.0,
                    'margen': 2.54,
                    'justificado': True,
                    'sangria': True,
                    'salto_pagina_secciones': True
                },
                "secciones": {
                    "portada": {"orden": 1, "requerida": True, "tipo": "portada"},
                    "resumen": {"orden": 2, "requerida": True, "tipo": "contenido"},
                    "introduccion": {"orden": 3, "requerida": True, "tipo": "contenido"},
                    "planteamiento": {"orden": 4, "requerida": True, "tipo": "contenido"},
                    "justificacion": {"orden": 5, "requerida": True, "tipo": "contenido"},
                    "objetivos": {"orden": 6, "requerida": True, "tipo": "contenido"},
                    "marco_teorico": {"orden": 7, "requerida": True, "tipo": "contenido"},
                    "metodologia": {"orden": 8, "requerida": True, "tipo": "contenido"},
                    "conclusiones": {"orden": 9, "requerida": True, "tipo": "contenido"},
                    "referencias": {"orden": 10, "requerida": True, "tipo": "referencias"}
                },
                "configuracion": {
                    "min_referencias": 5,
                    "min_paginas": 20,
                    "formato_citas": "APA",
                    "incluir_anexos": True,
                    "numeracion_paginas": True
                }
            },
            
            "cientifico_avanzado": {
                "nombre": "🔬 Científico Avanzado",
                "descripcion": "Estructura completa para investigación científica y publicación",
                "categoria": "Investigación",
                "autor": "Sistema",
                "version": "1.0",
                "fecha_creacion": "2025-01-01",
                "formato": {
                    'fuente_texto': 'Times New Roman',
                    'tamaño_texto': 12,
                    'fuente_titulo': 'Times New Roman',
                    'tamaño_titulo': 14,
                    'interlineado': 2.0,
                    'margen': 2.54,
                    'justificado': True,
                    'sangria': True,
                    'salto_pagina_secciones': True
                },
                "secciones": {
                    "portada": {"orden": 1, "requerida": True, "tipo": "portada"},
                    "resumen": {"orden": 2, "requerida": True, "tipo": "contenido"},
                    "abstract": {"orden": 3, "requerida": True, "tipo": "contenido"},
                    "introduccion": {"orden": 4, "requerida": True, "tipo": "contenido"},
                    "revision_literatura": {"orden": 5, "requerida": True, "tipo": "contenido"},
                    "planteamiento": {"orden": 6, "requerida": True, "tipo": "contenido"},
                    "hipotesis": {"orden": 7, "requerida": True, "tipo": "contenido"},
                    "objetivos": {"orden": 8, "requerida": True, "tipo": "contenido"},
                    "metodologia": {"orden": 9, "requerida": True, "tipo": "contenido"},
                    "resultados": {"orden": 10, "requerida": True, "tipo": "contenido"},
                    "discusion": {"orden": 11, "requerida": True, "tipo": "contenido"},
                    "conclusiones": {"orden": 12, "requerida": True, "tipo": "contenido"},
                    "limitaciones": {"orden": 13, "requerida": False, "tipo": "contenido"},
                    "recomendaciones": {"orden": 14, "requerida": False, "tipo": "contenido"},
                    "referencias": {"orden": 15, "requerida": True, "tipo": "referencias"},
                    "anexos": {"orden": 16, "requerida": False, "tipo": "anexos"}
                },
                "configuracion": {
                    "min_referencias": 15,
                    "min_paginas": 50,
                    "formato_citas": "APA",
                    "incluir_anexos": True,
                    "numeracion_paginas": True,
                    "incluir_abstract": True,
                    "incluir_palabras_clave": True
                }
            },
            
            "tesis_doctoral": {
                "nombre": "🎓 Tesis Doctoral",
                "descripcion": "Estructura completa para tesis de doctorado con capítulos",
                "categoria": "Doctorado",
                "autor": "Sistema",
                "version": "1.0",
                "fecha_creacion": "2025-01-01",
                "formato": {
                    'fuente_texto': 'Times New Roman',
                    'tamaño_texto': 12,
                    'fuente_titulo': 'Times New Roman',
                    'tamaño_titulo': 16,
                    'interlineado': 2.0,
                    'margen': 3.0,
                    'justificado': True,
                    'sangria': True,
                    'salto_pagina_secciones': True
                },
                "secciones": {
                    "portada": {"orden": 1, "requerida": True, "tipo": "portada"},
                    "dedicatoria": {"orden": 2, "requerida": False, "tipo": "contenido"},
                    "agradecimientos": {"orden": 3, "requerida": False, "tipo": "contenido"},
                    "resumen": {"orden": 4, "requerida": True, "tipo": "contenido"},
                    "abstract": {"orden": 5, "requerida": True, "tipo": "contenido"},
                    "indice": {"orden": 6, "requerida": True, "tipo": "indice"},
                    "capitulo_1_introduccion": {"orden": 7, "requerida": True, "tipo": "capitulo"},
                    "capitulo_2_marco_teorico": {"orden": 8, "requerida": True, "tipo": "capitulo"},
                    "capitulo_3_metodologia": {"orden": 9, "requerida": True, "tipo": "capitulo"},
                    "capitulo_4_resultados": {"orden": 10, "requerida": True, "tipo": "capitulo"},
                    "capitulo_5_discusion": {"orden": 11, "requerida": True, "tipo": "capitulo"},
                    "capitulo_6_conclusiones": {"orden": 12, "requerida": True, "tipo": "capitulo"},
                    "referencias": {"orden": 13, "requerida": True, "tipo": "referencias"},
                    "anexos": {"orden": 14, "requerida": False, "tipo": "anexos"}
                },
                "configuracion": {
                    "min_referencias": 50,
                    "min_paginas": 150,
                    "formato_citas": "APA",
                    "incluir_anexos": True,
                    "numeracion_paginas": True,
                    "incluir_abstract": True,
                    "incluir_palabras_clave": True,
                    "estructura_capitulos": True
                }
            }
        }
    
    def inicializar_sistema_plantillas(self):
        """Inicializa el sistema de plantillas"""
        try:
            # Crear directorio de plantillas
            os.makedirs(self.templates_dir, exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['predefinidas', 'personalizadas', 'importadas']
            for subdir in subdirs:
                os.makedirs(os.path.join(self.templates_dir, subdir), exist_ok=True)
            
            # Guardar plantillas predefinidas si no existen
            self.guardar_plantillas_predefinidas()
            
            return True
        except Exception as e:
            print(f"Error inicializando sistema de plantillas: {e}")
            return False
    
    def guardar_plantillas_predefinidas(self):
        """Guarda las plantillas predefinidas en archivos JSON"""
        try:
            predefinidas_dir = os.path.join(self.templates_dir, 'predefinidas')
            
            for template_id, template_data in self.plantillas_predefinidas.items():
                filepath = os.path.join(predefinidas_dir, f"{template_id}.json")
                
                # Solo guardar si no existe o si la versión es diferente
                if not os.path.exists(filepath) or self.necesita_actualizacion(filepath, template_data):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error guardando plantillas predefinidas: {e}")
            return False
    
    def necesita_actualizacion(self, filepath, template_data):
        """Verifica si una plantilla necesita actualización"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            return existing_data.get('version') != template_data.get('version')
        except:
            return True
    
    def cargar_plantillas_personalizadas(self):
        """Carga las plantillas personalizadas desde archivos"""
        try:
            personalizadas_dir = os.path.join(self.templates_dir, 'personalizadas')
            
            if not os.path.exists(personalizadas_dir):
                return []
            
            plantillas = []
            
            for filename in os.listdir(personalizadas_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(personalizadas_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                        
                        # Validar estructura básica
                        if self.validar_plantilla(template_data):
                            template_data['id'] = filename[:-5]  # Quitar .json
                            template_data['filepath'] = filepath
                            plantillas.append(template_data)
                    
                    except Exception as e:
                        print(f"Error cargando plantilla {filename}: {e}")
            
            self.plantillas_personalizadas = plantillas
            return plantillas
            
        except Exception as e:
            print(f"Error cargando plantillas personalizadas: {e}")
            return []
    
    def validar_plantilla(self, template_data):
        """Valida que una plantilla tenga la estructura correcta"""
        campos_requeridos = ['nombre', 'descripcion', 'secciones', 'formato']
        
        for campo in campos_requeridos:
            if campo not in template_data:
                return False
        
        # Validar que tenga al menos una sección
        if not template_data['secciones']:
            return False
        
        return True
    
    def obtener_todas_plantillas(self):
        """Obtiene todas las plantillas disponibles (predefinidas + personalizadas)"""
        todas_plantillas = []
        
        # Agregar predefinidas
        for template_id, template_data in self.plantillas_predefinidas.items():
            template_copy = template_data.copy()
            template_copy['id'] = template_id
            template_copy['tipo'] = 'predefinida'
            todas_plantillas.append(template_copy)
        
        # Agregar personalizadas
        for template_data in self.plantillas_personalizadas:
            template_copy = template_data.copy()
            template_copy['tipo'] = 'personalizada'
            todas_plantillas.append(template_copy)
        
        return todas_plantillas
    
    def aplicar_plantilla(self, template_id, aplicar_formato=True, aplicar_secciones=True):
        """Aplica una plantilla al proyecto actual"""
        try:
            # Buscar la plantilla
            plantilla = self.obtener_plantilla_por_id(template_id)
            
            if not plantilla:
                messagebox.showerror("❌ Error", f"Plantilla '{template_id}' no encontrada")
                return False
            
            # Confirmar aplicación
            respuesta = messagebox.askyesno(
                "🎨 Aplicar Plantilla",
                f"¿Aplicar la plantilla '{plantilla['nombre']}'?\n\n"
                f"Esto modificará:\n"
                f"{'• Formato del documento' if aplicar_formato else ''}\n"
                f"{'• Estructura de secciones' if aplicar_secciones else ''}\n\n"
                f"Descripción: {plantilla['descripcion']}"
            )
            
            if not respuesta:
                return False
            
            # Crear respaldo antes de aplicar
            if hasattr(self.app, 'backup_manager'):
                self.app.backup_manager.crear_respaldo_manual("Antes de aplicar plantilla")
            
            # Aplicar formato si se solicita
            if aplicar_formato and 'formato' in plantilla:
                self.aplicar_formato_plantilla(plantilla['formato'])
            
            # Aplicar estructura de secciones si se solicita
            if aplicar_secciones and 'secciones' in plantilla:
                self.aplicar_secciones_plantilla(plantilla['secciones'])
            
            # Actualizar interfaz
            if hasattr(self.app, 'actualizar_interfaz_completa'):
                self.app.actualizar_interfaz_completa()
            
            messagebox.showinfo(
                "✅ Plantilla Aplicada",
                f"Plantilla '{plantilla['nombre']}' aplicada correctamente.\n\n"
                f"Se ha creado un respaldo automático del estado anterior."
            )
            
            return True
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error aplicando plantilla:\n{str(e)}")
            return False
    
    def obtener_plantilla_por_id(self, template_id):
        """Obtiene una plantilla específica por su ID"""
        # Buscar en predefinidas
        if template_id in self.plantillas_predefinidas:
            plantilla = self.plantillas_predefinidas[template_id].copy()
            plantilla['id'] = template_id
            plantilla['tipo'] = 'predefinida'
            return plantilla
        
        # Buscar en personalizadas
        for plantilla in self.plantillas_personalizadas:
            if plantilla.get('id') == template_id:
                return plantilla
        
        return None
    
    def aplicar_formato_plantilla(self, formato_config):
        """Aplica la configuración de formato de la plantilla"""
        try:
            # Actualizar configuración de formato
            self.app.formato_config.update(formato_config)
            
            # Actualizar interfaz de formato si existe
            if hasattr(self.app, 'actualizar_controles_formato'):
                self.app.actualizar_controles_formato()
            
            return True
        except Exception as e:
            print(f"Error aplicando formato: {e}")
            return False
    
    def aplicar_secciones_plantilla(self, secciones_config):
        """Aplica la estructura de secciones de la plantilla"""
        try:
            # Convertir secciones de plantilla a formato del sistema
            nuevas_secciones = {}
            
            for seccion_id, seccion_config in secciones_config.items():
                # Crear configuración de sección
                nueva_seccion = {
                    'titulo': self.generar_titulo_seccion(seccion_id),
                    'instruccion': self.generar_instruccion_seccion(seccion_id),
                    'requerida': seccion_config.get('requerida', False),
                    'capitulo': seccion_config.get('tipo') == 'capitulo',
                    'orden': seccion_config.get('orden', 99)
                }
                
                nuevas_secciones[seccion_id] = nueva_seccion
            
            # Actualizar secciones del sistema
            self.app.secciones_disponibles = новas_secciones
            self.app.secciones_activas = list(nuevas_secciones.keys())
            
            # Actualizar interfaz de secciones si existe
            if hasattr(self.app, 'actualizar_lista_secciones'):
                self.app.actualizar_lista_secciones()
            
            if hasattr(self.app, 'crear_pestanas_contenido'):
                self.app.crear_pestanas_contenido()
            
            return True
        except Exception as e:
            print(f"Error aplicando secciones: {e}")
            return False
    
    def generar_titulo_seccion(self, seccion_id):
        """Genera título amigable para una sección"""
        titulos_map = {
            'resumen': '📄 Resumen',
            'abstract': '🌐 Abstract',
            'introduccion': '🔍 Introducción',
            'planteamiento': '❓ Planteamiento del Problema',
            'justificacion': '💡 Justificación',
            'objetivos': '🎯 Objetivos',
            'marco_teorico': '📖 Marco Teórico',
            'revision_literatura': '📚 Revisión de Literatura',
            'hipotesis': '🔬 Hipótesis',
            'metodologia': '⚙️ Metodología',
            'resultados': '📊 Resultados',
            'discusion': '💬 Discusión',
            'conclusiones': '✅ Conclusiones',
            'limitaciones': '⚠️ Limitaciones',
            'recomendaciones': '💡 Recomendaciones',
            'dedicatoria': '💝 Dedicatoria',
            'agradecimientos': '🙏 Agradecimientos',
            'capitulo_1_introduccion': '📖 Capítulo I: Introducción',
            'capitulo_2_marco_teorico': '📚 Capítulo II: Marco Teórico',
            'capitulo_3_metodologia': '⚙️ Capítulo III: Metodología',
            'capitulo_4_resultados': '📊 Capítulo IV: Resultados',
            'capitulo_5_discusion': '💬 Capítulo V: Discusión',
            'capitulo_6_conclusiones': '✅ Capítulo VI: Conclusiones'
        }
        
        return titulos_map.get(seccion_id, seccion_id.replace('_', ' ').title())
    
    def generar_instruccion_seccion(self, seccion_id):
        """Genera instrucción para una sección"""
        instrucciones_map = {
            'resumen': 'Resumen ejecutivo del proyecto (150-300 palabras)',
            'abstract': 'Summary in English (150-300 words)',
            'introduccion': 'Presenta el tema, contexto e importancia del proyecto',
            'planteamiento': 'Define claramente el problema a investigar',
            'justificacion': 'Explica por qué es importante investigar este tema',
            'objetivos': 'Objetivo general y específicos (verbos en infinitivo)',
            'marco_teorico': 'Base teórica y antecedentes (INCLUIR CITAS)',
            'revision_literatura': 'Revisión sistemática de literatura científica',
            'hipotesis': 'Hipótesis de investigación y variables',
            'metodologia': 'Tipo de estudio y técnicas de recolección de datos',
            'resultados': 'Datos obtenidos (incluir gráficos, tablas)',
            'discusion': 'Confronta resultados con la teoría del marco teórico',
            'conclusiones': 'Hallazgos principales y respuestas a los objetivos',
            'limitaciones': 'Limitaciones del estudio y su impacto',
            'recomendaciones': 'Recomendaciones para futuras investigaciones'
        }
        
        return instrucciones_map.get(seccion_id, f'Desarrolla el contenido de {seccion_id.replace("_", " ")}')
    
    def crear_plantilla_personalizada(self, nombre, descripcion, basada_en=None):
        """Crea una nueva plantilla personalizada"""
        try:
            # Generar ID único
            template_id = self.generar_id_unico(nombre)
            
            # Crear estructura base
            if basada_en:
                plantilla_base = self.obtener_plantilla_por_id(basada_en)
                if plantilla_base:
                    nueva_plantilla = copy.deepcopy(plantilla_base)
                    # Actualizar metadatos
                    nueva_plantilla['nombre'] = nombre
                    nueva_plantilla['descripcion'] = descripcion
                    nueva_plantilla['autor'] = 'Usuario'
                    nueva_plantilla['tipo'] = 'personalizada'
                else:
                    nueva_plantilla = self.crear_plantilla_vacia(nombre, descripcion)
            else:
                nueva_plantilla = self.crear_plantilla_vacia(nombre, descripcion)
            
            # Configurar metadatos
            nueva_plantilla['id'] = template_id
            nueva_plantilla['fecha_creacion'] = datetime.now().isoformat()
            nueva_plantilla['fecha_modificacion'] = datetime.now().isoformat()
            nueva_plantilla['version'] = '1.0'
            
            # Guardar plantilla
            filepath = os.path.join(self.templates_dir, 'personalizadas', f"{template_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(nueva_plantilla, f, ensure_ascii=False, indent=2)
            
            # Agregar a lista
            nueva_plantilla['filepath'] = filepath
            self.plantillas_personalizadas.append(nueva_plantilla)
            
            return nueva_plantilla
            
        except Exception as e:
            print(f"Error creando plantilla personalizada: {e}")
            return None
    
    def crear_plantilla_vacia(self, nombre, descripcion):
        """Crea una plantilla vacía con estructura mínima"""
        return {
            'nombre': nombre,
            'descripcion': descripcion,
            'categoria': 'Personalizada',
            'autor': 'Usuario',
            'formato': {
                'fuente_texto': 'Times New Roman',
                'tamaño_texto': 12,
                'fuente_titulo': 'Times New Roman',
                'tamaño_titulo': 14,
                'interlineado': 2.0,
                'margen': 2.54,
                'justificado': True,
                'sangria': True,
                'salto_pagina_secciones': True
            },
            'secciones': {
                'introduccion': {'orden': 1, 'requerida': True, 'tipo': 'contenido'},
                'desarrollo': {'orden': 2, 'requerida': True, 'tipo': 'contenido'},
                'conclusiones': {'orden': 3, 'requerida': True, 'tipo': 'contenido'},
                'referencias': {'orden': 4, 'requerida': True, 'tipo': 'referencias'}
            },
            'configuracion': {
                'min_referencias': 3,
                'min_paginas': 10,
                'formato_citas': 'APA',
                'incluir_anexos': False,
                'numeracion_paginas': True
            }
        }
    
    def generar_id_unico(self, nombre):
        """Genera un ID único para una plantilla"""
        # Crear ID base desde el nombre
        id_base = "".join(c.lower() for c in nombre if c.isalnum() or c.isspace()).replace(' ', '_')
        id_base = id_base[:20]  # Limitar longitud
        
        # Verificar unicidad
        contador = 1
        id_propuesto = id_base
        
        while self.id_existe(id_propuesto):
            id_propuesto = f"{id_base}_{contador}"
            contador += 1
        
        return id_propuesto
    
    def id_existe(self, template_id):
        """Verifica si un ID de plantilla ya existe"""
        if template_id in self.plantillas_predefinidas:
            return True
        
        for plantilla in self.plantillas_personalizadas:
            if plantilla.get('id') == template_id:
                return True
        
        return False
    
    def gestionar_plantillas(self, parent_window):
        """Abre la ventana principal de gestión de plantillas"""
        template_window = ctk.CTkToplevel(parent_window)
        template_window.title("🎨 Gestión Avanzada de Plantillas")
        template_window.geometry("1100x800")
        template_window.transient(parent_window)
        template_window.grab_set()
        
        # Centrar ventana
        self.centrar_ventana(template_window, 1100, 800)
        
        # Crear interfaz
        self.crear_interfaz_gestion(template_window)
    
    def centrar_ventana(self, ventana, ancho, alto):
        """Centra una ventana en la pantalla"""
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def crear_interfaz_gestion(self, window):
        """Crea la interfaz principal de gestión de plantillas"""
        main_frame = ctk.CTkFrame(window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título principal
        title_label = ctk.CTkLabel(
            main_frame, text="🎨 Gestión Avanzada de Plantillas Académicas",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Botones principales
        self.crear_botones_principales(main_frame, window)
        
        # Pestañas de gestión
        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        
        # Pestaña de plantillas predefinidas
        predefinidas_tab = tabview.add("📚 Predefinidas")
        self.crear_tab_predefinidas(predefinidas_tab, window)
        
        # Pestaña de plantillas personalizadas
        personalizadas_tab = tabview.add("🎨 Personalizadas")
        self.crear_tab_personalizadas(personalizadas_tab, window)
        
        # Pestaña de crear nueva
        crear_tab = tabview.add("➕ Crear Nueva")
        self.crear_tab_crear_nueva(crear_tab, window)
        
        # Pestaña de importar/exportar
        importar_tab = tabview.add("🔄 Importar/Exportar")
        self.crear_tab_importar_exportar(importar_tab, window)
        
        # Botones de cierre
        self.crear_botones_cierre(main_frame, window)
    
    def crear_botones_principales(self, parent, window):
        """Crea los botones principales de la interfaz"""
        btn_frame = ctk.CTkFrame(parent, height=60, corner_radius=10)
        btn_frame.pack(fill="x", pady=(0, 15))
        btn_frame.pack_propagate(False)
        
        # Frame interno para centrar botones
        inner_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        inner_frame.pack(expand=True, fill="both", padx=15, pady=10)
        
        # Botón de aplicar plantilla rápida
        apply_btn = ctk.CTkButton(
            inner_frame, text="⚡ Aplicar Plantilla",
            command=lambda: self.aplicar_plantilla_rapida(window),
            width=150, height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        apply_btn.pack(side="left", padx=(0, 10))
        
        # Botón de vista previa
        preview_btn = ctk.CTkButton(
            inner_frame, text="👁️ Vista Previa",
            command=self.mostrar_vista_previa,
            width=130, height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="blue", hover_color="darkblue"
        )
        preview_btn.pack(side="left", padx=(0, 10))
        
        # Botón de ayuda
        help_btn = ctk.CTkButton(
            inner_frame, text="❓ Ayuda",
            command=self.mostrar_ayuda_plantillas,
            width=100, height=35, font=ctk.CTkFont(size=12, weight="bold")
        )
        help_btn.pack(side="right")
    
    def crear_tab_predefinidas(self, parent, window):
        """Crea la pestaña de plantillas predefinidas"""
        # Marco de información
        info_frame = ctk.CTkFrame(parent, fg_color="darkgreen", corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        info_label = ctk.CTkLabel(
            info_frame, text="📚 PLANTILLAS PREDEFINIDAS DEL SISTEMA",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        info_label.pack(pady=(15, 5))
        
        desc_label = ctk.CTkLabel(
            info_frame, text="Plantillas profesionales diseñadas para diferentes tipos de proyectos académicos",
            font=ctk.CTkFont(size=11), text_color="lightgreen"
        )
        desc_label.pack(pady=(0, 15))
        
        # Lista de plantillas predefinidas
        templates_frame = ctk.CTkScrollableFrame(parent, height=450)
        templates_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for template_id, template_data in self.plantillas_predefinidas.items():
            self.crear_item_plantilla(templates_frame, template_id, template_data, 'predefinida', window)
    
    def crear_tab_personalizadas(self, parent, window):
        """Crea la pestaña de plantillas personalizadas"""
        # Marco de información
        info_frame = ctk.CTkFrame(parent, fg_color="darkblue", corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        info_label = ctk.CTkLabel(
            info_frame, text="🎨 PLANTILLAS PERSONALIZADAS",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        info_label.pack(pady=(15, 5))
        
        desc_label = ctk.CTkLabel(
            info_frame, text=f"Tus plantillas personalizadas ({len(self.plantillas_personalizadas)} disponibles)",
            font=ctk.CTkFont(size=11), text_color="lightblue"
        )
        desc_label.pack(pady=(0, 15))
        
        # Lista de plantillas personalizadas
        self.personalizadas_frame = ctk.CTkScrollableFrame(parent, height=450)
        self.personalizadas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.actualizar_lista_personalizadas(window)
    
    def actualizar_lista_personalizadas(self, window):
        """Actualiza la lista de plantillas personalizadas"""
        # Limpiar frame
        for widget in self.personalizadas_frame.winfo_children():
            widget.destroy()
        
        if not self.plantillas_personalizadas:
            # Mensaje si no hay plantillas
            empty_label = ctk.CTkLabel(
                self.personalizadas_frame, 
                text="📝 No tienes plantillas personalizadas.\n\nCrea una nueva en la pestaña 'Crear Nueva'",
                font=ctk.CTkFont(size=14), text_color="gray"
            )
            empty_label.pack(pady=50)
        else:
            # Mostrar plantillas personalizadas
            for template_data in self.plantillas_personalizadas:
                self.crear_item_plantilla(
                    self.personalizadas_frame, 
                    template_data['id'], 
                    template_data, 
                    'personalizada', 
                    window
                )
    
    def crear_item_plantilla(self, parent, template_id, template_data, tipo, window):
        """Crea un item visual para mostrar una plantilla"""
        item_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)
        item_frame.pack(fill="x", padx=5, pady=10)
        
        # Información principal
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=15)
        
        # Nombre y badges
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Nombre
        name_label = ctk.CTkLabel(
            header_frame, text=template_data['nombre'],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        name_label.pack(side="left")
        
        # Badges
        badges_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        badges_frame.pack(side="right")
        
        # Badge de tipo
        tipo_color = "green" if tipo == 'predefinida' else "blue"
        tipo_badge = ctk.CTkLabel(
            badges_frame, text=tipo.title(),
            font=ctk.CTkFont(size=10, weight="bold"), 
            text_color=tipo_color
        )
        tipo_badge.pack(side="right", padx=(0, 10))
        
        # Badge de categoría
        categoria = template_data.get('categoria', 'General')
        cat_badge = ctk.CTkLabel(
            badges_frame, text=categoria,
            font=ctk.CTkFont(size=10), text_color="gray60"
        )
        cat_badge.pack(side="right", padx=(0, 10))
        
        # Descripción
        desc_label = ctk.CTkLabel(
            info_frame, text=template_data['descripcion'],
            font=ctk.CTkFont(size=12), text_color="gray70",
            wraplength=800, justify="left"
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Estadísticas
        stats_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Número de secciones
        num_secciones = len(template_data.get('secciones', {}))
        secciones_label = ctk.CTkLabel(
            stats_frame, text=f"📄 {num_secciones} secciones",
            font=ctk.CTkFont(size=10), text_color="gray60"
        )
        secciones_label.pack(side="left", padx=(0, 20))
        
        # Formato
        formato = template_data.get('formato', {})
        formato_text = f"📝 {formato.get('fuente_texto', 'Times New Roman')} {formato.get('tamaño_texto', 12)}pt"
        formato_label = ctk.CTkLabel(
            stats_frame, text=formato_text,
            font=ctk.CTkFont(size=10), text_color="gray60"
        )
        formato_label.pack(side="left", padx=(0, 20))
        
        # Referencias mínimas
        config = template_data.get('configuracion', {})
        min_refs = config.get('min_referencias', 0)
        if min_refs > 0:
            refs_label = ctk.CTkLabel(
                stats_frame, text=f"📚 {min_refs} refs mín.",
                font=ctk.CTkFont(size=10), text_color="gray60"
            )
            refs_label.pack(side="left")
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(10, 0))
        
        # Botón aplicar
        apply_btn = ctk.CTkButton(
            actions_frame, text="✅ Aplicar",
            command=lambda: self.aplicar_plantilla(template_id),
            width=80, height=30, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        apply_btn.pack(side="left", padx=(0, 10))
        
        # Botón vista previa
        preview_btn = ctk.CTkButton(
            actions_frame, text="👁️ Vista Previa",
            command=lambda: self.mostrar_vista_previa_plantilla(template_id),
            width=100, height=30, font=ctk.CTkFont(size=11),
            fg_color="blue", hover_color="darkblue"
        )
        preview_btn.pack(side="left", padx=(0, 10))
        
        # Botones adicionales para personalizadas
        if tipo == 'personalizada':
            edit_btn = ctk.CTkButton(
                actions_frame, text="✏️ Editar",
                command=lambda: self.editar_plantilla(template_id),
                width=80, height=30, font=ctk.CTkFont(size=11)
            )
            edit_btn.pack(side="left", padx=(0, 10))
            
            delete_btn = ctk.CTkButton(
                actions_frame, text="🗑️ Eliminar",
                command=lambda: self.eliminar_plantilla(template_id, window),
                width=90, height=30, font=ctk.CTkFont(size=11),
                fg_color="red", hover_color="darkred"
            )
            delete_btn.pack(side="right")
    
    def crear_tab_crear_nueva(self, parent, window):
        """Crea la pestaña para crear nueva plantilla"""
        # Marco de información
        info_frame = ctk.CTkFrame(parent, fg_color="purple", corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        info_label = ctk.CTkLabel(
            info_frame, text="➕ CREAR NUEVA PLANTILLA",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        info_label.pack(pady=(15, 5))
        
        desc_label = ctk.CTkLabel(
            info_frame, text="Crea tu propia plantilla personalizada desde cero o basada en una existente",
            font=ctk.CTkFont(size=11), text_color="lightgreen"
        )
        desc_label.pack(pady=(0, 15))
        
        # Formulario de creación
        form_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)
        form_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Campos del formulario
        fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20, pady=20)
        
        # Nombre
        ctk.CTkLabel(fields_frame, text="Nombre de la plantilla:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.nombre_entry = ctk.CTkEntry(fields_frame, placeholder_text="Ej: Mi Plantilla de Tesis", width=400)
        self.nombre_entry.pack(fill="x", pady=(0, 15))
        
        # Descripción
        ctk.CTkLabel(fields_frame, text="Descripción:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.descripcion_entry = ctk.CTkTextbox(fields_frame, height=80, width=400)
        self.descripcion_entry.pack(fill="x", pady=(0, 15))
        
        # Basada en plantilla existente
        ctk.CTkLabel(fields_frame, text="Basada en plantilla existente (opcional):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        todas_plantillas = self.obtener_todas_plantillas()
        plantillas_nombres = ["Ninguna (Crear desde cero)"] + [p['nombre'] for p in todas_plantillas]
        
        self.basada_en_combo = ctk.CTkComboBox(fields_frame, values=plantillas_nombres, width=400)
        self.basada_en_combo.pack(fill="x", pady=(0, 20))
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        actions_frame.pack(fill="x")
        
        create_btn = ctk.CTkButton(
            actions_frame, text="✅ Crear Plantilla",
            command=lambda: self.crear_plantilla_desde_formulario(window),
            width=150, height=40, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        create_btn.pack(side="left")
        
        clear_btn = ctk.CTkButton(
            actions_frame, text="🗑️ Limpiar",
            command=self.limpiar_formulario,
            width=100, height=40, font=ctk.CTkFont(size=12)
        )
        clear_btn.pack(side="right")
    
    def crear_tab_importar_exportar(self, parent, window):
        """Crea la pestaña de importar/exportar plantillas"""
        # Marco de información
        info_frame = ctk.CTkFrame(parent, fg_color="darkorange", corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        info_label = ctk.CTkLabel(
            info_frame, text="🔄 IMPORTAR Y EXPORTAR PLANTILLAS",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        info_label.pack(pady=(15, 5))
        
        desc_label = ctk.CTkLabel(
            info_frame, text="Comparte tus plantillas o importa plantillas de otros usuarios",
            font=ctk.CTkFont(size=11), text_color="white"
        )
        desc_label.pack(pady=(0, 15))
        
        # Sección de exportar
        export_frame = ctk.CTkFrame(parent, fg_color="darkgreen", corner_radius=10)
        export_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        export_title = ctk.CTkLabel(
            export_frame, text="📤 EXPORTAR PLANTILLAS",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        export_title.pack(pady=(15, 10))
        
        export_desc = ctk.CTkLabel(
            export_frame, text="Exporta tus plantillas personalizadas para compartir o hacer respaldo",
            font=ctk.CTkFont(size=11), text_color="lightgreen"
        )
        export_desc.pack(pady=(0, 15))
        
        export_actions = ctk.CTkFrame(export_frame, fg_color="transparent")
        export_actions.pack(fill="x", padx=20, pady=(0, 15))
        
        export_all_btn = ctk.CTkButton(
            export_actions, text="📦 Exportar Todas",
            command=self.exportar_todas_plantillas,
            width=150, height=35, font=ctk.CTkFont(size=12, weight="bold")
        )
        export_all_btn.pack(side="left", padx=(0, 10))
        
        export_selected_btn = ctk.CTkButton(
            export_actions, text="📋 Exportar Seleccionadas",
            command=self.exportar_plantillas_seleccionadas,
            width=180, height=35, font=ctk.CTkFont(size=12, weight="bold")
        )
        export_selected_btn.pack(side="left")
        
        # Sección de importar
        import_frame = ctk.CTkFrame(parent, fg_color="darkblue", corner_radius=10)
        import_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        import_title = ctk.CTkLabel(
            import_frame, text="📥 IMPORTAR PLANTILLAS",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        import_title.pack(pady=(15, 10))
        
        import_desc = ctk.CTkLabel(
            import_frame, text="Importa plantillas desde archivos JSON o paquetes de plantillas",
            font=ctk.CTkFont(size=11), text_color="lightblue"
        )
        import_desc.pack(pady=(0, 15))
        
        import_actions = ctk.CTkFrame(import_frame, fg_color="transparent")
        import_actions.pack(fill="x", padx=20, pady=(0, 15))
        
        import_file_btn = ctk.CTkButton(
            import_actions, text="📁 Importar Archivo",
            command=lambda: self.importar_plantilla_archivo(window),
            width=150, height=35, font=ctk.CTkFont(size=12, weight="bold")
        )
        import_file_btn.pack(side="left", padx=(0, 10))
        
        import_package_btn = ctk.CTkButton(
            import_actions, text="📦 Importar Paquete",
            command=lambda: self.importar_paquete_plantillas(window),
            width=150, height=35, font=ctk.CTkFont(size=12, weight="bold")
        )
        import_package_btn.pack(side="left")
    
    def crear_botones_cierre(self, parent, window):
        """Crea los botones de cierre de la ventana"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        help_btn = ctk.CTkButton(
            btn_frame, text="❓ Ayuda",
            command=self.mostrar_ayuda_plantillas,
            width=100, height=35
        )
        help_btn.pack(side="left")
        
        close_btn = ctk.CTkButton(
            btn_frame, text="✅ Cerrar",
            command=window.destroy,
            width=120, height=35
        )
        close_btn.pack(side="right")
    
    # Métodos de acción
    def aplicar_plantilla_rapida(self, parent_window):
        """Diálogo rápido para aplicar plantilla"""
        dialog = AplicarPlantillaDialog(parent_window, self)
        if dialog.result:
            self.aplicar_plantilla(dialog.result['template_id'], 
                                 dialog.result['aplicar_formato'], 
                                 dialog.result['aplicar_secciones'])
    
    def mostrar_vista_previa(self):
        """Muestra vista previa de plantilla seleccionada"""
        messagebox.showinfo("👁️ Vista Previa", 
            "🚧 Función en desarrollo\n\n"
            "Próximamente podrás ver una vista previa detallada de cada plantilla con:\n"
            "• Estructura de secciones\n"
            "• Configuración de formato\n"
            "• Ejemplo de documento generado")
    
    def mostrar_vista_previa_plantilla(self, template_id):
        """Muestra vista previa de una plantilla específica"""
        plantilla = self.obtener_plantilla_por_id(template_id)
        if plantilla:
            # Crear ventana de vista previa
            preview_window = ctk.CTkToplevel(self.app.root)
            preview_window.title(f"👁️ Vista Previa: {plantilla['nombre']}")
            preview_window.geometry("800x600")
            preview_window.transient(self.app.root)
            
            self.crear_vista_previa_plantilla(preview_window, plantilla)
    
    def crear_vista_previa_plantilla(self, window, plantilla):
        """Crea la interfaz de vista previa de plantilla"""
        main_frame = ctk.CTkFrame(window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text=f"👁️ Vista Previa: {plantilla['nombre']}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Información general
        info_frame = ctk.CTkFrame(main_frame, fg_color="darkblue", corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_text = f"📝 {plantilla['descripcion']}\n"
        info_text += f"📂 Categoría: {plantilla.get('categoria', 'General')}\n"
        info_text += f"👤 Autor: {plantilla.get('autor', 'Desconocido')}\n"
        info_text += f"📅 Creado: {plantilla.get('fecha_creacion', 'N/A')}"
        
        info_label = ctk.CTkLabel(
            info_frame, text=info_text, font=ctk.CTkFont(size=12),
            text_color="white", justify="left"
        )
        info_label.pack(padx=15, pady=15)
        
        # Secciones
        sections_frame = ctk.CTkFrame(main_frame, fg_color="darkgreen", corner_radius=10)
        sections_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        sections_title = ctk.CTkLabel(
            sections_frame, text="📋 ESTRUCTURA DE SECCIONES",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        sections_title.pack(pady=(15, 10))
        
        # Lista de secciones
        sections_list = ctk.CTkScrollableFrame(sections_frame, height=300)
        sections_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        secciones = plantilla.get('secciones', {})
        secciones_ordenadas = sorted(secciones.items(), key=lambda x: x[1].get('orden', 99))
        
        for seccion_id, seccion_config in secciones_ordenadas:
            seccion_frame = ctk.CTkFrame(sections_list, fg_color="gray20", corner_radius=5)
            seccion_frame.pack(fill="x", pady=2)
            
            titulo_seccion = self.generar_titulo_seccion(seccion_id)
            requerida = "✅ Requerida" if seccion_config.get('requerida', False) else "⚪ Opcional"
            tipo = seccion_config.get('tipo', 'contenido').title()
            
            seccion_text = f"{seccion_config.get('orden', 99)}. {titulo_seccion}\n{requerida} | Tipo: {tipo}"
            
            seccion_label = ctk.CTkLabel(
                seccion_frame, text=seccion_text, font=ctk.CTkFont(size=11),
                justify="left", text_color="white"
            )
            seccion_label.pack(padx=10, pady=8, anchor="w")
        
        # Botón cerrar
        close_btn = ctk.CTkButton(
            main_frame, text="✅ Cerrar Vista Previa",
            command=window.destroy,
            width=180, height=35
        )
        close_btn.pack(pady=(0, 10))
    
    def crear_plantilla_desde_formulario(self, window):
        """Crea una plantilla desde el formulario"""
        try:
            nombre = self.nombre_entry.get().strip()
            descripcion = self.descripcion_entry.get("1.0", "end").strip()
            basada_en_texto = self.basada_en_combo.get()
            
            # Validar campos
            if not nombre:
                messagebox.showerror("❌ Error", "El nombre de la plantilla es obligatorio")
                return
            
            if not descripcion:
                messagebox.showerror("❌ Error", "La descripción es obligatoria")
                return
            
            # Determinar plantilla base
            basada_en_id = None
            if basada_en_texto != "Ninguna (Crear desde cero)":
                # Buscar ID de la plantilla seleccionada
                todas_plantillas = self.obtener_todas_plantillas()
                for plantilla in todas_plantillas:
                    if plantilla['nombre'] == basada_en_texto:
                        basada_en_id = plantilla['id']
                        break
            
            # Crear plantilla
            nueva_plantilla = self.crear_plantilla_personalizada(nombre, descripcion, basada_en_id)
            
            if nueva_plantilla:
                messagebox.showinfo("✅ Plantilla Creada", 
                    f"Plantilla '{nombre}' creada exitosamente.\n\n"
                    f"ID: {nueva_plantilla['id']}\n"
                    f"Puedes encontrarla en la pestaña 'Personalizadas'")
                
                # Limpiar formulario
                self.limpiar_formulario()
                
                # Actualizar lista de personalizadas
                if hasattr(self, 'personalizadas_frame'):
                    self.actualizar_lista_personalizadas(window)
            else:
                messagebox.showerror("❌ Error", "Error al crear la plantilla")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error creando plantilla:\n{str(e)}")
    
    def limpiar_formulario(self):
        """Limpia el formulario de creación"""
        self.nombre_entry.delete(0, "end")
        self.descripcion_entry.delete("1.0", "end")
        self.basada_en_combo.set("Ninguna (Crear desde cero)")
    
    def editar_plantilla(self, template_id):
        """Abre editor de plantilla"""
        messagebox.showinfo("✏️ Editar Plantilla", 
            "🚧 Editor de plantillas en desarrollo\n\n"
            "Próximamente podrás editar:\n"
            "• Información básica\n"
            "• Estructura de secciones\n"
            "• Configuración de formato\n"
            "• Reglas de validación")
    
    def eliminar_plantilla(self, template_id, window):
        """Elimina una plantilla personalizada"""
        # Buscar plantilla
        plantilla = None
        for p in self.plantillas_personalizadas:
            if p['id'] == template_id:
                plantilla = p
                break
        
        if not plantilla:
            messagebox.showerror("❌ Error", "Plantilla no encontrada")
            return
        
        # Confirmación
        respuesta = messagebox.askyesno(
            "🗑️ Eliminar Plantilla",
            f"¿Estás seguro de que quieres eliminar la plantilla '{plantilla['nombre']}'?\n\n"
            f"Esta acción no se puede deshacer."
        )
        
        if respuesta:
            try:
                # Eliminar archivo
                if 'filepath' in plantilla and os.path.exists(plantilla['filepath']):
                    os.remove(plantilla['filepath'])
                
                # Eliminar de lista
                self.plantillas_personalizadas.remove(plantilla)
                
                # Actualizar interfaz
                if hasattr(self, 'personalizadas_frame'):
                    self.actualizar_lista_personalizadas(window)
                
                messagebox.showinfo("✅ Eliminada", f"Plantilla '{plantilla['nombre']}' eliminada correctamente")
                
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error eliminando plantilla:\n{str(e)}")
    
    def exportar_todas_plantillas(self):
        """Exporta todas las plantillas personalizadas"""
        if not self.plantillas_personalizadas:
            messagebox.showwarning("⚠️ Sin Plantillas", "No tienes plantillas personalizadas para exportar")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Paquete de plantillas", "*.json")],
                title="Exportar Todas las Plantillas"
            )
            
            if filename:
                export_data = {
                    'version': '2.0',
                    'tipo': 'paquete_plantillas',
                    'fecha_exportacion': datetime.now().isoformat(),
                    'total_plantillas': len(self.plantillas_personalizadas),
                    'plantillas': []
                }
                
                for plantilla in self.plantillas_personalizadas:
                    # Crear copia limpia sin filepath
                    plantilla_limpia = {k: v for k, v in plantilla.items() if k != 'filepath'}
                    export_data['plantillas'].append(plantilla_limpia)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("📤 Exportado", 
                    f"Paquete de {len(self.plantillas_personalizadas)} plantillas exportado a:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error exportando plantillas:\n{str(e)}")
    
    def exportar_plantillas_seleccionadas(self):
        """Exporta plantillas seleccionadas por el usuario"""
        messagebox.showinfo("📋 Exportar Seleccionadas", 
            "🚧 Función en desarrollo\n\n"
            "Próximamente podrás seleccionar plantillas específicas para exportar")
    
    def importar_plantilla_archivo(self, window):
        """Importa una plantilla desde archivo JSON"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Plantillas JSON", "*.json"), ("Todos los archivos", "*.*")],
                title="Importar Plantilla"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                # Validar estructura
                if not self.validar_plantilla(import_data):
                    messagebox.showerror("❌ Error", "El archivo no contiene una plantilla válida")
                    return
                
                # Generar ID único
                nombre_original = import_data['nombre']
                import_data['id'] = self.generar_id_unico(nombre_original)
                import_data['fecha_importacion'] = datetime.now().isoformat()
                
                # Verificar si ya existe
                if any(p['nombre'] == nombre_original for p in self.plantillas_personalizadas):
                    respuesta = messagebox.askyesno(
                        "⚠️ Plantilla Existente",
                        f"Ya existe una plantilla con el nombre '{nombre_original}'.\n\n"
                        f"¿Importar con nombre modificado?"
                    )
                    
                    if respuesta:
                        import_data['nombre'] = f"{nombre_original} (Importada)"
                    else:
                        return
                
                # Guardar plantilla importada
                filepath = os.path.join(self.templates_dir, 'personalizadas', f"{import_data['id']}.json")
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(import_data, f, ensure_ascii=False, indent=2)
                
                # Agregar a lista
                import_data['filepath'] = filepath
                self.plantillas_personalizadas.append(import_data)
                
                # Actualizar interfaz
                if hasattr(self, 'personalizadas_frame'):
                    self.actualizar_lista_personalizadas(window)
                
                messagebox.showinfo("📥 Importada", 
                    f"Plantilla '{import_data['nombre']}' importada correctamente")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error importando plantilla:\n{str(e)}")
    
    def importar_paquete_plantillas(self, window):
        """Importa un paquete de plantillas"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Paquete de plantillas", "*.json")],
                title="Importar Paquete de Plantillas"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                # Validar paquete
                if package_data.get('tipo') != 'paquete_plantillas':
                    messagebox.showerror("❌ Error", "El archivo no es un paquete de plantillas válido")
                    return
                
                plantillas_importadas = 0
                plantillas_saltadas = 0
                
                for plantilla_data in package_data.get('plantillas', []):
                    if self.validar_plantilla(plantilla_data):
                        # Verificar si ya existe
                        if not any(p['nombre'] == plantilla_data['nombre'] for p in self.plantillas_personalizadas):
                            # Generar ID único y guardar
                            plantilla_data['id'] = self.generar_id_unico(plantilla_data['nombre'])
                            plantilla_data['fecha_importacion'] = datetime.now().isoformat()
                            
                            filepath = os.path.join(self.templates_dir, 'personalizadas', f"{plantilla_data['id']}.json")
                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump(plantilla_data, f, ensure_ascii=False, indent=2)
                            
                            plantilla_data['filepath'] = filepath
                            self.plantillas_personalizadas.append(plantilla_data)
                            plantillas_importadas += 1
                        else:
                            plantillas_saltadas += 1
                
                # Actualizar interfaz
                if hasattr(self, 'personalizadas_frame'):
                    self.actualizar_lista_personalizadas(window)
                
                messagebox.showinfo("📦 Paquete Importado", 
                    f"Paquete procesado:\n"
                    f"• {plantillas_importadas} plantillas importadas\n"
                    f"• {plantillas_saltadas} plantillas saltadas (ya existían)")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error importando paquete:\n{str(e)}")
    
    def mostrar_ayuda_plantillas(self):
        """Muestra ayuda del sistema de plantillas"""
        messagebox.showinfo(
            "❓ Ayuda - Sistema de Plantillas",
            "🎨 SISTEMA AVANZADO DE PLANTILLAS\n\n"
            "TIPOS DE PLANTILLAS:\n"
            "• Predefinidas: Plantillas profesionales del sistema\n"
            "• Personalizadas: Creadas por ti o importadas\n\n"
            "FUNCIONALIDADES:\n"
            "• Aplicar plantillas completas al proyecto\n"
            "• Crear plantillas personalizadas\n"
            "• Importar/exportar plantillas\n"
            "• Vista previa de estructura\n"
            "• Configuración de formato automática\n\n"
            "PLANTILLAS PREDEFINIDAS:\n"
            "• Académico Básico: Proyectos de grado\n"
            "• Científico Avanzado: Investigación científica\n"
            "• Tesis Doctoral: Estructura completa de tesis\n\n"
            "¡Ahorra tiempo y mantén consistencia profesional!"
        )


class AplicarPlantillaDialog:
    """Diálogo para aplicar plantilla con opciones"""
    
    def __init__(self, parent, template_manager):
        self.result = None
        self.template_manager = template_manager
        
        # Crear ventana
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("🎨 Aplicar Plantilla")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar
        self.centrar_ventana()
        
        self.setup_dialog()
    
    def centrar_ventana(self):
        """Centra el diálogo"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
    
    def setup_dialog(self):
        """Configura el diálogo"""
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text="🎨 Aplicar Plantilla al Proyecto",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Selección de plantilla
        template_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        template_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(template_frame, text="Seleccionar plantilla:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        todas_plantillas = self.template_manager.obtener_todas_plantillas()
        plantillas_nombres = [p['nombre'] for p in todas_plantillas]
        
        self.template_combo = ctk.CTkComboBox(template_frame, values=plantillas_nombres, width=500)
        self.template_combo.pack(fill="x")
        
        # Opciones de aplicación
        options_frame = ctk.CTkFrame(main_frame, fg_color="darkblue", corner_radius=10)
        options_frame.pack(fill="x", pady=(0, 20))
        
        options_title = ctk.CTkLabel(
            options_frame, text="⚙️ Opciones de Aplicación",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        options_title.pack(pady=(15, 10))
        
        # Checkboxes
        self.aplicar_formato = ctk.CTkCheckBox(
            options_frame, text="Aplicar configuración de formato (fuente, márgenes, etc.)",
            font=ctk.CTkFont(size=12), text_color="white"
        )
        self.aplicar_formato.pack(anchor="w", padx=15, pady=5)
        self.aplicar_formato.select()  # Seleccionado por defecto
        
        self.aplicar_secciones = ctk.CTkCheckBox(
            options_frame, text="Aplicar estructura de secciones",
            font=ctk.CTkFont(size=12), text_color="white"
        )
        self.aplicar_secciones.pack(anchor="w", padx=15, pady=(5, 15))
        self.aplicar_secciones.select()  # Seleccionado por defecto
        
        # Advertencia
        warning_frame = ctk.CTkFrame(main_frame, fg_color="darkorange", corner_radius=10)
        warning_frame.pack(fill="x", pady=(0, 20))
        
        warning_text = "⚠️ IMPORTANTE: Aplicar una plantilla modificará la estructura actual del proyecto.\n" \
                      "Se creará un respaldo automático antes de aplicar los cambios."
        
        warning_label = ctk.CTkLabel(
            warning_frame, text=warning_text, font=ctk.CTkFont(size=11),
            text_color="white", wraplength=500, justify="left"
        )
        warning_label.pack(padx=15, pady=15)
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            btn_frame, text="❌ Cancelar", command=self.cancelar,
            width=120, height=35
        )
        cancel_btn.pack(side="left")
        
        apply_btn = ctk.CTkButton(
            btn_frame, text="✅ Aplicar Plantilla", command=self.aplicar,
            width=150, height=35, fg_color="green", hover_color="darkgreen"
        )
        apply_btn.pack(side="right")
    
    def aplicar(self):
        """Aplica la plantilla seleccionada"""
        template_name = self.template_combo.get()
        if not template_name:
            messagebox.showerror("❌ Error", "Selecciona una plantilla")
            return
        
        # Buscar ID de la plantilla
        todas_plantillas = self.template_manager.obtener_todas_plantillas()
        template_id = None
        
        for plantilla in todas_plantillas:
            if plantilla['nombre'] == template_name:
                template_id = plantilla['id']
                break
        
        if not template_id:
            messagebox.showerror("❌ Error", "Plantilla no encontrada")
            return
        
        # Configurar resultado
        self.result = {
            'template_id': template_id,
            'aplicar_formato': self.aplicar_formato.get(),
            'aplicar_secciones': self.aplicar_secciones.get()
        }
        
        self.dialog.destroy()
    
    def cancelar(self):
        """Cancela la operación"""
        self.dialog.destroy()