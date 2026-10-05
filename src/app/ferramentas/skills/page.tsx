import { CrmShell } from "@/components/crm/crm-shell";
import { NexusToolChrome } from "@/components/nexus/nexus-tool-chrome";
import { SkillsDashboard } from "@/components/skills-dashboard";

export default function FerramentasSkillsPage() {
  return (
    <CrmShell hideHeader>
      <NexusToolChrome toolId="skills">
        <div className="nexus-skills-skin">
          <SkillsDashboard embedded />
        </div>
      </NexusToolChrome>
    </CrmShell>
  );
}
