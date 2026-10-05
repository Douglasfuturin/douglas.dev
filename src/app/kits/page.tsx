import { CrmShell } from "@/components/crm/crm-shell";
import { SkillsDashboard } from "@/components/skills-dashboard";

export default function KitsPage() {
  return (
    <CrmShell
      title="Ninja Kits"
      subtitle="Skills instaláveis e runners do ecossistema Ninja."
    >
      <SkillsDashboard />
    </CrmShell>
  );
}
