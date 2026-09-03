import { notFound } from "next/navigation";
import { Chat } from "@/components/Chat";
import { getConversation, loadConversationMessages } from "@/lib/conversations";

export default async function ConversationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const conversation = await getConversation(id);
  if (!conversation) notFound();

  const initialMessages = await loadConversationMessages(id);

  return <Chat conversationId={id} initialMessages={initialMessages} isNew={false} />;
}
