/** Validates that XAI_API_KEY looks like a real key, not the .env.example stub. */
export function getXaiApiKeyStatus(): {
  ok: boolean;
  key?: string;
  error?: string;
} {
  const key = process.env.XAI_API_KEY?.trim();
  if (!key) {
    return {
      ok: false,
      error:
        "Missing XAI_API_KEY. Crie em https://console.x.ai e coloque em .env.local",
    };
  }
  // Placeholder from .env.example: "xai-..."
  if (
    key === "xai-..." ||
    key === "xai-xxx" ||
    key.length < 20 ||
    /^xai-\.+$/i.test(key)
  ) {
    return {
      ok: false,
      error:
        "XAI_API_KEY inválida (ainda é o placeholder do .env.example). Substitua pela chave real em https://console.x.ai",
    };
  }
  return { ok: true, key };
}
