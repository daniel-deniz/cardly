import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { listConversations } from "@/lib/conversations";
import { Sidebar } from "@/components/Sidebar";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) redirect("/login");

  const conversations = await listConversations();

  return (
    <div className="flex h-screen">
      <Sidebar conversations={conversations} userEmail={user.email ?? ""} />
      <div className="flex-1 overflow-hidden">{children}</div>
    </div>
  );
}
