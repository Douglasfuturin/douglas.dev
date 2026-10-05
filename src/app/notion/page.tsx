import { redirect } from "next/navigation";

/** Atalho para o agente Notion (guia do repositório). */
export default function NotionAgentPage() {
  redirect("/?mode=notion");
}
