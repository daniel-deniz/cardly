"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, type UIMessage } from "ai";
import { ArrowUp } from "lucide-react";
import { CardlyAvatar } from "@/components/CardlyAvatar";
import { CopyButton } from "@/components/CopyButton";
import { TypingIndicator } from "@/components/TypingIndicator";

const SUGERENCIAS = [
  "El buscador de clientes tarda más de 10 segundos y bloquea la pantalla",
  "Queremos exportar el listado de facturas a Excel, solo para administradores",
  "Al guardar un pedido sin dirección no avisa y se pierde lo escrito",
];

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
  const hiloRef = useRef<HTMLDivElement>(null);
  // Si el usuario sube a releer algo, dejamos de arrastrarle al fondo.
  const pegadoAlFondoRef = useRef(true);
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

  const isBusy = status === "submitted" || status === "streaming";

  // Las tarjetas son largas: sin esto el final de la respuesta se queda fuera de vista.
  // Se ancla de golpe (no "smooth") porque durante el streaming cada chunk vuelve a
  // dispararlo y las animaciones encadenadas se pisan y no llegan al fondo.
  useEffect(() => {
    const contenedor = hiloRef.current;
    if (!contenedor || !pegadoAlFondoRef.current) return;
    contenedor.scrollTop = contenedor.scrollHeight;
  }, [messages, isBusy]);

  const alHacerScroll = () => {
    const contenedor = hiloRef.current;
    if (!contenedor) return;
    const distanciaAlFondo = contenedor.scrollHeight - contenedor.scrollTop - contenedor.clientHeight;
    pegadoAlFondoRef.current = distanciaAlFondo < 120;
  };

  const enviar = (texto: string) => {
    const limpio = texto.trim();
    if (!limpio || isBusy) return;
    setChatError(null);
    failedRef.current = false;
    sendMessage({ text: limpio });
    setInput("");
  };

  const sinMensajes = messages.length === 0;

  return (
    <div className="flex h-full flex-col bg-background">
      <header className="flex items-center gap-3 border-b border-border-subtle px-6 py-3">
        <CardlyAvatar size={36} />
        <div className="min-w-0">
          <p className="text-sm font-semibold leading-tight">Cardly</p>
          <p className="truncate text-xs text-neutral-500">
            {isBusy ? "Escribiendo…" : "Tu asistente de tarjetas de producto"}
          </p>
        </div>
      </header>

      <div ref={hiloRef} onScroll={alHacerScroll} className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto max-w-2xl">
          {sinMensajes ? (
            <div className="flex flex-col items-center gap-4 pt-10 text-center">
              <CardlyAvatar size={72} />
              <div>
                <p className="text-base font-semibold">¿Qué convertimos en tarjeta?</p>
                <p className="mt-1 text-sm text-neutral-500">
                  Cuéntame la funcionalidad o el bug con tus palabras. Yo le doy el formato.
                </p>
              </div>
              <div className="mt-2 flex w-full flex-col gap-2">
                {SUGERENCIAS.map((sugerencia) => (
                  <button
                    key={sugerencia}
                    type="button"
                    onClick={() => enviar(sugerencia)}
                    className="rounded-xl border border-border-subtle bg-surface px-4 py-3 text-left text-sm text-neutral-600 transition-colors hover:border-brand-400 hover:text-foreground dark:text-neutral-300"
                  >
                    {sugerencia}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              {messages.map((message, index) => {
                const text = textFromMessage(message);
                const isUser = message.role === "user";
                // Mientras se genera, la última tarjeta está a medias: copiarla daría un
                // texto incompleto, así que el botón aparece al terminar.
                const generandose = isBusy && index === messages.length - 1;

                if (isUser) {
                  return (
                    <div key={message.id} className="cardly-aparece flex justify-end">
                      <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-brand-500 px-4 py-2.5 text-sm text-white">
                        {text}
                      </div>
                    </div>
                  );
                }

                return (
                  <div key={message.id} className="cardly-aparece flex gap-3">
                    <CardlyAvatar />
                    <div className="min-w-0 flex-1">
                      <div className="w-fit max-w-full whitespace-pre-wrap rounded-2xl rounded-tl-md border border-border-subtle bg-surface px-4 py-3 text-sm">
                        {/* Mientras no ha llegado texto, los puntos evitan una burbuja vacía. */}
                        {text || <TypingIndicator />}
                      </div>
                      {text && !generandose && (
                        <div className="mt-1">
                          <CopyButton text={text} />
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {status === "submitted" && (
                <div className="flex gap-3">
                  <CardlyAvatar />
                  <div className="w-fit rounded-2xl rounded-tl-md border border-border-subtle bg-surface px-4 py-3">
                    <TypingIndicator />
                  </div>
                </div>
              )}

              {chatError && (
                <p
                  role="alert"
                  className="rounded-xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/50 dark:text-red-300"
                >
                  {chatError}
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="px-6 pb-6">
        <form
          onSubmit={(event) => {
            event.preventDefault();
            enviar(input);
          }}
          className="mx-auto flex max-w-2xl items-center gap-2 rounded-full border border-border-subtle bg-surface-strong py-2 pl-5 pr-2 focus-within:border-brand-400"
        >
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Describe la funcionalidad o el bug…"
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-neutral-500"
          />
          <button
            type="submit"
            disabled={isBusy || !input.trim()}
            aria-label="Enviar"
            className="grid size-9 shrink-0 place-items-center rounded-full bg-brand-500 text-white transition-colors hover:bg-brand-600 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ArrowUp className="size-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
