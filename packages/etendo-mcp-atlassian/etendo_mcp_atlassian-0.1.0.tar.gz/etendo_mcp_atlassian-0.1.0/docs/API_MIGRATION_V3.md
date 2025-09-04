# Migración a Jira REST API v3

## Resumen

Este documento describe los cambios realizados para migrar el MCP de Atlassian de usar algunos endpoints de API v2 a API v3, y mejorar la compatibilidad con las actualizaciones de GDPR que Atlassian implementó.

## Cambios Realizados

### 1. Issue Link Types - Migrado de v2 a v3

**Archivo**: `src/mcp_atlassian/jira/links.py`

**Cambio**:

```python
# ANTES (API v2)
link_types_response = self.jira.get("rest/api/2/issueLinkType")

# DESPUÉS (API v3)
link_types_response = self.jira.get("rest/api/3/issueLinkType")
```

**Justificación**: El endpoint v3 tiene la misma funcionalidad que v2 pero es la versión recomendada y futura. No hay cambios en el formato de respuesta.

### 2. User Permission Search - Migrado de v2 a v3

**Archivo**: `src/mcp_atlassian/jira/users.py`

**Cambio**:

```python
# ANTES (API v2)
url = f"{self.config.url}/rest/api/2/user/permission/search"

# DESPUÉS (API v3) 
url = f"{self.config.url}/rest/api/3/user/permission/search"
```

**Justificación**: El endpoint v3 tiene la misma funcionalidad y formato que v2, pero es la versión estándar actual.

## Estado del Manejo de Usuarios GDPR

El código ya está **correctamente implementado** para manejar las actualizaciones de GDPR:

### ✅ Uso de accountId
- El código ya prioriza `accountId` para Jira Cloud
- Tiene fallbacks apropiados a `name` y `key` para Server/DC
- Los métodos de búsqueda de usuarios usan `query` en lugar de `username` deprecated

### ✅ Manejo Defensivo
- `_get_account_id()` acepta objetos dict de usuario y extrae el identificador apropiado
- Soporte para múltiples formatos de identificador (accountId, username, email, etc.)
- Lógica robusta para determinar parámetros de API según el tipo de instancia

### ✅ Búsqueda de Usuarios
- Usa `user_find_by_user_string()` con parámetro `query` en Cloud
- Fallback a búsqueda por permisos cuando la búsqueda directa falla
- Manejo apropiado de respuestas vacías y errores

## Endpoints Verificados como v3

Los siguientes endpoints ya estaban usando API v3:
- `/rest/api/3/version` (client.py)
- `/rest/api/3/issue/{issueKey}/remotelink` (links.py)

## Compatibilidad

### Jira Cloud
- ✅ Completamente compatible con API v3
- ✅ Usa accountId como identificador principal
- ✅ Maneja campos de usuario según configuración de privacidad

### Jira Server/Data Center
- ✅ Compatible con versiones que soporten API v3
- ✅ Fallback apropiado a `username`/`key` cuando `accountId` no esté disponible
- ⚠️ Algunas instancias muy antiguas podrían no tener algunos endpoints v3

## Recomendaciones Futuras

1. **Monitoreo**: Revisar logs para asegurar que no hay warnings sobre endpoints deprecated
2. **Testing**: Ejecutar tests contra instancias Cloud y Server para validar compatibilidad
3. **Actualizaciones**: Mantenerse al día con los changelogs de Atlassian para futuras migraciones

## Documentación de Referencia

- [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [GDPR Migration Guide](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-api-migration-guide/)
- [Issue Link Types API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-link-types/)
- [User Search API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/)
