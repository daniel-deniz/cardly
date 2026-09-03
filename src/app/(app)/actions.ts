"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/lib/supabase/server";

// RLS limita ambas operaciones a las conversaciones del propio usuario, así que
// un id ajeno simplemente no afecta a ninguna fila.

export async function renameConversation(id: string, title: string) {
  const nuevoTitulo = title.trim().slice(0, 80);
  if (!nuevoTitulo) return;

  const supabase = await createClient();
  const { error } = await supabase
    .from("conversations")
    .update({ title: nuevoTitulo })
    .eq("id", id);

  if (error) {
    console.error("[Cardly] no se pudo renombrar la conversación", error);
    throw new Error("No se pudo renombrar la conversación.");
  }

  revalidatePath("/", "layout");
}

export async function deleteConversation(id: string) {
  const supabase = await createClient();
  // Los mensajes caen con la conversación por el ON DELETE CASCADE del esquema.
  const { error } = await supabase.from("conversations").delete().eq("id", id);

  if (error) {
    console.error("[Cardly] no se pudo borrar la conversación", error);
    throw new Error("No se pudo borrar la conversación.");
  }

  revalidatePath("/", "layout");
}
