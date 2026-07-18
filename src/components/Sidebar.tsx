"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ConversationSummary } from "@/lib/conversations";
import { signOut } from "@/app/login/actions";

export function Sidebar({
  conversations,
  userEmail,
}: {
  conversations: ConversationSummary[];
  userEmail: string;
}) {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-950">
      <div className="p-3">
        <Link
          href="/"
          className="block w-full rounded-md bg-neutral-900 px-3 py-2 text-center text-sm font-medium text-white dark:bg-neutral-100 dark:text-neutral-900"
        >
          + Nueva conversación
        </Link>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-2">
        {conversations.map((conversation) => (
          <Link
            key={conversation.id}
            href={`/c/${conversation.id}`}
            className={`block truncate rounded-md px-3 py-2 text-sm ${
              pathname === `/c/${conversation.id}`
                ? "bg-neutral-200 dark:bg-neutral-800"
                : "hover:bg-neutral-200/60 dark:hover:bg-neutral-800/60"
            }`}
          >
            {conversation.title}
          </Link>
        ))}
        {conversations.length === 0 && (
          <p className="px-3 py-2 text-sm text-neutral-500">Aún no hay conversaciones.</p>
        )}
      </nav>

      <div className="border-t border-neutral-200 p-3 dark:border-neutral-800">
        <p className="mb-2 truncate text-xs text-neutral-500">{userEmail}</p>
        <form action={signOut}>
          <button
            type="submit"
            className="w-full rounded-md border border-neutral-300 px-3 py-1.5 text-sm dark:border-neutral-700"
          >
            Cerrar sesión
          </button>
        </form>
      </div>
    </aside>
  );
}
