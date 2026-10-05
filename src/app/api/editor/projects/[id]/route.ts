import { NextResponse } from "next/server";
import {
  deleteEditorProject,
  getEditorProject,
  updateEditorProject,
} from "@/lib/editor/project-store";
import type { EditorProjectPatch } from "@/lib/editor/project-types";
import { VIDEO_STYLES, type VideoStyle } from "@/lib/video/options";

export const runtime = "nodejs";

type Ctx = { params: Promise<{ id: string }> };

export async function GET(_req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const project = await getEditorProject(id);
  if (!project) {
    return NextResponse.json({ error: "Projeto não encontrado" }, { status: 404 });
  }
  return NextResponse.json({ project });
}

export async function PATCH(req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  try {
    const body = (await req.json()) as EditorProjectPatch;
    if (body.estilo && !(VIDEO_STYLES as readonly string[]).includes(body.estilo)) {
      return NextResponse.json({ error: "Estilo inválido" }, { status: 400 });
    }
    const project = await updateEditorProject(id, {
      ...body,
      estilo: body.estilo as VideoStyle | undefined,
    });
    if (!project) {
      return NextResponse.json(
        { error: "Projeto não encontrado" },
        { status: 404 },
      );
    }
    return NextResponse.json({ project });
  } catch (err) {
    return NextResponse.json(
      {
        error: err instanceof Error ? err.message : "Falha ao atualizar projeto",
      },
      { status: 500 },
    );
  }
}

export async function DELETE(_req: Request, ctx: Ctx) {
  const { id } = await ctx.params;
  const ok = await deleteEditorProject(id);
  if (!ok) {
    return NextResponse.json({ error: "Projeto não encontrado" }, { status: 404 });
  }
  return NextResponse.json({ ok: true });
}
