# 📋 Campos y Valores para User Stories (HU) - CONFIGURACIÓN LOCAL

> **📍 SCOPE LOCAL:** Esta configuración es específica para este workspace y sobrescribe la configuración global.


Esta guía contiene todos los campos disponibles para crear User Stories en Azure DevOps y sus valores permitidos.

## 🚨 IMPORTANTE - Proceso Correcto en Dos Pasos

### 🔥 PASO 1: CREAR WORK ITEM
**Para crear User Stories usar:** `"workItemType": "User Story"`
**Proyecto:** `"project": "Nequi"`
**CRÍTICO:** NO incluir `System.Parent` en la creación inicial (campo read-only)

❌ **NO usar:** "UserStory", "Historia de Usuario" o cualquier otro tipo
✅ **USAR:** "User Story" (exactamente como está escrito, con espacio)

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
- **Descripción:** Epic padre que contiene esta User Story
- **Parent por defecto:** 6825854 ("ESCALAR: Asegurar el soporte de la plataforma Delfos")
- **Parent personalizado:** Si el usuario proporciona otro Epic ID, usar ese
- **Método de asignación:** `mcp_azuredevops_wit_work_items_link` con type: "parent"

### System.IterationPath
- **Tipo:** String
- **Obligatorio:** SÍ - CRÍTICO
- **Descripción:** Sprint/Iteración donde se trabajará la User Story
- **Formato:** "Nequi\\{Año}\\{Quarter}\\{Sprint}"
- **Consulta dinámica:** Usar MCP `mcp_azuredevops_work_list_team_iterations`
- **Equipo:** "Plataforma Delfos"
- **Criterio:** Buscar iteración con `timeFrame: 1` (current) o `timeFrame: 2` (future)
- **Ejemplo:** `{"name": "System.IterationPath", "value": "Nequi\\2025\\Q4\\Sprint 2025 - 22"}`

### System.Title
- **Tipo:** String
- **Obligatorio:** Sí
- **Formato:** "🤖 {Título descriptivo de la funcionalidad}"
- **Ejemplo:** "🤖 Consultar historial de transacciones del usuario"

### Microsoft.VSTS.Common.AcceptanceCriteria
- **Tipo:** HTML
- **Obligatorio:** Sí
- **Formato:** Lista HTML con criterios específicos y medibles
- **Template:**
```html
<ul>
<li>Criterio funcional específico y medible</li>
<li>Criterio de rendimiento o usabilidad</li>
<li>Criterio de validación o error handling</li>
</ul>
```

### Microsoft.VSTS.Common.ValueArea
- **Tipo:** String
- **Obligatorio:** Sí
- **Valores permitidos:**
  - "Business" (por defecto) - entrega valor al usuario o sistema
  - "Business" - entrega valor al usuario o sistema
  - "Architectural" - trabajo de soporte para otras historias o componentes

### Custom.Country
- **Tipo:** String
- **Obligatorio:** Sí
- **Valores permitidos:**
  - "Colombia" (por defecto)
  - "Colombia"
  - "Core"
  - "Guatemala"
  - "Panama"

### Custom.89c0567a-122f-408f-a324-fa6e349e3ac1 (Clasificación)
- **Tipo:** String
- **Obligatorio:** Sí
- **Valores permitidos:**
  - "Deuda Técnica"
  - "Legal"
  - "Operación"
  - "Soporte"
  - "Transformación"

## 🔧 Campos Opcionales Comunes

### System.Description
- **Tipo:** HTML
- **Obligatorio:** No (pero recomendado)
- **Formato:** Estructura LAKiller con mención HTML
- **Template:**
```html
<div><b>Yo</b> <a href="#" data-vss-mention="version:2.0,7c4e1873-3e5c-6322-b999-ca2059fc90a0">@Andres Felipe Montaña Rojas</a> como {rol}<br></div>
<div><b>Requiero</b> {funcionalidad específica}</div>
<div><b>Con la finalidad de</b> {beneficio/valor que obtiene}</div>
```

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
- **Valor por defecto:** 5

### System.Tags
- **Tipo:** String (separado por punto y coma)
- **Tags base:** "EPA; 2025-Q4; Kiro"

### System.AreaPath
- **Tipo:** String
- **Valor por defecto:** "Nequi\\Plataforma Delfos"

## 📝 Campos de Definition of Ready (DoR) - Obligatorios con valor por defecto "0"

### Custom.Lasdependenciasinternasfueronresueltas
- **Nombre:** "Las dependencias internas fueron resueltas"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.Lasdependenciasexternasfueronresueltas
- **Nombre:** "Las dependencias externas fueron resueltas"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.LaHuestatanclaraqueelequipopuededefinirelCOMO
- **Nombre:** "La Hu esta tan clara que el equipo puede definir el COMO"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.Cuentaconcriteriosdeaceptacion
- **Nombre:** "Cuenta con criterios de aceptacion"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.Cuentaconladocumentacionnecesaria
- **Nombre:** "Cuenta con la documentacion necesaria"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.Notienesentidodividirmas
- **Nombre:** "No tiene sentido dividir mas"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.usuariosClaveImpactados
- **Nombre:** "usuariosClaveImpactados"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

## 📝 Campos de Definition of Done (DoD) - Obligatorios con valor por defecto "0"

### Custom.f52fba57-f21a-4e84-b97f-d71a24d09d04
- **Nombre:** "Realizó inspección por pares"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.eef3afd0-1acc-4869-85db-7926bb9f9fba
- **Nombre:** "El producto completo está disponible en el ambiente de desarrollo y listo para ser desplegado en QA"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.aa36d140-c06f-49cb-9513-851c1b488eb1
- **Nombre:** "Cumple con los estándares de nombramiento y documentación de código"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.Seejecutaronlaspruebasnecesariasintegrales
- **Nombre:** "Se ejecutaron las pruebas necesarias integrales"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.66136588-ed15-422b-a710-e309ec3bff6d
- **Nombre:** "Se cuenta con una cobertura mínima del 70 en las pruebas unitarias del desarrollo de la HU"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.51223344-9a8b-4a71-a8b4-b211b42c1d55
- **Nombre:** "El pipeline se ejecutó exitosamente"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.Seactualizaronlashistoriasdeusuarioenlaherramientacorrespondiente
- **Nombre:** "Se actualizaron las historias de usuario en la herramienta correspondiente"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.Lahistoriadeusuarioseencuentraversionadaysepuederealizartrazabilidad
- **Nombre:** "La historia de usuario se encuentra versionada y se puede realizar trazabilidad"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.c627d551-308e-4cfb-8175-a36a4b667a79
- **Nombre:** "Se generó o actualizó la documentación asociada a la Historia de usuario"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.818d0d1b-df75-46a3-926c-7b99681e5ef9
- **Nombre:** "Lo que implementé cubre cada uno de los criterios de aceptación de la HU"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.b543e17b-55a4-4650-a30f-e1f843e32447
- **Nombre:** "La generación y estructura de logs generada para la Historia de usuario es correcta"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

### Custom.LaimplementacionfueaceptadaporelPO
- **Nombre:** "La implementacion fue aceptada por el PO"
- **Tipo:** Integer (0/1)
- **Obligatorio:** Sí
- **Valor por defecto:** "0"

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
  workItemType: "User Story",
  project: "Nequi",
  fields: [
    // TODOS los campos obligatorios EXCEPTO System.Parent
    {"name": "System.IterationPath", "value": sprint.path},
    {"name": "System.Title", "value": "🤖 Título de la User Story"},
    // ... otros campos incluyendo DoR/DoD con valor "0"
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
3. **Campos obligatorios con "0":** Muchos campos DoR/DoD son obligatorios pero tienen valor por defecto "0"
4. **Mención HTML:** Si se usa descripción, usar el formato exacto con el ID de Andres Felipe Montaña Rojas
5. **Value Area:** "Business" es el valor por defecto y más común para User Stories
6. **Clasificación:** Campo obligatorio, usado como fallback para Epic parent automático
7. **Country:** Campo obligatorio, valores: Colombia (defecto), Core, Guatemala, Panama
8. **Tags:** Separar con "; " (punto y coma + espacio)
9. **Tags base obligatorios:** Siempre incluir "EPA; 2025-Q4; Kiro"
10. **Story Points:** Para User Stories típicamente usar valores más altos que Habilitadores (5-13)

## 📊 Diferencias clave con Habilitadores

- **User Stories** tienen muchos más campos DoR/DoD obligatorios
- **User Stories** tienen ValueArea (Business/Architectural)
- **User Stories** no tienen Categoria_HA ni Área solicitante
- **User Stories** tienen campos específicos de testing y repositorios
- **User Stories** se enfocan en funcionalidad del usuario final
