# 🎨 UI Web Básica - NOVA Dashboard

**Prioridad**: MEDIA (Post-MVP)
**Esfuerzo estimado**: 1-2 semanas
**Estado**: BACKLOG
**Fecha agregada**: 4 Noviembre 2025

---

## 📌 Objetivo

Crear un dashboard web simple para:
- Ver workflows disponibles
- Ejecutar workflows manualmente
- Ver estado de ejecuciones
- Visualizar Chain of Work
- No requiere autenticación (MVP)

---

## 🎯 User Stories

### 1. Como usuario, quiero ver la lista de workflows
```
Pantalla: /workflows
- Tabla con: ID, Name, Description, Last Execution
- Botón "Execute" por cada workflow
- Botón "View Details" por cada workflow
```

### 2. Como usuario, quiero ejecutar un workflow
```
Pantalla: /workflows/{id}/execute
- Formulario simple:
  * Client Slug (dropdown: idom, otros...)
  * Initial Context (JSON editor opcional)
- Botón "Execute"
- Al ejecutar → Redirige a /executions/{id}
```

### 3. Como usuario, quiero ver el estado de una ejecución
```
Pantalla: /executions/{id}
- Status badge: Success/Failed/Running
- Timeline de ejecución
- Final result (JSON viewer)
- Error message (si falló)
- Botón "View Chain of Work"
```

### 4. Como usuario, quiero ver el Chain of Work
```
Pantalla: /executions/{id}/chain
- Timeline visual de nodos ejecutados
- Por cada nodo:
  * Node ID y tipo
  * Input context
  * Output result
  * Execution time
  * Code executed (collapsible)
  * Status (success/failed)
- Total execution time
```

### 5. Como usuario, quiero ver todas las ejecuciones
```
Pantalla: /executions
- Tabla con: ID, Workflow, Status, Started At, Duration
- Filtros: Status, Workflow, Date range
- Paginación
- Click en row → /executions/{id}
```

---

## 🏗️ Stack Tecnológico

### Frontend
```
Framework: React + Vite
UI Library: shadcn/ui (Tailwind CSS)
State Management: TanStack Query (React Query)
Routing: React Router
Forms: React Hook Form + Zod
JSON Viewer: react-json-view
Code Editor: Monaco Editor (opcional, para ver código)
```

### Backend
```
API: FastAPI (ya existe)
Endpoints ya disponibles:
  - GET /workflows
  - POST /workflows/{id}/execute
  - GET /executions
  - GET /executions/{id}
  - GET /executions/{id}/chain
  - GET /tasks/{task_id}
```

### Deployment
```
Frontend: Vercel o Railway Static
Backend: Railway (ya desplegado)
```

---

## 🎨 Wireframes / Mockups

### Dashboard Home
```
+------------------------------------------+
|  NOVA Dashboard                    [User]|
+------------------------------------------+
|  Workflows (3)  |  Executions (11)      |
+------------------------------------------+
|                                          |
|  Recent Executions                       |
|  +------------------------------------+  |
|  | ✅ Exec #11 | Invoice V3 | 2s ago |  |
|  | ✅ Exec #10 | Invoice V3 | 5s ago |  |
|  | ❌ Exec #6  | Invoice V3 | 2d ago |  |
|  +------------------------------------+  |
|                                          |
|  Workflows                               |
|  +------------------------------------+  |
|  | Invoice Processing V3              |  |
|  | Last run: 2s ago (✅ Success)      |  |
|  | [Execute] [Details]                |  |
|  +------------------------------------+  |
|                                          |
+------------------------------------------+
```

### Execution Detail
```
+------------------------------------------+
|  < Back to Executions                    |
+------------------------------------------+
|  Execution #11                      ✅   |
|  Workflow: Invoice Processing V3         |
|  Started: 31 Oct 22:52                   |
|  Duration: 12.3s                         |
+------------------------------------------+
|                                          |
|  Timeline:                               |
|  ●━━━●━━━●━━━●━━━●  (5 nodes)          |
|  Start → Extract → Validate → ... → End |
|                                          |
|  Final Result:                           |
|  +------------------------------------+  |
|  | {                                  |  |
|  |   "invoice_id": 123,               |  |
|  |   "total_amount": 1200,            |  |
|  |   "status": "approved"             |  |
|  | }                                  |  |
|  +------------------------------------+  |
|                                          |
|  [View Chain of Work]                    |
+------------------------------------------+
```

### Chain of Work
```
+------------------------------------------+
|  < Back to Execution #11                 |
+------------------------------------------+
|  Chain of Work (5 steps)                 |
|  Total time: 12.3s                       |
+------------------------------------------+
|                                          |
|  1. ✅ start (0.001s)                    |
|     Input: {...}                         |
|     Output: {...}                        |
|                                          |
|  2. ✅ read_emails (2.5s)                |
|     Input: {...}                         |
|     Output: {has_emails: true, ...}      |
|     [Show Code]                          |
|                                          |
|  3. ✅ extract_pdf_text (5.2s)           |
|     Input: {pdf_data: ...}               |
|     Output: {ocr_text: "...", ...}       |
|     [Show Code]                          |
|                                          |
|  ... (más nodos)                         |
|                                          |
+------------------------------------------+
```

---

## 📁 Estructura del Proyecto

```
/nova-ui/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── Layout.tsx       # Navbar, Sidebar
│   │   ├── WorkflowCard.tsx
│   │   ├── ExecutionCard.tsx
│   │   ├── ChainOfWork.tsx
│   │   └── StatusBadge.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Workflows.tsx
│   │   ├── WorkflowDetail.tsx
│   │   ├── Executions.tsx
│   │   ├── ExecutionDetail.tsx
│   │   └── ChainOfWork.tsx
│   ├── lib/
│   │   ├── api.ts           # API client (fetch wrapper)
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useWorkflows.ts
│   │   ├── useExecutions.ts
│   │   └── useChainOfWork.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 🚀 Plan de Implementación

### Fase 1: Setup (1 día)
```bash
# Crear proyecto
npm create vite@latest nova-ui -- --template react-ts
cd nova-ui

# Install dependencies
npm install react-router-dom @tanstack/react-query
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card badge table
```

### Fase 2: API Client (1 día)
```typescript
// src/lib/api.ts
export const api = {
  workflows: {
    list: () => fetch('/api/workflows'),
    get: (id) => fetch(`/api/workflows/${id}`),
    execute: (id, data) => fetch(`/api/workflows/${id}/execute`, {...})
  },
  executions: {
    list: () => fetch('/api/executions'),
    get: (id) => fetch(`/api/executions/${id}`),
    getChain: (id) => fetch(`/api/executions/${id}/chain`)
  }
}
```

### Fase 3: Pages (3-4 días)
- Dashboard (1 día)
- Workflows List + Detail (1 día)
- Executions List + Detail (1 día)
- Chain of Work (1 día)

### Fase 4: Polish (2-3 días)
- Loading states
- Error handling
- Responsive design
- Dark mode (opcional)

---

## 📊 Métricas de Éxito

### MVP (Semana 1)
- ✅ Ver lista de workflows
- ✅ Ejecutar workflow manualmente
- ✅ Ver estado de ejecución
- ✅ Ver Chain of Work básico

### V1.1 (Semana 2)
- ✅ Polling automático de status
- ✅ Filtros y búsqueda
- ✅ JSON viewers mejorados
- ✅ Timeline visual bonito

---

## 🎨 Design System

### Colores
```
Primary: Blue (#3B82F6)
Success: Green (#10B981)
Error: Red (#EF4444)
Warning: Yellow (#F59E0B)
Neutral: Gray (#6B7280)
```

### Tipografía
```
Font: Inter (Google Fonts)
Heading: font-bold
Body: font-normal
Code: font-mono
```

---

## 🔗 Referencias

- **shadcn/ui**: https://ui.shadcn.com/
- **TanStack Query**: https://tanstack.com/query/latest
- **React Router**: https://reactrouter.com/
- **Vite**: https://vitejs.dev/

---

## 📝 Notas

### ¿Por qué shadcn/ui?
- No es una librería NPM, son componentes copiables
- Tailwind CSS (full control)
- Muy customizable
- Gratis y open source

### ¿Por qué React Query?
- Manejo de estado async perfecto para APIs
- Cache automático
- Polling automático
- Error retry

### ¿Dónde deployar?
- **Vercel**: Gratis, deploy automático con GitHub
- **Railway**: Puede servir static files también
- **Netlify**: Otra opción gratis

### Alternativas consideradas
- **Next.js**: Overkill para MVP (no necesitamos SSR)
- **Vue**: Menos familiaridad
- **Svelte**: Menos ecosystem

---

**Última actualización**: 4 Noviembre 2025
