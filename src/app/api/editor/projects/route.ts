import { NextResponse } from "next/server";
import {
  createEditorProject,
  getActiveProjectId,
  listEditorProjects,
  setActiveEditorProject,
} from "@/lib/editor/project-store";
import { VIDEO_STYLES, type VideoStyle } from "@/lib/video/options";

export const runtime = "nodejs";

export async function GET() {
  const [projects, activeProjectId] = await Promise.all([
    listEditorProjects(),
    getActiveProjectId(),
  ]);
  return NextResponse.json({ projects, activeProjectId });
}

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as {
      name?: string;
      estilo?: string;
      description?: string;
      action?: "activate";
      projectId?: string;
    };

    if (body.action === "activate" && body.projectId) {
      const project = await setActiveEditorProject(body.projectId);
      if (!project) {
        return NextResponse.json(
          { error: "Projeto não encontrado" },
          { status: 404 },
        );
      }
      return NextResponse.json({ project, activeProjectId: project.id });
    }

    const estilo = (
      typeof body.estilo === "string" &&
      (VIDEO_STYLES as readonly string[]).includes(body.estilo)
        ? body.estilo
        : "aula-ccnp"
    ) as VideoStyle;

    const project = await createEditorProject({
      name: body.name?.trim() || "",
      estilo,
      description: body.description,
    });

    return NextResponse.json({ project, activeProjectId: project.id });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Falha ao criar projeto" },
      { status: 500 },
    );
  }
}
