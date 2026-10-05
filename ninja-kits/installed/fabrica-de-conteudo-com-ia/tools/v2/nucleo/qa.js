/* qa.js — inspeção de peça. A MESMA regra no Estúdio (navegador) e no `v2.py qa`
   (Playwright): o que passa aqui passa no render.

   V2QA.estatico(fonte)          lê o HTML: contrato da timeline, tokens, documentação
   V2QA.dinamico(win, sons, o)   com a peça PRONTA (__ready): duração, cues com arquivo,
                                 texto que vaza/é cortado pela caixa, texto fora do quadro,
                                 zona do rosto (16:9), entrada e saída (peças alfa)
     o = {alfa, sai, rosto: [x0, y0, x1, y1] | null}

   Achado: {nivel: 'falha'|'aviso'|'nota', tipo, msg}
   Pra excluir um trecho de propósito (letreiro que corre, texto de guia): data-qa="ignora".
   Pra declarar a intenção da peça inteira: <html data-qa="entra-seco fica">. */
(function (G) {
  const TOKENS = new Set(['#0b0d12', '#0640fb', '#f2c744', '#ffffff', '#fff', '#f4f2ec', '#17a354', '#e1432f',
    '#3b3f4a', '#7c808b', '#d9d4c8', '#dce4ff', '#c9d6ff', '#ffe0d9', '#000', '#000000', '#e9e6df']);
  const FONTE_FORA = /\b(Inter|Roboto|Arial|Helvetica|Archivo|JetBrains|Montserrat|Poppins|Fraunces)\b/;

  function estatico(src) {
    const A = [], add = (nivel, tipo, msg) => A.push({nivel, tipo, msg});
    const cab = (src.match(/<!--([\s\S]*?)-->/) || ['', ''])[1];
    const cod = src.replace(/<!--[\s\S]*?-->/g, '').replace(/\/\*[\s\S]*?\*\//g, '');
    const css = (cod.match(/<style[^>]*>[\s\S]*?<\/style>/gi) || []).join('\n');
    if (/@keyframes|[\s;{]animation\s*:/.test(css)) add('falha', 'contrato', 'animação em CSS: roda fora da timeline e não sai no render quadro a quadro');
    if (/requestAnimationFrame|setInterval\s*\(/.test(cod)) add('falha', 'contrato', 'relógio próprio (requestAnimationFrame/setInterval): o render busca a timeline, não espera');
    const cores = new Set();
    for (const m of cod.matchAll(/(?::\s*|,\s*|\(\s*|['"])(#[0-9a-f]{3,8})(?=[\s;,)'"}!])/gi)) {
      const h = m[1].toLowerCase();
      if ([4, 5, 7, 9].includes(h.length) && !TOKENS.has(h)) cores.add(h);
    }
    if (cores.size) add('aviso', 'token', 'cor fora do núcleo: ' + [...cores].slice(0, 5).join(' '));
    const f = cod.match(FONTE_FORA);
    if (f) add('aviso', 'token', 'fonte fora do núcleo: ' + f[1]);
    // D.cabe embrulha cada linha do alvo num <span>: regra "alvo span" pega o embrulho também
    const alvos = [...cod.matchAll(/D\.cabe\(\s*['"]([^'"]+)['"]/g)].map(m => m[1].trim().split(/\s+/).pop());
    const regras = [...css.matchAll(/([^{}]+?)\s+span\s*\{/g)].map(m => m[1].trim().split(/\s+/).pop());
    const pega = regras.filter(r => alvos.some(a => r === a || r.endsWith(a)));
    if (pega.length) add('nota', 'css', 'regra "' + pega[0] + ' span" num alvo do D.cabe: também pega o embrulho de linha (use "' + pega[0] + ' > span")');
    if (!/^\s*\?\S/m.test(cab)) add('nota', 'doc', 'cabeçalho sem linha de exemplo (?…): o catálogo fica sem exemplo');
    if (/D\.[nq]\(\s*'t'\s*,/.test(cod)) add('nota', 'api', 'lê ?t= (antigo); as peças novas usam ?t0=');
    return A;
  }

  function opac(w, el) {
    let a = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = w.getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      a *= parseFloat(cs.opacity);
      if (a < .04) return 0;
    }
    return a;
  }
  // o retângulo que um pai recorta: overflow ≠ visible, ou clip-path inset()
  function caixaCorte(w, e, cs) {
    const b = e.getBoundingClientRect(), m = cs.clipPath && cs.clipPath.match(/inset\(([^)]*)\)/);
    if (!m) return b;
    const v = m[1].split(/\s+round\s+/)[0].trim().split(/\s+/);
    const [t, r, bo, l] = v.length === 1 ? [v[0], v[0], v[0], v[0]] : v.length === 2 ? [v[0], v[1], v[0], v[1]] : v.length === 3 ? [v[0], v[1], v[2], v[1]] : v;
    const px = (s, tot) => /%$/.test(s) ? parseFloat(s) / 100 * tot : parseFloat(s) || 0;
    return {left: b.left + px(l, b.width), right: b.right - px(r, b.width), top: b.top + px(t, b.height), bottom: b.bottom - px(bo, b.height)};
  }
  // o que sobra visível do texto depois dos pais que cortam (até `ate`, exclusive)
  function recorta(w, el, r, ate) {
    let x0 = r.left, y0 = r.top, x1 = r.right, y1 = r.bottom;
    for (let e = el; e && e.nodeType === 1 && e !== w.document.body && e !== ate; e = e.parentElement) {
      const cs = w.getComputedStyle(e);
      if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible' || (cs.clipPath && cs.clipPath !== 'none')) {
        const b = caixaCorte(w, e, cs);
        x0 = Math.max(x0, b.left); y0 = Math.max(y0, b.top); x1 = Math.min(x1, b.right); y1 = Math.min(y1, b.bottom);
        if (x1 - x0 < 1 || y1 - y0 < 1) return null;
      }
    }
    return {left: x0, top: y0, right: x1, bottom: y1};
  }
  function textos(w) {
    const d = w.document, rg = d.createRange(), tw = d.createTreeWalker(d.body, 4), out = [];
    let n;
    while ((n = tw.nextNode())) {
      const tx = n.textContent.replace(/\s+/g, ' ').trim();
      if (!tx) continue;
      const el = n.parentElement;
      if (!el || el.closest('script,style,noscript,[data-qa="ignora"]')) continue;
      rg.selectNodeContents(n);
      const b = rg.getBoundingClientRect();
      if (b.width < 1 || b.height < 1) continue;
      const a = opac(w, el);
      if (!a) continue;
      // o retângulo do texto é a caixa da linha, não a tinta: tira o respiro do
      // ascendente/descendente (em display gigante com entrelinha < 1 ele sobra muito)
      const fs = parseFloat(w.getComputedStyle(el).fontSize) || 16;
      const r = {left: b.left, right: b.right, top: b.top + fs * .22, bottom: b.bottom - fs * .1};
      if (r.bottom <= r.top) { r.top = b.top; r.bottom = b.bottom; }
      const vis = recorta(w, el, r, null);
      if (vis) out.push({el, tx, r, vis, a, fs});
    }
    return out;
  }
  // posicionado de propósito (etiqueta na borda, carimbo que sobra): não é vazar
  function solto(w, el, ate) {
    for (let e = el; e && e !== ate; e = e.parentElement) {
      const p = w.getComputedStyle(e).position;
      if (p === 'absolute' || p === 'fixed') return true;
    }
    return false;
  }
  // dentro de máscara em degradê (lista que corre): o corte é o desenho
  function mascarado(w, el) {
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = w.getComputedStyle(e);
      if ((cs.maskImage && cs.maskImage !== 'none') || (cs.webkitMaskImage && cs.webkitMaskImage !== 'none')) return true;
    }
    return false;
  }
  const dentro = (r, W, H) => r.right > 0 && r.left < W && r.bottom > 0 && r.top < H;

  function mede(w, W, H, o) {
    const out = [];
    for (const {el, tx, r, vis, fs} of textos(w)) {
      if (mascarado(w, el)) continue;
      const cx = el.closest('.nb');
      if (cx && !solto(w, el, cx)) {
        const rr = recorta(w, el, r, cx);       // os pais DENTRO da caixa que cortam (rolo de dígitos, máscara de palavra)
        if (rr) {
          const b = cx.getBoundingClientRect(), cs = w.getComputedStyle(cx), bw = parseFloat(cs.borderLeftWidth) || 0;
          const px = Math.max(b.left + bw - rr.left, rr.right - (b.right - bw), 0), py = Math.max(b.top - rr.top, rr.bottom - b.bottom, 0);
          if (px > Math.max(3, fs * .05) || py > 10) {
            const corta = cs.overflowX !== 'visible' || cs.overflowY !== 'visible';
            if (!corta) out.push({tipo: 'vaza', tx: tx.slice(0, 36), px: Math.round(Math.max(px, py))});
            else out.push({tipo: 'cortado', tx: tx.slice(0, 36), px: Math.round(Math.max(px, py))});
          }
        }
      }
      if (dentro(vis, W, H)) {
        const f = Math.max(-r.left, r.right - W, -r.top, r.bottom - H);
        if (f > 4) out.push({tipo: 'fora', tx: tx.slice(0, 36), px: Math.round(f)});
        if (o.rosto) {
          const [x0, y0, x1, y1] = o.rosto;
          if (vis.right > x0 && vis.left < x1 && vis.bottom > y0 && vis.top < y1) out.push({tipo: 'rosto', tx: tx.slice(0, 36), px: 0});
        }
      }
    }
    return out;
  }

  function dinamico(w, sons, o) {
    o = o || {};
    const tl = w.__tl, dur = +w.__duration, cues = (w.__cues || []).slice(), A = [];
    const add = (nivel, tipo, msg) => A.push({nivel, tipo, msg});
    const W = w.innerWidth, H = w.innerHeight;
    if (!(dur > 0 && dur < 90)) add('falha', 'duracao', 'duração declarada inválida: ' + dur);
    const tld = tl.duration();
    if (tld > dur + .05) add('aviso', 'duracao', `a timeline tem ${tld.toFixed(2)}s e a peça declara ${dur.toFixed(2)}s: o render corta o fim`);
    const faltam = [...new Set(cues.filter(c => !sons[c.tipo]).map(c => c.tipo))];
    if (faltam.length) add('falha', 'som', 'cue sem arquivo na biblioteca: ' + faltam.join(', '));
    const depois = cues.filter(c => c.t > dur + .05);
    if (depois.length) add('aviso', 'som', `${depois.length} cue(s) depois do fim: ${depois.map(c => c.tipo + '@' + c.t).join(', ')}`);
    if (w.document.fonts && !w.document.fonts.check('700 40px "Space Grotesk"')) add('aviso', 'fonte', 'Space Grotesk não carregou: o render sai com a fonte do sistema');
    // layout: dois instantes em que tudo já entrou e nada saiu
    const vistos = new Map();
    [dur * .5, Math.max(0, dur - .55)].forEach(t => {
      tl.time(t, false);
      mede(w, W, H, o).forEach(p => { const k = p.tipo + '|' + p.tx; if (!vistos.has(k)) vistos.set(k, {...p, t}); });
    });
    const ROT = {vaza: 'texto vaza da caixa', cortado: 'texto cortado pela caixa', fora: 'texto sai do quadro', rosto: 'texto na zona do rosto'};
    vistos.forEach(p => add(p.tipo === 'fora' || p.tipo === 'rosto' ? 'aviso' : 'falha', 'layout',
      `${ROT[p.tipo]}${p.px ? ' em ' + p.px + 'px' : ''}: "${p.tx}" (${p.t.toFixed(2)}s)`));
    // data-qa no <html>: "entra-seco" (gancho que bate no 1º quadro), "fica" (segura até o corte)
    const decl = w.document.documentElement.getAttribute('data-qa') || '';
    if (o.alfa) {
      tl.time(0, false);
      const v0 = /entra-seco/.test(decl) ? [] : textos(w).filter(x => x.a > .3 && dentro(x.vis, W, H));
      if (v0.length) add('aviso', 'entrada', `já está na tela no quadro 0: "${v0[0].tx.slice(0, 32)}" (entra sem animação)`);
      if (o.sai !== false && !/fica/.test(decl)) {
        tl.time(dur, false);
        const vf = textos(w).filter(x => x.a > .3 && dentro(x.vis, W, H));
        if (vf.length) add('aviso', 'saida', `ainda na tela no último quadro: "${vf[0].tx.slice(0, 32)}" (a peça não sai)`);
      }
    }
    return {dur, tl: +tld.toFixed(3), ncues: cues.length, sons: [...new Set(cues.map(c => c.tipo))], achados: A};
  }

  G.V2QA = {estatico, dinamico, mede, versao: 2};
})(typeof window !== 'undefined' ? window : globalThis);
