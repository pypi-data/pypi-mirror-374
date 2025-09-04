#!/usr/bin/env python3
"""
Script para probar la conversión entre texto plano y ADF
"""

import sys
import json
sys.path.insert(0, 'src')

def test_adf_conversion():
    """Probar las funciones de conversión ADF"""
    
    # Crear una instancia mock de la clase para probar las funciones
    class MockIssuesManager:
        def _text_to_adf(self, text: str) -> dict:
            """Conversión de texto a ADF (copiada de issues.py)"""
            if not text:
                return {
                    "type": "doc",
                    "version": 1,
                    "content": []
                }
            
            # Split text into paragraphs
            paragraphs = text.strip().split('\n\n')
            content = []
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Handle line breaks within paragraphs
                    lines = paragraph.strip().split('\n')
                    paragraph_content = []
                    
                    for i, line in enumerate(lines):
                        if line.strip():
                            paragraph_content.append({
                                "type": "text",
                                "text": line.strip()
                            })
                            # Add hard break for line breaks within paragraph (except last line)
                            if i < len(lines) - 1:
                                paragraph_content.append({
                                    "type": "hardBreak"
                                })
                    
                    if paragraph_content:
                        content.append({
                            "type": "paragraph",
                            "content": paragraph_content
                        })
            
            # If no content was generated, create a simple empty paragraph
            if not content:
                content = [{
                    "type": "paragraph",
                    "content": []
                }]
            
            return {
                "type": "doc",
                "version": 1,
                "content": content
            }
        
        def _adf_to_text(self, adf_content) -> str:
            """Conversión de ADF a texto (copiada de issues.py)"""
            if not adf_content:
                return ""
                
            # If it's already a string, return as-is
            if isinstance(adf_content, str):
                return adf_content
                
            # If it's not a dict (ADF structure), convert to string
            if not isinstance(adf_content, dict):
                return str(adf_content)
            
            # Parse ADF structure
            content = adf_content.get("content", [])
            if not content:
                return ""
            
            paragraphs = []
            for node in content:
                if node.get("type") == "paragraph":
                    paragraph_text = self._extract_text_from_paragraph(node)
                    if paragraph_text:
                        paragraphs.append(paragraph_text)
            
            return "\n\n".join(paragraphs)
        
        def _extract_text_from_paragraph(self, paragraph_node: dict) -> str:
            """Extracción de texto de párrafo ADF (copiada de issues.py)"""
            content = paragraph_node.get("content", [])
            if not content:
                return ""
            
            text_parts = []
            for node in content:
                if node.get("type") == "text":
                    text_parts.append(node.get("text", ""))
                elif node.get("type") == "hardBreak":
                    text_parts.append("\n")
            
            return "".join(text_parts)
    
    manager = MockIssuesManager()
    
    # Casos de prueba
    test_cases = [
        "Texto simple de una línea",
        "Párrafo uno\n\nPárrafo dos",
        "Línea uno\nLínea dos en el mismo párrafo\n\nNuevo párrafo",
        "",
        "Solo\n\n\n\nEspacios entre párrafos"
    ]
    
    print("=== Test de Conversión ADF ===")
    print()
    
    for i, original_text in enumerate(test_cases, 1):
        print(f"Test {i}: {repr(original_text)}")
        
        # Convertir a ADF
        adf = manager._text_to_adf(original_text)
        print(f"ADF: {json.dumps(adf, indent=2, ensure_ascii=False)}")
        
        # Convertir de vuelta a texto
        converted_text = manager._adf_to_text(adf)
        print(f"Convertido: {repr(converted_text)}")
        
        # Verificar que el round-trip funciona
        if original_text.strip() == converted_text.strip():
            print("✅ Round-trip exitoso")
        else:
            print("❌ Round-trip falló")
            print(f"   Original: {repr(original_text.strip())}")
            print(f"   Convertido: {repr(converted_text.strip())}")
        
        print("-" * 50)
    
    print("\n🎉 Test completado!")

if __name__ == "__main__":
    test_adf_conversion()
