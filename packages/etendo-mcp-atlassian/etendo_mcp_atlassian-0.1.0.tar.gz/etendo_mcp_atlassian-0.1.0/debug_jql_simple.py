#!/usr/bin/env python3
"""
Prueba simple para debuggear JQL sin depender de los módulos del proyecto.
"""

import requests
import json
import os
import base64

def test_jql_direct():
    """Prueba directa a la API de Jira sin usar el MCP."""
    
    # Obtener credenciales desde variables de entorno
    jira_url = os.getenv('JIRA_URL')
    jira_email = os.getenv('JIRA_EMAIL')  
    jira_token = os.getenv('JIRA_TOKEN')
    
    if not all([jira_url, jira_email, jira_token]):
        print("ERROR: Falta configurar variables de entorno JIRA_URL, JIRA_EMAIL, JIRA_TOKEN")
        return
    
    # Preparar autenticación
    auth_string = f"{jira_email}:{jira_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Primero, verificar el usuario actual
    print("=== Verificando usuario actual ===")
    try:
        myself_url = f"{jira_url}/rest/api/3/myself"
        myself_response = requests.get(myself_url, headers=headers)
        myself_response.raise_for_status()
        myself_data = myself_response.json()
        
        print(f"Usuario actual: {myself_data.get('displayName')}")
        print(f"Account ID: {myself_data.get('accountId')}")
        print(f"Email: {myself_data.get('emailAddress')}")
        
        account_id = myself_data.get('accountId')
        
    except Exception as e:
        print(f"Error obteniendo usuario actual: {e}")
        return
    
    # Probar diferentes variantes de JQL
    print(f"\n=== Probando búsquedas JQL ===")
    
    jql_tests = [
        # Usar currentUser() en lugar de accountId específico
        "assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC",
        
        # Usar accountId directo sin función
        f"assignee = '{account_id}' AND statusCategory != Done ORDER BY updated DESC",
        
        # JQL simple
        f"assignee = '{account_id}'",
        
        # JQL original con función accountId
        f"assignee in (accountId('{account_id}')) AND statusCategory != Done ORDER BY updated DESC",
        
        # Solo verificar si hay tareas actualizadas recientemente
        f"assignee = '{account_id}' AND updated >= '-7d'",
    ]
    
    for i, jql in enumerate(jql_tests, 1):
        print(f"\n--- Test {i}: {jql[:80]}... ---")
        
        try:
            search_url = f"{jira_url}/rest/api/3/search"
            params = {
                'jql': jql,
                'startAt': 0,
                'maxResults': 10,
                'fields': 'summary,status,priority,project,issuetype,updated'
            }
            
            response = requests.get(search_url, headers=headers, params=params)
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Total: {data.get('total')}")
                print(f"StartAt: {data.get('startAt')}")
                print(f"MaxResults: {data.get('maxResults')}")
                print(f"Issues encontrados: {len(data.get('issues', []))}")
                
                if data.get('issues'):
                    print("Primeras tareas:")
                    for issue in data['issues'][:3]:
                        print(f"  - {issue['key']}: {issue['fields']['summary']}")
                else:
                    print("No se encontraron tareas")
                    
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error en la búsqueda: {e}")

if __name__ == "__main__":
    test_jql_direct()
