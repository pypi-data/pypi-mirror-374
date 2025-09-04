#!/usr/bin/env python3
"""
Test de la función de normalización de JQL.
"""

import re

def normalize_jql_for_cloud(jql: str) -> str:
    """
    Normalize JQL to work better with Jira Cloud API v3.
    
    Args:
        jql: Original JQL query
        
    Returns:
        Normalized JQL query
    """
    # Replace accountId('id') with direct accountId assignment
    # accountId('5d94e6fe6110c10ddb7a0435') -> '5d94e6fe6110c10ddb7a0435'
    pattern = r"accountId\('([^']+)'\)"
    normalized = re.sub(pattern, r"'\1'", jql)
    
    # Replace 'assignee in (accountId(...))' with 'assignee = accountId'
    pattern2 = r"assignee\s+in\s+\(([^)]+)\)"
    normalized = re.sub(pattern2, r"assignee = \1", normalized)
    
    return normalized

def test_normalization():
    """Test la normalización de JQL."""
    
    test_cases = [
        # Caso original del usuario
        (
            "assignee in (accountId('5d94e6fe6110c10ddb7a0435')) AND statusCategory != Done ORDER BY updated DESC",
            "assignee = '5d94e6fe6110c10ddb7a0435' AND statusCategory != Done ORDER BY updated DESC"
        ),
        
        # Otros casos
        (
            "assignee in (accountId('123')) AND project = 'TEST'",
            "assignee = '123' AND project = 'TEST'"
        ),
        
        # Caso que no debe cambiar
        (
            "assignee = currentUser() AND statusCategory != Done",
            "assignee = currentUser() AND statusCategory != Done"
        ),
        
        # Caso directo con accountId
        (
            "assignee = '5d94e6fe6110c10ddb7a0435'",
            "assignee = '5d94e6fe6110c10ddb7a0435'"
        ),
    ]
    
    print("=== Test de Normalización de JQL ===")
    for i, (input_jql, expected) in enumerate(test_cases, 1):
        result = normalize_jql_for_cloud(input_jql)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        print(f"\nTest {i}: {status}")
        print(f"Input:    {input_jql}")
        print(f"Expected: {expected}")
        print(f"Result:   {result}")
        
        if result != expected:
            print(f"❌ ERROR: Resultado no coincide con lo esperado")

if __name__ == "__main__":
    test_normalization()
