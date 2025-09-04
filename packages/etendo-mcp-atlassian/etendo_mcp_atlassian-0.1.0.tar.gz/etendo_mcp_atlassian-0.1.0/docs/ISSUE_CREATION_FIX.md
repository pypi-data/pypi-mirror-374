# Fix: Error al crear tareas - Migración API v2 a v3

## Problema
Error al crear tareas: `ToolException("Error calling tool 'create_issue'")`

## Causa Identificada
Varios métodos en `issues.py` aún usaban la librería atlassian-python-api que internamente usa endpoints v2 deprecados.

## Métodos Actualizados

### ✅ **Creación de Issues**
- `create_issue()` - Cambiado de `self.jira.create_issue()` a `self.jira.post("/rest/api/3/issue")`
- Agregado logging detallado para debugging

### ✅ **Actualización de Issues**  
- `update_issue()` - Cambiado de `self.jira.update_issue()` a `self.jira.put("/rest/api/3/issue/{key}")`
- Aplicado en múltiples ubicaciones (creación de Epic, actualización general)

### ✅ **Obtención de Issues**
- `get_issue()` calls - Cambiado de `self.jira.get_issue()` a `self.jira.get("/rest/api/3/issue/{key}")`
- Aplicado en métodos de creación, actualización y consulta

### ✅ **Comentarios de Issues**
- `issue_get_comments()` - Cambiado de `self.jira.issue_get_comments()` a `self.jira.get("/rest/api/3/issue/{key}/comment")`

## Cambios Técnicos Específicos

### Creación de Issues (línea ~615)
```python
# ANTES
response = self.jira.create_issue(fields=fields)

# DESPUÉS  
payload = {"fields": fields}
response = self.jira.post("/rest/api/3/issue", json=payload)
```

### Actualización de Issues (líneas ~1074, ~1133)
```python
# ANTES
self.jira.update_issue(issue_key=issue_key, update={"fields": update_fields})

# DESPUÉS
update_payload = {"fields": update_fields}
self.jira.put(f"/rest/api/3/issue/{issue_key}", json=update_payload)
```

### Obtención de Issues (múltiples líneas)
```python
# ANTES
issue_data = self.jira.get_issue(issue_key)

# DESPUÉS
issue_data = self.jira.get(f"/rest/api/3/issue/{issue_key}")
```

### Comentarios (línea ~276)
```python
# ANTES
response = self.jira.issue_get_comments(issue_key)

# DESPUÉS
response = self.jira.get(f"/rest/api/3/issue/{issue_key}/comment")
```

## Logging Mejorado
- Agregado debug de payloads de creación y actualización
- Logging de respuestas de API para mejor troubleshooting
- Manejo de errores más específico con context

## ⚠️ Métodos Pendientes de Actualizar
Estos métodos aún usan la librería pero no son críticos para la creación básica de tareas:

- `set_issue_status_by_transition_id()`
- `delete_issue()`
- `get_issue_transitions()`
- `set_issue_status()`
- `create_issues()` (bulk)

## Testing
Después de estos cambios, la creación de tareas debería funcionar correctamente usando los endpoints v3.

Para probar:
```json
{
  "action": "create_issue",
  "project": "TEST",
  "summary": "Test task",
  "description": "Test description", 
  "issue_type": "Task"
}
```
