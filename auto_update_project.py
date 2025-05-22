#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Actualizador del Proyecto - Aplica cambios de código automáticamente
Aplica las mejoras sugeridas de forma segura con backup y rollback
"""

import os
import shutil
import json
import re
from datetime import datetime
from pathlib import Path

class ProjectAutoUpdater:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(self.script_dir, "backups", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.changes_log = []
        self.files_to_update = {
            'ui/main_window.py': 'update_main_window',
            'core/document_generator.py': 'update_document_generator',
            'core/validator.py': 'update_validator'
        }
        
        # Crear directorio de backup
        os.makedirs(self.backup_dir, exist_ok=True)
        
        print("🔧 AUTOMATIZADOR DE CAMBIOS DEL PROYECTO")
        print("=" * 50)
        print(f"📁 Directorio base: {self.script_dir}")
        print(f"💾 Backup en: {self.backup_dir}")
        print()

    def create_backup(self, file_path):
        """Crea backup de un archivo antes de modificarlo"""
        try:
            if os.path.exists(file_path):
                backup_path = os.path.join(self.backup_dir, os.path.relpath(file_path, self.script_dir))
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copy2(file_path, backup_path)
                print(f"💾 Backup creado: {os.path.relpath(file_path, self.script_dir)}")
                return True
            else:
                print(f"⚠️ Archivo no encontrado: {file_path}")
                return False
        except Exception as e:
            print(f"❌ Error creando backup de {file_path}: {e}")
            return False

    def verify_file_structure(self):
        """Verifica que los archivos necesarios existan"""
        print("🔍 VERIFICANDO ESTRUCTURA DE ARCHIVOS")
        missing_files = []
        
        for file_path in self.files_to_update.keys():
            full_path = os.path.join(self.script_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
            else:
                print(f"✅ {file_path}")
        
        if missing_files:
            print(f"❌ Archivos faltantes: {missing_files}")
            return False
        
        print("✅ Estructura de archivos verificada\n")
        return True

    def update_main_window(self):
        """Actualiza ui/main_window.py con las mejoras"""
        file_path = os.path.join(self.script_dir, 'ui', 'main_window.py')
        
        if not self.create_backup(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Actualizar buscar_imagenes_base
            old_buscar_imagenes = r'def buscar_imagenes_base\(self\):.*?except Exception as e:.*?print\(f"Error buscando imágenes base: {e}"\)'
            new_buscar_imagenes = '''def buscar_imagenes_base(self):
        """Busca imágenes base en la carpeta resources/images"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Actualizar ruta a resources/images
            recursos_dir = os.path.join(script_dir, "..", "resources", "images")
            recursos_dir = os.path.normpath(recursos_dir)
            
            print(f"🔍 Buscando imágenes en: {recursos_dir}")
            
            # Crear directorio si no existe
            if not os.path.exists(recursos_dir):
                os.makedirs(recursos_dir)
                print(f"📁 Directorio creado: {recursos_dir}")
            
            # Buscar encabezado con múltiples extensiones
            encabezado_extensions = ['Encabezado.png', 'Encabezado.jpg', 'Encabezado.jpeg', 'encabezado.png']
            for filename in encabezado_extensions:
                encabezado_path = os.path.join(recursos_dir, filename)
                if os.path.exists(encabezado_path):
                    self.ruta_encabezado = encabezado_path
                    print(f"✅ Encabezado encontrado: {filename}")
                    break
            else:
                print("⚠️ Encabezado.png no encontrado en resources/images")
            
            # Buscar insignia con múltiples extensiones
            insignia_extensions = ['Insignia.png', 'Insignia.jpg', 'Insignia.jpeg', 'insignia.png']
            for filename in insignia_extensions:
                insignia_path = os.path.join(recursos_dir, filename)
                if os.path.exists(insignia_path):
                    self.ruta_insignia = insignia_path
                    print(f"✅ Insignia encontrada: {filename}")
                    break
            else:
                print("⚠️ Insignia.png no encontrada en resources/images")
                
        except Exception as e:
            print(f"❌ Error buscando imágenes base: {e}")
            messagebox.showwarning("⚠️ Imágenes", 
                f"Error al buscar imágenes base:\\n{str(e)}\\n\\n"
                f"Coloca las imágenes en: resources/images/\\n"
                f"• Encabezado.png\\n• Insignia.png")'''
            
            # Aplicar cambio con regex más flexible
            content = re.sub(old_buscar_imagenes, new_buscar_imagenes, content, flags=re.DOTALL)
            
            # Actualizar método gestionar_imagenes (solo la parte de información de rutas)
            old_path_info = r'# Estado de imágenes base.*?recursos_dir = os\.path\.join\(script_dir, "..", "Recursos"\)'
            new_path_info = '''# Información de rutas actualizadas
        path_frame = ctk.CTkFrame(main_frame, fg_color="darkblue", corner_radius=10)
        path_frame.pack(fill="x", pady=(0, 15))
        
        path_title = ctk.CTkLabel(
            path_frame, text="📂 Ubicación de Imágenes Base",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        path_title.pack(pady=(10, 5))
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        recursos_dir = os.path.join(script_dir, "..", "resources", "images")'''
            
            content = re.sub(old_path_info, new_path_info, content, flags=re.DOTALL)
            
            # Guardar archivo actualizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.changes_log.append("✅ ui/main_window.py - Actualizada búsqueda de imágenes")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando main_window.py: {e}")
            return False

    def update_document_generator(self):
        """Actualiza core/document_generator.py con mejoras de texto en negrita"""
        file_path = os.path.join(self.script_dir, 'core', 'document_generator.py')
        
        if not self.create_backup(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar y reemplazar el método crear_portada_profesional
            old_portada_method = r'def crear_portada_profesional\(self, doc, app_instance\):.*?doc\.add_page_break\(\)'
            
            new_portada_method = '''def crear_portada_profesional(self, doc, app_instance):
        """Crea portada profesional con formato de texto mejorado y negrita"""
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
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run("LOGO/EMBLEMA DE LA INSTITUCIÓN")
                run.bold = True
                run.font.size = Pt(14)
        else:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run("LOGO/EMBLEMA DE LA INSTITUCIÓN")
            run.bold = True
            run.font.size = Pt(14)
        
        # Espaciado
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Institución - MEJORADO
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(app_instance.proyecto_data['institucion'].get().upper())
        run.bold = True
        run.font.name = app_instance.formato_config['fuente_titulo']
        run.font.size = Pt(app_instance.formato_config['tamaño_titulo'] + 2)
        
        doc.add_paragraph()
        
        # Título del proyecto - MEJORADO
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f'"{app_instance.proyecto_data["titulo"].get()}"')
        run.bold = True
        run.font.name = app_instance.formato_config['fuente_titulo']
        run.font.size = Pt(app_instance.formato_config['tamaño_titulo'] + 4)
        
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Información del proyecto con formato mejorado
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
                
                # Crear el texto con etiqueta en negrita y valor normal
                label_run = p.add_run(f"{label}: ")
                label_run.bold = True
                label_run.font.name = app_instance.formato_config['fuente_texto']
                label_run.font.size = Pt(app_instance.formato_config['tamaño_texto'])
                
                value_run = p.add_run(app_instance.proyecto_data[field].get())
                value_run.bold = False
                value_run.font.name = app_instance.formato_config['fuente_texto']
                value_run.font.size = Pt(app_instance.formato_config['tamaño_texto'])
        
        # Espaciado adicional
        doc.add_paragraph()
        
        # Estudiantes - MEJORADO
        if app_instance.proyecto_data['estudiantes'].get():
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_run = p.add_run("Estudiantes:")
            title_run.bold = True
            title_run.font.name = app_instance.formato_config['fuente_texto']
            title_run.font.size = Pt(app_instance.formato_config['tamaño_texto'] + 1)
            
            estudiantes = app_instance.proyecto_data['estudiantes'].get().split(',')
            for estudiante in estudiantes:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                student_run = p.add_run(estudiante.strip())
                student_run.font.name = app_instance.formato_config['fuente_texto']
                student_run.font.size = Pt(app_instance.formato_config['tamaño_texto'])
        
        # Tutores - MEJORADO
        if app_instance.proyecto_data['tutores'].get():
            doc.add_paragraph()  # Espaciado
            
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_run = p.add_run("Tutores:")
            title_run.bold = True
            title_run.font.name = app_instance.formato_config['fuente_texto']
            title_run.font.size = Pt(app_instance.formato_config['tamaño_texto'] + 1)
            
            tutores = app_instance.proyecto_data['tutores'].get().split(',')
            for tutor in tutores:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                tutor_run = p.add_run(tutor.strip())
                tutor_run.font.name = app_instance.formato_config['fuente_texto']
                tutor_run.font.size = Pt(app_instance.formato_config['tamaño_texto'])
        
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Fecha - MEJORADO
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        year_label = p.add_run("Año: ")
        year_label.bold = True
        year_label.font.name = app_instance.formato_config['fuente_texto']
        year_label.font.size = Pt(app_instance.formato_config['tamaño_texto'])
        
        year_value = p.add_run(str(datetime.now().year))
        year_value.font.name = app_instance.formato_config['fuente_texto']
        year_value.font.size = Pt(app_instance.formato_config['tamaño_texto'])
        
        doc.add_page_break()'''
            
            # Aplicar cambio
            content = re.sub(old_portada_method, new_portada_method, content, flags=re.DOTALL)
            
            # Actualizar obtener_ruta_imagen si existe
            old_ruta_imagen = r'def obtener_ruta_imagen\(self, tipo, app_instance\):.*?return None'
            new_ruta_imagen = '''def obtener_ruta_imagen(self, tipo, app_instance):
        """Obtiene la ruta final de la imagen a usar (personalizada o base) - MEJORADA"""
        if tipo == "encabezado":
            # Prioridad: personalizada -> base
            return (getattr(app_instance, 'encabezado_personalizado', None) or 
                   getattr(app_instance, 'ruta_encabezado', None))
        elif tipo == "insignia":
            # Prioridad: personalizada -> base
            return (getattr(app_instance, 'insignia_personalizada', None) or 
                   getattr(app_instance, 'ruta_insignia', None))
        return None'''
            
            content = re.sub(old_ruta_imagen, new_ruta_imagen, content, flags=re.DOTALL)
            
            # Guardar archivo actualizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.changes_log.append("✅ core/document_generator.py - Mejorado texto en negrita de portada")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando document_generator.py: {e}")
            return False

    def update_validator(self):
        """Actualiza core/validator.py con validaciones mejoradas"""
        file_path = os.path.join(self.script_dir, 'core', 'validator.py')
        
        if not self.create_backup(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Agregar imports si no existen
            if 'from datetime import datetime' not in content:
                content = content.replace(
                    'from tkinter import messagebox',
                    'from tkinter import messagebox\nfrom datetime import datetime'
                )
            
            # Agregar método de validación de imágenes si no existe
            if '_validar_imagenes' not in content:
                validation_methods = '''
    def _validar_imagenes(self, app_instance, advertencias, sugerencias):
        """Valida disponibilidad y calidad de imágenes"""
        enc_activo = (getattr(app_instance, 'encabezado_personalizado', None) or 
                     getattr(app_instance, 'ruta_encabezado', None))
        ins_activo = (getattr(app_instance, 'insignia_personalizada', None) or 
                     getattr(app_instance, 'ruta_insignia', None))
        
        if not enc_activo and not ins_activo:
            advertencias.append("⚠️ No hay imágenes configuradas (encabezado/insignia)")
        elif not enc_activo:
            sugerencias.append("💡 Considera agregar imagen de encabezado")
        elif not ins_activo:
            sugerencias.append("💡 Considera agregar imagen de insignia")

    def _validar_formato_referencias(self, referencias, advertencias):
        """Valida formato APA básico en referencias"""
        for i, ref in enumerate(referencias, 1):
            # Validar formato básico de autor
            if not re.match(r'^[A-ZÁ-Ž].*,\\s*[A-Z]\\.', ref.get('autor', '')):
                advertencias.append(f"⚠️ Referencia {i}: Formato de autor incorrecto (usar: Apellido, N.)")
            
            # Validar año
            año = ref.get('año', '')
            if not año.isdigit() or not (1900 <= int(año) <= datetime.now().year + 1):
                advertencias.append(f"⚠️ Referencia {i}: Año inválido ({año})")'''
                
                # Insertar antes de la última función
                last_method_pos = content.rfind('    def ')
                if last_method_pos != -1:
                    content = content[:last_method_pos] + validation_methods + '\n\n' + content[last_method_pos:]
            
            # Actualizar validar_proyecto si es necesario
            if 'sugerencias = []' not in content:
                content = content.replace(
                    'advertencias = []',
                    'advertencias = []\n        sugerencias = []'
                )
            
            # Guardar archivo actualizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.changes_log.append("✅ core/validator.py - Agregadas validaciones mejoradas")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando validator.py: {e}")
            return False

    def create_setup_directories_script(self):
        """Crea el script setup_directories.py"""
        setup_script_path = os.path.join(self.script_dir, 'setup_directories.py')
        
        setup_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador de Directorios - Crea estructura de directorios necesaria
"""

import os
import shutil
from datetime import datetime

def crear_estructura_directorios():
    """Crea la estructura de directorios necesaria para el proyecto"""
    print("🏗️ CONFIGURANDO ESTRUCTURA DE DIRECTORIOS\\n")
    
    # Obtener directorio base del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = script_dir
    
    # Directorios a crear
    directorios = [
        "resources",
        "resources/images",
        "plantillas",
        "backups",
        "exports"
    ]
    
    created_dirs = []
    
    for directorio in directorios:
        ruta_completa = os.path.join(base_dir, directorio)
        
        if not os.path.exists(ruta_completa):
            try:
                os.makedirs(ruta_completa)
                created_dirs.append(directorio)
                print(f"✅ Creado: {directorio}/")
            except Exception as e:
                print(f"❌ Error creando {directorio}: {e}")
        else:
            print(f"📁 Ya existe: {directorio}/")
    
    # Migrar imágenes si existen en Recursos
    migrar_imagenes_recursos(base_dir)
    
    print(f"\\n🎉 CONFIGURACIÓN COMPLETADA")
    if created_dirs:
        print(f"📂 Directorios creados: {len(created_dirs)}")

def migrar_imagenes_recursos(base_dir):
    """Migra imágenes del directorio Recursos al nuevo resources/images"""
    recursos_viejo = os.path.join(base_dir, "Recursos")
    recursos_nuevo = os.path.join(base_dir, "resources", "images")
    
    if os.path.exists(recursos_viejo):
        print(f"\\n🔄 MIGRANDO IMÁGENES DE {recursos_viejo}")
        
        archivos_migrados = 0
        for archivo in os.listdir(recursos_viejo):
            if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                origen = os.path.join(recursos_viejo, archivo)
                destino = os.path.join(recursos_nuevo, archivo)
                
                try:
                    if not os.path.exists(destino):
                        shutil.copy2(origen, destino)
                        print(f"   📋 Migrado: {archivo}")
                        archivos_migrados += 1
                    else:
                        print(f"   ⏭️ Ya existe: {archivo}")
                except Exception as e:
                    print(f"   ❌ Error migrando {archivo}: {e}")
        
        if archivos_migrados > 0:
            print(f"✅ {archivos_migrados} archivo(s) migrado(s) exitosamente")

if __name__ == "__main__":
    crear_estructura_directorios()
'''
        
        try:
            with open(setup_script_path, 'w', encoding='utf-8') as f:
                f.write(setup_content)
            
            self.changes_log.append("✅ setup_directories.py - Script creado")
            return True
        except Exception as e:
            print(f"❌ Error creando setup_directories.py: {e}")
            return False

    def create_readme_update(self):
        """Crea/actualiza README con información sobre los cambios"""
        readme_path = os.path.join(self.script_dir, 'README_ACTUALIZACION.md')
        
        readme_content = f'''# Actualización del Proyecto - {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Cambios Aplicados Automáticamente

### 🖼️ Ubicación de Imágenes
- **Cambio**: Movidas de `Recursos/` a `resources/images/`
- **Archivos**: Encabezado.png, Insignia.png
- **Beneficio**: Estructura más organizada y estándar

### ✨ Texto en Negrita Mejorado
- **Cambio**: Etiquetas en negrita, valores normales en portada
- **Afecta**: Ciclo, Énfasis, Tutores, Estudiantes, etc.
- **Beneficio**: Mejor legibilidad y formato profesional

### 🔍 Validaciones Mejoradas
- **Cambio**: Nuevas validaciones de formato APA e imágenes
- **Beneficio**: Detección temprana de errores

## Archivos Modificados
{chr(10).join(f"- {change}" for change in self.changes_log)}

## Backup Creado
📁 **Ubicación**: `{self.backup_dir}`
- Contiene copias de seguridad de todos los archivos modificados
- Úsalo para restaurar si algo sale mal

## Próximos Pasos
1. Ejecutar `python setup_directories.py` para configurar directorios
2. Mover imágenes a `resources/images/`
3. Probar la aplicación con `python main.py`

## Rollback (Si es necesario)
Si algo sale mal, puedes restaurar usando los backups:
```bash
# Ejemplo para restaurar main_window.py
cp "{self.backup_dir}/ui/main_window.py" "ui/main_window.py"
```
'''
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            return True
        except Exception as e:
            print(f"❌ Error creando README: {e}")
            return False

    def run_updates(self):
        """Ejecuta todas las actualizaciones"""
        print("🚀 INICIANDO PROCESO DE ACTUALIZACIÓN")
        print("=" * 50)
        
        # Verificar estructura
        if not self.verify_file_structure():
            print("❌ Estructura de archivos inválida. Cancelando...")
            return False
        
        # Preguntar confirmación
        print("⚠️ ATENCIÓN: Este script modificará archivos de código.")
        print(f"✅ Se creará backup en: {self.backup_dir}")
        print()
        respuesta = input("¿Continuar con las actualizaciones? (s/n): ").lower().strip()
        
        if respuesta not in ['s', 'si', 'y', 'yes']:
            print("🛑 Actualizaciones canceladas por el usuario")
            return False
        
        print("\n🔄 APLICANDO ACTUALIZACIONES...")
        
        # Lista de actualizaciones
        updates = [
            ("main_window.py", self.update_main_window),
            ("document_generator.py", self.update_document_generator),
            ("validator.py", self.update_validator),
            ("setup_directories.py", self.create_setup_directories_script)
        ]
        
        successful_updates = 0
        
        for update_name, update_function in updates:
            print(f"\n🔧 Actualizando {update_name}...")
            try:
                if update_function():
                    print(f"✅ {update_name} actualizado exitosamente")
                    successful_updates += 1
                else:
                    print(f"❌ Error actualizando {update_name}")
            except Exception as e:
                print(f"❌ Excepción actualizando {update_name}: {e}")
        
        # Crear README de actualización
        self.create_readme_update()
        
        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE ACTUALIZACIONES")
        print(f"✅ Exitosas: {successful_updates}/{len(updates)}")
        print(f"💾 Backup en: {self.backup_dir}")
        
        if successful_updates == len(updates):
            print("\n🎉 ¡TODAS LAS ACTUALIZACIONES COMPLETADAS!")
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. Ejecutar: python setup_directories.py")
            print("2. Mover imágenes a resources/images/")
            print("3. Probar: python main.py")
        else:
            print(f"\n⚠️ {len(updates) - successful_updates} actualizaciones fallaron")
            print("📄 Revisa los mensajes de error arriba")
            print("💾 Usa los backups para restaurar si es necesario")
        
        return successful_updates == len(updates)

    def rollback(self, backup_path=None):
        """Restaura archivos desde backup"""
        if backup_path is None:
            backup_path = self.backup_dir
        
        if not os.path.exists(backup_path):
            print(f"❌ Backup no encontrado: {backup_path}")
            return False
        
        print(f"🔄 RESTAURANDO DESDE: {backup_path}")
        
        try:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    backup_file = os.path.join(root, file)
                    relative_path = os.path.relpath(backup_file, backup_path)
                    original_file = os.path.join(self.script_dir, relative_path)
                    
                    # Crear directorio si no existe
                    os.makedirs(os.path.dirname(original_file), exist_ok=True)
                    
                    # Restaurar archivo
                    shutil.copy2(backup_file, original_file)
                    print(f"📁 Restaurado: {relative_path}")
            
            print("✅ Restauración completada")
            return True
            
        except Exception as e:
            print(f"❌ Error en restauración: {e}")
            return False

def main():
    """Función principal"""
    updater = ProjectAutoUpdater()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        if len(sys.argv) > 2:
            updater.rollback(sys.argv[2])
        else:
            print("❌ Especifica la ruta del backup para rollback")
    else:
        updater.run_updates()

if __name__ == "__main__":
    main()