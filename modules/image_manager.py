"""
Gestor de imágenes para el Generador de Proyectos Académicos
Maneja carga, validación y gestión de imágenes personalizadas y base
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

class ImageManager:
    """Gestiona todas las operaciones relacionadas con imágenes"""
    
    def __init__(self, app):
        self.app = app
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Configuraciones recomendadas
        self.recommended_sizes = {
            'encabezado': {'width': 600, 'height': 100, 'max_width': 800, 'max_height': 150},
            'insignia': {'width': 100, 'height': 100, 'max_width': 200, 'max_height': 200}
        }
    
    def buscar_imagenes_base(self):
        """Busca las imágenes base en resources/images"""
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            recursos_dir = os.path.join(script_dir, "resources", "images")
            
            # Crear directorio si no existe
            os.makedirs(recursos_dir, exist_ok=True)
            
            # Buscar imágenes
            encabezado_path = os.path.join(recursos_dir, "Encabezado.png")
            insignia_path = os.path.join(recursos_dir, "Insignia.png")
            
            # Validar que existan y sean válidas
            self.app.ruta_encabezado = encabezado_path if self.validar_imagen(encabezado_path) else None
            self.app.ruta_insignia = insignia_path if self.validar_imagen(insignia_path) else None
            
            return {
                'encabezado_encontrado': self.app.ruta_encabezado is not None,
                'insignia_encontrada': self.app.ruta_insignia is not None,
                'directorio': recursos_dir
            }
            
        except Exception as e:
            print(f"Error buscando imágenes base: {e}")
            return {'encabezado_encontrado': False, 'insignia_encontrada': False, 'directorio': None}
    
    def validar_imagen(self, ruta):
        """Valida que una imagen sea válida y del formato correcto"""
        if not os.path.exists(ruta):
            return False
        
        try:
            # Verificar extensión
            _, ext = os.path.splitext(ruta.lower())
            if ext not in self.supported_formats:
                return False
            
            # Verificar tamaño de archivo
            if os.path.getsize(ruta) > self.max_file_size:
                return False
            
            # Verificar que se pueda abrir como imagen
            with Image.open(ruta) as img:
                # Verificar dimensiones mínimas
                if img.width < 50 or img.height < 50:
                    return False
                return True
                
        except Exception:
            return False
    
    def cargar_imagen_personalizada(self, tipo, parent_window=None):
        """Carga una imagen personalizada para encabezado o insignia"""
        try:
            filetypes = [
                ("Todas las imágenes", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG files", "*.png"),
                ("JPG files", "*.jpg *.jpeg"),
                ("BMP files", "*.bmp"),
                ("GIF files", "*.gif")
            ]
            
            filename = filedialog.askopenfilename(
                title=f"Seleccionar {tipo.capitalize()}",
                filetypes=filetypes,
                parent=parent_window
            )
            
            if not filename:
                return None
            
            # Validar imagen
            if not self.validar_imagen(filename):
                messagebox.showerror(
                    "❌ Imagen Inválida", 
                    "La imagen seleccionada no es válida o no cumple con los requisitos:\n"
                    f"• Formatos soportados: {', '.join(self.supported_formats)}\n"
                    f"• Tamaño máximo: {self.max_file_size // (1024*1024)}MB\n"
                    "• Dimensiones mínimas: 50x50px"
                )
                return None
            
            # Verificar dimensiones y mostrar información
            info_resultado = self.analizar_imagen(filename, tipo)
            
            if info_resultado['mostrar_advertencia']:
                respuesta = messagebox.askyesno(
                    "⚠️ Dimensiones no Óptimas",
                    info_resultado['mensaje_advertencia'] + "\n\n¿Continuar de todas formas?"
                )
                if not respuesta:
                    return None
            
            # Guardar referencia
            if tipo == "encabezado":
                self.app.encabezado_personalizado = filename
            elif tipo == "insignia":
                self.app.insignia_personalizada = filename
            
            # Mostrar información de éxito
            messagebox.showinfo(
                "✅ Imagen Cargada", 
                f"{tipo.capitalize()} cargado correctamente.\n\n"
                f"📊 Información:\n"
                f"• Tamaño: {info_resultado['width']}x{info_resultado['height']} píxeles\n"
                f"• Archivo: {os.path.basename(filename)}\n"
                f"• Formato: {info_resultado['format']}\n"
                f"• Tamaño: {info_resultado['file_size_mb']:.1f} MB"
            )
            
            return filename
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar imagen:\n{str(e)}")
            return None
    
    def analizar_imagen(self, ruta, tipo):
        """Analiza una imagen y proporciona información detallada"""
        try:
            with Image.open(ruta) as img:
                width, height = img.size
                format_img = img.format
                file_size = os.path.getsize(ruta)
                file_size_mb = file_size / (1024 * 1024)
                
                # Obtener configuración recomendada para el tipo
                recomendado = self.recommended_sizes.get(tipo, {})
                
                # Verificar si está dentro de rangos óptimos
                mostrar_advertencia = False
                mensaje_advertencia = ""
                
                if recomendado:
                    max_w = recomendado.get('max_width', float('inf'))
                    max_h = recomendado.get('max_height', float('inf'))
                    rec_w = recomendado.get('width', 0)
                    rec_h = recomendado.get('height', 0)
                    
                    if width > max_w or height > max_h:
                        mostrar_advertencia = True
                        mensaje_advertencia = f"La imagen es muy grande.\n" \
                                            f"Tamaño actual: {width}x{height}px\n" \
                                            f"Máximo recomendado: {max_w}x{max_h}px"
                    
                    elif abs(width - rec_w) > rec_w * 0.5 or abs(height - rec_h) > rec_h * 0.5:
                        mostrar_advertencia = True
                        mensaje_advertencia = f"Las dimensiones no son óptimas.\n" \
                                            f"Tamaño actual: {width}x{height}px\n" \
                                            f"Recomendado: {rec_w}x{rec_h}px"
                
                return {
                    'width': width,
                    'height': height,
                    'format': format_img,
                    'file_size_mb': file_size_mb,
                    'mostrar_advertencia': mostrar_advertencia,
                    'mensaje_advertencia': mensaje_advertencia,
                    'es_optima': not mostrar_advertencia
                }
                
        except Exception as e:
            return {
                'width': 0, 'height': 0, 'format': 'Unknown', 'file_size_mb': 0,
                'mostrar_advertencia': True,
                'mensaje_advertencia': f"Error analizando imagen: {str(e)}",
                'es_optima': False
            }
    
    def gestionar_imagenes(self, parent_window):
        """Abre ventana principal de gestión de imágenes"""
        img_window = ctk.CTkToplevel(parent_window)
        img_window.title("🖼️ Gestión de Imágenes")
        img_window.geometry("700x600")
        img_window.transient(parent_window)
        img_window.grab_set()
        
        # Centrar ventana
        self.centrar_ventana(img_window, 700, 600)
        
        # Crear interfaz
        self.crear_interfaz_gestion(img_window)
    
    def centrar_ventana(self, ventana, ancho, alto):
        """Centra una ventana en la pantalla"""
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def crear_interfaz_gestion(self, window):
        """Crea la interfaz de gestión de imágenes"""
        main_frame = ctk.CTkFrame(window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título principal
        title_label = ctk.CTkLabel(
            main_frame, text="🖼️ Gestión Avanzada de Imágenes",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Estado de imágenes base
        self.crear_seccion_imagenes_base(main_frame)
        
        # Gestión de imágenes personalizadas
        self.crear_seccion_imagenes_personalizadas(main_frame, window)
        
        # Herramientas avanzadas
        self.crear_seccion_herramientas(main_frame)
        
        # Información y botones de cierre
        self.crear_seccion_info_cierre(main_frame, window)
    
    def crear_seccion_imagenes_base(self, parent):
        """Crea la sección de estado de imágenes base"""
        status_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)
        status_frame.pack(fill="x", pady=(0, 15))
        
        status_title = ctk.CTkLabel(
            status_frame, text="📁 Estado de Imágenes Base",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_title.pack(pady=(15, 10))
        
        # Buscar y mostrar estado actual
        estado = self.buscar_imagenes_base()
        
        # Estado del encabezado
        enc_status = "✅ Encontrado" if estado['encabezado_encontrado'] else "❌ No encontrado"
        enc_color = "lightgreen" if estado['encabezado_encontrado'] else "lightcoral"
        enc_label = ctk.CTkLabel(
            status_frame, text=f"📋 Encabezado.png: {enc_status}",
            font=ctk.CTkFont(size=12), text_color=enc_color
        )
        enc_label.pack(pady=2)
        
        # Estado de la insignia
        ins_status = "✅ Encontrado" if estado['insignia_encontrada'] else "❌ No encontrado"
        ins_color = "lightgreen" if estado['insignia_encontrada'] else "lightcoral"
        ins_label = ctk.CTkLabel(
            status_frame, text=f"🏛️ Insignia.png: {ins_status}",
            font=ctk.CTkFont(size=12), text_color=ins_color
        )
        ins_label.pack(pady=(2, 15))
        
        # Mostrar directorio
        if estado['directorio']:
            dir_label = ctk.CTkLabel(
                status_frame, text=f"📂 Directorio: {estado['directorio']}",
                font=ctk.CTkFont(size=10), text_color="gray70"
            )
            dir_label.pack(pady=(0, 10))
    
    def crear_seccion_imagenes_personalizadas(self, parent, window):
        """Crea la sección de gestión de imágenes personalizadas"""
        custom_frame = ctk.CTkFrame(parent, fg_color="darkblue", corner_radius=10)
        custom_frame.pack(fill="x", pady=(0, 15))
        
        custom_title = ctk.CTkLabel(
            custom_frame, text="🎨 Imágenes Personalizadas",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        custom_title.pack(pady=(15, 10))
        
        # Botones de carga
        btn_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        enc_btn = ctk.CTkButton(
            btn_frame, text="📋 Cargar Encabezado", 
            command=lambda: self.cargar_y_actualizar("encabezado", window),
            width=200, height=35, font=ctk.CTkFont(size=12, weight="bold")
        )
        enc_btn.pack(side="left", padx=(0, 10))
        
        ins_btn = ctk.CTkButton(
            btn_frame, text="🏛️ Cargar Insignia", 
            command=lambda: self.cargar_y_actualizar("insignia", window),
            width=200, height=35, font=ctk.CTkFont(size=12, weight="bold")
        )
        ins_btn.pack(side="right", padx=(10, 0))
        
        # Estado actual
        self.enc_custom_label = ctk.CTkLabel(
            custom_frame, 
            text=f"📋 Encabezado: {'✅ Cargado' if self.app.encabezado_personalizado else '⏸️ No cargado'}",
            font=ctk.CTkFont(size=11), text_color="lightblue"
        )
        self.enc_custom_label.pack(pady=2)
        
        self.ins_custom_label = ctk.CTkLabel(
            custom_frame, 
            text=f"🏛️ Insignia: {'✅ Cargado' if self.app.insignia_personalizada else '⏸️ No cargado'}",
            font=ctk.CTkFont(size=11), text_color="lightblue"
        )
        self.ins_custom_label.pack(pady=(2, 15))
    
    def crear_seccion_herramientas(self, parent):
        """Crea la sección de herramientas avanzadas"""
        tools_frame = ctk.CTkFrame(parent, fg_color="darkgreen", corner_radius=10)
        tools_frame.pack(fill="x", pady=(0, 15))
        
        tools_title = ctk.CTkLabel(
            tools_frame, text="🛠️ Herramientas Avanzadas",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        tools_title.pack(pady=(15, 10))
        
        tools_btn_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        tools_btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Botón para restablecer
        reset_btn = ctk.CTkButton(
            tools_btn_frame, text="🔄 Restablecer Todo", 
            command=self.restablecer_imagenes,
            width=150, height=30, fg_color="red", hover_color="darkred"
        )
        reset_btn.pack(side="left")
        
        # Botón para optimizar
        optimize_btn = ctk.CTkButton(
            tools_btn_frame, text="⚡ Optimizar Imágenes", 
            command=self.optimizar_imagenes,
            width=150, height=30, fg_color="orange", hover_color="darkorange"
        )
        optimize_btn.pack(side="right")
    
    def crear_seccion_info_cierre(self, parent, window):
        """Crea la sección de información y botones de cierre"""
        # Información técnica
        info_frame = ctk.CTkFrame(parent, fg_color="purple", corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_text = """💡 INFORMACIÓN TÉCNICA:

📏 TAMAÑOS RECOMENDADOS:
• Encabezado: 600x100px (máx: 800x150px)  
• Insignia: 100x100px (máx: 200x200px)

📎 FORMATOS SOPORTADOS: PNG, JPG, JPEG, BMP, GIF
📦 TAMAÑO MÁXIMO: 10MB por imagen
🎯 CALIDAD: Se recomienda PNG para mejor calidad

⚠️ PRIORIDAD: Las imágenes personalizadas tienen prioridad sobre las base"""
        
        info_label = ctk.CTkLabel(
            info_frame, text=info_text, font=ctk.CTkFont(size=10),
            justify="left", wraplength=600, text_color="white"
        )
        info_label.pack(padx=15, pady=15)
        
        # Botón de cierre
        close_btn = ctk.CTkButton(
            parent, text="✅ Cerrar Gestión", 
            command=window.destroy,
            width=200, height=40, font=ctk.CTkFont(size=12, weight="bold")
        )
        close_btn.pack(pady=(0, 10))
    
    def cargar_y_actualizar(self, tipo, window):
        """Carga imagen y actualiza la interfaz"""
        resultado = self.cargar_imagen_personalizada(tipo, window)
        if resultado:
            # Actualizar labels
            if tipo == "encabezado":
                self.enc_custom_label.configure(text="📋 Encabezado: ✅ Cargado")
            else:
                self.ins_custom_label.configure(text="🏛️ Insignia: ✅ Cargado")
    
    def restablecer_imagenes(self):
        """Restablece todas las imágenes personalizadas"""
        respuesta = messagebox.askyesno(
            "🔄 Restablecer Imágenes",
            "¿Estás seguro de que quieres restablecer todas las imágenes personalizadas?\n\n"
            "Se usarán las imágenes base (si están disponibles)."
        )
        
        if respuesta:
            self.app.encabezado_personalizado = None
            self.app.insignia_personalizada = None
            
            # Actualizar labels si existen
            if hasattr(self, 'enc_custom_label'):
                self.enc_custom_label.configure(text="📋 Encabezado: ⏸️ No cargado")
            if hasattr(self, 'ins_custom_label'):
                self.ins_custom_label.configure(text="🏛️ Insignia: ⏸️ No cargado")
            
            messagebox.showinfo("🔄 Restablecido", 
                "Imágenes restablecidas. Se usarán las imágenes base cuando estén disponibles.")
    
    def optimizar_imagenes(self):
        """Función placeholder para optimización futura"""
        messagebox.showinfo("⚡ Optimización", 
            "🚧 Función en desarrollo\n\n"
            "Próximamente:\n"
            "• Redimensionamiento automático\n"
            "• Compresión inteligente\n"
            "• Conversión de formatos\n"
            "• Mejora de calidad")
    
    def obtener_ruta_imagen(self, tipo):
        """Obtiene la ruta final de la imagen a usar (personalizada o base)"""
        if tipo == "encabezado":
            return self.app.encabezado_personalizado or self.app.ruta_encabezado
        elif tipo == "insignia":
            return self.app.insignia_personalizada or self.app.ruta_insignia
        return None
    
    def tiene_imagen(self, tipo):
        """Verifica si hay una imagen disponible del tipo especificado"""
        ruta = self.obtener_ruta_imagen(tipo)
        return ruta is not None and os.path.exists(ruta)
    
    def get_image_info(self, tipo):
        """Obtiene información detallada de una imagen"""
        ruta = self.obtener_ruta_imagen(tipo)
        if not ruta or not os.path.exists(ruta):
            return None
        
        return self.analizar_imagen(ruta, tipo)