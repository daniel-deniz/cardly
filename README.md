# Draft – av-cards

Draft es un agente de IA orientado a equipos de producto y tecnología.
Su objetivo es transformar inputs poco estructurados en tarjetas claras y accionables
(Funcionalidad o Bug) siguiendo reglas estrictas.

## Qué hace hoy
- Detecta intención del usuario (tarjeta vs small talk)
- Genera tarjetas con formato estándar:
  - Título
  - Descripción
  - Requisitos
  - Validación
- Aplica reglas para evitar invención y mantener claridad

## Qué no hace aún
- No envía emails
- No gestiona versiones
- No tiene interfaz gráfica
- No persiste datos

## Estructura del proyecto
- `src/llm.py`: conexión con el modelo de IA
- `src/state.py`: estado de la conversación
- `src/nodes.py`: lógica de negocio de Draft (reglas y generación)
- `src/graph.py`: flujo del agente (orquestación)

## Requisitos
- Python 3.10+ (recomendado)
- Dependencias en `requirements.txt`

## Cómo ejecutarlo en local (básico)
1. Clonar el repositorio
2. Crear y activar un entorno virtual
3. Instalar dependencias
4. Ejecutar el script principal (según configuración local)

> Nota: este repositorio está en fase inicial y el modo de ejecución puede cambiar.

## Roadmap inmediato
- Mejorar README con ejemplo de input/output
- Añadir pruebas básicas de validación
- Diseñar flujo de email de release por versión (2.3)
