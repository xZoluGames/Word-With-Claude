"""
Sistema de citas - Procesamiento automático de citas académicas formato APA
"""

import re
from tkinter import messagebox

class CitationProcessor:
    def __init__(self):
        self.citation_patterns = {
            'textual': r'\[CITA:textual:([^:]+):([^:]+):?([^]]*)\]',
            'parafraseo': r'\[CITA:parafraseo:([^:]+):([^:]+)\]',
            'larga': r'\[CITA:larga:([^:]+):([^:]+):?([^]]*)\]',
            'web': r'\[CITA:web:([^:]+):([^:]+)\]',
            'multiple': r'\[CITA:multiple:([^:]+):([^:]+)\]'
        }
        
        self.citation_examples = {
            'textual': '[CITA:textual:García:2020:45] - Cita textual con página',
            'parafraseo': '[CITA:parafraseo:López:2019] - Parafraseo de idea',
            'larga': '[CITA:larga:Martínez:2021:78] - Cita larga (más de 40 palabras)',
            'web': '[CITA:web:OMS:2023] - Fuente web institucional',
            'multiple': '[CITA:multiple:García y López:2020] - Múltiples autores'
        }
    
    def procesar_citas(self, texto):
        """Procesa todas las citas en el texto y las convierte a formato APA"""
        def reemplazar_cita(match):
            cita_completa = match.group(0)
            contenido = cita_completa[6:-1]  # Quita [CITA: y ]
            partes = contenido.split(':')
            
            if len(partes) >= 3:
                tipo, autor, año = partes[0], partes[1], partes[2]
                pagina = partes[3] if len(partes) > 3 else None
                
                return self._formatear_cita_apa(tipo, autor, año, pagina)
            
            return cita_completa
        
        return re.sub(r'\[CITA:[^\]]+\]', reemplazar_cita, texto)
    
    def _formatear_cita_apa(self, tipo, autor, año, pagina=None):
        """Formatea una cita individual según el estilo APA"""
        if tipo == 'textual':
            return f" ({autor}, {año}, p. {pagina})" if pagina else f" ({autor}, {año})"
        elif tipo == 'parafraseo':
            return f" ({autor}, {año})"
        elif tipo == 'larga':
            return f"\n\n({autor}, {año}, p. {pagina})\n\n" if pagina else f"\n\n({autor}, {año})\n\n"
        elif tipo == 'web':
            return f" ({autor}, {año})"
        elif tipo == 'multiple':
            return f" ({autor}, {año})"
        else:
            return f" ({autor}, {año})"
    
    def validar_citas(self, texto):
        """Valida que las citas tengan el formato correcto"""
        citas_encontradas = re.findall(r'\[CITA:[^\]]+\]', texto)
        citas_validas = []
        citas_invalidas = []
        
        for cita in citas_encontradas:
            contenido = cita[6:-1]  # Quita [CITA: y ]
            partes = contenido.split(':')
            
            if len(partes) >= 3:
                tipo, autor, año = partes[0], partes[1], partes[2]
                if tipo in self.citation_patterns.keys() and autor.strip() and año.strip():
                    citas_validas.append(cita)
                else:
                    citas_invalidas.append(cita)
            else:
                citas_invalidas.append(cita)
        
        return {
            'validas': citas_validas,
            'invalidas': citas_invalidas,
            'total': len(citas_encontradas)
        }
    
    def extraer_autores_citados(self, texto):
        """Extrae lista de autores citados en el texto"""
        citas_encontradas = re.findall(r'\[CITA:[^\]]+\]', texto)
        autores_citados = set()
        
        for cita in citas_encontradas:
            contenido = cita[6:-1]
            partes = contenido.split(':')
            if len(partes) >= 3:
                autor = partes[1].strip()
                autores_citados.add(autor)
        
        return sorted(list(autores_citados))
    
    def generar_sugerencias_citas(self, seccion_tipo):
        """Genera sugerencias de citas según el tipo de sección"""
        sugerencias = {
            'marco_teorico': [
                "💡 Usa [CITA:parafraseo:Autor:Año] para ideas parafraseadas",
                "📖 Usa [CITA:textual:Autor:Año:Página] para citas textuales",
                "🔍 Incluye al menos 3-5 citas por párrafo teórico"
            ],
            'metodologia': [
                "📊 Cita metodologías: [CITA:parafraseo:Hernández:2018]",
                "🔬 Referencias de instrumentos: [CITA:textual:Autor:Año:Página]"
            ],
            'discusion': [
                "💬 Compara resultados: [CITA:parafraseo:Autor:Año]",
                "🔄 Contrasta con estudios previos usando citas"
            ]
        }
        
        return sugerencias.get(seccion_tipo, ["📝 Usa citas para respaldar tus afirmaciones"])
    
    def obtener_ejemplos_citas(self):
        """Retorna ejemplos de uso de citas"""
        return self.citation_examples
    
    def insertar_cita_automatica(self, texto_seleccionado, tipo_cita, autor, año, pagina=None):
        """Inserta automáticamente una cita en formato correcto"""
        if tipo_cita in ['textual', 'larga'] and pagina:
            cita = f"[CITA:{tipo_cita}:{autor}:{año}:{pagina}]"
        else:
            cita = f"[CITA:{tipo_cita}:{autor}:{año}]"
        
        return f"{texto_seleccionado} {cita}"
    
    def analizar_densidad_citas(self, texto):
        """Analiza la densidad de citas en el texto"""
        palabras_total = len(texto.split())
        citas_total = len(re.findall(r'\[CITA:[^\]]+\]', texto))
        
        if palabras_total == 0:
            return {'densidad': 0, 'recomendacion': 'Sin contenido'}
        
        densidad = citas_total / (palabras_total / 100)  # Citas por cada 100 palabras
        
        if densidad < 1:
            recomendacion = "⚠️ Pocas citas - Agrega más referencias"
        elif densidad > 5:
            recomendacion = "⚠️ Demasiadas citas - Equilibra con análisis propio"
        else:
            recomendacion = "✅ Densidad de citas adecuada"
        
        return {
            'densidad': round(densidad, 2),
            'citas_total': citas_total,
            'palabras_total': palabras_total,
            'recomendacion': recomendacion
        }