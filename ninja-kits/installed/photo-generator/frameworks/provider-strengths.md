# Image Generation Provider Strengths

> When to use which image generation provider. The decision matters — wrong provider for the use case wastes generations, breaks brand, or produces garbled output. As of 2026 the practical providers for programmatic workflows are Gemini Nano Banana Pro and OpenAI GPT Image (gpt-image-2). Imagen 4 is an option; Midjourney and Flux are mentioned for completeness but rarely chosen for client work.

---

## At a glance

| Provider | Best for | Worst at | Cost/image | API |
|----------|----------|----------|-----------|-----|
| **Gemini Nano Banana Pro** | Photorealism, reference-driven generation, atmospheric backgrounds | Embedded text | ~$0.04-$0.08 | `google-genai` SDK |
| **OpenAI gpt-image-2** | Text-in-image (best of any provider), product mockups, clean illustrations, edits | Reference-photo likeness; atmospheric moods | ~$0.005 low / ~$0.04 med / ~$0.17 high | `openai` SDK |
| **Imagen 4** | Highest-fidelity photorealism (no reference) | Setup overhead via Vertex AI | ~$0.04-$0.08 | Vertex AI |
| **Midjourney v6+** | Aesthetic excellence | No official API | N/A programmatically | Discord bot only |
| **Flux (Black Forest)** | High-volume on-brand via LoRA training | Self-hosting required | varies | Replicate / fal.ai / self-host |

---

## Gemini 3 Pro Image Preview (Nano Banana Pro)

### What it's great at

**Photorealism with reference images.** Pass a headshot, get the same person in a new scene. This is the killer feature — likeness preservation across generations is dramatically better than any competitor in 2026. Used heavily in `thumbnail-concept` and `webinar-deck` for putting [VOICE OWNER] into composite scenes.

**Atmospheric backgrounds.** Strong at out-of-focus, moody, low-information imagery. The kind of "warm bokeh on deep navy" backdrop that goes behind text in slides — Gemini nails this. Better than OpenAI for atmospheric work.

**Scenes and environments.** Lifestyle photography, real-world settings, candid feeling images. Less "stock-photo" output than Imagen 4 in some categories.

**Multiple aspect ratios.** Supports 16:9, 9:16, 4:3, 3:4, 1:1, 21:9 cleanly via `image_config.aspect_ratio`.

**Speed.** ~5-10 seconds per image generation. Faster than OpenAI high-quality tier.

### What it's terrible at

**Text in images.** Garbles text reliably. Single short words sometimes work; anything longer than 2 words is a coin flip. Always overlay text in HTML/CSS at the destination, never bake it into the image.

**Surgical edits.** Doesn't support precise region-edits the way OpenAI does. You can pass a reference image and request changes, but "change just this corner" is unreliable.

**Cleanline illustrations.** Output is photographic by default. Asking for "flat illustration" works but gets a photo-y illustration, not clean vector-style.

**Tiny details and counting.** "Three icons in a row" often comes back with 2 or 4. Not reliable for counted compositions.

### When to use Gemini

- Atmospheric backgrounds for slides ✅
- Founder/team scenes with reference photo ✅
- Real-world environments / lifestyle ✅
- Composite of person + product / scene ✅
- Textures, abstract moody imagery ✅
- Most use cases unless reason to pick another ✅ (default)

### When NOT to use Gemini

- Need text in the image → OpenAI ❌
- Need a precise edit of an existing image → OpenAI ❌
- Need clean flat illustrations → OpenAI ❌
- Need infographic with labels → OpenAI ❌

### API quick reference

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[prompt_text, reference_image_pil_object],  # PIL Image objects
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9"),
    ),
)
# Image lives in response.candidates[0].content.parts[i].inline_data
```

### Pricing (estimated as of 2026)
- ~$0.04-$0.08 per image at standard quality
- No quality tier — single output quality

---

## OpenAI GPT Image (gpt-image-2)

`gpt-image-2` is OpenAI's latest image model (the line also includes `gpt-image-1.5` and the cheaper `gpt-image-1-mini`). It is the AIOS's **text-rendering champion** — the default provider for any image where labels and on-image type matter, and the default for every `product-mockup` offer spread.

### What it's great at

**Text rendering — best of any provider.** Renders multi-word labels, headlines, and full lockups cleanly and consistently. A `product-mockup` spread with a dozen labels comes back legible. This alone makes it the default for offer spreads, single mockups, infographics, and anything with embedded text.

**Reference-image composition.** The `images.edit` endpoint composes a new image from one or more reference images — pass a logo, product screenshots, or a finished product to build a spread around, and gpt-image-2 incorporates them. It processes every image input at high fidelity automatically (no `input_fidelity` parameter to set).

**Clean illustration aesthetics.** Flat, line-art, geometric, character-design and infographic work come out cleaner than Gemini.

**Surgical edits with a mask.** `images.edit` with a mask replaces a specific region precisely — the way to fix one garbled label without re-rolling the whole spread.

**Quality + size control.** Quality tiers `low` / `medium` / `high` trade cost for polish. Sizes are flexible (any resolution within the constraints: edges multiple of 16, max edge 3840, long:short ratio ≤ 3:1) up to 4K.

### What it's terrible at

**Likeness from reference photos.** It accepts a reference image but doesn't preserve a *specific person's* likeness the way Gemini does. Use Gemini for "put [VOICE OWNER] in this scene."

**Atmospheric subtlety.** Backgrounds come out "polished" rather than "moody." For gritty, atmospheric, cinematic backdrops (slide backgrounds), Gemini wins.

**Speed and cost at high quality.** `high` is slower and ~$0.17/image — fine for a final hero asset, pricey for rapid drafts (use `medium` or `low` to iterate).

**Transparent backgrounds.** `gpt-image-2` does not output transparent backgrounds. Generate on white, then cut out with `product-mockup`'s `remove_background.py`.

### When to use gpt-image-2

- Anything with embedded text — offer spreads, product mockups, labels, infographics ✅ (the default)
- Composing from reference images — logo, screenshots, build-a-spread-around-a-product ✅
- Clean flat illustrations / character work / iconography ✅
- A surgical mask edit to fix one region ✅

### When NOT to use it

- Preserve a specific person's likeness → Gemini ❌
- Atmospheric / moody background → Gemini ❌
- Photojournalistic / candid feel → Gemini ❌

### API quick reference

```python
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Generation
result = client.images.generate(
    model="gpt-image-2",
    prompt=prompt_text,
    size="1536x1024",      # 3:2 — any valid size; edges multiple of 16
    quality="high",         # "low" / "medium" / "high" / "auto"
)
# Image bytes are base64 in result.data[0].b64_json

# Reference-image composition / edit
result = client.images.edit(
    model="gpt-image-2",
    image=[open("logo.png", "rb"), open("product.png", "rb")],
    prompt="compose using these references...",
    size="1536x1024",
    # mask=open("mask.png", "rb")   # optional — precise region edit
)
```

### Pricing (as of 2026, per image)
- **Low:** ~$0.005-0.006 — drafts, thumbnails, fast iteration
- **Medium:** ~$0.04-0.05 — solid quality for most work
- **High:** ~$0.165-0.211 — final hero assets (offer spreads, sales-page imagery)
- Edit requests with reference images cost extra input tokens (inputs processed at high fidelity)

---

## Imagen 4 (Google, via Vertex AI)

### What it's great at

**Photorealism.** Arguably the highest fidelity of any provider for pure photography. Skin tones, hair, fabric — all extremely realistic. Better than Gemini at "this could be a real photo."

**Variants tuned for use cases.** Imagen 4 Fast (cheap, quick), Imagen 4 Pro (default), Imagen 4 Ultra (highest quality, slower). Allows fine-grained quality control.

**Photographic style range.** Excellent at studio, editorial, lifestyle, fashion — every photo style we care about, Imagen handles well.

### What it's terrible at

**Setup overhead.** Vertex AI requires GCP project, service account, IAM permissions. More steps than Gemini's simple API key.

**Reference image preservation.** Not as strong as Gemini for specific-person likeness preservation.

**No native edit endpoint.** Can't surgically edit existing images the way OpenAI does.

**Programmatic access friction.** The auth/setup flow makes it harder to drop into scripts. Most independent shops use Gemini instead even though Imagen is technically higher fidelity.

### When to use Imagen 4

- Maximum photorealism for hero shots ✅ (when worth the setup)
- High-volume photo generation (Imagen 4 Fast is cheap) ✅
- Fashion / lifestyle / editorial photography ✅
- When [CLIENT NAME] has Vertex AI already wired up ✅

### When NOT to use Imagen 4

- Quick one-off generations → Gemini ❌ (setup overhead)
- Need surgical edits → OpenAI ❌
- Reference-photo likeness preservation → Gemini ❌
- Simple workflow without GCP infra → Gemini ❌

### API quick reference

```python
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

aiplatform.init(project="your-gcp-project", location="us-central1")
model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-preview-001")
response = model.generate_images(
    prompt=prompt_text,
    number_of_images=4,
    aspect_ratio="16:9",
    negative_prompt="no text, no logos",
)
# Images in response.images
```

### Pricing (as of 2026)
- Imagen 4 Fast: ~$0.02-$0.04 per image
- Imagen 4 Pro: ~$0.04-$0.08 per image
- Imagen 4 Ultra: ~$0.08-$0.16 per image

---

## Midjourney v6+ (and v7)

Mentioned for completeness. Skip for programmatic workflows.

### What it's great at

- Best aesthetic quality of any provider for artistic / illustration work
- Strongest "this feels intentionally designed" output
- Cinematic mood and color grading

### Why we don't use it programmatically

- **No official API.** Generation happens via Discord bot. Third-party APIs exist (e.g., useapi.net) but are unofficial, prone to break, and against ToS.
- **Async workflow.** Requests take 60+ seconds, polled — not a clean fit for synchronous skill execution.
- **No reference-image likeness.** Less control over consistency.

If a [CLIENT NAME] team member wants Midjourney aesthetics for hand-curated assets, they can generate manually and drop into `assets/style-references/` — those become anchor images for Gemini generation.

---

## Flux (Black Forest Labs)

### What it's great at

- Open-source, self-hostable — full control
- Best provider for high-volume on-brand generation via LoRA training (train a model on 20-50 client photos, generate unlimited on-brand variants)
- High photorealism comparable to Imagen 4
- Strong text rendering in some variants (Flux.1 dev)
- Run via Replicate, fal.ai, RunPod, or self-host

### Why we don't use it by default

- **Infrastructure overhead.** Self-hosting requires GPU; serverless via Replicate adds setup steps
- **LoRA training is a project.** Worth it for high-volume / mature clients; overkill for new ones
- **Reference-image preservation requires LoRA training.** Without a trained LoRA, doesn't beat Gemini

### When Flux makes sense

- [CLIENT NAME] is generating 100+ images/month and brand drift is a problem
- Trained LoRA on their photos → unlimited on-brand generations
- High-end workflow with infra team available

For most clients in the AIOS, start with Gemini + OpenAI. Move to Flux only after volume justifies the LoRA training investment.

---

## Decision tree

```
Need to generate an image. Start here:

├─ Does it need readable text / labels in the image?
│  └─ YES → OpenAI gpt-image-2   (offer spreads, product mockups, infographics)
│
├─ Is it an EDIT of an existing image (with or without a mask)?
│  └─ YES → OpenAI gpt-image-2
│
├─ Is it composed from reference images (logo, product, build-around)?
│  └─ YES → OpenAI gpt-image-2
│
├─ Does it need to preserve a specific person's likeness?
│  └─ YES → Gemini Nano Banana Pro (with reference image)
│
├─ Is it a clean flat illustration / character / iconography?
│  └─ YES → OpenAI gpt-image-2
│
├─ Is it an atmospheric background (out-of-focus, moody)?
│  └─ YES → Gemini Nano Banana Pro
│
├─ Is it a scene / photograph / lifestyle?
│  └─ YES → Gemini Nano Banana Pro
│
├─ Need maximum photorealism AND have Vertex AI set up?
│  └─ YES → Imagen 4 Pro or Ultra
│
└─ Default → Gemini Nano Banana Pro (general); gpt-image-2 (anything text-heavy)
```

---

## Multi-provider workflows

Some images benefit from combining providers:

### Composite workflow: background + foreground
1. Generate atmospheric background with **Gemini** (low information density)
2. Generate clean foreground element with **OpenAI** (e.g., product, character)
3. Composite in Photoshop / via Python PIL / via HTML+CSS layering

### Iteration workflow: photo + clean edit
1. Generate base photo with **Gemini** (photorealism)
2. Send to **OpenAI gpt-image-2 edit** for surgical changes (replace background, change colors of one element, fix one garbled label)

### Volume workflow: trained Flux + Gemini
1. Train **Flux LoRA** on [CLIENT NAME]'s reference image library (one-time setup)
2. Use Flux for high-volume on-brand generation
3. Use Gemini for one-offs and reference-driven composites

For most [CLIENT NAME] workflows, the simple path — Gemini default, OpenAI for text/edits/illustrations — is enough.

---

## Provider availability and fallbacks

The `generate_image.py` script supports provider fallback:

```python
def generate_with_fallback(prompt, intent, preferred="gemini"):
    providers = [preferred, "openai", "imagen"]  # priority order
    for provider in providers:
        if not provider_available(provider):
            continue
        try:
            return generate(provider, prompt, intent)
        except ProviderError:
            continue
    raise RuntimeError("All providers failed")
```

If `GEMINI_API_KEY` isn't set, fall back to OpenAI. If neither is set, error with a clear message about which env var to add. Imagen requires Vertex AI setup, so it's never auto-fallback — opt-in only.
