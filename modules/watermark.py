"""
Sistema Avanzado de Marcas de Agua para Documentos - Versión Corregida
Compatible con diferentes versiones de python-docx
"""

import os
from PIL import Image, ImageEnhance
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
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
            if img.mode == 'RGBA':
                # Procesar canal alpha
                alpha = img.split()[-1]
                alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
                img.putalpha(alpha)
            else:
                # Si no tiene alpha, crear uno
                img = img.convert('RGBA')
                data = img.getdata()
                newData = []
                for item in data:
                    # Cambiar todos los píxeles blancos (o casi blancos) a transparentes
                    if len(item) == 4:
                        newData.append((item[0], item[1], item[2], int(item[3] * opacity)))
                    else:
                        newData.append((item[0], item[1], item[2], int(255 * opacity)))
                img.putdata(newData)
            
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
        """Agrega marca de agua a una sección del documento - Método alternativo"""
        try:
            # Método simplificado que no usa xpath con namespaces
            header = section.header
            
            # Limpiar header existente si es necesario
            if not header.paragraphs:
                header.add_paragraph()
            
            # Usar el primer párrafo
            paragraph = header.paragraphs[0]
            
            # Agregar la imagen directamente al header
            run = paragraph.add_run()
            
            # Intentar diferentes métodos según la versión
            try:
                # Método 1: Agregar imagen con tamaño específico
                if stretch:
                    # Calcular ancho de página menos márgenes (aproximado)
                    picture = run.add_picture(image_path, width=Inches(7.5))
                else:
                    picture = run.add_picture(image_path, width=Inches(5))
                
                # Intentar configurar la imagen como fondo
                self._configure_as_background(picture, paragraph)
                
                return True
                
            except Exception as e:
                print(f"Método 1 falló: {e}")
                
                # Método 2: Usar drawing ML directamente
                try:
                    return self._add_watermark_alternative(paragraph, image_path, opacity, stretch)
                except Exception as e2:
                    print(f"Método 2 también falló: {e2}")
                    return False
                    
        except Exception as e:
            print(f"Error agregando marca de agua: {e}")
            return False
    
    def _configure_as_background(self, picture, paragraph):
        """Intenta configurar la imagen como fondo"""
        try:
            # Obtener el elemento de imagen
            if hasattr(picture, '_inline'):
                inline = picture._inline
                
                # Intentar cambiar a anchor (flotante)
                # Esto permite que el texto fluya sobre la imagen
                anchor = OxmlElement('wp:anchor')
                
                # Copiar atributos importantes
                for key, value in [
                    ('behindDoc', '1'),
                    ('locked', '0'),
                    ('layoutInCell', '1'),
                    ('allowOverlap', '1')
                ]:
                    anchor.set(key, value)
                
                # Mover elementos del inline al anchor
                for child in list(inline):
                    anchor.append(child)
                
                # Reemplazar inline con anchor
                parent = inline.getparent()
                parent.replace(inline, anchor)
                
        except Exception as e:
            # Si falla, al menos la imagen está en el header
            pass
    
    def _add_watermark_alternative(self, paragraph, image_path, opacity, stretch):
        """Método alternativo para agregar marca de agua usando XML directo"""
        try:
            # Procesar imagen primero
            if stretch:
                processed_image = self.process_image_for_watermark(image_path, opacity, 7.5)
            else:
                processed_image = self.process_image_for_watermark(image_path, opacity, 5)
            
            if not processed_image:
                return False
            
            # Convertir a base64
            image_base64 = base64.b64encode(processed_image).decode('utf-8')
            
            # Crear elemento run
            run = paragraph.add_run()
            r = run._r
            
            # Crear estructura pict
            pict = OxmlElement('w:pict')
            
            # Crear shape
            shape = OxmlElement('v:shape')
            shape.set('id', '_x0000_i1025')
            shape.set('type', '#_x0000_t75')
            shape.set('style', 'width:600pt;height:100pt;position:absolute;z-index:-251658752')
            
            # Crear imagedata
            imagedata = OxmlElement('v:imagedata')
            imagedata.set(qn('r:id'), 'rId1')
            imagedata.set('o:title', 'Watermark')
            
            # Agregar imagedata a shape
            shape.append(imagedata)
            
            # Agregar shape a pict
            pict.append(shape)
            
            # Agregar pict a run
            r.append(pict)
            
            # Intentar agregar la relación de imagen
            try:
                # Este es un método simplificado, puede necesitar ajustes
                document = paragraph.part
                image_part = document.new_image_part(image_path)
                imagedata.set(qn('r:id'), document.relate_to(image_part, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'))
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"Error en método alternativo: {e}")
            return False
    
    def add_simple_header_image(self, section, image_path, width_inches=6.5):
        """Método simple para agregar imagen al encabezado"""
        try:
            header = section.header
            
            # Asegurar que hay un párrafo
            if not header.paragraphs:
                p = header.add_paragraph()
            else:
                p = header.paragraphs[0]
            
            # Centrar el párrafo
            p.alignment = 1  # Center
            
            # Agregar la imagen
            run = p.add_run()
            picture = run.add_picture(image_path, width=Inches(width_inches))
            
            return True
            
        except Exception as e:
            print(f"Error agregando imagen simple al header: {e}")
            return False
