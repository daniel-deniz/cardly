import { Chat } from "@/components/Chat";

export default function NewConversationPage() {
  const conversationId = crypto.randomUUID();

  return <Chat conversationId={conversationId} initialMessages={[]} isNew />;
}
