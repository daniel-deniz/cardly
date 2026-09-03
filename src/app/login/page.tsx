"use client";

import { useActionState } from "react";
import { CardlyAvatar } from "@/components/CardlyAvatar";
import { signIn } from "./actions";

export default function LoginPage() {
  const [state, formAction, pending] = useActionState(signIn, { error: "" });

  return (
    <main className="flex min-h-screen items-center justify-center bg-surface px-4">
      <form
        action={formAction}
        className="w-full max-w-sm space-y-4 rounded-2xl border border-border-subtle bg-surface-strong p-8 shadow-sm"
      >
        <div className="flex flex-col items-center gap-3 text-center">
          <CardlyAvatar size={64} />
          <div>
            <h1 className="text-xl font-semibold">Cardly</h1>
            <p className="text-sm text-neutral-500">
              Inicia sesión con la cuenta que te ha dado el administrador.
            </p>
          </div>
        </div>

        <div className="space-y-1">
          <label htmlFor="email" className="text-sm font-medium">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            className="w-full rounded-lg border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-brand-400"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="password" className="text-sm font-medium">
            Contraseña
          </label>
          <input
            id="password"
            name="password"
            type="password"
            required
            className="w-full rounded-lg border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-brand-400"
          />
        </div>

        {state?.error && (
          <p className="text-sm text-red-600" role="alert">
            {state.error}
          </p>
        )}

        <button
          type="submit"
          disabled={pending}
          className="w-full rounded-lg bg-brand-500 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-600 disabled:opacity-50"
        >
          {pending ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </main>
  );
}
