# tests/test_citations.py
import unittest
from modules.citations import CitationProcessor

class TestCitationProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = CitationProcessor()
    
    def test_procesar_cita_simple(self):
        texto = "Según [CITA:parafraseo:García:2020]"
        resultado = self.processor.procesar_citas_avanzado(texto)
        self.assertIn("(García, 2020)", resultado)