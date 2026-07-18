# Cardly

Cardly es un asistente de IA para equipos de producto y tecnología: convierte una
petición en lenguaje natural en una tarjeta de **funcionalidad** o **bug** lista para
copiar/pegar en un kanban, con un formato consistente para todo el equipo.

Sucesor de av-cards ("Draft"), reconstruido como app web con cuentas por usuario e
historial de conversaciones guardado. La parte de generación de emails de release de
la versión anterior no se ha portado.

## Stack

- [Next.js](https://nextjs.org) (App Router) + Tailwind CSS, desplegado en Vercel.
- [Vercel AI SDK](https://ai-sdk.dev) (`useChat`, `streamText`) para el chat con streaming.
- [Supabase](https://supabase.com): Auth (alta de usuarios manual, sin registro público)
  + Postgres para conversaciones e historial, con RLS por usuario.
- OpenAI (`gpt-4o-mini`) para la generación de tarjetas.

## Desarrollo local

1. Copia `.env.example` a `.env.local` y rellena:
   - `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` de tu proyecto Supabase.
   - `OPENAI_API_KEY`.
2. Aplica `supabase/schema.sql` en el SQL Editor de Supabase.
3. Da de alta usuarios de prueba desde Authentication → Users (no hay pantalla de registro).
4. `npm install && npm run dev`

## Estructura

- `src/app/(app)` — layout con sidebar de conversaciones + páginas de chat.
- `src/app/login` — login por email/contraseña.
- `src/app/api/chat` — endpoint que genera la tarjeta y persiste los mensajes.
- `src/lib/prompt.ts` — reglas de negocio del asistente.
- `supabase/schema.sql` — tablas `conversations` / `messages` y políticas RLS.
