"""
Sistema de comentarios y notas para el proyecto académico
Permite agregar anotaciones, comentarios y recordatorios
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import customtkinter as ctk
from tkinter import messagebox
import uuid
from utils.logger import get_logger

logger = get_logger('NotesComments')

class NotesCommentsManager:
    """Gestor de notas y comentarios"""
    
    def __init__(self):
        self.notes = {}  # {note_id: note_data}
        self.comments = {}  # {section_id: [comments]}
        self.reminders = []  # Lista de recordatorios
        
        # Tipos de notas
        self.note_types = {
            'idea': {'icon': '💡', 'color': 'yellow'},
            'todo': {'icon': '📋', 'color': 'blue'},
            'important': {'icon': '⚠️', 'color': 'red'},
            'reference': {'icon': '📚', 'color': 'green'},
            'question': {'icon': '❓', 'color': 'purple'},
            'revision': {'icon': '✏️', 'color': 'orange'}
        }
        
        logger.info("NotesCommentsManager inicializado")
    
    def add_note(self, section_id: str, text: str, note_type: str = 'idea',
                 position: Optional[Tuple[str, str]] = None) -> str:
        """
        Agrega una nota
        
        Args:
            section_id: ID de la sección
            text: Texto de la nota
            note_type: Tipo de nota
            position: Posición en el texto (inicio, fin)
            
        Returns:
            ID de la nota creada
        """
        note_id = str(uuid.uuid4())
        
        note_data = {
            'id': note_id,
            'section_id': section_id,
            'text': text,
            'type': note_type,
            'position': position,
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'resolved': False,
            'tags': [],
            'priority': 'normal'
        }
        
        self.notes[note_id] = note_data
        
        logger.info(f"Nota agregada: {note_id} en sección {section_id}")
        
        return note_id
    
    def add_comment(self, section_id: str, text: str, parent_id: Optional[str] = None) -> str:
        """
        Agrega un comentario a una sección
        
        Args:
            section_id: ID de la sección
            text: Texto del comentario
            parent_id: ID del comentario padre (para respuestas)
            
        Returns:
            ID del comentario
        """
        comment_id = str(uuid.uuid4())
        
        comment_data = {
            'id': comment_id,
            'text': text,
            'parent_id': parent_id,
            'created': datetime.now().isoformat(),
            'author': 'Usuario',  # En versión multiusuario, usar ID real
            'resolved': False,
            'replies': []
        }
        
        if section_id not in self.comments:
            self.comments[section_id] = []
        
        if parent_id:
            # Buscar comentario padre y agregar respuesta
            for comment in self.comments[section_id]:
                if comment['id'] == parent_id:
                    comment['replies'].append(comment_id)
                    break
        
        self.comments[section_id].append(comment_data)
        
        logger.info(f"Comentario agregado: {comment_id} en sección {section_id}")
        
        return comment_id
    
    def add_reminder(self, text: str, due_date: datetime, section_id: Optional[str] = None) -> str:
        """
        Agrega un recordatorio
        
        Args:
            text: Texto del recordatorio
            due_date: Fecha de vencimiento
            section_id: Sección relacionada (opcional)
            
        Returns:
            ID del recordatorio
        """
        reminder_id = str(uuid.uuid4())
        
        reminder_data = {
            'id': reminder_id,
            'text': text,
            'due_date': due_date.isoformat(),
            'section_id': section_id,
            'created': datetime.now().isoformat(),
            'completed': False,
            'priority': 'normal'
        }
        
        self.reminders.append(reminder_data)
        
        # Ordenar por fecha
        self.reminders.sort(key=lambda x: x['due_date'])
        
        logger.info(f"Recordatorio agregado: {reminder_id}")
        
        return reminder_id
    
    def get_notes_for_section(self, section_id: str) -> List[Dict]:
        """Obtiene todas las notas de una sección"""
        return [note for note in self.notes.values() if note['section_id'] == section_id]
    
    def get_comments_for_section(self, section_id: str) -> List[Dict]:
        """Obtiene todos los comentarios de una sección"""
        return self.comments.get(section_id, [])
    
    def get_pending_reminders(self) -> List[Dict]:
        """Obtiene recordatorios pendientes"""
        now = datetime.now()
        return [
            r for r in self.reminders 
            if not r['completed'] and datetime.fromisoformat(r['due_date']) > now
        ]
    
    def get_overdue_reminders(self) -> List[Dict]:
        """Obtiene recordatorios vencidos"""
        now = datetime.now()
        return [
            r for r in self.reminders 
            if not r['completed'] and datetime.fromisoformat(r['due_date']) <= now
        ]
    
    def update_note(self, note_id: str, **kwargs):
        """Actualiza una nota"""
        if note_id in self.notes:
            self.notes[note_id].update(kwargs)
            self.notes[note_id]['modified'] = datetime.now().isoformat()
            logger.info(f"Nota actualizada: {note_id}")
    
    def delete_note(self, note_id: str):
        """Elimina una nota"""
        if note_id in self.notes:
            del self.notes[note_id]
            logger.info(f"Nota eliminada: {note_id}")
    
    def resolve_note(self, note_id: str):
        """Marca una nota como resuelta"""
        if note_id in self.notes:
            self.notes[note_id]['resolved'] = True
            self.notes[note_id]['resolved_date'] = datetime.now().isoformat()
    
    def search_notes(self, query: str) -> List[Dict]:
        """Busca notas por texto"""
        query_lower = query.lower()
        results = []
        
        for note in self.notes.values():
            if query_lower in note['text'].lower():
                results.append(note)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas de notas y comentarios"""
        total_notes = len(self.notes)
        resolved_notes = len([n for n in self.notes.values() if n['resolved']])
        
        notes_by_type = {}
        for note_type in self.note_types:
            notes_by_type[note_type] = len([
                n for n in self.notes.values() if n['type'] == note_type
            ])
        
        total_comments = sum(len(comments) for comments in self.comments.values())
        total_reminders = len(self.reminders)
        pending_reminders = len(self.get_pending_reminders())
        overdue_reminders = len(self.get_overdue_reminders())
        
        return {
            'total_notes': total_notes,
            'resolved_notes': resolved_notes,
            'pending_notes': total_notes - resolved_notes,
            'notes_by_type': notes_by_type,
            'total_comments': total_comments,
            'total_reminders': total_reminders,
            'pending_reminders': pending_reminders,
            'overdue_reminders': overdue_reminders
        }
    
    def export_notes(self) -> Dict:
        """Exporta todas las notas y comentarios"""
        return {
            'notes': self.notes,
            'comments': self.comments,
            'reminders': self.reminders,
            'exported_date': datetime.now().isoformat()
        }
    
    def import_notes(self, data: Dict):
        """Importa notas y comentarios"""
        if 'notes' in data:
            self.notes.update(data['notes'])
        
        if 'comments' in data:
            for section_id, comments in data['comments'].items():
                if section_id not in self.comments:
                    self.comments[section_id] = []
                self.comments[section_id].extend(comments)
        
        if 'reminders' in data:
            self.reminders.extend(data['reminders'])
            self.reminders.sort(key=lambda x: x['due_date'])
        
        logger.info("Notas y comentarios importados")


class NotesPanel(ctk.CTkFrame):
    """Panel lateral de notas para la interfaz"""
    
    def __init__(self, parent, app_instance, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.app_instance = app_instance
        self.notes_manager = NotesCommentsManager()
        self.current_section_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del panel"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="gray25", height=40)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="📝 Notas y Comentarios",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        # Botón agregar
        ctk.CTkButton(
            header_frame,
            text="➕",
            width=30,
            height=30,
            command=self.add_note_dialog
        ).pack(side="right", padx=5)
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, height=300)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab de notas
        notes_tab = self.tabview.add("📝 Notas")
        self.setup_notes_tab(notes_tab)
        
        # Tab de comentarios
        comments_tab = self.tabview.add("💬 Comentarios")
        self.setup_comments_tab(comments_tab)
        
        # Tab de recordatorios
        reminders_tab = self.tabview.add("⏰ Recordatorios")
        self.setup_reminders_tab(reminders_tab)
        
        # Estadísticas
        self.stats_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.stats_label.pack(pady=5)
        
        self.update_stats()
    
    def setup_notes_tab(self, parent):
        """Configura la pestaña de notas"""
        # Filtros
        filter_frame = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        filter_frame.pack(fill="x")
        
        self.filter_type = ctk.CTkComboBox(
            filter_frame,
            values=["Todas"] + list(self.notes_manager.note_types.keys()),
            width=100,
            height=25,
            command=self.filter_notes
        )
        self.filter_type.pack(side="left", padx=5)
        self.filter_type.set("Todas")
        
        self.show_resolved_var = ctk.CTkCheckBox(
            filter_frame,
            text="Mostrar resueltas",
            height=25,
            command=self.filter_notes
        )
        self.show_resolved_var.pack(side="left", padx=5)
        
        # Lista de notas
        self.notes_scroll = ctk.CTkScrollableFrame(parent)
        self.notes_scroll.pack(fill="both", expand=True, pady=(5, 0))
    
    def setup_comments_tab(self, parent):
        """Configura la pestaña de comentarios"""
        # Input de comentario
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", pady=(5, 10))
        
        self.comment_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Agregar comentario..."
        )
        self.comment_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.comment_entry.bind("<Return>", lambda e: self.add_comment())
        
        ctk.CTkButton(
            input_frame,
            text="➤",
            width=30,
            command=self.add_comment
        ).pack(side="right")
        
        # Lista de comentarios
        self.comments_scroll = ctk.CTkScrollableFrame(parent)
        self.comments_scroll.pack(fill="both", expand=True)
    
    def setup_reminders_tab(self, parent):
        """Configura la pestaña de recordatorios"""
        # Botón agregar recordatorio
        ctk.CTkButton(
            parent,
            text="➕ Agregar Recordatorio",
            command=self.add_reminder_dialog
        ).pack(pady=10)
        
        # Lista de recordatorios
        self.reminders_scroll = ctk.CTkScrollableFrame(parent)
        self.reminders_scroll.pack(fill="both", expand=True)
    
    def set_current_section(self, section_id: str):
        """Establece la sección actual"""
        self.current_section_id = section_id
        self.refresh_all()
    
    def refresh_all(self):
        """Actualiza todas las vistas"""
        self.refresh_notes()
        self.refresh_comments()
        self.refresh_reminders()
        self.update_stats()
    
    def refresh_notes(self):
        """Actualiza la lista de notas"""
        # Limpiar lista
        for widget in self.notes_scroll.winfo_children():
            widget.destroy()
        
        if not self.current_section_id:
            return
        
        # Obtener notas de la sección
        notes = self.notes_manager.get_notes_for_section(self.current_section_id)
        
        # Filtrar
        filter_type = self.filter_type.get()
        show_resolved = self.show_resolved_var.get()
        
        for note in notes:
            # Aplicar filtros
            if filter_type != "Todas" and note['type'] != filter_type:
                continue
            
            if not show_resolved and note['resolved']:
                continue
            
            # Crear widget de nota
            self.create_note_widget(note)
    
    def create_note_widget(self, note: Dict):
        """Crea un widget para mostrar una nota"""
        note_frame = ctk.CTkFrame(
            self.notes_scroll,
            fg_color="gray20" if not note['resolved'] else "gray30",
            corner_radius=8
        )
        note_frame.pack(fill="x", pady=5)
        
        # Header
        header_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Tipo y fecha
        type_info = self.notes_manager.note_types[note['type']]
        type_label = ctk.CTkLabel(
            header_frame,
            text=f"{type_info['icon']} {note['type'].title()}",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        type_label.pack(side="left")
        
        date_label = ctk.CTkLabel(
            header_frame,
            text=datetime.fromisoformat(note['created']).strftime("%d/%m %H:%M"),
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        date_label.pack(side="right")
        
        # Texto
        text_label = ctk.CTkLabel(
            note_frame,
            text=note['text'],
            wraplength=250,
            justify="left",
            font=ctk.CTkFont(size=11)
        )
        text_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Botones
        if not note['resolved']:
            btn_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            ctk.CTkButton(
                btn_frame,
                text="✓",
                width=30,
                height=25,
                command=lambda n=note: self.resolve_note(n['id']),
                fg_color="green",
                hover_color="darkgreen"
            ).pack(side="left", padx=(0, 5))
            
            ctk.CTkButton(
                btn_frame,
                text="✏️",
                width=30,
                height=25,
                command=lambda n=note: self.edit_note(n['id'])
            ).pack(side="left", padx=(0, 5))
            
            ctk.CTkButton(
                btn_frame,
                text="🗑️",
                width=30,
                height=25,
                command=lambda n=note: self.delete_note(n['id']),
                fg_color="red",
                hover_color="darkred"
            ).pack(side="left")
    
    def refresh_comments(self):
        """Actualiza la lista de comentarios"""
        # Limpiar lista
        for widget in self.comments_scroll.winfo_children():
            widget.destroy()
        
        if not self.current_section_id:
            return
        
        # Obtener comentarios
        comments = self.notes_manager.get_comments_for_section(self.current_section_id)
        
        # Mostrar comentarios
        for comment in comments:
            if not comment['parent_id']:  # Solo comentarios principales
                self.create_comment_widget(comment, comments)
    
    def create_comment_widget(self, comment: Dict, all_comments: List[Dict], level: int = 0):
        """Crea un widget para mostrar un comentario"""
        comment_frame = ctk.CTkFrame(
            self.comments_scroll,
            fg_color="gray20" if level == 0 else "gray25",
            corner_radius=8
        )
        comment_frame.pack(fill="x", pady=5, padx=(level * 20, 0))
        
        # Header
        header_frame = ctk.CTkFrame(comment_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        author_label = ctk.CTkLabel(
            header_frame,
            text=comment['author'],
            font=ctk.CTkFont(size=11, weight="bold")
        )
        author_label.pack(side="left")
        
        date_label = ctk.CTkLabel(
            header_frame,
            text=datetime.fromisoformat(comment['created']).strftime("%d/%m %H:%M"),
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        date_label.pack(side="right")
        
        # Texto
        text_label = ctk.CTkLabel(
            comment_frame,
            text=comment['text'],
            wraplength=250 - (level * 20),
            justify="left",
            font=ctk.CTkFont(size=11)
        )
        text_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Botón responder
        if level < 3:  # Limitar profundidad de respuestas
            ctk.CTkButton(
                comment_frame,
                text="Responder",
                height=25,
                command=lambda c=comment: self.reply_to_comment(c['id'])
            ).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Mostrar respuestas
        for reply_id in comment['replies']:
            for reply in all_comments:
                if reply['id'] == reply_id:
                    self.create_comment_widget(reply, all_comments, level + 1)
                    break
    
    def refresh_reminders(self):
        """Actualiza la lista de recordatorios"""
        # Limpiar lista
        for widget in self.reminders_scroll.winfo_children():
            widget.destroy()
        
        # Obtener recordatorios
        overdue = self.notes_manager.get_overdue_reminders()
        pending = self.notes_manager.get_pending_reminders()
        
        # Mostrar vencidos
        if overdue:
            ctk.CTkLabel(
                self.reminders_scroll,
                text="⚠️ Vencidos",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="red"
            ).pack(anchor="w", pady=(10, 5))
            
            for reminder in overdue:
                self.create_reminder_widget(reminder, is_overdue=True)
        
        # Mostrar pendientes
        if pending:
            ctk.CTkLabel(
                self.reminders_scroll,
                text="📅 Pendientes",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", pady=(10, 5))
            
            for reminder in pending:
                self.create_reminder_widget(reminder, is_overdue=False)
    
    def create_reminder_widget(self, reminder: Dict, is_overdue: bool):
        """Crea un widget para mostrar un recordatorio"""
        reminder_frame = ctk.CTkFrame(
            self.reminders_scroll,
            fg_color="darkred" if is_overdue else "gray20",
            corner_radius=8
        )
        reminder_frame.pack(fill="x", pady=5)
        
        # Fecha
        due_date = datetime.fromisoformat(reminder['due_date'])
        date_text = due_date.strftime("%d/%m/%Y %H:%M")
        
        if is_overdue:
            days_overdue = (datetime.now() - due_date).days
            date_text += f" ({days_overdue}d vencido)"
        
        date_label = ctk.CTkLabel(
            reminder_frame,
            text=date_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white" if is_overdue else "orange"
        )
        date_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Texto
        text_label = ctk.CTkLabel(
            reminder_frame,
            text=reminder['text'],
            wraplength=250,
            justify="left",
            font=ctk.CTkFont(size=11)
        )
        text_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Botones
        btn_frame = ctk.CTkFrame(reminder_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="✓ Completar",
            height=25,
            command=lambda r=reminder: self.complete_reminder(r['id']),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=30,
            height=25,
            command=lambda r=reminder: self.delete_reminder(r['id']),
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left")
    
    def update_stats(self):
        """Actualiza las estadísticas"""
        stats = self.notes_manager.get_statistics()
        
        stats_text = f"📊 {stats['total_notes']} notas ({stats['pending_notes']} pendientes) | "
        stats_text += f"💬 {stats['total_comments']} comentarios | "
        stats_text += f"⏰ {stats['pending_reminders']} recordatorios"
        
        if stats['overdue_reminders'] > 0:
            stats_text += f" ({stats['overdue_reminders']} vencidos)"
        
        self.stats_label.configure(text=stats_text)
    
    def add_note_dialog(self):
        """Muestra diálogo para agregar nota"""
        if not self.current_section_id:
            messagebox.showwarning("Sin sección", "Seleccione una sección primero")
            return
        
        dialog = NoteDialog(self, self.notes_manager)
        self.wait_window(dialog)
        
        if dialog.result:
            note_id = self.notes_manager.add_note(
                self.current_section_id,
                dialog.result['text'],
                dialog.result['type']
            )
            self.refresh_notes()
    
    def add_comment(self):
        """Agrega un comentario"""
        text = self.comment_entry.get().strip()
        if not text or not self.current_section_id:
            return
        
        self.notes_manager.add_comment(self.current_section_id, text)
        self.comment_entry.delete(0, "end")
        self.refresh_comments()
    
    def add_reminder_dialog(self):
        """Muestra diálogo para agregar recordatorio"""
        dialog = ReminderDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            self.notes_manager.add_reminder(
                dialog.result['text'],
                dialog.result['due_date'],
                self.current_section_id
            )
            self.refresh_reminders()
    
    def resolve_note(self, note_id: str):
        """Marca una nota como resuelta"""
        self.notes_manager.resolve_note(note_id)
        self.refresh_notes()
    
    def edit_note(self, note_id: str):
        """Edita una nota"""
        # Implementar diálogo de edición
        pass
    
    def delete_note(self, note_id: str):
        """Elimina una nota"""
        if messagebox.askyesno("Confirmar", "¿Eliminar esta nota?"):
            self.notes_manager.delete_note(note_id)
            self.refresh_notes()
    
    def reply_to_comment(self, parent_id: str):
        """Responde a un comentario"""
        # Implementar diálogo de respuesta
        pass
    
    def complete_reminder(self, reminder_id: str):
        """Marca un recordatorio como completado"""
        for reminder in self.notes_manager.reminders:
            if reminder['id'] == reminder_id:
                reminder['completed'] = True
                reminder['completed_date'] = datetime.now().isoformat()
                break
        
        self.refresh_reminders()
    
    def delete_reminder(self, reminder_id: str):
        """Elimina un recordatorio"""
        self.notes_manager.reminders = [
            r for r in self.notes_manager.reminders if r['id'] != reminder_id
        ]
        self.refresh_reminders()
    
    def filter_notes(self, *args):
        """Filtra las notas según los criterios"""
        self.refresh_notes()


class NoteDialog(ctk.CTkToplevel):
    """Diálogo para agregar/editar notas"""
    
    def __init__(self, parent, notes_manager):
        super().__init__(parent)
        
        self.notes_manager = notes_manager
        self.result = None
        
        self.title("➕ Agregar Nota")
        self.geometry("400x350")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tipo de nota
        ctk.CTkLabel(
            main_frame,
            text="Tipo de nota:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        type_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=(0, 15))
        
        self.type_var = ctk.StringVar(value="idea")
        
        for i, (note_type, info) in enumerate(self.notes_manager.note_types.items()):
            ctk.CTkRadioButton(
                type_frame,
                text=f"{info['icon']} {note_type.title()}",
                variable=self.type_var,
                value=note_type
            ).grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=5)
        
        # Texto
        ctk.CTkLabel(
            main_frame,
            text="Texto de la nota:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.text_widget = ctk.CTkTextbox(main_frame, height=100)
        self.text_widget.pack(fill="both", expand=True, pady=(0, 15))
        
        # Tags (opcional)
        ctk.CTkLabel(
            main_frame,
            text="Tags (separados por comas):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.tags_entry = ctk.CTkEntry(main_frame, placeholder_text="revisar, importante, cita")
        self.tags_entry.pack(fill="x", pady=(0, 20))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Agregar",
            command=self.add_note
        ).pack(side="right")
    
    def add_note(self):
        """Agrega la nota"""
        text = self.text_widget.get("1.0", "end-1c").strip()
        
        if not text:
            messagebox.showerror("Error", "El texto no puede estar vacío")
            return
        
        tags = [tag.strip() for tag in self.tags_entry.get().split(",") if tag.strip()]
        
        self.result = {
            'text': text,
            'type': self.type_var.get(),
            'tags': tags
        }
        
        self.destroy()


class ReminderDialog(ctk.CTkToplevel):
    """Diálogo para agregar recordatorios"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.result = None
        
        self.title("⏰ Agregar Recordatorio")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Texto
        ctk.CTkLabel(
            main_frame,
            text="Recordatorio:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.text_widget = ctk.CTkTextbox(main_frame, height=80)
        self.text_widget.pack(fill="x", pady=(0, 15))
        
        # Fecha y hora
        datetime_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        datetime_frame.pack(fill="x", pady=(0, 15))
        
        # Fecha
        date_frame = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        date_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            date_frame,
            text="Fecha:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.date_entry = ctk.CTkEntry(
            date_frame,
            placeholder_text="DD/MM/AAAA"
        )
        self.date_entry.pack(fill="x")
        
        # Hora
        time_frame = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        time_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            time_frame,
            text="Hora:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        self.time_entry = ctk.CTkEntry(
            time_frame,
            placeholder_text="HH:MM"
        )
        self.time_entry.pack(fill="x")
        
        # Prioridad
        ctk.CTkLabel(
            main_frame,
            text="Prioridad:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.priority_var = ctk.StringVar(value="normal")
        priority_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        priority_frame.pack(fill="x", pady=(0, 20))
        
        for priority, color in [("baja", "green"), ("normal", "orange"), ("alta", "red")]:
            ctk.CTkRadioButton(
                priority_frame,
                text=priority.title(),
                variable=self.priority_var,
                value=priority
            ).pack(side="left", padx=10)
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Agregar",
            command=self.add_reminder
        ).pack(side="right")
        
        # Establecer fecha/hora por defecto (mañana a las 9:00)
        tomorrow = datetime.now() + timedelta(days=1)
        self.date_entry.insert(0, tomorrow.strftime("%d/%m/%Y"))
        self.time_entry.insert(0, "09:00")
    
    def add_reminder(self):
        """Agrega el recordatorio"""
        text = self.text_widget.get("1.0", "end-1c").strip()
        
        if not text:
            messagebox.showerror("Error", "El texto no puede estar vacío")
            return
        
        # Parsear fecha y hora
        try:
            date_str = self.date_entry.get()
            time_str = self.time_entry.get()
            
            datetime_str = f"{date_str} {time_str}"
            due_date = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M")
            
            if due_date <= datetime.now():
                messagebox.showerror("Error", "La fecha debe ser futura")
                return
            
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha/hora inválido")
            return
        
        self.result = {
            'text': text,
            'due_date': due_date,
            'priority': self.priority_var.get()
        }
        
        self.destroy()