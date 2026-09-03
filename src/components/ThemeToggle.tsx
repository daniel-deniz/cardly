"use client";

import { Moon, Sun } from "lucide-react";

const CLAVE = "cardly-tema";

export function ThemeToggle() {
  // Sin estado de React: el tema vive en la clase de <html> y es el CSS quien decide
  // qué icono se ve. Así no hay desajuste de hidratación ni icono equivocado al cargar.
  const alternar = () => {
    const oscuro = document.documentElement.classList.toggle("dark");
    try {
      localStorage.setItem(CLAVE, oscuro ? "dark" : "light");
    } catch (error) {
      // En navegación privada puede estar bloqueado: el cambio vale para esta
      // sesión aunque no se recuerde.
      console.warn("[Cardly] no se pudo guardar la preferencia de tema", error);
    }
  };

  return (
    <button
      type="button"
      onClick={alternar}
      aria-label="Cambiar entre modo claro y oscuro"
      title="Cambiar entre modo claro y oscuro"
      className="grid size-9 place-items-center rounded-full text-neutral-500 transition-colors hover:bg-surface hover:text-foreground"
    >
      <Moon className="size-4 dark:hidden" />
      <Sun className="hidden size-4 dark:block" />
    </button>
  );
}
