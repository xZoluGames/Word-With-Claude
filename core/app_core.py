"""
Clase principal del Generador de Proyectos Académicos - Núcleo simplificado
Maneja la coordinación general entre módulos
"""

import customtkinter as ctk
import os
import json
from datetime import datetime
from .config_manager import ConfigManager
from .document_generator import DocumentGenerator

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ProyectoAcademicoGenerator:
    """Clase principal del generador - Solo coordinación central"""
    
    def __init__(self):
        # Configuración básica
        self.root = ctk.CTk()
        self.root.title("🎓 Generador de Proyectos Académicos - Versión Modular")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Inicializar managers
        self.config_manager = ConfigManager(self)
        self.document_generator = DocumentGenerator(self)
        
        # Variables de datos del proyecto
        self.proyecto_data = {}
        self.referencias = []
        self.content_texts = {}
        
        # Variables de configuración
        self.formato_config = self.config_manager.get_default_format_config()
        self.secciones_disponibles = self.config_manager.get_default_sections()
        self.secciones_activas = list(self.secciones_disponibles.keys())
        
        # Variables de imágenes
        self.ruta_encabezado = None
        self.ruta_insignia = None
        self.encabezado_personalizado = None
        self.insignia_personalizada = None
        
        # Variables de estado
        self.stats = {
            'total_words': 0, 
            'total_chars': 0, 
            'sections_completed': 0, 
            'references_added': 0
        }
        self.last_save_time = None
        self.auto_save_enabled = True
        self.usar_formato_base = False
        self.documento_base = None
        
        # Inicializar componentes
        self.buscar_imagenes_base()
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        self.inicializar_estadisticas()
        
        # Mostrar mensaje de bienvenida
        self.mostrar_bienvenida()
    
    def buscar_imagenes_base(self):
        """Busca las imágenes base en la carpeta Recursos"""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        recursos_dir = os.path.join(script_dir, "resources", "images")
        
        encabezado_path = os.path.join(recursos_dir, "Encabezado.png")
        insignia_path = os.path.join(recursos_dir, "Insignia.png")
        
        self.ruta_encabezado = encabezado_path if os.path.exists(encabezado_path) else None
        self.ruta_insignia = insignia_path if os.path.exists(insignia_path) else None
    
    def setup_ui(self):
        """Configura la interfaz de usuario básica"""
        # Este será el núcleo mínimo, la UI detallada irá en ui/main_window.py
        
        # Frame principal
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header básico
        self.setup_header(main_container)
        
        # Contenido principal
        self.setup_main_content(main_container)
        
        # Status bar
        self.setup_status_bar(main_container)
    
    def setup_header(self, parent):
        """Configura el header básico"""
        header_frame = ctk.CTkFrame(parent, height=80, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎓 Generador de Proyectos Académicos - Versión Modular",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Botones principales (versión simplificada)
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Solo botones esenciales por ahora
        save_btn = ctk.CTkButton(
            button_frame, text="💾 Guardar", command=self.guardar_proyecto,
            width=80, height=30
        )
        save_btn.pack(side="left", padx=(0, 5))
        
        load_btn = ctk.CTkButton(
            button_frame, text="📂 Cargar", command=self.cargar_proyecto,
            width=80, height=30
        )
        load_btn.pack(side="left", padx=(0, 5))
        
        validate_btn = ctk.CTkButton(
            button_frame, text="🔍 Validar", command=self.validar_proyecto,
            width=80, height=30
        )
        validate_btn.pack(side="left", padx=(0, 5))
        
        generate_btn = ctk.CTkButton(
            button_frame, text="📄 Generar", command=self.generar_documento,
            width=100, height=30, fg_color="green", hover_color="darkgreen"
        )
        generate_btn.pack(side="right")
    
    def setup_main_content(self, parent):
        """Configura el contenido principal básico"""
        content_frame = ctk.CTkFrame(parent, corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(5, 5))
        
        # Tabview simple por ahora
        self.tabview = ctk.CTkTabview(content_frame)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Pestañas básicas
        self.setup_basic_tabs()
    
    def setup_basic_tabs(self):
        """Configura pestañas básicas temporalmente"""
        # Información General
        info_tab = self.tabview.add("📋 Información")
        info_label = ctk.CTkLabel(
            info_tab, 
            text="Información General del Proyecto\n(UI completa se cargará desde ui/main_window.py)",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(expand=True)
        
        # Contenido
        content_tab = self.tabview.add("📝 Contenido")
        content_label = ctk.CTkLabel(
            content_tab, 
            text="Gestión de Contenido\n(Funcionalidad completa en desarrollo)",
            font=ctk.CTkFont(size=14)
        )
        content_label.pack(expand=True)
        
        # Estado
        status_tab = self.tabview.add("📊 Estado")
        self.status_text = ctk.CTkTextbox(status_tab, height=200)
        self.status_text.pack(fill="both", expand=True, padx=20, pady=20)
        self.status_text.insert("1.0", 
            "🎯 PROYECTO MODULAR INICIADO\n\n"
            "✅ Núcleo cargado correctamente\n"
            "✅ ConfigManager inicializado\n"
            "✅ DocumentGenerator preparado\n"
            "⏳ Módulos UI en desarrollo\n\n"
            "📁 Estructura modular activa\n"
            "🔄 Sistema de auto-guardado preparado\n"
        )
    
    def setup_status_bar(self, parent):
        """Configura barra de estado"""
        status_frame = ctk.CTkFrame(parent, height=30, corner_radius=5)
        status_frame.pack(fill="x", padx=10, pady=(5, 10))
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="📊 Sistema modular iniciado | Referencias: 0 | Auto-guardado: Activo",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(pady=5)
    
    def setup_keyboard_shortcuts(self):
        """Configura atajos de teclado"""
        self.root.bind('<Control-s>', lambda e: self.guardar_proyecto())
        self.root.bind('<Control-o>', lambda e: self.cargar_proyecto())
        self.root.bind('<Control-n>', lambda e: self.nuevo_proyecto())
        self.root.bind('<F5>', lambda e: self.validar_proyecto())
        self.root.bind('<F9>', lambda e: self.generar_documento())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
    
    def inicializar_estadisticas(self):
        """Inicializa el sistema de estadísticas"""
        self.actualizar_estadisticas()
        if self.auto_save_enabled:
            self.auto_save_project()
    
    def actualizar_estadisticas(self):
        """Actualiza estadísticas en tiempo real"""
        # Lógica básica - será expandida en módulos específicos
        self.status_label.configure(
            text=f"📊 Referencias: {len(self.referencias)} | "
                 f"Secciones: {len(self.secciones_activas)} | "
                 f"Auto-guardado: {'Activo' if self.auto_save_enabled else 'Inactivo'}"
        )
        # Programar próxima actualización
        self.root.after(5000, self.actualizar_estadisticas)
    
    def auto_save_project(self):
        """Sistema de auto-guardado"""
        if self.auto_save_enabled:
            try:
                self.config_manager.auto_save(self.get_project_data())
                print(f"Auto-guardado: {datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"Error en auto-guardado: {e}")
            
            # Programar próximo auto-guardado (5 minutos)
            self.root.after(300000, self.auto_save_project)
    
    def get_project_data(self):
        """Obtiene todos los datos del proyecto para guardado"""
        return {
            'version': '2.0',
            'fecha_guardado': datetime.now().isoformat(),
            'proyecto_data': {k: v.get() if hasattr(v, 'get') else str(v) 
                            for k, v in self.proyecto_data.items()},
            'referencias': self.referencias,
            'secciones_activas': self.secciones_activas,
            'secciones_disponibles': self.secciones_disponibles,
            'formato_config': self.formato_config,
            'stats': self.stats
        }
    
    def load_project_data(self, data):
        """Carga datos del proyecto"""
        if 'referencias' in data:
            self.referencias = data['referencias']
        if 'secciones_activas' in data:
            self.secciones_activas = data['secciones_activas']
        if 'formato_config' in data:
            self.formato_config.update(data['formato_config'])
        # Más lógica de carga será implementada en módulos específicos
    
    # Métodos principales - implementación básica
    def guardar_proyecto(self):
        """Guarda proyecto completo"""
        try:
            data = self.get_project_data()
            self.config_manager.save_project(data)
            self.actualizar_status("💾 Proyecto guardado correctamente")
        except Exception as e:
            self.actualizar_status(f"❌ Error al guardar: {str(e)}")
    
    def cargar_proyecto(self):
        """Carga proyecto desde archivo"""
        try:
            data = self.config_manager.load_project()
            if data:
                self.load_project_data(data)
                self.actualizar_status("📂 Proyecto cargado correctamente")
        except Exception as e:
            self.actualizar_status(f"❌ Error al cargar: {str(e)}")
    
    def nuevo_proyecto(self):
        """Crea nuevo proyecto"""
        # Reiniciar variables
        self.referencias = []
        self.proyecto_data = {}
        self.content_texts = {}
        self.secciones_activas = list(self.secciones_disponibles.keys())
        self.actualizar_status("🆕 Nuevo proyecto creado")
    
    def validar_proyecto(self):
        """Validación básica del proyecto"""
        errores = []
        advertencias = []
        
        # Validaciones básicas
        if not self.referencias:
            advertencias.append("⚠️ Sin referencias bibliográficas")
        
        if len(self.secciones_activas) < 5:
            advertencias.append("⚠️ Pocas secciones activas")
        
        # Mostrar resultados en status
        if not errores and not advertencias:
            resultado = "✅ Proyecto válido y completo"
        elif not errores:
            resultado = f"✅ Proyecto válido | {len(advertencias)} advertencias"
        else:
            resultado = f"❌ {len(errores)} errores encontrados"
        
        self.actualizar_status(resultado)
        
        # Actualizar en status text si existe
        if hasattr(self, 'status_text'):
            validation_result = f"🔍 VALIDACIÓN - {datetime.now().strftime('%H:%M:%S')}\n"
            validation_result += f"Errores: {len(errores)} | Advertencias: {len(advertencias)}\n"
            validation_result += f"Estado: {resultado}\n" + "-"*50 + "\n"
            
            current_content = self.status_text.get("1.0", "end")
            self.status_text.delete("1.0", "end")
            self.status_text.insert("1.0", validation_result + current_content)
    
    def generar_documento(self):
        """Genera documento usando DocumentGenerator"""
        try:
            self.actualizar_status("📄 Generando documento...")
            success = self.document_generator.generate_document(self.get_project_data())
            if success:
                self.actualizar_status("✅ Documento generado exitosamente")
            else:
                self.actualizar_status("❌ Error al generar documento")
        except Exception as e:
            self.actualizar_status(f"❌ Error: {str(e)}")
    
    def actualizar_status(self, mensaje):
        """Actualiza mensaje de estado"""
        if hasattr(self, 'status_label'):
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.status_label.configure(text=f"[{timestamp}] {mensaje}")
    
    def mostrar_bienvenida(self):
        """Muestra mensaje de bienvenida modular"""
        self.root.after(1000, lambda: self.actualizar_status(
            "🎓 Sistema modular iniciado - Listo para crear proyectos profesionales"
        ))
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error en ejecución: {e}")
        finally:
            # Guardar automáticamente al cerrar
            if self.auto_save_enabled:
                try:
                    self.config_manager.auto_save(self.get_project_data())
                except:
                    pass