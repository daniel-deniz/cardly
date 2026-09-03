"use client";

import { useState } from "react";

type CopyState = "idle" | "copied" | "error";

export function CopyButton({ text }: { text: string }) {
  const [state, setState] = useState<CopyState>("idle");

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setState("copied");
    } catch (error) {
      console.error("[Cardly] no se pudo copiar la tarjeta", error);
      setState("error");
    }
    setTimeout(() => setState("idle"), 2000);
  };

  return (
    <button
      type="button"
      onClick={copy}
      aria-label="Copiar la tarjeta al portapapeles"
      className="rounded-md px-2 py-1 text-xs text-neutral-500 transition-colors hover:bg-neutral-200 hover:text-neutral-900 dark:hover:bg-neutral-800 dark:hover:text-neutral-100"
    >
      {state === "copied" ? "Copiado" : state === "error" ? "No se pudo copiar" : "Copiar tarjeta"}
    </button>
  );
}
