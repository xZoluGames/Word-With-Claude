"""
Gestión de referencias bibliográficas - Sistema completo de referencias APA
"""

import customtkinter as ctk
from tkinter import messagebox
import re
from datetime import datetime

class ReferenceManager:
    def __init__(self):
        self.referencias = []
        self.tipos_referencia = {
            'Libro': {
                'campos': ['autor', 'año', 'titulo', 'editorial', 'ciudad'],
                'formato': '{autor} ({año}). {titulo}. {editorial}.'
            },
            'Artículo': {
                'campos': ['autor', 'año', 'titulo', 'revista', 'volumen', 'paginas'],
                'formato': '{autor} ({año}). {titulo}. {revista}, {volumen}, {paginas}.'
            },
            'Web': {
                'campos': ['autor', 'año', 'titulo', 'sitio_web', 'url', 'fecha_acceso'],
                'formato': '{autor} ({año}). {titulo}. {sitio_web}. {url}'
            },
            'Tesis': {
                'campos': ['autor', 'año', 'titulo', 'tipo_tesis', 'institucion'],
                'formato': '{autor} ({año}). {titulo} ({tipo_tesis}). {institucion}.'
            }
        }
    
    def agregar_referencia(self, ref_data):
        """Agrega una nueva referencia con validación"""
        # Validar campos requeridos
        campos_requeridos = ['autor', 'año', 'titulo']
        for campo in campos_requeridos:
            if not ref_data.get(campo, '').strip():
                raise ValueError(f"El campo '{campo}' es requerido")
        
        # Validar año
        try:
            año = int(ref_data['año'])
            if año < 1800 or año > datetime.now().year + 1:
                raise ValueError("Año inválido")
        except ValueError:
            raise ValueError("El año debe ser un número válido")
        
        # Validar formato del autor
        if not self._validar_formato_autor(ref_data['autor']):
            raise ValueError("Formato de autor incorrecto. Use: 'Apellido, N.' o 'Apellido, N. M.'")
        
        # Crear referencia
        referencia = {
            'id': len(self.referencias) + 1,
            'fecha_agregada': datetime.now().isoformat(),
            **ref_data
        }
        
        self.referencias.append(referencia)
        return referencia
    
    def eliminar_referencia(self, index=-1):
        """Elimina una referencia por índice (por defecto la última)"""
        if not self.referencias:
            raise ValueError("No hay referencias para eliminar")
        
        if index == -1:
            index = len(self.referencias) - 1
        
        if 0 <= index < len(self.referencias):
            referencia_eliminada = self.referencias.pop(index)
            return referencia_eliminada
        else:
            raise ValueError("Índice de referencia inválido")
    
    def editar_referencia(self, index, nuevos_datos):
        """Edita una referencia existente"""
        if 0 <= index < len(self.referencias):
            self.referencias[index].update(nuevos_datos)
            self.referencias[index]['fecha_modificada'] = datetime.now().isoformat()
            return self.referencias[index]
        else:
            raise ValueError("Índice de referencia inválido")
    
    def generar_apa_format(self, referencia):
        """Genera formato APA para una referencia"""
        tipo = referencia.get('tipo', 'Libro')
        
        if tipo == 'Libro':
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. {referencia.get('fuente', 'Editorial desconocida')}."
        elif tipo == 'Artículo':
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. {referencia.get('fuente', 'Revista desconocida')}."
        elif tipo == 'Web':
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. {referencia.get('fuente', 'Sitio web')}."
        elif tipo == 'Tesis':
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']} (Tesis). {referencia.get('fuente', 'Institución')}."
        else:
            return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. {referencia.get('fuente', '')}."
    
    def ordenar_referencias(self, criterio='autor'):
        """Ordena las referencias según el criterio especificado"""
        if criterio == 'autor':
            self.referencias.sort(key=lambda x: x['autor'].lower())
        elif criterio == 'año':
            self.referencias.sort(key=lambda x: int(x['año']), reverse=True)
        elif criterio == 'titulo':
            self.referencias.sort(key=lambda x: x['titulo'].lower())
        elif criterio == 'tipo':
            self.referencias.sort(key=lambda x: x.get('tipo', 'Libro').lower())
    
    def buscar_referencias(self, termino):
        """Busca referencias por término en autor, título o fuente"""
        termino = termino.lower()
        resultados = []
        
        for i, ref in enumerate(self.referencias):
            if (termino in ref['autor'].lower() or 
                termino in ref['titulo'].lower() or 
                termino in ref.get('fuente', '').lower()):
                resultados.append((i, ref))
        
        return resultados
    
    def exportar_referencias(self, formato='apa'):
        """Exporta todas las referencias en el formato especificado"""
        if formato == 'apa':
            referencias_formateadas = []
            for ref in sorted(self.referencias, key=lambda x: x['autor'].lower()):
                referencias_formateadas.append(self.generar_apa_format(ref))
            return '\n\n'.join(referencias_formateadas)
        else:
            return str(self.referencias)
    
    def importar_referencias_bibtex(self, contenido_bibtex):
        """Importa referencias desde formato BibTeX (básico)"""
        # Implementación básica para BibTeX
        entradas = re.findall(r'@\w+\{[^}]+\}', contenido_bibtex, re.DOTALL)
        referencias_importadas = 0
        
        for entrada in entradas:
            try:
                ref_data = self._parsear_bibtex_entrada(entrada)
                if ref_data:
                    self.agregar_referencia(ref_data)
                    referencias_importadas += 1
            except Exception as e:
                print(f"Error importando entrada: {e}")
        
        return referencias_importadas
    
    def validar_referencias_citadas(self, texto_documento):
        """Valida que todas las citas tengan su referencia correspondiente"""
        from .citations import CitationProcessor
        
        processor = CitationProcessor()
        autores_citados = processor.extraer_autores_citados(texto_documento)
        autores_referencias = [ref['autor'] for ref in self.referencias]
        
        citas_sin_referencia = []
        for autor in autores_citados:
            if not any(autor.lower() in ref_autor.lower() for ref_autor in autores_referencias):
                citas_sin_referencia.append(autor)
        
        referencias_sin_citar = []
        for ref in self.referencias:
            autor_ref = ref['autor'].split(',')[0]  # Tomar solo el apellido
            if not any(autor_ref.lower() in autor.lower() for autor in autores_citados):
                referencias_sin_citar.append(ref['autor'])
        
        return {
            'citas_sin_referencia': citas_sin_referencia,
            'referencias_sin_citar': referencias_sin_citar,
            'total_citas': len(autores_citados),
            'total_referencias': len(self.referencias)
        }
    
    def generar_estadisticas(self):
        """Genera estadísticas de las referencias"""
        if not self.referencias:
            return {'total': 0, 'mensaje': 'No hay referencias agregadas'}
        
        tipos_count = {}
        años_count = {}
        
        for ref in self.referencias:
            tipo = ref.get('tipo', 'Libro')
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
            
            año = ref.get('año', 'Sin año')
            años_count[año] = años_count.get(año, 0) + 1
        
        año_mas_reciente = max([int(ref['año']) for ref in self.referencias if ref['año'].isdigit()])
        año_mas_antiguo = min([int(ref['año']) for ref in self.referencias if ref['año'].isdigit()])
        
        return {
            'total': len(self.referencias),
            'por_tipo': tipos_count,
            'por_año': años_count,
            'rango_años': f"{año_mas_antiguo}-{año_mas_reciente}",
            'año_mas_reciente': año_mas_reciente,
            'tipo_mas_usado': max(tipos_count.items(), key=lambda x: x[1])[0] if tipos_count else 'N/A'
        }
    
    def _validar_formato_autor(self, autor):
        """Valida que el autor tenga formato APA correcto"""
        # Patrones válidos: "Apellido, N." o "Apellido, N. M." o "Apellido, N. M. y Apellido2, P."
        patron_simple = r'^[A-ZÁ-Ž][a-záñü]+(?:\s[A-ZÁ-Ž][a-záñü]+)?,\s[A-Z]\.(?:\s[A-Z]\.)?$'
        patron_multiple = r'^[A-ZÁ-Ž][a-záñü]+(?:\s[A-ZÁ-Ž][a-záñü]+)?,\s[A-Z]\.(?:\s[A-Z]\.)?\sy\s[A-ZÁ-Ž][a-záñü]+(?:\s[A-ZÁ-Ž][a-záñü]+)?,\s[A-Z]\.(?:\s[A-Z]\.)?$'
        
        return bool(re.match(patron_simple, autor) or re.match(patron_multiple, autor))
    
    def _parsear_bibtex_entrada(self, entrada):
        """Parsea una entrada BibTeX y extrae los datos"""
        # Implementación básica para parsear BibTeX
        lineas = entrada.split('\n')
        ref_data = {}
        
        for linea in lineas:
            if '=' in linea:
                campo, valor = linea.split('=', 1)
                campo = campo.strip()
                valor = valor.strip().strip(',').strip('{}').strip('"')
                
                if campo == 'author':
                    ref_data['autor'] = valor
                elif campo == 'year':
                    ref_data['año'] = valor
                elif campo == 'title':
                    ref_data['titulo'] = valor
                elif campo == 'publisher':
                    ref_data['fuente'] = valor
                elif campo == 'journal':
                    ref_data['fuente'] = valor
        
        return ref_data if len(ref_data) >= 3 else None
    
    def limpiar_referencias(self):
        """Limpia todas las referencias"""
        cantidad = len(self.referencias)
        self.referencias.clear()
        return cantidad
    
    def duplicar_referencia(self, index):
        """Duplica una referencia existente"""
        if 0 <= index < len(self.referencias):
            ref_original = self.referencias[index].copy()
            ref_original['id'] = len(self.referencias) + 1
            ref_original['titulo'] = f"{ref_original['titulo']} (Copia)"
            ref_original['fecha_agregada'] = datetime.now().isoformat()
            self.referencias.append(ref_original)
            return ref_original
        else:
            raise ValueError("Índice de referencia inválido")