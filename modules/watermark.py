"""
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
