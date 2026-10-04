/** Prompts iniciais objetivos para executar cada skill pelo dashboard. */

export type KitStarter = {
  label: string;
  prompt: string;
};

const DEFAULT_STARTERS = (id: string, name: string): KitStarter[] => [
  {
    label: "Começar",
    prompt: `Use a skill ${name} (${id}). Peça só o mínimo necessário e entregue o resultado pronto para usar.`,
  },
  {
    label: "Brief rápido",
    prompt: `Ative ${id}. Faça 1 pergunta crítica se faltar dado; senão assuma defaults e entregue a versão 1 completa.`,
  },
];

export const KIT_STARTERS: Record<string, KitStarter[]> = {
  "youtube-script": [
    {
      label: "Roteiro 10 min",
      prompt:
        "Escreva um roteiro de YouTube de ~10 minutos. Nicho: [preencha]. Tema: [preencha]. Tom: direto e didático. Inclua gancho, retenção a cada 30s e CTA.",
    },
    {
      label: "Roteiro Shorts",
      prompt:
        "Crie 5 roteiros de Shorts (30–45s) sobre [tema], com hook na 1ª frase e CTA final.",
    },
  ],
  "youtube-title": [
    {
      label: "10 títulos",
      prompt:
        "Gere 10 títulos de YouTube de alto CTR para o vídeo: [tema/roteiro]. Rankeie e explique o porquê do top 3.",
    },
  ],
  "youtube-description": [
    {
      label: "Descrição SEO",
      prompt:
        "Escreva a descrição SEO completa (com timestamps placeholder) para: [título/tema]. Inclua CTA e links.",
    },
  ],
  "youtube-thumbnail": [
    {
      label: "4 thumbnails",
      prompt:
        "Crie 4 conceitos de thumbnail de alto CTR para: [título]. Texto curto, emoção, contraste. Gere prompts de imagem.",
    },
  ],
  "youtube-research": [
    {
      label: "Brief de nicho",
      prompt:
        "Pesquise o nicho [nicho] no YouTube: gaps, ângulos virais e 10 ideias de vídeo com potencial.",
    },
  ],
  "youtube-analysis": [
    {
      label: "Analisar canal",
      prompt:
        "Analise o canal/vídeo: [URL ou @handle]. Retenção, títulos, frequência, oportunidades.",
    },
  ],
  "youtube-audit": [
    {
      label: "Auditoria canal",
      prompt:
        "Audite o canal [URL/@handle]: branding, SEO, thumbnails, cadência. Checklist priorizado.",
    },
  ],
  "youtube-init": [
    {
      label: "Setup canal",
      prompt:
        "Monte o setup inicial de um canal sobre [nicho]: posicionamento, primeiros 10 vídeos e branding.",
    },
  ],
  "youtube-pack": [
    {
      label: "Pacote completo",
      prompt:
        "Pacote YouTube completo para o tema [tema]: pesquisa → título → roteiro → descrição → thumbnail.",
    },
  ],
  "youtube-preview": [
    {
      label: "Teaser",
      prompt:
        "Crie um preview/teaser (hook + texto on-screen) para o vídeo: [tema].",
    },
  ],
  "youtube-presentation": [
    {
      label: "Deck aula",
      prompt:
        "Estruture uma apresentação/aula YouTube sobre [tema]: outline de slides + falas.",
    },
  ],
  "instagram-reel-script": [
    {
      label: "Roteiro Reel",
      prompt:
        "Roteiro de Reel 30–45s sobre [tema]. Hook 1s, corpo, legenda e CTA.",
    },
  ],
  "instagram-pack": [
    {
      label: "Semana IG",
      prompt:
        "Pacote Instagram da semana para [nicho/marca]: 3 carrosséis, 3 reels, stories e bio.",
    },
  ],
  "instagram-audit": [
    {
      label: "Auditar perfil",
      prompt:
        "Audite o Instagram [@perfil]: bio, grade, reels, hashtags. Plano de 7 dias.",
    },
  ],
  "instagram-analysis": [
    {
      label: "Concorrentes",
      prompt:
        "Analise [@perfil] e 2 concorrentes. Insights e oportunidades de conteúdo.",
    },
  ],
  "instagram-carousel-preview": [
    {
      label: "Carrossel",
      prompt:
        "Planeje um carrossel de 8 slides sobre [tema]: headline, visual e CTA por slide.",
    },
  ],
  "instagram-thread-carousel": [
    {
      label: "Thread → carrossel",
      prompt:
        "Converta esta thread em carrossel Instagram (cole a thread abaixo):\n\n[cole aqui]",
    },
  ],
  "instagram-thumbnail": [
    {
      label: "Capa Reel",
      prompt:
        "Crie 4 capas de Reel para [tema]: texto curto + prompt visual.",
    },
  ],
  "instagram-sponsor-outreach": [
    {
      label: "Outreach",
      prompt:
        "Escreva 3 DMs/e-mails de patrocínio para marcas de [nicho]. Perfil: [@handle], métricas: [preencha].",
    },
  ],
  "graphic-carousel": [
    {
      label: "Carrossel gráfico",
      prompt:
        "Roteiro visual de carrossel gráfico sobre [tema]: tipografia, hierarquia, CTA por slide.",
    },
  ],
  "handdrawn-carousel": [
    {
      label: "Hand-drawn",
      prompt:
        "Carrossel hand-drawn sobre [tema]: slides, captions e direção de arte.",
    },
  ],
  "graphics-handdrawn-carousel": [
    {
      label: "Hand-drawn gráfico",
      prompt:
        "Carrossel hand-drawn gráfico sobre [tema]: layout + copy por slide.",
    },
  ],
  "notebook-carousel": [
    {
      label: "Estilo caderno",
      prompt:
        "Carrossel estilo caderno/anotações sobre [tema]: slides educacionais.",
    },
  ],
  "thread-to-carousel": [
    {
      label: "Converter thread",
      prompt:
        "Transforme esta thread em carrossel Instagram pronto para design:\n\n[cole a thread]",
    },
  ],
  "thread-to-carousel-alt": [
    {
      label: "Variante storytelling",
      prompt:
        "Thread → carrossel com foco em storytelling visual:\n\n[cole a thread]",
    },
  ],
  "generate-ads": [
    {
      label: "4 criativos",
      prompt:
        "Gere 4 criativos de anúncio (ângulo, hook, copy, CTA) para [produto/oferta] em Meta Ads.",
    },
  ],
  "optimize-ads": [
    {
      label: "Otimizar",
      prompt:
        "Otimize esta campanha (cole métricas):\n\n[CPA/CTR/ROAS]\n\nHipóteses + próximos testes.",
    },
  ],
  "ad-manager": [
    {
      label: "Estrutura campanha",
      prompt:
        "Planeje estrutura Meta Ads (campanha → adset → ads + UTMs) para [produto], orçamento [R$].",
    },
  ],
  "meta-ads-manager": [
    {
      label: "Gestão Meta",
      prompt:
        "Monte o plano de gestão Meta Ads para [objetivo]: públicos, criativos e métricas.",
    },
  ],
  "meta-ads-optimizer": [
    {
      label: "Otimizar Meta",
      prompt:
        "Otimize com base nestes números (cole):\n\n[métricas]\n\nAções por prioridade.",
    },
  ],
  "cartoon-ad-generator": [
    {
      label: "Ad cartoon",
      prompt:
        "Gere 4 conceitos de anúncio ilustrado/cartoon para [produto], com prompts de imagem.",
    },
  ],
  "meme-ad-generator": [
    {
      label: "Ad meme",
      prompt:
        "Crie 5 ads em formato meme para [produto/oferta]: conceito, caption e hooks.",
    },
  ],
  "ecommerce-ad-generator": [
    {
      label: "Ads e-commerce",
      prompt:
        "Gere 4 ads de e-commerce a partir de [URL do produto ou descrição]. Copy + conceito visual.",
    },
  ],
  ugc: [
    {
      label: "Brief UGC",
      prompt:
        "Brief UGC completo para creators sobre [produto]: roteiro falado, shots, do/don't e CTA.",
    },
  ],
  "email-writer": [
    {
      label: "Escrever e-mail",
      prompt:
        "Escreva um e-mail para [destinatário/objetivo]. Tom profissional e direto. Assunto + corpo + CTA.",
    },
  ],
  "email-sequence": [
    {
      label: "Sequência",
      prompt:
        "Crie uma sequência de e-mail [welcome/nurture/launch] para [oferta]. Assuntos, corpos e timing.",
    },
  ],
  "clone-website": [
    {
      label: "Clonar site",
      prompt:
        "Clone/analise este site e entregue estrutura Next.js + mapa visual: [URL]",
    },
  ],
  "copy-website": [
    {
      label: "Copy de página",
      prompt:
        "Escreva o copy completo de uma landing para [produto/oferta]: hero, benefícios, prova, CTA.",
    },
  ],
  "landing-page": [
    {
      label: "Landing",
      prompt:
        "Estruture uma landing de alta conversão para [oferta]: wireframe + copy por seção.",
    },
  ],
  "photo-generator": [
    {
      label: "Prompts foto",
      prompt:
        "Gere 4 prompts de foto/produto on-brand para [produto/cena]. Estilo: [preencha].",
    },
  ],
  "brand-image": [
    {
      label: "Imagem de marca",
      prompt:
        "Gere imagens on-brand para [marca/uso]. Leia brand-style se houver e proponha 4 variações.",
    },
  ],
  "nano-banana-diagrams": [
    {
      label: "Diagrama",
      prompt:
        "Crie um diagrama claro de [conceito/fluxo] com descrição estruturada + prompt de geração.",
    },
  ],
  "nano-banana-pro-diagram-skill": [
    {
      label: "Diagrama pro",
      prompt:
        "Diagrama avançado (arquitetura/funil/fluxo) de [sistema]. Entregue especificação + prompt.",
    },
  ],
  "fabrica-de-conteudo-com-ia": [
    {
      label: "Fábrica semanal",
      prompt:
        "Fábrica de conteúdo para [nicho]: ideias → roteiros → posts → calendário da semana.",
    },
  ],
  vsl: [
    {
      label: "Roteiro VSL",
      prompt:
        "Escreva um roteiro de VSL para [oferta]: abertura, problema, solução, oferta e close.",
    },
  ],
  "webinar-deck": [
    {
      label: "Deck webinar",
      prompt:
        "Monte um deck de webinar sobre [tema]: agenda, outline de slides, falas e CTA.",
    },
  ],
  "quick-research": [
    {
      label: "Pesquisa rápida",
      prompt:
        "Pesquisa rápida com fontes sobre: [pergunta]. Resumo acionável + links.",
    },
  ],
  "news-scanner": [
    {
      label: "Scan notícias",
      prompt:
        "Varra as notícias recentes sobre [tema]. Brief + links principais.",
    },
  ],
  "scan-news-on": [
    {
      label: "Brief diário",
      prompt:
        "Brief diário de notícias do nicho [nicho]: o que importa e por quê.",
    },
  ],
  "marketing-report": [
    {
      label: "Relatório",
      prompt:
        "Monte um relatório de marketing com base nestes dados (cole KPIs):\n\n[dados]\n\nInsights + próximos passos.",
    },
  ],
  "contract-review": [
    {
      label: "Revisar contrato",
      prompt:
        "Revise este contrato (não é aconselho jurídico): riscos, cláusulas e o que negociar.\n\n[cole o contrato]",
    },
  ],
  "invoice-creator": [
    {
      label: "Fatura",
      prompt:
        "Estruture uma fatura/orçamento para [cliente/serviço]: itens, valores, impostos e termos.",
    },
  ],
  "security-audit": [
    {
      label: "Audit segurança",
      prompt:
        "Checklist de segurança para [app/site/URL]. Achados por severidade + correções.",
    },
  ],
  "accessibility-audit": [
    {
      label: "Audit a11y",
      prompt:
        "Auditoria WCAG deste projeto/Next.js. Liste violações com arquivo, severidade e fix.",
    },
  ],
  "goal-tracker": [
    {
      label: "Metas",
      prompt:
        "Monte metas SMART + tracking semanal para: [objetivo]. Plano e métricas.",
    },
  ],
  "morning-brief": [
    {
      label: "Brief manhã",
      prompt:
        "Brief matinal: prioridades do dia para [contexto/projeto]. Agenda, riscos e foco.",
    },
  ],
  "team-update": [
    {
      label: "Update time",
      prompt:
        "Escreva um team update: wins, blockers e próximos passos de [projeto/semana].",
    },
  ],
  "learning-path": [
    {
      label: "Trilha",
      prompt:
        "Crie uma trilha de aprendizado para [objetivo/skill], com marcos semanais.",
    },
  ],
  "5x-think": [
    {
      label: "Pensar 5x",
      prompt:
        "Pense 5 níveis mais fundo sobre: [decisão/problema]. Premissas, contra-argumentos e decisão.",
    },
  ],
  "editar-video": [
    {
      label: "Editar vídeo",
      prompt:
        "Liste estilos disponíveis e edite o vídeo em [caminho] com legendas e estilo reel-mono.",
    },
  ],
};

export function startersForKit(id: string, name?: string): KitStarter[] {
  return KIT_STARTERS[id] ?? DEFAULT_STARTERS(id, name || id);
}

export function displayNameForKit(id: string, installedName?: string): string {
  // Prefer PT labels; fall back to installed name or pretty id.
  // Imported lazily by callers that already use labels-pt.
  if (installedName && installedName !== id) return installedName;
  return id
    .split("-")
    .map((p) => (p.length <= 3 ? p.toUpperCase() : p[0].toUpperCase() + p.slice(1)))
    .join(" ");
}
