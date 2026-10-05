import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { tool } from "ai";
import { z } from "zod";
import {
  extractInstallUsageHints,
  fetchRepoBundle,
} from "./github-client";

const NOTION_API = "https://api.notion.com/v1";
const NOTION_VERSION = "2022-06-28";

type NotionRichText = {
  type: "text";
  text: { content: string; link?: { url: string } | null };
};

function notionToken(): string {
  return (
    process.env.NOTION_TOKEN ||
    process.env.NOTION_API_KEY ||
    process.env.NOTION_SECRET ||
    ""
  );
}

function defaultParentPageId(): string {
  return (
    process.env.NOTION_PARENT_PAGE_ID ||
    process.env.NOTION_PAGE_ID ||
    ""
  ).replace(/-/g, "");
}

function rich(content: string, url?: string): NotionRichText[] {
  const chunks: NotionRichText[] = [];
  const text = content.slice(0, 1900);
  chunks.push({
    type: "text",
    text: url ? { content: text, link: { url } } : { content: text },
  });
  return chunks;
}

function heading(text: string, level: 1 | 2 | 3 = 2) {
  const key =
    level === 1 ? "heading_1" : level === 2 ? "heading_2" : "heading_3";
  return {
    object: "block" as const,
    type: key,
    [key]: { rich_text: rich(text) },
  };
}

function paragraph(text: string, url?: string) {
  return {
    object: "block" as const,
    type: "paragraph" as const,
    paragraph: { rich_text: rich(text, url) },
  };
}

function bulleted(text: string) {
  return {
    object: "block" as const,
    type: "bulleted_list_item" as const,
    bulleted_list_item: { rich_text: rich(text) },
  };
}

function codeBlock(text: string, language = "bash") {
  return {
    object: "block" as const,
    type: "code" as const,
    code: {
      rich_text: rich(text.slice(0, 1900)),
      language,
    },
  };
}

function divider() {
  return {
    object: "block" as const,
    type: "divider" as const,
    divider: {},
  };
}

async function notionFetch(pathname: string, init?: RequestInit) {
  const token = notionToken();
  if (!token) {
    throw new Error(
      "NOTION_TOKEN ausente. Defina NOTION_TOKEN (integração Notion) e compartilhe a página pai com a integração.",
    );
  }
  const res = await fetch(`${NOTION_API}${pathname}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Notion-Version": NOTION_VERSION,
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg =
      (data as { message?: string }).message ||
      JSON.stringify(data).slice(0, 400);
    throw new Error(`Notion API ${res.status}: ${msg}`);
  }
  return data as Record<string, unknown>;
}

function buildMarkdownGuide(input: {
  fullName: string;
  url: string;
  description: string | null;
  language: string | null;
  stars: number;
  topics: string[];
  license: string | null;
  homepage: string | null;
  install: string[];
  usage: string[];
  extraNotes?: string;
}): string {
  const installBody =
    input.install.length > 0
      ? input.install.join("\n")
      : [
          `git clone ${input.url}.git`,
          `cd ${input.fullName.split("/")[1] || "repo"}`,
          "# siga o README do projeto para dependências",
        ].join("\n");

  const usageBody =
    input.usage.length > 0
      ? input.usage.join("\n")
      : "Consulte o README do repositório para exemplos oficiais de uso.";

  return `# ${input.fullName}

## Link
${input.url}

${input.homepage ? `Homepage: ${input.homepage}\n` : ""}
## O que é
${input.description || "Sem descrição no GitHub — veja o README."}

- Stars: ${input.stars}
- Linguagem: ${input.language || "n/d"}
- Licença: ${input.license || "n/d"}
- Tópicos: ${input.topics.length ? input.topics.join(", ") : "n/d"}

## Como instalar
\`\`\`bash
${installBody}
\`\`\`

## Como utilizar
\`\`\`
${usageBody}
\`\`\`

${input.extraNotes ? `## Notas\n${input.extraNotes}\n` : ""}
---
Gerado pelo Grokish Notion Agent.
`;
}

function buildNotionChildren(input: {
  url: string;
  description: string | null;
  language: string | null;
  stars: number;
  topics: string[];
  license: string | null;
  homepage: string | null;
  install: string[];
  usage: string[];
  extraNotes?: string;
  localFileHint?: string;
}) {
  const children: Record<string, unknown>[] = [
    heading("Link do repositório", 2),
    paragraph(input.url, input.url),
  ];
  if (input.homepage) {
    children.push(paragraph(`Homepage: ${input.homepage}`, input.homepage));
  }
  children.push(
    divider(),
    heading("O que é", 2),
    paragraph(input.description || "Sem descrição no GitHub."),
    bulleted(`Stars: ${input.stars}`),
    bulleted(`Linguagem: ${input.language || "n/d"}`),
    bulleted(`Licença: ${input.license || "n/d"}`),
  );
  if (input.topics.length) {
    children.push(bulleted(`Tópicos: ${input.topics.join(", ")}`));
  }
  children.push(heading("Como instalar", 2));
  if (input.install.length) {
    children.push(
      codeBlock(
        input.install
          .filter((l) => !l.startsWith("#") || l.length < 120)
          .join("\n")
          .slice(0, 1800),
      ),
    );
  } else {
    children.push(
      codeBlock(`git clone ${input.url}.git\n# depois siga o README`),
    );
  }
  children.push(heading("Como utilizar", 2));
  if (input.usage.length) {
    children.push(codeBlock(input.usage.join("\n").slice(0, 1800), "plain text"));
  } else {
    children.push(
      paragraph("Veja exemplos no README oficial do repositório."),
    );
  }
  if (input.extraNotes) {
    children.push(heading("Notas", 2), paragraph(input.extraNotes));
  }
  if (input.localFileHint) {
    children.push(
      divider(),
      paragraph(`Arquivo local espelhado: ${input.localFileHint}`),
    );
  }
  return children.slice(0, 90);
}

async function uploadMarkdownAttachment(
  filename: string,
  content: string,
): Promise<{ fileUploadId: string } | { skipped: string }> {
  // Notion File Upload API (multi-part): create → send → use file_upload id
  try {
    const created = (await notionFetch("/file_uploads", {
      method: "POST",
      body: JSON.stringify({
        filename,
        content_type: "text/markdown",
      }),
    })) as { id?: string; upload_url?: string };
    if (!created.id || !created.upload_url) {
      return { skipped: "create file_uploads não retornou upload_url" };
    }
    const form = new FormData();
    form.append(
      "file",
      new Blob([content], { type: "text/markdown" }),
      filename,
    );
    const sendRes = await fetch(created.upload_url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${notionToken()}`,
        "Notion-Version": NOTION_VERSION,
      },
      body: form,
    });
    if (!sendRes.ok) {
      const t = await sendRes.text().catch(() => "");
      return { skipped: `upload falhou: ${sendRes.status} ${t.slice(0, 200)}` };
    }
    return { fileUploadId: created.id };
  } catch (err) {
    return {
      skipped: err instanceof Error ? err.message : "upload indisponível",
    };
  }
}

export type RepoGuideResult = {
  ok: boolean;
  localPath?: string;
  markdown?: string;
  notionPageId?: string | null;
  notionUrl?: string | null;
  title?: string;
  attachment?: Record<string, unknown> | null;
  error?: string;
  tip?: string;
  repo?: { fullName: string; url: string; stars: number };
};

/** Exporta guia .md local (sem Notion). */
export async function exportRepoGuideBundle(input: {
  fullName: string;
  extraNotes?: string;
}): Promise<RepoGuideResult> {
  const repo = await fetchRepoBundle(input.fullName);
  const hints = extractInstallUsageHints(repo.readmePreview);
  const markdown = buildMarkdownGuide({
    fullName: repo.fullName,
    url: repo.url,
    description: repo.description,
    language: repo.language,
    stars: repo.stars,
    topics: repo.topics,
    license: repo.license,
    homepage: repo.homepage,
    install: hints.install,
    usage: hints.usage,
    extraNotes: input.extraNotes,
  });
  const safeName = repo.fullName.replace(/[^\w.-]+/g, "_");
  const outDir = path.join(process.cwd(), "outputs", "repo-guides");
  await mkdir(outDir, { recursive: true });
  const localPath = path.join(outDir, `${safeName}.md`);
  await writeFile(localPath, markdown, "utf8");
  return {
    ok: true,
    localPath,
    markdown,
    repo: {
      fullName: repo.fullName,
      url: repo.url,
      stars: repo.stars,
    },
  };
}

/** Publica guia no Notion + salva .md local. */
export async function publishRepoGuideBundle(input: {
  fullName: string;
  parentPageId?: string;
  title?: string;
  extraNotes?: string;
  attachMarkdownFile?: boolean;
}): Promise<RepoGuideResult> {
  const attachMarkdownFile = input.attachMarkdownFile !== false;
  const exported = await exportRepoGuideBundle({
    fullName: input.fullName,
    extraNotes: input.extraNotes,
  });
  if (!exported.ok || !exported.localPath || !exported.markdown || !exported.repo) {
    return exported;
  }

  const repo = await fetchRepoBundle(input.fullName);
  const hints = extractInstallUsageHints(repo.readmePreview);
  const pageTitle = input.title || `Guia: ${repo.fullName}`;
  const parent = (input.parentPageId || defaultParentPageId()).replace(/-/g, "");

  if (!parent) {
    return {
      ok: false,
      localPath: exported.localPath,
      markdown: exported.markdown,
      repo: exported.repo,
      error:
        "Defina NOTION_PARENT_PAGE_ID (ou passe parentPageId) e compartilhe a página com a integração Notion (NOTION_TOKEN).",
    };
  }

  if (!notionToken()) {
    return {
      ok: false,
      localPath: exported.localPath,
      markdown: exported.markdown,
      repo: exported.repo,
      error:
        "NOTION_TOKEN ausente. Defina NOTION_TOKEN e compartilhe a página pai com a integração.",
    };
  }

  const children = buildNotionChildren({
    url: repo.url,
    description: repo.description,
    language: repo.language,
    stars: repo.stars,
    topics: repo.topics,
    license: repo.license,
    homepage: repo.homepage,
    install: hints.install,
    usage: hints.usage,
    extraNotes: input.extraNotes,
    localFileHint: exported.localPath,
  });

  const page = (await notionFetch("/pages", {
    method: "POST",
    body: JSON.stringify({
      parent: { page_id: parent },
      properties: {
        title: {
          title: [{ type: "text", text: { content: pageTitle } }],
        },
      },
      children,
    }),
  })) as { id?: string; url?: string };

  let attachment: Record<string, unknown> | null = null;
  if (attachMarkdownFile && page.id) {
    const safeName = repo.fullName.replace(/[^\w.-]+/g, "_");
    const uploaded = await uploadMarkdownAttachment(
      `${safeName}.md`,
      exported.markdown,
    );
    if ("fileUploadId" in uploaded) {
      try {
        await notionFetch(`/blocks/${page.id}/children`, {
          method: "PATCH",
          body: JSON.stringify({
            children: [
              heading("Arquivo do guia", 2),
              {
                object: "block",
                type: "file",
                file: {
                  type: "file_upload",
                  file_upload: { id: uploaded.fileUploadId },
                  name: `${safeName}.md`,
                },
              },
            ],
          }),
        });
        attachment = { ok: true, fileUploadId: uploaded.fileUploadId };
      } catch (err) {
        attachment = {
          ok: false,
          error: err instanceof Error ? err.message : "falha ao anexar arquivo",
        };
      }
    } else {
      attachment = { ok: false, skipped: uploaded.skipped };
    }
  }

  return {
    ok: true,
    notionPageId: page.id || null,
    notionUrl: page.url || null,
    localPath: exported.localPath,
    markdown: exported.markdown,
    title: pageTitle,
    repo: exported.repo,
    attachment,
    tip: "Se a página não aparecer, confira se a integração tem acesso à página pai no Notion.",
  };
}

export function notionRepoTools() {
  return {
    publish_repo_guide_to_notion: tool({
      description:
        "Cria no Notion um guia do repositório (link + instalação + uso), salva um arquivo .md local e tenta anexar o arquivo na página. Use quando o usuário pedir para publicar/disponibilizar no Notion.",
      inputSchema: z.object({
        fullName: z.string().describe("owner/repo ou URL GitHub"),
        parentPageId: z
          .string()
          .optional()
          .describe(
            "ID da página pai no Notion (senão usa NOTION_PARENT_PAGE_ID)",
          ),
        title: z.string().optional().describe("Título da página Notion"),
        extraNotes: z
          .string()
          .optional()
          .describe("Observações extras do usuário"),
        attachMarkdownFile: z
          .boolean()
          .optional()
          .describe("Tentar anexar .md na página (default true)"),
      }),
      execute: async (args) => {
        try {
          return await publishRepoGuideBundle(args);
        } catch (err) {
          return {
            ok: false,
            error: err instanceof Error ? err.message : "Falha Notion/GitHub",
          };
        }
      },
    }),

    export_repo_guide_markdown: tool({
      description:
        "Gera (e salva localmente) um arquivo Markdown com link do repo + instalação + uso, sem publicar no Notion.",
      inputSchema: z.object({
        fullName: z.string(),
        extraNotes: z.string().optional(),
      }),
      execute: async (args) => {
        try {
          const result = await exportRepoGuideBundle(args);
          return {
            ok: result.ok,
            localPath: result.localPath,
            markdown: result.markdown,
            repoUrl: result.repo?.url,
            error: result.error,
          };
        } catch (err) {
          return {
            ok: false,
            error: err instanceof Error ? err.message : "Falha ao exportar",
          };
        }
      },
    }),
  };
}
