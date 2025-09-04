#!/usr/bin/env python3
"""
Script para debuggear el problema de JQL search que no devuelve resultados.
"""

import logging
import json
from src.mcp_atlassian.jira.client import JiraClient
from src.mcp_atlassian.jira.config import JiraConfig

# Configurar logging para ver los detalles
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_jql_variants():
    """Probar diferentes variantes de JQL para identificar el problema."""
    
    # Configurar cliente (usando las variables de entorno)
    config = JiraConfig.from_env()
    client = JiraClient(config)
    
    # JQL original que no funciona
    original_jql = "assignee in (accountId('5d94e6fe6110c10ddb7a0435')) AND statusCategory != Done ORDER BY updated DESC"
    
    # Variantes de JQL para probar
    jql_variants = [
        # JQL directo con accountId
        "assignee = '5d94e6fe6110c10ddb7a0435' AND statusCategory != Done ORDER BY updated DESC",
        
        # JQL más simple
        "assignee = '5d94e6fe6110c10ddb7a0435'",
        
        # JQL usando currentUser()
        "assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC",
        
        # JQL original
        original_jql,
        
        # Solo verificar que el usuario existe
        "assignee = '5d94e6fe6110c10ddb7a0435' AND updated >= '-30d'",
    ]
    
    for i, jql in enumerate(jql_variants, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {jql}")
        print(f"{'='*60}")
        
        try:
            # Hacer la búsqueda
            search_result = client.search.search_issues(
                jql=jql,
                fields="summary,status,priority,project,issuetype,updated",
                limit=10
            )
            
            print(f"Total: {search_result.total}")
            print(f"Start At: {search_result.start_at}")
            print(f"Max Results: {search_result.max_results}")
            print(f"Issues Count: {len(search_result.issues)}")
            
            if search_result.issues:
                print("Issues found:")
                for issue in search_result.issues[:3]:  # Mostrar solo los primeros 3
                    print(f"  - {issue.key}: {issue.fields.summary}")
            else:
                print("No issues found")
                
            # Probar también una llamada directa a la API
            print(f"\n--- Direct API call ---")
            params = {
                "jql": jql,
                "startAt": 0,
                "maxResults": 10,
                "fields": "summary,status,priority,project,issuetype,updated"
            }
            direct_response = client.jira.get("/rest/api/3/search", params=params)
            print(f"Direct API response keys: {list(direct_response.keys()) if isinstance(direct_response, dict) else 'NOT DICT'}")
            if isinstance(direct_response, dict):
                print(f"Direct API total: {direct_response.get('total')}")
                print(f"Direct API issues count: {len(direct_response.get('issues', []))}")
                
        except Exception as e:
            print(f"ERROR: {e}")
            logger.exception("Error during JQL test")

if __name__ == "__main__":
    test_jql_variants()
