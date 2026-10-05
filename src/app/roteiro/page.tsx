import { redirect } from "next/navigation";

/** Atalho para o Roteirista. */
export default function RoteiroPage() {
  redirect("/studio?mode=roteiro");
}
