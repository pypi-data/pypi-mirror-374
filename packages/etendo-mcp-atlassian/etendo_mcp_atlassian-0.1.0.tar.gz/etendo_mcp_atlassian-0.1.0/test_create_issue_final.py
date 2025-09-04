#!/usr/bin/env python3
"""
Script para probar la creación de issues después de las correcciones de sintaxis
"""

import sys
import os
sys.path.insert(0, 'src')

# Configurar logging básico
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_create_issue():
    """Probar la creación de un issue simple"""
    
    try:
        from mcp_atlassian.jira.client import JiraClient
        from mcp_atlassian.jira.config import JiraConfig
        
        # Configuración de prueba (estos valores necesitan ser reales)
        config = JiraConfig(
            server_url="https://etendo.atlassian.net",
            username="roman@etendo.software", 
            password=os.getenv("JIRA_PASSWORD", "dummy"),  # Usar variable de entorno
            auth_method="basic"
        )
        
        client = JiraClient(config)
        
        print("🔄 Intentando crear un issue de prueba...")
        
        # Probar creación de issue
        issue = client.create_issue(
            project_key="ETENDO PRODUCT",
            summary="Issue de prueba después de corrección de sintaxis",
            issue_type="Task",
            description="Este es un issue de prueba para verificar que la corrección de sintaxis funciona correctamente.",
            assignee="roman@etendo.software"
        )
        
        print(f"✅ Issue creado exitosamente: {issue.key}")
        print(f"   URL: {issue.url}")
        print(f"   Estado: {issue.status}")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        print(f"   Tipo de error: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Test de Creación de Issues ===")
    print("Nota: Este test requiere credenciales válidas de Jira")
    
    if not os.getenv("JIRA_PASSWORD"):
        print("⚠️  Variable de entorno JIRA_PASSWORD no encontrada")
        print("   Para ejecutar el test completo, usar:")
        print("   export JIRA_PASSWORD='tu_password' && python3 test_create_issue_final.py")
        print("")
        print("🔄 Ejecutando test de sintaxis solamente...")
        
        try:
            sys.path.insert(0, 'src')
            from mcp_atlassian.jira.issues import JiraIssuesManager
            from mcp_atlassian.jira.client import JiraClient
            print("✅ Importación exitosa - sin errores de sintaxis")
        except Exception as e:
            print(f"❌ Error de importación: {e}")
    else:
        success = test_create_issue()
        if success:
            print("🎉 ¡Todas las pruebas exitosas!")
        else:
            print("❌ Algunas pruebas fallaron")
