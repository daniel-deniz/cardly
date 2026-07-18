import { Chat } from "@/components/Chat";
import { loadConversationMessages } from "@/lib/conversations";

export default async function ConversationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const initialMessages = await loadConversationMessages(id);

  return <Chat conversationId={id} initialMessages={initialMessages} isNew={false} />;
}
