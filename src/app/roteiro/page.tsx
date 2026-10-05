import { redirect } from "next/navigation";

/** Atalho para o modo Roteirista (Reels 60s). */
export default function RoteiroPage() {
  redirect("/?mode=roteiro");
}
