"""
Validador de proyectos para el Generador de Proyectos Académicos
Realiza validaciones inteligentes y adaptativas del contenido del proyecto
"""

import re
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from collections import Counter

class ProjectValidator:
    """Validador inteligente de proyectos académicos"""
    
    def __init__(self, app):
        self.app = app
        self.criterios_validacion = self.get_criterios_validacion()
        self.configuracion_validacion = self.get_configuracion_validacion()
        
    def get_criterios_validacion(self):
        """Define los criterios de validación por categorías"""
        return {
            'informacion_general': {
                'titulo': {
                    'requerido': True,
                    'min_palabras': 3,
                    'max_palabras': 20,
                    'peso': 10
                },
                'estudiantes': {
                    'requerido': True,
                    'min_caracteres': 5,
                    'peso': 8
                },
                'tutores': {
                    'requerido': True,
                    'min_caracteres': 5,
                    'peso': 8
                },
                'institucion': {
                    'requerido': False,
                    'peso': 5
                }
            },
            'contenido_secciones': {
                'min_caracteres_seccion_requerida': 100,
                'min_palabras_seccion_requerida': 20,
                'peso_por_seccion': 15
            },
            'referencias': {
                'min_referencias': 3,
                'referencias_por_pagina': 0.5,  # Referencias por cada página estimada
                'peso': 20
            },
            'citas': {
                'min_citas_marco_teorico': 2,
                'patron_cita_valida': r'\[CITA:[^\]]+\]',
                'peso': 15
            },
            'coherencia': {
                'palabras_clave_repetidas': 0.02,  # 2% de palabras pueden repetirse
                'peso': 10
            }
        }
    
    def get_configuracion_validacion(self):
        """Configuración de niveles de validación"""
        return {
            'niveles': {
                'basico': {
                    'nombre': 'Básico',
                    'descripcion': 'Validación mínima para proyectos en desarrollo',
                    'umbral_aprobacion': 60
                },
                'estandar': {
                    'nombre': 'Estándar',
                    'descripcion': 'Validación completa para proyectos terminados',
                    'umbral_aprobacion': 80
                },
                'estricto': {
                    'nombre': 'Estricto',
                    'descripcion': 'Validación rigurosa para publicación',
                    'umbral_aprobacion': 95
                }
            },
            'nivel_actual': 'estandar'
        }
    
    def validar_proyecto_completo(self, nivel=None):
        """Realiza validación completa del proyecto"""
        if nivel is None:
            nivel = self.configuracion_validacion['nivel_actual']
        
        # Inicializar resultado
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'nivel_validacion': nivel,
            'puntaje_total': 0,
            'puntaje_maximo': 100,
            'porcentaje': 0,
            'aprobado': False,
            'errores': [],
            'advertencias': [],
            'sugerencias': [],
            'detalles_por_categoria': {},
            'estadisticas': {},
            'recomendaciones': []
        }
        
        try:
            # Validar cada categoría
            self.validar_informacion_general(resultado)
            self.validar_contenido_secciones(resultado)
            self.validar_referencias(resultado)
            self.validar_citas(resultado)
            self.validar_coherencia_texto(resultado)
            
            # Calcular puntaje final
            self.calcular_puntaje_final(resultado)
            
            # Determinar aprobación
            umbral = self.configuracion_validacion['niveles'][nivel]['umbral_aprobacion']
            resultado['aprobado'] = resultado['porcentaje'] >= umbral
            
            # Generar recomendaciones
            self.generar_recomendaciones(resultado)
            
            # Mostrar resultados
            self.mostrar_resultados_validacion(resultado)
            
            return resultado
            
        except Exception as e:
            messagebox.showerror("❌ Error de Validación", f"Error durante la validación:\n{str(e)}")
            return None
    
    def validar_informacion_general(self, resultado):
        """Valida la información general del proyecto"""
        detalles = {
            'categoria': 'Información General',
            'puntaje': 0,
            'puntaje_maximo': 31,  # Suma de pesos de criterios
            'campos_validados': {},
            'problemas': []
        }
        
        criterios = self.criterios_validacion['informacion_general']
        
        for campo, config in criterios.items():
            if campo in self.app.proyecto_data:
                valor = self.app.proyecto_data[campo].get().strip()
                resultado_campo = self.validar_campo_informacion(campo, valor, config)
                
                detalles['campos_validados'][campo] = resultado_campo
                detalles['puntaje'] += resultado_campo['puntaje']
                
                if resultado_campo['errores']:
                    resultado['errores'].extend(resultado_campo['errores'])
                    detalles['problemas'].extend(resultado_campo['errores'])
                
                if resultado_campo['advertencias']:
                    resultado['advertencias'].extend(resultado_campo['advertencias'])
        
        resultado['detalles_por_categoria']['informacion_general'] = detalles
    
    def validar_campo_informacion(self, campo, valor, config):
        """Valida un campo específico de información general"""
        resultado_campo = {
            'campo': campo,
            'valor': valor,
            'puntaje': 0,
            'puntaje_maximo': config['peso'],
            'errores': [],
            'advertencias': []
        }
        
        # Verificar si es requerido
        if config['requerido'] and not valor:
            resultado_campo['errores'].append(f"❌ Campo '{campo}' es obligatorio")
            return resultado_campo
        
        if not valor:  # Campo opcional vacío
            return resultado_campo
        
        # Validaciones específicas
        if campo == 'titulo':
            palabras = len(valor.split())
            if palabras < config.get('min_palabras', 0):
                resultado_campo['errores'].append(f"❌ Título muy corto (mínimo {config['min_palabras']} palabras)")
            elif palabras > config.get('max_palabras', 100):
                resultado_campo['advertencias'].append(f"⚠️ Título muy largo (máximo {config['max_palabras']} palabras recomendadas)")
            else:
                resultado_campo['puntaje'] = config['peso']
        
        elif campo in ['estudiantes', 'tutores']:
            if len(valor) < config.get('min_caracteres', 0):
                resultado_campo['errores'].append(f"❌ {campo.capitalize()} muy corto")
            else:
                resultado_campo['puntaje'] = config['peso']
                
                # Validar formato de nombres
                if ',' in valor:  # Múltiples nombres
                    nombres = [n.strip() for n in valor.split(',')]
                    nombres_validos = [n for n in nombres if len(n.split()) >= 2]
                    if len(nombres_validos) < len(nombres):
                        resultado_campo['advertencias'].append(f"⚠️ Algunos {campo} no tienen formato completo (Nombre Apellido)")
        
        else:  # Otros campos
            if valor:
                resultado_campo['puntaje'] = config['peso']
        
        return resultado_campo
    
    def validar_contenido_secciones(self, resultado):
        """Valida el contenido de las secciones"""
        detalles = {
            'categoria': 'Contenido de Secciones',
            'puntaje': 0,
            'puntaje_maximo': 0,
            'secciones_validadas': {},
            'estadisticas': {
                'total_secciones': len(self.app.secciones_activas),
                'secciones_requeridas': 0,
                'secciones_completas': 0,
                'secciones_vacias': 0,
                'total_palabras': 0,
                'total_caracteres': 0
            }
        }
        
        criterios = self.criterios_validacion['contenido_secciones']
        
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.secciones_disponibles:
                seccion_info = self.app.secciones_disponibles[seccion_id]
                
                # Solo validar secciones de contenido (no capítulos)
                if not seccion_info.get('capitulo', False):
                    contenido = self.obtener_contenido_seccion(seccion_id)
                    resultado_seccion = self.validar_seccion_individual(seccion_id, seccion_info, contenido, criterios)
                    
                    detalles['secciones_validadas'][seccion_id] = resultado_seccion
                    detalles['puntaje'] += resultado_seccion['puntaje']
                    detalles['puntaje_maximo'] += resultado_seccion['puntaje_maximo']
                    
                    # Actualizar estadísticas
                    if seccion_info.get('requerida', False):
                        detalles['estadisticas']['secciones_requeridas'] += 1
                    
                    if resultado_seccion['tiene_contenido']:
                        detalles['estadisticas']['secciones_completas'] += 1
                        detalles['estadisticas']['total_palabras'] += resultado_seccion['palabras']
                        detalles['estadisticas']['total_caracteres'] += resultado_seccion['caracteres']
                    else:
                        detalles['estadisticas']['secciones_vacias'] += 1
                    
                    # Agregar errores y advertencias
                    if resultado_seccion['errores']:
                        resultado['errores'].extend(resultado_seccion['errores'])
                    if resultado_seccion['advertencias']:
                        resultado['advertencias'].extend(resultado_seccion['advertencias'])
        
        resultado['detalles_por_categoria']['contenido_secciones'] = detalles
        resultado['estadisticas']['contenido'] = detalles['estadisticas']
    
    def validar_seccion_individual(self, seccion_id, seccion_info, contenido, criterios):
        """Valida una sección individual"""
        resultado_seccion = {
            'seccion_id': seccion_id,
            'titulo': seccion_info['titulo'],
            'requerida': seccion_info.get('requerida', False),
            'contenido': contenido,
            'caracteres': len(contenido),
            'palabras': len(contenido.split()) if contenido else 0,
            'tiene_contenido': bool(contenido.strip()),
            'puntaje': 0,
            'puntaje_maximo': criterios['peso_por_seccion'],
            'errores': [],
            'advertencias': []
        }
        
        if not contenido.strip():
            if resultado_seccion['requerida']:
                resultado_seccion['errores'].append(f"❌ Sección requerida '{seccion_info['titulo']}' está vacía")
            else:
                resultado_seccion['advertencias'].append(f"⚠️ Sección '{seccion_info['titulo']}' está vacía")
            return resultado_seccion
        
        # Validar longitud mínima
        if resultado_seccion['requerida']:
            if resultado_seccion['caracteres'] < criterios['min_caracteres_seccion_requerida']:
                resultado_seccion['errores'].append(
                    f"❌ Sección '{seccion_info['titulo']}' muy corta "
                    f"(mínimo {criterios['min_caracteres_seccion_requerida']} caracteres)"
                )
            elif resultado_seccion['palabras'] < criterios['min_palabras_seccion_requerida']:
                resultado_seccion['errores'].append(
                    f"❌ Sección '{seccion_info['titulo']}' muy corta "
                    f"(mínimo {criterios['min_palabras_seccion_requerida']} palabras)"
                )
            else:
                resultado_seccion['puntaje'] = criterios['peso_por_seccion']
        else:
            # Sección opcional con contenido
            if resultado_seccion['palabras'] >= 10:  # Mínimo razonable para opcionales
                resultado_seccion['puntaje'] = criterios['peso_por_seccion']
            else:
                resultado_seccion['advertencias'].append(f"⚠️ Sección '{seccion_info['titulo']}' muy breve")
                resultado_seccion['puntaje'] = criterios['peso_por_seccion'] // 2
        
        # Validaciones específicas por tipo de sección
        self.validar_seccion_especifica(seccion_id, contenido, resultado_seccion)
        
        return resultado_seccion
    
    def validar_seccion_especifica(self, seccion_id, contenido, resultado_seccion):
        """Validaciones específicas según el tipo de sección"""
        if seccion_id == 'objetivos':
            # Validar que los objetivos usen verbos en infinitivo
            verbos_infinitivo = r'\b(analizar|identificar|determinar|evaluar|comparar|describir|explicar|demostrar|proponer|desarrollar|establecer|verificar|investigar|examinar|estudiar|conocer|comprender)\b'
            if not re.search(verbos_infinitivo, contenido.lower()):
                resultado_seccion['advertencias'].append("⚠️ Los objetivos deben usar verbos en infinitivo (analizar, identificar, etc.)")
        
        elif seccion_id == 'marco_teorico':
            # Validar que tenga citas
            citas = re.findall(r'\[CITA:[^\]]+\]', contenido)
            if not citas:
                resultado_seccion['advertencias'].append("⚠️ Marco teórico debería incluir citas de fuentes")
        
        elif seccion_id == 'metodologia':
            # Validar términos metodológicos
            terminos_metodologicos = ['método', 'técnica', 'instrumento', 'población', 'muestra', 'análisis']
            terminos_encontrados = sum(1 for termino in terminos_metodologicos if termino in contenido.lower())
            if terminos_encontrados < 2:
                resultado_seccion['advertencias'].append("⚠️ Metodología podría incluir más términos técnicos específicos")
    
    def validar_referencias(self, resultado):
        """Valida las referencias bibliográficas"""
        detalles = {
            'categoria': 'Referencias Bibliográficas',
            'puntaje': 0,
            'puntaje_maximo': self.criterios_validacion['referencias']['peso'],
            'total_referencias': len(self.app.referencias),
            'referencias_validas': 0,
            'referencias_problematicas': [],
            'estadisticas': {
                'por_tipo': {},
                'por_año': {},
                'autores_unicos': set(),
                'referencias_recientes': 0  # Últimos 5 años
            }
        }
        
        criterios = self.criterios_validacion['referencias']
        año_actual = datetime.now().year
        
        # Validar cantidad mínima
        if detalles['total_referencias'] < criterios['min_referencias']:
            resultado['errores'].append(
                f"❌ Muy pocas referencias ({detalles['total_referencias']}/{criterios['min_referencias']} mínimas)"
            )
        
        # Validar cada referencia
        for i, ref in enumerate(self.app.referencias):
            problemas_ref = []
            
            # Campos obligatorios
            if not ref.get('autor', '').strip():
                problemas_ref.append("Sin autor")
            else:
                detalles['estadisticas']['autores_unicos'].add(ref['autor'])
            
            if not ref.get('año', '').strip():
                problemas_ref.append("Sin año")
            else:
                año = ref['año']
                if año.isdigit():
                    año_int = int(año)
                    if año_int >= año_actual - 5:
                        detalles['estadisticas']['referencias_recientes'] += 1
                    detalles['estadisticas']['por_año'][año] = detalles['estadisticas']['por_año'].get(año, 0) + 1
            
            if not ref.get('titulo', '').strip():
                problemas_ref.append("Sin título")
            
            # Estadísticas por tipo
            tipo = ref.get('tipo', 'Sin tipo')
            detalles['estadisticas']['por_tipo'][tipo] = detalles['estadisticas']['por_tipo'].get(tipo, 0) + 1
            
            if problemas_ref:
                detalles['referencias_problematicas'].append({
                    'indice': i + 1,
                    'referencia': ref,
                    'problemas': problemas_ref
                })
            else:
                detalles['referencias_validas'] += 1
        
        # Calcular puntaje
        if detalles['total_referencias'] >= criterios['min_referencias']:
            if detalles['referencias_problematicas']:
                # Puntaje proporcional
                proporcion_validas = detalles['referencias_validas'] / detalles['total_referencias']
                detalles['puntaje'] = int(criterios['peso'] * proporcion_validas)
            else:
                detalles['puntaje'] = criterios['peso']
        
        # Agregar advertencias por referencias problemáticas
        for ref_prob in detalles['referencias_problematicas']:
            resultado['advertencias'].append(
                f"⚠️ Referencia #{ref_prob['indice']}: {', '.join(ref_prob['problemas'])}"
            )
        
        # Convertir set a número para estadísticas
        detalles['estadisticas']['autores_unicos'] = len(detalles['estadisticas']['autores_unicos'])
        
        resultado['detalles_por_categoria']['referencias'] = detalles
        resultado['estadisticas']['referencias'] = detalles['estadisticas']
    
    def validar_citas(self, resultado):
        """Valida el sistema de citas en el texto"""
        detalles = {
            'categoria': 'Sistema de Citas',
            'puntaje': 0,
            'puntaje_maximo': self.criterios_validacion['citas']['peso'],
            'citas_encontradas': [],
            'citas_problematicas': [],
            'estadisticas': {
                'total_citas': 0,
                'por_tipo': {},
                'por_seccion': {},
                'citas_huerfanas': []  # Citas sin referencia correspondiente
            }
        }
        
        criterios = self.criterios_validacion['citas']
        patron_cita = criterios['patron_cita_valida']
        
        # Buscar citas en todas las secciones
        for seccion_id, text_widget in self.app.content_texts.items():
            if seccion_id in self.app.secciones_disponibles:
                contenido = text_widget.get("1.0", "end")
                citas_seccion = re.findall(patron_cita, contenido)
                
                detalles['estadisticas']['por_seccion'][seccion_id] = len(citas_seccion)
                
                for cita in citas_seccion:
                    resultado_cita = self.validar_cita_individual(cita, seccion_id)
                    detalles['citas_encontradas'].append(resultado_cita)
                    
                    if not resultado_cita['valida']:
                        detalles['citas_problematicas'].append(resultado_cita)
                    
                    # Estadísticas por tipo
                    tipo = resultado_cita['tipo']
                    detalles['estadisticas']['por_tipo'][tipo] = detalles['estadisticas']['por_tipo'].get(tipo, 0) + 1
        
        detalles['estadisticas']['total_citas'] = len(detalles['citas_encontradas'])
        
        # Validar marco teórico específicamente
        marco_teorico_citas = detalles['estadisticas']['por_seccion'].get('marco_teorico', 0)
        if marco_teorico_citas < criterios['min_citas_marco_teorico']:
            resultado['advertencias'].append(
                f"⚠️ Marco teórico tiene pocas citas ({marco_teorico_citas}/{criterios['min_citas_marco_teorico']} mínimas)"
            )
        
        # Verificar citas huérfanas (sin referencia correspondiente)
        self.detectar_citas_huerfanas(detalles)
        
        # Calcular puntaje
        if detalles['estadisticas']['total_citas'] > 0:
            proporcion_validas = (detalles['estadisticas']['total_citas'] - len(detalles['citas_problematicas'])) / detalles['estadisticas']['total_citas']
            detalles['puntaje'] = int(criterios['peso'] * proporcion_validas)
        
        # Agregar errores por citas problemáticas
        for cita_prob in detalles['citas_problematicas']:
            resultado['errores'].append(f"❌ Cita inválida en {cita_prob['seccion']}: {cita_prob['cita']}")
        
        resultado['detalles_por_categoria']['citas'] = detalles
        resultado['estadisticas']['citas'] = detalles['estadisticas']
    
    def validar_cita_individual(self, cita, seccion_id):
        """Valida una cita individual"""
        resultado_cita = {
            'cita': cita,
            'seccion': seccion_id,
            'valida': False,
            'tipo': 'desconocido',
            'autor': '',
            'año': '',
            'problemas': []
        }
        
        try:
            # Extraer componentes de la cita
            contenido = cita[6:-1]  # Quitar [CITA: y ]
            partes = contenido.split(':')
            
            if len(partes) < 3:
                resultado_cita['problemas'].append("Formato incompleto")
                return resultado_cita
            
            tipo, autor, año = partes[0].strip(), partes[1].strip(), partes[2].strip()
            
            resultado_cita['tipo'] = tipo
            resultado_cita['autor'] = autor
            resultado_cita['año'] = año
            
            # Validar tipo
            tipos_validos = ['textual', 'parafraseo', 'larga', 'web', 'multiple']
            if tipo not in tipos_validos:
                resultado_cita['problemas'].append(f"Tipo inválido: {tipo}")
            
            # Validar que tengan contenido
            if not autor:
                resultado_cita['problemas'].append("Sin autor")
            if not año:
                resultado_cita['problemas'].append("Sin año")
            
            # Si no hay problemas, es válida
            if not resultado_cita['problemas']:
                resultado_cita['valida'] = True
                
        except Exception as e:
            resultado_cita['problemas'].append(f"Error de formato: {str(e)}")
        
        return resultado_cita
    
    def detectar_citas_huerfanas(self, detalles):
        """Detecta citas que no tienen referencia correspondiente"""
        # Obtener autores de las referencias
        autores_referencias = set()
        for ref in self.app.referencias:
            autor = ref.get('autor', '').strip()
            if autor:
                # Extraer apellido principal
                if ',' in autor:
                    apellido = autor.split(',')[0].strip()
                else:
                    apellido = autor.split()[-1] if autor.split() else autor
                autores_referencias.add(apellido.lower())
        
        # Verificar cada cita
        for cita_info in detalles['citas_encontradas']:
            if cita_info['valida'] and cita_info['autor']:
                autor_cita = cita_info['autor'].lower()
                # Buscar coincidencia con algún autor de las referencias
                encontrado = any(autor_cita in autor_ref or autor_ref in autor_cita 
                               for autor_ref in autores_referencias)
                
                if not encontrado:
                    detalles['estadisticas']['citas_huerfanas'].append({
                        'cita': cita_info['cita'],
                        'autor': cita_info['autor'],
                        'seccion': cita_info['seccion']
                    })
    
    def validar_coherencia_texto(self, resultado):
        """Valida la coherencia general del texto"""
        detalles = {
            'categoria': 'Coherencia del Texto',
            'puntaje': 0,
            'puntaje_maximo': self.criterios_validacion['coherencia']['peso'],
            'analisis': {
                'palabras_mas_frecuentes': {},
                'repeticiones_excesivas': [],
                'longitud_promedio_parrafos': 0,
                'variedad_vocabulario': 0
            }
        }
        
        # Obtener todo el texto del proyecto
        texto_completo = self.obtener_texto_completo()
        
        if not texto_completo:
            resultado['advertencias'].append("⚠️ No hay suficiente contenido para analizar coherencia")
            resultado['detalles_por_categoria']['coherencia'] = detalles
            return
        
        # Análisis de vocabulario
        palabras = re.findall(r'\b\w+\b', texto_completo.lower())
        contador_palabras = Counter(palabras)
        
        # Palabras más frecuentes (excluyendo artículos, preposiciones, etc.)
        palabras_excluir = {'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'pero', 'sus', 'como', 'esto', 'esta', 'está', 'ser', 'son', 'han', 'más', 'muy', 'puede', 'debe', 'cada', 'todo', 'todos', 'otras', 'otros', 'mismo', 'también', 'entre', 'sobre', 'desde', 'hasta', 'donde', 'cuando', 'cual', 'cuales', 'quien', 'quienes'}
        
        palabras_relevantes = {p: c for p, c in contador_palabras.items() 
                             if len(p) > 3 and p not in palabras_excluir}
        
        detalles['analisis']['palabras_mas_frecuentes'] = dict(
            sorted(palabras_relevantes.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # Detectar repeticiones excesivas
        total_palabras = len(palabras)
        umbral_repeticion = self.criterios_validacion['coherencia']['palabras_clave_repetidas']
        
        for palabra, frecuencia in palabras_relevantes.items():
            if frecuencia / total_palabras > umbral_repeticion:
                detalles['analisis']['repeticiones_excesivas'].append({
                    'palabra': palabra,
                    'frecuencia': frecuencia,
                    'porcentaje': (frecuencia / total_palabras) * 100
                })
        
        # Variedad de vocabulario (ratio de palabras únicas)
        palabras_unicas = len(set(palabras))
        detalles['analisis']['variedad_vocabulario'] = palabras_unicas / total_palabras if total_palabras > 0 else 0
        
        # Calcular puntaje basado en calidad del texto
        puntaje_base = self.criterios_validacion['coherencia']['peso']
        
        # Penalizar repeticiones excesivas
        if detalles['analisis']['repeticiones_excesivas']:
            penalizacion = min(len(detalles['analisis']['repeticiones_excesivas']) * 2, puntaje_base // 2)
            puntaje_base -= penalizacion
        
        # Bonificar buena variedad de vocabulario
        if detalles['analisis']['variedad_vocabulario'] > 0.3:  # 30% de palabras únicas es bueno
            puntaje_base += 2
        
        detalles['puntaje'] = max(0, puntaje_base)
        
        # Generar advertencias
        if detalles['analisis']['repeticiones_excesivas']:
            for rep in detalles['analisis']['repeticiones_excesivas']:
                resultado['advertencias'].append(
                    f"⚠️ Palabra '{rep['palabra']}' se repite excesivamente ({rep['frecuencia']} veces, {rep['porcentaje']:.1f}%)"
                )
        
        if detalles['analisis']['variedad_vocabulario'] < 0.2:
            resultado['advertencias'].append("⚠️ Vocabulario limitado, considera usar sinónimos y variedad de términos")
        
        resultado['detalles_por_categoria']['coherencia'] = detalles
    
    def calcular_puntaje_final(self, resultado):
        """Calcula el puntaje final del proyecto"""
        puntaje_total = 0
        puntaje_maximo = 0
        
        for categoria, detalles in resultado['detalles_por_categoria'].items():
            puntaje_total += detalles['puntaje']
            puntaje_maximo += detalles['puntaje_maximo']
        
        resultado['puntaje_total'] = puntaje_total
        resultado['puntaje_maximo'] = puntaje_maximo
        resultado['porcentaje'] = (puntaje_total / puntaje_maximo * 100) if puntaje_maximo > 0 else 0
    
    def generar_recomendaciones(self, resultado):
        """Genera recomendaciones específicas basadas en la validación"""
        recomendaciones = []
        
        # Recomendaciones basadas en errores comunes
        if resultado['errores']:
            recomendaciones.append("🔧 Corrige primero todos los errores marcados")
        
        # Recomendaciones por categoría
        for categoria, detalles in resultado['detalles_por_categoria'].items():
            if categoria == 'informacion_general':
                if detalles['puntaje'] < detalles['puntaje_maximo'] * 0.8:
                    recomendaciones.append("📝 Completa y mejora la información general del proyecto")
            
            elif categoria == 'contenido_secciones':
                secciones_vacias = detalles.get('estadisticas', {}).get('secciones_vacias', 0)
                if secciones_vacias > 0:
                    recomendaciones.append(f"✍️ Completa las {secciones_vacias} secciones vacías")
            
            elif categoria == 'referencias':
                if detalles['total_referencias'] < 5:
                    recomendaciones.append("📚 Agrega más referencias bibliográficas para fortalecer el marco teórico")
            
            elif categoria == 'citas':
                if detalles['estadisticas']['total_citas'] < 3:
                    recomendaciones.append("📖 Incluye más citas en el texto para respaldar tus afirmaciones")
        
        # Recomendaciones generales según puntaje
        porcentaje = resultado['porcentaje']
        if porcentaje < 50:
            recomendaciones.append("🚨 El proyecto necesita trabajo significativo antes de presentación")
        elif porcentaje < 70:
            recomendaciones.append("⚠️ El proyecto está en desarrollo, continúa mejorando las áreas marcadas")
        elif porcentaje < 90:
            recomendaciones.append("👍 Buen progreso, refina los detalles para alcanzar excelencia")
        else:
            recomendaciones.append("🎉 ¡Excelente trabajo! El proyecto cumple con altos estándares de calidad")
        
        resultado['recomendaciones'] = recomendaciones
    
    def mostrar_resultados_validacion(self, resultado):
        """Muestra los resultados de validación en una ventana detallada"""
        result_window = ctk.CTkToplevel(self.app.root)
        result_window.title("🔍 Resultados de Validación Completa")
        result_window.geometry("1000x700")
        result_window.transient(self.app.root)
        
        # Centrar ventana
        result_window.update_idletasks()
        x = (result_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (result_window.winfo_screenheight() // 2) - (700 // 2)
        result_window.geometry(f"1000x700+{x}+{y}")
        
        # Crear interfaz
        self.crear_interfaz_resultados(result_window, resultado)
    
    def crear_interfaz_resultados(self, window, resultado):
        """Crea la interfaz para mostrar resultados de validación"""
        main_frame = ctk.CTkFrame(window, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header con puntaje principal
        self.crear_header_resultados(main_frame, resultado)
        
        # Tabview con detalles
        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        
        # Pestaña de resumen
        resumen_tab = tabview.add("📊 Resumen")
        self.crear_tab_resumen(resumen_tab, resultado)
        
        # Pestaña de detalles por categoría
        detalles_tab = tabview.add("🔍 Detalles")
        self.crear_tab_detalles(detalles_tab, resultado)
        
        # Pestaña de estadísticas
        stats_tab = tabview.add("📈 Estadísticas")
        self.crear_tab_estadisticas(stats_tab, resultado)
        
        # Pestaña de recomendaciones
        recom_tab = tabview.add("💡 Recomendaciones")
        self.crear_tab_recomendaciones(recom_tab, resultado)
        
        # Botones finales
        self.crear_botones_resultados(main_frame, window, resultado)
    
    def crear_header_resultados(self, parent, resultado):
        """Crea el header con puntaje principal"""
        header_frame = ctk.CTkFrame(parent, height=120, corner_radius=15)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Color basado en puntaje
        porcentaje = resultado['porcentaje']
        if porcentaje >= 90:
            color = "darkgreen"
            emoji = "🎉"
            mensaje = "¡EXCELENTE!"
        elif porcentaje >= 70:
            color = "darkblue"
            emoji = "👍"
            mensaje = "BUEN TRABAJO"
        elif porcentaje >= 50:
            color = "darkorange"
            emoji = "⚠️"
            mensaje = "EN PROGRESO"
        else:
            color = "darkred"
            emoji = "🚨"
            mensaje = "NECESITA TRABAJO"
        
        header_frame.configure(fg_color=color)
        
        # Contenido del header
        content_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Título
        title_label = ctk.CTkLabel(
            content_frame, 
            text=f"🔍 VALIDACIÓN COMPLETA DEL PROYECTO",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="white"
        )
        title_label.pack(pady=(0, 5))
        
        # Puntaje principal
        score_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        score_frame.pack(fill="x")
        
        score_label = ctk.CTkLabel(
            score_frame,
            text=f"{emoji} {porcentaje:.1f}% - {mensaje}",
            font=ctk.CTkFont(size=24, weight="bold"), text_color="white"
        )
        score_label.pack(side="left")
        
        # Estado de aprobación
        estado = "✅ APROBADO" if resultado['aprobado'] else "❌ NO APROBADO"
        estado_label = ctk.CTkLabel(
            score_frame, text=estado,
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        )
        estado_label.pack(side="right")
        
        # Información adicional
        info_text = f"Nivel: {resultado['nivel_validacion'].title()} | Errores: {len(resultado['errores'])} | Advertencias: {len(resultado['advertencias'])}"
        info_label = ctk.CTkLabel(
            content_frame, text=info_text,
            font=ctk.CTkFont(size=11), text_color="lightgray"
        )
        info_label.pack()
    
    def crear_tab_resumen(self, parent, resultado):
        """Crea la pestaña de resumen"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Errores críticos
        if resultado['errores']:
            error_frame = ctk.CTkFrame(scroll_frame, fg_color="darkred", corner_radius=10)
            error_frame.pack(fill="x", pady=(0, 15))
            
            error_title = ctk.CTkLabel(
                error_frame, text="🚨 ERRORES CRÍTICOS",
                font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
            )
            error_title.pack(pady=(15, 10))
            
            for error in resultado['errores']:
                error_label = ctk.CTkLabel(
                    error_frame, text=f"• {error}",
                    font=ctk.CTkFont(size=11), text_color="white",
                    wraplength=800, justify="left"
                )
                error_label.pack(anchor="w", padx=15, pady=2)
            
            error_frame.pack_configure(pady=(0, 15))
        
        # Advertencias
        if resultado['advertencias']:
            warn_frame = ctk.CTkFrame(scroll_frame, fg_color="darkorange", corner_radius=10)
            warn_frame.pack(fill="x", pady=(0, 15))
            
            warn_title = ctk.CTkLabel(
                warn_frame, text="⚠️ ADVERTENCIAS",
                font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
            )
            warn_title.pack(pady=(15, 10))
            
            for advertencia in resultado['advertencias'][:10]:  # Mostrar máximo 10
                warn_label = ctk.CTkLabel(
                    warn_frame, text=f"• {advertencia}",
                    font=ctk.CTkFont(size=11), text_color="white",
                    wraplength=800, justify="left"
                )
                warn_label.pack(anchor="w", padx=15, pady=2)
            
            if len(resultado['advertencias']) > 10:
                more_label = ctk.CTkLabel(
                    warn_frame, text=f"... y {len(resultado['advertencias']) - 10} más",
                    font=ctk.CTkFont(size=10), text_color="lightgray"
                )
                more_label.pack(padx=15, pady=(0, 15))
            else:
                warn_frame.pack_configure(pady=(0, 15))
        
        # Resumen por categorías
        cat_frame = ctk.CTkFrame(scroll_frame, fg_color="darkblue", corner_radius=10)
        cat_frame.pack(fill="x")
        
        cat_title = ctk.CTkLabel(
            cat_frame, text="📊 PUNTAJE POR CATEGORÍAS",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        cat_title.pack(pady=(15, 10))
        
        for categoria, detalles in resultado['detalles_por_categoria'].items():
            porcentaje_cat = (detalles['puntaje'] / detalles['puntaje_maximo'] * 100) if detalles['puntaje_maximo'] > 0 else 0
            
            cat_item = ctk.CTkLabel(
                cat_frame, 
                text=f"• {detalles['categoria']}: {porcentaje_cat:.1f}% ({detalles['puntaje']}/{detalles['puntaje_maximo']})",
                font=ctk.CTkFont(size=12), text_color="white", justify="left"
            )
            cat_item.pack(anchor="w", padx=15, pady=2)
        
        cat_frame.pack_configure(pady=(0, 15))
    
    def crear_tab_detalles(self, parent, resultado):
        """Crea la pestaña de detalles por categoría"""
        # Implementación de detalles expandidos
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Mostrar detalles para cada categoría
        for categoria, detalles in resultado['detalles_por_categoria'].items():
            self.crear_detalle_categoria(scroll_frame, categoria, detalles)
    
    def crear_detalle_categoria(self, parent, categoria, detalles):
        """Crea detalle para una categoría específica"""
        cat_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)
        cat_frame.pack(fill="x", pady=(0, 15))
        
        # Título de categoría
        title_label = ctk.CTkLabel(
            cat_frame, text=f"📋 {detalles['categoria']}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # Puntaje de categoría
        porcentaje_cat = (detalles['puntaje'] / detalles['puntaje_maximo'] * 100) if detalles['puntaje_maximo'] > 0 else 0
        score_label = ctk.CTkLabel(
            cat_frame, 
            text=f"Puntaje: {detalles['puntaje']}/{detalles['puntaje_maximo']} ({porcentaje_cat:.1f}%)",
            font=ctk.CTkFont(size=12), text_color="gray70"
        )
        score_label.pack(pady=(0, 10))
        
        # Detalles específicos según categoría
        if categoria == 'informacion_general' and 'campos_validados' in detalles:
            for campo, info in detalles['campos_validados'].items():
                campo_text = f"• {campo.replace('_', ' ').title()}: "
                if info['errores']:
                    campo_text += f"❌ {info['errores'][0]}"
                    color = "lightcoral"
                elif info['puntaje'] == info['puntaje_maximo']:
                    campo_text += "✅ Completo"
                    color = "lightgreen"
                else:
                    campo_text += "⚠️ Incompleto"
                    color = "orange"
                
                campo_label = ctk.CTkLabel(
                    cat_frame, text=campo_text,
                    font=ctk.CTkFont(size=11), text_color=color
                )
                campo_label.pack(anchor="w", padx=15, pady=2)
        
        cat_frame.pack_configure(pady=(0, 15))
    
    def crear_tab_estadisticas(self, parent, resultado):
        """Crea la pestaña de estadísticas"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Mostrar estadísticas si existen
        if 'estadisticas' in resultado:
            for categoria, stats in resultado['estadisticas'].items():
                if stats:  # Solo mostrar si hay datos
                    self.crear_estadisticas_categoria(scroll_frame, categoria, stats)
    
    def crear_estadisticas_categoria(self, parent, categoria, stats):
        """Crea estadísticas para una categoría"""
        stats_frame = ctk.CTkFrame(parent, fg_color="darkgreen", corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 15))
        
        title_label = ctk.CTkLabel(
            stats_frame, text=f"📈 Estadísticas - {categoria.title()}",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        title_label.pack(pady=(15, 10))
        
        # Mostrar estadísticas según tipo
        if isinstance(stats, dict):
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    stat_text = f"• {key.replace('_', ' ').title()}: {value}"
                elif isinstance(value, list):
                    stat_text = f"• {key.replace('_', ' ').title()}: {len(value)} elementos"
                else:
                    stat_text = f"• {key.replace('_', ' ').title()}: {str(value)}"
                
                stat_label = ctk.CTkLabel(
                    stats_frame, text=stat_text,
                    font=ctk.CTkFont(size=11), text_color="white"
                )
                stat_label.pack(anchor="w", padx=15, pady=2)
        
        stats_frame.pack_configure(pady=(0, 15))
    
    def crear_tab_recomendaciones(self, parent, resultado):
        """Crea la pestaña de recomendaciones"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        recom_frame = ctk.CTkFrame(scroll_frame, fg_color="purple", corner_radius=10)
        recom_frame.pack(fill="x", pady=(0, 15))
        
        title_label = ctk.CTkLabel(
            recom_frame, text="💡 RECOMENDACIONES PERSONALIZADAS",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white"
        )
        title_label.pack(pady=(15, 10))
        
        for recomendacion in resultado['recomendaciones']:
            recom_label = ctk.CTkLabel(
                recom_frame, text=f"• {recomendacion}",
                font=ctk.CTkFont(size=12), text_color="white",
                wraplength=800, justify="left"
            )
            recom_label.pack(anchor="w", padx=15, pady=5)
        
        recom_frame.pack_configure(pady=(0, 15))
    
    def crear_botones_resultados(self, parent, window, resultado):
        """Crea botones para las acciones finales"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        # Botón para exportar reporte
        export_btn = ctk.CTkButton(
            btn_frame, text="📤 Exportar Reporte",
            command=lambda: self.exportar_reporte_validacion(resultado),
            width=150, height=35
        )
        export_btn.pack(side="left")
        
        # Botón para nueva validación
        revalidate_btn = ctk.CTkButton(
            btn_frame, text="🔄 Validar Nuevamente",
            command=lambda: [window.destroy(), self.validar_proyecto_completo()],
            width=150, height=35, fg_color="orange", hover_color="darkorange"
        )
        revalidate_btn.pack(side="left", padx=(10, 0))
        
        # Botón cerrar
        close_btn = ctk.CTkButton(
            btn_frame, text="✅ Cerrar", command=window.destroy,
            width=120, height=35
        )
        close_btn.pack(side="right")
    
    def exportar_reporte_validacion(self, resultado):
        """Exporta el reporte de validación a archivo"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt"), ("JSON", "*.json")],
                title="Exportar Reporte de Validación"
            )
            
            if filename:
                if filename.endswith('.json'):
                    self.exportar_reporte_json(filename, resultado)
                else:
                    self.exportar_reporte_texto(filename, resultado)
                
                messagebox.showinfo("📤 Exportado", f"Reporte exportado a:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al exportar reporte:\n{str(e)}")
    
    def exportar_reporte_texto(self, filename, resultado):
        """Exporta reporte en formato de texto"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("🔍 REPORTE DE VALIDACIÓN DE PROYECTO ACADÉMICO\n")
            f.write("=" * 60 + "\n\n")
            
            # Información general
            f.write(f"Fecha de validación: {resultado['timestamp']}\n")
            f.write(f"Nivel de validación: {resultado['nivel_validacion'].title()}\n")
            f.write(f"Puntaje total: {resultado['puntaje_total']}/{resultado['puntaje_maximo']} ({resultado['porcentaje']:.1f}%)\n")
            f.write(f"Estado: {'APROBADO' if resultado['aprobado'] else 'NO APROBADO'}\n\n")
            
            # Errores
            if resultado['errores']:
                f.write("🚨 ERRORES CRÍTICOS:\n")
                for error in resultado['errores']:
                    f.write(f"  • {error}\n")
                f.write("\n")
            
            # Advertencias
            if resultado['advertencias']:
                f.write("⚠️ ADVERTENCIAS:\n")
                for advertencia in resultado['advertencias']:
                    f.write(f"  • {advertencia}\n")
                f.write("\n")
            
            # Recomendaciones
            if resultado['recomendaciones']:
                f.write("💡 RECOMENDACIONES:\n")
                for recomendacion in resultado['recomendaciones']:
                    f.write(f"  • {recomendacion}\n")
                f.write("\n")
            
            # Detalles por categoría
            f.write("📊 DETALLES POR CATEGORÍA:\n")
            f.write("-" * 40 + "\n")
            for categoria, detalles in resultado['detalles_por_categoria'].items():
                porcentaje = (detalles['puntaje'] / detalles['puntaje_maximo'] * 100) if detalles['puntaje_maximo'] > 0 else 0
                f.write(f"\n{detalles['categoria']}: {porcentaje:.1f}% ({detalles['puntaje']}/{detalles['puntaje_maximo']})\n")
    
    def exportar_reporte_json(self, filename, resultado):
        """Exporta reporte en formato JSON"""
        import json
        
        # Crear copia del resultado para exportar
        resultado_export = resultado.copy()
        
        # Convertir sets a listas si existen
        def convert_sets(obj):
            if isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, dict):
                return {k: convert_sets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_sets(item) for item in obj]
            return obj
        
        resultado_export = convert_sets(resultado_export)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultado_export, f, ensure_ascii=False, indent=2)
    
    # Métodos auxiliares
    def obtener_contenido_seccion(self, seccion_id):
        """Obtiene el contenido de una sección específica"""
        if seccion_id in self.app.content_texts:
            return self.app.content_texts[seccion_id].get("1.0", "end").strip()
        return ""
    
    def obtener_texto_completo(self):
        """Obtiene todo el texto del proyecto"""
        texto_completo = ""
        for seccion_id in self.app.secciones_activas:
            if seccion_id in self.app.content_texts:
                contenido = self.app.content_texts[seccion_id].get("1.0", "end").strip()
                if contenido:
                    texto_completo += contenido + " "
        return texto_completo.strip()