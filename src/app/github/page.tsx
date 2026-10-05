import { redirect } from "next/navigation";

/** Atalho para o GitHub Scout. */
export default function GithubPage() {
  redirect("/studio?mode=github");
}
