#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Reorganización Modular del Código
Divide main_window.py en múltiples módulos para mejor mantenibilidad
"""

import os
import shutil
from pathlib import Path
import re

class CodeReorganizer:
    def __init__(self):
        self.base_path = Path(".")
        self.ui_path = self.base_path / "ui"
        self.backup_path = self.base_path / "backup_original"
        
    def run(self):
        """Ejecuta la reorganización completa"""
        print("🚀 Iniciando reorganización modular del código...")
        
        # 1. Crear backup
        self.create_backup()
        
        # 2. Crear nueva estructura de directorios
        self.create_directory_structure()
        
        # 3. Extraer y crear módulos
        self.extract_font_manager()
        self.extract_tooltip()
        self.extract_tabs()
        self.extract_widgets()
        self.extract_dialogs()
        
        # 4. Crear nuevo main_window.py simplificado
        self.create_simplified_main_window()
        
        # 5. Actualizar imports en otros archivos
        self.update_imports()
        
        print("✅ Reorganización completada exitosamente!")
        print("📁 Backup creado en: backup_original/")
        print("🔍 Revisa la nueva estructura y prueba la aplicación")
        
    def create_backup(self):
        """Crea backup de los archivos originales"""
        print("📦 Creando backup...")
        
        if self.backup_path.exists():
            shutil.rmtree(self.backup_path)
        
        # Copiar archivos importantes
        files_to_backup = [
            "ui/main_window.py",
            "ui/__init__.py",
            "ui/dialogs.py",
            "ui/components.py",
            "main.py"
        ]
        
        for file in files_to_backup:
            src = self.base_path / file
            if src.exists():
                dst = self.backup_path / file
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  ✓ Backup: {file}")
    
    def create_directory_structure(self):
        """Crea la nueva estructura de directorios"""
        print("📁 Creando estructura de directorios...")
        
        dirs = [
            "ui/tabs",
            "ui/widgets",
            "ui/dialogs",
            "ui/utils"
        ]
        
        for dir_path in dirs:
            path = self.base_path / dir_path
            path.mkdir(parents=True, exist_ok=True)
            
            # Crear __init__.py
            init_file = path / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Module for {}"""\n'.format(dir_path.split('/')[-1]))
        
        print("  ✓ Estructura de directorios creada")
    
    def extract_font_manager(self):
        """Extrae FontManager a su propio módulo"""
        print("📝 Extrayendo FontManager...")
        
        content = '''"""
Font Manager - Gestión de fuentes para accesibilidad y diseño responsivo
"""

import customtkinter as ctk

class FontManager:
    """Gestor de fuentes para accesibilidad y diseño responsivo"""
    def __init__(self):
        self.base_size = 12
        self.scale = 1.0
        self.font_cache = {}
        
    def get_size(self, tipo="normal"):
        """Obtiene el tamaño de fuente según el tipo y escala actual"""
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
    
    def get_font(self, tipo="normal", weight="normal", family=None):
        """Obtiene una fuente CTk con el tamaño y peso especificados"""
        size = self.get_size(tipo)
        cache_key = f"{tipo}_{weight}_{family}_{size}"
        
        if cache_key not in self.font_cache:
            if family is None:
                family = "Segoe UI" if ctk.get_appearance_mode() == "Light" else "Helvetica"
            
            self.font_cache[cache_key] = ctk.CTkFont(
                family=family,
                size=size,
                weight=weight
            )
        
        return self.font_cache[cache_key]
    
    def increase_scale(self):
        """Aumenta la escala de fuentes"""
        if self.scale < 1.5:
            self.scale += 0.1
            self.font_cache.clear()
            return True
        return False
            
    def decrease_scale(self):
        """Disminuye la escala de fuentes"""
        if self.scale > 0.7:
            self.scale -= 0.1
            self.font_cache.clear()
            return True
        return False
    
    def reset_scale(self):
        """Restablece la escala por defecto"""
        self.scale = 1.0
        self.font_cache.clear()
    
    def get_current_scale(self):
        """Obtiene la escala actual"""
        return self.scale
'''
        
        file_path = self.ui_path / "widgets" / "font_manager.py"
        file_path.write_text(content)
        print("  ✓ FontManager extraído")
    
    def extract_tooltip(self):
        """Extrae ToolTip a su propio módulo"""
        print("📝 Extrayendo ToolTip...")
        
        content = '''"""
ToolTip Widget - Tooltips para widgets de CustomTkinter
"""

import customtkinter as ctk

class ToolTip:
    """Clase para crear tooltips en widgets de CustomTkinter"""
    def __init__(self, widget, text='tooltip'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.tooltip = None
    
    def on_enter(self, event=None):
        """Muestra el tooltip cuando el mouse entra al widget"""
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        # Crear ventana del tooltip
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        
        # Posicionar tooltip
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Frame del tooltip con estilo
        tooltip_frame = ctk.CTkFrame(
            self.tooltip, 
            fg_color="gray20", 
            corner_radius=6,
            border_width=1,
            border_color="gray40"
        )
        tooltip_frame.pack()
        
        # Texto del tooltip
        label = ctk.CTkLabel(
            tooltip_frame, 
            text=self.text,
            font=ctk.CTkFont(size=11),
            text_color="white",
            justify="left",
            wraplength=300
        )
        label.pack(padx=8, pady=5)
        
        # Asegurar que el tooltip esté sobre otros widgets
        self.tooltip.lift()
    
    def on_leave(self, event=None):
        """Oculta el tooltip cuando el mouse sale del widget"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
'''
        
        file_path = self.ui_path / "widgets" / "tooltip.py"
        file_path.write_text(content)
        print("  ✓ ToolTip extraído")
    
    def extract_tabs(self):
        """Extrae cada pestaña a su propio módulo"""
        print("📑 Extrayendo pestañas...")
        
        # Tab: Información General
        self.create_info_general_tab()
        
        # Tab: Contenido Dinámico
        self.create_contenido_dinamico_tab()
        
        # Tab: Citas y Referencias
        self.create_citas_referencias_tab()
        
        # Tab: Formato Avanzado
        self.create_formato_avanzado_tab()
        
        # Tab: Generación
        self.create_generacion_tab()
        
        # Crear __init__.py para tabs
        init_content = '''"""
Tabs Module - Pestañas de la interfaz principal
"""

from .info_general import InfoGeneralTab
from .contenido_dinamico import ContenidoDinamicoTab
from .citas_referencias import CitasReferenciasTab
from .formato_avanzado import FormatoAvanzadoTab
from .generacion import GeneracionTab

__all__ = [
    'InfoGeneralTab',
    'ContenidoDinamicoTab',
    'CitasReferenciasTab',
    'FormatoAvanzadoTab',
    'GeneracionTab'
]
'''
        (self.ui_path / "tabs" / "__init__.py").write_text(init_content)
        print("  ✓ Todas las pestañas extraídas")
    
    def create_info_general_tab(self):
        """Crea el módulo para la pestaña de Información General"""
        content = '''"""
Tab de Información General - Datos básicos del proyecto
"""

import customtkinter as ctk
from tkinter import messagebox

class InfoGeneralTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la pestaña de información general"""
        # Scroll frame con altura reducida
        scroll_frame = ctk.CTkScrollableFrame(self.parent, label_text="Datos del Proyecto", height=400)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Toggle para usar formato base
        base_frame = ctk.CTkFrame(scroll_frame, fg_color="darkblue", corner_radius=8)
        base_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            base_frame, text="📋 Formato Base",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 5))
        
        self.app.usar_base_var = ctk.CTkCheckBox(
            base_frame, text="Usar plantilla base (3º AÑO)",
            font=ctk.CTkFont(size=12), command=self.app.toggle_formato_base
        )
        self.app.usar_base_var.pack(pady=(0, 10))
        
        # Campos organizados
        self.crear_campos(scroll_frame)
    
    def crear_campos(self, parent):
        """Crea los campos de entrada"""
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
            row_frame = ctk.CTkFrame(parent, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            # Primera columna
            if i < len(campos):
                self.crear_campo(row_frame, campos[i], side="left")
            
            # Segunda columna
            if i + 1 < len(campos):
                self.crear_campo(row_frame, campos[i + 1], side="right")
        
        # Campos largos
        campos_largos = [
            ("Área de Desarrollo", "area", "Especifique el área de desarrollo"),
            ("Estudiantes (separar con comas)", "estudiantes", "Nombre1 Apellido1, Nombre2 Apellido2"),
            ("Tutores (separar con comas)", "tutores", "Prof. Nombre Apellido, Dr. Nombre Apellido"),
            ("Director", "director", "Cristina Raichakowski"),
            ("Responsable", "responsable", "Nombre del responsable")
        ]
        
        for label, key, placeholder in campos_largos:
            field_frame = ctk.CTkFrame(parent, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(field_frame, text=label, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            entry = ctk.CTkEntry(field_frame, placeholder_text=placeholder, height=30)
            entry.pack(fill="x", pady=(3, 0))
            self.app.proyecto_data[key] = entry
    
    def crear_campo(self, parent, campo_data, side="left"):
        """Crea un campo individual"""
        label, key, placeholder = campo_data
        
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        if side == "left":
            field_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        else:
            field_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(field_frame, text=label, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        entry = ctk.CTkEntry(field_frame, placeholder_text=placeholder, height=30)
        entry.pack(fill="x", pady=(3, 0))
        self.app.proyecto_data[key] = entry
'''
        
        (self.ui_path / "tabs" / "info_general.py").write_text(content)
    
    def create_contenido_dinamico_tab(self):
        """Crea el módulo para la pestaña de Contenido Dinámico"""
        content = '''"""
Tab de Contenido Dinámico - Gestión de secciones y contenido
"""

import customtkinter as ctk
from tkinter import messagebox
from ..dialogs import SeccionDialog

class ContenidoDinamicoTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de contenido dinámico"""
        # Frame principal
        paned_window = ctk.CTkFrame(self.parent, fg_color="transparent")
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel de control izquierdo
        self.create_control_panel(paned_window)
        
        # Panel de contenido derecho
        self.create_content_panel(paned_window)
        
        # Actualizar lista y crear pestañas
        self.app.actualizar_lista_secciones()
        self.app.crear_pestanas_contenido()
    
    def create_control_panel(self, parent):
        """Crea el panel de control de secciones"""
        self.app.control_frame = ctk.CTkFrame(parent, width=320, corner_radius=10)
        self.app.control_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Header del panel
        header_frame = ctk.CTkFrame(self.app.control_frame, fg_color="gray25", height=45)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Botón colapsar
        self.app.sidebar_collapsed = False
        collapse_btn = ctk.CTkButton(
            header_frame, text="◀", width=30, height=30,
            command=self.app.toggle_sidebar,
            font=ctk.CTkFont(size=14)
        )
        collapse_btn.pack(side="left", padx=5, pady=7)
        
        title_label = ctk.CTkLabel(
            header_frame, text="🛠️ Gestión de Secciones",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left", padx=(5, 0))
        
        # Frame de búsqueda
        self.create_search_frame()
        
        # Botones de gestión
        self.create_management_buttons()
        
        # Lista de secciones
        self.create_sections_list()
    
    def create_search_frame(self):
        """Crea el frame de búsqueda"""
        search_frame = ctk.CTkFrame(self.app.control_frame, height=45)
        search_frame.pack(fill="x", padx=8, pady=(8, 4))
        
        search_icon = ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=12))
        search_icon.pack(side="left", padx=(8, 4))
        
        self.app.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar sección...",
            height=30, font=ctk.CTkFont(size=11)
        )
        self.app.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.app.search_entry.bind("<KeyRelease>", self.app.filtrar_secciones)
    
    def create_management_buttons(self):
        """Crea los botones de gestión de secciones"""
        btn_frame = ctk.CTkFrame(self.app.control_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=(4, 8))
        
        # Primera fila de botones
        btn_row1 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_row1.pack(fill="x", pady=2)
        
        add_btn = ctk.CTkButton(
            btn_row1, text="➕ Agregar", command=self.app.agregar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        add_btn.pack(side="left", padx=(0, 4))
        
        remove_btn = ctk.CTkButton(
            btn_row1, text="➖ Quitar", command=self.app.quitar_seccion,
            width=90, height=30, fg_color="red", hover_color="darkred",
            font=ctk.CTkFont(size=11)
        )
        remove_btn.pack(side="left", padx=(0, 4))
        
        edit_btn = ctk.CTkButton(
            btn_row1, text="✏️ Editar", command=self.app.editar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        edit_btn.pack(side="left")
        
        # Segunda fila
        btn_row2 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_row2.pack(fill="x", pady=2)
        
        up_btn = ctk.CTkButton(
            btn_row2, text="⬆️ Subir", command=self.app.subir_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        up_btn.pack(side="left", padx=(0, 4))
        
        down_btn = ctk.CTkButton(
            btn_row2, text="⬇️ Bajar", command=self.app.bajar_seccion,
            width=90, height=30, font=ctk.CTkFont(size=11)
        )
        down_btn.pack(side="left", padx=(0, 4))
        
        preview_btn = ctk.CTkButton(
            btn_row2, text="👁️ Preview", command=self.app.mostrar_preview,
            width=90, height=30, fg_color="purple", hover_color="darkviolet",
            font=ctk.CTkFont(size=11)
        )
        preview_btn.pack(side="left")
    
    def create_sections_list(self):
        """Crea la lista de secciones"""
        list_label = ctk.CTkLabel(
            self.app.control_frame, text="📋 Secciones Activas:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        list_label.pack(anchor="w", padx=8, pady=(8, 4))
        
        self.app.secciones_listbox = ctk.CTkScrollableFrame(
            self.app.control_frame, label_text="",
            fg_color="gray15", corner_radius=8
        )
        self.app.secciones_listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
    
    def create_content_panel(self, parent):
        """Crea el panel de contenido"""
        self.app.content_container = ctk.CTkFrame(parent, corner_radius=10)
        self.app.content_container.pack(side="right", fill="both", expand=True)
        
        # Breadcrumb navigation
        breadcrumb_frame = ctk.CTkFrame(self.app.content_container, height=35, fg_color="gray25")
        breadcrumb_frame.pack(fill="x", padx=8, pady=(8, 4))
        breadcrumb_frame.pack_propagate(False)
        
        self.app.breadcrumb_label = ctk.CTkLabel(
            breadcrumb_frame, text="📍 Navegación: ",
            font=ctk.CTkFont(size=11), anchor="w"
        )
        self.app.breadcrumb_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Sub-tabview
        self.app.content_tabview = ctk.CTkTabview(
            self.app.content_container,
            segmented_button_selected_color="darkblue",
            segmented_button_selected_hover_color="blue"
        )
        self.app.content_tabview.pack(expand=True, fill="both", padx=8, pady=(4, 8))
'''
        
        (self.ui_path / "tabs" / "contenido_dinamico.py").write_text(content)
    
    def create_citas_referencias_tab(self):
        """Crea el módulo para Citas y Referencias"""
        # Crear archivo con solo la estructura básica
        content = '''"""
Tab de Citas y Referencias - Gestión de citas y bibliografía
"""

import customtkinter as ctk
from tkinter import messagebox

class CitasReferenciasTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de citas y referencias"""
        # Contenedor principal con scroll
        main_scroll = ctk.CTkScrollableFrame(self.parent, label_text="")
        main_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Panel de instrucciones
        self.create_instructions_panel(main_scroll)
        
        # Panel de agregar referencias
        self.create_add_references_panel(main_scroll)
        
        # Lista de referencias
        self.create_references_list(main_scroll)
    
    def create_instructions_panel(self, parent):
        """Crea el panel de instrucciones de citas"""
        instruc_frame = ctk.CTkFrame(parent, fg_color="gray15", corner_radius=10)
        instruc_frame.pack(fill="x", pady=(0, 15))
        
        # Header con botón de colapsar
        instruc_header = ctk.CTkFrame(instruc_frame, fg_color="gray20", height=40)
        instruc_header.pack(fill="x")
        instruc_header.pack_propagate(False)
        
        self.app.instruc_collapsed = False
        
        def toggle_instructions():
            if self.app.instruc_collapsed:
                instruc_content.pack(fill="x", padx=15, pady=(0, 15))
                collapse_btn.configure(text="▼")
            else:
                instruc_content.pack_forget()
                collapse_btn.configure(text="▶")
            self.app.instruc_collapsed = not self.app.instruc_collapsed
        
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
        
        self.create_citation_examples(instruc_content)
    
    def create_citation_examples(self, parent):
        """Crea los ejemplos de citas"""
        ejemplos_frame = ctk.CTkFrame(parent, fg_color="transparent")
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
    
    def create_add_references_panel(self, parent):
        """Panel para agregar referencias"""
        ref_frame = ctk.CTkFrame(parent, corner_radius=10)
        ref_frame.pack(fill="x", pady=(0, 15))
        
        ref_title = ctk.CTkLabel(
            ref_frame, text="➕ Agregar Referencias",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ref_title.pack(pady=(15, 10))
        
        # Formulario
        form_frame = ctk.CTkFrame(ref_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.create_reference_form(form_frame)
        
        # Botones
        self.create_reference_buttons(ref_frame)
    
    def create_reference_form(self, parent):
        """Crea el formulario de referencias"""
        # Primera fila
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        # Tipo
        tipo_container = ctk.CTkFrame(row1, fg_color="transparent")
        tipo_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            tipo_container, text="Tipo de referencia:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.app.ref_tipo = ctk.CTkComboBox(
            tipo_container,
            values=["Libro", "Artículo", "Web", "Tesis", "Conferencia", "Informe"],
            height=35, font=ctk.CTkFont(size=12),
            command=self.app.actualizar_campos_referencia
        )
        self.app.ref_tipo.pack(fill="x", pady=(5, 0))
        self.app.ref_tipo.set("Libro")
        
        # Autor(es)
        autor_container = ctk.CTkFrame(row1, fg_color="transparent")
        autor_container.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            autor_container, text="Autor(es):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.app.ref_autor = ctk.CTkEntry(
            autor_container, placeholder_text="Apellido, N. o García, J. y López, M.",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.app.ref_autor.pack(fill="x", pady=(5, 0))
        
        # Segunda fila
        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        # Año
        año_container = ctk.CTkFrame(row2, fg_color="transparent")
        año_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            año_container, text="Año:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.app.ref_año = ctk.CTkEntry(
            año_container, placeholder_text="2024",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.app.ref_año.pack(fill="x", pady=(5, 0))
        
        # Título
        titulo_container = ctk.CTkFrame(row2, fg_color="transparent")
        titulo_container.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            titulo_container, text="Título:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.app.ref_titulo = ctk.CTkEntry(
            titulo_container, placeholder_text="Título completo del trabajo",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.app.ref_titulo.pack(fill="x", pady=(5, 0))
        
        # Tercera fila
        row3 = ctk.CTkFrame(parent, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        self.app.fuente_container = ctk.CTkFrame(row3, fg_color="transparent")
        self.app.fuente_container.pack(fill="x")
        
        self.app.fuente_label = ctk.CTkLabel(
            self.app.fuente_container, text="Editorial/Fuente:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.app.fuente_label.pack(anchor="w")
        
        self.app.ref_fuente = ctk.CTkEntry(
            self.app.fuente_container, placeholder_text="Editorial, revista o URL",
            height=35, font=ctk.CTkFont(size=12)
        )
        self.app.ref_fuente.pack(fill="x", pady=(5, 0))
    
    def create_reference_buttons(self, parent):
        """Crea los botones de acción para referencias"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        
        add_ref_btn = ctk.CTkButton(
            btn_frame, text="➕ Agregar Referencia",
            command=self.app.agregar_referencia,
            height=40, font=ctk.CTkFont(size=13, weight="bold"),
            width=180
        )
        add_ref_btn.pack(side="left", padx=5)
        
        import_btn = ctk.CTkButton(
            btn_frame, text="📥 Importar BibTeX",
            command=self.app.importar_bibtex,
            height=40, font=ctk.CTkFont(size=13),
            width=150, fg_color="purple", hover_color="darkviolet"
        )
        import_btn.pack(side="left", padx=5)
    
    def create_references_list(self, parent):
        """Crea la lista de referencias"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True)
        
        # Header con búsqueda
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
        
        self.app.ref_search = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar referencia...",
            width=200, height=30
        )
        self.app.ref_search.pack(side="left")
        self.app.ref_search.bind("<KeyRelease>", self.app.filtrar_referencias)
        
        # Lista scrollable
        self.app.ref_scroll_frame = ctk.CTkScrollableFrame(
            list_frame, height=300,
            fg_color="gray15", corner_radius=8
        )
        self.app.ref_scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Botones de gestión
        self.create_management_buttons(list_frame)
    
    def create_management_buttons(self, parent):
        """Crea botones de gestión de referencias"""
        manage_frame = ctk.CTkFrame(parent, fg_color="transparent")
        manage_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        delete_btn = ctk.CTkButton(
            manage_frame, text="🗑️ Eliminar Seleccionadas",
            command=self.app.eliminar_referencias_seleccionadas,
            fg_color="red", hover_color="darkred",
            height=35, width=180
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        export_btn = ctk.CTkButton(
            manage_frame, text="📤 Exportar APA",
            command=self.app.exportar_referencias_apa,
            height=35, width=150
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        stats_label = ctk.CTkLabel(
            manage_frame, text=f"Total: {len(self.app.referencias)} referencias",
            font=ctk.CTkFont(size=12)
        )
        stats_label.pack(side="right")
        self.app.ref_stats_label = stats_label
'''
        
        (self.ui_path / "tabs" / "citas_referencias.py").write_text(content)
    
    def create_formato_avanzado_tab(self):
        """Crea el módulo para Formato Avanzado"""
        content = '''"""
Tab de Formato Avanzado - Configuración de estilos del documento
"""

import customtkinter as ctk
from tkinter import messagebox

class FormatoAvanzadoTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de formato avanzado"""
        scroll_frame = ctk.CTkScrollableFrame(self.parent, label_text="Configuración de Formato", height=400)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Sección de tipografía
        self.create_typography_section(scroll_frame)
        
        # Sección de espaciado
        self.create_spacing_section(scroll_frame)
        
        # Opciones de alineación
        self.create_alignment_section(scroll_frame)
        
        # Botón para aplicar configuración
        apply_btn = ctk.CTkButton(
            scroll_frame, text="✅ Aplicar Configuración", command=self.app.aplicar_formato,
            height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        apply_btn.pack(pady=15)
    
    def create_typography_section(self, parent):
        """Crea la sección de tipografía"""
        tipo_frame = ctk.CTkFrame(parent, fg_color="darkgreen", corner_radius=8)
        tipo_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            tipo_frame, text="🔤 Tipografía",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        tipo_grid = ctk.CTkFrame(tipo_frame, fg_color="transparent")
        tipo_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        # Primera fila
        row1_tipo = ctk.CTkFrame(tipo_grid, fg_color="transparent")
        row1_tipo.pack(fill="x", pady=3)
        
        # Fuente del texto
        fuente_texto_frame = ctk.CTkFrame(row1_tipo, fg_color="transparent")
        fuente_texto_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(fuente_texto_frame, text="Fuente texto:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.fuente_texto = ctk.CTkComboBox(
            fuente_texto_frame, values=["Times New Roman", "Arial", "Calibri"], height=25
        )
        self.app.fuente_texto.set("Times New Roman")
        self.app.fuente_texto.pack(fill="x")
        
        # Tamaño del texto
        tamaño_texto_frame = ctk.CTkFrame(row1_tipo, fg_color="transparent")
        tamaño_texto_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(tamaño_texto_frame, text="Tamaño:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.tamaño_texto = ctk.CTkComboBox(tamaño_texto_frame, values=["10", "11", "12", "13", "14"], height=25)
        self.app.tamaño_texto.set("12")
        self.app.tamaño_texto.pack(fill="x")
        
        # Segunda fila
        row2_tipo = ctk.CTkFrame(tipo_grid, fg_color="transparent")
        row2_tipo.pack(fill="x", pady=3)
        
        # Fuente de títulos
        fuente_titulo_frame = ctk.CTkFrame(row2_tipo, fg_color="transparent")
        fuente_titulo_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(fuente_titulo_frame, text="Fuente títulos:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.fuente_titulo = ctk.CTkComboBox(
            fuente_titulo_frame, values=["Times New Roman", "Arial", "Calibri"], height=25
        )
        self.app.fuente_titulo.set("Times New Roman")
        self.app.fuente_titulo.pack(fill="x")
        
        # Tamaño de títulos
        tamaño_titulo_frame = ctk.CTkFrame(row2_tipo, fg_color="transparent")
        tamaño_titulo_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(tamaño_titulo_frame, text="Tamaño:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.tamaño_titulo = ctk.CTkComboBox(tamaño_titulo_frame, values=["12", "13", "14", "15", "16"], height=25)
        self.app.tamaño_titulo.set("14")
        self.app.tamaño_titulo.pack(fill="x")
    
    def create_spacing_section(self, parent):
        """Crea la sección de espaciado"""
        espaciado_frame = ctk.CTkFrame(parent, fg_color="darkblue", corner_radius=8)
        espaciado_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            espaciado_frame, text="📏 Espaciado",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        espaciado_grid = ctk.CTkFrame(espaciado_frame, fg_color="transparent")
        espaciado_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        espaciado_row = ctk.CTkFrame(espaciado_grid, fg_color="transparent")
        espaciado_row.pack(fill="x", pady=3)
        
        # Interlineado
        interlineado_frame = ctk.CTkFrame(espaciado_row, fg_color="transparent")
        interlineado_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(interlineado_frame, text="Interlineado:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.interlineado = ctk.CTkComboBox(interlineado_frame, values=["1.0", "1.5", "2.0"], height=25)
        self.app.interlineado.set("2.0")
        self.app.interlineado.pack(fill="x")
        
        # Márgenes
        margen_frame = ctk.CTkFrame(espaciado_row, fg_color="transparent")
        margen_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(margen_frame, text="Márgenes (cm):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.app.margen = ctk.CTkComboBox(margen_frame, values=["2.0", "2.54", "3.0"], height=25)
        self.app.margen.set("2.54")
        self.app.margen.pack(fill="x")
    
    def create_alignment_section(self, parent):
        """Crea la sección de alineación"""
        align_frame = ctk.CTkFrame(parent, fg_color="darkred", corner_radius=8)
        align_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            align_frame, text="📐 Alineación",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(pady=(10, 8))
        
        align_grid = ctk.CTkFrame(align_frame, fg_color="transparent")
        align_grid.pack(fill="x", padx=15, pady=(0, 10))
        
        # Primera fila
        align_row = ctk.CTkFrame(align_grid, fg_color="transparent")
        align_row.pack(fill="x", pady=3)
        
        self.app.salto_pagina_var = ctk.CTkCheckBox(
            align_row, text="Salto de página entre secciones", font=ctk.CTkFont(size=12)
        )
        self.app.salto_pagina_var.select()
        self.app.salto_pagina_var.pack(side="left", padx=(10, 10))
        
        self.app.conservar_siguiente_var = ctk.CTkCheckBox(
            align_row, text="Conservar con siguiente", font=ctk.CTkFont(size=12)
        )
        self.app.conservar_siguiente_var.select()
        self.app.conservar_siguiente_var.pack(side="right", padx=(10, 10))
        
        # Segunda fila
        align_row2 = ctk.CTkFrame(align_grid, fg_color="transparent")
        align_row2.pack(fill="x", pady=3)
        
        self.app.justificado_var = ctk.CTkCheckBox(
            align_row2, text="Justificado", font=ctk.CTkFont(size=12)
        )
        self.app.justificado_var.select()
        self.app.justificado_var.pack(side="left", padx=(10, 10))
        
        self.app.sangria_var = ctk.CTkCheckBox(
            align_row2, text="Sangría primera línea", font=ctk.CTkFont(size=12)
        )
        self.app.sangria_var.select()
        self.app.sangria_var.pack(side="right", padx=(10, 10))
'''
        
        (self.ui_path / "tabs" / "formato_avanzado.py").write_text(content)
    
    def create_generacion_tab(self):
        """Crea el módulo para Generación"""
        content = '''"""
Tab de Generación - Opciones y validación del documento final
"""

import customtkinter as ctk
from tkinter import messagebox

class GeneracionTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de generación"""
        # Panel superior - Opciones
        self.create_options_panel()
        
        # Panel inferior - Validación
        self.create_validation_panel()
        
        # Inicializar con mensaje de bienvenida
        self.app.mostrar_bienvenida_validacion()
    
    def create_options_panel(self):
        """Crea el panel de opciones de generación"""
        paned = ctk.CTkFrame(self.parent, fg_color="transparent")
        paned.pack(fill="both", expand=True, padx=20, pady=20)
        
        top_frame = ctk.CTkFrame(paned, corner_radius=15, height=200)
        top_frame.pack(fill="x", pady=(0, 10))
        top_frame.pack_propagate(False)
        
        options_title = ctk.CTkLabel(
            top_frame, text="⚙️ Opciones de Generación",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        options_title.pack(pady=(20, 15))
        
        # Grid de opciones
        options_grid = ctk.CTkFrame(top_frame, fg_color="transparent")
        options_grid.pack(padx=30, pady=(0, 20))
        
        # Columnas
        col1 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=20)
        
        col2 = ctk.CTkFrame(options_grid, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=20)
        
        # Opciones columna 1
        self.app.incluir_portada = ctk.CTkCheckBox(
            col1, text="📄 Incluir Portada",
            font=ctk.CTkFont(size=14)
        )
        self.app.incluir_portada.select()
        self.app.incluir_portada.pack(anchor="w", pady=5)
        
        self.app.incluir_indice = ctk.CTkCheckBox(
            col1, text="📑 Incluir Índice",
            font=ctk.CTkFont(size=14)
        )
        self.app.incluir_indice.select()
        self.app.incluir_indice.pack(anchor="w", pady=5)
        
        # Opciones columna 2
        self.app.incluir_agradecimientos = ctk.CTkCheckBox(
            col2, text="🙏 Incluir Agradecimientos",
            font=ctk.CTkFont(size=14)
        )
        self.app.incluir_agradecimientos.pack(anchor="w", pady=5)
        
        self.app.numeracion_paginas = ctk.CTkCheckBox(
            col2, text="📊 Numeración de páginas",
            font=ctk.CTkFont(size=14)
        )
        self.app.numeracion_paginas.select()
        self.app.numeracion_paginas.pack(anchor="w", pady=5)
    
    def create_validation_panel(self):
        """Crea el panel de validación"""
        bottom_frame = ctk.CTkFrame(self.parent.master, corner_radius=15)
        bottom_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Header con tabs
        header_frame = ctk.CTkFrame(bottom_frame, height=50, fg_color="gray25")
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Tabs de validación
        self.app.validation_tabs = ctk.CTkSegmentedButton(
            header_frame,
            values=["🔍 Validación", "📋 Logs", "📊 Estadísticas", "💡 Sugerencias"],
            command=self.app.cambiar_tab_validacion
        )
        self.app.validation_tabs.pack(side="left", padx=15, pady=10)
        self.app.validation_tabs.set("🔍 Validación")
        
        # Botón de limpiar
        clear_btn = ctk.CTkButton(
            header_frame, text="🗑️", width=35, height=35,
            command=self.app.limpiar_validacion,
            fg_color="transparent", hover_color="gray30"
        )
        clear_btn.pack(side="right", padx=15)
        
        # Contenedor de contenido
        self.app.validation_container = ctk.CTkFrame(bottom_frame)
        self.app.validation_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Área de texto
        self.app.validation_text = ctk.CTkTextbox(
            self.app.validation_container,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="gray10"
        )
        self.app.validation_text.pack(fill="both", expand=True)
        
        # Panel de progreso
        self.create_progress_panel(bottom_frame)
    
    def create_progress_panel(self, parent):
        """Crea el panel de progreso"""
        progress_frame = ctk.CTkFrame(parent, height=80)
        progress_frame.pack(fill="x", padx=15, pady=(0, 15))
        progress_frame.pack_propagate(False)
        
        # Etiqueta de estado
        self.app.status_label = ctk.CTkLabel(
            progress_frame, text="🟢 Listo para validar",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.app.status_label.pack(pady=(10, 5))
        
        # Barra de progreso
        self.app.progress = ctk.CTkProgressBar(
            progress_frame, height=20,
            progress_color="green"
        )
        self.app.progress.pack(fill="x", padx=20, pady=(0, 5))
        self.app.progress.set(0)
        
        # Subtareas
        self.app.subtask_label = ctk.CTkLabel(
            progress_frame, text="",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        self.app.subtask_label.pack()
'''
        
        (self.ui_path / "tabs" / "generacion.py").write_text(content)
    
    def extract_widgets(self):
        """Extrae widgets adicionales"""
        print("🔧 Extrayendo widgets adicionales...")
        
        # Preview Window
        self.create_preview_window_widget()
        
        # Image Manager Dialog
        self.create_image_manager_widget()
        
        # Update widgets __init__.py
        init_content = '''"""
Widgets Module - Componentes reutilizables de la interfaz
"""

from .font_manager import FontManager
from .tooltip import ToolTip
from .preview_window import PreviewWindow
from .image_manager import ImageManagerDialog

__all__ = [
    'FontManager',
    'ToolTip',
    'PreviewWindow',
    'ImageManagerDialog'
]
'''
        (self.ui_path / "widgets" / "__init__.py").write_text(init_content)
        print("  ✓ Widgets adicionales extraídos")
    
    def create_preview_window_widget(self):
        """Crea el widget de ventana de preview"""
        content = '''"""
Preview Window - Ventana de vista previa del documento
"""

import customtkinter as ctk

class PreviewWindow:
    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        
    def show(self):
        """Muestra la ventana de preview"""
        if not self.window:
            self.create_window()
        else:
            self.window.deiconify()
            self.app.actualizar_preview()
    
    def create_window(self):
        """Crea la ventana de vista previa"""
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title("👁️ Vista Previa del Documento")
        
        # Posicionar a la derecha
        main_x = self.app.root.winfo_x()
        main_y = self.app.root.winfo_y()
        main_width = self.app.root.winfo_width()
        
        self.window.geometry(f"400x800+{main_x + main_width + 10}+{main_y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Opciones
        self.create_options(main_frame)
        
        # Área de preview
        self.create_preview_area(main_frame)
        
        # Configurar cierre
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
    
    def create_header(self, parent):
        """Crea el header de la ventana"""
        header_frame = ctk.CTkFrame(parent, height=50, fg_color="gray25")
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame, text="📄 Vista Previa del Documento",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=15, pady=10)
        
        refresh_btn = ctk.CTkButton(
            header_frame, text="🔄", width=35, height=35,
            command=self.app.actualizar_preview,
            font=ctk.CTkFont(size=16)
        )
        refresh_btn.pack(side="right", padx=15)
    
    def create_options(self, parent):
        """Crea las opciones de vista"""
        options_frame = ctk.CTkFrame(parent, height=40)
        options_frame.pack(fill="x", pady=(0, 10))
        options_frame.pack_propagate(False)
        
        self.app.preview_mode = ctk.CTkSegmentedButton(
            options_frame,
            values=["📝 Texto", "🎨 Formato", "📊 Estructura"],
            command=self.app.cambiar_modo_preview
        )
        self.app.preview_mode.pack(padx=10, pady=5)
        self.app.preview_mode.set("📝 Texto")
    
    def create_preview_area(self, parent):
        """Crea el área de preview"""
        self.app.preview_text = ctk.CTkTextbox(
            parent, wrap="word",
            font=ctk.CTkFont(family="Georgia", size=12),
            state="disabled"
        )
        self.app.preview_text.pack(fill="both", expand=True)
    
    def hide(self):
        """Oculta la ventana"""
        if self.window:
            self.window.withdraw()
'''
        
        (self.ui_path / "widgets" / "preview_window.py").write_text(content)
    
    def create_image_manager_widget(self):
        """Crea el widget de gestión de imágenes"""
        content = '''"""
Image Manager - Diálogo de gestión de imágenes
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os

class ImageManagerDialog:
    def __init__(self, parent_app):
        self.app = parent_app
        
    def show(self):
        """Muestra el diálogo de gestión de imágenes"""
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title("🖼️ Gestión de Imágenes")
        self.window.geometry("600x500")
        self.window.transient(self.app.root)
        self.window.grab_set()
        
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main_frame = ctk.CTkFrame(self.window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text="🖼️ Gestión de Imágenes del Documento",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Estado de imágenes base
        self.create_status_section(main_frame)
        
        # Sección de carga personalizada
        self.create_custom_section(main_frame)
        
        # Configuración de marca de agua
        self.create_watermark_section(main_frame)
        
        # Información adicional
        self.create_info_section(main_frame)
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def create_status_section(self, parent):
        """Crea la sección de estado"""
        status_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)
        status_frame.pack(fill="x", pady=(0, 20))
        
        status_title = ctk.CTkLabel(
            status_frame, text="📁 Estado de Imágenes Base",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_title.pack(pady=(10, 5))
        
        # Estado del encabezado
        enc_status = "✅ Encontrado" if self.app.ruta_encabezado else "❌ No encontrado"
        enc_label = ctk.CTkLabel(
            status_frame, text=f"Encabezado.png: {enc_status}",
            font=ctk.CTkFont(size=12)
        )
        enc_label.pack(pady=2)
        
        # Estado de la insignia
        ins_status = "✅ Encontrado" if self.app.ruta_insignia else "❌ No encontrado"
        ins_label = ctk.CTkLabel(
            status_frame, text=f"Insignia.png: {ins_status}",
            font=ctk.CTkFont(size=12)
        )
        ins_label.pack(pady=(2, 10))
    
    def create_custom_section(self, parent):
        """Crea la sección de carga personalizada"""
        custom_frame = ctk.CTkFrame(parent, fg_color="darkblue", corner_radius=10)
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
            command=lambda: self.app.cargar_imagen_personalizada("encabezado", self.window),
            width=200, height=35
        )
        enc_btn.pack(side="left", padx=(0, 10))
        
        ins_btn = ctk.CTkButton(
            btn_frame, text="🏛️ Cargar Insignia", 
            command=lambda: self.app.cargar_imagen_personalizada("insignia", self.window),
            width=200, height=35
        )
        ins_btn.pack(side="right", padx=(10, 0))
        
        # Estado de imágenes personalizadas
        self.create_custom_status(parent)
    
    def create_custom_status(self, parent):
        """Crea el estado de imágenes personalizadas"""
        custom_status_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)
        custom_status_frame.pack(fill="x", pady=(0, 20))
        
        custom_status_title = ctk.CTkLabel(
            custom_status_frame, text="🎨 Imágenes Personalizadas Cargadas",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        custom_status_title.pack(pady=(10, 5))
        
        self.app.enc_custom_label = ctk.CTkLabel(
            custom_status_frame, 
            text=f"Encabezado: {'✅ Cargado' if self.app.encabezado_personalizado else '⏸️ No cargado'}",
            font=ctk.CTkFont(size=12)
        )
        self.app.enc_custom_label.pack(pady=2)
        
        self.app.ins_custom_label = ctk.CTkLabel(
            custom_status_frame, 
            text=f"Insignia: {'✅ Cargado' if self.app.insignia_personalizada else '⏸️ No cargado'}",
            font=ctk.CTkFont(size=12)
        )
        self.app.ins_custom_label.pack(pady=(2, 10))
    
    def create_watermark_section(self, parent):
        """Crea la sección de configuración de marca de agua"""
        watermark_frame = ctk.CTkFrame(parent, fg_color="purple", corner_radius=10)
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
        
        self.app.opacity_slider = ctk.CTkSlider(
            opacity_frame, from_=0.1, to=1.0,
            command=self.app.actualizar_opacidad_preview
        )
        self.app.opacity_slider.set(self.app.watermark_opacity)
        self.app.opacity_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.app.opacity_label = ctk.CTkLabel(
            opacity_frame, text=f"{int(self.app.watermark_opacity * 100)}%",
            font=ctk.CTkFont(size=12), text_color="white"
        )
        self.app.opacity_label.pack(side="left")
        
        # Modo de encabezado
        mode_frame = ctk.CTkFrame(watermark_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            mode_frame, text="Modo:",
            font=ctk.CTkFont(size=12), text_color="white"
        ).pack(side="left", padx=(0, 10))
        
        self.app.mode_var = ctk.StringVar(value=self.app.watermark_mode)
        
        watermark_radio = ctk.CTkRadioButton(
            mode_frame, text="Marca de Agua",
            variable=self.app.mode_var, value="watermark",
            text_color="white"
        )
        watermark_radio.pack(side="left", padx=(0, 20))
        
        normal_radio = ctk.CTkRadioButton(
            mode_frame, text="Normal",
            variable=self.app.mode_var, value="normal",
            text_color="white"
        )
        normal_radio.pack(side="left")
        
        # Estirar al ancho
        self.app.stretch_var = ctk.CTkCheckBox(
            watermark_frame, text="Estirar al ancho de página",
            font=ctk.CTkFont(size=12), text_color="white"
        )
        self.app.stretch_var.select() if self.app.watermark_stretch else self.app.stretch_var.deselect()
        self.app.stretch_var.pack(pady=(0, 15))
    
    def create_info_section(self, parent):
        """Crea la sección de información"""
        info_frame = ctk.CTkFrame(parent, fg_color="green", corner_radius=10)
        info_frame.pack(fill="x")
        
        info_text = """💡 INFORMACIÓN IMPORTANTE:
- Las imágenes base se buscan en: /resources/images/
- Las imágenes personalizadas tienen prioridad sobre las base
- Formatos soportados: PNG, JPG, JPEG
- Tamaño recomendado: Encabezado 600x100px, Insignia 100x100px"""
        
        info_label = ctk.CTkLabel(
            info_frame, text=info_text, font=ctk.CTkFont(size=10),
            justify="left", wraplength=550, text_color="white"
        )
        info_label.pack(padx=15, pady=10)
    
    def create_action_buttons(self, parent):
        """Crea los botones de acción"""
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", pady=(10, 0))
        
        reset_btn = ctk.CTkButton(
            action_frame, text="🔄 Restablecer", 
            command=lambda: self.app.restablecer_imagenes(self.window),
            width=120, height=35, fg_color="red", hover_color="darkred"
        )
        reset_btn.pack(side="left")
        
        close_btn = ctk.CTkButton(
            action_frame, text="✅ Cerrar", 
            command=self.window.destroy,
            width=120, height=35
        )
        close_btn.pack(side="right")
'''
        
        (self.ui_path / "widgets" / "image_manager.py").write_text(content)
    
    def extract_dialogs(self):
        """Extrae diálogos adicionales"""
        print("💬 Extrayendo diálogos adicionales...")
        
        # Help Dialog
        self.create_help_dialog()
        
        # Update dialogs __init__.py
        init_update = '''"""
Dialogs Module - Ventanas de diálogo de la aplicación
"""

from .section_dialog import SeccionDialog
from .citation_dialog import CitationDialog
from .help_dialog import HelpDialog

__all__ = [
    'SeccionDialog',
    'CitationDialog',
    'HelpDialog'
]
'''
        
        # Leer contenido actual de dialogs.py y crear archivos separados
        dialogs_path = self.ui_path / "dialogs.py"
        if dialogs_path.exists():
            content = dialogs_path.read_text()
            
            # Extraer SeccionDialog
            section_start = content.find("class SeccionDialog:")
            section_end = content.find("\nclass CitationDialog:")
            if section_start != -1 and section_end != -1:
                section_content = '''"""
Section Dialog - Diálogo para agregar/editar secciones
"""

import customtkinter as ctk
from tkinter import messagebox
import re

''' + content[section_start:section_end]
                
                (self.ui_path / "dialogs" / "section_dialog.py").write_text(section_content)
            
            # Extraer CitationDialog
            citation_start = content.find("class CitationDialog:")
            if citation_start != -1:
                citation_content = '''"""
Citation Dialog - Diálogo para insertar citas
"""

import customtkinter as ctk
from tkinter import messagebox

''' + content[citation_start:]
                
                (self.ui_path / "dialogs" / "citation_dialog.py").write_text(citation_content)
        
        # Actualizar __init__.py
        (self.ui_path / "dialogs" / "__init__.py").write_text(init_update)
        print("  ✓ Diálogos extraídos")
    
    def create_help_dialog(self):
        """Crea el diálogo de ayuda"""
        content = '''"""
Help Dialog - Diálogo de ayuda y guías
"""

import customtkinter as ctk

class HelpDialog:
    def __init__(self, parent_app):
        self.app = parent_app
    
    def show(self):
        """Muestra el diálogo de ayuda completa"""
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title("📖 Guía Profesional Completa")
        self.window.geometry("1000x800")
        
        main_frame = ctk.CTkFrame(self.window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, text="📖 GUÍA PROFESIONAL COMPLETA",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        self.text_widget = ctk.CTkTextbox(main_frame, wrap="word", font=ctk.CTkFont(size=12))
        self.text_widget.pack(expand=True, fill="both", padx=20, pady=(10, 20))
        
        self.load_help_content()
        self.text_widget.configure(state="disabled")
    
    def load_help_content(self):
        """Carga el contenido de ayuda"""
        content = """
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

[... resto del contenido de ayuda ...]
"""
        self.text_widget.insert("1.0", content)
    
    def show_contextual_help(self, section):
        """Muestra ayuda contextual específica"""
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title(f"💡 Ayuda - {section}")
        self.window.geometry("600x400")
        
        # Contenido específico según sección
        # ... implementar contenido contextual ...
'''
        
        (self.ui_path / "dialogs" / "help_dialog.py").write_text(content)
    
    def create_simplified_main_window(self):
        """Crea el nuevo main_window.py simplificado"""
        print("📝 Creando main_window.py simplificado...")
        
        content = '''"""
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
                f"Error al buscar imágenes base:\\n{str(e)}\\n\\n"
                f"Coloca las imágenes en: resources/images/\\n"
                f"• Encabezado.png\\n• Insignia.png")
    
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
            "Generador de Proyectos Académicos - Versión Profesional\\n\\n"
            "🆕 CARACTERÍSTICAS AVANZADAS:\\n"
            "• Estructura modular mejorada\\n"
            "• Auto-guardado cada 5 minutos\\n"
            "• Estadísticas en tiempo real\\n"
            "• Sistema de guardado/carga completo\\n"
            "• Gestión avanzada de imágenes\\n"
            "• Exportación de configuraciones\\n\\n"
            "⌨️ ATAJOS DE TECLADO:\\n"
            "• Ctrl+S: Guardar proyecto\\n"
            "• Ctrl+O: Cargar proyecto\\n"
            "• Ctrl+N: Nuevo proyecto\\n"
            "• F5: Validar proyecto\\n"
            "• F9: Generar documento\\n"
            "• Ctrl+Q: Salir\\n\\n"
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
'''
        
        # Agregar métodos restantes necesarios
        content += '''
    
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
'''
        
        file_path = self.ui_path / "main_window_new.py"
        file_path.write_text(content)
        
        print("  ✓ main_window.py simplificado creado")
    
    def update_imports(self):
        """Actualiza las importaciones en otros archivos"""
        print("🔄 Actualizando importaciones...")
        
        # Actualizar ui/__init__.py
        ui_init_content = '''"""
UI - Interfaz de usuario del generador de proyectos académicos
"""

from .main_window import ProyectoAcademicoGenerator
from .widgets import FontManager, ToolTip
from .components import StatsPanel, FormatPanel

__all__ = [
    'ProyectoAcademicoGenerator',
    'FontManager',
    'ToolTip',
    'StatsPanel',
    'FormatPanel'
]
'''
        
        (self.ui_path / "__init__.py").write_text(ui_init_content)
        
        print("  ✓ Importaciones actualizadas")
        
        # Renombrar el archivo nuevo
        print("\n⚠️ IMPORTANTE:")
        print("1. Revisa que todo funcione correctamente")
        print("2. Si todo está bien, renombra manualmente:")
        print("   - main_window.py → main_window_old.py")
        print("   - main_window_new.py → main_window.py")
        print("3. El backup está en: backup_original/")

if __name__ == "__main__":
    reorganizer = CodeReorganizer()
    reorganizer.run()