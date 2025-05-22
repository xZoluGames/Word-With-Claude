"""
Generador de documentos profesionales para el Proyecto Académico Generator
Maneja la creación de documentos Word con formato APA y estructura profesional
"""

import re
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE

class DocumentGenerator:
    """Genera documentos Word profesionales con formato APA"""
    
    def __init__(self, app):
        self.app = app
    
    def generate_document(self, project_data):
        """Genera el documento completo"""
        try:
            # Crear documento
            doc = Document()
            
            # Configurar estilos profesionales
            self.configurar_estilos_profesionales(doc)
            
            # Generar contenido según estructura
            self.crear_portada_profesional(doc, project_data)
            self.crear_contenido_principal(doc, project_data)
            self.crear_referencias_profesionales(doc, project_data)
            
            # Guardar documento
            return self.guardar_documento(doc)
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al generar documento:\n{str(e)}")
            return False
    
    def configurar_estilos_profesionales(self, doc):
        """Configura estilos profesionales para el documento"""
        formato_config = self.app.formato_config
        
        # Configurar estilo Normal
        normal_style = doc.styles['Normal']
        normal_style.font.name = formato_config.get('fuente_texto', 'Times New Roman')
        normal_style.font.size = Pt(formato_config.get('tamaño_texto', 12))
        
        # Configurar interlineado
        interlineado = formato_config.get('interlineado', 2.0)
        if interlineado == 1.0:
            normal_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        elif interlineado == 1.5:
            normal_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        else:
            normal_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        
        # Configurar alineación
        if formato_config.get('justificado', True):
            normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Configurar sangría
        if formato_config.get('sangria', True):
            normal_style.paragraph_format.first_line_indent = Inches(0.5)
        
        normal_style.paragraph_format.space_after = Pt(0)
        
        # Crear estilo para títulos profesionales
        try:
            titulo_style = doc.styles.add_style('Titulo Profesional', WD_STYLE_TYPE.PARAGRAPH)
        except:
            titulo_style = doc.styles['Heading 1']
        
        titulo_style.font.name = formato_config.get('fuente_titulo', 'Times New Roman')
        titulo_style.font.size = Pt(formato_config.get('tamaño_titulo', 14))
        titulo_style.font.bold = True
        titulo_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        titulo_style.paragraph_format.space_before = Pt(12)
        titulo_style.paragraph_format.space_after = Pt(12)
        
        # Configurar para índice automático
        titulo_style.paragraph_format.outline_level = 0
        
        if formato_config.get('conservar_siguiente', True):
            titulo_style.paragraph_format.keep_with_next = True
        
        # Configurar márgenes del documento
        sections = doc.sections
        for section in sections:
            margen_cm = formato_config.get('margen', 2.54)
            margen_inches = margen_cm / 2.54
            section.top_margin = Inches(margen_inches)
            section.bottom_margin = Inches(margen_inches)
            section.left_margin = Inches(margen_inches)
            section.right_margin = Inches(margen_inches)
    
    def crear_portada_profesional(self, doc, project_data):
        """Crea portada profesional con imágenes"""
        proyecto_info = project_data.get('proyecto_data', {})
        
        # Agregar imagen de encabezado si existe
        self.agregar_imagen_encabezado(doc)
        
        # Espaciado inicial
        doc.add_paragraph()
        
        # Institución
        if 'institucion' in proyecto_info and proyecto_info['institucion']:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(proyecto_info['institucion'].upper())
            run.bold = True
            run.font.name = self.app.formato_config.get('fuente_titulo', 'Times New Roman')
            run.font.size = Pt(self.app.formato_config.get('tamaño_titulo', 14) + 2)
        
        doc.add_paragraph()
        
        # Título del proyecto
        if 'titulo' in proyecto_info and proyecto_info['titulo']:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(f'"{proyecto_info["titulo"]}"')
            run.bold = True
            run.font.name = self.app.formato_config.get('fuente_titulo', 'Times New Roman')
            run.font.size = Pt(self.app.formato_config.get('tamaño_titulo', 14) + 4)
        
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Información del proyecto
        campos_info = [
            ('ciclo', 'Ciclo'),
            ('curso', 'Curso'),
            ('enfasis', 'Énfasis'),
            ('area', 'Área de Desarrollo'),
            ('categoria', 'Categoría'),
            ('director', 'Director'),
            ('responsable', 'Responsable')
        ]
        
        for campo, etiqueta in campos_info:
            if campo in proyecto_info and proyecto_info[campo]:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(f"{etiqueta}: {proyecto_info[campo]}")
                run.font.name = self.app.formato_config.get('fuente_texto', 'Times New Roman')
        
        doc.add_paragraph()
        
        # Estudiantes
        if 'estudiantes' in proyecto_info and proyecto_info['estudiantes']:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run("Estudiantes:").bold = True
            
            estudiantes = proyecto_info['estudiantes'].split(',')
            for estudiante in estudiantes:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run(estudiante.strip())
        
        # Tutores
        if 'tutores' in proyecto_info and proyecto_info['tutores']:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run("Tutores:").bold = True
            
            tutores = proyecto_info['tutores'].split(',')
            for tutor in tutores:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run(tutor.strip())
        
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Fecha
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(f"Año: {datetime.now().year}")
        
        # Agregar imagen de insignia si existe
        self.agregar_imagen_insignia(doc)
        
        doc.add_page_break()
    
    def agregar_imagen_encabezado(self, doc):
        """Agrega imagen de encabezado si está disponible"""
        try:
            imagen_path = self.obtener_ruta_imagen('encabezado')
            if imagen_path and os.path.exists(imagen_path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(imagen_path, width=Inches(6))
        except Exception as e:
            print(f"Error agregando encabezado: {e}")
    
    def agregar_imagen_insignia(self, doc):
        """Agrega imagen de insignia si está disponible"""
        try:
            imagen_path = self.obtener_ruta_imagen('insignia')
            if imagen_path and os.path.exists(imagen_path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(imagen_path, width=Inches(2))
        except Exception as e:
            print(f"Error agregando insignia: {e}")
    
    def obtener_ruta_imagen(self, tipo):
        """Obtiene la ruta de la imagen a usar (personalizada o base)"""
        if tipo == "encabezado":
            return self.app.encabezado_personalizado or self.app.ruta_encabezado
        elif tipo == "insignia":
            return self.app.insignia_personalizada or self.app.ruta_insignia
        return None
    
    def crear_contenido_principal(self, doc, project_data):
        """Crea el contenido principal del documento"""
        # Agregar índice placeholder
        self.crear_indice_placeholder(doc)
        
        # Crear secciones dinámicamente
        secciones_activas = project_data.get('secciones_activas', [])
        secciones_disponibles = project_data.get('secciones_disponibles', {})
        
        for seccion_id in secciones_activas:
            if seccion_id in secciones_disponibles:
                seccion = secciones_disponibles[seccion_id]
                
                if seccion.get('capitulo', False):
                    # Es un título de capítulo
                    self.crear_titulo_capitulo(doc, seccion)
                else:
                    # Es contenido
                    contenido = self.obtener_contenido_seccion(seccion_id)
                    if contenido:
                        self.crear_seccion_profesional(doc, seccion, contenido)
    
    def crear_indice_placeholder(self, doc):
        """Crea placeholder para el índice"""
        p = doc.add_paragraph()
        p.style = doc.styles['Titulo Profesional']
        run = p.add_run("ÍNDICE")
        run.bold = True
        
        # Configurar como sección de nivel 1
        p.paragraph_format.outline_level = 0
        if self.app.formato_config.get('salto_pagina_secciones', True):
            p.paragraph_format.page_break_before = True
        
        doc.add_paragraph()
        
        instrucciones = """INSTRUCCIONES PARA GENERAR ÍNDICE AUTOMÁTICO:

1. En Word, ir a la pestaña "Referencias"
2. Hacer clic en "Tabla de contenido" 
3. Seleccionar "Automática" o "Personalizada"
4. El índice se generará automáticamente

NOTA: Todas las secciones están configuradas con niveles de esquema apropiados."""
        
        content_p = doc.add_paragraph(instrucciones)
        content_p.style = doc.styles['Normal']
        
        doc.add_page_break()
    
    def crear_titulo_capitulo(self, doc, seccion):
        """Crea título de capítulo"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Limpiar título de emojis para el documento
        titulo_limpio = self.limpiar_titulo(seccion['titulo'])
        run = p.add_run(titulo_limpio.upper())
        run.bold = True
        run.font.name = self.app.formato_config.get('fuente_titulo', 'Times New Roman')
        run.font.size = Pt(self.app.formato_config.get('tamaño_titulo', 14))
        
        # Configurar para índice
        p.paragraph_format.outline_level = 0
        if self.app.formato_config.get('salto_pagina_secciones', True):
            p.paragraph_format.page_break_before = True
        
        doc.add_paragraph()
    
    def crear_seccion_profesional(self, doc, seccion, contenido):
        """Crea una sección profesional con formato APA"""
        # Título de la sección
        p = doc.add_paragraph()
        p.style = doc.styles['Titulo Profesional']
        
        titulo_limpio = self.limpiar_titulo(seccion['titulo'])
        run = p.add_run(titulo_limpio.upper())
        run.bold = True
        
        # Configurar como sección de nivel 1
        p.paragraph_format.outline_level = 0
        if self.app.formato_config.get('salto_pagina_secciones', True):
            p.paragraph_format.page_break_before = True
        
        # Contenido procesado
        contenido_procesado = self.procesar_citas(contenido.strip())
        if contenido_procesado:
            content_p = doc.add_paragraph(contenido_procesado)
            content_p.style = doc.styles['Normal']
        
        doc.add_paragraph()  # Espaciado
    
    def obtener_contenido_seccion(self, seccion_id):
        """Obtiene el contenido de una sección"""
        if seccion_id in self.app.content_texts:
            return self.app.content_texts[seccion_id].get("1.0", "end").strip()
        return ""
    
    def limpiar_titulo(self, titulo):
        """Limpia emojis y caracteres especiales del título"""
        # Remover emojis comunes
        titulo_limpio = re.sub(r'[📄📚📖🔍❓❔💡🎯⚙️📊💬✅🔬🛠️💬]', '', titulo)
        # Limpiar espacios extra
        titulo_limpio = ' '.join(titulo_limpio.split())
        return titulo_limpio.strip()
    
    def procesar_citas(self, texto):
        """Procesa las citas en el texto y las convierte a formato APA"""
        def reemplazar_cita(match):
            cita_completa = match.group(0)
            contenido = cita_completa[6:-1]  # Quita [CITA: y ]
            partes = contenido.split(':')
            
            if len(partes) >= 3:
                tipo, autor, año = partes[0], partes[1], partes[2]
                pagina = partes[3] if len(partes) > 3 else None
                
                if tipo == 'textual':
                    return f" ({autor}, {año}, p. {pagina})" if pagina else f" ({autor}, {año})"
                elif tipo == 'parafraseo':
                    return f" ({autor}, {año})"
                elif tipo == 'larga':
                    cita_texto = f"\n\n({autor}, {año}"
                    if pagina:
                        cita_texto += f", p. {pagina}"
                    cita_texto += ")\n\n"
                    return cita_texto
                elif tipo == 'web':
                    return f" ({autor}, {año})"
                elif tipo == 'multiple':
                    return f" ({autor}, {año})"
            
            return cita_completa
        
        return re.sub(r'\[CITA:[^\]]+\]', reemplazar_cita, texto)
    
    def crear_referencias_profesionales(self, doc, project_data):
        """Crea sección de referencias con formato APA"""
        referencias = project_data.get('referencias', [])
        
        if not referencias:
            return
        
        # Título de referencias
        p = doc.add_paragraph()
        p.style = doc.styles['Titulo Profesional']
        run = p.add_run("REFERENCIAS")
        run.bold = True
        
        # Configurar como sección de nivel 1
        p.paragraph_format.outline_level = 0
        if self.app.formato_config.get('salto_pagina_secciones', True):
            p.paragraph_format.page_break_before = True
        
        doc.add_paragraph()
        
        # Ordenar referencias alfabéticamente por autor
        referencias_ordenadas = sorted(referencias, key=lambda x: x.get('autor', ''))
        
        # Crear cada referencia con formato APA
        for ref in referencias_ordenadas:
            ref_text = self.formatear_referencia_apa(ref)
            p = doc.add_paragraph(ref_text)
            
            # Aplicar sangría francesa (hanging indent)
            p.paragraph_format.first_line_indent = Inches(-0.5)
            p.paragraph_format.left_indent = Inches(0.5)
            p.style = doc.styles['Normal']
    
    def formatear_referencia_apa(self, referencia):
        """Formatea una referencia según estilo APA"""
        autor = referencia.get('autor', 'Autor desconocido')
        año = referencia.get('año', 'Sin fecha')
        titulo = referencia.get('titulo', 'Sin título')
        fuente = referencia.get('fuente', 'Sin fuente')
        tipo = referencia.get('tipo', 'Libro')
        
        # Formato básico APA
        if tipo == 'Libro':
            return f"{autor} ({año}). {titulo}. {fuente}."
        elif tipo == 'Artículo':
            return f"{autor} ({año}). {titulo}. {fuente}."
        elif tipo == 'Web':
            return f"{autor} ({año}). {titulo}. Recuperado de {fuente}"
        elif tipo == 'Tesis':
            return f"{autor} ({año}). {titulo} (Tesis). {fuente}."
        else:
            return f"{autor} ({año}). {titulo}. {fuente}."
    
    def guardar_documento(self, doc):
        """Guarda el documento con diálogo"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word documents", "*.docx")],
                title="Guardar Proyecto Académico"
            )
            
            if filename:
                doc.save(filename)
                
                messagebox.showinfo(
                    "🎉 ¡Documento Generado!",
                    f"Documento creado exitosamente:\n{filename}\n\n"
                    f"Características aplicadas:\n"
                    f"• Formato profesional con niveles de esquema\n"
                    f"• Saltos de página automáticos\n"
                    f"• Control de líneas profesional\n"
                    f"• Referencias APA automáticas\n\n"
                    f"Para generar el índice automático:\n"
                    f"Referencias > Tabla de contenido > Automática"
                )
                return True
            
            return False
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar documento:\n{str(e)}")
            return False