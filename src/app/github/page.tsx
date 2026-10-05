import { redirect } from "next/navigation";

/** Atalho para o modo GitHub Scout no chat. */
export default function GithubScoutPage() {
  redirect("/?mode=github");
}
