"""
Ventana principal - Interfaz completa del generador de proyectos académicos
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import os
from datetime import datetime
from PIL import Image

# Imports de módulos internos
from core.project_manager import ProjectManager
from core.document_generator import DocumentGenerator
from core.validator import ProjectValidator
from modules.citations import CitationProcessor
from modules.references import ReferenceManager
from modules.sections import SectionManager
from .dialogs import SeccionDialog

class ProyectoAcademicoGenerator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎓 Generador de Proyectos Académicos - Versión Avanzada")
        self.root.geometry("1200x700")
        from template_manager import obtener_template_manager
        self.template_manager = obtener_template_manager()
        # Hacer la ventana redimensionable
        self.root.minsize(1000, 600)
        self.configurar_ventana_responsiva()
        
        # Inicializar gestor de fuentes
        self.font_manager = FontManager()
        
        # Configurar atajos mejorados
        self.configurar_atajos_accesibilidad()
        # Inicializar componentes modulares
        self.project_manager = ProjectManager()
        self.document_generator = DocumentGenerator()
        self.validator = ProjectValidator()
        self.citation_processor = CitationProcessor()
        self.reference_manager = ReferenceManager()
        self.section_manager = SectionManager()
        
        # Variables para almacenar la información
        self.proyecto_data = {}
        self.referencias = []
        self.documento_base = None
        self.usar_formato_base = False
        
                # Variables para imágenes
        self.encabezado_personalizado = None
        self.insignia_personalizada = None
        self.ruta_encabezado = None
        self.ruta_insignia = None
        
        # Configuración de marca de agua
        self.watermark_opacity = 0.3
        self.watermark_stretch = True
        self.watermark_mode = 'watermark'  # 'watermark' o 'normal' 
        
        # Buscar imágenes base
        self.buscar_imagenes_base()
        
        # Secciones dinámicas - estructura inicial
        self.secciones_disponibles = self.get_secciones_iniciales()
        self.secciones_activas = list(self.secciones_disponibles.keys())
        self.content_texts = {}
        
        # Configuración de formato
        self.formato_config = {
            'fuente_texto': 'Times New Roman',
            'tamaño_texto': 12,
            'fuente_titulo': 'Times New Roman', 
            'tamaño_titulo': 14,
            'interlineado': 2.0,
            'margen': 2.54,
            'justificado': True,
            'sangria': True
        }
        
        # Variables de estadísticas
        self.stats = {
            'total_words': 0,
            'total_chars': 0,
            'sections_completed': 0,
            'references_added': 0
        }
        
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        self.mostrar_bienvenida()
        
        # Iniciar estadísticas y auto-guardado
        self.actualizar_estadisticas()
        self.project_manager.auto_save_project(self)
    def cargar_documento_base(self):
        """Carga el documento base usando template_manager"""
        from template_manager import aplicar_plantilla_tercer_ano
        aplicar_plantilla_tercer_ano(self)

    def gestionar_plantillas(self):
        """Abre el gestor de plantillas avanzado"""
        from template_manager import mostrar_gestor_plantillas
        mostrar_gestor_plantillas(self)
    
    def buscar_imagenes_base(self):
        """Busca imágenes base en la carpeta resources/images"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Actualizar ruta a resources/images
            recursos_dir = os.path.join(script_dir, "..", "resources", "images")
            recursos_dir = os.path.normpath(recursos_dir)
            
            print(f"🔍 Buscando imágenes en: {recursos_dir}")
            
            # Crear directorio si no existe
            if not os.path.exists(recursos_dir):
                os.makedirs(recursos_dir)
                print(f"📁 Directorio creado: {recursos_dir}")
            
            # Buscar encabezado con múltiples extensiones
            encabezado_extensions = ['Encabezado.png', 'Encabezado.jpg', 'Encabezado.jpeg', 'encabezado.png']
            for filename in encabezado_extensions:
                encabezado_path = os.path.join(recursos_dir, filename)
                if os.path.exists(encabezado_path):
                    self.ruta_encabezado = encabezado_path
                    print(f"✅ Encabezado encontrado: {filename}")
                    break
            else:
                print("⚠️ Encabezado.png no encontrado en resources/images")
            
            # Buscar insignia con múltiples extensiones
            insignia_extensions = ['Insignia.png', 'Insignia.jpg', 'Insignia.jpeg', 'insignia.png']
            for filename in insignia_extensions:
                insignia_path = os.path.join(recursos_dir, filename)
                if os.path.exists(insignia_path):
                    self.ruta_insignia = insignia_path
                    print(f"✅ Insignia encontrada: {filename}")
                    break
            else:
                print("⚠️ Insignia.png no encontrada en resources/images")
                
        except Exception as e:
            print(f"❌ Error buscando imágenes base: {e}")
            messagebox.showwarning("⚠️ Imágenes", 
                f"Error al buscar imágenes base:\n{str(e)}\n\n"
                f"Coloca las imágenes en: resources/images/\n"
                f"• Encabezado.png\n• Insignia.png")
    
    def get_secciones_iniciales(self):
        """Define las secciones disponibles inicialmente"""
        return {
            "resumen": {
                "titulo": "📄 Resumen", 
                "instruccion": "Resumen ejecutivo del proyecto (150-300 palabras)",
                "requerida": False,
                "capitulo": False
            },
            "introduccion": {
                "titulo": "🔍 Introducción", 
                "instruccion": "Presenta el tema, contexto e importancia",
                "requerida": True,
                "capitulo": False
            },
            "capitulo1": {
                "titulo": "📖 CAPÍTULO I", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "planteamiento": {
                "titulo": "❓ Planteamiento del Problema", 
                "instruccion": "Define el problema a investigar",
                "requerida": True,
                "capitulo": False
            },
            "preguntas": {
                "titulo": "❔ Preguntas de Investigación", 
                "instruccion": "Pregunta general y específicas",
                "requerida": True,
                "capitulo": False
            },
            "delimitaciones": {
                "titulo": "📏 Delimitaciones", 
                "instruccion": "Límites del estudio (temporal, espacial, conceptual)",
                "requerida": False,
                "capitulo": False
            },
            "justificacion": {
                "titulo": "💡 Justificación", 
                "instruccion": "Explica por qué es importante investigar",
                "requerida": True,
                "capitulo": False
            },
            "objetivos": {
                "titulo": "🎯 Objetivos", 
                "instruccion": "General y específicos (verbos en infinitivo)",
                "requerida": True,
                "capitulo": False
            },
            "capitulo2": {
                "titulo": "📚 CAPÍTULO II - ESTADO DEL ARTE", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "marco_teorico": {
                "titulo": "📖 Marco Teórico", 
                "instruccion": "Base teórica y antecedentes (USA CITAS)",
                "requerida": True,
                "capitulo": False
            },
            "capitulo3": {
                "titulo": "🔬 CAPÍTULO III", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "metodologia": {
                "titulo": "⚙️ Marco Metodológico", 
                "instruccion": "Tipo de estudio y técnicas de recolección",
                "requerida": True,
                "capitulo": False
            },
            "capitulo4": {
                "titulo": "🛠️ CAPÍTULO IV - DESARROLLO", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "desarrollo": {
                "titulo": "⚙️ Desarrollo", 
                "instruccion": "Proceso de investigación paso a paso",
                "requerida": False,
                "capitulo": False
            },
            "capitulo5": {
                "titulo": "📊 CAPÍTULO V - ANÁLISIS DE DATOS", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "resultados": {
                "titulo": "📊 Resultados", 
                "instruccion": "Datos obtenidos (gráficos, tablas)",
                "requerida": False,
                "capitulo": False
            },
            "analisis_datos": {
                "titulo": "📈 Análisis de Datos", 
                "instruccion": "Interpretación de resultados",
                "requerida": False,
                "capitulo": False
            },
            "capitulo6": {
                "titulo": "💬 CAPÍTULO VI", 
                "instruccion": "Título de capítulo",
                "requerida": False,
                "capitulo": True
            },
            "discusion": {
                "titulo": "💬 Discusión", 
                "instruccion": "Confronta resultados con teoría",
                "requerida": False,
                "capitulo": False
            },
            "conclusiones": {
                "titulo": "✅ Conclusiones", 
                "instruccion": "Hallazgos principales y respuestas a objetivos",
                "requerida": True,
                "capitulo": False
            }
        }
    
    def setup_ui(self):
        """Configura la interfaz de usuario moderna con mejor gestión de espacio"""
        # Frame principal con scroll
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header con título y botones principales
        header_frame = ctk.CTkFrame(main_container, height=120, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Título en header
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎓 Generador de Proyectos Académicos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Botones principales en header
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        # Primera fila de botones
        btn_row1 = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_row1.pack(fill="x", pady=(0, 5))
        
        help_btn = ctk.CTkButton(
            btn_row1, text="📖 Guía", command=self.mostrar_instrucciones,
            width=80, height=30, font=ctk.CTkFont(size=11, weight="bold")
        )
        help_btn.pack(side="left", padx=(0, 5))
        
        template_btn = ctk.CTkButton(
            btn_row1, text="📋 Plantilla", command=self.cargar_documento_base,
            width=90, height=30, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="purple", hover_color="darkviolet"
        )
        template_btn.pack(side="left", padx=(0, 5))
        
        # Botones de proyecto
        save_btn = ctk.CTkButton(
            btn_row1, text="💾 Guardar", command=self.guardar_proyecto,
            width=80, height=30, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="darkgreen", hover_color="green"
        )
        save_btn.pack(side="left", padx=(0, 5))
        
        load_btn = ctk.CTkButton(
            btn_row1, text="📂 Cargar", command=self.cargar_proyecto,
            width=80, height=30, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="darkblue", hover_color="blue"
        )
        load_btn.pack(side="left", padx=(0, 5))
        
        # Estadísticas en tiempo real
        self.stats_label = ctk.CTkLabel(
            btn_row1, text="📊 Palabras: 0 | Secciones: 0/13 | Referencias: 0",
            font=ctk.CTkFont(size=10), text_color="gray70"
        )
        self.stats_label.pack(side="right", padx=(5, 0))
        
        # Segunda fila de botones
        btn_row2 = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_row2.pack(fill="x")
        
        # Botones de imágenes
        images_btn = ctk.CTkButton(
            btn_row2, text="🖼️ Imágenes", command=self.gestionar_imagenes,
            width=90, height=30, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="darkblue", hover_color="navy"
        )
        images_btn.pack(side="left", padx=(0, 5))
        
        export_btn = ctk.CTkButton(
            btn_row2, text="📤 Exportar Config", command=self.exportar_configuracion,
            width=110, height=30, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="darkorange", hover_color="orange"
        )
        export_btn.pack(side="left", padx=(0, 5))
        
        validate_btn = ctk.CTkButton(
            btn_row2, text="🔍 Validar", command=self.validar_proyecto,
            width=80, height=30, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="orange", hover_color="darkorange"
        )
        validate_btn.pack(side="left", padx=(0, 5))
        
        generate_btn = ctk.CTkButton(
            btn_row2, text="📄 Generar Documento", command=self.generar_documento_async,
            width=140, height=30, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        generate_btn.pack(side="right", padx=(5, 0))
        
        # Frame contenedor para tabs con scroll
        content_container = ctk.CTkFrame(main_container, corner_radius=10)
        content_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Tabview principal con altura reducida
        self.tabview = ctk.CTkTabview(content_container, width=1100, height=520)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Crear pestañas
        self.setup_info_general()
        self.setup_contenido_dinamico()
        self.setup_citas_referencias()
        self.setup_formato_avanzado()
        self.setup_generacion()
    
    def setup_info_general(self):
        """Pestaña de información general mejorada y más compacta"""
        tab = self.tabview.add("📋 Información General")
        
        # Scroll frame con altura reducida
        scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Datos del Proyecto", height=400)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Toggle para usar formato base - más compacto
        base_frame = ctk.CTkFrame(scroll_frame, fg_color="darkblue", corner_radius=8)
        base_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            base_frame, text="📋 Formato Base",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 5))
        
        self.usar_base_var = ctk.CTkCheckBox(
            base_frame, text="Usar plantilla base (3º AÑO)",
            font=ctk.CTkFont(size=12), command=self.toggle_formato_base
        )
        self.usar_base_var.pack(pady=(0, 10))
        
        # Campos organizados en filas de 2 columnas usando pack
        campos = [
            ("Institución Educativa", "institucion", "Colegio Privado Divina Esperanza"),
            ("Título del Proyecto", "titulo", "Ingrese el título de su investigación"),
            ("Categoría", "categoria", "Ciencia o Tecnología"),
            ("Ciclo", "ciclo", "Tercer año"),
            ("Curso", "curso", "3 BTI"),
            ("Énfasis", "enfasis", "Tecnología")
        ]
        
        # Crear campos en pares
        for i in range(0, len(campos), 2):
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            # Primera columna
            if i < len(campos):
                label, key, placeholder = campos[i]
                field_frame1 = ctk.CTkFrame(row_frame, fg_color="transparent")
                field_frame1.pack(side="left", fill="both", expand=True, padx=(0, 10))
                
                ctk.CTkLabel(field_frame1, text=label, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
                entry = ctk.CTkEntry(field_frame1, placeholder_text=placeholder, height=35)
                entry.pack(fill="x", pady=(5, 0))
                self.proyecto_data[key] = entry
            
            # Segunda columna
            if i + 1 < len(campos):
                label, key, placeholder = campos[i + 1]
                field_frame2 = ctk.CTkFrame(row_frame, fg_color="transparent")
                field_frame2.pack(side="right", fill="both", expand=True, padx=(10, 0))
                
                ctk.CTkLabel(field_frame2, text=label, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
                entry = ctk.CTkEntry(field_frame2, placeholder_text=placeholder, height=30)
                entry.pack(fill="x", pady=(3, 0))
                self.proyecto_data[key] = entry
        
        # Campos largos (ancho completo)
        campos_largos = [
            ("Área de Desarrollo", "area", "Especifique el área de desarrollo"),
            ("Estudiantes (separar con comas)", "estudiantes", "Nombre1 Apellido1, Nombre2 Apellido2"),
            ("Tutores (separar con comas)", "tutores", "Prof. Nombre Apellido, Dr. Nombre Apellido"),
            ("Director", "director", "Cristina Raichakowski"),
            ("Responsable", "responsable", "Nombre del responsable")
        ]
        
        for label, key, placeholder in campos_largos:
            field_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(field_frame, text=label, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            entry = ctk.CTkEntry(field_frame, placeholder_text=placeholder, height=30)
            entry.pack(fill="x", pady=(3, 0))
            self.proyecto_data[key] = entry
    
    def setup_contenido_dinamico(self):
        """Pestaña de contenido con gestión dinámica de secciones mejorada"""
        tab = self.tabview.add("📝 Contenido Dinámico")
        
        # Frame principal con PanedWindow para redimensionar
        paned_window = ctk.CTkFrame(tab, fg_color="transparent")
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel de control izquierdo - REDIMENSIONABLE
        control_frame = ctk.CTkFrame(paned_window, width=320, corner_radius=10)
        control_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Header del panel con botón de colapsar
        header_frame = ctk.CTkFrame(control_frame, fg_color="gray25", height=45)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Botón colapsar
        self.sidebar_collapsed = False
        collapse_btn = ctk.CTkButton(
            header_frame, text="◀", width=30, height=30,
            command=self.toggle_sidebar,
            font=ctk.CTkFont(size=14)
        )
        collapse_btn.pack(side="left", padx=5, pady=7)
        
        title_label = ctk.CTkLabel(
            header_frame, text="🛠️ Gestión de Secciones",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left", padx=(5, 0))
        
        # Frame de búsqueda
        search_frame = ctk.CTkFrame(control_frame, height=45)
        search_frame.pack(fill="x", padx=8, pady=(8, 4))
        
        search_icon = ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=12))
        search_icon.pack(side="left", padx=(8, 4))
        
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar sección...",
            height=30, font=ctk.CTkFont(size=11)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self.filtrar_secciones)
        
        # Botones de gestión mejorados
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=(4, 8))
        
        # Primera fila de botones
        btn_row1 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_row1.pack(fill="x", pady=2)
        
        add_btn = ctk.CTkButton(
            btn_row1, text="➕ Agregar", command=self.agregar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        add_btn.pack(side="left", padx=(0, 4))
        
        remove_btn = ctk.CTkButton(
            btn_row1, text="➖ Quitar", command=self.quitar_seccion,
            width=90, height=30, fg_color="red", hover_color="darkred",
            font=ctk.CTkFont(size=11)
        )
        remove_btn.pack(side="left", padx=(0, 4))
        
        edit_btn = ctk.CTkButton(
            btn_row1, text="✏️ Editar", command=self.editar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        edit_btn.pack(side="left")
        
        # Segunda fila - botones de orden
        btn_row2 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_row2.pack(fill="x", pady=2)
        
        up_btn = ctk.CTkButton(
            btn_row2, text="⬆️ Subir", command=self.subir_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        up_btn.pack(side="left", padx=(0, 4))
        
        down_btn = ctk.CTkButton(
            btn_row2, text="⬇️ Bajar", command=self.bajar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        down_btn.pack(side="left", padx=(0, 4))
        
        # Botón de vista previa
        preview_btn = ctk.CTkButton(
            btn_row2, text="👁️ Preview", command=self.mostrar_preview,
            width=90, height=30, fg_color="purple", hover_color="darkviolet",
            font=ctk.CTkFont(size=11)
        )
        preview_btn.pack(side="left")
        
        # Lista de secciones mejorada con scroll
        list_label = ctk.CTkLabel(
            control_frame, text="📋 Secciones Activas:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        list_label.pack(anchor="w", padx=8, pady=(8, 4))
        
        # Scrollable frame mejorado
        self.secciones_listbox = ctk.CTkScrollableFrame(
            control_frame, label_text="",
            fg_color="gray15", corner_radius=8
        )
        self.secciones_listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Panel de contenido (derecha) - EXPANDIBLE
        self.content_container = ctk.CTkFrame(paned_window, corner_radius=10)
        self.content_container.pack(side="right", fill="both", expand=True)
        
        # Breadcrumb navigation
        breadcrumb_frame = ctk.CTkFrame(self.content_container, height=35, fg_color="gray25")
        breadcrumb_frame.pack(fill="x", padx=8, pady=(8, 4))
        breadcrumb_frame.pack_propagate(False)
        
        self.breadcrumb_label = ctk.CTkLabel(
            breadcrumb_frame, text="📍 Navegación: ",
            font=ctk.CTkFont(size=11), anchor="w"
        )
        self.breadcrumb_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Sub-tabview mejorado
        self.content_tabview = ctk.CTkTabview(
            self.content_container,
            segmented_button_selected_color="darkblue",
            segmented_button_selected_hover_color="blue"
        )
        self.content_tabview.pack(expand=True, fill="both", padx=8, pady=(4, 8))
        
        # Guardar referencias
        self.control_frame = control_frame
        
        # Actualizar lista y crear pestañas
        self.actualizar_lista_secciones()
        self.crear_pestanas_contenido()


    # Método para colapsar/expandir sidebar
    def toggle_sidebar(self):
        """Colapsa o expande el panel lateral"""
        if self.sidebar_collapsed:
            self.control_frame.configure(width=320)
            self.sidebar_collapsed = False
        else:
            self.control_frame.configure(width=50)
            self.sidebar_collapsed = True


    # Método para filtrar secciones
    def filtrar_secciones(self, event=None):
        """Filtra las secciones según el término de búsqueda"""
        termino = self.search_entry.get().lower()
        
        # Actualizar la lista mostrando solo las coincidencias
        for widget in self.secciones_listbox.winfo_children():
            widget.destroy()
        
        for i, seccion_id in enumerate(self.secciones_activas):
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                
                # Verificar si coincide con el término de búsqueda
                if termino in seccion['titulo'].lower() or termino in seccion_id.lower():
                    self.crear_item_seccion(i, seccion_id, seccion)


    # Método mejorado para crear items de sección
    def crear_item_seccion(self, index, seccion_id, seccion):
        """Crea un item visual mejorado para una sección"""
        # Frame contenedor con hover effect
        item_frame = ctk.CTkFrame(
            self.secciones_listbox, 
            fg_color="gray20", 
            corner_radius=8,
            height=60
        )
        item_frame.pack(fill="x", pady=3, padx=5)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            item_frame, text="", width=20,
            command=lambda idx=index: self.seleccionar_seccion(idx)
        )
        checkbox.pack(side="left", padx=(10, 5), pady=5)
        checkbox.seccion_index = index
        
        # Contenedor de información
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=5)
        
        # Título con color según tipo
        color = "yellow" if seccion['requerida'] else "white"
        if seccion['capitulo']:
            color = "lightblue"
        
        title_label = ctk.CTkLabel(
            info_frame, text=seccion['titulo'],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color, anchor="w"
        )
        title_label.pack(fill="x", padx=(0, 10))
        
        # Subtítulo con tipo
        tipo = "Capítulo" if seccion['capitulo'] else "Sección"
        if seccion['requerida']:
            tipo += " (Requerida)"
        
        subtitle_label = ctk.CTkLabel(
            info_frame, text=tipo,
            font=ctk.CTkFont(size=10),
            text_color="gray60", anchor="w"
        )
        subtitle_label.pack(fill="x", padx=(0, 10))
        
        # Botón de acceso rápido
        quick_btn = ctk.CTkButton(
            item_frame, text="→", width=30, height=30,
            command=lambda: self.ir_a_seccion(seccion_id),
            font=ctk.CTkFont(size=14)
        )
        quick_btn.pack(side="right", padx=10)
        
        # Efecto hover
        def on_enter(e):
            item_frame.configure(fg_color="gray25")
        
        def on_leave(e):
            item_frame.configure(fg_color="gray20")
        
        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)


    # Método para ir directamente a una sección
    def ir_a_seccion(self, seccion_id):
        """Navega directamente a una sección específica"""
        # Buscar la pestaña correspondiente
        for tab_name in self.content_tabview._tab_dict.keys():
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                if tab_name == seccion['titulo']:
                    self.content_tabview.set(tab_name)
                    # Actualizar breadcrumb
                    self.breadcrumb_label.configure(
                        text=f"📍 Navegación: Contenido > {seccion['titulo']}"
                    )
                    break

    def setup_citas_referencias(self):
        """Pestaña para gestión de citas mejorada con más espacio y funcionalidad"""
        tab = self.tabview.add("📚 Citas y Referencias")
        
        # Contenedor principal con scroll
        main_scroll = ctk.CTkScrollableFrame(tab, label_text="")
        main_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Panel de instrucciones colapsable
        instruc_frame = ctk.CTkFrame(main_scroll, fg_color="gray15", corner_radius=10)
        instruc_frame.pack(fill="x", pady=(0, 15))
        
        # Header con botón de colapsar
        instruc_header = ctk.CTkFrame(instruc_frame, fg_color="gray20", height=40)
        instruc_header.pack(fill="x")
        instruc_header.pack_propagate(False)
        
        self.instruc_collapsed = False
        
        def toggle_instructions():
            if self.instruc_collapsed:
                instruc_content.pack(fill="x", padx=15, pady=(0, 15))
                collapse_btn.configure(text="▼")
            else:
                instruc_content.pack_forget()
                collapse_btn.configure(text="▶")
            self.instruc_collapsed = not self.instruc_collapsed
        
        collapse_btn = ctk.CTkButton(
            instruc_header, text="▼", width=30, height=25,
            command=toggle_instructions,
            fg_color="transparent", hover_color="gray30"
        )
        collapse_btn.pack(side="left", padx=(10, 5))
        
        instruc_title = ctk.CTkLabel(
            instruc_header, text="🚀 SISTEMA DE CITAS - Guía Rápida",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="lightgreen"
        )
        instruc_title.pack(side="left", pady=10)
        
        # Contenido de instrucciones
        instruc_content = ctk.CTkFrame(instruc_frame, fg_color="transparent")
        instruc_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # Grid de ejemplos
        ejemplos_frame = ctk.CTkFrame(instruc_content, fg_color="transparent")
        ejemplos_frame.pack(fill="x")
        
        ejemplos = [
            ("📝 Textual corta", "[CITA:textual:García:2020:45]", "(García, 2020, p. 45)"),
            ("🔄 Parafraseo", "[CITA:parafraseo:López:2019]", "(López, 2019)"),
            ("📖 Textual larga", "[CITA:larga:Martínez:2021:78]", "Bloque con sangría"),
            ("👥 Múltiples autores", "[CITA:multiple:García y López:2020]", "(García y López, 2020)"),
            ("🌐 Fuente web", "[CITA:web:OMS:2023]", "(OMS, 2023)"),
            ("💬 Comunicación personal", "[CITA:personal:Pérez:2022:email]", "(Pérez, comunicación personal, 2022)")
        ]
        
        for i, (tipo, formato, resultado) in enumerate(ejemplos):
            row = i // 2
            col = i % 2
            
            ejemplo_frame = ctk.CTkFrame(ejemplos_frame, fg_color="gray25", corner_radius=8)
            ejemplo_frame.pack(side="left", fill="x", expand=True, padx=5, pady=2)
            
            ctk.CTkLabel(
                ejemplo_frame, text=tipo,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(pady=(5, 2))
            
            ctk.CTkLabel(
                ejemplo_frame, text=formato,
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color="lightblue"
            ).pack()
            
            ctk.CTkLabel(
                ejemplo_frame, text=f"→ {resultado}",
                font=ctk.CTkFont(size=10),
                text_color="lightgreen"
            ).pack(pady=(2, 5))
        
        # Panel de agregar referencias mejorado
        ref_frame = ctk.CTkFrame(main_scroll, corner_radius=10)
        ref_frame.pack(fill="x", pady=(0, 15))
        
        ref_title = ctk.CTkLabel(
            ref_frame, text="➕ Agregar Referencias",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ref_title.pack(pady=(15, 10))
        
        # Formulario en grid para mejor organización
        form_frame = ctk.CTkFrame(ref_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Primera fila
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        # Tipo
        tipo_container = ctk.CTkFrame(row1, fg_color="transparent")
        tipo_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            tipo_container, text="Tipo de referencia:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.ref_tipo = ctk.CTkComboBox(
            tipo_container,
            values=["Libro", "Artículo", "Web", "Tesis", "Conferencia", "Informe"],
            height=35, font=ctk.CTkFont(size=12),
            command=self.actualizar_campos_referencia
        )
        self.ref_tipo.pack(fill="x", pady=(5, 0))
        self.ref_tipo.set("Libro")
        
        # Autor(es)
        autor_container = ctk.CTkFrame(row1, fg_color="transparent")
        autor_container.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            autor_container, text="Autor(es):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.ref_autor = ctk.CTkEntry(
            autor_container, placeholder_text="Apellido, N. o García, J. y López, M.",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.ref_autor.pack(fill="x", pady=(5, 0))
        
        # Segunda fila
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        # Año
        año_container = ctk.CTkFrame(row2, fg_color="transparent")
        año_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            año_container, text="Año:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.ref_año = ctk.CTkEntry(
            año_container, placeholder_text="2024",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.ref_año.pack(fill="x", pady=(5, 0))
        
        # Título
        titulo_container = ctk.CTkFrame(row2, fg_color="transparent")
        titulo_container.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            titulo_container, text="Título:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.ref_titulo = ctk.CTkEntry(
            titulo_container, placeholder_text="Título completo del trabajo",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.ref_titulo.pack(fill="x", pady=(5, 0))
        
        # Tercera fila - Campo dinámico según tipo
        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        self.fuente_container = ctk.CTkFrame(row3, fg_color="transparent")
        self.fuente_container.pack(fill="x")
        
        self.fuente_label = ctk.CTkLabel(
            self.fuente_container, text="Editorial/Fuente:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.fuente_label.pack(anchor="w")
        
        self.ref_fuente = ctk.CTkEntry(
            self.fuente_container, placeholder_text="Editorial, revista o URL",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.ref_fuente.pack(fill="x", pady=(5, 0))
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(ref_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        
        add_ref_btn = ctk.CTkButton(
            btn_frame, text="➕ Agregar Referencia",
            command=self.agregar_referencia,
            height=40, font=ctk.CTkFont(size=13, weight="bold"),
            width=180
        )
        add_ref_btn.pack(side="left", padx=5)
        
        import_btn = ctk.CTkButton(
            btn_frame, text="📥 Importar BibTeX",
            command=self.importar_bibtex,
            height=40, font=ctk.CTkFont(size=13),
            width=150, fg_color="purple", hover_color="darkviolet"
        )
        import_btn.pack(side="left", padx=5)
        
        # Lista de referencias mejorada
        list_frame = ctk.CTkFrame(main_scroll)
        list_frame.pack(fill="both", expand=True)
        
        # Header con búsqueda y filtros
        list_header = ctk.CTkFrame(list_frame, height=50, fg_color="gray25")
        list_header.pack(fill="x")
        list_header.pack_propagate(False)
        
        list_title = ctk.CTkLabel(
            list_header, text="📋 Referencias Agregadas",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_title.pack(side="left", padx=15)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(list_header, fg_color="transparent")
        search_frame.pack(side="right", padx=15)
        
        ctk.CTkLabel(search_frame, text="🔍").pack(side="left", padx=(0, 5))
        
        self.ref_search = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar referencia...",
            width=200, height=30
        )
        self.ref_search.pack(side="left")
        self.ref_search.bind("<KeyRelease>", self.filtrar_referencias)
        
        # Lista scrollable con altura mayor
        self.ref_scroll_frame = ctk.CTkScrollableFrame(
            list_frame, height=300,
            fg_color="gray15", corner_radius=8
        )
        self.ref_scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Botones de gestión
        manage_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        manage_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        delete_btn = ctk.CTkButton(
            manage_frame, text="🗑️ Eliminar Seleccionadas",
            command=self.eliminar_referencias_seleccionadas,
            fg_color="red", hover_color="darkred",
            height=35, width=180
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        export_btn = ctk.CTkButton(
            manage_frame, text="📤 Exportar APA",
            command=self.exportar_referencias_apa,
            height=35, width=150
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        stats_label = ctk.CTkLabel(
            manage_frame, text=f"Total: {len(self.referencias)} referencias",
            font=ctk.CTkFont(size=12)
        )
        stats_label.pack(side="right")
        self.ref_stats_label = stats_label


    # Método auxiliar para actualizar campos según tipo
    def actualizar_campos_referencia(self, choice):
        """Actualiza los campos del formulario según el tipo de referencia"""
        tipos_config = {
            "Libro": ("Editorial:", "Nombre de la editorial"),
            "Artículo": ("Revista:", "Nombre de la revista, volumen(número), páginas"),
            "Web": ("URL:", "https://ejemplo.com"),
            "Tesis": ("Universidad:", "Universidad e información adicional"),
            "Conferencia": ("Evento:", "Nombre del evento y lugar"),
            "Informe": ("Organización:", "Organización que publica")
        }
        
        label, placeholder = tipos_config.get(choice, ("Fuente:", "Información de publicación"))
        self.fuente_label.configure(text=label)
        self.ref_fuente.configure(placeholder_text=placeholder)
    
    def setup_formato_avanzado(self):
        """Pestaña para opciones avanzadas de formato - más compacta"""
        tab = self.tabview.add("🎨 Formato")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Configuración de Formato", height=400)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Sección de tipografía - más compacta
        tipo_frame = ctk.CTkFrame(scroll_frame, fg_color="darkgreen", corner_radius=8)
        tipo_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            tipo_frame, text="🔤 Tipografía",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        # Configuración de tipografía usando pack - más compacta
        tipo_grid = ctk.CTkFrame(tipo_frame, fg_color="transparent")
        tipo_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        # Primera fila
        row1_tipo = ctk.CTkFrame(tipo_grid, fg_color="transparent")
        row1_tipo.pack(fill="x", pady=3)
        
        # Fuente del texto
        fuente_texto_frame = ctk.CTkFrame(row1_tipo, fg_color="transparent")
        fuente_texto_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(fuente_texto_frame, text="Fuente texto:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.fuente_texto = ctk.CTkComboBox(
            fuente_texto_frame, values=["Times New Roman", "Arial", "Calibri"], height=25
        )
        self.fuente_texto.set("Times New Roman")
        self.fuente_texto.pack(fill="x")
        
        # Tamaño del texto
        tamaño_texto_frame = ctk.CTkFrame(row1_tipo, fg_color="transparent")
        tamaño_texto_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(tamaño_texto_frame, text="Tamaño:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.tamaño_texto = ctk.CTkComboBox(tamaño_texto_frame, values=["10", "11", "12", "13", "14"], height=25)
        self.tamaño_texto.set("12")
        self.tamaño_texto.pack(fill="x")
        
        # Segunda fila
        row2_tipo = ctk.CTkFrame(tipo_grid, fg_color="transparent")
        row2_tipo.pack(fill="x", pady=3)
        
        # Fuente de títulos
        fuente_titulo_frame = ctk.CTkFrame(row2_tipo, fg_color="transparent")
        fuente_titulo_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(fuente_titulo_frame, text="Fuente títulos:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.fuente_titulo = ctk.CTkComboBox(
            fuente_titulo_frame, values=["Times New Roman", "Arial", "Calibri"], height=25
        )
        self.fuente_titulo.set("Times New Roman")
        self.fuente_titulo.pack(fill="x")
        
        # Tamaño de títulos
        tamaño_titulo_frame = ctk.CTkFrame(row2_tipo, fg_color="transparent")
        tamaño_titulo_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(tamaño_titulo_frame, text="Tamaño:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.tamaño_titulo = ctk.CTkComboBox(tamaño_titulo_frame, values=["12", "13", "14", "15", "16"], height=25)
        self.tamaño_titulo.set("14")
        self.tamaño_titulo.pack(fill="x")
        
        # Sección de espaciado - más compacta
        espaciado_frame = ctk.CTkFrame(scroll_frame, fg_color="darkblue", corner_radius=8)
        espaciado_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            espaciado_frame, text="📏 Espaciado",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        espaciado_grid = ctk.CTkFrame(espaciado_frame, fg_color="transparent")
        espaciado_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        # Fila de espaciado
        espaciado_row = ctk.CTkFrame(espaciado_grid, fg_color="transparent")
        espaciado_row.pack(fill="x", pady=3)
        
        # Interlineado
        interlineado_frame = ctk.CTkFrame(espaciado_row, fg_color="transparent")
        interlineado_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(interlineado_frame, text="Interlineado:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.interlineado = ctk.CTkComboBox(interlineado_frame, values=["1.0", "1.5", "2.0"], height=25)
        self.interlineado.set("2.0")
        self.interlineado.pack(fill="x")
        
        # Márgenes
        margen_frame = ctk.CTkFrame(espaciado_row, fg_color="transparent")
        margen_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(margen_frame, text="Márgenes (cm):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.margen = ctk.CTkComboBox(margen_frame, values=["2.0", "2.54", "3.0"], height=25)
        self.margen.set("2.54")
        self.margen.pack(fill="x")
        
        # Opciones de alineación - más compacta
        align_frame = ctk.CTkFrame(scroll_frame, fg_color="darkred", corner_radius=8)
        align_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            align_frame, text="📐 Alineación",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        align_grid = ctk.CTkFrame(align_frame, fg_color="transparent")
        align_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        # Fila de opciones de alineación
        align_row = ctk.CTkFrame(align_grid, fg_color="transparent")
        align_row.pack(fill="x", pady=3)
        
        # Opciones de formato profesional
        self.salto_pagina_var = ctk.CTkCheckBox(
            align_row, text="Salto de página entre secciones", font=ctk.CTkFont(size=12)
        )
        self.salto_pagina_var.select()
        self.salto_pagina_var.pack(side="left", padx=(10, 10))
        
        self.conservar_siguiente_var = ctk.CTkCheckBox(
            align_row, text="Conservar con siguiente", font=ctk.CTkFont(size=12)
        )
        self.conservar_siguiente_var.select()
        self.conservar_siguiente_var.pack(side="right", padx=(10, 10))
        
        # Segunda fila de opciones profesionales
        align_row2 = ctk.CTkFrame(align_grid, fg_color="transparent")
        align_row2.pack(fill="x", pady=3)
        
        self.justificado_var = ctk.CTkCheckBox(
            align_row2, text="Justificado", font=ctk.CTkFont(size=12)
        )
        self.justificado_var.select()
        self.justificado_var.pack(side="left", padx=(10, 10))
        
        self.sangria_var = ctk.CTkCheckBox(
            align_row2, text="Sangría primera línea", font=ctk.CTkFont(size=12)
        )
        self.sangria_var.select()
        self.sangria_var.pack(side="right", padx=(10, 10))
        
        # Botón para aplicar configuración
        apply_btn = ctk.CTkButton(
            scroll_frame, text="✅ Aplicar Configuración", command=self.aplicar_formato,
            height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        apply_btn.pack(pady=15)
    
# Modificar setup_generacion() en ui/main_window.py para incluir panel inferior

    def setup_generacion(self):
        """Pestaña de generación con panel de validación mejorado"""
        tab = self.tabview.add("🔧 Generar")
        
        # Usar PanedWindow para panel redimensionable
        paned = ctk.CTkFrame(tab, fg_color="transparent")
        paned.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Panel superior - Opciones
        top_frame = ctk.CTkFrame(paned, corner_radius=15, height=200)
        top_frame.pack(fill="x", pady=(0, 10))
        top_frame.pack_propagate(False)
        
        options_title = ctk.CTkLabel(
            top_frame, text="⚙️ Opciones de Generación",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        options_title.pack(pady=(20, 15))
        
        # Grid de opciones mejorado
        options_grid = ctk.CTkFrame(top_frame, fg_color="transparent")
        options_grid.pack(padx=30, pady=(0, 20))
        
        # Opciones en columnas
        col1 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=20)
        
        col2 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=20)
        
        # Columna 1
        self.incluir_portada = ctk.CTkCheckBox(
            col1, text="📄 Incluir Portada",
            font=ctk.CTkFont(size=14)
        )
        self.incluir_portada.select()
        self.incluir_portada.pack(anchor="w", pady=5)
        
        self.incluir_indice = ctk.CTkCheckBox(
            col1, text="📑 Incluir Índice",
            font=ctk.CTkFont(size=14)
        )
        self.incluir_indice.select()
        self.incluir_indice.pack(anchor="w", pady=5)
        
        # Columna 2
        self.incluir_agradecimientos = ctk.CTkCheckBox(
            col2, text="🙏 Incluir Agradecimientos",
            font=ctk.CTkFont(size=14)
        )
        self.incluir_agradecimientos.pack(anchor="w", pady=5)
        
        self.numeracion_paginas = ctk.CTkCheckBox(
            col2, text="📊 Numeración de páginas",
            font=ctk.CTkFont(size=14)
        )
        self.numeracion_paginas.select()
        self.numeracion_paginas.pack(anchor="w", pady=5)
        
        # Panel inferior expandible - Validación
        bottom_frame = ctk.CTkFrame(paned, corner_radius=15)
        bottom_frame.pack(fill="both", expand=True)
        
        # Header del panel con tabs
        header_frame = ctk.CTkFrame(bottom_frame, height=50, fg_color="gray25")
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Tabs de validación
        self.validation_tabs = ctk.CTkSegmentedButton(
            header_frame,
            values=["🔍 Validación", "📋 Logs", "📊 Estadísticas", "💡 Sugerencias"],
            command=self.cambiar_tab_validacion
        )
        self.validation_tabs.pack(side="left", padx=15, pady=10)
        self.validation_tabs.set("🔍 Validación")
        
        # Botón de limpiar
        clear_btn = ctk.CTkButton(
            header_frame, text="🗑️", width=35, height=35,
            command=self.limpiar_validacion,
            fg_color="transparent", hover_color="gray30"
        )
        clear_btn.pack(side="right", padx=15)
        
        # Contenedor de contenido con scroll
        self.validation_container = ctk.CTkFrame(bottom_frame)
        self.validation_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Área de texto para validación
        self.validation_text = ctk.CTkTextbox(
            self.validation_container,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="gray10"
        )
        self.validation_text.pack(fill="both", expand=True)
        
        # Panel de progreso mejorado
        progress_frame = ctk.CTkFrame(bottom_frame, height=80)
        progress_frame.pack(fill="x", padx=15, pady=(0, 15))
        progress_frame.pack_propagate(False)
        
        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(
            progress_frame, text="🟢 Listo para validar",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(pady=(10, 5))
        
        # Barra de progreso mejorada
        self.progress = ctk.CTkProgressBar(
            progress_frame, height=20,
            progress_color="green"
        )
        self.progress.pack(fill="x", padx=20, pady=(0, 5))
        self.progress.set(0)
        
        # Subtareas
        self.subtask_label = ctk.CTkLabel(
            progress_frame, text="",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        self.subtask_label.pack()
        
        # Inicializar con mensaje de bienvenida mejorado
        self.mostrar_bienvenida_validacion()


    def mostrar_bienvenida_validacion(self):
        """Muestra mensaje de bienvenida mejorado en el panel de validación"""
        mensaje = """✨ GENERADOR AVANZADO DE PROYECTOS ACADÉMICOS v2.0
        
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    🆕 MEJORAS DE INTERFAZ IMPLEMENTADAS:

    📝 EDITOR MEJORADO
        • Cuadros de texto expandibles con botón de maximizar
        • Contador de palabras en tiempo real
        • Altura aumentada para mejor visualización
        • Editor modal para edición en pantalla completa
    
    🔍 NAVEGACIÓN OPTIMIZADA
        • Panel lateral con búsqueda de secciones
        • Navegación rápida con un clic
        • Breadcrumb para ubicación actual
        • Panel colapsable para más espacio
    
    📚 GESTIÓN DE REFERENCIAS
        • Formulario mejorado con tipos adicionales
        • Búsqueda y filtrado de referencias
        • Importación de BibTeX
        • Vista previa de formato APA
    
    👁️ VISTA PREVIA EN TIEMPO REAL
        • Panel lateral con preview del documento
        • Tres modos: Texto, Formato y Estructura
        • Actualización automática
        • Estadísticas de completitud
    
    📊 VALIDACIÓN AVANZADA
        • Panel inferior con tabs
        • Logs detallados del proceso
        • Estadísticas en tiempo real
        • Sugerencias inteligentes

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    💡 CONSEJOS DE USO:

    1. USA EL BOTÓN ⛶ para expandir cualquier sección y editarla cómodamente
    2. NAVEGA RÁPIDAMENTE usando el panel lateral o breadcrumb
    3. ACTIVA LA VISTA PREVIA para ver tu documento mientras escribes
    4. REVISA LAS SUGERENCIAS en el panel de validación
    5. USA CTRL+S para guardar tu proyecto frecuentemente

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    🎯 Haz clic en 'Validar Proyecto' cuando estés listo para revisar tu trabajo
    """
        self.validation_text.delete("1.0", "end")
        self.validation_text.insert("1.0", mensaje)


    def cambiar_tab_validacion(self, valor):
        """Cambia el contenido según la tab seleccionada"""
        self.validation_text.delete("1.0", "end")
        
        if valor == "🔍 Validación":
            # Ejecutar validación
            self.validar_proyecto()
        elif valor == "📋 Logs":
            self.mostrar_logs()
        elif valor == "📊 Estadísticas":
            self.mostrar_estadisticas_detalladas()
        elif valor == "💡 Sugerencias":
            self.mostrar_sugerencias()


    def mostrar_estadisticas_detalladas(self):
        """Muestra estadísticas detalladas del proyecto"""
        stats = []
        stats.append("📊 ESTADÍSTICAS DETALLADAS DEL PROYECTO\n")
        stats.append("="*60 + "\n\n")
        
        # Estadísticas por sección
        stats.append("📝 CONTENIDO POR SECCIÓN:\n\n")
        
        total_palabras = 0
        total_caracteres = 0
        
        for seccion_id in self.secciones_activas:
            if seccion_id in self.secciones_disponibles and seccion_id in self.content_texts:
                seccion = self.secciones_disponibles[seccion_id]
                if not seccion['capitulo']:
                    content = self.content_texts[seccion_id].get("1.0", "end").strip()
                    palabras = len(content.split()) if content else 0
                    caracteres = len(content)
                    
                    total_palabras += palabras
                    total_caracteres += caracteres
                    
                    # Barra de progreso visual
                    progreso = min(100, (palabras / 500) * 100)  # 500 palabras como objetivo
                    barra = "█" * int(progreso / 10) + "░" * (10 - int(progreso / 10))
                    
                    stats.append(f"   • {seccion['titulo']:<30} {barra} {palabras:>5} palabras\n")
        
        stats.append(f"\n📊 TOTALES:\n")
        stats.append(f"   • Palabras totales: {total_palabras:,}\n")
        stats.append(f"   • Caracteres totales: {total_caracteres:,}\n")
        stats.append(f"   • Promedio por sección: {total_palabras // max(1, len(self.secciones_activas)):,}\n")
        stats.append(f"   • Referencias: {len(self.referencias)}\n")
        
        # Tiempo estimado de lectura
        tiempo_lectura = total_palabras / 200  # 200 palabras por minuto
        stats.append(f"   • Tiempo de lectura: {int(tiempo_lectura)} minutos\n")
        
        self.validation_text.insert("1.0", ''.join(stats))
    
    def setup_keyboard_shortcuts(self):
        """Configura atajos de teclado"""
        self.root.bind('<Control-s>', lambda e: self.guardar_proyecto())
        self.root.bind('<Control-o>', lambda e: self.cargar_proyecto())
        self.root.bind('<Control-n>', lambda e: self.nuevo_proyecto())
        self.root.bind('<F5>', lambda e: self.validar_proyecto())
        self.root.bind('<F9>', lambda e: self.generar_documento_async())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
    
    # Métodos delegados a componentes modulares
    def guardar_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.guardar_proyecto(self)
    
    def cargar_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.cargar_proyecto(self)
    
    def nuevo_proyecto(self):
        """Delega a ProjectManager"""
        self.project_manager.nuevo_proyecto(self)
    
    def exportar_configuracion(self):
        """Delega a ProjectManager"""
        self.project_manager.exportar_configuracion(self)
    
    def generar_documento_async(self):
        """Delega a DocumentGenerator"""
        self.document_generator.generar_documento_async(self)
    
    def validar_proyecto(self):
        """Delega a ProjectValidator"""
        self.validator.validar_proyecto(self)
    
    # Métodos de UI específicos que se mantienen aquí
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas en tiempo real"""
        total_words = 0
        total_chars = 0
        sections_completed = 0
        
        for key, text_widget in self.content_texts.items():
            if key in self.secciones_disponibles:
                content = text_widget.get("1.0", "end").strip()
                if content and len(content) > 10:
                    sections_completed += 1
                    words = len(content.split())
                    total_words += words
                    total_chars += len(content)
        
        self.stats = {
            'total_words': total_words,
            'total_chars': total_chars,
            'sections_completed': sections_completed,
            'references_added': len(self.referencias)
        }
        
        # Actualizar label
        total_sections = len([s for s in self.secciones_disponibles.values() if not s['capitulo']])
        stats_text = f"📊 Palabras: {total_words} | Secciones: {sections_completed}/{total_sections} | Referencias: {len(self.referencias)}"
        self.stats_label.configure(text=stats_text)
        
        # Programar próxima actualización
        self.root.after(2000, self.actualizar_estadisticas)
    
    def gestionar_imagenes(self):
        """Abre ventana para gestionar imágenes del documento"""
        img_window = ctk.CTkToplevel(self.root)
        img_window.title("🖼️ Gestión de Imágenes")
        img_window.geometry("600x500")
        img_window.transient(self.root)
        img_window.grab_set()
        
        # Centrar ventana
        img_window.update_idletasks()
        x = (img_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (img_window.winfo_screenheight() // 2) - (500 // 2)
        img_window.geometry(f"600x500+{x}+{y}")
        
        main_frame = ctk.CTkFrame(img_window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text="🖼️ Gestión de Imágenes del Documento",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Estado de imágenes base
        status_frame = ctk.CTkFrame(main_frame, fg_color="gray20", corner_radius=10)
        status_frame.pack(fill="x", pady=(0, 20))
        
        status_title = ctk.CTkLabel(
            status_frame, text="📁 Estado de Imágenes Base",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_title.pack(pady=(10, 5))
        
        # Estado del encabezado
        enc_status = "✅ Encontrado" if self.ruta_encabezado else "❌ No encontrado"
        enc_label = ctk.CTkLabel(
            status_frame, text=f"Encabezado.png: {enc_status}",
            font=ctk.CTkFont(size=12)
        )
        enc_label.pack(pady=2)
        
        # Estado de la insignia
        ins_status = "✅ Encontrado" if self.ruta_insignia else "❌ No encontrado"
        ins_label = ctk.CTkLabel(
            status_frame, text=f"Insignia.png: {ins_status}",
            font=ctk.CTkFont(size=12)
        )
        ins_label.pack(pady=(2, 10))
        
        # Sección de carga personalizada
        custom_frame = ctk.CTkFrame(main_frame, fg_color="darkblue", corner_radius=10)
        custom_frame.pack(fill="x", pady=(0, 20))
        
        custom_title = ctk.CTkLabel(
            custom_frame, text="📤 Cargar Imágenes Personalizadas",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        custom_title.pack(pady=(15, 10))
        
        # Botones de carga
        btn_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        enc_btn = ctk.CTkButton(
            btn_frame, text="📋 Cargar Encabezado", 
            command=lambda: self.cargar_imagen_personalizada("encabezado", img_window),
            width=200, height=35
        )
        enc_btn.pack(side="left", padx=(0, 10))
        
        ins_btn = ctk.CTkButton(
            btn_frame, text="🏛️ Cargar Insignia", 
            command=lambda: self.cargar_imagen_personalizada("insignia", img_window),
            width=200, height=35
        )
        ins_btn.pack(side="right", padx=(10, 0))
        
        # Estado de imágenes personalizadas
        custom_status_frame = ctk.CTkFrame(main_frame, fg_color="gray20", corner_radius=10)
        custom_status_frame.pack(fill="x", pady=(0, 20))
        
        custom_status_title = ctk.CTkLabel(
            custom_status_frame, text="🎨 Imágenes Personalizadas Cargadas",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        custom_status_title.pack(pady=(10, 5))
        
        self.enc_custom_label = ctk.CTkLabel(
            custom_status_frame, 
            text=f"Encabezado: {'✅ Cargado' if self.encabezado_personalizado else '⏸️ No cargado'}",
            font=ctk.CTkFont(size=12)
        )
        self.enc_custom_label.pack(pady=2)
        
        self.ins_custom_label = ctk.CTkLabel(
            custom_status_frame, 
            text=f"Insignia: {'✅ Cargado' if self.insignia_personalizada else '⏸️ No cargado'}",
            font=ctk.CTkFont(size=12)
        )
        self.ins_custom_label.pack(pady=(2, 10))
        
        # Botones de acción
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 10))
        
        reset_btn = ctk.CTkButton(
            action_frame, text="🔄 Restablecer", 
            command=lambda: self.restablecer_imagenes(img_window),
            width=120, height=35, fg_color="red", hover_color="darkred"
        )
        reset_btn.pack(side="left")
        
        close_btn = ctk.CTkButton(
            action_frame, text="✅ Cerrar", 
            command=img_window.destroy,
            width=120, height=35
        )
        close_btn.pack(side="right")
        
                # Sección de configuración de marca de agua
        watermark_frame = ctk.CTkFrame(main_frame, fg_color="purple", corner_radius=10)
        watermark_frame.pack(fill="x", pady=(0, 20))
        
        watermark_title = ctk.CTkLabel(
            watermark_frame, text="⚙️ Configuración de Marca de Agua",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        watermark_title.pack(pady=(15, 10))
        
        # Control de opacidad
        opacity_frame = ctk.CTkFrame(watermark_frame, fg_color="transparent")
        opacity_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            opacity_frame, text="Transparencia:",
            font=ctk.CTkFont(size=12), text_color="white"
        ).pack(side="left", padx=(0, 10))
        
        self.opacity_slider = ctk.CTkSlider(
            opacity_frame, from_=0.1, to=1.0,
            command=self.actualizar_opacidad_preview
        )
        self.opacity_slider.set(self.watermark_opacity)
        self.opacity_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.opacity_label = ctk.CTkLabel(
            opacity_frame, text=f"{int(self.watermark_opacity * 100)}%",
            font=ctk.CTkFont(size=12), text_color="white"
        )
        self.opacity_label.pack(side="left")
        
        # Modo de encabezado
        mode_frame = ctk.CTkFrame(watermark_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            mode_frame, text="Modo:",
            font=ctk.CTkFont(size=12), text_color="white"
        ).pack(side="left", padx=(0, 10))
        
        self.mode_var = ctk.StringVar(value=self.watermark_mode)
        
        watermark_radio = ctk.CTkRadioButton(
            mode_frame, text="Marca de Agua",
            variable=self.mode_var, value="watermark",
            text_color="white"
        )
        watermark_radio.pack(side="left", padx=(0, 20))
        
        normal_radio = ctk.CTkRadioButton(
            mode_frame, text="Normal",
            variable=self.mode_var, value="normal",
            text_color="white"
        )
        normal_radio.pack(side="left")
        
        # Estirar al ancho
        self.stretch_var = ctk.CTkCheckBox(
            watermark_frame, text="Estirar al ancho de página",
            font=ctk.CTkFont(size=12), text_color="white"
        )
        self.stretch_var.select() if self.watermark_stretch else self.stretch_var.deselect()
        self.stretch_var.pack(pady=(0, 15))
        
        # Información adicional
        info_frame = ctk.CTkFrame(main_frame, fg_color="green", corner_radius=10)
        info_frame.pack(fill="x")
        
        info_text = """💡 INFORMACIÓN IMPORTANTE:
- Las imágenes base se buscan en: /Recursos/Encabezado.png e /Recursos/Insignia.png
- Las imágenes personalizadas tienen prioridad sobre las base
- Formatos soportados: PNG, JPG, JPEG
- Tamaño recomendado: Encabezado 600x100px, Insignia 100x100px"""
        
        info_label = ctk.CTkLabel(
            info_frame, text=info_text, font=ctk.CTkFont(size=10),
            justify="left", wraplength=550, text_color="white"
        )
        info_label.pack(padx=15, pady=10)
    
    def cargar_imagen_personalizada(self, tipo, window):
        """Carga una imagen personalizada"""
        filetypes = [
            ("Imágenes", "*.png *.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("JPG files", "*.jpg *.jpeg")
        ]
        
        filename = filedialog.askopenfilename(
            title=f"Seleccionar {tipo.capitalize()}",
            filetypes=filetypes
        )
        
        if filename:
            try:
                # Verificar que sea una imagen válida
                with Image.open(filename) as img:
                    # Validar tamaño mínimo
                    if img.width < 50 or img.height < 50:
                        messagebox.showwarning("⚠️ Advertencia", 
                            "La imagen es muy pequeña. Se recomienda al menos 50x50 píxeles.")
                    
                    if tipo == "encabezado":
                        self.encabezado_personalizado = filename
                        self.enc_custom_label.configure(text="Encabezado: ✅ Cargado")
                    else:
                        self.insignia_personalizada = filename
                        self.ins_custom_label.configure(text="Insignia: ✅ Cargado")
                    
                    messagebox.showinfo("✅ Éxito", 
                        f"{tipo.capitalize()} cargado correctamente.\n"
                        f"Tamaño: {img.width}x{img.height} píxeles")
                        
            except Exception as e:
                messagebox.showerror("❌ Error", 
                    f"Error al cargar la imagen:\n{str(e)}")
    
    def restablecer_imagenes(self, window):
        """Restablece las imágenes a las base"""
        self.encabezado_personalizado = None
        self.insignia_personalizada = None
        
        # Actualizar labels
        self.enc_custom_label.configure(text="Encabezado: ⏸️ No cargado")
        self.ins_custom_label.configure(text="Insignia: ⏸️ No cargado")
        
        messagebox.showinfo("🔄 Restablecido", 
            "Se usarán las imágenes base (si están disponibles)")
    
    def toggle_formato_base(self):
        """Activa/desactiva el uso del formato base"""
        if self.usar_base_var.get():
            if self.documento_base is None:
                self.cargar_documento_base()
            else:
                self.aplicar_formato_base()
        else:
            self.limpiar_formato_base()
    
    def cargar_documento_base(self):
        """Carga el documento base proporcionado"""
        try:
            # Simulamos la carga del formato base
            self.documento_base = {
                'institucion': 'COLEGIO PRIVADO DIVINA ESPERANZA',
                'ciclo': 'Tercer año',
                'curso': '3 BTI',
                'enfasis': 'Tecnología',
                'director': 'Cristina Raichakowski'
            }
            
            messagebox.showinfo("✅ Éxito", 
                "Formato base cargado correctamente.\n"
                "Se aplicarán automáticamente:\n"
                "• Estructura del documento\n"
                "• Datos predefinidos\n"
                "• Formato específico\n\n"
                "Marca la casilla para activarlo.")
            
            self.usar_base_var.select()
            self.aplicar_formato_base()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar formato base:\n{str(e)}")
    
    def aplicar_formato_base(self):
        """Aplica los datos del formato base"""
        if self.documento_base:
            for key, value in self.documento_base.items():
                if key in self.proyecto_data:
                    self.proyecto_data[key].delete(0, "end")
                    self.proyecto_data[key].insert(0, value)
            
            messagebox.showinfo("✅ Aplicado", "Formato base aplicado correctamente")
    
    def limpiar_formato_base(self):
        """Limpia los datos del formato base"""
        campos_base = ['institucion', 'ciclo', 'curso', 'enfasis', 'director']
        for campo in campos_base:
            if campo in self.proyecto_data:
                self.proyecto_data[campo].delete(0, "end")
    
    def aplicar_formato(self):
        """Aplica la configuración de formato"""
        self.formato_config = {
            'fuente_texto': self.fuente_texto.get(),
            'tamaño_texto': int(self.tamaño_texto.get()),
            'fuente_titulo': self.fuente_titulo.get(),
            'tamaño_titulo': int(self.tamaño_titulo.get()),
            'interlineado': float(self.interlineado.get()),
            'margen': float(self.margen.get()),
            'justificado': self.justificado_var.get(),
            'sangria': self.sangria_var.get()
        }
        
        messagebox.showinfo("✅ Aplicado", "Configuración de formato aplicada correctamente")
    
    def actualizar_lista_secciones(self):
        """Actualiza la lista visual de secciones activas"""
        # Limpiar lista actual
        for widget in self.secciones_listbox.winfo_children():
            widget.destroy()
        
        # Recrear lista
        for i, seccion_id in enumerate(self.secciones_activas):
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                
                item_frame = ctk.CTkFrame(self.secciones_listbox, fg_color="gray20", corner_radius=5)
                item_frame.pack(fill="x", pady=2, padx=5)
                
                # Checkbox para selección
                checkbox = ctk.CTkCheckBox(
                    item_frame, text="", width=20, command=lambda idx=i: self.seleccionar_seccion(idx)
                )
                checkbox.pack(side="left", padx=(10, 5), pady=5)
                
                # Texto de la sección
                color = "yellow" if seccion['requerida'] else "white"
                if seccion['capitulo']:
                    color = "lightblue"
                
                label = ctk.CTkLabel(
                    item_frame, text=seccion['titulo'], 
                    font=ctk.CTkFont(size=11), text_color=color
                )
                label.pack(side="left", fill="x", expand=True, pady=5)
                
                # Guardar referencia para selección
                checkbox.seccion_index = i
    
    def seleccionar_seccion(self, index):
        """Maneja la selección de secciones"""
        # Esta función se puede expandir para manejar selecciones múltiples
        pass
    
    def agregar_seccion(self):
        """Agrega una nueva sección personalizada"""
        dialog = SeccionDialog(self.root, self.secciones_disponibles)
        if dialog.result:
            seccion_id, seccion_data = dialog.result
            self.secciones_disponibles[seccion_id] = seccion_data
            self.secciones_activas.append(seccion_id)
            self.actualizar_lista_secciones()
            self.crear_pestanas_contenido()
            messagebox.showinfo("✅ Agregada", f"Sección '{seccion_data['titulo']}' agregada correctamente")
    
    def quitar_seccion(self):
        """Quita secciones seleccionadas"""
        # Encontrar secciones seleccionadas
        secciones_a_quitar = []
        for widget in self.secciones_listbox.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkCheckBox) and child.get():
                        if hasattr(child, 'seccion_index'):
                            secciones_a_quitar.append(child.seccion_index)
        
        if secciones_a_quitar:
            # Verificar si hay secciones requeridas
            secciones_requeridas = []
            for idx in secciones_a_quitar:
                seccion_id = self.secciones_activas[idx]
                if self.secciones_disponibles[seccion_id]['requerida']:
                    secciones_requeridas.append(self.secciones_disponibles[seccion_id]['titulo'])
            
            if secciones_requeridas:
                messagebox.showwarning("⚠️ Advertencia", 
                    f"No se pueden eliminar secciones requeridas:\n{', '.join(secciones_requeridas)}")
                return
            
            # Quitar secciones (en orden inverso para mantener índices)
            for idx in sorted(secciones_a_quitar, reverse=True):
                seccion_id = self.secciones_activas.pop(idx)
                if seccion_id in self.content_texts:
                    del self.content_texts[seccion_id]
            
            self.actualizar_lista_secciones()
            self.crear_pestanas_contenido()
            messagebox.showinfo("✅ Eliminadas", f"{len(secciones_a_quitar)} sección(es) eliminada(s)")
        else:
            messagebox.showwarning("⚠️ Selección", "Selecciona al menos una sección para eliminar")
    
    
    def editar_seccion(self):
        """Edita una sección existente"""
        # Obtener sección seleccionada
        secciones_seleccionadas = self.obtener_secciones_seleccionadas()
        
        if len(secciones_seleccionadas) != 1:
            messagebox.showwarning("⚠️ Selección", 
                "Selecciona exactamente una sección para editar")
            return
        
        idx = secciones_seleccionadas[0]
        seccion_id = self.secciones_activas[idx]
        
        if seccion_id not in self.secciones_disponibles:
            messagebox.showerror("❌ Error", "Sección no encontrada")
            return
        
        seccion_data = self.secciones_disponibles[seccion_id]
        
        # Verificar si es una sección base crítica
        secciones_no_editables = ['introduccion', 'objetivos', 'marco_teorico', 
                                  'metodologia', 'conclusiones']
        
        if seccion_id in secciones_no_editables and seccion_data.get('base', False):
            messagebox.showinfo("ℹ️ Información", 
                "Las secciones base críticas no se pueden editar completamente.\n"
                "Solo puedes modificar sus instrucciones.")
            
            # Permitir edición limitada
            nueva_instruccion = self.solicitar_nueva_instruccion(seccion_data)
            if nueva_instruccion:
                self.secciones_disponibles[seccion_id]['instruccion'] = nueva_instruccion
                self.actualizar_lista_secciones()
                self.crear_pestanas_contenido()
                messagebox.showinfo("✅ Actualizado", 
                    f"Instrucción de '{seccion_data['titulo']}' actualizada")
            return
        
        # Abrir diálogo de edición
        dialog = SeccionDialog(self.root, self.secciones_disponibles, 
                              editar=True, seccion_actual=(seccion_id, seccion_data))
        
        if dialog.result:
            nuevo_id, nuevos_datos = dialog.result
            
            # Actualizar sección
            self.secciones_disponibles[seccion_id].update(nuevos_datos)
            
            # Actualizar interfaz
            self.actualizar_lista_secciones()
            self.crear_pestanas_contenido()
            
            messagebox.showinfo("✅ Actualizada", 
                f"Sección '{nuevos_datos['titulo']}' actualizada correctamente")
    
    def solicitar_nueva_instruccion(self, seccion_data):
        """Solicita nueva instrucción para una sección"""
        dialog = ctk.CTkInputDialog(
            text=f"Nueva instrucción para '{seccion_data['titulo']}':",
            title="Editar Instrucción"
        )
        return dialog.get_input()

    
    def subir_seccion(self):
        """Sube una sección en el orden"""
        secciones_seleccionadas = self.obtener_secciones_seleccionadas()
        if len(secciones_seleccionadas) == 1:
            idx = secciones_seleccionadas[0]
            if idx > 0:
                # Intercambiar posiciones
                self.secciones_activas[idx], self.secciones_activas[idx-1] = \
                self.secciones_activas[idx-1], self.secciones_activas[idx]
                self.actualizar_lista_secciones()
                self.crear_pestanas_contenido()
        else:
            messagebox.showwarning("⚠️ Selección", "Selecciona exactamente una sección")
    
    def bajar_seccion(self):
        """Baja una sección en el orden"""
        secciones_seleccionadas = self.obtener_secciones_seleccionadas()
        if len(secciones_seleccionadas) == 1:
            idx = secciones_seleccionadas[0]
            if idx < len(self.secciones_activas) - 1:
                # Intercambiar posiciones
                self.secciones_activas[idx], self.secciones_activas[idx+1] = \
                self.secciones_activas[idx+1], self.secciones_activas[idx]
                self.actualizar_lista_secciones()
                self.crear_pestanas_contenido()
        else:
            messagebox.showwarning("⚠️ Selección", "Selecciona exactamente una sección")
    
    def obtener_secciones_seleccionadas(self):
        """Obtiene las secciones actualmente seleccionadas"""
        seleccionadas = []
        for widget in self.secciones_listbox.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkCheckBox) and child.get():
                        if hasattr(child, 'seccion_index'):
                            seleccionadas.append(child.seccion_index)
        return seleccionadas
    
    def crear_pestanas_contenido(self):
        """Crea las pestañas de contenido basadas en secciones activas"""
        # Limpiar pestañas existentes
        for tab_name in list(self.content_tabview._tab_dict.keys()):
            self.content_tabview.delete(tab_name)
        
        # Crear nuevas pestañas
        for seccion_id in self.secciones_activas:
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                
                if not seccion['capitulo']:  # Solo crear pestañas para contenido
                    tab = self.content_tabview.add(seccion['titulo'])
                    
                    # Frame principal con scroll
                    main_frame = ctk.CTkFrame(tab, fg_color="transparent")
                    main_frame.pack(fill="both", expand=True)
                    
                    # Frame de instrucciones más compacto
                    instruc_frame = ctk.CTkFrame(main_frame, fg_color="gray20", corner_radius=10, height=60)
                    instruc_frame.pack(fill="x", padx=10, pady=(10, 5))
                    instruc_frame.pack_propagate(False)
                    
                    instruc_label = ctk.CTkLabel(
                        instruc_frame, text=f"💡 {seccion['instruccion']}",
                        font=ctk.CTkFont(size=11), wraplength=650, justify="left"
                    )
                    instruc_label.pack(padx=15, pady=8)
                    
                    # Frame contenedor para el text widget y controles
                    text_container = ctk.CTkFrame(main_frame, fg_color="transparent")
                    text_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
                    
                    # Barra de herramientas
                    toolbar = ctk.CTkFrame(text_container, height=35, fg_color="gray25")
                    toolbar.pack(fill="x", pady=(0, 5))
                    toolbar.pack_propagate(False)
                    
                    # Contador de palabras en tiempo real
                    word_count_label = ctk.CTkLabel(
                        toolbar, text="📝 Palabras: 0 | Caracteres: 0",
                        font=ctk.CTkFont(size=10)
                    )
                    word_count_label.pack(side="left", padx=10)
                    
                    # Botón expandir
                    expand_btn = ctk.CTkButton(
                        toolbar, text="⛶ Expandir", width=80, height=25,
                        command=lambda sid=seccion_id: self.expandir_editor(sid),
                        font=ctk.CTkFont(size=11)
                    )
                    expand_btn.pack(side="right", padx=10)
                    
                    # Text widget mejorado
                    text_widget = ctk.CTkTextbox(
                        text_container, wrap="word", 
                        font=ctk.CTkFont(family="Consolas", size=13),
                        height=500,  # Altura aumentada
                        corner_radius=8,
                        border_width=1,
                        border_color="gray40"
                    )
                    text_widget.pack(expand=True, fill="both")
                    
                    # Vincular evento para actualizar contador
                    def update_count(event=None):
                        content = text_widget.get("1.0", "end-1c")
                        words = len(content.split())
                        chars = len(content)
                        word_count_label.configure(text=f"📝 Palabras: {words} | Caracteres: {chars}")
                    
                    text_widget.bind("<KeyRelease>", update_count)
                    
                    # Conservar contenido existente
                    if seccion_id in self.content_texts:
                        contenido_existente = self.content_texts[seccion_id].get("1.0", "end")
                        text_widget.insert("1.0", contenido_existente)
                        update_count()
                    
                    self.content_texts[seccion_id] = text_widget
    
    def agregar_referencia(self):
        """Agrega una referencia a la lista con diseño moderno"""
        if not all([self.ref_autor.get(), self.ref_ano.get(), self.ref_titulo.get()]):
            messagebox.showerror("❌ Error", "Completa al menos Autor, Año y Título")
            return
        
        ref = {
            'tipo': self.ref_tipo.get(),
            'autor': self.ref_autor.get(),
            'año': self.ref_ano.get(),
            'titulo': self.ref_titulo.get(),
            'fuente': self.ref_fuente.get()
        }
        
        self.referencias.append(ref)
        
        # Crear frame para la referencia
        ref_item_frame = ctk.CTkFrame(self.ref_scroll_frame, fg_color="gray20", corner_radius=8)
        ref_item_frame.pack(fill="x", padx=5, pady=5)
        
        # Formato APA para mostrar
        apa_ref = f"{ref['autor']} ({ref['año']}). {ref['titulo']}. {ref['fuente']}"
        
        ref_label = ctk.CTkLabel(
            ref_item_frame, text=f"📖 {apa_ref}", font=ctk.CTkFont(size=11),
            wraplength=800, justify="left"
        )
        ref_label.pack(padx=15, pady=10, anchor="w")
        
        # Limpiar campos
        self.ref_autor.delete(0, "end")
        self.ref_ano.delete(0, "end")
        self.ref_titulo.delete(0, "end")
        self.ref_fuente.delete(0, "end")
        
        messagebox.showinfo("✅ Éxito", "Referencia agregada correctamente")
    
    def eliminar_referencia(self):
        """Elimina la última referencia"""
        if self.referencias:
            self.referencias.pop()
            self.actualizar_lista_referencias()
            messagebox.showinfo("🗑️ Eliminado", "Última referencia eliminada")
        else:
            messagebox.showwarning("⚠️ Advertencia", "No hay referencias para eliminar")
    
    def actualizar_lista_referencias(self):
        """Actualiza la lista visual de referencias"""
        # Limpiar lista actual
        for widget in self.ref_scroll_frame.winfo_children():
            widget.destroy()
        
        # Recrear todas las referencias
        for ref in self.referencias:
            ref_item_frame = ctk.CTkFrame(self.ref_scroll_frame, fg_color="gray20", corner_radius=8)
            ref_item_frame.pack(fill="x", padx=5, pady=5)
            
            apa_ref = f"{ref['autor']} ({ref['año']}). {ref['titulo']}. {ref['fuente']}"
            ref_label = ctk.CTkLabel(
                ref_item_frame, text=f"📖 {apa_ref}", font=ctk.CTkFont(size=11),
                wraplength=800, justify="left"
            )
            ref_label.pack(padx=15, pady=10, anchor="w")
    
    def mostrar_bienvenida(self):
        """Muestra mensaje de bienvenida con atajos de teclado"""
        self.root.after(1000, lambda: messagebox.showinfo(
            "🎓 ¡Generador Profesional!",
            "Generador de Proyectos Académicos - Versión Profesional\n\n"
            "🆕 CARACTERÍSTICAS AVANZADAS:\n"
            "• Formato profesional con niveles de esquema\n"
            "• Auto-guardado cada 5 minutos\n"
            "• Estadísticas en tiempo real\n"
            "• Sistema de guardado/carga completo\n"
            "• Gestión avanzada de imágenes\n"
            "• Exportación de configuraciones\n\n"
            "⌨️ ATAJOS DE TECLADO:\n"
            "• Ctrl+S: Guardar proyecto\n"
            "• Ctrl+O: Cargar proyecto\n"
            "• Ctrl+N: Nuevo proyecto\n"
            "• F5: Validar proyecto\n"
            "• F9: Generar documento\n"
            "• Ctrl+Q: Salir\n\n"
            "🚀 ¡Crea proyectos profesionales únicos!"
        ))
    
    def mostrar_instrucciones(self):
        """Muestra guía completa con nuevas características"""
        instruc_window = ctk.CTkToplevel(self.root)
        instruc_window.title("📖 Guía Profesional Completa")
        instruc_window.geometry("1000x800")
        
        main_frame = ctk.CTkFrame(instruc_window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, text="📖 GUÍA PROFESIONAL COMPLETA",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        instruc_text = ctk.CTkTextbox(main_frame, wrap="word", font=ctk.CTkFont(size=12))
        instruc_text.pack(expand=True, fill="both", padx=20, pady=(10, 20))
        
        instrucciones = """
🎓 GENERADOR PROFESIONAL DE PROYECTOS ACADÉMICOS - VERSIÓN 2.0

═══════════════════════════════════════════════════════════════════

🚀 CARACTERÍSTICAS PROFESIONALES AVANZADAS:
- Formato Word con niveles de esquema para índices automáticos
- Saltos de página inteligentes entre secciones principales
- Control profesional de líneas viudas y huérfanas
- Sistema completo de guardado/carga de proyectos
- Auto-guardado automático cada 5 minutos
- Estadísticas en tiempo real (palabras, secciones, referencias)
- Exportación/importación de configuraciones
- Gestión avanzada de imágenes personalizadas
- Atajos de teclado para flujo de trabajo eficiente

═══════════════════════════════════════════════════════════════════

⌨️ ATAJOS DE TECLADO PROFESIONALES:
- Ctrl+S: Guardar proyecto completo
- Ctrl+O: Cargar proyecto existente
- Ctrl+N: Crear nuevo proyecto
- F5: Validar proyecto rápidamente
- F9: Generar documento final
- Ctrl+Q: Salir de la aplicación

═══════════════════════════════════════════════════════════════════

💾 SISTEMA DE PROYECTOS:

🔹 GUARDAR PROYECTO (Ctrl+S):
- Guarda TODA la información del proyecto
- Incluye contenido, configuración, imágenes, referencias
- Formato JSON para máxima compatibilidad
- Permite reanudar trabajo exactamente donde lo dejaste

🔹 CARGAR PROYECTO (Ctrl+O):
- Restaura proyecto completo
- Mantiene estructura personalizada
- Compatible con versiones anteriores
- Validación automática de integridad

🔹 AUTO-GUARDADO:
- Backup automático cada 5 minutos en "auto_save.json"
- Recuperación automática en caso de cierre inesperado
- No interrumpe el flujo de trabajo

═══════════════════════════════════════════════════════════════════

📊 ESTADÍSTICAS EN TIEMPO REAL:

El panel superior muestra constantemente:
- 📊 Palabras totales escritas
- 📝 Secciones completadas vs total
- 📚 Referencias bibliográficas agregadas
- Actualización automática cada 2 segundos

═══════════════════════════════════════════════════════════════════

🖼️ GESTIÓN AVANZADA DE IMÁGENES:

🔹 IMÁGENES BASE:
- Coloca en /Recursos/Encabezado.png (15cm x 2.5cm)
- Coloca en /Recursos/Insignia.png (3cm x 3cm)
- Detección automática al iniciar

🔹 IMÁGENES PERSONALIZADAS:
- Botón "🖼️ Imágenes" para gestión completa
- Carga imágenes específicas por proyecto
- Prioridad sobre imágenes base
- Validación automática de formatos y tamaños
- Integración perfecta en documento final

═══════════════════════════════════════════════════════════════════

📄 FORMATO PROFESIONAL WORD:

🔹 NIVELES DE ESQUEMA:
- Todos los títulos configurados como Nivel 1
- Índice automático en Word: Referencias > Tabla de contenido
- Navegación rápida por documento
- Estructura profesional garantizada

🔹 CONTROL DE PÁRRAFOS:
- Saltos de página antes de secciones principales
- "Conservar con el siguiente" para títulos
- Control de líneas viudas y huérfanas
- Conservar líneas juntas para coherencia

🔹 FORMATO APA AUTOMÁTICO:
- Sangría francesa en referencias (1.27cm)
- Interlineado doble configurable
- Justificación automática
- Márgenes estándar (2.54cm)

═══════════════════════════════════════════════════════════════════

📚 SISTEMA DE CITAS PROFESIONAL:

🔥 TIPOS SOPORTADOS:

📝 Cita textual corta:
"El conocimiento es poder" [CITA:textual:Bacon:1597:25]
→ "El conocimiento es poder" (Bacon, 1597, p. 25)

🔄 Parafraseo:
Los estudios demuestran mejoras [CITA:parafraseo:García:2020]
→ Los estudios demuestran mejoras (García, 2020)

📖 Cita textual larga (más de 40 palabras):
Su extensa reflexión sobre el tema [CITA:larga:Autor:2021:45]
→ Formato de bloque independiente con sangría

👥 Múltiples autores:
Investigaciones recientes [CITA:multiple:García y López:2020]
→ Investigaciones recientes (García y López, 2020)

🌐 Fuentes web:
Según datos oficiales [CITA:web:OMS:2023]
→ Según datos oficiales (OMS, 2023)

═══════════════════════════════════════════════════════════════════

🛠️ GESTIÓN DINÁMICA DE SECCIONES:

🔹 OPERACIONES DISPONIBLES:
- ➕ Agregar: Crea secciones completamente personalizadas
- ➖ Quitar: Elimina secciones (protege las requeridas)
- ✏️ Editar: Modifica títulos, instrucciones y propiedades
- ⬆️⬇️ Reordenar: Cambia orden de aparición en documento

🔹 TIPOS DE SECCIONES:
- 📖 Capítulos: Solo títulos organizacionales (azul)
- 📝 Contenido: Secciones con texto (blanco)
- ⚠️ Requeridas: Obligatorias para validación (amarillo)
- 🎨 Personalizadas: Creadas según tus necesidades

═══════════════════════════════════════════════════════════════════

🎨 FORMATO COMPLETAMENTE PERSONALIZABLE:

🔹 TIPOGRAFÍA:
- Fuentes independientes para texto y títulos
- Tamaños específicos (10-18pt)
- Familias: Times New Roman, Arial, Calibri, etc.

🔹 ESPACIADO:
- Interlineado: 1.0, 1.5, 2.0, 2.5
- Márgenes: 2.0-3.5 cm
- Sangría primera línea configurable

🔹 OPCIONES PROFESIONALES:
- Saltos de página entre secciones
- Conservar títulos con contenido
- Control de líneas viudas y huérfanas
- Justificación automática

═══════════════════════════════════════════════════════════════════

🚀 ¡AHORA PUEDES CREAR PROYECTOS DE NIVEL PROFESIONAL!

Este generador avanzado combina la potencia de automatización con la flexibilidad 
necesaria para crear documentos académicos de la más alta calidad. 

Experimenta con las diferentes configuraciones y encuentra el formato perfecto 
para tu institución y tipo de proyecto.

¡El futuro de la creación de documentos académicos está aquí!
        """
        
        instruc_text.insert("1.0", instrucciones)
        instruc_text.configure(state="disabled")
    
    # Métodos stub para funcionalidades futuras
    def gestionar_plantillas(self):
        messagebox.showinfo("🚧 En desarrollo", "Gestión de plantillas en desarrollo")
    
    def cambiar_tema(self):
        messagebox.showinfo("🚧 En desarrollo", "Cambio de temas en desarrollo")
    
    def vista_previa_documento(self):
        messagebox.showinfo("🚧 En desarrollo", "Vista previa en desarrollo")
    
    def gestionar_respaldos(self):
        messagebox.showinfo("🚧 En desarrollo", "Gestión de respaldos en desarrollo")
    
    def configuracion_avanzada(self):
        messagebox.showinfo("🚧 En desarrollo", "Configuración avanzada en desarrollo")
    
    
    def actualizar_opacidad_preview(self, value):
        """Actualiza el preview de opacidad"""
        self.watermark_opacity = float(value)
        self.opacity_label.configure(text=f"{int(self.watermark_opacity * 100)}%")
        
    def aplicar_configuracion_watermark(self):
        """Aplica la configuración de marca de agua"""
        self.watermark_mode = self.mode_var.get()
        self.watermark_stretch = self.stretch_var.get()
        messagebox.showinfo("✅ Aplicado", "Configuración de marca de agua actualizada")
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()
    def expandir_editor(self, seccion_id):
        """Abre el editor en una ventana expandida"""
        if seccion_id not in self.content_texts:
            return
        
        # Crear ventana modal
        expand_window = ctk.CTkToplevel(self.root)
        expand_window.title(f"✏️ Editor Expandido - {self.secciones_disponibles[seccion_id]['titulo']}")
        
        # Tamaño grande por defecto
        screen_width = expand_window.winfo_screenwidth()
        screen_height = expand_window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        expand_window.geometry(f"{window_width}x{window_height}")
        expand_window.transient(self.root)
        
        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        expand_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(expand_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text=f"📝 {self.secciones_disponibles[seccion_id]['titulo']}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Instrucciones
        instruc_label = ctk.CTkLabel(
            main_frame,
            text=self.secciones_disponibles[seccion_id]['instruccion'],
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        instruc_label.pack(pady=(0, 10))
        
        # Editor expandido
        expanded_text = ctk.CTkTextbox(
            main_frame, wrap="word",
            font=ctk.CTkFont(family="Consolas", size=14),
            corner_radius=8
        )
        expanded_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Copiar contenido actual
        current_content = self.content_texts[seccion_id].get("1.0", "end-1c")
        expanded_text.insert("1.0", current_content)
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        # Estadísticas
        stats_label = ctk.CTkLabel(
            btn_frame, text="",
            font=ctk.CTkFont(size=11)
        )
        stats_label.pack(side="left")
        
        def update_stats(event=None):
            content = expanded_text.get("1.0", "end-1c")
            words = len(content.split())
            chars = len(content)
            lines = content.count('\n') + 1
            stats_label.configure(
                text=f"📊 Palabras: {words} | Caracteres: {chars} | Líneas: {lines}"
            )
        
        expanded_text.bind("<KeyRelease>", update_stats)
        update_stats()
        
        def save_and_close():
            # Guardar contenido de vuelta
            new_content = expanded_text.get("1.0", "end-1c")
            self.content_texts[seccion_id].delete("1.0", "end")
            self.content_texts[seccion_id].insert("1.0", new_content)
            expand_window.destroy()
        
        save_btn = ctk.CTkButton(
            btn_frame, text="💾 Guardar y Cerrar",
            command=save_and_close,
            fg_color="green", hover_color="darkgreen"
        )
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            btn_frame, text="❌ Cancelar",
            command=expand_window.destroy,
            fg_color="red", hover_color="darkred"
        )
        cancel_btn.pack(side="right")
        
        # Foco al editor
        expanded_text.focus()
# Agregar a ui/main_window.py

    def mostrar_preview(self):
        """Muestra vista previa del documento en panel lateral"""
        # Crear ventana de preview si no existe
        if not hasattr(self, 'preview_window'):
            self.crear_ventana_preview()
        else:
            self.preview_window.deiconify()
            self.actualizar_preview()


    def crear_ventana_preview(self):
        """Crea ventana de vista previa acoplable"""
        self.preview_window = ctk.CTkToplevel(self.root)
        self.preview_window.title("👁️ Vista Previa del Documento")
        
        # Posicionar a la derecha de la ventana principal
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        
        self.preview_window.geometry(f"400x800+{main_x + main_width + 10}+{main_y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.preview_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, height=50, fg_color="gray25")
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame, text="📄 Vista Previa del Documento",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=15, pady=10)
        
        # Botón actualizar
        refresh_btn = ctk.CTkButton(
            header_frame, text="🔄", width=35, height=35,
            command=self.actualizar_preview,
            font=ctk.CTkFont(size=16)
        )
        refresh_btn.pack(side="right", padx=15)
        
        # Opciones de vista
        options_frame = ctk.CTkFrame(main_frame, height=40)
        options_frame.pack(fill="x", pady=(0, 10))
        options_frame.pack_propagate(False)
        
        self.preview_mode = ctk.CTkSegmentedButton(
            options_frame,
            values=["📝 Texto", "🎨 Formato", "📊 Estructura"],
            command=self.cambiar_modo_preview
        )
        self.preview_mode.pack(padx=10, pady=5)
        self.preview_mode.set("📝 Texto")
        
        # Área de preview con scroll
        self.preview_text = ctk.CTkTextbox(
            main_frame, wrap="word",
            font=ctk.CTkFont(family="Georgia", size=12),
            state="disabled"
        )
        self.preview_text.pack(fill="both", expand=True)
        
        # Actualizar preview inicial
        self.actualizar_preview()
        
        # Configurar para que se actualice automáticamente
        self.preview_window.protocol("WM_DELETE_WINDOW", self.ocultar_preview)


    def actualizar_preview(self):
        """Actualiza el contenido de la vista previa"""
        if not hasattr(self, 'preview_window') or not self.preview_window.winfo_exists():
            return
        
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        
        modo = self.preview_mode.get()
        
        if modo == "📝 Texto":
            # Vista de texto simple
            preview_content = self.generar_preview_texto()
        elif modo == "🎨 Formato":
            # Vista con formato aplicado
            preview_content = self.generar_preview_formato()
        else:
            # Vista de estructura
            preview_content = self.generar_preview_estructura()
        
        self.preview_text.insert("1.0", preview_content)
        self.preview_text.configure(state="disabled")


    def generar_preview_texto(self):
        """Genera vista previa en texto plano"""
        preview = []
        
        # Portada
        preview.append(f"{self.proyecto_data['institucion'].get().upper()}\n")
        preview.append(f"\"{self.proyecto_data['titulo'].get()}\"\n\n")
        
        # Información general
        for campo in ['estudiantes', 'tutores', 'curso', 'año']:
            if campo in self.proyecto_data and self.proyecto_data[campo].get():
                preview.append(f"{campo.title()}: {self.proyecto_data[campo].get()}\n")
        
        preview.append("\n" + "="*50 + "\n\n")
        
        # Contenido de secciones
        for seccion_id in self.secciones_activas:
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                
                if seccion['capitulo']:
                    preview.append(f"\n{seccion['titulo'].upper()}\n")
                    preview.append("="*30 + "\n\n")
                elif seccion_id in self.content_texts:
                    content = self.content_texts[seccion_id].get("1.0", "end").strip()
                    if content:
                        preview.append(f"{seccion['titulo'].upper()}\n")
                        preview.append("-"*20 + "\n")
                        preview.append(f"{content[:500]}{'...' if len(content) > 500 else ''}\n\n")
        
        # Referencias
        if self.referencias:
            preview.append("\nREFERENCIAS\n")
            preview.append("="*30 + "\n")
            for ref in self.referencias[:5]:
                preview.append(f"• {ref['autor']} ({ref['año']}). {ref['titulo']}.\n")
            if len(self.referencias) > 5:
                preview.append(f"... y {len(self.referencias) - 5} referencias más\n")
        
        return ''.join(preview)


    def generar_preview_estructura(self):
        """Genera vista previa de la estructura del documento"""
        preview = ["ESTRUCTURA DEL DOCUMENTO\n", "="*40 + "\n\n"]
        
        # Estadísticas generales
        total_palabras = sum(
            len(self.content_texts[sid].get("1.0", "end").split())
            for sid in self.content_texts if sid in self.secciones_activas
        )
        
        preview.append(f"📊 ESTADÍSTICAS GENERALES:\n")
        preview.append(f"   • Secciones activas: {len(self.secciones_activas)}\n")
        preview.append(f"   • Palabras totales: {total_palabras:,}\n")
        preview.append(f"   • Referencias: {len(self.referencias)}\n")
        preview.append(f"   • Completitud: {self.calcular_completitud()}%\n\n")
        
        preview.append("📋 ESTRUCTURA:\n\n")
        
        # Árbol de secciones
        capitulo_actual = None
        for seccion_id in self.secciones_activas:
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                
                if seccion['capitulo']:
                    capitulo_actual = seccion['titulo']
                    preview.append(f"\n📂 {capitulo_actual}\n")
                else:
                    palabras = 0
                    if seccion_id in self.content_texts:
                        content = self.content_texts[seccion_id].get("1.0", "end").strip()
                        palabras = len(content.split()) if content else 0
                    
                    estado = "✅" if palabras > 50 else "⚠️" if palabras > 0 else "❌"
                    requerida = " (REQ)" if seccion.get('requerida', False) else ""
                    
                    preview.append(f"   {estado} {seccion['titulo']}{requerida} - {palabras} palabras\n")
        
        return ''.join(preview)


    def calcular_completitud(self):
        """Calcula el porcentaje de completitud del proyecto"""
        secciones_requeridas = 0
        secciones_completas = 0
        
        for seccion_id in self.secciones_activas:
            if seccion_id in self.secciones_disponibles:
                seccion = self.secciones_disponibles[seccion_id]
                if seccion.get('requerida', False) and not seccion.get('capitulo', False):
                    secciones_requeridas += 1
                    if seccion_id in self.content_texts:
                        content = self.content_texts[seccion_id].get("1.0", "end").strip()
                        if len(content) > 50:  # Mínimo 50 caracteres
                            secciones_completas += 1
        
        if secciones_requeridas == 0:
            return 100
        
        return int((secciones_completas / secciones_requeridas) * 100)

    class ToolTip:
        """Clase para crear tooltips en widgets de CustomTkinter"""
        def __init__(self, widget, text='tooltip'):
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.on_enter)
            self.widget.bind("<Leave>", self.on_leave)
            self.tooltip = None
        
        def on_enter(self, event=None):
            x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25
            
            self.tooltip = ctk.CTkToplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ctk.CTkLabel(
                self.tooltip, text=self.text,
                fg_color="gray20", corner_radius=6,
                padx=10, pady=5,
                font=ctk.CTkFont(size=11)
            )
            label.pack()
        
        def on_leave(self, event=None):
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None


    # Agregar tooltips a los botones principales
    def agregar_tooltips(self):
        """Agrega tooltips a todos los elementos importantes"""
        tooltips = {
            # Botones principales
            self.guardar_btn: "Guardar proyecto completo (Ctrl+S)",
            self.cargar_btn: "Cargar proyecto existente (Ctrl+O)",
            self.validar_btn: "Validar contenido del proyecto (F5)",
            self.generar_btn: "Generar documento Word (F9)",
            
            # Campos de entrada
            self.proyecto_data['titulo']: "Título completo de tu investigación o proyecto",
            self.proyecto_data['estudiantes']: "Nombres separados por comas: Juan Pérez, María García",
            self.proyecto_data['categoria']: "Selecciona: Ciencia (investigación) o Tecnología (desarrollo)",
            
            # Secciones
            self.agregar_seccion_btn: "Agregar una nueva sección personalizada al documento",
            self.quitar_seccion_btn: "Eliminar secciones seleccionadas (no se pueden eliminar las requeridas)",
            self.subir_btn: "Mover la sección seleccionada hacia arriba en el orden",
            self.bajar_btn: "Mover la sección seleccionada hacia abajo en el orden",
            
            # Referencias
            self.ref_autor: "Formato APA: Apellido, N. o múltiples: García, J. y López, M.",
            self.ref_año: "Año de publicación (4 dígitos)",
            self.ref_titulo: "Título completo sin comillas ni cursivas",
            self.ref_fuente: "Editorial para libros, revista para artículos, URL para web",
            
            # Formato
            self.fuente_texto: "Fuente para el contenido del documento",
            self.tamaño_texto: "Tamaño en puntos para el texto normal",
            self.interlineado: "Espacio entre líneas (APA requiere 2.0)",
            self.margen: "Márgenes en centímetros (APA: 2.54 cm)",
            
            # Opciones de generación
            self.incluir_portada: "Genera página de portada con datos del proyecto",
            self.incluir_indice: "Incluye índice automático (se actualiza en Word)",
            self.incluir_agradecimientos: "Agrega página de agradecimientos después de la portada",
            self.numeracion_paginas: "Numera las páginas del documento"
        }
        
        for widget, texto in tooltips.items():
            if hasattr(self, widget.__name__):
                ToolTip(widget, texto)


    # Ayuda contextual mejorada
    def mostrar_ayuda_contextual(self, seccion):
        """Muestra ayuda específica para cada sección"""
        ayuda_window = ctk.CTkToplevel(self.root)
        ayuda_window.title(f"💡 Ayuda - {seccion}")
        ayuda_window.geometry("600x400")
        
        # Contenido de ayuda específico
        ayudas = {
            "introduccion": {
                "titulo": "📝 Cómo escribir una buena introducción",
                "contenido": """
    La introducción debe:

    ✓ Presentar el tema de investigación
    ✓ Explicar el contexto y antecedentes
    ✓ Mostrar la importancia del estudio
    ✓ Indicar el alcance del trabajo
    ✓ Presentar brevemente la estructura

    Extensión recomendada: 1-2 páginas
    No incluyas: resultados ni conclusiones
                """
            },
            "marco_teorico": {
                "titulo": "📚 Construyendo el marco teórico",
                "contenido": """
    El marco teórico debe:

    ✓ Revisar literatura relevante
    ✓ Definir conceptos clave
    ✓ Presentar teorías relacionadas
    ✓ Mostrar el estado del arte
    ✓ Usar mínimo 10-15 referencias

    IMPORTANTE: Usa citas en formato [CITA:tipo:autor:año]
    Ejemplo: [CITA:parafraseo:García:2020]
                """
            },
            "metodologia": {
                "titulo": "🔬 Describiendo la metodología",
                "contenido": """
    La metodología debe incluir:

    ✓ Tipo de investigación
    ✓ Población y muestra
    ✓ Instrumentos utilizados
    ✓ Procedimientos
    ✓ Análisis de datos

    Sé específico y detallado para permitir replicación
                """
            }
        }
        
        info = ayudas.get(seccion, {"titulo": "Ayuda", "contenido": "Información no disponible"})
        
        # Frame principal
        main_frame = ctk.CTkFrame(ayuda_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text=info["titulo"],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Contenido
        content_text = ctk.CTkTextbox(
            main_frame, wrap="word",
            font=ctk.CTkFont(size=12)
        )
        content_text.pack(fill="both", expand=True, pady=(0, 20))
        content_text.insert("1.0", info["contenido"])
        content_text.configure(state="disabled")
        
        # Botón cerrar
        close_btn = ctk.CTkButton(
            main_frame, text="Entendido",
            command=ayuda_window.destroy
        )
        close_btn.pack()

# Mejoras de accesibilidad para ui/main_window.py

# 1. Configuración de tamaños de fuente escalables
    class FontManager:
        """Gestor de fuentes para accesibilidad"""
        def __init__(self):
            self.base_size = 12
            self.scale = 1.0

        def get_size(self, tipo="normal"):
            sizes = {
                "tiny": int(8 * self.scale),
                "small": int(10 * self.scale),
                "normal": int(12 * self.scale),
                "medium": int(14 * self.scale),
                "large": int(16 * self.scale),
                "xlarge": int(20 * self.scale),
                "title": int(24 * self.scale)
            }
            return sizes.get(tipo, self.base_size)
        
        def increase_scale(self):
            if self.scale < 1.5:
                self.scale += 0.1
                
        def decrease_scale(self):
            if self.scale > 0.7:
                self.scale -= 0.1


    # 2. Detectar tamaño de pantalla y ajustar interfaz
    def configurar_ventana_responsiva(self):
        """Configura la ventana según el tamaño de pantalla"""
        # Obtener dimensiones de pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcular tamaño óptimo (80% de la pantalla)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Límites mínimos y máximos
        window_width = max(1000, min(window_width, 1600))
        window_height = max(600, min(window_height, 900))
        
        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Ajustar componentes según tamaño
        if screen_width < 1366:  # Pantallas pequeñas
            self.modo_compacto = True
            self.ajustar_modo_compacto()
        elif screen_width > 1920:  # Pantallas grandes
            self.modo_expandido = True
            self.ajustar_modo_expandido()


    # 3. Modo compacto para pantallas pequeñas
    def ajustar_modo_compacto(self):
        """Ajusta la interfaz para pantallas pequeñas"""
        # Reducir padding
        self.padding_x = 5
        self.padding_y = 5
        
        # Ocultar paneles secundarios por defecto
        if hasattr(self, 'control_frame'):
            self.control_frame.configure(width=250)  # Panel lateral más estrecho
        
        # Usar fuentes más pequeñas
        self.font_manager.scale = 0.9
        
        # Reducir altura de componentes
        self.default_entry_height = 30
        self.default_button_height = 35


    # 4. Modo expandido para pantallas grandes
    def ajustar_modo_expandido(self):
        """Ajusta la interfaz para pantallas grandes"""
        # Aumentar padding
        self.padding_x = 20
        self.padding_y = 15
        
        # Expandir paneles
        if hasattr(self, 'control_frame'):
            self.control_frame.configure(width=400)  # Panel lateral más ancho
        
        # Usar fuentes más grandes
        self.font_manager.scale = 1.2
        
        # Aumentar altura de componentes
        self.default_entry_height = 40
        self.default_button_height = 45


    # 5. Atajos de teclado mejorados para accesibilidad
    def configurar_atajos_accesibilidad(self):
        """Configura atajos de teclado adicionales para accesibilidad"""
        # Navegación entre pestañas
        self.root.bind('<Control-Tab>', self.siguiente_pestaña)
        self.root.bind('<Control-Shift-Tab>', self.pestaña_anterior)
        
        # Zoom de interfaz
        self.root.bind('<Control-plus>', self.aumentar_zoom)
        self.root.bind('<Control-minus>', self.disminuir_zoom)
        self.root.bind('<Control-0>', self.restablecer_zoom)
        
        # Navegación entre secciones
        self.root.bind('<Alt-Up>', lambda e: self.subir_seccion())
        self.root.bind('<Alt-Down>', lambda e: self.bajar_seccion())
        
        # Acceso rápido a funciones
        self.root.bind('<F1>', lambda e: self.mostrar_instrucciones())
        self.root.bind('<F2>', lambda e: self.ir_a_seccion_actual())
        self.root.bind('<F3>', lambda e: self.buscar_en_contenido())
        self.root.bind('<F4>', lambda e: self.mostrar_preview())


    # 6. Función de zoom
    def aumentar_zoom(self, event=None):
        """Aumenta el tamaño de la interfaz"""
        self.font_manager.increase_scale()
        self.actualizar_tamaños_fuente()
        
    def disminuir_zoom(self, event=None):
        """Disminuye el tamaño de la interfaz"""
        self.font_manager.decrease_scale()
        self.actualizar_tamaños_fuente()
        
    def restablecer_zoom(self, event=None):
        """Restablece el tamaño por defecto"""
        self.font_manager.scale = 1.0
        self.actualizar_tamaños_fuente()


    # 7. Alto contraste para mejor visibilidad
    def toggle_alto_contraste(self):
        """Alterna entre modo normal y alto contraste"""
        if not hasattr(self, 'alto_contraste'):
            self.alto_contraste = False
        
        self.alto_contraste = not self.alto_contraste
        
        if self.alto_contraste:
            # Colores de alto contraste
            ctk.set_appearance_mode("light")
            self.colores = {
                'bg': 'white',
                'fg': 'black',
                'button': '#0066CC',
                'button_hover': '#0052A3',
                'success': '#008000',
                'error': '#CC0000',
                'warning': '#FF8C00'
            }
        else:
            # Colores normales
            ctk.set_appearance_mode("dark")
            self.colores = {
                'bg': 'gray15',
                'fg': 'white',
                'button': 'blue',
                'button_hover': 'darkblue',
                'success': 'green',
                'error': 'red',
                'warning': 'orange'
            }
        
        # Aplicar colores
        self.aplicar_tema()


    # 8. Indicadores visuales mejorados
    def agregar_indicadores_visuales(self):
        """Agrega indicadores visuales para mejor feedback"""
        # Indicador de campo activo
        def on_focus_in(event):
            event.widget.configure(border_color="blue", border_width=2)
        
        def on_focus_out(event):
            event.widget.configure(border_color="gray40", border_width=1)
        
        # Aplicar a todos los campos de entrada
        for widget in self.root.winfo_children():
            if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                widget.bind("<FocusIn>", on_focus_in)
                widget.bind("<FocusOut>", on_focus_out)


    # 9. Mensajes de estado hablados (para lectores de pantalla)
    def anunciar_estado(self, mensaje):
        """Anuncia un mensaje de estado para accesibilidad"""
        # Crear label temporal para lectores de pantalla
        if hasattr(self, 'status_announcement'):
            self.status_announcement.destroy()
        
        self.status_announcement = ctk.CTkLabel(
            self.root, text=mensaje,
            fg_color="transparent", text_color="transparent"
        )
        self.status_announcement.pack()
        
        # Eliminar después de 3 segundos
        self.root.after(3000, lambda: self.status_announcement.destroy() if hasattr(self, 'status_announcement') else None)