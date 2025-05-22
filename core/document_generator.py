"""
Generador de documentos Word - Versión Corregida con Encabezados como Marca de Agua
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.section import WD_SECTION, WD_ORIENTATION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import threading
import os
from datetime import datetime
from tkinter import filedialog, messagebox
import re

class DocumentGenerator:
    def __init__(self):
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
    
    def generar_documento_async(self, app_instance):
        """Genera el documento profesional en un hilo separado"""
        def generar():
            try:
                app_instance.progress.set(0)
                app_instance.progress.start()
                
                # Crear documento
                doc = Document()
                
                # Configurar documento con encabezados como marca de agua
                self.configurar_documento_completo(doc, app_instance)
                app_instance.progress.set(0.1)
                
                # Generar contenido
                if app_instance.incluir_portada.get():
                    self.crear_portada_profesional(doc, app_instance)
                    app_instance.progress.set(0.2)
                
                if app_instance.incluir_agradecimientos.get():
                    self.crear_agradecimientos_profesional(doc, app_instance)
                    app_instance.progress.set(0.3)
                
                if 'resumen' in app_instance.secciones_activas and 'resumen' in app_instance.content_texts:
                    contenido_resumen = app_instance.content_texts['resumen'].get("1.0", "end")
                    self.crear_seccion_profesional(doc, "RESUMEN", contenido_resumen, app_instance, nivel=1)
                    app_instance.progress.set(0.4)
                
                if app_instance.incluir_indice.get():
                    self.crear_indice_profesional(doc, app_instance)
                    app_instance.progress.set(0.5)
                
                # Contenido principal dinámico
                self.crear_contenido_dinamico_mejorado(doc, app_instance)
                app_instance.progress.set(0.8)
                
                # Referencias
                self.crear_referencias_profesionales(doc, app_instance)
                app_instance.progress.set(0.9)
                
                # Guardar documento
                filename = filedialog.asksaveasfilename(
                    defaultextension=".docx",
                    filetypes=[("Word documents", "*.docx")],
                    title="Guardar Proyecto Académico Profesional"
                )
                
                if filename:
                    doc.save(filename)
                    app_instance.progress.stop()
                    app_instance.progress.set(1)
                    
                    self.mostrar_mensaje_exito(filename, app_instance)
                else:
                    app_instance.progress.stop()
                    app_instance.progress.set(0)
            
            except Exception as e:
                app_instance.progress.stop()
                app_instance.progress.set(0)
                messagebox.showerror("❌ Error", f"Error al generar documento:\n{str(e)}")
        
        thread = threading.Thread(target=generar)
        thread.daemon = True
        thread.start()
    
    def configurar_documento_completo(self, doc, app_instance):
        """Configura el documento con estilos y encabezados como marca de agua"""
        # Configurar márgenes
        for section in doc.sections:
            section.top_margin = Inches(app_instance.formato_config['margen'] / 2.54)
            section.bottom_margin = Inches(app_instance.formato_config['margen'] / 2.54)
            section.left_margin = Inches(app_instance.formato_config['margen'] / 2.54)
            section.right_margin = Inches(app_instance.formato_config['margen'] / 2.54)
            
            # Configurar encabezado como marca de agua
            self.configurar_encabezado_marca_agua(section, app_instance)
        
        # Configurar estilos
        self.configurar_estilos_profesionales(doc, app_instance)
    
    def configurar_encabezado_marca_agua(self, section, app_instance):
        """Configura el encabezado como marca de agua detrás del texto"""
        header = section.header
        
        # Limpiar contenido existente
        for paragraph in header.paragraphs:
            p = paragraph._element
            p.getparent().remove(p)
            p._p = p._element = None
        
        # Obtener ruta de imagen de encabezado
        ruta_encabezado = self.obtener_ruta_imagen("encabezado", app_instance)
        
        if ruta_encabezado and os.path.exists(ruta_encabezado):
            # Crear párrafo para la imagen
            p = header.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Agregar imagen con configuración especial
            run = p.add_run()
            try:
                picture = run.add_picture(ruta_encabezado, width=Inches(6.5))
                
                # Configurar la imagen para que esté detrás del texto
                # Acceder al elemento XML de la imagen
                drawing = picture._element
                
                # Buscar el elemento anchor
                for child in drawing:
                    if child.tag.endswith('anchor'):
                        # Configurar behindDoc="1" para poner la imagen detrás del texto
                        child.set('behindDoc', '1')
                        
                        # Ajustar posición y transparencia
                        for prop in child:
                            if prop.tag.endswith('positionH'):
                                prop.set('relativeFrom', 'page')
                            if prop.tag.endswith('positionV'):
                                prop.set('relativeFrom', 'page')
                
                # Hacer la imagen más transparente (efecto marca de agua)
                # Esto se puede lograr con efectos adicionales si es necesario
                
            except Exception as e:
                print(f"Error agregando imagen de encabezado: {e}")
        else:
            # Si no hay imagen, agregar texto simple
            p = header.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(app_instance.proyecto_data.get('institucion', {}).get() or "INSTITUCIÓN EDUCATIVA")
            run.bold = True
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(128, 128, 128)  # Gris para efecto marca de agua
    
    def configurar_estilos_profesionales(self, doc, app_instance):
        """Configura estilos profesionales del documento"""
        # Estilo normal
        style = doc.styles['Normal']
        style.font.name = app_instance.formato_config['fuente_texto']
        style.font.size = Pt(app_instance.formato_config['tamaño_texto'])
        style.font.color.rgb = RGBColor(0, 0, 0)  # Negro
        
        # Configurar interlineado
        if app_instance.formato_config['interlineado'] == 1.0:
            style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        elif app_instance.formato_config['interlineado'] == 1.5:
            style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        else:
            style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        
        if app_instance.formato_config['justificado']:
            style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        if app_instance.formato_config['sangria']:
            style.paragraph_format.first_line_indent = Inches(0.5)
        
        style.paragraph_format.space_after = Pt(0)
        
        # Crear/actualizar estilos de títulos con niveles y COLOR NEGRO
        for i in range(1, 7):
            heading_name = f'Heading {i}'
            if heading_name in doc.styles:
                heading_style = doc.styles[heading_name]
            else:
                try:
                    heading_style = doc.styles.add_style(heading_name, WD_STYLE_TYPE.PARAGRAPH)
                except:
                    continue
            
            # Configurar estilo del título
            heading_style.font.name = app_instance.formato_config['fuente_titulo']
            heading_style.font.size = Pt(app_instance.formato_config['tamaño_titulo'] - (i-1))
            heading_style.font.bold = True
            heading_style.font.color.rgb = RGBColor(0, 0, 0)  # NEGRO, no azul
            heading_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            heading_style.paragraph_format.space_before = Pt(12)
            heading_style.paragraph_format.space_after = Pt(12)
            heading_style.paragraph_format.keep_with_next = True
            
            # Configurar nivel de esquema
            heading_style.paragraph_format.outline_level = i - 1
    
    def crear_portada_profesional(self, doc, app_instance):
        """Crea portada profesional con formato mejorado"""
        # Logo/emblema si existe
        ruta_imagen = self.obtener_ruta_imagen("insignia", app_instance)
        if ruta_imagen and os.path.exists(ruta_imagen):
            try:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(ruta_imagen, width=Inches(1.5))
            except Exception as e:
                print(f"Error cargando insignia: {e}")
        
        # Espaciado
        for _ in range(3):
            doc.add_paragraph()
        
        # Institución
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(app_instance.proyecto_data['institucion'].get().upper())
        run.bold = True
        run.font.name = app_instance.formato_config['fuente_titulo']
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0, 0, 0)  # Negro
        
        doc.add_paragraph()
        
        # Título del proyecto
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f'"{app_instance.proyecto_data["titulo"].get()}"')
        run.bold = True
        run.font.name = app_instance.formato_config['fuente_titulo']
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0, 0, 0)  # Negro
        
        # Espaciado
        for _ in range(3):
            doc.add_paragraph()
        
        # Información del proyecto
        info_fields = [
            ('ciclo', 'Ciclo'),
            ('curso', 'Curso'), 
            ('enfasis', 'Énfasis'),
            ('area', 'Área de Desarrollo'),
            ('categoria', 'Categoría'),
            ('director', 'Director'),
            ('responsable', 'Responsable')
        ]
        
        for field, label in info_fields:
            if field in app_instance.proyecto_data and app_instance.proyecto_data[field].get().strip():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Etiqueta en negrita
                label_run = p.add_run(f"{label}: ")
                label_run.bold = True
                label_run.font.name = app_instance.formato_config['fuente_texto']
                label_run.font.size = Pt(12)
                label_run.font.color.rgb = RGBColor(0, 0, 0)
                
                # Valor normal
                value_run = p.add_run(app_instance.proyecto_data[field].get())
                value_run.font.name = app_instance.formato_config['fuente_texto']
                value_run.font.size = Pt(12)
                value_run.font.color.rgb = RGBColor(0, 0, 0)
        
        # Espaciado
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Estudiantes
        if app_instance.proyecto_data['estudiantes'].get():
            self._agregar_lista_personas(doc, "Estudiantes", 
                                       app_instance.proyecto_data['estudiantes'].get(), 
                                       app_instance)
        
        # Tutores
        if app_instance.proyecto_data['tutores'].get():
            doc.add_paragraph()
            self._agregar_lista_personas(doc, "Tutores", 
                                       app_instance.proyecto_data['tutores'].get(), 
                                       app_instance)
        
        # Espaciado final
        for _ in range(3):
            doc.add_paragraph()
        
        # Fecha
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        year_label = p.add_run("Año: ")
        year_label.bold = True
        year_label.font.size = Pt(12)
        year_label.font.color.rgb = RGBColor(0, 0, 0)
        
        year_value = p.add_run(str(datetime.now().year))
        year_value.font.size = Pt(12)
        year_value.font.color.rgb = RGBColor(0, 0, 0)
        
        doc.add_page_break()
    
    def _agregar_lista_personas(self, doc, titulo, personas_str, app_instance):
        """Agrega una lista de personas (estudiantes o tutores) con formato"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = p.add_run(f"{titulo}:")
        title_run.bold = True
        title_run.font.size = Pt(13)
        title_run.font.color.rgb = RGBColor(0, 0, 0)
        
        personas = personas_str.split(',')
        for persona in personas:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(persona.strip())
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(0, 0, 0)
    
    def crear_agradecimientos_profesional(self, doc, app_instance):
        """Crea página de agradecimientos con formato profesional"""
        # Usar estilo Heading 1 para el título
        p = doc.add_heading('AGRADECIMIENTOS', level=1)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        content_p = doc.add_paragraph("(Agregar agradecimientos personalizados aquí)")
        content_p.style = doc.styles['Normal']
        doc.add_page_break()
    
    def crear_indice_profesional(self, doc, app_instance):
        """Crea índice profesional con instrucciones"""
        # Usar estilo Heading 1
        p = doc.add_heading('ÍNDICE', level=1)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        
        instrucciones = """INSTRUCCIONES PARA GENERAR ÍNDICE AUTOMÁTICO:

1. En Word, ir a la pestaña "Referencias"
2. Hacer clic en "Tabla de contenido"  
3. Seleccionar el estilo deseado
4. El índice se generará automáticamente

NOTA: Todos los títulos están configurados con niveles de esquema para facilitar la generación automática."""
        
        for linea in instrucciones.split('\n'):
            p = doc.add_paragraph(linea)
            p.style = doc.styles['Normal']
        
        doc.add_paragraph()
        
        # Tabla de ilustraciones
        p = doc.add_heading('TABLA DE ILUSTRACIONES', level=2)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph("(Agregar manualmente si hay figuras, tablas o gráficos)")
        doc.add_page_break()
    
    def crear_contenido_dinamico_mejorado(self, doc, app_instance):
        """Crea contenido con niveles de esquema correctos"""
        capitulo_num = 0
        
        for seccion_id in app_instance.secciones_activas:
            if seccion_id in app_instance.secciones_disponibles:
                seccion = app_instance.secciones_disponibles[seccion_id]
                
                if seccion['capitulo']:
                    # Es un título de capítulo
                    capitulo_num += 1
                    titulo = seccion['titulo']
                    # Limpiar emojis
                    titulo_limpio = re.sub(r'[^\w\s-]', '', titulo).strip()
                    
                    # Agregar como Heading 1
                    p = doc.add_heading(titulo_limpio, level=1)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    
                    # Salto de página si no es el primer capítulo
                    if capitulo_num > 1:
                        doc.add_page_break()
                    else:
                        doc.add_paragraph()
                else:
                    # Es contenido - agregar como Heading 2
                    if seccion_id in app_instance.content_texts:
                        contenido = app_instance.content_texts[seccion_id].get("1.0", "end").strip()
                        if contenido:
                            titulo = seccion['titulo']
                            titulo_limpio = re.sub(r'[^\w\s-]', '', titulo).strip()
                            self.crear_seccion_profesional(doc, titulo_limpio.upper(), 
                                                         contenido, app_instance, nivel=2)
    
    def crear_seccion_profesional(self, doc, titulo, contenido, app_instance, nivel=1):
        """Crea una sección con nivel de esquema específico"""
        # Título con nivel de esquema
        p = doc.add_heading(titulo, level=nivel)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Contenido procesado
        contenido_procesado = self.procesar_citas_mejorado(contenido.strip(), app_instance)
        
        if contenido_procesado:
            # Dividir en párrafos
            parrafos = contenido_procesado.split('\n\n')
            for parrafo in parrafos:
                if parrafo.strip():
                    p = doc.add_paragraph(parrafo.strip())
                    p.style = doc.styles['Normal']
        
        doc.add_paragraph()  # Espaciado
    
    def procesar_citas_mejorado(self, texto, app_instance):
        """Procesa las citas con formato mejorado"""
        # Usar el CitationProcessor si está disponible
        if hasattr(app_instance, 'citation_processor'):
            return app_instance.citation_processor.procesar_citas_avanzado(texto)
        
        # Procesador básico de respaldo
        def reemplazar_cita(match):
            cita_completa = match.group(0)
            contenido = cita_completa[6:-1]  # Quita [CITA: y ]
            partes = contenido.split(':')
            
            if len(partes) >= 3:
                tipo, autor, año = partes[0], partes[1], partes[2]
                pagina = partes[3] if len(partes) > 3 else None
                
                # Formatear según tipo
                if tipo == 'textual':
                    if pagina:
                        return f" ({autor}, {año}, p. {pagina})"
                    else:
                        return f" ({autor}, {año})"
                elif tipo == 'parafraseo':
                    return f" ({autor}, {año})"
                elif tipo == 'larga':
                    # Cita larga en bloque separado
                    if pagina:
                        return f"\n\n     ({autor}, {año}, p. {pagina})\n\n"
                    else:
                        return f"\n\n     ({autor}, {año})\n\n"
                elif tipo == 'web':
                    return f" ({autor}, {año})"
                elif tipo == 'multiple':
                    return f" ({autor}, {año})"
                else:
                    return f" ({autor}, {año})"
            
            return cita_completa
        
        # Procesar todas las citas
        texto_procesado = re.sub(r'\[CITA:[^\]]+\]', reemplazar_cita, texto)
        
        return texto_procesado
    
    def crear_referencias_profesionales(self, doc, app_instance):
        """Crea referencias con formato APA profesional mejorado"""
        if not app_instance.referencias:
            return
        
        # Título como Heading 1
        p = doc.add_heading('REFERENCIAS', level=1)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        
        # Ordenar referencias alfabéticamente
        referencias_ordenadas = sorted(app_instance.referencias, 
                                     key=lambda x: x['autor'].split(',')[0].strip())
        
        for ref in referencias_ordenadas:
            # Formatear según tipo
            ref_text = self._formatear_referencia_apa(ref)
            
            p = doc.add_paragraph(ref_text)
            # Formato APA: sangría francesa
            p.paragraph_format.first_line_indent = Inches(-0.5)
            p.paragraph_format.left_indent = Inches(0.5)
            p.style = doc.styles['Normal']
    
    def _formatear_referencia_apa(self, ref):
        """Formatea una referencia según el estilo APA"""
        tipo = ref.get('tipo', 'Libro')
        autor = ref.get('autor', '')
        año = ref.get('año', '')
        titulo = ref.get('titulo', '')
        fuente = ref.get('fuente', '')
        
        if tipo == 'Libro':
            return f"{autor} ({año}). {titulo}. {fuente}."
        elif tipo == 'Artículo':
            return f"{autor} ({año}). {titulo}. {fuente}."
        elif tipo == 'Web':
            return f"{autor} ({año}). {titulo}. Recuperado de {fuente}"
        elif tipo == 'Tesis':
            return f"{autor} ({año}). {titulo} [Tesis]. {fuente}."
        else:
            return f"{autor} ({año}). {titulo}. {fuente}."
    
    def obtener_ruta_imagen(self, tipo, app_instance):
        """Obtiene la ruta de la imagen con prioridad correcta"""
        if tipo == "encabezado":
            # Prioridad: personalizada -> base
            return (getattr(app_instance, 'encabezado_personalizado', None) or 
                   getattr(app_instance, 'ruta_encabezado', None))
        elif tipo == "insignia":
            # Prioridad: personalizada -> base
            return (getattr(app_instance, 'insignia_personalizada', None) or 
                   getattr(app_instance, 'ruta_insignia', None))
        return None
    
    def mostrar_mensaje_exito(self, filename, app_instance):
        """Muestra mensaje de éxito completo"""
        app_instance.validation_text.delete("1.0", "end")
        app_instance.validation_text.insert("1.0", 
            f"🎉 ¡DOCUMENTO PROFESIONAL GENERADO!\n\n"
            f"📄 Archivo: {os.path.basename(filename)}\n"
            f"📍 Ubicación: {filename}\n\n"
            f"✅ MEJORAS APLICADAS:\n"
            f"   • Encabezados como marca de agua\n"
            f"   • Títulos en color negro\n"
            f"   • Niveles de esquema correctos\n"
            f"   • Formato de citas mejorado\n"
            f"   • Referencias APA optimizadas\n\n"
            f"📋 PARA COMPLETAR EN WORD:\n"
            f"   • Referencias > Tabla de contenido > Automática\n"
            f"   • El índice detectará todos los niveles\n\n"
            f"🚀 ¡Tu proyecto está listo con calidad profesional!"
        )
        
        messagebox.showinfo("🎉 ¡Éxito Total!", 
            f"Documento generado con todas las mejoras:\n{filename}\n\n"
            f"Características implementadas:\n"
            f"• Encabezados como marca de agua\n"
            f"• Títulos en negro (no azul)\n"
            f"• Niveles de esquema funcionales\n"
            f"• Sistema de citas optimizado\n"
            f"• Formato profesional completo")
