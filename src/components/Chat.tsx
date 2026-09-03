"use client";

import { useRef, useState } from "react";
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
  // El SDK entrega los errores que llegan dentro del stream por callback, no en su
  // estado `error` (ese solo cubre fallos de transporte), así que los guardamos aquí.
  const [chatError, setChatError] = useState<string | null>(null);
  const failedRef = useRef(false);
  // La página de conversación nueva genera un id por render; se congela aquí para que
  // un router.refresh() no cambie el id del chat a media conversación.
  const [chatId] = useState(conversationId);

  const { messages, sendMessage, status } = useChat({
    id: chatId,
    messages: initialMessages,
    transport: new DefaultChatTransport({ api: "/api/chat" }),
    onError: (error) => {
      console.error("[Cardly] error en el chat", error);
      failedRef.current = true;
      setChatError(error.message);
    },
    onFinish: () => {
      // Si ha fallado no tocamos la ruta: el refresh remontaría el componente y
      // borraría el mensaje de error que acabamos de enseñar.
      if (failedRef.current) return;
      // replaceState en vez de router.push para no remontar el chat a mitad de uso.
      if (isNew) window.history.replaceState({}, "", `/c/${chatId}`);
      router.refresh();
    },
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!input.trim()) return;
    setChatError(null);
    failedRef.current = false;
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

          {chatError && (
            <p
              role="alert"
              className="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
            >
              {chatError}
            </p>
          )}
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
