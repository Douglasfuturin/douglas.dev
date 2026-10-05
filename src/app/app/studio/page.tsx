import { ChatApp } from "@/components/chat-app";

export default function AppStudioPage() {
  return (
    <div className="flex h-full min-h-0 flex-col">
      <ChatApp variant="studio" />
    </div>
  );
}
