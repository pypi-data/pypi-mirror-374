#!/usr/bin/env python3
"""
Script para probar la creación de issues con logging detallado.
"""

import logging
import json

# Configurar logging para ver todos los detalles
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_issue_creation():
    """Test simple de creación de issue."""
    print("=== Testing Basic Issue Creation ===")
    
    # Payload mínimo para crear una issue
    basic_payload = {
        "fields": {
            "summary": "Test issue from script",
            "project": {"key": "ETENDO PRODUCT"},  # Ajusta según tu proyecto
            "issuetype": {"name": "Task"}
        }
    }
    
    print(f"Basic payload: {json.dumps(basic_payload, indent=2)}")
    
    # Si tienes configurado el cliente Jira, puedes probarlo aquí
    # Por ahora solo mostramos el payload que se enviaría
    print("This is the basic payload that would be sent to Jira API v3")
    print("Endpoint: POST /rest/api/3/issue")
    
    # Verificar que el JSON es válido
    try:
        json_str = json.dumps(basic_payload)
        parsed = json.loads(json_str)
        print("✅ JSON payload is valid")
    except Exception as e:
        print(f"❌ JSON payload error: {e}")

if __name__ == "__main__":
    test_basic_issue_creation()
