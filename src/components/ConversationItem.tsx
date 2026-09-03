"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Pencil, Trash2 } from "lucide-react";
import type { ConversationSummary } from "@/lib/conversations";
import { deleteConversation, renameConversation } from "@/app/(app)/actions";

export function ConversationItem({ conversation }: { conversation: ConversationSummary }) {
  const pathname = usePathname();
  const router = useRouter();
  const [renombrando, setRenombrando] = useState(false);
  const [titulo, setTitulo] = useState(conversation.title);
  const [, startTransition] = useTransition();

  const esActiva = pathname === `/c/${conversation.id}`;

  const guardarNombre = () => {
    setRenombrando(false);
    const limpio = titulo.trim();
    if (!limpio || limpio === conversation.title) {
      setTitulo(conversation.title);
      return;
    }
    startTransition(() => renameConversation(conversation.id, limpio));
  };

  const borrar = () => {
    if (!confirm(`¿Borrar "${conversation.title}"? No se puede deshacer.`)) return;
    startTransition(async () => {
      await deleteConversation(conversation.id);
      // Si estabas viéndola, la ruta dejaría de existir: vuelve a una nueva.
      if (esActiva) router.push("/");
    });
  };

  if (renombrando) {
    return (
      <form
        onSubmit={(event) => {
          event.preventDefault();
          guardarNombre();
        }}
        className="px-1 py-0.5"
      >
        <input
          autoFocus
          value={titulo}
          onChange={(event) => setTitulo(event.target.value)}
          onBlur={guardarNombre}
          onKeyDown={(event) => {
            if (event.key === "Escape") {
              setTitulo(conversation.title);
              setRenombrando(false);
            }
          }}
          className="w-full rounded-md border border-neutral-400 bg-white px-2 py-1.5 text-sm dark:border-neutral-600 dark:bg-neutral-900"
        />
      </form>
    );
  }

  return (
    <div
      className={`group flex items-center gap-1 rounded-md pr-1 ${
        esActiva ? "bg-neutral-200 dark:bg-neutral-800" : "hover:bg-neutral-200/60 dark:hover:bg-neutral-800/60"
      }`}
    >
      <Link href={`/c/${conversation.id}`} className="flex-1 truncate px-3 py-2 text-sm">
        {conversation.title}
      </Link>

      <button
        type="button"
        onClick={() => setRenombrando(true)}
        aria-label={`Renombrar ${conversation.title}`}
        className="rounded p-1 text-neutral-500 opacity-0 hover:text-neutral-900 focus-visible:opacity-100 group-hover:opacity-100 dark:hover:text-neutral-100"
      >
        <Pencil className="size-3.5" />
      </button>

      <button
        type="button"
        onClick={borrar}
        aria-label={`Borrar ${conversation.title}`}
        className="rounded p-1 text-neutral-500 opacity-0 hover:text-red-600 focus-visible:opacity-100 group-hover:opacity-100"
      >
        <Trash2 className="size-3.5" />
      </button>
    </div>
  );
}
