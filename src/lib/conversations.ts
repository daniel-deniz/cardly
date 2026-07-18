import type { UIMessage } from "ai";
import { createClient } from "@/lib/supabase/server";
import { dbError } from "@/lib/errors";

export type ConversationSummary = {
  id: string;
  title: string;
  updated_at: string;
};

export async function listConversations(): Promise<ConversationSummary[]> {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("conversations")
    .select("id, title, updated_at")
    .order("updated_at", { ascending: false });

  if (error) dbError(error);
  return data ?? [];
}

export async function loadConversationMessages(conversationId: string): Promise<UIMessage[]> {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("messages")
    .select("id, role, content")
    .eq("conversation_id", conversationId)
    .order("created_at", { ascending: true });

  if (error) dbError(error);

  return (data ?? []).map((message) => ({
    id: message.id,
    role: message.role as "user" | "assistant",
    parts: [{ type: "text" as const, text: message.content }],
  }));
}
