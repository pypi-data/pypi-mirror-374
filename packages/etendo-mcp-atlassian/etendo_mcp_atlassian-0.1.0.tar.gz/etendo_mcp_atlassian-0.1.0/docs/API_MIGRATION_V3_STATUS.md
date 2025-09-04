# Estado de la Migración de Jira API v2 a v3

## Resumen
Este documento rastrea el progreso de la migración de endpoints de Jira API v2 a v3 en el MCP Atlassian.

## Razón de la Migración
Los logs del usuario mostraron errores 410 Gone en endpoints v2:
```
The requested API has been removed. Please migrate to the /rest/api/3/search/jql API
```

Esto indica que algunos endpoints v2 han sido completamente eliminados y requieren migración urgente.

## Archivos Actualizados

### ✅ COMPLETADOS

#### src/mcp_atlassian/jira/links.py
- ✅ `get("rest/api/3/issueLinkType")` (actualizado de v2)
- ⚠️ `create_issue_link()` y `remove_issue_link()` - métodos de librería aún en uso

#### src/mcp_atlassian/jira/users.py
- ✅ `get("/rest/api/3/myself")` (reemplazó `myself()`)
- ✅ `get("/rest/api/3/user", params=api_kwargs)` (reemplazó `user(**api_kwargs)`)
- ✅ `get("/rest/api/3/user/search")` (reemplazó `user_find_by_user_string()`)
- ✅ URL de permissions actualizada a v3

#### src/mcp_atlassian/jira/search.py
- ✅ `get("/rest/api/3/search", params={jql, startAt, maxResults})` (reemplazó `jql()`)
- ✅ `get("/rest/agile/1.0/board/{board_id}/issue")` (reemplazó `get_issues_for_board()`)
- ✅ `get("/rest/agile/1.0/sprint/{sprint_id}/issue")` (reemplazó `get_sprint_issues()`)
- ⚠️ `enhanced_jql_get_list_of_tickets()` - método de librería aún en uso

#### src/mcp_atlassian/jira/client.py
- ✅ `get("/rest/api/3/myself")` en test de autenticación
- ✅ `post("/rest/api/3/version")` en create_version

#### src/mcp_atlassian/jira/projects.py
- ✅ `get("/rest/api/3/project", params=params)` (reemplazó `projects()`)
- ✅ `get("/rest/api/3/project/{project_key}")` (reemplazó `project()`)
- ✅ `get("/rest/api/3/issue/createmeta")` (reemplazó `issue_createmeta()`)
- ✅ `get("/rest/api/3/project/{project_key}/component")` (reemplazó `get_project_components()`)
- ✅ `get("/rest/api/3/project/{project_key}/version")` (reemplazó `get_project_versions()`)
- ✅ `get("/rest/api/3/project/{project_key}/role")` (reemplazó `get_project_roles()`)
- ✅ JQL search actualizado a v3

#### src/mcp_atlassian/jira/epics.py
- ✅ JQL searches actualizados a `/rest/api/3/search`
- ✅ `get("/rest/api/3/issue/{issue_key}")` (reemplazó `get_issue()` en múltiples ubicaciones)
- ✅ `get("/rest/api/3/field")` (reemplazó `get_all_fields()`)

#### src/mcp_atlassian/jira/attachments.py
- ✅ `get("/rest/api/3/issue/{issue_key}")` (reemplazó `issue()`)

#### src/mcp_atlassian/jira/issues.py
- ✅ `get("/rest/api/3/issue/{issue_key}")` (reemplazó `get_issue()` con parámetros)
- ✅ `post("/rest/api/3/issue")` (reemplazó `create_issue()`)

### ⚠️ PENDIENTES DE REVISIÓN

#### Métodos de librería que pueden usar v2 internamente:
- `create_issue_link()` en links.py
- `remove_issue_link()` en links.py  
- `enhanced_jql_get_list_of_tickets()` en search.py
- `get_project_actors_for_role_project()` en projects.py
- `get_project_permission_scheme()` en projects.py
- `get_project_notification_scheme()` en projects.py
- `get_users_with_browse_permission_to_a_project()` en projects.py
- `update_issue()` en epics.py (múltiples ubicaciones)
- `add_attachment()` en attachments.py
- `issue_get_comments()` en comments.py
- `issue_add_comment()` en comments.py
- `issue_createmeta_fieldtypes()` en fields.py

## Parámetros Actualizados
- `limit` → `maxResults`
- `start` → `startAt`
- Parámetros ahora se pasan como `params` dict en lugar de argumentos de función

## Próximos Pasos
1. Revisar los métodos marcados como ⚠️ PENDIENTES
2. Probar funcionalmente todas las operaciones críticas
3. Validar que los parámetros de respuesta son compatibles
4. Ejecutar tests de integración

## Notas Técnicas
- Los endpoints Agile (board/sprint) usan `/rest/agile/1.0/` que parece ser estable
- Todos los cambios preservan la lógica existente, solo cambian las llamadas HTTP subyacentes
- Se mantiene el manejo de errores y validación de tipos existente
