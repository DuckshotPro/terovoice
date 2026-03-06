# 📋 Campos y Valores para Habilitadores (HA) - CONFIGURACIÓN LOCAL

> **📍 SCOPE LOCAL:** Esta configuración es específica para este workspace y sobrescribe la configuración global.


Esta guía contiene todos los campos disponibles para crear Habilitadores en Azure DevOps y sus valores permitidos.

## 🚨 IMPORTANTE - Proceso Correcto en Dos Pasos

### 🔥 PASO 1: CREAR WORK ITEM
**Para crear Habilitadores usar:** `"workItemType": "Habilitador"`
**Proyecto:** `"project": "Nequi"`
**CRÍTICO:** NO incluir `System.Parent` en la creación inicial (campo read-only)

❌ **NO usar:** "Enabler" o cualquier otro tipo
✅ **USAR:** "Habilitador" (exactamente como está escrito)

### 🔥 PASO 2: ASIGNAR PARENT EPIC
**Método:** `mcp_azuredevops_wit_work_items_link`
**Parent por defecto:** 6825854 ("ESCALAR: Asegurar el soporte de la plataforma Delfos")
**Parent personalizado:** Si el usuario proporciona otro Epic ID, usar ese

## 🔧 Campos Obligatorios

### 🚨 CAMPOS CRÍTICOS - NUNCA OMITIR:

### System.Parent
- **Tipo:** Integer (ID del Epic) - CAMPO READ-ONLY
- **Obligatorio:** SÍ - CRÍTICO
- **PROCESO CORRECTO:** NO incluir en creación inicial, asignar después con linking
- **Descripción:** Epic padre que contiene este habilitador
- **Parent por defecto:** 6825854 ("ESCALAR: Asegurar el soporte de la plataforma Delfos")
- **Parent personalizado:** Si el usuario proporciona otro Epic ID, usar ese
- **Método de asignación:** `mcp_azuredevops_wit_work_items_link` con type: "parent"

### System.IterationPath
- **Tipo:** String
- **Obligatorio:** SÍ - CRÍTICO
- **Descripción:** Sprint/Iteración donde se trabajará el habilitador
- **Formato:** "Nequi\\{Año}\\{Quarter}\\{Sprint}"
- **Consulta dinámica:** Usar MCP `mcp_azuredevops_work_list_team_iterations`
- **Equipo:** "Plataforma Delfos"
- **Criterio:** Buscar iteración con `timeFrame: 1` (current) o `timeFrame: 2` (future)
- **Ejemplo:** `{"name": "System.IterationPath", "value": "Nequi\\2025\\Q4\\Sprint 2025 - 22"}`

### System.Title
- **Tipo:** String
- **Obligatorio:** Sí
- **Formato:** "🤖 [HA-{Categoría}] {Título descriptivo}"
- **Ejemplo:** "🤖 [HA-Desarrollo Componentes] Implementar API de autenticación"

### System.Description
- **Tipo:** HTML
- **Obligatorio:** Sí
- **Formato:** Estructura LAKiller con mención HTML
- **Template:**
```html
<div><b>Yo</b> <a href="#" data-vss-mention="version:2.0,7c4e1873-3e5c-6322-b999-ca2059fc90a0">@Andres Felipe Montaña Rojas</a> como Líder Técnico<br></div>
<div><b>Requiero</b> {requerimiento detallado}</div>
<div><b>Con la finalidad de</b> {propósito y beneficio}</div>
```

### Microsoft.VSTS.Common.AcceptanceCriteria
- **Tipo:** HTML
- **Obligatorio:** Sí
- **Formato:** Lista HTML con criterios específicos
- **Template:**
```html
<ul>
<li>Criterio 1 específico y medible</li>
<li>Criterio 2 específico y medible</li>
<li>Criterio 3 específico y medible</li>
</ul>
```

### Custom.Categoria_HA
- **Tipo:** String
- **Obligatorio:** Sí
- **Valores permitidos:**
  - "Desarrollo Componentes"
  - "Infraestructura"
  - "Seguridad"
  - "Datos"
  - "Investigación"

### Custom.89c0567a-122f-408f-a324-fa6e349e3ac1 (Clasificación)
- **Tipo:** String
- **Obligatorio:** Sí
- **Valores permitidos:**
  - "Deuda Técnica"
  - "Legal"
  - "Operación"
  - "Soporte"
  - "Transformación"

### Custom.9587aecc-cd66-47b4-a44a-9965a2b8e4a9 (Área solicitante)
- **Tipo:** String
- **Obligatorio:** Sí
- **Formato:** "[Nequi]\\{NombreDelEquipo}"
- **Valor por defecto:** "[Nequi]\\Plataforma Delfos"

## 🔧 Campos Opcionales Comunes

### System.AssignedTo
- **Tipo:** String (email)
- **Valor por defecto:** "afmontan@nequi.com"

### Microsoft.VSTS.Common.Priority
- **Tipo:** Integer
- **Valores:** 1 (Alta), 2 (Media), 3 (Baja), 4 (Muy Baja)
- **Valor por defecto:** 2

### Microsoft.VSTS.Scheduling.StoryPoints
- **Tipo:** Integer
- **Rango:** 1-20 (típicamente)
- **Valor por defecto:** 3

### System.Tags
- **Tipo:** String (separado por punto y coma)
- **Tags base:** "EPA; 2025-Q4; Kiro"

### Custom.Country
- **Tipo:** String
- **Valores permitidos:**
  - "Colombia" (por defecto)
  - "Colombia"
  - "Core"
  - "Guatemala"
  - "Panama"

### System.AreaPath
- **Tipo:** String
- **Valor por defecto:** "Nequi\\Plataforma Delfos"

## 🔥 PROCESO OBLIGATORIO EN DOS PASOS

### Paso 1: Crear Work Item SIN System.Parent
```javascript
// 1. Consultar sprint actual
const sprint = await mcp_azuredevops_work_list_team_iterations({
  project: "Nequi",
  team: "Plataforma Delfos"
});

// 2. Crear work item SIN System.Parent
const workItem = await mcp_azuredevops_wit_create_work_item({
  workItemType: "Habilitador",
  project: "Nequi",
  fields: [
    // TODOS los campos obligatorios EXCEPTO System.Parent
    {"name": "System.IterationPath", "value": sprint.path},
    {"name": "System.Title", "value": "🤖 [HA-Desarrollo Componentes] Título"},
    // ... otros campos
  ]
});
```

### Paso 2: Asignar Parent Epic
```javascript
// 3. Asignar parent usando linking
const parentId = userProvidedId || "6825854"; // Por defecto: Epic Plataforma Delfos
await mcp_azuredevops_wit_work_items_link({
  project: "Nequi",
  updates: [{
    type: "parent",
    linkToId: parseInt(parentId),
    id: workItem.id
  }]
});
```

## 🚨 Notas Importantes

1. **Proceso en dos pasos:** NUNCA incluir System.Parent en la creación inicial
2. **Parent por defecto:** 6825854 (Epic "ESCALAR: Asegurar el soporte de la plataforma Delfos")
3. **Mención HTML:** Siempre usar el formato exacto con el ID de Andres Felipe Montaña Rojas
4. **Área solicitante:** Campo obligatorio, debe usar exactamente uno de los valores de la lista
5. **Formato área:** Siempre usar "[Nequi]\\{NombreEquipo}" - respetar mayúsculas y espacios
6. **Categoría HA:** Verificar valores permitidos en el sistema antes de usar
7. **Tags:** Separar con "; " (punto y coma + espacio)
8. **Tags base obligatorios:** Siempre incluir "EPA; 2025-Q4; Kiro"
