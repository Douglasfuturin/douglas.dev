import { redirect } from "next/navigation";

/** Atalho para o pack Scout → Roteiro → Notion. */
export default function PipelinePage() {
  redirect("/?mode=pipeline");
}
