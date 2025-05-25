"""
Análisis de texto avanzado para proyectos académicos

Proporciona métricas de legibilidad, análisis semántico,
detección de problemas comunes y sugerencias de mejora.
"""

import re
import nltk
import textstat
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from utils.logger import get_logger
from utils.cache import cached

# Descargar recursos NLTK necesarios
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

logger = get_logger('TextAnalyzer')

class TextAnalyzer:
    """Analizador avanzado de texto académico"""
    
    def __init__(self, language='spanish'):
        """
        Inicializa el analizador
        
        Args:
            language: Idioma del texto ('spanish' o 'english')
        """
        self.language = language
        self.stopwords = set(nltk.corpus.stopwords.words(language))
        
        # Palabras de transición comunes en español
        self.transition_words = {
            'addition': ['además', 'también', 'asimismo', 'igualmente', 'del mismo modo'],
            'contrast': ['sin embargo', 'no obstante', 'pero', 'aunque', 'mientras que'],
            'cause': ['porque', 'debido a', 'ya que', 'puesto que', 'dado que'],
            'effect': ['por lo tanto', 'en consecuencia', 'así', 'entonces', 'por ende'],
            'sequence': ['primero', 'segundo', 'finalmente', 'posteriormente', 'a continuación'],
            'example': ['por ejemplo', 'tales como', 'como', 'específicamente', 'en particular'],
            'conclusion': ['en conclusión', 'en resumen', 'finalmente', 'para concluir', 'en síntesis']
        }
        
        # Verbos académicos por categoría
        self.academic_verbs = {
            'analyze': ['analizar', 'examinar', 'estudiar', 'investigar', 'explorar'],
            'argue': ['argumentar', 'sostener', 'afirmar', 'plantear', 'proponer'],
            'compare': ['comparar', 'contrastar', 'diferenciar', 'distinguir', 'relacionar'],
            'define': ['definir', 'conceptualizar', 'caracterizar', 'delimitar', 'especificar'],
            'evaluate': ['evaluar', 'valorar', 'juzgar', 'estimar', 'apreciar']
        }
        
        logger.info(f"TextAnalyzer inicializado para idioma: {language}")
    
    @cached(ttl=300)  # Cache por 5 minutos
    def analyze_complete(self, text: str, section_type: Optional[str] = None) -> Dict:
        """
        Realiza un análisis completo del texto
        
        Args:
            text: Texto a analizar
            section_type: Tipo de sección (introduccion, marco_teorico, etc.)
            
        Returns:
            Dict con todos los análisis
        """
        if not text or not text.strip():
            return self._empty_analysis()
        
        logger.debug(f"Analizando texto de {len(text)} caracteres")
        
        analysis = {
            'basic_stats': self.get_basic_statistics(text),
            'readability': self.analyze_readability(text),
            'vocabulary': self.analyze_vocabulary(text),
            'structure': self.analyze_structure(text),
            'coherence': self.analyze_coherence(text),
            'academic_style': self.analyze_academic_style(text),
            'problems': self.detect_problems(text),
            'suggestions': self.generate_suggestions(text, section_type),
            'timestamp': datetime.now().isoformat()
        }
        
        # Agregar análisis específico por sección
        if section_type:
            analysis['section_specific'] = self.analyze_section_specific(text, section_type)
        
        return analysis
    
    def get_basic_statistics(self, text: str) -> Dict:
        """Obtiene estadísticas básicas del texto"""
        sentences = nltk.sent_tokenize(text, language=self.language)
        words = nltk.word_tokenize(text, language=self.language)
        words_clean = [w.lower() for w in words if w.isalpha()]
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        return {
            'characters': len(text),
            'characters_no_spaces': len(text.replace(' ', '')),
            'words': len(words_clean),
            'unique_words': len(set(words_clean)),
            'sentences': len(sentences),
            'paragraphs': len(paragraphs),
            'avg_words_per_sentence': len(words_clean) / max(1, len(sentences)),
            'avg_sentences_per_paragraph': len(sentences) / max(1, len(paragraphs)),
            'lexical_diversity': len(set(words_clean)) / max(1, len(words_clean))
        }
    
    def analyze_readability(self, text: str) -> Dict:
        """Analiza la legibilidad del texto"""
        try:
            # Índices de legibilidad
            readability_scores = {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'gunning_fog': textstat.gunning_fog(text),
                'automated_readability_index': textstat.automated_readability_index(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'linsear_write_formula': textstat.linsear_write_formula(text),
                'dale_chall_readability_score': textstat.dale_chall_readability_score(text),
                'text_standard': textstat.text_standard(text, float_output=False)
            }
            
            # Interpretar nivel de dificultad
            flesch = readability_scores['flesch_reading_ease']
            if flesch >= 90:
                difficulty = "Muy fácil"
            elif flesch >= 80:
                difficulty = "Fácil"
            elif flesch >= 70:
                difficulty = "Bastante fácil"
            elif flesch >= 60:
                difficulty = "Estándar"
            elif flesch >= 50:
                difficulty = "Bastante difícil"
            elif flesch >= 30:
                difficulty = "Difícil"
            else:
                difficulty = "Muy difícil"
            
            readability_scores['difficulty_level'] = difficulty
            readability_scores['recommended_education_level'] = self._interpret_grade_level(
                readability_scores['flesch_kincaid_grade']
            )
            
            return readability_scores
            
        except Exception as e:
            logger.error(f"Error analizando legibilidad: {e}")
            return {'error': str(e)}
    
    def analyze_vocabulary(self, text: str) -> Dict:
        """Analiza el vocabulario utilizado"""
        words = nltk.word_tokenize(text.lower(), language=self.language)
        words_clean = [w for w in words if w.isalpha()]
        
        # Filtrar stopwords
        content_words = [w for w in words_clean if w not in self.stopwords]
        
        # Análisis de frecuencia
        word_freq = Counter(words_clean)
        content_word_freq = Counter(content_words)
        
        # Palabras más comunes
        most_common = content_word_freq.most_common(20)
        
        # Longitud de palabras
        word_lengths = [len(w) for w in words_clean]
        avg_word_length = sum(word_lengths) / max(1, len(word_lengths))
        
        # Palabras largas (más de 10 caracteres)
        long_words = [w for w in set(words_clean) if len(w) > 10]
        
        # Detectar palabras académicas
        academic_words = self._detect_academic_vocabulary(content_words)
        
        return {
            'total_words': len(words_clean),
            'unique_words': len(set(words_clean)),
            'content_words': len(content_words),
            'avg_word_length': round(avg_word_length, 2),
            'long_words': long_words[:20],  # Top 20
            'most_common_words': most_common,
            'academic_words': academic_words,
            'vocabulary_richness': len(set(content_words)) / max(1, len(content_words))
        }
    
    def analyze_structure(self, text: str) -> Dict:
        """Analiza la estructura del texto"""
        sentences = nltk.sent_tokenize(text, language=self.language)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Longitud de oraciones
        sentence_lengths = [len(nltk.word_tokenize(s, language=self.language)) for s in sentences]
        
        # Longitud de párrafos
        paragraph_lengths = [len(nltk.sent_tokenize(p, language=self.language)) for p in paragraphs]
        
        # Detectar palabras de transición
        transitions_found = self._detect_transitions(text)
        
        # Detectar estructura de párrafos (inicio, desarrollo, conclusión)
        paragraph_types = self._classify_paragraphs(paragraphs)
        
        return {
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'avg_sentence_length': sum(sentence_lengths) / max(1, len(sentence_lengths)),
            'max_sentence_length': max(sentence_lengths) if sentence_lengths else 0,
            'min_sentence_length': min(sentence_lengths) if sentence_lengths else 0,
            'avg_paragraph_length': sum(paragraph_lengths) / max(1, len(paragraph_lengths)),
            'transitions_used': transitions_found,
            'transition_density': len(transitions_found) / max(1, len(sentences)),
            'paragraph_classification': paragraph_types
        }
    
    def analyze_coherence(self, text: str) -> Dict:
        """Analiza la coherencia y cohesión del texto"""
        sentences = nltk.sent_tokenize(text, language=self.language)
        
        # Análisis de repetición de palabras clave entre oraciones
        keyword_chains = self._analyze_keyword_chains(sentences)
        
        # Análisis de conectores
        connectors = self._analyze_connectors(text)
        
        # Análisis de pronombres y referencias
        references = self._analyze_references(text)
        
        return {
            'keyword_chains': keyword_chains,
            'connector_usage': connectors,
            'reference_chains': references,
            'coherence_score': self._calculate_coherence_score(keyword_chains, connectors, references)
        }
    
    def analyze_academic_style(self, text: str) -> Dict:
        """Analiza el estilo académico del texto"""
        # Detectar características de estilo académico
        features = {
            'passive_voice': self._detect_passive_voice(text),
            'nominalizations': self._detect_nominalizations(text),
            'academic_verbs': self._count_academic_verbs(text),
            'personal_pronouns': self._detect_personal_pronouns(text),
            'informal_expressions': self._detect_informal_expressions(text),
            'citations_indicators': self._detect_citation_indicators(text)
        }
        
        # Calcular puntuación de estilo académico
        academic_score = self._calculate_academic_score(features)
        
        return {
            'features': features,
            'academic_score': academic_score,
            'style_level': self._interpret_academic_level(academic_score)
        }
    
    def detect_problems(self, text: str) -> List[Dict]:
        """Detecta problemas comunes en el texto"""
        problems = []
        
        # Oraciones muy largas
        sentences = nltk.sent_tokenize(text, language=self.language)
        for i, sentence in enumerate(sentences):
            words = nltk.word_tokenize(sentence, language=self.language)
            if len(words) > 40:
                problems.append({
                    'type': 'long_sentence',
                    'severity': 'medium',
                    'location': f'Oración {i+1}',
                    'description': f'Oración muy larga ({len(words)} palabras)',
                    'suggestion': 'Considera dividir esta oración en dos o más oraciones más cortas.'
                })
        
        # Párrafos muy cortos o muy largos
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        for i, para in enumerate(paragraphs):
            sentences_in_para = nltk.sent_tokenize(para, language=self.language)
            if len(sentences_in_para) < 2:
                problems.append({
                    'type': 'short_paragraph',
                    'severity': 'low',
                    'location': f'Párrafo {i+1}',
                    'description': 'Párrafo muy corto (menos de 2 oraciones)',
                    'suggestion': 'Desarrolla más la idea o combina con otro párrafo.'
                })
            elif len(sentences_in_para) > 8:
                problems.append({
                    'type': 'long_paragraph',
                    'severity': 'medium',
                    'location': f'Párrafo {i+1}',
                    'description': f'Párrafo muy largo ({len(sentences_in_para)} oraciones)',
                    'suggestion': 'Considera dividir este párrafo para mejorar la legibilidad.'
                })
        
        # Repetición excesiva de palabras
        word_repetitions = self._detect_excessive_repetition(text)
        for word, count in word_repetitions:
            problems.append({
                'type': 'word_repetition',
                'severity': 'low',
                'location': 'Todo el texto',
                'description': f'La palabra "{word}" se repite {count} veces',
                'suggestion': f'Busca sinónimos o reformula para evitar la repetición excesiva de "{word}".'
            })
        
        # Falta de palabras de transición
        transitions = self._detect_transitions(text)
        if len(transitions) < len(sentences) * 0.2:  # Menos del 20% de oraciones con transiciones
            problems.append({
                'type': 'lack_of_transitions',
                'severity': 'medium',
                'location': 'Todo el texto',
                'description': 'Pocas palabras de transición detectadas',
                'suggestion': 'Agrega conectores y palabras de transición para mejorar el flujo del texto.'
            })
        
        return problems
    
    def generate_suggestions(self, text: str, section_type: Optional[str] = None) -> List[str]:
        """Genera sugerencias específicas para mejorar el texto"""
        suggestions = []
        
        # Analizar estadísticas básicas
        stats = self.get_basic_statistics(text)
        
        # Sugerencias basadas en longitud
        if stats['words'] < 100:
            suggestions.append("📝 El texto es muy corto. Considera desarrollar más las ideas principales.")
        
        # Sugerencias basadas en diversidad léxica
        if stats['lexical_diversity'] < 0.4:
            suggestions.append("📚 La diversidad léxica es baja. Intenta usar sinónimos y vocabulario más variado.")
        
        # Sugerencias basadas en estructura
        if stats['avg_words_per_sentence'] > 25:
            suggestions.append("✂️ Las oraciones son muy largas en promedio. Considera usar oraciones más cortas y directas.")
        elif stats['avg_words_per_sentence'] < 10:
            suggestions.append("🔗 Las oraciones son muy cortas. Combina algunas para mejorar el flujo.")
        
        # Sugerencias específicas por sección
        if section_type:
            section_suggestions = self._get_section_specific_suggestions(text, section_type)
            suggestions.extend(section_suggestions)
        
        # Sugerencias de estilo académico
        academic_style = self.analyze_academic_style(text)
        if academic_style['academic_score'] < 0.5:
            suggestions.append("🎓 El estilo podría ser más académico. Usa verbos académicos y evita expresiones informales.")
        
        return suggestions
    
    def analyze_section_specific(self, text: str, section_type: str) -> Dict:
        """Realiza análisis específico según el tipo de sección"""
        analyses = {
            'introduccion': self._analyze_introduction,
            'marco_teorico': self._analyze_theoretical_framework,
            'metodologia': self._analyze_methodology,
            'resultados': self._analyze_results,
            'conclusiones': self._analyze_conclusions
        }
        
        analyzer = analyses.get(section_type, self._analyze_generic)
        return analyzer(text)
    
    # Métodos auxiliares privados
    
    def _empty_analysis(self) -> Dict:
        """Retorna un análisis vacío"""
        return {
            'basic_stats': {},
            'readability': {},
            'vocabulary': {},
            'structure': {},
            'coherence': {},
            'academic_style': {},
            'problems': [],
            'suggestions': ["No hay texto para analizar"],
            'timestamp': datetime.now().isoformat()
        }
    
    def _interpret_grade_level(self, grade: float) -> str:
        """Interpreta el nivel de grado educativo"""
        if grade < 6:
            return "Primaria"
        elif grade < 9:
            return "Secundaria básica"
        elif grade < 13:
            return "Secundaria superior"
        elif grade < 16:
            return "Universitario"
        else:
            return "Postgrado"
    
    def _detect_academic_vocabulary(self, words: List[str]) -> List[str]:
        """Detecta vocabulario académico en el texto"""
        academic_terms = {
            'análisis', 'síntesis', 'hipótesis', 'teoría', 'metodología',
            'investigación', 'estudio', 'resultados', 'conclusión', 'evidencia',
            'datos', 'muestra', 'variable', 'correlación', 'significativo',
            'paradigma', 'enfoque', 'perspectiva', 'marco', 'conceptual',
            'empírico', 'cualitativo', 'cuantitativo', 'sistemático', 'riguroso'
        }
        
        found = [w for w in words if w in academic_terms]
        return list(set(found))
    
    def _detect_transitions(self, text: str) -> List[Tuple[str, str]]:
        """Detecta palabras y frases de transición"""
        found_transitions = []
        text_lower = text.lower()
        
        for category, transitions in self.transition_words.items():
            for transition in transitions:
                if transition in text_lower:
                    count = text_lower.count(transition)
                    found_transitions.extend([(transition, category)] * count)
        
        return found_transitions
    
    def _classify_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """Clasifica párrafos según su función"""
        classifications = []
        
        for para in paragraphs:
            if any(intro in para.lower() for intro in ['el presente trabajo', 'este estudio', 'el objetivo']):
                classifications.append('introduction')
            elif any(dev in para.lower() for dev in ['por lo tanto', 'además', 'asimismo']):
                classifications.append('development')
            elif any(conc in para.lower() for conc in ['en conclusión', 'finalmente', 'en resumen']):
                classifications.append('conclusion')
            else:
                classifications.append('body')
        
        return classifications
    
    def _analyze_keyword_chains(self, sentences: List[str]) -> Dict:
        """Analiza cadenas de palabras clave entre oraciones"""
        keyword_chains = defaultdict(list)
        
        for i, sentence in enumerate(sentences):
            words = set(w.lower() for w in nltk.word_tokenize(sentence, language=self.language) 
                       if w.isalpha() and w.lower() not in self.stopwords)
            
            if i > 0:
                prev_words = set(w.lower() for w in nltk.word_tokenize(sentences[i-1], language=self.language) 
                               if w.isalpha() and w.lower() not in self.stopwords)
                
                shared = words & prev_words
                for word in shared:
                    keyword_chains[word].append((i-1, i))
        
        return dict(keyword_chains)
    
    def _analyze_connectors(self, text: str) -> Dict:
        """Analiza el uso de conectores"""
        connectors = {
            'addition': 0,
            'contrast': 0,
            'cause': 0,
            'effect': 0,
            'sequence': 0,
            'example': 0,
            'conclusion': 0
        }
        
        text_lower = text.lower()
        for category, words in self.transition_words.items():
            for word in words:
                if word in text_lower:
                    connectors[category] += text_lower.count(word)
        
        return connectors
    
    def _analyze_references(self, text: str) -> Dict:
        """Analiza referencias y pronombres"""
        pronouns = {
            'personal': ['yo', 'tú', 'él', 'ella', 'nosotros', 'ustedes', 'ellos'],
            'demonstrative': ['este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas'],
            'relative': ['que', 'cual', 'cuales', 'quien', 'quienes', 'cuyo', 'cuya']
        }
        
        references = defaultdict(int)
        text_lower = text.lower()
        
        for category, pron_list in pronouns.items():
            for pron in pron_list:
                references[category] += len(re.findall(r'\b' + pron + r'\b', text_lower))
        
        return dict(references)
    
    def _calculate_coherence_score(self, keyword_chains: Dict, connectors: Dict, references: Dict) -> float:
        """Calcula una puntuación de coherencia"""
        # Fórmula simple basada en indicadores
        chain_score = min(1.0, len(keyword_chains) / 10)
        connector_score = min(1.0, sum(connectors.values()) / 20)
        reference_score = min(1.0, sum(references.values()) / 30)
        
        return (chain_score + connector_score + reference_score) / 3
    
    def _detect_passive_voice(self, text: str) -> int:
        """Detecta uso de voz pasiva (simplificado para español)"""
        # Patrones comunes de voz pasiva en español
        passive_patterns = [
            r'\b(fue|fueron|es|son|está|están|será|serán)\s+\w+[ai]d[oa]s?\b',
            r'\bse\s+\w+[aó]\b'
        ]
        
        count = 0
        for pattern in passive_patterns:
            count += len(re.findall(pattern, text.lower()))
        
        return count
    
    def _detect_nominalizations(self, text: str) -> List[str]:
        """Detecta nominalizaciones comunes"""
        # Sufijos comunes de nominalización en español
        suffixes = ['ción', 'sión', 'miento', 'anza', 'encia', 'idad', 'ismo', 'ura']
        
        words = nltk.word_tokenize(text.lower(), language=self.language)
        nominalizations = []
        
        for word in set(words):
            if any(word.endswith(suffix) for suffix in suffixes) and len(word) > 7:
                nominalizations.append(word)
        
        return nominalizations[:20]  # Top 20
    
    def _count_academic_verbs(self, text: str) -> Dict[str, int]:
        """Cuenta el uso de verbos académicos"""
        verb_counts = defaultdict(int)
        text_lower = text.lower()
        
        for category, verbs in self.academic_verbs.items():
            for verb in verbs:
                # Buscar diferentes conjugaciones
                verb_root = verb[:-2] if verb.endswith('ar') or verb.endswith('er') or verb.endswith('ir') else verb
                count = len(re.findall(r'\b' + verb_root + r'\w*\b', text_lower))
                if count > 0:
                    verb_counts[category] += count
        
        return dict(verb_counts)
    
    def _detect_personal_pronouns(self, text: str) -> int:
        """Detecta pronombres personales de primera persona"""
        first_person = ['yo', 'me', 'mí', 'conmigo', 'nosotros', 'nos']
        count = 0
        text_lower = text.lower()
        
        for pronoun in first_person:
            count += len(re.findall(r'\b' + pronoun + r'\b', text_lower))
        
        return count
    
    def _detect_informal_expressions(self, text: str) -> List[str]:
        """Detecta expresiones informales"""
        informal = [
            'bueno', 'pues', 'o sea', 'así que', 'la verdad', 'en realidad',
            'obviamente', 'básicamente', 'simplemente', 'realmente'
        ]
        
        found = []
        text_lower = text.lower()
        
        for expr in informal:
            if expr in text_lower:
                found.append(expr)
        
        return found
    
    def _detect_citation_indicators(self, text: str) -> int:
        """Detecta indicadores de citas"""
        # Patrones que indican citas
        patterns = [
            r'\([A-Z][a-z]+,?\s+\d{4}\)',  # (Autor, 2020)
            r'según\s+[A-Z][a-z]+',         # según García
            r'de acuerdo con',              # de acuerdo con
            r'\bcita\b',                    # cita
            r'\bafirma\b',                  # afirma
            r'\bseñala\b'                   # señala
        ]
        
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text))
        
        return count
    
    def _calculate_academic_score(self, features: Dict) -> float:
        """Calcula puntuación de estilo académico"""
        score = 0.0
        
        # Factores positivos
        score += min(0.2, features['academic_verbs'].get('analyze', 0) * 0.02)
        score += min(0.2, features['citations_indicators'] * 0.02)
        score += min(0.1, len(features['nominalizations']) * 0.01)
        score += min(0.1, features['passive_voice'] * 0.01)
        
        # Factores negativos
        score -= min(0.2, features['personal_pronouns'] * 0.02)
        score -= min(0.2, len(features['informal_expressions']) * 0.05)
        
        return max(0.0, min(1.0, score + 0.5))  # Normalizar entre 0 y 1
    
    def _interpret_academic_level(self, score: float) -> str:
        """Interpreta el nivel de estilo académico"""
        if score >= 0.8:
            return "Altamente académico"
        elif score >= 0.6:
            return "Académico"
        elif score >= 0.4:
            return "Moderadamente académico"
        elif score >= 0.2:
            return "Poco académico"
        else:
            return "Informal"
    
    def _detect_excessive_repetition(self, text: str) -> List[Tuple[str, int]]:
        """Detecta palabras repetidas excesivamente"""
        words = nltk.word_tokenize(text.lower(), language=self.language)
        content_words = [w for w in words if w.isalpha() and w not in self.stopwords and len(w) > 4]
        
        word_freq = Counter(content_words)
        total_words = len(content_words)
        
        # Palabras que aparecen más del 2% del total
        excessive = [(word, count) for word, count in word_freq.items() 
                    if count > total_words * 0.02 and count > 3]
        
        return sorted(excessive, key=lambda x: x[1], reverse=True)[:10]
    
    def _get_section_specific_suggestions(self, text: str, section_type: str) -> List[str]:
        """Genera sugerencias específicas por tipo de sección"""
        suggestions = []
        
        if section_type == 'introduccion':
            if 'objetivo' not in text.lower():
                suggestions.append("🎯 La introducción debe incluir claramente los objetivos del estudio.")
            if 'problema' not in text.lower() and 'pregunta' not in text.lower():
                suggestions.append("❓ Considera incluir la pregunta de investigación o problema a resolver.")
                
        elif section_type == 'marco_teorico':
            citations = self._detect_citation_indicators(text)
            if citations < 5:
                suggestions.append("📚 El marco teórico necesita más referencias y citas de fuentes.")
            if 'teoría' not in text.lower() and 'concepto' not in text.lower():
                suggestions.append("🔍 Asegúrate de definir los conceptos y teorías principales.")
                
        elif section_type == 'metodologia':
            method_keywords = ['método', 'muestra', 'procedimiento', 'instrumento', 'análisis']
            if not any(kw in text.lower() for kw in method_keywords):
                suggestions.append("🔬 La metodología debe describir claramente los métodos utilizados.")
                
        elif section_type == 'conclusiones':
            if 'resultado' not in text.lower():
                suggestions.append("📊 Las conclusiones deben relacionarse con los resultados obtenidos.")
            if 'futuro' not in text.lower() and 'recomenda' not in text.lower():
                suggestions.append("🔮 Considera incluir recomendaciones o líneas futuras de investigación.")
        
        return suggestions
    
    # Análisis específicos por sección
    
    def _analyze_introduction(self, text: str) -> Dict:
        """Análisis específico para introducciones"""
        elements = {
            'has_context': any(word in text.lower() for word in ['contexto', 'antecedente', 'historia']),
            'has_problem': any(word in text.lower() for word in ['problema', 'desafío', 'necesidad']),
            'has_objectives': any(word in text.lower() for word in ['objetivo', 'propósito', 'meta']),
            'has_justification': any(word in text.lower() for word in ['importancia', 'relevancia', 'justifica']),
            'has_scope': any(word in text.lower() for word in ['alcance', 'delimita', 'limita'])
        }
        
        completeness = sum(elements.values()) / len(elements)
        
        return {
            'elements': elements,
            'completeness_score': completeness,
            'missing_elements': [k for k, v in elements.items() if not v]
        }
    
    def _analyze_theoretical_framework(self, text: str) -> Dict:
        """Análisis específico para marco teórico"""
        # Contar definiciones
        definition_patterns = [
            r'se define como',
            r'es definido como',
            r'se entiende por',
            r'consiste en',
            r'se refiere a'
        ]
        
        definitions = 0
        for pattern in definition_patterns:
            definitions += len(re.findall(pattern, text.lower()))
        
        # Contar teorías mencionadas
        theory_indicators = ['teoría', 'modelo', 'paradigma', 'enfoque', 'perspectiva']
        theories = sum(text.lower().count(ind) for ind in theory_indicators)
        
        # Verificar citas
        citations = self._detect_citation_indicators(text)
        
        return {
            'definitions_count': definitions,
            'theories_mentioned': theories,
            'citations_count': citations,
            'citation_density': citations / max(1, len(nltk.sent_tokenize(text, language=self.language)))
        }
    
    def _analyze_methodology(self, text: str) -> Dict:
        """Análisis específico para metodología"""
        elements = {
            'has_design': any(word in text.lower() for word in ['diseño', 'tipo de estudio', 'enfoque']),
            'has_population': any(word in text.lower() for word in ['población', 'universo']),
            'has_sample': any(word in text.lower() for word in ['muestra', 'muestreo', 'participantes']),
            'has_instruments': any(word in text.lower() for word in ['instrumento', 'herramienta', 'cuestionario']),
            'has_procedure': any(word in text.lower() for word in ['procedimiento', 'proceso', 'etapa']),
            'has_analysis': any(word in text.lower() for word in ['análisis', 'estadística', 'procesamiento'])
        }
        
        return {
            'methodological_elements': elements,
            'completeness': sum(elements.values()) / len(elements)
        }
    
    def _analyze_results(self, text: str) -> Dict:
        """Análisis específico para resultados"""
        # Detectar elementos cuantitativos
        numbers = re.findall(r'\b\d+[,.]?\d*\s*%?\b', text)
        
        # Detectar tablas y figuras mencionadas
        tables = len(re.findall(r'tabla\s+\d+', text.lower()))
        figures = len(re.findall(r'figura\s+\d+|gráfico\s+\d+', text.lower()))
        
        # Detectar términos estadísticos
        stat_terms = ['media', 'promedio', 'desviación', 'correlación', 'significativo', 'p-valor']
        stats_mentioned = sum(text.lower().count(term) for term in stat_terms)
        
        return {
            'quantitative_data': len(numbers),
            'tables_referenced': tables,
            'figures_referenced': figures,
            'statistical_terms': stats_mentioned,
            'data_density': len(numbers) / max(1, len(nltk.word_tokenize(text, language=self.language))) * 100
        }
    
    def _analyze_conclusions(self, text: str) -> Dict:
        """Análisis específico para conclusiones"""
        elements = {
            'references_objectives': any(word in text.lower() for word in ['objetivo', 'propósito']),
            'summarizes_findings': any(word in text.lower() for word in ['resultado', 'hallazgo', 'encontr']),
            'has_implications': any(word in text.lower() for word in ['implica', 'significa', 'sugiere']),
            'has_limitations': any(word in text.lower() for word in ['limitación', 'restricción']),
            'has_recommendations': any(word in text.lower() for word in ['recomend', 'suger', 'propone']),
            'has_future_research': any(word in text.lower() for word in ['futuro', 'posterior', 'próximo'])
        }
        
        return {
            'conclusion_elements': elements,
            'completeness': sum(elements.values()) / len(elements)
        }
    
    def _analyze_generic(self, text: str) -> Dict:
        """Análisis genérico para secciones no específicas"""
        return {
            'word_count': len(nltk.word_tokenize(text, language=self.language)),
            'sentence_count': len(nltk.sent_tokenize(text, language=self.language)),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()])
        }