import { openai } from "@ai-sdk/openai";
import { streamText, convertToModelMessages, type UIMessage } from "ai";
import { createClient } from "@/lib/supabase/server";
import { SYSTEM_PROMPT } from "@/lib/prompt";

function textFromMessage(message: UIMessage): string {
  return message.parts
    .filter((part): part is Extract<typeof part, { type: "text" }> => part.type === "text")
    .map((part) => part.text)
    .join("\n")
    .trim();
}

export async function POST(req: Request) {
  const { id, messages }: { id: string; messages: UIMessage[] } = await req.json();

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return new Response("No autorizado", { status: 401 });
  }

  const lastMessage = messages[messages.length - 1];
  const lastMessageText = lastMessage ? textFromMessage(lastMessage) : "";

  const { data: existingConversation } = await supabase
    .from("conversations")
    .select("id")
    .eq("id", id)
    .maybeSingle();

  if (!existingConversation) {
    const { error } = await supabase.from("conversations").insert({
      id,
      user_id: user.id,
      title: lastMessageText.slice(0, 60) || "Nueva conversación",
    });
    if (error) {
      console.error("[Cardly] error creando conversación", error);
      return new Response("No se pudo crear la conversación", { status: 500 });
    }
  }

  if (lastMessage?.role === "user" && lastMessageText) {
    const { error } = await supabase
      .from("messages")
      .insert({ conversation_id: id, role: "user", content: lastMessageText });
    if (error) {
      console.error("[Cardly] no se pudo guardar el mensaje del usuario", error);
    }
  }

  const result = streamText({
    model: openai(process.env.OPENAI_MODEL ?? "gpt-5.5"),
    system: SYSTEM_PROMPT,
    messages: await convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse({
    originalMessages: messages,
    onError: (streamError) => {
      // Sin esto el fallo viaja como un stream vacío con HTTP 200 y el usuario no ve nada.
      console.error("[Cardly] error generando la tarjeta", streamError);
      return "No se ha podido generar la tarjeta. Revisa la configuración de OpenAI e inténtalo de nuevo.";
    },
    onFinish: async ({ responseMessage }) => {
      const text = textFromMessage(responseMessage);
      if (!text) return;

      const { error: insertError } = await supabase
        .from("messages")
        .insert({ conversation_id: id, role: "assistant", content: text });
      if (insertError) {
        console.error("[Cardly] no se pudo guardar la respuesta", insertError);
        return;
      }

      const { error: updateError } = await supabase
        .from("conversations")
        .update({ updated_at: new Date().toISOString() })
        .eq("id", id);
      if (updateError) {
        console.error("[Cardly] no se pudo actualizar la conversación", updateError);
      }
    },
  });
}
