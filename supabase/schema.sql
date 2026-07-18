-- Cardly: esquema de datos
-- Cuentas de usuario viven en auth.users (Supabase Auth), alta manual desde el dashboard.

create table conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'Nueva conversación',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz not null default now()
);

create index messages_conversation_id_idx on messages(conversation_id, created_at);
create index conversations_user_id_idx on conversations(user_id, updated_at desc);

alter table conversations enable row level security;
alter table messages enable row level security;

create policy "own_conversations" on conversations
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "own_messages" on messages
  for all
  using (
    exists (
      select 1 from conversations
      where conversations.id = messages.conversation_id
        and conversations.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1 from conversations
      where conversations.id = messages.conversation_id
        and conversations.user_id = auth.uid()
    )
  );
