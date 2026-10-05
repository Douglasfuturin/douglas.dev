import { redirect } from "next/navigation";

/** Atalho: GitHub Scout + roteiros Reels 60s por nicho. */
export default function GithubPage() {
  redirect(
    "/studio?mode=github&q=" +
      encodeURIComponent(
        "Busca os melhores repositórios do GitHub em diferentes nichos (mais stars/avaliações) e me entrega um roteiro de vídeo de até 60 segundos explicando o que cada vencedor faz. Use scout_niches_with_reels_scripts.",
      ) +
      "&autosend=1",
  );
}
