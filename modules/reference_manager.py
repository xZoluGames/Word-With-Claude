"""
Gestor de referencias y citas para el Generador de Proyectos Académicos
Maneja el sistema completo de citas APA y referencias bibliográficas
"""

import re
import json
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime

class ReferenceManager:
    """Gestiona citas y referencias bibliográficas con formato APA"""
    
    def __init__(self, app):
        self.app = app
        self.tipos_cita = {
            'textual': 'Cita textual (menos de 40 palabras)',
            'larga': 'Cita textual larga (más de 40 palabras)', 
            'parafraseo': 'Parafraseo de ideas',
            'web': 'Fuente web o digital',
            'multiple': 'Múltiples autores'
        }
        
        self.tipos_referencia = {
            'Libro': 'Libro impreso o digital',
            'Artículo': 'Artículo de revista científica',
            'Web': 'Página web o artículo online',
            'Tesis': 'Tesis o disertación',
            'Informe': 'Informe técnico o institucional',
            'Conferencia': 'Ponencia o presentación'
        }
    
    def agregar_referencia_completa(self, datos_referencia):
        """Agrega una referencia con validación completa"""
        try:
            # Validar datos obligatorios
            campos_requeridos = ['autor', 'año', 'titulo']
            for campo in campos_requeridos:
                if not datos_referencia.get(campo, '').strip():
                    raise ValueError(f"El campo '{campo}' es obligatorio")
            
            # Limpiar y normalizar datos
            referencia_limpia = self.limpiar_datos_referencia(datos_referencia)
            
            # Generar ID único
            referencia_limpia['id'] = self.generar_id_referencia(referencia_limpia)
            
            # Verificar duplicados
            if self.es_referencia_duplicada(referencia_limpia):
                respuesta = messagebox.askyesno(
                    "⚠️ Posible Duplicado",
                    f"Ya existe una referencia similar de {referencia_limpia['autor']} ({referencia_limpia['año']}).\n\n"
                    "¿Agregar de todas formas?"
                )
                if not respuesta:
                    return False
            
            # Agregar a la lista
            self.app.referencias.append(referencia_limpia)
            
            # Actualizar interfaz si existe
            if hasattr(self.app, 'actualizar_lista_referencias'):
                self.app.actualizar_lista_referencias()
            
            return True
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al agregar referencia:\n{str(e)}")
            return False
    
    def limpiar_datos_referencia(self, datos):
        """Limpia y normaliza los datos de una referencia"""
        referencia = {}
        
        # Limpiar autor
        autor = datos.get('autor', '').strip()
        if ',' not in autor and ' ' in autor:
            # Convertir "Nombre Apellido" a "Apellido, N."
            partes = autor.split()
            apellido = partes[-1]
            iniciales = '. '.join([p[0].upper() for p in partes[:-1]]) + '.'
            autor = f"{apellido}, {iniciales}"
        referencia['autor'] = autor
        
        # Limpiar año
        año = str(datos.get('año', '')).strip()
        if año.isdigit() and len(año) == 4:
            referencia['año'] = año
        else:
            referencia['año'] = 'Sin fecha'
        
        # Limpiar título
        titulo = datos.get('titulo', '').strip()
        if titulo and not titulo.endswith('.'):
            titulo += '.'
        referencia['titulo'] = titulo
        
        # Limpiar fuente
        referencia['fuente'] = datos.get('fuente', '').strip()
        
        # Tipo de referencia
        referencia['tipo'] = datos.get('tipo', 'Libro')
        
        # Campos adicionales
        referencia['paginas'] = datos.get('paginas', '')
        referencia['doi'] = datos.get('doi', '')
        referencia['url'] = datos.get('url', '')
        referencia['fecha_acceso'] = datos.get('fecha_acceso', '')
        
        return referencia
    
    def generar_id_referencia(self, referencia):
        """Genera un ID único para la referencia"""
        base = f"{referencia['autor'][:10]}_{referencia['año']}"
        base = re.sub(r'[^\w]', '_', base).lower()
        
        # Verificar unicidad
        contador = 1
        id_propuesto = base
        while any(ref.get('id') == id_propuesto for ref in self.app.referencias):
            id_propuesto = f"{base}_{contador}"
            contador += 1
        
        return id_propuesto
    
    def es_referencia_duplicada(self, nueva_referencia):
        """Verifica si una referencia ya existe"""
        for ref_existente in self.app.referencias:
            if (ref_existente['autor'].lower() == nueva_referencia['autor'].lower() and
                ref_existente['año'] == nueva_referencia['año'] and
                ref_existente['titulo'].lower() == nueva_referencia['titulo'].lower()):
                return True
        return False
    
    def formatear_referencia_apa(self, referencia):
        """Formatea una referencia según normas APA 7ma edición"""
        autor = referencia.get('autor', 'Autor desconocido')
        año = referencia.get('año', 'Sin fecha')
        titulo = referencia.get('titulo', 'Sin título')
        fuente = referencia.get('fuente', 'Sin fuente')
        tipo = referencia.get('tipo', 'Libro')
        
        # Formateo según tipo
        if tipo == 'Libro':
            return f"{autor} ({año}). {titulo} {fuente}."
            
        elif tipo == 'Artículo':
            return f"{autor} ({año}). {titulo} {fuente}."
            
        elif tipo == 'Web':
            url = referencia.get('url', fuente)
            fecha_acceso = referencia.get('fecha_acceso', '')
            if fecha_acceso:
                return f"{autor} ({año}). {titulo} Recuperado el {fecha_acceso} de {url}"
            else:
                return f"{autor} ({año}). {titulo} Recuperado de {url}"
                
        elif tipo == 'Tesis':
            return f"{autor} ({año}). {titulo} [Tesis]. {fuente}."
            
        elif tipo == 'Informe':
            return f"{autor} ({año}). {titulo} {fuente}."
            
        elif tipo == 'Conferencia':
            return f"{autor} ({año}). {titulo} En {fuente}."
            
        else:
            return f"{autor} ({año}). {titulo} {fuente}."
    
    def procesar_citas_en_texto(self, texto):
        """Procesa todas las citas en un texto y las convierte a formato APA"""
        def reemplazar_cita(match):
            cita_completa = match.group(0)
            try:
                # Extraer contenido de la cita
                contenido = cita_completa[6:-1]  # Quita [CITA: y ]
                partes = contenido.split(':')
                
                if len(partes) < 3:
                    return cita_completa  # Devolver sin cambios si formato incorrecto
                
                tipo = partes[0].strip()
                autor = partes[1].strip()
                año = partes[2].strip()
                pagina = partes[3].strip() if len(partes) > 3 else None
                
                # Formatear según tipo
                if tipo == 'textual':
                    if pagina:
                        return f" ({autor}, {año}, p. {pagina})"
                    else:
                        return f" ({autor}, {año})"
                        
                elif tipo == 'parafraseo':
                    return f" ({autor}, {año})"
                    
                elif tipo == 'larga':
                    cita_texto = f"\n\n\t({autor}, {año}"
                    if pagina:
                        cita_texto += f", p. {pagina}"
                    cita_texto += ")\n\n"
                    return cita_texto
                    
                elif tipo == 'web':
                    return f" ({autor}, {año})"
                    
                elif tipo == 'multiple':
                    # Manejar múltiples autores
                    autores = autor.split(' y ')
                    if len(autores) == 2:
                        return f" ({autores[0]} y {autores[1]}, {año})"
                    elif len(autores) > 2:
                        return f" ({autores[0]} et al., {año})"
                    else:
                        return f" ({autor}, {año})"
                
                else:
                    return f" ({autor}, {año})"
                    
            except Exception as e:
                print(f"Error procesando cita: {e}")
                return cita_completa
        
        # Buscar y reemplazar todas las citas
        patron_cita = r'\[CITA:[^\]]+\]'
        texto_procesado = re.sub(patron_cita, reemplazar_cita, texto)
        
        return texto_procesado
    
    def crear_interfaz_citas_avanzada(self, parent_frame):
        """Crea interfaz avanzada para gestión de citas"""
        # Frame principal para citas
        citas_frame = ctk.CTkFrame(parent_frame, fg_color="gray15", corner_radius=10)
        citas_frame.pack(fill="x", pady=(0, 15))
        
        # Título
        title_label = ctk.CTkLabel(
            citas_frame, text="🚀 SISTEMA AVANZADO DE CITAS APA",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="lightgreen"
        )
        title_label.pack(pady=(15, 10))
        
        # Instrucciones con ejemplos
        instruc_text = """📝 FORMATOS DE CITAS DISPONIBLES:

🔹 Textual corta: [CITA:textual:García:2020:45] → (García, 2020, p. 45)
🔹 Parafraseo: [CITA:parafraseo:López:2019] → (López, 2019)  
🔹 Textual larga: [CITA:larga:Martínez:2021:67] → Formato de bloque
🔹 Fuente web: [CITA:web:OMS:2023] → (OMS, 2023)
🔹 Múltiples autores: [CITA:multiple:García y López:2020] → (García y López, 2020)"""
        
        instruc_label = ctk.CTkLabel(
            citas_frame, text=instruc_text,
            font=ctk.CTkFont(size=11), text_color="lightblue", 
            wraplength=900, justify="left"
        )
        instruc_label.pack(padx=15, pady=(0, 10))
        
        # Herramientas de citas
        tools_frame = ctk.CTkFrame(citas_frame, fg_color="transparent")
        tools_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Botón para generar cita rápida
        quick_cite_btn = ctk.CTkButton(
            tools_frame, text="⚡ Generar Cita Rápida",
            command=self.generar_cita_rapida,
            width=150, height=30
        )
        quick_cite_btn.pack(side="left", padx=(0, 10))
        
        # Botón para validar citas en texto
        validate_cite_btn = ctk.CTkButton(
            tools_frame, text="🔍 Validar Citas",
            command=self.validar_citas_en_proyecto,
            width=150, height=30, fg_color="orange", hover_color="darkorange"
        )
        validate_cite_btn.pack(side="right", padx=(10, 0))
    
    def generar_cita_rapida(self):
        """Abre diálogo para generar cita rápida"""
        dialog = CitaRapidaDialog(self.app.root, self)
        if dialog.result:
            # Copiar al portapapeles
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(dialog.result)
            messagebox.showinfo("✅ Cita Generada", 
                f"Cita copiada al portapapeles:\n{dialog.result}")
    
    def validar_citas_en_proyecto(self):
        """Valida todas las citas en el proyecto"""
        citas_encontradas = []
        citas_problematicas = []
        
        # Buscar citas en todas las secciones
        for seccion_id, text_widget in self.app.content_texts.items():
            if seccion_id in self.app.secciones_disponibles:
                contenido = text_widget.get("1.0", "end")
                citas_seccion = re.findall(r'\[CITA:[^\]]+\]', contenido)
                
                for cita in citas_seccion:
                    citas_encontradas.append({
                        'seccion': self.app.secciones_disponibles[seccion_id]['titulo'],
                        'cita': cita,
                        'valida': self.validar_formato_cita(cita)
                    })
                    
                    if not self.validar_formato_cita(cita):
                        citas_problematicas.append(cita)
        
        # Mostrar resultados
        self.mostrar_resultados_validacion(citas_encontradas, citas_problematicas)
    
    def validar_formato_cita(self, cita):
        """Valida el formato de una cita individual"""
        try:
            # Verificar estructura básica
            if not cita.startswith('[CITA:') or not cita.endswith(']'):
                return False
            
            # Extraer y validar partes
            contenido = cita[6:-1]
            partes = contenido.split(':')
            
            if len(partes) < 3:
                return False
            
            tipo, autor, año = partes[0].strip(), partes[1].strip(), partes[2].strip()
            
            # Validar tipo
            if tipo not in self.tipos_cita:
                return False
            
            # Validar que tengan contenido
            if not autor or not año:
                return False
            
            return True
            
        except:
            return False
    
    def mostrar_resultados_validacion(self, citas_encontradas, citas_problematicas):
        """Muestra los resultados de validación en una ventana"""
        result_window = ctk.CTkToplevel(self.app.root)
        result_window.title("🔍 Resultados de Validación de Citas")
        result_window.geometry("800x600")
        result_window.transient(self.app.root)
        
        main_frame = ctk.CTkFrame(result_window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text="🔍 Reporte de Validación de Citas",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 15))
        
        # Estadísticas
        stats_frame = ctk.CTkFrame(main_frame, fg_color="darkgreen", corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 15))
        
        total_citas = len(citas_encontradas)
        citas_validas = total_citas - len(citas_problematicas)
        
        stats_text = f"📊 ESTADÍSTICAS:\n" \
                    f"• Total de citas encontradas: {total_citas}\n" \
                    f"• Citas válidas: {citas_validas}\n" \
                    f"• Citas con problemas: {len(citas_problematicas)}"
        
        stats_label = ctk.CTkLabel(
            stats_frame, text=stats_text, font=ctk.CTkFont(size=12),
            text_color="white", justify="left"
        )
        stats_label.pack(padx=15, pady=15)
        
        # Lista de resultados
        results_frame = ctk.CTkScrollableFrame(main_frame, height=350)
        results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        if not citas_encontradas:
            no_citas_label = ctk.CTkLabel(
                results_frame, text="📝 No se encontraron citas en el proyecto",
                font=ctk.CTkFont(size=14), text_color="gray"
            )
            no_citas_label.pack(pady=20)
        else:
            for cita_info in citas_encontradas:
                self.crear_item_validacion(results_frame, cita_info)
        
        # Botón cerrar
        close_btn = ctk.CTkButton(
            main_frame, text="✅ Cerrar", command=result_window.destroy,
            width=120, height=35
        )
        close_btn.pack(pady=(0, 10))
    
    def crear_item_validacion(self, parent, cita_info):
        """Crea un item visual para mostrar resultado de validación"""
        item_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=8)
        item_frame.pack(fill="x", padx=5, pady=5)
        
        # Icono de estado
        icono = "✅" if cita_info['valida'] else "❌"
        color = "lightgreen" if cita_info['valida'] else "lightcoral"
        
        # Información de la cita
        info_text = f"{icono} {cita_info['seccion']}\n{cita_info['cita']}"
        
        info_label = ctk.CTkLabel(
            item_frame, text=info_text, font=ctk.CTkFont(size=11),
            text_color=color, justify="left", wraplength=700
        )
        info_label.pack(padx=15, pady=10, anchor="w")
    
    def exportar_referencias(self, formato='apa'):
        """Exporta las referencias en diferentes formatos"""
        if not self.app.referencias:
            messagebox.showwarning("⚠️ Sin Referencias", "No hay referencias para exportar")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Archivo de texto", "*.txt"),
                    ("JSON", "*.json"),
                    ("CSV", "*.csv")
                ],
                title="Exportar Referencias"
            )
            
            if filename:
                if filename.endswith('.json'):
                    self.exportar_json(filename)
                elif filename.endswith('.csv'):
                    self.exportar_csv(filename)
                else:
                    self.exportar_texto(filename, formato)
                
                messagebox.showinfo("📤 Exportado", f"Referencias exportadas a:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al exportar:\n{str(e)}")
    
    def exportar_texto(self, filename, formato):
        """Exporta referencias en formato de texto"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("REFERENCIAS BIBLIOGRÁFICAS\n")
            f.write("=" * 50 + "\n\n")
            
            # Ordenar alfabéticamente
            referencias_ordenadas = sorted(self.app.referencias, key=lambda x: x.get('autor', ''))
            
            for ref in referencias_ordenadas:
                ref_formateada = self.formatear_referencia_apa(ref)
                f.write(f"{ref_formateada}\n\n")
    
    def exportar_json(self, filename):
        """Exporta referencias en formato JSON"""
        export_data = {
            'fecha_exportacion': datetime.now().isoformat(),
            'total_referencias': len(self.app.referencias),
            'referencias': self.app.referencias
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def exportar_csv(self, filename):
        """Exporta referencias en formato CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Autor', 'Año', 'Título', 'Fuente', 'Tipo'])
            
            for ref in self.app.referencias:
                writer.writerow([
                    ref.get('autor', ''),
                    ref.get('año', ''),
                    ref.get('titulo', ''),
                    ref.get('fuente', ''),
                    ref.get('tipo', '')
                ])


class CitaRapidaDialog:
    """Diálogo para generar citas rápidas"""
    
    def __init__(self, parent, reference_manager):
        self.result = None
        self.ref_manager = reference_manager
        
        # Crear ventana
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("⚡ Generador de Cita Rápida")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Configura el diálogo"""
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, text="⚡ Generar Cita Rápida",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Campos
        fields_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Tipo de cita
        ctk.CTkLabel(fields_frame, text="Tipo de cita:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.tipo_combo = ctk.CTkComboBox(
            fields_frame, 
            values=list(self.ref_manager.tipos_cita.keys()),
            width=400
        )
        self.tipo_combo.pack(fill="x", pady=(0, 15))
        
        # Autor
        ctk.CTkLabel(fields_frame, text="Autor:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.autor_entry = ctk.CTkEntry(fields_frame, placeholder_text="Apellido o Apellido, N.")
        self.autor_entry.pack(fill="x", pady=(0, 15))
        
        # Año
        ctk.CTkLabel(fields_frame, text="Año:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.año_entry = ctk.CTkEntry(fields_frame, placeholder_text="2024")
        self.año_entry.pack(fill="x", pady=(0, 15))
        
        # Página (opcional)
        ctk.CTkLabel(fields_frame, text="Página (opcional):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.pagina_entry = ctk.CTkEntry(fields_frame, placeholder_text="45")
        self.pagina_entry.pack(fill="x", pady=(0, 20))
        
        # Vista previa
        self.preview_frame = ctk.CTkFrame(main_frame, fg_color="gray20", corner_radius=10)
        self.preview_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(self.preview_frame, text="👁️ Vista Previa:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame, text="[CITA:tipo:autor:año:página]",
            font=ctk.CTkFont(size=11), text_color="lightblue", wraplength=400
        )
        self.preview_label.pack(padx=15, pady=(0, 10))
        
        # Actualizar vista previa en tiempo real
        self.tipo_combo.configure(command=self.actualizar_preview)
        self.autor_entry.bind('<KeyRelease>', lambda e: self.actualizar_preview())
        self.año_entry.bind('<KeyRelease>', lambda e: self.actualizar_preview())
        self.pagina_entry.bind('<KeyRelease>', lambda e: self.actualizar_preview())
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            btn_frame, text="❌ Cancelar", command=self.cancelar,
            fg_color="red", hover_color="darkred", width=120
        )
        cancel_btn.pack(side="left", padx=(20, 10))
        
        generate_btn = ctk.CTkButton(
            btn_frame, text="✅ Generar", command=self.generar,
            fg_color="green", hover_color="darkgreen", width=120
        )
        generate_btn.pack(side="right", padx=(10, 20))
    
    def actualizar_preview(self, *args):
        """Actualiza la vista previa de la cita"""
        tipo = self.tipo_combo.get()
        autor = self.autor_entry.get().strip()
        año = self.año_entry.get().strip()
        pagina = self.pagina_entry.get().strip()
        
        if tipo and autor and año:
            if pagina:
                preview = f"[CITA:{tipo}:{autor}:{año}:{pagina}]"
            else:
                preview = f"[CITA:{tipo}:{autor}:{año}]"
        else:
            preview = "[CITA:tipo:autor:año:página]"
        
        self.preview_label.configure(text=preview)
    
    def generar(self):
        """Genera la cita final"""
        tipo = self.tipo_combo.get()
        autor = self.autor_entry.get().strip()
        año = self.año_entry.get().strip()
        
        if not all([tipo, autor, año]):
            messagebox.showerror("❌ Error", "Completa al menos tipo, autor y año")
            return
        
        pagina = self.pagina_entry.get().strip()
        if pagina:
            self.result = f"[CITA:{tipo}:{autor}:{año}:{pagina}]"
        else:
            self.result = f"[CITA:{tipo}:{autor}:{año}]"
        
        self.dialog.destroy()
    
    def cancelar(self):
        """Cancela la operación"""
        self.dialog.destroy()