"use client";

import Link from "next/link";
import { LogOut, Plus } from "lucide-react";
import type { ConversationSummary } from "@/lib/conversations";
import { CardlyAvatar } from "@/components/CardlyAvatar";
import { ConversationItem } from "@/components/ConversationItem";
import { signOut } from "@/app/login/actions";

export function Sidebar({
  conversations,
  userEmail,
}: {
  conversations: ConversationSummary[];
  userEmail: string;
}) {
  return (
    <aside className="flex h-screen w-72 shrink-0 flex-col border-r border-border-subtle bg-surface">
      <div className="flex items-center gap-2 px-4 pb-2 pt-4">
        <CardlyAvatar size={28} />
        <span className="text-sm font-semibold">Cardly</span>
      </div>

      <div className="p-3">
        <Link
          href="/"
          className="flex w-full items-center justify-center gap-2 rounded-full bg-brand-500 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-600"
        >
          <Plus className="size-4" />
          Nueva conversación
        </Link>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto px-2">
        {conversations.map((conversation) => (
          <ConversationItem key={conversation.id} conversation={conversation} />
        ))}
        {conversations.length === 0 && (
          <p className="px-3 py-2 text-sm text-neutral-500">Aún no hay conversaciones.</p>
        )}
      </nav>

      <div className="flex items-center gap-2 border-t border-border-subtle p-3">
        <p className="min-w-0 flex-1 truncate text-xs text-neutral-500">{userEmail}</p>
        <form action={signOut}>
          <button
            type="submit"
            aria-label="Cerrar sesión"
            title="Cerrar sesión"
            className="grid size-8 place-items-center rounded-full text-neutral-500 transition-colors hover:bg-neutral-200 hover:text-foreground dark:hover:bg-neutral-800"
          >
            <LogOut className="size-4" />
          </button>
        </form>
      </div>
    </aside>
  );
}
