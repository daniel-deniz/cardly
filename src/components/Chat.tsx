"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, type UIMessage } from "ai";

function textFromMessage(message: UIMessage): string {
  return message.parts
    .filter((part): part is Extract<typeof part, { type: "text" }> => part.type === "text")
    .map((part) => part.text)
    .join("\n");
}

export function Chat({
  conversationId,
  initialMessages,
  isNew,
}: {
  conversationId: string;
  initialMessages: UIMessage[];
  isNew: boolean;
}) {
  const router = useRouter();
  const [input, setInput] = useState("");

  const { messages, sendMessage, status } = useChat({
    id: conversationId,
    messages: initialMessages,
    transport: new DefaultChatTransport({ api: "/api/chat" }),
    onFinish: () => {
      if (isNew) router.push(`/c/${conversationId}`);
      router.refresh();
    },
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!input.trim()) return;
    sendMessage({ text: input });
    setInput("");
  };

  const isBusy = status === "submitted" || status === "streaming";

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto max-w-2xl space-y-4">
          {messages.length === 0 && (
            <p className="text-sm text-neutral-500">
              Describe la funcionalidad o el bug que necesitas convertir en tarjeta.
            </p>
          )}
          {messages.map((message) => (
            <div
              key={message.id}
              className={`whitespace-pre-wrap rounded-lg px-4 py-3 text-sm ${
                message.role === "user"
                  ? "ml-auto max-w-[80%] bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900"
                  : "mr-auto max-w-[80%] bg-neutral-100 dark:bg-neutral-900"
              }`}
            >
              {textFromMessage(message)}
            </div>
          ))}
        </div>
      </div>

      <form
        onSubmit={handleSubmit}
        className="border-t border-neutral-200 p-4 dark:border-neutral-800"
      >
        <div className="mx-auto flex max-w-2xl gap-2">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ej: necesitamos que el filtro de facturas recuerde la última fecha usada"
            className="flex-1 rounded-md border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
          <button
            type="submit"
            disabled={isBusy}
            className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-neutral-100 dark:text-neutral-900"
          >
            {isBusy ? "Generando…" : "Enviar"}
          </button>
        </div>
      </form>
    </div>
  );
}
