#!/usr/bin/env python3
"""
Script para probar la función de conversión a ADF
"""

import json
import sys
sys.path.insert(0, 'src')

def test_adf_conversion():
    """Probar la conversión a Atlassian Document Format"""
    
    # Importar la clase que contiene el método
    from mcp_atlassian.jira.issues import JiraIssuesManager
    from mcp_atlassian.jira.config import JiraConfig
    from unittest.mock import Mock
    
    # Crear una instancia mock para probar el método
    config = JiraConfig(
        server_url="https://test.atlassian.net",
        username="test",
        password="test",
        auth_method="basic"
    )
    
    # Mock del cliente jira
    mock_jira = Mock()
    
    # Crear instancia para probar
    issues_manager = JiraIssuesManager(mock_jira)
    
    # Casos de prueba
    test_cases = [
        {
            "name": "Texto simple",
            "input": "Esta es una descripción simple para el issue.",
            "expected_type": "doc"
        },
        {
            "name": "Texto con múltiples párrafos",
            "input": "Primer párrafo.\n\nSegundo párrafo con más detalles.\n\nTercer párrafo final.",
            "expected_type": "doc"
        },
        {
            "name": "Texto con saltos de línea",
            "input": "Línea 1\nLínea 2\nLínea 3",
            "expected_type": "doc"
        },
        {
            "name": "Texto vacío",
            "input": "",
            "expected_type": "doc"
        },
        {
            "name": "Solo espacios",
            "input": "   \n\n   ",
            "expected_type": "doc"
        }
    ]
    
    print("=== Prueba de Conversión a ADF ===\n")
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Input: {repr(test_case['input'])}")
        
        try:
            result = issues_manager._text_to_adf(test_case["input"])
            
            print("ADF Output:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Validaciones básicas
            if result.get("type") != test_case["expected_type"]:
                print(f"❌ ERROR: Expected type '{test_case['expected_type']}', got '{result.get('type')}'")
                all_passed = False
            elif result.get("version") != 1:
                print(f"❌ ERROR: Expected version 1, got {result.get('version')}")
                all_passed = False
            elif "content" not in result:
                print("❌ ERROR: Missing 'content' field")
                all_passed = False
            else:
                print("✅ Estructura ADF válida")
                
        except Exception as e:
            print(f"❌ ERROR: Exception occurred: {e}")
            all_passed = False
            
        print("-" * 50)
    
    if all_passed:
        print("🎉 ¡Todos los tests pasaron!")
    else:
        print("❌ Algunos tests fallaron")
    
    return all_passed

if __name__ == "__main__":
    test_adf_conversion()
