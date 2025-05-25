"""
Sistema de búsqueda y reemplazo avanzado con expresiones regulares
"""

import re
from typing import List, Dict, Tuple, Optional
import customtkinter as ctk
from tkinter import messagebox
from utils.logger import get_logger

logger = get_logger('SearchReplace')

class SearchReplaceManager:
    """Gestor de búsqueda y reemplazo avanzado"""
    
    def __init__(self):
        self.search_history = []
        self.replace_history = []
        self.max_history = 20
        
        # Patrones predefinidos
        self.patterns = {
            'doble_espacio': (r'\s{2,}', ' ', 'Eliminar espacios dobles'),
            'salto_linea_multiple': (r'\n{3,}', '\n\n', 'Reducir saltos de línea múltiples'),
            'puntuacion_espacio': (r'\s+([.,;:!?])', r'\1', 'Eliminar espacio antes de puntuación'),
            'numero_romano': (r'\b([IVXLCDM]+)\b', r'[\1]', 'Marcar números romanos'),
            'url': (r'(https?://[^\s]+)', r'<\1>', 'Marcar URLs'),
            'email': (r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'[\1]', 'Marcar emails'),
            'cita_mal_formateada': (r'\(([^,]+),\s*(\d{4})\)', r'[CITA:parafraseo:\1:\2]', 'Corregir formato de citas')
        }
        
        logger.info("SearchReplaceManager inicializado")
    
    def search(self, text: str, pattern: str, case_sensitive: bool = False, 
               whole_words: bool = False, regex: bool = False) -> List[Tuple[int, int, str]]:
        """
        Busca un patrón en el texto
        
        Args:
            text: Texto donde buscar
            pattern: Patrón a buscar
            case_sensitive: Distinguir mayúsculas/minúsculas
            whole_words: Solo palabras completas
            regex: Usar expresiones regulares
            
        Returns:
            Lista de tuplas (inicio, fin, texto_encontrado)
        """
        if not pattern:
            return []
        
        matches = []
        
        try:
            # Preparar patrón
            if not regex:
                pattern = re.escape(pattern)
            
            if whole_words:
                pattern = r'\b' + pattern + r'\b'
            
            flags = 0 if case_sensitive else re.IGNORECASE
            
            # Buscar todas las coincidencias
            for match in re.finditer(pattern, text, flags):
                matches.append((match.start(), match.end(), match.group()))
            
            # Agregar a historial
            self._add_to_history(self.search_history, pattern)
            
            logger.info(f"Búsqueda completada: {len(matches)} coincidencias")
            
        except re.error as e:
            logger.error(f"Error en expresión regular: {e}")
            raise ValueError(f"Expresión regular inválida: {e}")
        
        return matches
    
    def replace(self, text: str, search_pattern: str, replace_pattern: str,
                case_sensitive: bool = False, whole_words: bool = False,
                regex: bool = False, confirm_each: bool = False) -> Tuple[str, int]:
        """
        Reemplaza un patrón en el texto
        
        Args:
            text: Texto donde reemplazar
            search_pattern: Patrón a buscar
            replace_pattern: Patrón de reemplazo
            case_sensitive: Distinguir mayúsculas/minúsculas
            whole_words: Solo palabras completas
            regex: Usar expresiones regulares
            confirm_each: Confirmar cada reemplazo
            
        Returns:
            Tupla (texto_modificado, número_de_reemplazos)
        """
        if not search_pattern:
            return text, 0
        
        try:
            # Preparar patrón
            if not regex:
                search_pattern = re.escape(search_pattern)
                replace_pattern = replace_pattern.replace('\\', '\\\\')
            
            if whole_words:
                search_pattern = r'\b' + search_pattern + r'\b'
            
            flags = 0 if case_sensitive else re.IGNORECASE
            
            if confirm_each:
                # Reemplazo interactivo (requiere UI)
                matches = list(re.finditer(search_pattern, text, flags))
                replacements = 0
                offset = 0
                
                for match in matches:
                    # Aquí se integraría con un diálogo de confirmación
                    # Por ahora, simulamos aceptación
                    start = match.start() + offset
                    end = match.end() + offset
                    
                    new_text = re.sub(search_pattern, replace_pattern, match.group(), flags=flags)
                    text = text[:start] + new_text + text[end:]
                    
                    offset += len(new_text) - (end - start)
                    replacements += 1
                
                result_text = text
                
            else:
                # Reemplazo directo
                result_text, replacements = re.subn(search_pattern, replace_pattern, text, flags=flags)
            
            # Agregar a historial
            self._add_to_history(self.search_history, search_pattern)
            self._add_to_history(self.replace_history, replace_pattern)
            
            logger.info(f"Reemplazo completado: {replacements} reemplazos")
            
            return result_text, replacements
            
        except re.error as e:
            logger.error(f"Error en expresión regular: {e}")
            raise ValueError(f"Expresión regular inválida: {e}")
    
    def search_in_project(self, app_instance, pattern: str, **kwargs) -> Dict[str, List[Tuple[int, int, str]]]:
        """
        Busca en todo el proyecto
        
        Args:
            app_instance: Instancia de la aplicación
            pattern: Patrón a buscar
            **kwargs: Opciones de búsqueda
            
        Returns:
            Diccionario con resultados por sección
        """
        results = {}
        
        # Buscar en cada sección
        for section_id, text_widget in app_instance.content_texts.items():
            if section_id in app_instance.secciones_disponibles:
                section_name = app_instance.secciones_disponibles[section_id]['titulo']
                text = text_widget.get("1.0", "end-1c")
                
                matches = self.search(text, pattern, **kwargs)
                if matches:
                    results[section_name] = matches
        
        # Buscar en información general
        for field_name, entry in app_instance.proyecto_data.items():
            if hasattr(entry, 'get'):
                text = entry.get()
                matches = self.search(text, pattern, **kwargs)
                if matches:
                    results[f"Info General - {field_name}"] = matches
        
        return results
    
    def replace_in_project(self, app_instance, search_pattern: str, 
                          replace_pattern: str, **kwargs) -> Dict[str, int]:
        """
        Reemplaza en todo el proyecto
        
        Args:
            app_instance: Instancia de la aplicación
            search_pattern: Patrón a buscar
            replace_pattern: Patrón de reemplazo
            **kwargs: Opciones de reemplazo
            
        Returns:
            Diccionario con número de reemplazos por sección
        """
        results = {}
        total_replacements = 0
        
        # Reemplazar en cada sección
        for section_id, text_widget in app_instance.content_texts.items():
            if section_id in app_instance.secciones_disponibles:
                section_name = app_instance.secciones_disponibles[section_id]['titulo']
                text = text_widget.get("1.0", "end-1c")
                
                new_text, count = self.replace(text, search_pattern, replace_pattern, **kwargs)
                
                if count > 0:
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", new_text)
                    results[section_name] = count
                    total_replacements += count
        
        logger.info(f"Reemplazo en proyecto: {total_replacements} reemplazos totales")
        
        return results
    
    def apply_pattern(self, text: str, pattern_name: str) -> Tuple[str, int]:
        """
        Aplica un patrón predefinido
        
        Args:
            text: Texto donde aplicar
            pattern_name: Nombre del patrón
            
        Returns:
            Tupla (texto_modificado, número_de_cambios)
        """
        if pattern_name not in self.patterns:
            raise ValueError(f"Patrón '{pattern_name}' no encontrado")
        
        search_pattern, replace_pattern, _ = self.patterns[pattern_name]
        return self.replace(text, search_pattern, replace_pattern, regex=True)
    
    def _add_to_history(self, history_list: List[str], item: str):
        """Agrega un elemento al historial"""
        if item in history_list:
            history_list.remove(item)
        
        history_list.insert(0, item)
        
        if len(history_list) > self.max_history:
            history_list.pop()


class SearchReplaceDialog(ctk.CTkToplevel):
    """Diálogo de búsqueda y reemplazo avanzado"""
    
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        
        self.app_instance = app_instance
        self.search_manager = SearchReplaceManager()
        self.current_matches = []
        self.current_match_index = 0
        
        self.setup_ui()
        self.bind_shortcuts()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.title("🔍 Búsqueda y Reemplazo Avanzado")
        self.geometry("600x700")
        self.transient(self.master)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tabs
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True)
        
        # Tab de búsqueda
        search_tab = self.tabview.add("🔍 Buscar")
        self.setup_search_tab(search_tab)
        
        # Tab de reemplazo
        replace_tab = self.tabview.add("🔄 Reemplazar")
        self.setup_replace_tab(replace_tab)
        
        # Tab de patrones
        patterns_tab = self.tabview.add("📋 Patrones")
        self.setup_patterns_tab(patterns_tab)
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Listo para buscar",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=(10, 0))
    
    def setup_search_tab(self, parent):
        """Configura la pestaña de búsqueda"""
        # Campo de búsqueda
        ctk.CTkLabel(parent, text="Buscar:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.search_entry = ctk.CTkEntry(parent, placeholder_text="Ingrese texto a buscar")
        self.search_entry.pack(fill="x", pady=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search())
        
        # Opciones
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 10))
        
        self.case_sensitive_var = ctk.CTkCheckBox(options_frame, text="Distinguir mayúsculas")
        self.case_sensitive_var.pack(side="left", padx=(0, 10))
        
        self.whole_words_var = ctk.CTkCheckBox(options_frame, text="Palabras completas")
        self.whole_words_var.pack(side="left", padx=(0, 10))
        
        self.regex_var = ctk.CTkCheckBox(options_frame, text="Expresión regular")
        self.regex_var.pack(side="left")
        
        # Alcance
        scope_frame = ctk.CTkFrame(parent)
        scope_frame.pack(fill="x", pady=(10, 10))
        
        ctk.CTkLabel(scope_frame, text="Buscar en:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.scope_var = ctk.StringVar(value="current")
        
        ctk.CTkRadioButton(scope_frame, text="Sección actual", variable=self.scope_var, value="current").pack(anchor="w", padx=20, pady=2)
        ctk.CTkRadioButton(scope_frame, text="Todo el proyecto", variable=self.scope_var, value="all").pack(anchor="w", padx=20, pady=2)
        ctk.CTkRadioButton(scope_frame, text="Secciones seleccionadas", variable=self.scope_var, value="selected").pack(anchor="w", padx=20, pady=(2, 10))
        
        # Botones
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(btn_frame, text="🔍 Buscar", command=self.search, width=100).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="⬇️ Siguiente", command=self.find_next, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="⬆️ Anterior", command=self.find_previous, width=100).pack(side="left", padx=5)
        
        # Resultados
        self.results_frame = ctk.CTkScrollableFrame(parent, height=200)
        self.results_frame.pack(fill="both", expand=True, pady=(10, 0))
    
    def setup_replace_tab(self, parent):
        """Configura la pestaña de reemplazo"""
        # Campos
        ctk.CTkLabel(parent, text="Buscar:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.replace_search_entry = ctk.CTkEntry(parent, placeholder_text="Texto a buscar")
        self.replace_search_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(parent, text="Reemplazar con:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.replace_with_entry = ctk.CTkEntry(parent, placeholder_text="Texto de reemplazo")
        self.replace_with_entry.pack(fill="x", pady=(0, 10))
        
        # Opciones (reutilizar)
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 10))
        
        self.replace_case_var = ctk.CTkCheckBox(options_frame, text="Distinguir mayúsculas")
        self.replace_case_var.pack(side="left", padx=(0, 10))
        
        self.replace_whole_var = ctk.CTkCheckBox(options_frame, text="Palabras completas")
        self.replace_whole_var.pack(side="left", padx=(0, 10))
        
        self.replace_regex_var = ctk.CTkCheckBox(options_frame, text="Expresión regular")
        self.replace_regex_var.pack(side="left")
        
        # Confirmación
        self.confirm_each_var = ctk.CTkCheckBox(parent, text="Confirmar cada reemplazo")
        self.confirm_each_var.pack(pady=10)
        
        # Botones
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="🔄 Reemplazar", 
            command=self.replace_single,
            width=120
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame, 
            text="🔄 Reemplazar todo", 
            command=self.replace_all,
            width=120,
            fg_color="orange",
            hover_color="darkorange"
        ).pack(side="left", padx=5)
        
        # Preview
        ctk.CTkLabel(parent, text="Vista previa:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(20, 5))
        
        self.preview_text = ctk.CTkTextbox(parent, height=150)
        self.preview_text.pack(fill="both", expand=True)
    
    def setup_patterns_tab(self, parent):
        """Configura la pestaña de patrones"""
        ctk.CTkLabel(
            parent, 
            text="Patrones de limpieza predefinidos:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 20))
        
        # Lista de patrones
        patterns_scroll = ctk.CTkScrollableFrame(parent)
        patterns_scroll.pack(fill="both", expand=True, padx=10)
        
        for pattern_name, (search, replace, description) in self.search_manager.patterns.items():
            pattern_frame = ctk.CTkFrame(patterns_scroll, fg_color="gray20", corner_radius=8)
            pattern_frame.pack(fill="x", pady=5)
            
            # Descripción
            ctk.CTkLabel(
                pattern_frame,
                text=f"📋 {description}",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", padx=15, pady=(10, 5))
            
            # Patrón
            ctk.CTkLabel(
                pattern_frame,
                text=f"Busca: {search[:50]}...",
                font=ctk.CTkFont(size=10, family="Courier"),
                text_color="gray70"
            ).pack(anchor="w", padx=25, pady=(0, 5))
            
            # Botón aplicar
            ctk.CTkButton(
                pattern_frame,
                text="Aplicar",
                command=lambda p=pattern_name: self.apply_pattern(p),
                width=80,
                height=25
            ).pack(anchor="e", padx=15, pady=(0, 10))
    
    def search(self):
        """Ejecuta la búsqueda"""
        pattern = self.search_entry.get()
        if not pattern:
            return
        
        try:
            if self.scope_var.get() == "current":
                # Buscar en sección actual
                current_tab = self.app_instance.content_tabview.get()
                
                for section_id, section_data in self.app_instance.secciones_disponibles.items():
                    if section_data['titulo'] == current_tab and section_id in self.app_instance.content_texts:
                        text_widget = self.app_instance.content_texts[section_id]
                        text = text_widget.get("1.0", "end-1c")
                        
                        self.current_matches = self.search_manager.search(
                            text, pattern,
                            case_sensitive=self.case_sensitive_var.get(),
                            whole_words=self.whole_words_var.get(),
                            regex=self.regex_var.get()
                        )
                        
                        self.display_results({current_tab: self.current_matches})
                        break
            
            elif self.scope_var.get() == "all":
                # Buscar en todo el proyecto
                results = self.search_manager.search_in_project(
                    self.app_instance, pattern,
                    case_sensitive=self.case_sensitive_var.get(),
                    whole_words=self.whole_words_var.get(),
                    regex=self.regex_var.get()
                )
                
                self.display_results(results)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def display_results(self, results: Dict):
        """Muestra los resultados de búsqueda"""
        # Limpiar resultados anteriores
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        total_matches = sum(len(matches) for matches in results.values())
        
        if total_matches == 0:
            ctk.CTkLabel(
                self.results_frame,
                text="No se encontraron coincidencias",
                text_color="gray"
            ).pack(pady=20)
        else:
            self.status_label.configure(text=f"Se encontraron {total_matches} coincidencias")
            
            for section, matches in results.items():
                if matches:
                    # Header de sección
                    section_frame = ctk.CTkFrame(self.results_frame, fg_color="gray25", corner_radius=8)
                    section_frame.pack(fill="x", pady=5)
                    
                    ctk.CTkLabel(
                        section_frame,
                        text=f"{section} ({len(matches)} coincidencias)",
                        font=ctk.CTkFont(size=12, weight="bold")
                    ).pack(anchor="w", padx=10, pady=5)
                    
                    # Mostrar algunas coincidencias
                    for i, (start, end, text) in enumerate(matches[:5]):
                        match_label = ctk.CTkLabel(
                            section_frame,
                            text=f"   Pos {start}: ...{text}...",
                            font=ctk.CTkFont(size=10),
                            text_color="gray70"
                        )
                        match_label.pack(anchor="w", padx=20, pady=2)
                    
                    if len(matches) > 5:
                        ctk.CTkLabel(
                            section_frame,
                            text=f"   ... y {len(matches) - 5} más",
                            font=ctk.CTkFont(size=10),
                            text_color="gray50"
                        ).pack(anchor="w", padx=20, pady=2)
    
    def find_next(self):
        """Encuentra la siguiente coincidencia"""
        if self.current_matches and self.current_match_index < len(self.current_matches) - 1:
            self.current_match_index += 1
            self.highlight_current_match()
    
    def find_previous(self):
        """Encuentra la coincidencia anterior"""
        if self.current_matches and self.current_match_index > 0:
            self.current_match_index -= 1
            self.highlight_current_match()
    
    def highlight_current_match(self):
        """Resalta la coincidencia actual"""
        # Implementar resaltado en el widget de texto
        pass
    
    def replace_single(self):
        """Reemplaza una sola ocurrencia"""
        # Implementar reemplazo individual
        pass
    
    def replace_all(self):
        """Reemplaza todas las ocurrencias"""
        search_pattern = self.replace_search_entry.get()
        replace_pattern = self.replace_with_entry.get()
        
        if not search_pattern:
            return
        
        try:
            results = self.search_manager.replace_in_project(
                self.app_instance,
                search_pattern,
                replace_pattern,
                case_sensitive=self.replace_case_var.get(),
                whole_words=self.replace_whole_var.get(),
                regex=self.replace_regex_var.get(),
                confirm_each=self.confirm_each_var.get()
            )
            
            total = sum(results.values())
            
            if total > 0:
                messagebox.showinfo(
                    "Reemplazo completado",
                    f"Se realizaron {total} reemplazos en {len(results)} secciones"
                )
            else:
                messagebox.showinfo("Sin coincidencias", "No se encontraron coincidencias para reemplazar")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def apply_pattern(self, pattern_name: str):
        """Aplica un patrón predefinido"""
        if messagebox.askyesno("Aplicar patrón", 
                              f"¿Aplicar el patrón '{pattern_name}' a todo el proyecto?"):
            
            total_changes = 0
            
            for section_id, text_widget in self.app_instance.content_texts.items():
                text = text_widget.get("1.0", "end-1c")
                new_text, changes = self.search_manager.apply_pattern(text, pattern_name)
                
                if changes > 0:
                    text_widget.delete("1.0", "end")
                    text_widget.insert("1.0", new_text)
                    total_changes += changes
            
            messagebox.showinfo(
                "Patrón aplicado",
                f"Se realizaron {total_changes} cambios"
            )
    
    def bind_shortcuts(self):
        """Vincula atajos de teclado"""
        self.bind('<Control-f>', lambda e: self.tabview.set("🔍 Buscar"))
        self.bind('<Control-h>', lambda e: self.tabview.set("🔄 Reemplazar"))
        self.bind('<F3>', lambda e: self.find_next())
        self.bind('<Shift-F3>', lambda e: self.find_previous())
        self.bind('<Escape>', lambda e: self.destroy())