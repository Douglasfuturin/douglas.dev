import { redirect } from "next/navigation";

/** Atalho para o Notion Guide. */
export default function NotionPage() {
  redirect("/studio?mode=notion");
}
