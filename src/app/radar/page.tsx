import { redirect } from "next/navigation";

/** Atalho para o Radar de Tendências. */
export default function RadarPage() {
  redirect("/studio?mode=radar");
}
