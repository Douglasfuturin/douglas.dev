#!/usr/bin/env node
/**
 * Generate a styled PowerPoint presentation from a JSON outline.
 *
 * Usage:
 *   node generate_presentation.js \
 *     --outline presentations/my-talk-assets/outline.json \
 *     --output presentations/my-talk.pptx \
 *     --mode normal
 *
 * Modes: normal, camera-left, camera-right
 *
 * Dependencies: npm install pptxgenjs
 */

const pptxgen = require("pptxgenjs");
const sizeOf = require("image-size");
const fs = require("fs");
const path = require("path");

// ── Design System ──────────────────────────────────────────────

const DEFAULT_ACCENT = "00CB5A";

const COLORS = {
  background: "0A0B12",
  accent: DEFAULT_ACCENT,
  white: "FFFFFF",
  light_gray: "A0A0A0",
  dark_gray: "1A1B26",
  card_border: "2A2B36",
};

const FONTS = {
  heading: "Heading Now Trial 04",
  body: "Heading Now Trial 04",
  serif: "IBM Plex Serif",
  comic: "Steel City Comic",
};

const SLIDE_W = 13.333;
const SLIDE_H = 7.5;
const MARGIN = 0.8;
const MARGIN_TOP = 0.6;

// ── Layout Bounds ──────────────────────────────────────────────

function getContentBounds(mode) {
  if (mode === "camera-left") {
    const contentLeft = SLIDE_W * 0.4;
    const contentWidth = SLIDE_W * 0.6 - MARGIN;
    return {
      left: contentLeft + 0.3,
      top: MARGIN_TOP,
      width: contentWidth,
      height: SLIDE_H - MARGIN_TOP - MARGIN,
    };
  } else if (mode === "camera-right") {
    const contentWidth = SLIDE_W * 0.6 - MARGIN;
    return {
      left: MARGIN,
      top: MARGIN_TOP,
      width: contentWidth,
      height: SLIDE_H - MARGIN_TOP - MARGIN,
    };
  }
  return {
    left: MARGIN,
    top: MARGIN_TOP,
    width: SLIDE_W - MARGIN * 2,
    height: SLIDE_H - MARGIN_TOP - MARGIN,
  };
}

function getImageBounds(mode) {
  if (mode === "camera-left") {
    const left = SLIDE_W * 0.4;
    return { left, top: 0, width: SLIDE_W - left, height: SLIDE_H };
  } else if (mode === "camera-right") {
    return { left: 0, top: 0, width: SLIDE_W * 0.6, height: SLIDE_H };
  }
  return { left: 0, top: 0, width: SLIDE_W, height: SLIDE_H };
}

// ── Helpers ────────────────────────────────────────────────────

function parseBodyText(bodyText) {
  const paragraphs = [];
  for (const rawLine of bodyText.split("\n")) {
    const line = rawLine.trim();
    if (!line) continue;
    if (line.startsWith("- ") || line.startsWith("* ")) {
      paragraphs.push({ text: line.slice(2), bullet: true });
    } else {
      paragraphs.push({ text: line, bullet: false });
    }
  }
  return paragraphs;
}

function parseInlineMarkup(text) {
  const parts = [];
  const regex = /==(.*?)==/g;
  let lastIndex = 0;
  let match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ text: text.slice(lastIndex, match.index), accent: false });
    }
    parts.push({ text: match[1], accent: true });
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push({ text: text.slice(lastIndex), accent: false });
  }
  return parts.length ? parts : [{ text, accent: false }];
}

function addStyledText(slide, text, opts) {
  const parts = parseInlineMarkup(text);
  if (parts.length === 1 && !parts[0].accent) {
    slide.addText(text, opts);
    return;
  }
  // Emphasis flips: green text → white emphasis, white text → green emphasis
  const emphasisColor = opts.color === COLORS.accent ? COLORS.white : COLORS.accent;
  const runs = parts.map((part) => ({
    text: part.text,
    options: {
      fontSize: opts.fontSize,
      fontFace: opts.fontFace,
      color: part.accent ? emphasisColor : opts.color,
      bold: part.accent ? true : !!opts.bold,
      italic: !!opts.italic,
    },
  }));
  const boxOpts = {};
  for (const key of ["x", "y", "w", "h", "align", "valign", "margin"]) {
    if (opts[key] !== undefined) boxOpts[key] = opts[key];
  }
  slide.addText(runs, boxOpts);
}

function buildRichText(paragraphs, { fontSize, fontFace, color, bold = false, italic = false }) {
  const emphasisColor = color === COLORS.accent ? COLORS.white : COLORS.accent;
  const runs = [];
  for (let i = 0; i < paragraphs.length; i++) {
    const p = paragraphs[i];
    const isLastParagraph = i === paragraphs.length - 1;
    const parts = parseInlineMarkup(p.text);
    for (let j = 0; j < parts.length; j++) {
      const part = parts[j];
      const isFirst = j === 0;
      const isLast = j === parts.length - 1;
      const opts = {
        fontSize: p.size || fontSize,
        fontFace: p.font || fontFace,
        color: part.accent ? emphasisColor : (p.color || color),
        bold: part.accent ? true : (p.bold || bold),
        italic: p.italic || italic,
      };
      if (isFirst) {
        opts.paraSpaceAfter = p.bullet ? 6 : 4;
        if (p.bullet) {
          opts.bullet = { code: "2022", color: COLORS.accent };
        }
      }
      if (isLast && !isLastParagraph) {
        opts.breakLine = true;
      }
      runs.push({ text: part.text, options: opts });
    }
  }
  return runs;
}

function addAccentLine(pres, slide, x, y, w, h = 0.04) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: COLORS.accent },
    line: { type: "none" },
  });
}

function addNumberCircle(pres, slide, x, y, number, diameter = 0.55) {
  const numStr = typeof number === "number" ? String(number).padStart(2, "0") : String(number);
  slide.addText(numStr, {
    shape: pres.shapes.OVAL,
    x, y, w: diameter, h: diameter,
    fill: { color: COLORS.accent },
    line: { type: "none" },
    fontSize: 18,
    fontFace: FONTS.heading,
    color: COLORS.background,
    bold: true,
    align: "center",
    valign: "middle",
    margin: 0,
  });
}

function addCardBackground(pres, slide, x, y, w, h) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: { color: COLORS.dark_gray },
    line: { color: COLORS.card_border, width: 1 },
    rectRadius: 0.1,
  });
}

function addFitImage(slide, imagePath, { left, top, width, height }) {
  if (imagePath && fs.existsSync(imagePath)) {
    const resolved = path.resolve(imagePath);
    try {
      const dimensions = sizeOf(resolved);
      const imgAspect = dimensions.width / dimensions.height;
      const boxAspect = width / height;

      let fitW, fitH;
      if (imgAspect > boxAspect) {
        // Image is wider than box — constrained by width
        fitW = width;
        fitH = width / imgAspect;
      } else {
        // Image is taller than box — constrained by height
        fitH = height;
        fitW = height * imgAspect;
      }

      // Center within bounds
      const fitLeft = left + (width - fitW) / 2;
      const fitTop = top + (height - fitH) / 2;

      slide.addImage({ path: resolved, x: fitLeft, y: fitTop, w: fitW, h: fitH });
    } catch (e) {
      // Fallback: place at full bounds if dimensions can't be read
      slide.addImage({ path: resolved, x: left, y: top, w: width, h: height });
    }
    return true;
  }
  return false;
}

// ── Hand-Drawn Annotations ─────────────────────────────────────

const ASSETS_DIR = path.resolve(__dirname, "../assets");

const CIRCLE_FILES = ["circle-1.png", "circle-2.png"];

function loadPngAsDataUri(filePath) {
  const buf = fs.readFileSync(filePath);
  return `data:image/png;base64,${buf.toString("base64")}`;
}

function getUnderlinePng() {
  return loadPngAsDataUri(path.join(ASSETS_DIR, "underline.png"));
}

function getCirclePng() {
  const file = CIRCLE_FILES[Math.floor(Math.random() * CIRCLE_FILES.length)];
  return loadPngAsDataUri(path.join(ASSETS_DIR, file));
}

function addHandDrawnUnderline(slide, x, y, w, h = 0.15) {
  slide.addImage({ data: getUnderlinePng(), x, y, w, h });
}

function addHandDrawnCircle(slide, x, y, w, h) {
  slide.addImage({ data: getCirclePng(), x, y, w, h: h || w * 0.7 });
}

// ── Slide Renderers ────────────────────────────────────────────

function renderTitle(pres, slide, data, bounds) {
  const { left, top, width, height } = bounds;
  const heading = data.heading || "";
  const subtitle = data.subtitle || "";
  const titleTop = subtitle ? top + height * 0.25 : top + height * 0.3;

  addStyledText(slide, heading, {
    x: left, y: titleTop, w: width, h: height * 0.35,
    fontSize: 54, fontFace: FONTS.heading,
    color: COLORS.white, bold: true,
    align: "center", valign: "middle",
  });

  if (data.heading_underline) {
    const ulW = width * 0.5;
    addHandDrawnUnderline(slide, left + (width - ulW) / 2, titleTop + height * 0.35 - 0.15, ulW);
  }

  if (subtitle) {
    addStyledText(slide, subtitle, {
      x: left, y: titleTop + 1.8, w: width, h: height * 0.2,
      fontSize: 22, fontFace: FONTS.serif,
      color: COLORS.light_gray, italic: true,
      align: "center", valign: "top",
    });
  }
}

function renderContent(pres, slide, data, bounds) {
  const { left, top, width, height } = bounds;
  const heading = data.heading || "";
  const body = data.body || "";
  const bullets = data.bullets || [];

  if (heading) {
    addStyledText(slide, heading, {
      x: left, y: top + 0.5, w: width, h: 1.2,
      fontSize: 36, fontFace: FONTS.heading,
      color: COLORS.accent, bold: true,
      align: "left", valign: "top",
    });
    if (data.heading_underline) {
      addHandDrawnUnderline(slide, left, top + 1.55, width * 0.4);
    }
  }

  const bodyTop = heading ? top + 2.0 : top + 0.5;
  const bodyHeight = heading ? height - 2.5 : height - 1.0;

  const paragraphs = [];
  if (body) paragraphs.push(...parseBodyText(body));
  for (const b of bullets) {
    paragraphs.push({ text: b, bullet: true });
  }

  if (paragraphs.length) {
    slide.addText(
      buildRichText(paragraphs, { fontSize: 26, fontFace: FONTS.body, color: COLORS.white }),
      { x: left, y: bodyTop, w: width, h: bodyHeight, valign: "top" }
    );
  }
}

function renderContentMedia(pres, slide, data, bounds, imageBounds) {
  const { left, top, width, height } = bounds;
  const heading = data.heading || "";
  const body = data.body || "";
  const bullets = data.bullets || [];
  const imagePath = data.image_path || "";
  const mediaSide = data.media_side || "right";
  const caption = data.caption || "";

  const gap = 0.3;
  const textPct = 0.55;
  const mediaPct = 0.45;

  let textLeft, textWidth, mediaLeft, mediaWidth;
  if (mediaSide === "right") {
    textLeft = left;
    textWidth = width * textPct - gap;
    mediaLeft = left + width * textPct + gap / 2;
    mediaWidth = width * mediaPct - gap / 2;
  } else {
    mediaLeft = left;
    mediaWidth = width * mediaPct - gap / 2;
    textLeft = left + width * mediaPct + gap / 2;
    textWidth = width * textPct - gap;
  }

  // Text side
  if (heading) {
    addStyledText(slide, heading, {
      x: textLeft, y: top + 0.5, w: textWidth, h: 1.2,
      fontSize: 32, fontFace: FONTS.heading,
      color: COLORS.accent, bold: true,
      align: "left", valign: "top",
    });
    if (data.heading_underline) {
      addHandDrawnUnderline(slide, textLeft, top + 1.55, textWidth * 0.5);
    }
  }

  const txtBodyTop = heading ? top + 1.8 : top + 0.5;
  const paragraphs = [];
  if (body) paragraphs.push(...parseBodyText(body));
  for (const b of bullets) {
    paragraphs.push({ text: b, bullet: true });
  }

  if (paragraphs.length) {
    slide.addText(
      buildRichText(paragraphs, { fontSize: 22, fontFace: FONTS.body, color: COLORS.white }),
      { x: textLeft, y: txtBodyTop, w: textWidth, h: height - 2.3, valign: "top" }
    );
  }

  // Media side
  const mediaTop = top + 0.3;
  const mediaHeight = height - 0.6;
  const padding = 0.15;
  const captionReserve = caption ? 0.4 : 0;
  const imgPlaced = addFitImage(slide, imagePath, {
    left: mediaLeft + padding,
    top: mediaTop + padding,
    width: mediaWidth - padding * 2,
    height: mediaHeight - padding * 2 - captionReserve,
  });

  if (!imgPlaced) {
    slide.addText(`[Media: ${imagePath}]`, {
      x: mediaLeft, y: mediaTop + mediaHeight * 0.4, w: mediaWidth, h: 1,
      fontSize: 16, fontFace: FONTS.body,
      color: COLORS.light_gray, align: "center",
    });
  }

  if (caption) {
    slide.addText(caption, {
      x: mediaLeft, y: mediaTop + mediaHeight - 0.35, w: mediaWidth, h: 0.3,
      fontSize: 14, fontFace: FONTS.body,
      color: COLORS.light_gray, align: "center",
    });
  }
}

function renderImage(pres, slide, data, bounds, imageBounds) {
  const imagePath = data.image_path || "";
  const caption = data.caption || "";

  const imgPlaced = addFitImage(slide, imagePath, {
    left: imageBounds.left,
    top: imageBounds.top,
    width: imageBounds.width,
    height: imageBounds.height,
  });

  if (!imgPlaced) {
    slide.addText(`[Image: ${imagePath}]`, {
      x: bounds.left, y: bounds.top + bounds.height * 0.4, w: bounds.width, h: 1,
      fontSize: 20, fontFace: FONTS.body,
      color: COLORS.light_gray, align: "center",
    });
  }

  if (caption) {
    slide.addText(caption, {
      x: bounds.left, y: bounds.top + bounds.height - 0.8, w: bounds.width, h: 0.6,
      fontSize: 16, fontFace: FONTS.body,
      color: COLORS.light_gray, align: "center",
    });
  }
}

function renderGif(pres, slide, data, bounds, imageBounds) {
  renderImage(pres, slide, data, bounds, imageBounds);
}

function renderSectionDivider(pres, slide, data, bounds) {
  const { left, top, width } = bounds;
  const heading = data.heading || "";
  const subtitle = data.subtitle || "";
  const sectionNumber = data.section_number;

  const centerX = left + width / 2;
  let lineTop;

  if (sectionNumber != null) {
    const circleSize = 0.55;
    addNumberCircle(pres, slide, centerX - circleSize / 2, top + 1.0, sectionNumber);
    lineTop = top + 1.8;
  } else {
    lineTop = top + 1.5;
  }

  const lineWidth = 2.5;
  addAccentLine(pres, slide, centerX - lineWidth / 2, lineTop, lineWidth);

  const headingTop = lineTop + 0.4;
  addStyledText(slide, heading, {
    x: left, y: headingTop, w: width, h: 1.5,
    fontSize: 54, fontFace: FONTS.heading,
    color: COLORS.accent, bold: true,
    align: "center", valign: "top",
  });

  if (data.heading_underline) {
    const ulW = width * 0.4;
    addHandDrawnUnderline(slide, left + (width - ulW) / 2, headingTop + 1.3, ulW);
  }

  if (subtitle) {
    addStyledText(slide, subtitle, {
      x: left, y: headingTop + 1.2, w: width, h: 0.8,
      fontSize: 20, fontFace: FONTS.serif,
      color: COLORS.light_gray, italic: true,
      align: "center", valign: "top",
    });
  }
}

function renderQuote(pres, slide, data, bounds) {
  const { left, top, width, height } = bounds;
  const text = data.text || "";
  const attribution = data.attribution || "";

  const barTop = top + height * 0.25;

  // Vertical accent bar
  addAccentLine(pres, slide, left + 0.3, barTop, 0.06, 2.2);

  addStyledText(slide, text, {
    x: left + 0.9, y: barTop, w: width - 1.2, h: 1.8,
    fontSize: 30, fontFace: FONTS.serif,
    color: COLORS.white, italic: true,
    align: "left", valign: "top",
  });

  if (attribution) {
    slide.addText(`\u2014 ${attribution}`, {
      x: left + 0.9, y: barTop + 2.0, w: width - 1.2, h: 0.5,
      fontSize: 18, fontFace: FONTS.body,
      color: COLORS.light_gray,
      align: "left", valign: "top",
    });
  }
}

function renderStats(pres, slide, data, bounds) {
  const { left, top, width, height } = bounds;
  const value = data.value || "";
  const label = data.label || "";
  const context = data.context || "";

  const centerY = top + height * 0.25;

  addStyledText(slide, value, {
    x: left, y: centerY, w: width, h: 1.8,
    fontSize: 96, fontFace: FONTS.heading,
    color: COLORS.accent, bold: true,
    align: "center", valign: "middle",
  });

  if (data.value_circle) {
    const circW = 3.5;
    const circH = 2.2;
    addHandDrawnCircle(slide, left + (width - circW) / 2, centerY + (1.8 - circH) / 2, circW, circH);
  }

  const lineWidth = 2.0;
  addAccentLine(pres, slide, left + width / 2 - lineWidth / 2, centerY + 1.6, lineWidth, 0.03);

  addStyledText(slide, label, {
    x: left, y: centerY + 2.0, w: width, h: 1.0,
    fontSize: 28, fontFace: FONTS.body,
    color: COLORS.white,
    align: "center", valign: "top",
  });

  if (context) {
    slide.addText(context, {
      x: left, y: centerY + 2.8, w: width, h: 0.6,
      fontSize: 18, fontFace: FONTS.serif,
      color: COLORS.light_gray, italic: true,
      align: "center", valign: "top",
    });
  }
}

function renderTwoColumn(pres, slide, data, bounds) {
  const { left, top, width, height } = bounds;
  const heading = data.heading || "";

  let colTop = top + 0.3;
  if (heading) {
    addStyledText(slide, heading, {
      x: left, y: colTop, w: width, h: 1.0,
      fontSize: 32, fontFace: FONTS.heading,
      color: COLORS.accent, bold: true,
      align: "left", valign: "top",
    });
    if (data.heading_underline) {
      addHandDrawnUnderline(slide, left, colTop + 0.9, width * 0.35);
    }
    colTop = top + 1.6;
  }

  const colHeight = top + height - colTop - 0.3;
  const colWidth = width * 0.47;
  const rightColLeft = left + width * 0.53;

  // Vertical divider
  addAccentLine(pres, slide, left + width * 0.5 - 0.015, colTop + 0.2, 0.03, colHeight - 0.4);

  for (const side of ["left", "right"]) {
    const colLeft = side === "left" ? left : rightColLeft;
    const colHeading = data[`${side}_heading`] || "";
    const colBody = data[`${side}_body`] || "";
    const colBullets = data[`${side}_bullets`] || [];

    let yOffset = colTop;

    if (colHeading) {
      addStyledText(slide, colHeading, {
        x: colLeft, y: yOffset, w: colWidth, h: 0.8,
        fontSize: 28, fontFace: FONTS.heading,
        color: COLORS.white, bold: true,
        align: "left", valign: "top",
      });
      yOffset += 1.0;
    }

    const paragraphs = [];
    if (colBody) paragraphs.push(...parseBodyText(colBody));
    for (const b of colBullets) {
      paragraphs.push({ text: b, bullet: true });
    }

    if (paragraphs.length) {
      slide.addText(
        buildRichText(paragraphs, { fontSize: 22, fontFace: FONTS.body, color: COLORS.white }),
        { x: colLeft, y: yOffset, w: colWidth, h: colHeight - 1.2, valign: "top" }
      );
    }
  }
}

function renderAccent(pres, slide, data, bounds) {
  const { left, top, width, height } = bounds;
  slide.addText(data.text || "", {
    x: left, y: top + height * 0.3, w: width, h: height * 0.4,
    fontSize: 48, fontFace: FONTS.comic,
    color: COLORS.accent, bold: true,
    align: "center", valign: "middle",
  });
}

function renderBlank() {
  // Just the dark background — nothing to render.
}

// ── Renderer Dispatch ──────────────────────────────────────────

const RENDERERS = {
  title: renderTitle,
  content: renderContent,
  content_media: renderContentMedia,
  image: renderImage,
  gif: renderGif,
  section_divider: renderSectionDivider,
  quote: renderQuote,
  stats: renderStats,
  two_column: renderTwoColumn,
  accent: renderAccent,
  blank: renderBlank,
};

const MEDIA_TYPES = new Set(["image", "gif", "content_media"]);

// ── CLI & Main ─────────────────────────────────────────────────

function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--outline") args.outline = argv[++i];
    else if (argv[i] === "--output") args.output = argv[++i];
    else if (argv[i] === "--mode") args.mode = argv[++i];
  }
  if (!args.outline || !args.output) {
    console.error(
      "Usage: node generate_presentation.js --outline FILE --output FILE [--mode normal|camera-left|camera-right]"
    );
    process.exit(1);
  }
  args.mode = args.mode || "normal";
  return args;
}

async function main() {
  const args = parseArgs();

  if (!fs.existsSync(args.outline)) {
    console.error(`Error: Outline file not found: ${args.outline}`);
    process.exit(1);
  }

  const outline = JSON.parse(fs.readFileSync(args.outline, "utf-8"));
  const mode = args.mode !== "normal" ? args.mode : outline.mode || "normal";

  // Allow accent color override from outline (strip leading # if present)
  if (outline.accent_color) {
    COLORS.accent = outline.accent_color.replace(/^#/, "");
  }

  const contentBounds = getContentBounds(mode);
  const imageBounds = getImageBounds(mode);

  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = outline.author || "";
  pres.title = outline.title || "Presentation";

  pres.defineSlideMaster({
    title: "DARK_BG",
    background: { color: COLORS.background },
  });

  const slides = outline.slides || [];
  if (!slides.length) {
    console.error("Error: No slides in outline");
    process.exit(1);
  }

  for (let i = 0; i < slides.length; i++) {
    const slideData = slides[i];
    const slide = pres.addSlide({ masterName: "DARK_BG" });

    const slideType = slideData.type || "content";
    const renderer = RENDERERS[slideType];

    if (!renderer) {
      console.warn(`Warning: Unknown slide type '${slideType}' at index ${i}, skipping`);
      continue;
    }

    if (MEDIA_TYPES.has(slideType)) {
      renderer(pres, slide, slideData, contentBounds, imageBounds);
    } else {
      renderer(pres, slide, slideData, contentBounds);
    }

    // Speaker notes
    if (slideData.notes) {
      slide.addNotes(slideData.notes);
    }
  }

  // Ensure output directory exists
  const outputDir = path.dirname(path.resolve(args.output));
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  await pres.writeFile({ fileName: path.resolve(args.output) });

  console.log(`Presentation saved to: ${args.output}`);
  console.log(`Total slides: ${slides.length}`);
  console.log(`Mode: ${mode}`);
}

main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
