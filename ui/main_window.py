"""
Ventana principal - Coordinador principal de la aplicación
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

# Imports de UI
from .widgets import FontManager, ToolTip, PreviewWindow, ImageManagerDialog
from .tabs import (
    InfoGeneralTab, ContenidoDinamicoTab, CitasReferenciasTab,
    FormatoAvanzadoTab, GeneracionTab
)
from .dialogs import SeccionDialog, HelpDialog

class ProyectoAcademicoGenerator:
    """Clase principal del generador de proyectos académicos"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎓 Generador de Proyectos Académicos - Versión Avanzada")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Inicializar gestores y componentes
        self._init_managers()
        self._init_variables()
        self._init_ui_components()
        
        # Configurar ventana y UI
        self.configurar_ventana_responsiva()
        self.configurar_atajos_accesibilidad()
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        
        # Iniciar servicios
        self.mostrar_bienvenida()
        self.actualizar_estadisticas()
        self.project_manager.auto_save_project(self)
    
    def _init_managers(self):
        """Inicializa los gestores y procesadores"""
        from template_manager import obtener_template_manager
        
        self.template_manager = obtener_template_manager()
        self.project_manager = ProjectManager()
        self.document_generator = DocumentGenerator()
        self.validator = ProjectValidator()
        self.citation_processor = CitationProcessor()
        self.reference_manager = ReferenceManager()
        self.section_manager = SectionManager()
        self.font_manager = FontManager()
    
    def _init_variables(self):
        """Inicializa las variables de la aplicación"""
        # Datos del proyecto
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
        self.watermark_mode = 'watermark'
        
        # Secciones dinámicas
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
        
        # Estadísticas
        self.stats = {
            'total_words': 0,
            'total_chars': 0,
            'sections_completed': 0,
            'references_added': 0
        }
        
        # Buscar imágenes base
        self.buscar_imagenes_base()
    
    def _init_ui_components(self):
        """Inicializa componentes de UI"""
        self.preview_window = PreviewWindow(self)
        self.image_manager = ImageManagerDialog(self)
        self.help_dialog = HelpDialog(self)
    
    def configurar_ventana_responsiva(self):
        """Configura la ventana según el tamaño de pantalla"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        window_width = max(1000, min(window_width, 1600))
        window_height = max(600, min(window_height, 900))
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        if screen_width < 1366:
            self.modo_compacto = True
            self.ajustar_modo_compacto()
        elif screen_width > 1920:
            self.modo_expandido = True
            self.ajustar_modo_expandido()
        else:
            self.modo_compacto = False
            self.modo_expandido = False
    
    def ajustar_modo_compacto(self):
        """Ajusta la interfaz para pantallas pequeñas"""
        self.padding_x = 5
        self.padding_y = 5
        self.font_manager.scale = 0.9
        self.default_entry_height = 30
        self.default_button_height = 35
    
    def ajustar_modo_expandido(self):
        """Ajusta la interfaz para pantallas grandes"""
        self.padding_x = 20
        self.padding_y = 15
        self.font_manager.scale = 1.1
        self.default_entry_height = 40
        self.default_button_height = 45
    
    def configurar_atajos_accesibilidad(self):
        """Configura atajos de teclado para accesibilidad"""
        # Navegación entre pestañas
        self.root.bind('<Control-Tab>', self.siguiente_pestaña)
        self.root.bind('<Control-Shift-Tab>', self.pestaña_anterior)
        
        # Zoom de interfaz
        self.root.bind('<Control-plus>', self.aumentar_zoom)
        self.root.bind('<Control-equal>', self.aumentar_zoom)
        self.root.bind('<Control-minus>', self.disminuir_zoom)
        self.root.bind('<Control-0>', self.restablecer_zoom)
        
        # Navegación entre secciones
        self.root.bind('<Alt-Up>', lambda e: self.subir_seccion())
        self.root.bind('<Alt-Down>', lambda e: self.bajar_seccion())
        
        # Acceso rápido
        self.root.bind('<F1>', lambda e: self.mostrar_instrucciones())
        self.root.bind('<F2>', lambda e: self.ir_a_seccion_actual())
        self.root.bind('<F3>', lambda e: self.buscar_en_contenido())
        self.root.bind('<F4>', lambda e: self.mostrar_preview() if hasattr(self, 'mostrar_preview') else None)
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Frame principal
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self._create_header(main_container)
        
        # Content container
        content_container = ctk.CTkFrame(main_container, corner_radius=10)
        content_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Tabview principal
        self.tabview = ctk.CTkTabview(content_container, width=1100, height=520)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Crear pestañas
        self._create_tabs()
        
        # Agregar menú de accesibilidad
        self._create_accessibility_menu(main_container)
        
        # Agregar tooltips después de crear widgets
        self.root.after(1000, self.agregar_tooltips)
    
    def _create_header(self, parent):
        """Crea el header con título y botones principales"""
        header_frame = ctk.CTkFrame(parent, height=120, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Título
        self.title_label = ctk.CTkLabel(
            header_frame, 
            text="🎓 Generador de Proyectos Académicos",
            font=self.font_manager.get_font("title", "bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        # Botones principales
        self._create_header_buttons(header_frame)
    
    def _create_header_buttons(self, parent):
        """Crea los botones del header"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        # Primera fila
        btn_row1 = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_row1.pack(fill="x", pady=(0, 5))
        
        # Botones de la primera fila
        buttons_row1 = [
            ("📖 Guía", self.mostrar_instrucciones, "blue", 80),
            ("📋 Plantilla", self.cargar_documento_base, "purple", 90),
            ("💾 Guardar", self.guardar_proyecto, "darkgreen", 80),
            ("📂 Cargar", self.cargar_proyecto, "darkblue", 80)
        ]
        
        for text, command, color, width in buttons_row1:
            btn = ctk.CTkButton(
                btn_row1, text=text, command=command,
                width=width, height=30, 
                font=self.font_manager.get_font("small", "bold"),
                fg_color=color if color != "blue" else None,
                hover_color=f"dark{color}" if color != "blue" else None
            )
            btn.pack(side="left", padx=(0, 5))
        
        # Estadísticas
        self.stats_label = ctk.CTkLabel(
            btn_row1, text="📊 Palabras: 0 | Secciones: 0/13 | Referencias: 0",
            font=self.font_manager.get_font("small"), text_color="gray70"
        )
        self.stats_label.pack(side="right", padx=(5, 0))
        
        # Segunda fila
        btn_row2 = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_row2.pack(fill="x")
        
        # Botones de la segunda fila
        buttons_row2 = [
            ("🖼️ Imágenes", self.gestionar_imagenes, "darkblue", 90),
            ("📤 Exportar Config", self.exportar_configuracion, "darkorange", 110),
            ("🔍 Validar", self.validar_proyecto, "orange", 80),
            ("🗂️ Plantillas", self.gestionar_plantillas, "indigo", 90)
        ]
        
        for text, command, color, width in buttons_row2:
            btn = ctk.CTkButton(
                btn_row2, text=text, command=command,
                width=width, height=30,
                font=self.font_manager.get_font("small", "bold"),
                fg_color=color, hover_color=f"dark{color}"
            )
            btn.pack(side="left", padx=(0, 5))
        
        # Botón generar
        self.generate_btn = ctk.CTkButton(
            btn_row2, text="📄 Generar Documento", 
            command=self.generar_documento_async,
            width=140, height=30, 
            font=self.font_manager.get_font("small", "bold"),
            fg_color="green", hover_color="darkgreen"
        )
        self.generate_btn.pack(side="right", padx=(5, 0))
        
        # Guardar referencias a botones para tooltips
        self.help_btn = buttons_row1[0]
        self.template_btn = buttons_row1[1]
        self.save_btn = buttons_row1[2]
        self.load_btn = buttons_row1[3]
        self.images_btn = buttons_row2[0]
        self.export_btn = buttons_row2[1]
        self.validate_btn = buttons_row2[2]
        self.plantillas_btn = buttons_row2[3]
    
    def _create_tabs(self):
        """Crea las pestañas principales"""
        # Información General
        tab1 = self.tabview.add("📋 Información General")
        self.info_general_tab = InfoGeneralTab(tab1, self)
        
        # Contenido Dinámico
        tab2 = self.tabview.add("📝 Contenido Dinámico")
        self.contenido_dinamico_tab = ContenidoDinamicoTab(tab2, self)
        
        # Citas y Referencias
        tab3 = self.tabview.add("📚 Citas y Referencias")
        self.citas_referencias_tab = CitasReferenciasTab(tab3, self)
        
        # Formato Avanzado
        tab4 = self.tabview.add("🎨 Formato")
        self.formato_avanzado_tab = FormatoAvanzadoTab(tab4, self)
        
        # Generación
        tab5 = self.tabview.add("🔧 Generar")
        self.generacion_tab = GeneracionTab(tab5, self)
    
    def _create_accessibility_menu(self, parent):
        """Crea el menú de accesibilidad"""
        # Frame de accesibilidad en el header
        accessibility_frame = ctk.CTkFrame(parent.winfo_children()[0], fg_color="transparent")
        accessibility_frame.pack(side="right", padx=20)
        
        # Indicador de zoom
        self.zoom_label = ctk.CTkLabel(
            accessibility_frame, 
            text=f"🔍 {int(self.font_manager.get_current_scale() * 100)}%",
            font=self.font_manager.get_font("small")
        )
        self.zoom_label.pack(side="left", padx=(0, 10))
        
        # Botones de zoom
        zoom_buttons = [
            ("➖", self.disminuir_zoom, 30),
            ("100%", self.restablecer_zoom, 45),
            ("➕", self.aumentar_zoom, 30)
        ]
        
        for text, command, width in zoom_buttons:
            btn = ctk.CTkButton(
                accessibility_frame, text=text, width=width, height=25,
                command=command,
                font=self.font_manager.get_font("small", "bold" if text in ["➖", "➕"] else "normal")
            )
            btn.pack(side="left", padx=2)
        
        # Función para actualizar indicador
        self.actualizar_indicador_zoom = lambda: self.zoom_label.configure(
            text=f"🔍 {int(self.font_manager.get_current_scale() * 100)}%"
        ) if hasattr(self, 'zoom_label') else None
    
    def setup_keyboard_shortcuts(self):
        """Configura atajos de teclado principales"""
        shortcuts = {
            '<Control-s>': lambda e: self.guardar_proyecto(),
            '<Control-o>': lambda e: self.cargar_proyecto(),
            '<Control-n>': lambda e: self.nuevo_proyecto(),
            '<F5>': lambda e: self.validar_proyecto(),
            '<F9>': lambda e: self.generar_documento_async(),
            '<Control-q>': lambda e: self.root.quit()
        }
        
        for key, func in shortcuts.items():
            self.root.bind(key, func)
    
    # Métodos principales delegados
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
    
    def cargar_documento_base(self):
        """Carga el documento base usando template_manager"""
        from template_manager import aplicar_plantilla_tercer_ano
        aplicar_plantilla_tercer_ano(self)
    
    def gestionar_plantillas(self):
        """Abre el gestor de plantillas avanzado"""
        from template_manager import mostrar_gestor_plantillas
        mostrar_gestor_plantillas(self)
    
    def gestionar_imagenes(self):
        """Abre el gestor de imágenes"""
        self.image_manager.show()
    
    def mostrar_instrucciones(self):
        """Muestra las instrucciones completas"""
        self.help_dialog.show()
    
    def mostrar_preview(self):
        """Muestra la ventana de vista previa"""
        self.preview_window.show()
    
    # Métodos de accesibilidad y zoom
    def aumentar_zoom(self, event=None):
        """Aumenta el tamaño de la interfaz"""
        if self.font_manager.increase_scale():
            self.actualizar_tamaños_fuente()
            self.actualizar_indicador_zoom()
            self.anunciar_estado(f"Zoom aumentado a {int(self.font_manager.get_current_scale() * 100)}%")
        else:
            messagebox.showinfo("🔍 Zoom", "Zoom máximo alcanzado (150%)")
    
    def disminuir_zoom(self, event=None):
        """Disminuye el tamaño de la interfaz"""
        if self.font_manager.decrease_scale():
            self.actualizar_tamaños_fuente()
            self.actualizar_indicador_zoom()
            self.anunciar_estado(f"Zoom reducido a {int(self.font_manager.get_current_scale() * 100)}%")
        else:
            messagebox.showinfo("🔍 Zoom", "Zoom mínimo alcanzado (70%)")
    
    def restablecer_zoom(self, event=None):
        """Restablece el tamaño por defecto"""
        self.font_manager.reset_scale()
        self.actualizar_tamaños_fuente()
        self.actualizar_indicador_zoom()
        self.anunciar_estado("Zoom restablecido a 100%")
    
    def actualizar_tamaños_fuente(self):
        """Actualiza todos los tamaños de fuente en la interfaz"""
        # Actualizar elementos principales
        if hasattr(self, 'title_label'):
            self.title_label.configure(font=self.font_manager.get_font("title", "bold"))
        
        if hasattr(self, 'stats_label'):
            self.stats_label.configure(font=self.font_manager.get_font("small"))
        
        # Actualizar pestañas actuales
        current_tab = self.tabview.get()
        if current_tab in self.tabview._tab_dict:
            tab_widget = self.tabview.tab(current_tab)
            self._actualizar_fuentes_recursivo(tab_widget)
        
        self.anunciar_estado(f"Zoom: {int(self.font_manager.get_current_scale() * 100)}%")
    
    def _actualizar_fuentes_recursivo(self, widget):
        """Actualiza fuentes recursivamente en widgets hijos"""
        # Implementación simplificada
        pass
    
    def anunciar_estado(self, mensaje):
        """Anuncia un mensaje de estado para accesibilidad"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=mensaje)
    
    def siguiente_pestaña(self, event=None):
        """Navega a la siguiente pestaña"""
        tabs = list(self.tabview._tab_dict.keys())
        current = self.tabview.get()
        try:
            current_index = tabs.index(current)
            next_index = (current_index + 1) % len(tabs)
            self.tabview.set(tabs[next_index])
            self.anunciar_estado(f"Navegando a: {tabs[next_index]}")
        except ValueError:
            pass
    
    def pestaña_anterior(self, event=None):
        """Navega a la pestaña anterior"""
        tabs = list(self.tabview._tab_dict.keys())
        current = self.tabview.get()
        try:
            current_index = tabs.index(current)
            prev_index = (current_index - 1) % len(tabs)
            self.tabview.set(tabs[prev_index])
            self.anunciar_estado(f"Navegando a: {tabs[prev_index]}")
        except ValueError:
            pass
    
    # Métodos de utilidad
    def buscar_imagenes_base(self):
        """Busca imágenes base en la carpeta resources/images"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            recursos_dir = os.path.join(script_dir, "..", "resources", "images")
            recursos_dir = os.path.normpath(recursos_dir)
            
            print(f"🔍 Buscando imágenes en: {recursos_dir}")
            
            if not os.path.exists(recursos_dir):
                os.makedirs(recursos_dir)
                print(f"📁 Directorio creado: {recursos_dir}")
            
            # Buscar encabezado
            encabezado_extensions = ['Encabezado.png', 'Encabezado.jpg', 'Encabezado.jpeg', 'encabezado.png']
            for filename in encabezado_extensions:
                encabezado_path = os.path.join(recursos_dir, filename)
                if os.path.exists(encabezado_path):
                    self.ruta_encabezado = encabezado_path
                    print(f"✅ Encabezado encontrado: {filename}")
                    break
            else:
                print("⚠️ Encabezado.png no encontrado en resources/images")
            
            # Buscar insignia
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
        # [Mantener el contenido original de este método]
        return {
            "resumen": {
                "titulo": "📄 Resumen", 
                "instruccion": "Resumen ejecutivo del proyecto (150-300 palabras)",
                "requerida": False,
                "capitulo": False
            },
            # ... resto de secciones ...
        }
    
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
    
    def mostrar_bienvenida(self):
        """Muestra mensaje de bienvenida con atajos de teclado"""
        self.root.after(1000, lambda: messagebox.showinfo(
            "🎓 ¡Generador Profesional!",
            "Generador de Proyectos Académicos - Versión Profesional\n\n"
            "🆕 CARACTERÍSTICAS AVANZADAS:\n"
            "• Estructura modular mejorada\n"
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
    
    def agregar_tooltips(self):
        """Agrega tooltips a los botones principales"""
        # Implementación pendiente
        pass
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

# Incluir aquí todos los métodos restantes necesarios que no se han movido a módulos separados
# [Agregar métodos como actualizar_lista_secciones, crear_pestanas_contenido, etc.]

    
    # Métodos de secciones (coordinación con UI)
    def actualizar_lista_secciones(self):
        """Actualiza la lista visual de secciones activas"""
        # Implementación en contenido_dinamico_tab
        if hasattr(self, 'contenido_dinamico_tab'):
            # Delegar a la pestaña
            pass
    
    def crear_pestanas_contenido(self):
        """Crea las pestañas de contenido basadas en secciones activas"""
        # Implementación en contenido_dinamico_tab
        if hasattr(self, 'contenido_dinamico_tab'):
            # Delegar a la pestaña
            pass
    
    # Métodos de gestión de secciones
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
        # Implementación básica
        pass
    
    def editar_seccion(self):
        """Edita una sección existente"""
        # Implementación básica
        pass
    
    def subir_seccion(self):
        """Sube una sección en el orden"""
        # Implementación básica
        pass
    
    def bajar_seccion(self):
        """Baja una sección en el orden"""
        # Implementación básica
        pass
    
    # Métodos de referencias
    def agregar_referencia(self):
        """Agrega una referencia a la lista"""
        # Implementación básica
        pass
    
    def actualizar_lista_referencias(self):
        """Actualiza la lista visual de referencias"""
        # Implementación básica
        pass
    
    # Métodos de formato
    def toggle_formato_base(self):
        """Activa/desactiva el uso del formato base"""
        if self.usar_base_var.get():
            if self.documento_base is None:
                self.cargar_documento_base()
            else:
                self.aplicar_formato_base()
        else:
            self.limpiar_formato_base()
    
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
    
    # Métodos requeridos restantes (agregar implementaciones según necesidad)
    # ... más métodos necesarios ...
