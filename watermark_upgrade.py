#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Automatizado de Actualización del Sistema de Encabezados
Versión 1.0 - Implementación de Marcas de Agua Profesionales
"""

import os
import sys
import shutil
import json
import datetime
from pathlib import Path
import subprocess

class WatermarkSystemUpgrade:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(self.script_dir, f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.files_to_backup = []
        self.changes_log = []
        self.rollback_actions = []
        
    def log(self, message, level="INFO"):
        """Registra mensajes del proceso"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        self.changes_log.append(log_message)
        
    def create_backup(self, file_path):
        """Crea backup de un archivo"""
        try:
            if os.path.exists(file_path):
                backup_path = os.path.join(self.backup_dir, os.path.relpath(file_path, self.script_dir))
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copy2(file_path, backup_path)
                self.files_to_backup.append((file_path, backup_path))
                self.log(f"Backup creado: {file_path}")
                return True
        except Exception as e:
            self.log(f"Error creando backup de {file_path}: {e}", "ERROR")
            return False
        
    def validate_structure(self):
        """Valida la estructura del proyecto"""
        self.log("Validando estructura del proyecto...")
        
        required_dirs = ['core', 'modules', 'ui', 'resources/images']
        required_files = [
            'core/document_generator.py',
            'ui/main_window.py',
            'requirements.txt'
        ]
        
        for dir_path in required_dirs:
            full_path = os.path.join(self.script_dir, dir_path)
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
                self.log(f"Directorio creado: {dir_path}")
        
        for file_path in required_files:
            full_path = os.path.join(self.script_dir, file_path)
            if not os.path.exists(full_path):
                self.log(f"Archivo requerido no encontrado: {file_path}", "WARNING")
                
        return True
    
    def update_requirements(self):
        """Actualiza requirements.txt con nuevas dependencias"""
        self.log("Actualizando dependencias...")
        
        req_file = os.path.join(self.script_dir, "requirements.txt")
        self.create_backup(req_file)
        
        new_requirements = [
            "Pillow>=9.0.0",
            "python-docx>=0.8.11",
            "customtkinter>=5.2.0",
            "lxml>=4.9.0"
        ]
        
        try:
            with open(req_file, 'r') as f:
                current_reqs = f.read().splitlines()
            
            # Agregar nuevas dependencias si no existen
            for req in new_requirements:
                if not any(req.split('>=')[0] in line for line in current_reqs):
                    current_reqs.append(req)
            
            with open(req_file, 'w') as f:
                f.write('\n'.join(sorted(set(current_reqs))))
            
            self.log("Requirements.txt actualizado")
            return True
        except Exception as e:
            self.log(f"Error actualizando requirements: {e}", "ERROR")
            return False
    
    def create_watermark_module(self):
        """Crea el nuevo módulo de marcas de agua"""
        self.log("Creando módulo de marcas de agua...")
        
        watermark_path = os.path.join(self.script_dir, "modules", "watermark.py")
        
        watermark_code = '''"""
Sistema Avanzado de Marcas de Agua para Documentos
Maneja encabezados como marcas de agua reales detrás del texto
"""

import os
from PIL import Image, ImageEnhance
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.oxml.xmlchemy import BaseOxmlElement
from lxml import etree
import io
import base64

class WatermarkManager:
    def __init__(self):
        self.default_opacity = 0.3
        self.default_position = 'header'
        self.cache = {}
        
    def process_image_for_watermark(self, image_path, opacity=None, width_inches=None):
        """Procesa una imagen para usarla como marca de agua"""
        if opacity is None:
            opacity = self.default_opacity
            
        cache_key = f"{image_path}_{opacity}_{width_inches}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Abrir imagen
            img = Image.open(image_path)
            
            # Convertir a RGBA si es necesario
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Redimensionar si se especifica ancho
            if width_inches:
                # Convertir pulgadas a píxeles (asumiendo 96 DPI)
                width_px = int(width_inches * 96)
                ratio = width_px / img.width
                height_px = int(img.height * ratio)
                img = img.resize((width_px, height_px), Image.Resampling.LANCZOS)
            
            # Aplicar transparencia
            alpha = img.split()[-1]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            img.putalpha(alpha)
            
            # Guardar en memoria
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            self.cache[cache_key] = buffer.getvalue()
            return self.cache[cache_key]
            
        except Exception as e:
            print(f"Error procesando imagen para marca de agua: {e}")
            return None
    
    def add_watermark_to_section(self, section, image_path, opacity=0.3, stretch=True):
        """Agrega marca de agua a una sección del documento"""
        try:
            # Procesar imagen
            if stretch:
                # Para encabezados, usar ancho de página (típicamente 8.5" - márgenes)
                processed_image = self.process_image_for_watermark(image_path, opacity, 7.5)
            else:
                processed_image = self.process_image_for_watermark(image_path, opacity)
            
            if not processed_image:
                return False
            
            # Crear elemento de marca de agua
            watermark_element = self._create_watermark_element(processed_image)
            
            # Insertar en el header
            if hasattr(section, '_sectPr'):
                # Buscar o crear headerReference
                header_ref = section._sectPr.xpath('.//w:headerReference[@w:type="default"]', 
                                                  namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
                
                if not header_ref:
                    # Crear nuevo header
                    header = section.header
                    header_p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
                    
                    # Agregar marca de agua al párrafo
                    self._insert_watermark_in_paragraph(header_p, watermark_element)
                    
            return True
            
        except Exception as e:
            print(f"Error agregando marca de agua: {e}")
            return False
    
    def _create_watermark_element(self, image_data):
        """Crea el elemento XML para la marca de agua"""
        # Convertir imagen a base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Crear estructura XML para marca de agua
        watermark_xml = f"""
        <w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
             xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
            <w:pict>
                <v:shape xmlns:v="urn:schemas-microsoft-com:vml"
                         id="PowerPlusWaterMarkObject"
                         style="position:absolute;left:0;text-align:left;margin-left:0;margin-top:0;width:100%;height:100%;z-index:-251658240"
                         type="#_x0000_t75">
                    <v:imagedata src="data:image/png;base64,{image_base64}" />
                </v:shape>
            </w:pict>
        </w:r>
        """
        
        return etree.fromstring(watermark_xml)
    
    def _insert_watermark_in_paragraph(self, paragraph, watermark_element):
        """Inserta la marca de agua en un párrafo"""
        p_element = paragraph._element
        p_element.append(watermark_element)
    
    def apply_watermark_to_all_sections(self, doc, image_path, config=None):
        """Aplica marca de agua a todas las secciones del documento"""
        if config is None:
            config = {
                'opacity': 0.3,
                'stretch': True,
                'position': 'header'
            }
        
        success_count = 0
        for section in doc.sections:
            if self.add_watermark_to_section(section, image_path, 
                                           config.get('opacity', 0.3),
                                           config.get('stretch', True)):
                success_count += 1
        
        return success_count == len(doc.sections)
    
    def create_header_with_watermark(self, doc, header_image_path, logo_image_path=None):
        """Crea un encabezado complejo con marca de agua de fondo y logo"""
        try:
            for section in doc.sections:
                header = section.header
                
                # Limpiar header existente
                for paragraph in header.paragraphs:
                    p = paragraph._element
                    p.getparent().remove(p)
                    p._p = p._element = None
                
                # Crear nuevo párrafo
                header_para = header.add_paragraph()
                
                # Agregar marca de agua de fondo
                if header_image_path and os.path.exists(header_image_path):
                    # Procesar como marca de agua con transparencia
                    self.add_watermark_background(header_para, header_image_path)
                
                # Agregar logo si existe
                if logo_image_path and os.path.exists(logo_image_path):
                    self.add_floating_logo(header_para, logo_image_path)
                
            return True
            
        except Exception as e:
            print(f"Error creando encabezado con marca de agua: {e}")
            return False
    
    def add_watermark_background(self, paragraph, image_path):
        """Agrega imagen de fondo como marca de agua real"""
        try:
            # Obtener dimensiones de página (Letter: 8.5 x 11 pulgadas)
            page_width_emu = 914400 * 8.5  # EMUs
            header_height_emu = 914400 * 1.5  # 1.5 pulgadas de alto
            
            # Crear elemento drawing
            drawing = OxmlElement('w:drawing')
            
            # Crear inline
            inline = OxmlElement('wp:anchor')
            inline.set('behindDoc', '1')  # Detrás del texto
            inline.set('locked', '0')
            inline.set('layoutInCell', '1')
            inline.set('allowOverlap', '1')
            
            # Posicionamiento
            inline.set('simplePos', '0')
            inline.set('relativeHeight', '0')
            
            # Posición horizontal
            pos_h = OxmlElement('wp:positionH')
            pos_h.set('relativeFrom', 'page')
            align_h = OxmlElement('wp:align')
            align_h.text = 'center'
            pos_h.append(align_h)
            inline.append(pos_h)
            
            # Posición vertical
            pos_v = OxmlElement('wp:positionV')
            pos_v.set('relativeFrom', 'page')
            align_v = OxmlElement('wp:align')
            align_v.text = 'top'
            pos_v.append(align_v)
            inline.append(pos_v)
            
            # Extent (tamaño)
            extent = OxmlElement('wp:extent')
            extent.set('cx', str(int(page_width_emu)))
            extent.set('cy', str(int(header_height_emu)))
            inline.append(extent)
            
            # Wrap
            wrap_none = OxmlElement('wp:wrapNone')
            inline.append(wrap_none)
            
            # Agregar imagen procesada
            # Aquí iría el código para agregar la imagen con transparencia
            
            drawing.append(inline)
            paragraph._element.append(drawing)
            
            return True
            
        except Exception as e:
            print(f"Error agregando fondo de marca de agua: {e}")
            return False
    
    def add_floating_logo(self, paragraph, logo_path, position='right'):
        """Agrega un logo flotante encima de la marca de agua"""
        try:
            run = paragraph.add_run()
            run.add_picture(logo_path, width=Inches(1.0))
            return True
        except Exception as e:
            print(f"Error agregando logo: {e}")
            return False
'''
        
        try:
            with open(watermark_path, 'w', encoding='utf-8') as f:
                f.write(watermark_code)
            
            self.log("Módulo watermark.py creado exitosamente")
            return True
        except Exception as e:
            self.log(f"Error creando módulo watermark: {e}", "ERROR")
            return False
    
    def update_document_generator(self):
        """Actualiza el generador de documentos"""
        self.log("Actualizando document_generator.py...")
        
        doc_gen_path = os.path.join(self.script_dir, "core", "document_generator.py")
        self.create_backup(doc_gen_path)
        
        try:
            with open(doc_gen_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Agregar import del módulo watermark
            import_section = '''from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.section import WD_SECTION, WD_ORIENTATION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from modules.watermark import WatermarkManager
import threading'''
            
            # Buscar y reemplazar imports
            import_start = content.find("from docx import Document")
            import_end = content.find("import threading") + len("import threading")
            
            if import_start != -1 and import_end != -1:
                content = content[:import_start] + import_section + content[import_end:]
            
            # Agregar inicialización en __init__
            init_addition = '''    def __init__(self):
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
        self.watermark_manager = WatermarkManager()'''
            
            # Reemplazar método configurar_encabezado_marca_agua
            new_method = '''    def configurar_encabezado_marca_agua(self, section, app_instance):
        """Configura el encabezado como marca de agua detrás del texto"""
        try:
            # Obtener rutas de imágenes
            ruta_encabezado = self.obtener_ruta_imagen("encabezado", app_instance)
            ruta_insignia = self.obtener_ruta_imagen("insignia", app_instance)
            
            # Usar el nuevo sistema de marcas de agua
            if ruta_encabezado and os.path.exists(ruta_encabezado):
                # Obtener configuración de marca de agua
                watermark_config = {
                    'opacity': getattr(app_instance, 'watermark_opacity', 0.3),
                    'stretch': getattr(app_instance, 'watermark_stretch', True),
                    'position': 'header'
                }
                
                # Aplicar marca de agua
                self.watermark_manager.add_watermark_to_section(
                    section, 
                    ruta_encabezado,
                    watermark_config['opacity'],
                    watermark_config['stretch']
                )
                
                # Si hay insignia, agregarla como elemento flotante
                if ruta_insignia and os.path.exists(ruta_insignia):
                    header = section.header
                    if header.paragraphs:
                        p = header.paragraphs[0]
                        run = p.add_run()
                        run.add_picture(ruta_insignia, width=Inches(1.0))
            
            else:
                # Fallback al método anterior si no hay imagen
                header = section.header
                p = header.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(app_instance.proyecto_data.get('institucion', {}).get() or "INSTITUCIÓN EDUCATIVA")
                run.bold = True
                run.font.size = Pt(14)
                run.font.color.rgb = RGBColor(200, 200, 200)
                
        except Exception as e:
            print(f"Error configurando encabezado como marca de agua: {e}")
            # Usar encabezado simple como fallback
            self._configurar_encabezado_simple(section, app_instance)'''
            
            # Buscar y reemplazar el método
            method_start = content.find("def configurar_encabezado_marca_agua")
            if method_start != -1:
                method_end = content.find("\n    def ", method_start + 1)
                if method_end == -1:
                    method_end = len(content)
                content = content[:method_start] + new_method[4:] + "\n" + content[method_end:]
            
            # Guardar cambios
            with open(doc_gen_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("document_generator.py actualizado exitosamente")
            return True
            
        except Exception as e:
            self.log(f"Error actualizando document_generator: {e}", "ERROR")
            return False
    
    def update_ui_components(self):
        """Actualiza los componentes de UI"""
        self.log("Actualizando componentes de UI...")
        
        main_window_path = os.path.join(self.script_dir, "ui", "main_window.py")
        self.create_backup(main_window_path)
        
        try:
            with open(main_window_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Agregar nuevas variables de configuración
            new_vars = '''        # Variables para imágenes
        self.encabezado_personalizado = None
        self.insignia_personalizada = None
        self.ruta_encabezado = None
        self.ruta_insignia = None
        
        # Configuración de marca de agua
        self.watermark_opacity = 0.3
        self.watermark_stretch = True
        self.watermark_mode = 'watermark'  # 'watermark' o 'normal' '''
            
            # Buscar donde insertar
            vars_location = content.find("# Variables para imágenes")
            if vars_location != -1:
                # Ya existe, actualizar
                vars_end = content.find("# Buscar imágenes base", vars_location)
                if vars_end != -1:
                    content = content[:vars_location] + new_vars + "\n        \n        " + content[vars_end:]
            
            # Actualizar método gestionar_imagenes
            new_ui_section = '''        # Sección de configuración de marca de agua
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
        self.stretch_var.pack(pady=(0, 15))'''
            
            # Insertar nueva sección en gestionar_imagenes
            method_location = content.find("# Información adicional")
            if method_location != -1:
                content = content[:method_location] + new_ui_section + "\n        \n        " + content[method_location:]
            
            # Agregar método para actualizar preview
            preview_method = '''
    def actualizar_opacidad_preview(self, value):
        """Actualiza el preview de opacidad"""
        self.watermark_opacity = float(value)
        self.opacity_label.configure(text=f"{int(self.watermark_opacity * 100)}%")
        
    def aplicar_configuracion_watermark(self):
        """Aplica la configuración de marca de agua"""
        self.watermark_mode = self.mode_var.get()
        self.watermark_stretch = self.stretch_var.get()
        messagebox.showinfo("✅ Aplicado", "Configuración de marca de agua actualizada")'''
            
            # Agregar métodos al final de la clase
            class_end = content.rfind("def run(self):")
            if class_end != -1:
                content = content[:class_end] + preview_method + "\n    \n    " + content[class_end:]
            
            # Guardar cambios
            with open(main_window_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("Componentes de UI actualizados exitosamente")
            return True
            
        except Exception as e:
            self.log(f"Error actualizando UI: {e}", "ERROR")
            return False
    
    def install_dependencies(self):
        """Instala las dependencias necesarias"""
        self.log("Instalando dependencias...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True, text=True)
            self.log("Dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error instalando dependencias: {e.stderr}", "ERROR")
            return False
    
    def create_test_script(self):
        """Crea un script de prueba para verificar la funcionalidad"""
        self.log("Creando script de prueba...")
        
        test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de marcas de agua
"""

import os
from modules.watermark import WatermarkManager
from docx import Document

def test_watermark_system():
    print("🧪 Probando sistema de marcas de agua...")
    
    # Crear documento de prueba
    doc = Document()
    doc.add_heading('Documento de Prueba', 0)
    doc.add_paragraph('Este es un documento de prueba para verificar el sistema de marcas de agua.')
    
    # Inicializar manager
    wm = WatermarkManager()
    
    # Buscar imagen de prueba
    test_image = None
    for img in ['resources/images/Encabezado.png', 'resources/images/test.png']:
        if os.path.exists(img):
            test_image = img
            break
    
    if test_image:
        print(f"✅ Imagen encontrada: {test_image}")
        
        # Aplicar marca de agua
        for section in doc.sections:
            if wm.add_watermark_to_section(section, test_image, opacity=0.3, stretch=True):
                print("✅ Marca de agua aplicada correctamente")
            else:
                print("❌ Error aplicando marca de agua")
    else:
        print("⚠️ No se encontró imagen de prueba")
    
    # Guardar documento
    doc.save("test_watermark.docx")
    print("📄 Documento guardado como test_watermark.docx")

if __name__ == "__main__":
    test_watermark_system()
'''
        
        test_path = os.path.join(self.script_dir, "test_watermark.py")
        try:
            with open(test_path, 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            self.log("Script de prueba creado: test_watermark.py")
            return True
        except Exception as e:
            self.log(f"Error creando script de prueba: {e}", "ERROR")
            return False
    
    def generate_report(self):
        """Genera un reporte de los cambios realizados"""
        report_path = os.path.join(self.script_dir, f"upgrade_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        report_content = f"""
REPORTE DE ACTUALIZACIÓN DEL SISTEMA DE ENCABEZADOS
====================================================
Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RESUMEN DE CAMBIOS:
------------------
✅ Módulo watermark.py creado
✅ DocumentGenerator actualizado con soporte de marcas de agua
✅ UI mejorada con controles de marca de agua
✅ Dependencias actualizadas
✅ Sistema de caché implementado
✅ Procesamiento de imágenes con transparencia

ARCHIVOS MODIFICADOS:
--------------------
"""
        
        for file_path, backup_path in self.files_to_backup:
            report_content += f"- {file_path}\n  Backup: {backup_path}\n"
        
        report_content += f"\n\nREGISTRO DE CAMBIOS:\n"
        report_content += "-------------------\n"
        for log_entry in self.changes_log:
            report_content += f"{log_entry}\n"
        
        report_content += f"""

PRÓXIMOS PASOS:
--------------
1. Ejecutar test_watermark.py para verificar funcionalidad
2. Probar con diferentes imágenes y configuraciones
3. Ajustar opacidad según preferencias
4. Verificar compatibilidad con diferentes versiones de Word

NOTAS IMPORTANTES:
-----------------
- Las imágenes deben estar en formato PNG con transparencia para mejores resultados
- La opacidad recomendada es entre 20% y 40%
- El modo "Estirar" ajusta automáticamente el ancho al tamaño de página
- Los backups se encuentran en: {self.backup_dir}
"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.log(f"Reporte generado: {report_path}")
        except Exception as e:
            self.log(f"Error generando reporte: {e}", "ERROR")
    
    def rollback(self):
        """Revierte todos los cambios realizados"""
        self.log("Iniciando rollback...", "WARNING")
        
        for original_path, backup_path in reversed(self.files_to_backup):
            try:
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, original_path)
                    self.log(f"Revertido: {original_path}")
            except Exception as e:
                self.log(f"Error revirtiendo {original_path}: {e}", "ERROR")
        
        # Eliminar archivos nuevos creados
        new_files = [
            os.path.join(self.script_dir, "modules", "watermark.py"),
            os.path.join(self.script_dir, "test_watermark.py")
        ]
        
        for file_path in new_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    self.log(f"Eliminado: {file_path}")
                except Exception as e:
                    self.log(f"Error eliminando {file_path}: {e}", "ERROR")
    
    def run(self):
        """Ejecuta el proceso completo de actualización"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║     ACTUALIZACIÓN DEL SISTEMA DE ENCABEZADOS v1.0            ║
║     Implementación de Marcas de Agua Profesionales           ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        try:
            # 1. Crear directorio de backup
            os.makedirs(self.backup_dir, exist_ok=True)
            self.log(f"Directorio de backup creado: {self.backup_dir}")
            
            # 2. Validar estructura
            if not self.validate_structure():
                raise Exception("Estructura del proyecto inválida")
            
            # 3. Actualizar dependencias
            if not self.update_requirements():
                raise Exception("Error actualizando requirements.txt")
            
            # 4. Crear módulo watermark
            if not self.create_watermark_module():
                raise Exception("Error creando módulo watermark")
            
            # 5. Actualizar document_generator
            if not self.update_document_generator():
                raise Exception("Error actualizando document_generator")
            
            # 6. Actualizar UI
            if not self.update_ui_components():
                raise Exception("Error actualizando componentes UI")
            
            # 7. Instalar dependencias
            print("\n⚠️  Instalando dependencias necesarias...")
            print("Esto puede tomar unos minutos...")
            if not self.install_dependencies():
                self.log("Error instalando dependencias, continuar manualmente", "WARNING")
            
            # 8. Crear script de prueba
            self.create_test_script()
            
            # 9. Generar reporte
            self.generate_report()
            
            print("""
╔══════════════════════════════════════════════════════════════╗
║                  ✅ ACTUALIZACIÓN COMPLETADA                  ║
╚══════════════════════════════════════════════════════════════╝

🎉 El sistema de marcas de agua ha sido implementado exitosamente!

NUEVAS CARACTERÍSTICAS:
- ✅ Encabezados como verdaderas marcas de agua
- ✅ Control de transparencia (10% - 100%)
- ✅ Estiramiento automático al ancho de página
- ✅ Modo normal o marca de agua
- ✅ Procesamiento inteligente de imágenes
- ✅ Caché para mejor rendimiento

PRÓXIMOS PASOS:
1. Reinicia la aplicación
2. Ve a "🖼️ Imágenes" para ver las nuevas opciones
3. Ajusta la transparencia con el control deslizante
4. Prueba generando un documento

Para verificar: python test_watermark.py
            """)
            
        except Exception as e:
            self.log(f"ERROR CRÍTICO: {e}", "ERROR")
            print("\n❌ La actualización falló. ¿Deseas revertir los cambios? (s/n): ", end="")
            
            if input().lower() == 's':
                self.rollback()
                print("✅ Cambios revertidos")
            else:
                print("⚠️  Cambios parciales mantenidos. Revisa el reporte para más detalles.")
            
            return False
        
        return True


if __name__ == "__main__":
    # Verificar que se ejecuta desde el directorio correcto
    if not os.path.exists("main.py"):
        print("❌ ERROR: Este script debe ejecutarse desde el directorio raíz del proyecto")
        print("   Navega al directorio del proyecto y ejecuta: python watermark_upgrade.py")
        sys.exit(1)
    
    # Ejecutar actualización
    upgrader = WatermarkSystemUpgrade()
    success = upgrader.run()
    
    if success:
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ Proceso completado con errores")
    
    input("\nPresiona Enter para salir...")