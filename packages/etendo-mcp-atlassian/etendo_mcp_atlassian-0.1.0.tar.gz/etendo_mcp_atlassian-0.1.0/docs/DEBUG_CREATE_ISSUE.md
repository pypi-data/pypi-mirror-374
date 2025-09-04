# Debug: Error al Crear Issues - Análisis Detallado

## Estado Actual
Error persiste: `ToolException("Error calling tool 'create_issue'")`

## Logging Agregado

### ✅ **Server Level (jira.py)**
- Logging de parámetros de entrada
- Captura de excepciones completas 
- Información detallada de argumentos

### ✅ **Issue Creation Level (issues.py)**
- Logging del payload JSON enviado a la API
- Captura de respuestas HTTP
- Debug del procesamiento de campos adicionales
- Logging de errores en field map generation

## Qué Buscar en los Logs

### 1. **Logs del MCP Server**
Busca líneas como:
```
Creating issue: project=XXX, summary=XXX, type=XXX
About to create issue with payload: {...}
Issue creation response received: <type>
```

### 2. **Posibles Errores**
- **Field Map Error**: "Could not generate field map"
- **API Response Error**: "Unexpected return value type"
- **HTTP Error**: Error en la llamada POST a `/rest/api/3/issue`
- **JSON Error**: Problema serialización del payload

### 3. **Payload Validation**
El payload mínimo debería verse así:
```json
{
  "fields": {
    "summary": "Test issue",
    "project": {"key": "PROJECT_KEY"},
    "issuetype": {"name": "Task"}
  }
}
```

## Pasos para Debugging

### Paso 1: Verificar el Payload
Ejecuta el script de test:
```bash
python3 test_issue_creation.py
```

### Paso 2: Revisar Logs del MCP
Cuando ejecutes create_issue, deberías ver:
1. ✅ "Creating issue: project=..." 
2. ✅ "About to create issue with payload: ..."
3. ❌ **Aquí es donde probablemente falla**

### Paso 3: Identificar el Error Específico
Los logs detallados mostrarán exactamente:
- Qué parámetros llegan al método
- Qué payload se construye
- Qué respuesta (si alguna) viene de la API
- En qué punto exacto falla

## Problemas Potenciales Identificados

### 1. **Field Map Generation**
El método `_generate_field_map()` podría estar fallando, causando que `_process_additional_fields()` falle.

### 2. **API v3 Response Format**
La respuesta de la API v3 podría tener un formato diferente al esperado.

### 3. **Client HTTP Issues**
Problemas de autenticación o conectividad con Jira Cloud.

### 4. **Model Serialization**
El método `to_simplified_dict()` podría estar fallando en el modelo JiraIssue.

## Siguiente Paso
Con el logging detallado agregado, ejecuta la creación de issue nuevamente y comparte los logs específicos. Esto nos permitirá identificar exactamente dónde y por qué está fallando.

Los logs mostrarán:
- ✅ Si el problema está en la construcción del payload
- ✅ Si el problema está en la llamada HTTP a Jira
- ✅ Si el problema está en el procesamiento de la respuesta
- ✅ Si el problema está en la serialización del resultado final
