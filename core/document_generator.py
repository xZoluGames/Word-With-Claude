"""
Generador de documentos Word - Versión Corregida con Encabezados como Marca de Agua
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.section import WD_SECTION, WD_ORIENTATION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from modules.watermark import WatermarkManager
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
        self.watermark_manager = WatermarkManager()
    
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
        """Configura el encabezado como marca de agua detrás del texto - Versión Corregida"""
        try:
            # IMPORTANTE: Configurar primera página diferente
            section.different_first_page_header_footer = True
            
            # Configurar márgenes de sección
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.5)
            section.left_margin = Cm(3)
            section.right_margin = Cm(3)
            section.header_distance = Cm(1.25)
            section.footer_distance = Cm(1.25)
            
            # Obtener rutas de imágenes
            ruta_encabezado = self.obtener_ruta_imagen("encabezado", app_instance)
            
            # SOLO configurar encabezado para páginas 2+
            # NO agregar nada al encabezado de primera página
            if ruta_encabezado and os.path.exists(ruta_encabezado):
                # Obtener configuración
                opacity = getattr(app_instance, 'watermark_opacity', 0.3)
                stretch = getattr(app_instance, 'watermark_stretch', True)
                mode = getattr(app_instance, 'watermark_mode', 'watermark')
                
                # Trabajar SOLO con el header principal (NO primera página)
                header = section.header  # Este es el header para páginas 2+
                
                # Limpiar header existente
                for para in header.paragraphs:
                    p = para._element
                    p.getparent().remove(p)
                
                # Agregar párrafo para la imagen
                header_para = header.add_paragraph()
                header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Agregar imagen del encabezado
                run = header_para.add_run()
                
                if mode == 'watermark' and hasattr(self, 'watermark_manager'):
                    # Intentar aplicar como marca de agua con configuración correcta
                    try:
                        # Usar dimensiones específicas del watermark_manager
                        header_pic = run.add_picture(ruta_encabezado, width=self.watermark_manager.header_config['width'])
                        
                        # Configurar como marca de agua detrás del texto
                        self.watermark_manager.configurar_imagen_detras_texto(header_pic, self.watermark_manager.header_config)
                        print("✅ Encabezado configurado como marca de agua en páginas 2+")
                        
                    except Exception as e:
                        print(f"⚠️ Error configurando marca de agua, usando imagen simple: {e}")
                        # Si falla, usar método simple
                        self.watermark_manager.add_simple_header_image(section, ruta_encabezado)
                else:
                    # Modo normal - agregar imagen simple con dimensiones correctas
                    header_pic = run.add_picture(ruta_encabezado, width=Cm(20.96))
                    print("✅ Encabezado agregado en modo normal a páginas 2+")
            
            else:
                # Fallback - encabezado de texto simple para páginas 2+
                self._configurar_encabezado_simple(section, app_instance)
            
            # IMPORTANTE: NO agregar nada al first_page_header
            # La insignia se agregará en la portada, NO en el encabezado de primera página
                
        except Exception as e:
            print(f"Error configurando encabezado: {e}")
            # Usar encabezado simple como fallback
            self._configurar_encabezado_simple(section, app_instance)
    
    def _configurar_encabezado_simple(self, section, app_instance):
        """Configura un encabezado de texto simple para páginas 2+ solamente"""
        try:
            # Solo configurar el header principal (páginas 2+)
            header = section.header
            
            # Limpiar header existente
            for para in header.paragraphs:
                p = para._element
                p.getparent().remove(p)
            
            # Agregar texto simple
            p = header.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            institucion = app_instance.proyecto_data.get('institucion', None)
            if institucion and hasattr(institucion, 'get'):
                texto = institucion.get() or "INSTITUCIÓN EDUCATIVA"
            else:
                texto = "INSTITUCIÓN EDUCATIVA"
            
            run = p.add_run(texto.upper())
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.bold = True
            
            print("✅ Encabezado de texto configurado para páginas 2+")
            
        except Exception as e:
            print(f"Error configurando encabezado simple: {e}")
    
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
        
        style.paragraph_format.space_after = Pt(0)
        
        # Crear estilo especial para párrafos con sangría
        try:
            body_style = doc.styles.add_style('BodyTextIndent', WD_STYLE_TYPE.PARAGRAPH)
            body_style.base_style = doc.styles['Normal']
            body_style.font.name = app_instance.formato_config['fuente_texto']
            body_style.font.size = Pt(app_instance.formato_config['tamaño_texto'])
            
            if app_instance.formato_config['sangria']:
                body_style.paragraph_format.first_line_indent = Inches(0.5)
        except:
            if 'BodyTextIndent' in doc.styles:
                body_style = doc.styles['BodyTextIndent']
                body_style.font.name = app_instance.formato_config['fuente_texto']
                body_style.font.size = Pt(app_instance.formato_config['tamaño_texto'])
                
                if app_instance.formato_config['sangria']:
                    body_style.paragraph_format.first_line_indent = Inches(0.5)
        
        # IMPORTANTE: Configurar títulos SIN SANGRÍA
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
            heading_style.font.color.rgb = RGBColor(0, 0, 0)
            heading_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            heading_style.paragraph_format.space_before = Pt(12)
            heading_style.paragraph_format.space_after = Pt(12)
            heading_style.paragraph_format.keep_with_next = True
            heading_style.paragraph_format.outline_level = i - 1
            
            # CRÍTICO: Asegurar que los títulos NO tengan sangría
            heading_style.paragraph_format.first_line_indent = Inches(0)
    
    def crear_portada_profesional(self, doc, app_instance):
        """Crea portada profesional con formato mejorado - SIN duplicar insignia"""
        # Logo/emblema si existe - SOLO UNA VEZ en la portada
        ruta_insignia = self.obtener_ruta_imagen("insignia", app_instance)
        if ruta_insignia and os.path.exists(ruta_insignia):
            try:
                # Usar el watermark_manager para agregar la insignia con dimensiones correctas
                if hasattr(self, 'watermark_manager'):
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.first_line_indent = Inches(0)
                    run = p.add_run()
                    # Usar altura específica del logo_config
                    run.add_picture(ruta_insignia, height=self.watermark_manager.logo_config['height'])
                else:
                    # Fallback al método original
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run()
                    run.add_picture(ruta_insignia, width=Inches(1.5))
                
                print("✅ Insignia agregada a la portada")
                
            except Exception as e:
                print(f"Error cargando insignia: {e}")
        
        # Institución - CENTRADA
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        run = p.add_run(app_instance.proyecto_data['institucion'].get().upper())
        run.bold = True
        run.font.name = app_instance.formato_config['fuente_titulo']
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0, 0, 0)
        
        
        # Título del proyecto - CENTRADO
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        run = p.add_run(f'"{app_instance.proyecto_data["titulo"].get()}"')
        run.bold = True
        run.font.name = app_instance.formato_config['fuente_titulo']
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0, 0, 0)
        
        
        # Información del proyecto - ALINEADO A LA IZQUIERDA
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
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Etiqueta en negrita
                label_run = p.add_run(f"{label}: ")
                label_run.bold = True
                label_run.font.name = app_instance.formato_config['fuente_texto']
                label_run.font.size = Pt(14)
                label_run.font.color.rgb = RGBColor(0, 0, 0)
                
                # 🟢 NUEVO: Procesar valor con formato especial para Responsable
                valor_original = app_instance.proyecto_data[field].get()
                
                if field == 'responsable' and ',' in valor_original:
                    # Procesar lista de responsables igual que estudiantes/tutores
                    responsables = [resp.strip() for resp in valor_original.split(',')]
                    
                    if len(responsables) == 1:
                        valor_formateado = responsables[0]
                    elif len(responsables) == 2:
                        valor_formateado = f"{responsables[0]} y {responsables[1]}"
                    else:
                        todos_menos_ultimo = ", ".join(responsables[:-1])
                        valor_formateado = f"{todos_menos_ultimo} y {responsables[-1]}"
                    
                    value_run = p.add_run(valor_formateado)
                else:
                    # Para otros campos, usar el valor tal cual
                    value_run = p.add_run(valor_original)
                
                value_run.font.name = app_instance.formato_config['fuente_texto']
                value_run.font.size = Pt(12)
                value_run.font.color.rgb = RGBColor(0, 0, 0)
        
        
        # Estudiantes - SIN ESPACIOS
        if app_instance.proyecto_data['estudiantes'].get():
            self._agregar_lista_personas(doc, "Estudiantes", 
                                    app_instance.proyecto_data['estudiantes'].get(), 
                                    app_instance, alineacion='izquierda')
        
        # Tutores - SIN ESPACIOS
        if app_instance.proyecto_data['tutores'].get():
            # ❌ ELIMINADO: doc.add_paragraph()
            self._agregar_lista_personas(doc, "Tutores", 
                                    app_instance.proyecto_data['tutores'].get(), 
                                    app_instance, alineacion='izquierda')
        
        # ❌ ELIMINADO: Espaciado final antes de la fecha
        # for _ in range(3):
        #     doc.add_paragraph()
        
        # Fecha - CENTRADA
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER  # ✅ AÑO PERMANECE CENTRADO
        year_label = p.add_run("Año: ")
        year_label.bold = True
        year_label.font.name = app_instance.formato_config['fuente_texto']
        year_label.font.size = Pt(14)
        year_label.font.color.rgb = RGBColor(0, 0, 0)
        
        year_value = p.add_run(str(datetime.now().year))
        year_value.font.name = app_instance.formato_config['fuente_texto']
        year_value.font.size = Pt(12)
        year_value.font.color.rgb = RGBColor(0, 0, 0)
        
        doc.add_page_break()

    def _agregar_lista_personas(self, doc, titulo, personas_str, app_instance, alineacion='centro'):
        """Agrega una lista de personas (estudiantes o tutores) con formato EN UNA SOLA LÍNEA"""
        p = doc.add_paragraph()
        
        # Configurar alineación
        if alineacion == 'izquierda':
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Título en negrita (Estudiantes: o Tutores:) con ESPACIO después
        title_run = p.add_run(f"{titulo}: ")  # ← ✅ YA tiene espacio después de ":"
        title_run.bold = True
        title_run.font.name = app_instance.formato_config['fuente_texto']
        title_run.font.size = Pt(14)
        title_run.font.color.rgb = RGBColor(0, 0, 0)
        
        # 🟢 NUEVO: Procesar y normalizar la lista de personas
        # Dividir por comas y limpiar espacios de cada nombre
        personas = []
        for persona in personas_str.split(','):
            # Limpiar espacios al inicio y final de cada nombre
            persona_limpia = persona.strip()
            if persona_limpia:  # Solo agregar si no está vacío
                personas.append(persona_limpia)
        
        # 🟢 MEJORADO: Formatear la lista con comas y "y"
        if len(personas) == 0:
            # No hay personas
            personas_run = p.add_run("")
        elif len(personas) == 1:
            # Solo una persona: "Juan"
            personas_run = p.add_run(personas[0])
        elif len(personas) == 2:
            # Dos personas: "Juan y María"
            personas_run = p.add_run(f"{personas[0]} y {personas[1]}")
        else:
            # Tres o más personas: "Juan, María y Pedro"
            # Unir todos menos el último con comas y espacio
            todos_menos_ultimo = ", ".join(personas[:-1])
            # Agregar " y " antes del último
            personas_run = p.add_run(f"{todos_menos_ultimo} y {personas[-1]}")
        
        # Aplicar formato al texto de las personas
        personas_run.font.name = app_instance.formato_config['fuente_texto']
        personas_run.font.size = Pt(12)
        personas_run.font.color.rgb = RGBColor(0, 0, 0)
    
    def crear_agradecimientos_profesional(self, doc, app_instance):
        """Crea página de agradecimientos con formato profesional y sangría"""
        # Título sin sangría
        p = doc.add_heading('AGRADECIMIENTOS', level=1)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)  # Sin sangría
        
        doc.add_paragraph()
        
        # Párrafo de contenido - CON sangría
        content_p = doc.add_paragraph("(Agregar agradecimientos personalizados aquí)")
        
        # Aplicar sangría si está configurada
        if app_instance.formato_config.get('sangria', True):
            if 'BodyTextIndent' in doc.styles:
                content_p.style = doc.styles['BodyTextIndent']
            else:
                content_p.paragraph_format.first_line_indent = Inches(0.5)
        
        doc.add_page_break()
    
    def crear_indice_profesional(self, doc, app_instance):
        """Crea índice profesional con instrucciones"""
        # Título sin sangría
        p = doc.add_heading('ÍNDICE', level=1)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)  # Sin sangría
        
        doc.add_paragraph()
        
        instrucciones = """INSTRUCCIONES PARA GENERAR ÍNDICE AUTOMÁTICO:

    1. En Word, ir a la pestaña "Referencias"
    2. Hacer clic en "Tabla de contenido"  
    3. Seleccionar el estilo deseado
    4. El índice se generará automáticamente

    NOTA: Todos los títulos están configurados con niveles de esquema para facilitar la generación automática."""
        
        for linea in instrucciones.split('\n'):
            p = doc.add_paragraph(linea)
            # Sin sangría para instrucciones del índice
            p.paragraph_format.first_line_indent = Inches(0)
        
        doc.add_paragraph()
        
        # Tabla de ilustraciones
        p = doc.add_heading('TABLA DE ILUSTRACIONES', level=2)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)  # Sin sangría
        
        p = doc.add_paragraph("(Agregar manualmente si hay figuras, tablas o gráficos)")
        p.paragraph_format.first_line_indent = Inches(0)  # Sin sangría
        
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
                    # ASEGURAR sin sangría
                    p.paragraph_format.first_line_indent = Inches(0)
                    
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
        """Crea una sección con nivel de esquema específico y sangría correcta"""
        
        # Título con nivel de esquema (SIN sangría)
        p = doc.add_heading(titulo, level=nivel)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # ASEGURAR que el título NO tenga sangría
        p.paragraph_format.first_line_indent = Inches(0)
        
        # Contenido procesado
        contenido_procesado = self.procesar_citas_mejorado(contenido.strip(), app_instance)
        
        if contenido_procesado:
            # Dividir en párrafos
            parrafos = contenido_procesado.split('\n\n')
            
            for i, parrafo in enumerate(parrafos):
                if parrafo.strip():
                    # Crear párrafo
                    p = doc.add_paragraph(parrafo.strip())
                    
                    # Detectar tipo de párrafo
                    es_cita_bloque = (
                        len(parrafo.split()) > 40 or 
                        parrafo.strip().startswith('\t') or
                        parrafo.strip().startswith('     ')
                    )
                    
                    es_lista = any(parrafo.strip().startswith(marca) for marca in ['•', '-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.'])
                    
                    # APLICAR FORMATO SEGÚN TIPO
                    if es_cita_bloque:
                        # Citas en bloque: sin sangría primera línea, con margen izquierdo
                        p.paragraph_format.first_line_indent = Inches(0)
                        p.paragraph_format.left_indent = Inches(0.5)
                        p.paragraph_format.right_indent = Inches(0.5)
                    elif es_lista:
                        # Listas: sin sangría primera línea
                        p.paragraph_format.first_line_indent = Inches(0)
                        p.paragraph_format.left_indent = Inches(0.5)
                    else:
                        # PÁRRAFOS NORMALES: APLICAR SANGRÍA SI ESTÁ CONFIGURADA
                        if app_instance.formato_config.get('sangria', True):
                            # CAMBIO CLAVE: Usar el estilo con sangría
                            if 'BodyTextIndent' in doc.styles:
                                p.style = doc.styles['BodyTextIndent']
                            else:
                                # Si no existe el estilo, aplicar directamente
                                p.paragraph_format.first_line_indent = Inches(0.5)
        
        # Espaciado después de la sección
        doc.add_paragraph()
    
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
        
        # Título sin sangría
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
            # Formato APA: sangría francesa (NO primera línea)
            p.paragraph_format.first_line_indent = Inches(-0.5)
            p.paragraph_format.left_indent = Inches(0.5)
            # NO usar el estilo con sangría primera línea
            p.style = doc.styles['Normal']
    def aplicar_formato_parrafo(self, paragraph, app_instance, tipo='normal'):
        """Aplica formato de párrafo según el tipo y normas APA"""
        if tipo == 'portada':
            # Portada: sin sangría
            paragraph.paragraph_format.first_line_indent = Inches(0)
        elif tipo == 'titulo':
            # Títulos: sin sangría, centrados
            paragraph.paragraph_format.first_line_indent = Inches(0)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif tipo == 'cita_bloque':
            # Citas en bloque: sin sangría primera línea, con margen izquierdo
            paragraph.paragraph_format.first_line_indent = Inches(0)
            paragraph.paragraph_format.left_indent = Inches(0.5)
        elif tipo == 'referencia':
            # Referencias: sangría francesa
            paragraph.paragraph_format.first_line_indent = Inches(-0.5)
            paragraph.paragraph_format.left_indent = Inches(0.5)
        elif tipo == 'normal' and app_instance.formato_config.get('sangria', True):
            # Párrafos normales del cuerpo: con sangría primera línea
            paragraph.paragraph_format.first_line_indent = Inches(0.5)
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