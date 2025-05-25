"""
Sistema de temas personalizables para la interfaz

Gestiona temas predefinidos y personalizados para la aplicación
"""

import customtkinter as ctk
import json
import os
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import colorsys
from utils.logger import get_logger

logger = get_logger('ThemeManager')

class ThemeManager:
    """Gestor de temas de la aplicación"""
    
    def __init__(self, app_instance=None):
        """
        Inicializa el gestor de temas
        
        Args:
            app_instance: Instancia de la aplicación principal
        """
        self.app = app_instance
        self.themes_dir = Path('themes')
        self.themes_dir.mkdir(exist_ok=True)
        
        # Temas predefinidos
        self.builtin_themes = self._get_builtin_themes()
        
        # Tema actual
        self.current_theme_name = 'default_dark'
        self.current_theme = self.builtin_themes[self.current_theme_name].copy()
        
        # Cargar temas personalizados
        self.custom_themes = self._load_custom_themes()
        
        logger.info("ThemeManager inicializado")
    
    def _get_builtin_themes(self) -> Dict[str, Dict[str, Any]]:
        """Define los temas predefinidos"""
        return {
            'default_dark': {
                'name': 'Oscuro Predeterminado',
                'type': 'dark',
                'colors': {
                    # Colores principales
                    'bg_color': '#212121',
                    'fg_color': '#2B2B2B',
                    'hover_color': '#404040',
                    'border_color': '#565B5E',
                    'text_color': '#DCE4EE',
                    'text_disabled': '#7E8C9D',
                    'selected_color': '#1F6AA5',
                    
                    # Colores de acento
                    'primary': '#1F6AA5',
                    'secondary': '#144870',
                    'success': '#4CAF50',
                    'warning': '#FF9800',
                    'error': '#F44336',
                    'info': '#2196F3',
                    
                    # Elementos específicos
                    'button_fg': '#1F6AA5',
                    'button_hover': '#144870',
                    'button_text': '#DCE4EE',
                    'entry_fg': '#343638',
                    'entry_border': '#565B5E',
                    'entry_text': '#DCE4EE',
                    'frame_low': '#212121',
                    'frame_high': '#2B2B2B',
                    'progressbar_progress': '#1F6AA5',
                    'progressbar_bg': '#565B5E',
                    'switch_progress': '#1F6AA5',
                    'switch_button': '#DCE4EE',
                    'switch_bg': '#565B5E',
                    'scrollbar_button': '#606060',
                    'scrollbar_button_hover': '#808080',
                    
                    # Editor de texto
                    'editor_bg': '#2B2B2B',
                    'editor_text': '#DCE4EE',
                    'editor_cursor': '#DCE4EE',
                    'editor_selection': '#1F6AA5',
                    'editor_line_numbers': '#7E8C9D',
                    'editor_current_line': '#323232',
                    
                    # Sintaxis (para resaltado)
                    'syntax_keyword': '#569CD6',
                    'syntax_string': '#CE9178',
                    'syntax_comment': '#6A9955',
                    'syntax_number': '#B5CEA8',
                    'syntax_function': '#DCDCAA',
                    'syntax_class': '#4EC9B0',
                    'syntax_variable': '#9CDCFE',
                    'syntax_operator': '#D4D4D4'
                },
                'fonts': {
                    'default_family': 'Segoe UI',
                    'default_size': 12,
                    'title_family': 'Segoe UI',
                    'title_size': 18,
                    'heading_family': 'Segoe UI',
                    'heading_size': 14,
                    'code_family': 'Consolas',
                    'code_size': 11
                },
                'spacing': {
                    'padding_small': 5,
                    'padding_medium': 10,
                    'padding_large': 20,
                    'corner_radius': 10,
                    'button_corner': 6,
                    'entry_corner': 6
                }
            },
            
            'default_light': {
                'name': 'Claro Predeterminado',
                'type': 'light',
                'colors': {
                    'bg_color': '#EBEBEB',
                    'fg_color': '#F9F9FA',
                    'hover_color': '#DBDBDB',
                    'border_color': '#979DA2',
                    'text_color': '#212121',
                    'text_disabled': '#7E8C9D',
                    'selected_color': '#1F6AA5',
                    
                    'primary': '#1F6AA5',
                    'secondary': '#144870',
                    'success': '#4CAF50',
                    'warning': '#FF9800',
                    'error': '#F44336',
                    'info': '#2196F3',
                    
                    'button_fg': '#1F6AA5',
                    'button_hover': '#144870',
                    'button_text': '#FFFFFF',
                    'entry_fg': '#F9F9FA',
                    'entry_border': '#979DA2',
                    'entry_text': '#212121',
                    'frame_low': '#EBEBEB',
                    'frame_high': '#F9F9FA',
                    'progressbar_progress': '#1F6AA5',
                    'progressbar_bg': '#979DA2',
                    'switch_progress': '#1F6AA5',
                    'switch_button': '#FFFFFF',
                    'switch_bg': '#979DA2',
                    'scrollbar_button': '#C0C0C0',
                    'scrollbar_button_hover': '#A0A0A0',
                    
                    'editor_bg': '#FFFFFF',
                    'editor_text': '#212121',
                    'editor_cursor': '#212121',
                    'editor_selection': '#ADD6FF',
                    'editor_line_numbers': '#7E8C9D',
                    'editor_current_line': '#F5F5F5',
                    
                    'syntax_keyword': '#0000FF',
                    'syntax_string': '#A31515',
                    'syntax_comment': '#008000',
                    'syntax_number': '#098658',
                    'syntax_function': '#795E26',
                    'syntax_class': '#267F99',
                    'syntax_variable': '#001080',
                    'syntax_operator': '#000000'
                },
                'fonts': {
                    'default_family': 'Segoe UI',
                    'default_size': 12,
                    'title_family': 'Segoe UI',
                    'title_size': 18,
                    'heading_family': 'Segoe UI',
                    'heading_size': 14,
                    'code_family': 'Consolas',
                    'code_size': 11
                },
                'spacing': {
                    'padding_small': 5,
                    'padding_medium': 10,
                    'padding_large': 20,
                    'corner_radius': 10,
                    'button_corner': 6,
                    'entry_corner': 6
                }
            },
            
            'ocean_blue': {
                'name': 'Océano Azul',
                'type': 'dark',
                'colors': {
                    'bg_color': '#0A1929',
                    'fg_color': '#132F4C',
                    'hover_color': '#173A5E',
                    'border_color': '#265D97',
                    'text_color': '#B2BAC2',
                    'text_disabled': '#6B7A90',
                    'selected_color': '#0072E5',
                    
                    'primary': '#0072E5',
                    'secondary': '#004C99',
                    'success': '#1DB954',
                    'warning': '#FFA726',
                    'error': '#FF5252',
                    'info': '#29B6F6',
                    
                    'button_fg': '#0072E5',
                    'button_hover': '#004C99',
                    'button_text': '#FFFFFF',
                    'entry_fg': '#001E3C',
                    'entry_border': '#265D97',
                    'entry_text': '#B2BAC2',
                    'frame_low': '#0A1929',
                    'frame_high': '#132F4C',
                    'progressbar_progress': '#0072E5',
                    'progressbar_bg': '#265D97',
                    'switch_progress': '#0072E5',
                    'switch_button': '#B2BAC2',
                    'switch_bg': '#265D97',
                    'scrollbar_button': '#265D97',
                    'scrollbar_button_hover': '#3D7BAD',
                    
                    'editor_bg': '#001E3C',
                    'editor_text': '#B2BAC2',
                    'editor_cursor': '#B2BAC2',
                    'editor_selection': '#0072E5',
                    'editor_line_numbers': '#6B7A90',
                    'editor_current_line': '#132F4C',
                    
                    'syntax_keyword': '#7DD3FC',
                    'syntax_string': '#86EFAC',
                    'syntax_comment': '#6B7A90',
                    'syntax_number': '#FDE047',
                    'syntax_function': '#C084FC',
                    'syntax_class': '#FCA5A5',
                    'syntax_variable': '#93C5FD',
                    'syntax_operator': '#B2BAC2'
                },
                'fonts': {
                    'default_family': 'Inter',
                    'default_size': 12,
                    'title_family': 'Inter',
                    'title_size': 20,
                    'heading_family': 'Inter',
                    'heading_size': 14,
                    'code_family': 'JetBrains Mono',
                    'code_size': 11
                },
                'spacing': {
                    'padding_small': 6,
                    'padding_medium': 12,
                    'padding_large': 24,
                    'corner_radius': 12,
                    'button_corner': 8,
                    'entry_corner': 8
                }
            },
            
            'forest_green': {
                'name': 'Bosque Verde',
                'type': 'dark',
                'colors': {
                    'bg_color': '#0F1419',
                    'fg_color': '#1A2332',
                    'hover_color': '#253340',
                    'border_color': '#3E4C59',
                    'text_color': '#E6E1CF',
                    'text_disabled': '#8A8A8A',
                    'selected_color': '#87C05F',
                    
                    'primary': '#87C05F',
                    'secondary': '#5E8F3F',
                    'success': '#87C05F',
                    'warning': '#FFB454',
                    'error': '#FF6565',
                    'info': '#73D0FF',
                    
                    'button_fg': '#87C05F',
                    'button_hover': '#5E8F3F',
                    'button_text': '#0F1419',
                    'entry_fg': '#1A2332',
                    'entry_border': '#3E4C59',
                    'entry_text': '#E6E1CF',
                    'frame_low': '#0F1419',
                    'frame_high': '#1A2332',
                    'progressbar_progress': '#87C05F',
                    'progressbar_bg': '#3E4C59',
                    'switch_progress': '#87C05F',
                    'switch_button': '#E6E1CF',
                    'switch_bg': '#3E4C59',
                    'scrollbar_button': '#3E4C59',
                    'scrollbar_button_hover': '#5E6C7A',
                    
                    'editor_bg': '#0F1419',
                    'editor_text': '#E6E1CF',
                    'editor_cursor': '#FFB454',
                    'editor_selection': '#33415550',
                    'editor_line_numbers': '#8A8A8A',
                    'editor_current_line': '#191F2A',
                    
                    'syntax_keyword': '#FFA759',
                    'syntax_string': '#AAD94C',
                    'syntax_comment': '#626A73',
                    'syntax_number': '#D2A6FF',
                    'syntax_function': '#FFB454',
                    'syntax_class': '#73D0FF',
                    'syntax_variable': '#CBB2F7',
                    'syntax_operator': '#F29668'
                },
                'fonts': {
                    'default_family': 'Roboto',
                    'default_size': 12,
                    'title_family': 'Roboto',
                    'title_size': 18,
                    'heading_family': 'Roboto',
                    'heading_size': 14,
                    'code_family': 'Fira Code',
                    'code_size': 11
                },
                'spacing': {
                    'padding_small': 5,
                    'padding_medium': 10,
                    'padding_large': 20,
                    'corner_radius': 8,
                    'button_corner': 6,
                    'entry_corner': 6
                }
            },
            
            'academic_purple': {
                'name': 'Académico Púrpura',
                'type': 'light',
                'colors': {
                    'bg_color': '#F5F3FF',
                    'fg_color': '#FFFFFF',
                    'hover_color': '#E8E5FF',
                    'border_color': '#C7BFFF',
                    'text_color': '#1A1523',
                    'text_disabled': '#8B7FA6',
                    'selected_color': '#6B46C1',
                    
                    'primary': '#6B46C1',
                    'secondary': '#553C9A',
                    'success': '#10B981',
                    'warning': '#F59E0B',
                    'error': '#EF4444',
                    'info': '#3B82F6',
                    
                    'button_fg': '#6B46C1',
                    'button_hover': '#553C9A',
                    'button_text': '#FFFFFF',
                    'entry_fg': '#FFFFFF',
                    'entry_border': '#C7BFFF',
                    'entry_text': '#1A1523',
                    'frame_low': '#F5F3FF',
                    'frame_high': '#FFFFFF',
                    'progressbar_progress': '#6B46C1',
                    'progressbar_bg': '#C7BFFF',
                    'switch_progress': '#6B46C1',
                    'switch_button': '#FFFFFF',
                    'switch_bg': '#C7BFFF',
                    'scrollbar_button': '#C7BFFF',
                    'scrollbar_button_hover': '#A78BFA',
                    
                    'editor_bg': '#FFFFFF',
                    'editor_text': '#1A1523',
                    'editor_cursor': '#6B46C1',
                    'editor_selection': '#DDD6FE',
                    'editor_line_numbers': '#8B7FA6',
                    'editor_current_line': '#FAF9FF',
                    
                    'syntax_keyword': '#7C3AED',
                    'syntax_string': '#059669',
                    'syntax_comment': '#6B7280',
                    'syntax_number': '#DC2626',
                    'syntax_function': '#2563EB',
                    'syntax_class': '#DB2777',
                    'syntax_variable': '#7C3AED',
                    'syntax_operator': '#1A1523'
                },
                'fonts': {
                    'default_family': 'Georgia',
                    'default_size': 12,
                    'title_family': 'Georgia',
                    'title_size': 20,
                    'heading_family': 'Georgia',
                    'heading_size': 14,
                    'code_family': 'Courier New',
                    'code_size': 11
                },
                'spacing': {
                    'padding_small': 6,
                    'padding_medium': 12,
                    'padding_large': 24,
                    'corner_radius': 12,
                    'button_corner': 8,
                    'entry_corner': 8
                }
            }
        }
    
    def _load_custom_themes(self) -> Dict[str, Dict[str, Any]]:
        """Carga temas personalizados desde archivos"""
        custom_themes = {}
        
        for theme_file in self.themes_dir.glob('*.json'):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                
                if self._validate_theme(theme_data):
                    custom_themes[theme_file.stem] = theme_data
                    logger.info(f"Tema personalizado cargado: {theme_file.stem}")
                else:
                    logger.warning(f"Tema inválido: {theme_file.stem}")
                    
            except Exception as e:
                logger.error(f"Error cargando tema {theme_file}: {e}")
        
        return custom_themes
    
    def _validate_theme(self, theme: Dict[str, Any]) -> bool:
        """Valida que un tema tenga la estructura correcta"""
        required_sections = ['name', 'type', 'colors', 'fonts', 'spacing']
        required_colors = ['bg_color', 'fg_color', 'text_color', 'primary']
        
        # Verificar secciones principales
        for section in required_sections:
            if section not in theme:
                return False
        
        # Verificar colores mínimos
        for color in required_colors:
            if color not in theme.get('colors', {}):
                return False
        
        return True
    
    def get_available_themes(self) -> List[Tuple[str, str, str]]:
        """
        Obtiene lista de temas disponibles
        
        Returns:
            Lista de tuplas (id, nombre, tipo)
        """
        themes = []
        
        # Temas predefinidos
        for theme_id, theme_data in self.builtin_themes.items():
            themes.append((theme_id, theme_data['name'], theme_data['type']))
        
        # Temas personalizados
        for theme_id, theme_data in self.custom_themes.items():
            themes.append((theme_id, theme_data['name'] + ' (Custom)', theme_data['type']))
        
        return themes
    
    def apply_theme(self, theme_name: str) -> bool:
        """
        Aplica un tema a la aplicación
        
        Args:
            theme_name: Nombre del tema
            
        Returns:
            bool: True si se aplicó exitosamente
        """
        # Buscar tema
        if theme_name in self.builtin_themes:
            theme = self.builtin_themes[theme_name]
        elif theme_name in self.custom_themes:
            theme = self.custom_themes[theme_name]
        else:
            logger.error(f"Tema no encontrado: {theme_name}")
            return False
        
        try:
            # Establecer modo de apariencia
            ctk.set_appearance_mode(theme['type'])
            
            # Aplicar colores a CustomTkinter
            self._apply_ctk_theme(theme)
            
            # Guardar tema actual
            self.current_theme_name = theme_name
            self.current_theme = theme.copy()
            
            # Aplicar a la aplicación si está disponible
            if self.app:
                self._apply_to_app(theme)
            
            logger.info(f"Tema aplicado: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error aplicando tema: {e}")
            return False
    
    def _apply_ctk_theme(self, theme: Dict[str, Any]):
        """Aplica el tema a CustomTkinter"""
        # Crear diccionario de colores para CTk
        ctk_colors = {
            "window_bg_color": [theme['colors']['bg_color'], theme['colors']['bg_color']],
            "fg_color": [theme['colors']['fg_color'], theme['colors']['fg_color']],
            "hover_color": [theme['colors']['hover_color'], theme['colors']['hover_color']],
            "border_color": [theme['colors']['border_color'], theme['colors']['border_color']],
            "text_color": [theme['colors']['text_color'], theme['colors']['text_color']],
            "text_color_disabled": [theme['colors']['text_disabled'], theme['colors']['text_disabled']],
            "button": [theme['colors']['button_fg'], theme['colors']['button_fg']],
            "button_hover": [theme['colors']['button_hover'], theme['colors']['button_hover']],
            "entry": [theme['colors']['entry_fg'], theme['colors']['entry_fg']],
            "entry_border": [theme['colors']['entry_border'], theme['colors']['entry_border']],
            "frame_border": [theme['colors']['border_color'], theme['colors']['border_color']],
            "frame_low": [theme['colors']['frame_low'], theme['colors']['frame_low']],
            "frame_high": [theme['colors']['frame_high'], theme['colors']['frame_high']],
            "progressbar": [theme['colors']['progressbar_bg'], theme['colors']['progressbar_bg']],
            "progressbar_progress": [theme['colors']['progressbar_progress'], theme['colors']['progressbar_progress']],
            "switch": [theme['colors']['switch_bg'], theme['colors']['switch_bg']],
            "switch_progress": [theme['colors']['switch_progress'], theme['colors']['switch_progress']],
            "switch_button": [theme['colors']['switch_button'], theme['colors']['switch_button']],
            "scrollbar_button": [theme['colors']['scrollbar_button'], theme['colors']['scrollbar_button']],
            "scrollbar_button_hover": [theme['colors']['scrollbar_button_hover'], theme['colors']['scrollbar_button_hover']]
        }
        
        # Guardar tema personalizado temporalmente
        theme_file = self.themes_dir / '_temp_theme.json'
        with open(theme_file, 'w') as f:
            json.dump(ctk_colors, f)
        
        # Aplicar tema
        ctk.set_default_color_theme(str(theme_file))
    
    def _apply_to_app(self, theme: Dict[str, Any]):
        """Aplica el tema a la aplicación"""
        if not self.app:
            return
        
        # Actualizar ventana principal
        if hasattr(self.app, 'root'):
            self.app.root.configure(fg_color=theme['colors']['bg_color'])
        
        # Actualizar todos los widgets recursivamente
        self._update_widget_theme(self.app.root, theme)
    
    def _update_widget_theme(self, widget, theme: Dict[str, Any]):
        """Actualiza el tema de un widget y sus hijos recursivamente"""
        colors = theme['colors']
        
        # Actualizar según tipo de widget
        if isinstance(widget, ctk.CTkFrame):
            widget.configure(fg_color=colors['frame_high'])
        elif isinstance(widget, ctk.CTkButton):
            widget.configure(
                fg_color=colors['button_fg'],
                hover_color=colors['button_hover'],
                text_color=colors['button_text']
            )
        elif isinstance(widget, ctk.CTkEntry):
            widget.configure(
                fg_color=colors['entry_fg'],
                border_color=colors['entry_border'],
                text_color=colors['entry_text']
            )
        elif isinstance(widget, ctk.CTkLabel):
            widget.configure(text_color=colors['text_color'])
        elif isinstance(widget, ctk.CTkTextbox):
            widget.configure(
                fg_color=colors['editor_bg'],
                text_color=colors['editor_text']
            )
        
        # Actualizar hijos
        for child in widget.winfo_children():
            self._update_widget_theme(child, theme)
    
    def create_custom_theme(self, name: str, base_theme: str = None) -> bool:
        """
        Crea un nuevo tema personalizado
        
        Args:
            name: Nombre del tema
            base_theme: Tema base (opcional)
            
        Returns:
            bool: True si se creó exitosamente
        """
        # Usar tema base o default
        if base_theme and base_theme in self.builtin_themes:
            new_theme = self.builtin_themes[base_theme].copy()
        else:
            new_theme = self.builtin_themes['default_dark'].copy()
        
        # Actualizar nombre
        new_theme['name'] = name
        
        # Guardar
        theme_file = self.themes_dir / f"{name.lower().replace(' ', '_')}.json"
        
        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(new_theme, f, ensure_ascii=False, indent=2)
            
            # Agregar a temas personalizados
            self.custom_themes[theme_file.stem] = new_theme
            
            logger.info(f"Tema personalizado creado: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando tema: {e}")
            return False
    
    def edit_theme_color(self, theme_name: str, color_key: str, color_value: str):
        """
        Edita un color en un tema personalizado
        
        Args:
            theme_name: Nombre del tema
            color_key: Clave del color
            color_value: Nuevo valor del color
        """
        if theme_name not in self.custom_themes:
            logger.error(f"Solo se pueden editar temas personalizados")
            return
        
        theme = self.custom_themes[theme_name]
        
        if 'colors' in theme and color_key in theme['colors']:
            theme['colors'][color_key] = color_value
            
            # Guardar cambios
            theme_file = self.themes_dir / f"{theme_name}.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme, f, ensure_ascii=False, indent=2)
            
            # Si es el tema actual, reaplicar
            if theme_name == self.current_theme_name:
                self.apply_theme(theme_name)
    
    def delete_custom_theme(self, theme_name: str) -> bool:
        """
        Elimina un tema personalizado
        
        Args:
            theme_name: Nombre del tema
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        if theme_name not in self.custom_themes:
            logger.error("Solo se pueden eliminar temas personalizados")
            return False
        
        try:
            # Eliminar archivo
            theme_file = self.themes_dir / f"{theme_name}.json"
            if theme_file.exists():
                theme_file.unlink()
            
            # Eliminar de diccionario
            del self.custom_themes[theme_name]
            
            # Si era el tema actual, cambiar a default
            if theme_name == self.current_theme_name:
                self.apply_theme('default_dark')
            
            logger.info(f"Tema eliminado: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando tema: {e}")
            return False
    
    def export_theme(self, theme_name: str, filepath: str) -> bool:
        """
        Exporta un tema a archivo
        
        Args:
            theme_name: Nombre del tema
            filepath: Ruta del archivo
            
        Returns:
            bool: True si se exportó exitosamente
        """
        # Buscar tema
        if theme_name in self.builtin_themes:
            theme = self.builtin_themes[theme_name]
        elif theme_name in self.custom_themes:
            theme = self.custom_themes[theme_name]
        else:
            logger.error(f"Tema no encontrado: {theme_name}")
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(theme, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Tema exportado: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando tema: {e}")
            return False
    
    def import_theme(self, filepath: str) -> Optional[str]:
        """
        Importa un tema desde archivo
        
        Args:
            filepath: Ruta del archivo
            
        Returns:
            str: Nombre del tema importado o None si falló
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme = json.load(f)
            
            if not self._validate_theme(theme):
                logger.error("Tema inválido")
                return None
            
            # Generar nombre único
            base_name = theme['name']
            name = base_name
            counter = 1
            
            while name.lower().replace(' ', '_') in self.custom_themes:
                name = f"{base_name} ({counter})"
                counter += 1
            
            # Actualizar nombre
            theme['name'] = name
            
            # Guardar
            theme_id = name.lower().replace(' ', '_')
            theme_file = self.themes_dir / f"{theme_id}.json"
            
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme, f, ensure_ascii=False, indent=2)
            
            # Agregar a temas
            self.custom_themes[theme_id] = theme
            
            logger.info(f"Tema importado: {name}")
            return theme_id
            
        except Exception as e:
            logger.error(f"Error importando tema: {e}")
            return None
    
    def get_theme_preview(self, theme_name: str) -> Dict[str, str]:
        """
        Obtiene una vista previa de colores del tema
        
        Args:
            theme_name: Nombre del tema
            
        Returns:
            Dict con colores principales
        """
        # Buscar tema
        if theme_name in self.builtin_themes:
            theme = self.builtin_themes[theme_name]
        elif theme_name in self.custom_themes:
            theme = self.custom_themes[theme_name]
        else:
            return {}
        
        colors = theme.get('colors', {})
        
        return {
            'background': colors.get('bg_color', '#000000'),
            'foreground': colors.get('fg_color', '#111111'),
            'primary': colors.get('primary', '#0066CC'),
            'text': colors.get('text_color', '#FFFFFF'),
            'success': colors.get('success', '#00AA00'),
            'warning': colors.get('warning', '#FFAA00'),
            'error': colors.get('error', '#FF0000')
        }
    
    def generate_color_variations(self, base_color: str, count: int = 5) -> List[str]:
        """
        Genera variaciones de un color base
        
        Args:
            base_color: Color base en formato hex
            count: Número de variaciones
            
        Returns:
            Lista de colores en formato hex
        """
        # Convertir hex a RGB
        base_color = base_color.lstrip('#')
        r, g, b = tuple(int(base_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Convertir a HSV
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        variations = []
        
        for i in range(count):
            # Variar luminosidad
            factor = 0.5 + (i / count)
            new_v = min(1.0, v * factor)
            
            # Convertir de vuelta a RGB
            new_r, new_g, new_b = colorsys.hsv_to_rgb(h, s, new_v)
            
            # Convertir a hex
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(new_r * 255),
                int(new_g * 255),
                int(new_b * 255)
            )
            
            variations.append(hex_color)
        
        return variations