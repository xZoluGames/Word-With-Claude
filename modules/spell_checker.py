"""
Corrector ortográfico y gramatical integrado para proyectos académicos

Este módulo proporciona:
- Corrección ortográfica en español
- Análisis gramatical
- Diccionario personalizado de términos académicos
- Integración con la interfaz principal
"""

from spellchecker import SpellChecker
import language_tool_python
from utils.logger import get_logger
import re
import json
import os
from typing import List, Dict, Set, Tuple
import customtkinter as ctk
from tkinter import messagebox
import threading

logger = get_logger('SpellChecker')

class SpellCheckManager:
    """Gestor principal de corrección ortográfica y gramatical"""
    
    def __init__(self, language='es'):
        """
        Inicializa el corrector con soporte para español
        
        Args:
            language: Código de idioma (por defecto 'es' para español)
        """
        logger.info(f"Inicializando SpellCheckManager para idioma: {language}")
        
        self.language = language
        self.spell = SpellChecker(language=language)
        
        # Inicializar LanguageTool en thread separado para no bloquear UI
        self.grammar_tool = None
        self._init_grammar_tool_async()
        
        self.custom_dictionary = set()
        self.ignored_words = set()
        self.corrections_history = []
        
        # Cargar diccionarios
        self.dict_path = os.path.join('data', 'dictionaries')
        os.makedirs(self.dict_path, exist_ok=True)
        
        self.load_academic_terms()
        self.load_custom_dictionary()
    
    def _init_grammar_tool_async(self):
        """Inicializa LanguageTool de forma asíncrona"""
        def init():
            try:
                self.grammar_tool = language_tool_python.LanguageTool(self.language)
                logger.info("LanguageTool inicializado correctamente")
            except Exception as e:
                logger.error(f"Error inicializando LanguageTool: {e}")
                self.grammar_tool = None
        
        thread = threading.Thread(target=init, daemon=True)
        thread.start()
    
    def load_academic_terms(self):
        """Carga términos académicos comunes en español"""
        academic_terms = [
            # Metodología
            'metodología', 'hipótesis', 'variables', 'muestra', 'población',
            'correlación', 'análisis', 'síntesis', 'investigación', 'estudio',
            'paradigma', 'enfoque', 'cuantitativo', 'cualitativo', 'mixto',
            
            # Estadística
            'estadística', 'desviación', 'estándar', 'media', 'mediana',
            'moda', 'varianza', 'regresión', 'significancia', 'intervalo',
            
            # Términos de investigación
            'marco', 'teórico', 'conceptual', 'empírico', 'experimental',
            'observacional', 'longitudinal', 'transversal', 'prospectivo',
            'retrospectivo', 'inductivo', 'deductivo', 'validez', 'confiabilidad',
            
            # Términos académicos generales
            'bibliografía', 'referencias', 'citas', 'parafraseo', 'plagiarismo',
            'resumen', 'abstract', 'palabras', 'clave', 'introducción',
            'conclusiones', 'recomendaciones', 'anexos', 'apéndices',
            
            # Verbos académicos
            'analizar', 'sintetizar', 'evaluar', 'comparar', 'contrastar',
            'describir', 'explicar', 'argumentar', 'fundamentar', 'sustentar',
            'plantear', 'proponer', 'desarrollar', 'implementar', 'validar'
        ]
        
        self.custom_dictionary.update(academic_terms)
        logger.info(f"Cargados {len(academic_terms)} términos académicos")
    
    def load_custom_dictionary(self):
        """Carga el diccionario personalizado del usuario"""
        custom_dict_file = os.path.join(self.dict_path, 'custom_dictionary.json')
        
        if os.path.exists(custom_dict_file):
            try:
                with open(custom_dict_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.custom_dictionary.update(data.get('words', []))
                    self.ignored_words.update(data.get('ignored', []))
                logger.info(f"Diccionario personalizado cargado: {len(self.custom_dictionary)} palabras")
            except Exception as e:
                logger.error(f"Error cargando diccionario personalizado: {e}")
    
    def save_custom_dictionary(self):
        """Guarda el diccionario personalizado"""
        custom_dict_file = os.path.join(self.dict_path, 'custom_dictionary.json')
        
        try:
            data = {
                'words': list(self.custom_dictionary),
                'ignored': list(self.ignored_words)
            }
            with open(custom_dict_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Diccionario personalizado guardado")
        except Exception as e:
            logger.error(f"Error guardando diccionario: {e}")
    
    def check_spelling(self, text: str) -> List[Dict]:
        """
        Verifica ortografía y retorna lista de errores
        
        Args:
            text: Texto a verificar
            
        Returns:
            Lista de diccionarios con errores encontrados
        """
        # Extraer palabras del texto
        words = re.findall(r'\b[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+\b', text)
        misspelled = []
        seen = set()
        
        for word in words:
            word_lower = word.lower()
            
            # Saltar si ya se procesó o está en diccionarios
            if (word_lower in seen or 
                word_lower in self.custom_dictionary or
                word_lower in self.ignored_words):
                continue
            
            seen.add(word_lower)
            
            # Verificar si está mal escrita
            if word_lower not in self.spell:
                # Buscar posición en el texto
                positions = [(m.start(), m.end()) for m in re.finditer(r'\b' + re.escape(word) + r'\b', text)]
                
                misspelled.append({
                    'word': word,
                    'word_lower': word_lower,
                    'suggestions': list(self.spell.candidates(word_lower))[:5] if self.spell.candidates(word_lower) else [],
                    'positions': positions,
                    'count': len(positions)
                })
        
        return misspelled
    
    def check_grammar(self, text: str) -> List[Dict]:
        """
        Verifica gramática y retorna sugerencias
        
        Args:
            text: Texto a verificar
            
        Returns:
            Lista de sugerencias gramaticales
        """
        if not self.grammar_tool:
            logger.warning("LanguageTool no está disponible")
            return []
        
        try:
            matches = self.grammar_tool.check(text)
            suggestions = []
            
            for match in matches:
                # Filtrar algunas reglas que pueden ser molestas
                if match.ruleId in ['WHITESPACE_RULE', 'UPPERCASE_SENTENCE_START']:
                    continue
                
                suggestions.append({
                    'message': match.message,
                    'replacements': match.replacements[:3] if match.replacements else [],
                    'offset': match.offset,
                    'length': match.errorLength,
                    'category': match.category,
                    'rule_id': match.ruleId,
                    'context': text[max(0, match.offset-20):min(len(text), match.offset+match.errorLength+20)]
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error verificando gramática: {e}")
            return []
    
    def add_to_dictionary(self, word: str):
        """Agrega una palabra al diccionario personalizado"""
        self.custom_dictionary.add(word.lower())
        self.save_custom_dictionary()
        logger.info(f"Palabra agregada al diccionario: {word}")
    
    def ignore_word(self, word: str):
        """Ignora una palabra para esta sesión"""
        self.ignored_words.add(word.lower())
        logger.info(f"Palabra ignorada: {word}")
    
    def get_statistics(self, text: str) -> Dict:
        """Obtiene estadísticas del texto"""
        words = re.findall(r'\b[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+\b', text)
        sentences = re.split(r'[.!?]+', text)
        
        return {
            'total_words': len(words),
            'unique_words': len(set(word.lower() for word in words)),
            'sentences': len([s for s in sentences if s.strip()]),
            'avg_word_length': sum(len(word) for word in words) / max(1, len(words)),
            'longest_word': max(words, key=len) if words else ""
        }
    
    def auto_correct(self, text: str, corrections: List[Tuple[str, str]]) -> str:
        """
        Aplica correcciones automáticas al texto
        
        Args:
            text: Texto original
            corrections: Lista de tuplas (palabra_incorrecta, palabra_correcta)
            
        Returns:
            Texto corregido
        """
        corrected_text = text
        
        for incorrect, correct in corrections:
            # Usar regex para mantener mayúsculas/minúsculas
            pattern = r'\b' + re.escape(incorrect) + r'\b'
            
            def replace_func(match):
                original = match.group()
                if original.isupper():
                    return correct.upper()
                elif original[0].isupper():
                    return correct.capitalize()
                else:
                    return correct.lower()
            
            corrected_text = re.sub(pattern, replace_func, corrected_text, flags=re.IGNORECASE)
        
        # Guardar en historial
        self.corrections_history.append({
            'timestamp': datetime.now().isoformat(),
            'corrections': corrections
        })
        
        return corrected_text


class SpellCheckDialog(ctk.CTkToplevel):
    """Diálogo interactivo de corrección ortográfica"""
    
    def __init__(self, parent, text_widget, section_name=""):
        super().__init__(parent)
        
        self.text_widget = text_widget
        self.section_name = section_name
        self.spell_checker = SpellCheckManager()
        
        self.current_errors = []
        self.current_error_index = 0
        self.corrections_to_apply = []
        
        self.setup_ui()
        self.check_text()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.title(f"🔤 Corrector Ortográfico - {self.section_name}")
        self.geometry("700x500")
        self.transient(self.master)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Verificando ortografía...",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(side="left")
        
        self.stats_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.stats_label.pack(side="right")
        
        # Área de error actual
        error_frame = ctk.CTkFrame(main_frame)
        error_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            error_frame,
            text="Palabra incorrecta:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.error_label = ctk.CTkLabel(
            error_frame,
            text="",
            font=ctk.CTkFont(size=16),
            text_color="red"
        )
        self.error_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Contexto
        ctk.CTkLabel(
            error_frame,
            text="Contexto:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.context_text = ctk.CTkTextbox(
            error_frame,
            height=60,
            font=ctk.CTkFont(size=11)
        )
        self.context_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # Sugerencias
        suggestions_frame = ctk.CTkFrame(main_frame)
        suggestions_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(
            suggestions_frame,
            text="Sugerencias:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Frame scrollable para sugerencias
        self.suggestions_scroll = ctk.CTkScrollableFrame(
            suggestions_frame,
            height=150
        )
        self.suggestions_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Botones de acción
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(fill="x")
        
        # Primera fila de botones
        row1 = ctk.CTkFrame(action_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(
            row1,
            text="⬅️ Anterior",
            command=self.previous_error,
            width=100
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            row1,
            text="Ignorar",
            command=self.ignore_current,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            row1,
            text="Ignorar todas",
            command=self.ignore_all_current,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            row1,
            text="Agregar al diccionario",
            command=self.add_to_dictionary,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            row1,
            text="➡️ Siguiente",
            command=self.next_error,
            width=100
        ).pack(side="left", padx=5)
        
        # Segunda fila
        row2 = ctk.CTkFrame(action_frame, fg_color="transparent")
        row2.pack(fill="x")
        
        self.auto_correct_btn = ctk.CTkButton(
            row2,
            text="🔧 Corregir todo automáticamente",
            command=self.auto_correct_all,
            width=200,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.auto_correct_btn.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            row2,
            text="✅ Aplicar y cerrar",
            command=self.apply_and_close,
            width=120
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            row2,
            text="❌ Cancelar",
            command=self.cancel,
            width=100,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(main_frame)
        self.progress.pack(fill="x", pady=(20, 0))
        self.progress.set(0)
    
    def check_text(self):
        """Verifica el texto y encuentra errores"""
        text = self.text_widget.get("1.0", "end-1c")
        
        # Verificar ortografía
        self.current_errors = self.spell_checker.check_spelling(text)
        
        # Actualizar UI
        if self.current_errors:
            self.title_label.configure(
                text=f"Se encontraron {len(self.current_errors)} posibles errores"
            )
            self.show_current_error()
        else:
            self.title_label.configure(text="✅ No se encontraron errores")
            self.error_label.configure(text="¡Excelente! No hay errores ortográficos.")
            self.disable_navigation_buttons()
        
        # Actualizar estadísticas
        stats = self.spell_checker.get_statistics(text)
        self.stats_label.configure(
            text=f"Palabras: {stats['total_words']} | Únicas: {stats['unique_words']}"
        )
    
    def show_current_error(self):
        """Muestra el error actual"""
        if not self.current_errors or self.current_error_index >= len(self.current_errors):
            return
        
        error = self.current_errors[self.current_error_index]
        
        # Mostrar palabra incorrecta
        self.error_label.configure(text=error['word'])
        
        # Mostrar contexto
        text = self.text_widget.get("1.0", "end-1c")
        if error['positions']:
            pos = error['positions'][0]
            start = max(0, pos[0] - 30)
            end = min(len(text), pos[1] + 30)
            
            context = text[start:end]
            # Resaltar la palabra en el contexto
            word_start = pos[0] - start
            word_end = pos[1] - start
            
            highlighted_context = (
                context[:word_start] + 
                f">>>{context[word_start:word_end]}<<<" +
                context[word_end:]
            )
            
            self.context_text.delete("1.0", "end")
            self.context_text.insert("1.0", highlighted_context)
        
        # Mostrar sugerencias
        self.show_suggestions(error['suggestions'])
        
        # Actualizar progress
        progress = (self.current_error_index + 1) / len(self.current_errors)
        self.progress.set(progress)
        
        # Habilitar/deshabilitar botones de navegación
        self.update_navigation_buttons()
    
    def show_suggestions(self, suggestions):
        """Muestra las sugerencias de corrección"""
        # Limpiar sugerencias anteriores
        for widget in self.suggestions_scroll.winfo_children():
            widget.destroy()
        
        if not suggestions:
            ctk.CTkLabel(
                self.suggestions_scroll,
                text="No hay sugerencias disponibles",
                text_color="gray"
            ).pack(pady=10)
        else:
            for i, suggestion in enumerate(suggestions):
                btn = ctk.CTkButton(
                    self.suggestions_scroll,
                    text=suggestion,
                    command=lambda s=suggestion: self.apply_suggestion(s),
                    fg_color="transparent",
                    hover_color="gray20",
                    anchor="w"
                )
                btn.pack(fill="x", padx=5, pady=2)
                
                # Seleccionar primera sugerencia por defecto
                if i == 0:
                    btn.configure(fg_color="gray20")
    
    def apply_suggestion(self, suggestion):
        """Aplica una sugerencia de corrección"""
        if not self.current_errors or self.current_error_index >= len(self.current_errors):
            return
        
        error = self.current_errors[self.current_error_index]
        
        # Agregar a lista de correcciones
        self.corrections_to_apply.append((error['word'], suggestion))
        
        # Pasar al siguiente error
        self.next_error()
    
    def next_error(self):
        """Va al siguiente error"""
        if self.current_error_index < len(self.current_errors) - 1:
            self.current_error_index += 1
            self.show_current_error()
        else:
            # Llegamos al final
            if self.corrections_to_apply:
                self.ask_apply_corrections()
            else:
                messagebox.showinfo("✅ Finalizado", "Revisión completada")
    
    def previous_error(self):
        """Va al error anterior"""
        if self.current_error_index > 0:
            self.current_error_index -= 1
            self.show_current_error()
    
    def ignore_current(self):
        """Ignora el error actual"""
        self.next_error()
    
    def ignore_all_current(self):
        """Ignora todas las instancias de la palabra actual"""
        if not self.current_errors or self.current_error_index >= len(self.current_errors):
            return
        
        error = self.current_errors[self.current_error_index]
        word = error['word_lower']
        
        # Agregar a palabras ignoradas
        self.spell_checker.ignore_word(word)
        
        # Remover todas las instancias de esta palabra de la lista de errores
        self.current_errors = [e for e in self.current_errors if e['word_lower'] != word]
        
        # Ajustar índice si es necesario
        if self.current_error_index >= len(self.current_errors):
            self.current_error_index = max(0, len(self.current_errors) - 1)
        
        if self.current_errors:
            self.show_current_error()
        else:
            self.title_label.configure(text="✅ No hay más errores")
    
    def add_to_dictionary(self):
        """Agrega la palabra actual al diccionario"""
        if not self.current_errors or self.current_error_index >= len(self.current_errors):
            return
        
        error = self.current_errors[self.current_error_index]
        word = error['word']
        
        # Confirmar
        if messagebox.askyesno("Agregar al diccionario", 
                              f"¿Agregar '{word}' al diccionario personalizado?"):
            self.spell_checker.add_to_dictionary(word)
            self.ignore_all_current()
    
    def auto_correct_all(self):
        """Corrige automáticamente todos los errores"""
        corrections = []
        
        for error in self.current_errors:
            if error['suggestions']:
                # Usar la primera sugerencia
                corrections.append((error['word'], error['suggestions'][0]))
        
        if corrections:
            if messagebox.askyesno("Auto-corrección",
                                  f"¿Aplicar {len(corrections)} correcciones automáticas?"):
                self.corrections_to_apply = corrections
                self.apply_corrections()
                self.destroy()
        else:
            messagebox.showinfo("Sin correcciones", 
                               "No hay sugerencias automáticas disponibles")
    
    def ask_apply_corrections(self):
        """Pregunta si aplicar las correcciones"""
        if messagebox.askyesno("Aplicar correcciones",
                              f"¿Aplicar {len(self.corrections_to_apply)} correcciones?"):
            self.apply_corrections()
    
    def apply_corrections(self):
        """Aplica las correcciones al texto"""
        if not self.corrections_to_apply:
            return
        
        # Obtener texto actual
        text = self.text_widget.get("1.0", "end-1c")
        
        # Aplicar correcciones
        corrected_text = self.spell_checker.auto_correct(text, self.corrections_to_apply)
        
        # Actualizar widget
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", corrected_text)
        
        messagebox.showinfo("✅ Correcciones aplicadas",
                           f"Se aplicaron {len(self.corrections_to_apply)} correcciones")
    
    def apply_and_close(self):
        """Aplica correcciones pendientes y cierra"""
        if self.corrections_to_apply:
            self.apply_corrections()
        self.destroy()
    
    def cancel(self):
        """Cancela sin aplicar cambios"""
        self.destroy()
    
    def update_navigation_buttons(self):
        """Actualiza estado de botones de navegación"""
        # Implementar según necesidad
        pass
    
    def disable_navigation_buttons(self):
        """Deshabilita botones cuando no hay errores"""
        # Implementar según necesidad
        pass


# Función auxiliar para integración fácil
def check_spelling_in_widget(parent, text_widget, section_name=""):
    """
    Función helper para verificar ortografía en un widget de texto
    
    Args:
        parent: Ventana padre
        text_widget: Widget de texto a verificar
        section_name: Nombre de la sección (opcional)
    """
    dialog = SpellCheckDialog(parent, text_widget, section_name)
    dialog.grab_set()
    parent.wait_window(dialog)