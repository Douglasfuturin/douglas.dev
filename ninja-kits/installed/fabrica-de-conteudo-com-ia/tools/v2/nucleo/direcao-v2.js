/* O ritmo da VSL, v2. Mesma API do pipeline: window.__tl (pausada),
   window.__duration, window.__ready — o html_para_video.py não muda.

   O renderer BUSCA a linha do tempo quadro a quadro. Então todo movimento —
   inclusive o que flutua e respira — mora na timeline. Nada de CSS animation,
   nada de requestAnimationFrame: o que não está na timeline não sai no vídeo.

   `t` continua significando "ESTÁ NA TELA", não "começa a se mexer" (ANTECIPA).

   Um perfil de movimento (PERFIS.a). Ele muda a mola, a queda e a saída —
   nunca o tempo das falas.

   Novo:
     D.monta(fn)      espera a fonte, mede, monta a timeline e só então __ready.
                      Toda a montagem acontece DEPOIS da fonte — é o que deixa
                      medir, dividir palavra e animar na ordem certa.
     D.pousa          a peça cai e a sombra dura aparece quando ela toca o chão (sem quicar)
     D.palavras       texto sobe palavra a palavra por máscara
     D.titulo         palavras + o marcador varre a <b>
     D.carimbo        etiqueta que bate na tela
     D.desliza        um foco que anda de item em item
     D.flutua         micro-movimento contínuo (peças sobre o apresentador)
     D.sai            saída dentro da peça. ?sai=0 desliga, quando o compositor
                      já tira a peça com o `sobe` do plano. */
(function () {
const Q = new URLSearchParams(location.search);
const R = document.documentElement;
const DIR = 'a';   // direção fechada (2a/3c); ?dir é ignorado
R.dataset.dir = DIR;
if ((Q.get('ar') || '').startsWith('1080x1920')) R.classList.add('v');
if (Q.get('k')) R.style.setProperty('--k', Q.get('k'));
// ?alfa=1 tira o papel de qualquer peça de tela cheia (renderize com --alpha)
if (Q.get('alfa') === '1') R.classList.add('alfa');
// ?chao=1 — peça transparente sobre o papel do tema, quando ela TOMA a tela (o explicador
// de aula que corta a gravação). Quem pinta o chão é o núcleo, não quem chama.
if (Q.get('chao') === '1') R.classList.remove('alfa');
// ?tema=tinta — chão tinta em qualquer peça (ver direcao-v2.css)
if (Q.get('tema') === 'tinta') R.classList.add('tinta');
// ?tema=tinteiro — o canal de Lorcana (ver direcao-v2.css). A letra dele não é a das peças,
// então a fonte entra aqui; o D.monta espera a do --fd antes do primeiro quadro.
if (Q.get('tema') === 'tinteiro') {
  R.classList.add('tinteiro');
  const f = document.createElement('link');
  f.rel = 'stylesheet';
  f.href = 'https://fonts.googleapis.com/css2?family=Unbounded:wght@500;600;700;800;900&display=block';
  // o D.monta espera ESTA folha: antes dela a regra @font-face nem existe, o fonts.load
  // volta na hora, e a medida sai com a letra substituta — o título do lote do Mercado
  // Livre encolheu na medida da letra estreita e vazou da tela com a Unbounded (29/09)
  window.__folha = new Promise(r => { f.onload = f.onerror = r; setTimeout(r, 8000); });
  document.head.appendChild(f);
}
// ?tema=marca — a marca do aluno: marca/tema.css, na raiz da fábrica (ao lado de tools/), por cima
// do núcleo. Ela redeclara os tokens em html.marca e traz a própria letra (@font-face por caminho).
// O D.monta espera a folha E as faces dela: a peça que mede o título (D.cabe) mediria a substituta.
// Fica em __tema, não em __folha, porque peça que espera a própria letra sobrescreve a __folha.
if (Q.get('tema') === 'marca') {
  R.classList.add('marca');
  const f = document.createElement('link');
  f.rel = 'stylesheet';
  f.href = new URL('../../../marca/tema.css', document.currentScript.src).href;
  window.__tema = new Promise(r => {
    f.onload = r;
    f.onerror = () => { console.error('tema marca: não achei ' + f.href); r(); };
    setTimeout(r, 8000);
  }).then(() => Promise.all([...document.fonts].map(x => x.load().catch(() => null))));
  document.head.appendChild(f);
}
window.__ready = false;
/* Cues de efeito sonoro: [{t, tipo, ...}], em segundos do vídeo, no instante
   em que a coisa ESTÁ na tela. O html_para_video.py salva isto em
   <saída>.cues.json ao lado do .mov. Vocabulário fixo, pra biblioteca de SFX
   ter um arquivo por nome (a lista inteira, com o uso de cada um, está em
   sfx/sfx.json): pop · click · stamp · impact · whoosh · whoosh-out · swish ·
   tick-roll · type · ding · riser* · boom · sub-drop · hit · swell* · tom ·
   shimmer · tape-stop · glitch · thud · papel · marca · mouse · notif · venda ·
   certo · erro · obturador · zoom-in      (* termina no instante do cue) */
window.__cues = [];

const PERFIS = {
  // Entra firme e freia sem passar do ponto (POUSA, o pousa e o carimbo); a mola fica pra quem
  // pede (MOLA, HEROI). Medido em 03/10: as referências chegam a 90 % em 67–200 ms e nunca passam
  // do ponto; o back.out passava 10–15 % e a queda de 48 px andava 10 px num quadro.
  a: {ENT: .50, EASE: 'power4.out', POUSA: 'expo.out', MOLA: 'back.out(1.7)', HEROI: 'back.out(2.1)',
      SAI: 'power3.in', TILT: 0, ROT: -1.2, QUEDA: 16},
};
const P = PERFIS[DIR];
const $ = s => typeof s === 'string' ? document.querySelector(s) : s;
const $$ = s => typeof s === 'string' ? [...document.querySelectorAll(s)]
  : Array.isArray(s) ? s.flatMap(x => typeof x === 'string' ? [...document.querySelectorAll(x)] : [x]).filter(Boolean)
  : [s].filter(Boolean);
const css = n => getComputedStyle(R).getPropertyValue(n).trim();

const D = window.D = {
  DIR, P, ANTECIPA: .18, PASSO: .34, tl: null, css, $, $$,
  // ?vivo=1 — a peça na live (fonte de navegador do OBS): pronta, a timeline TOCA em tempo
  // real, uma vez. Sem ele, a de sempre: pausada, buscável, pro render e pro qa.
  vivo: Q.get('vivo') === '1',
  // Parâmetro AUSENTE cai no exemplo; parâmetro passado VAZIO fica vazio. Antes os
  // dois caíam no exemplo, e uma citação sem fonte saía assinada "The Verge".
  q(k, d) { const v = Q.get(k); return v === null ? d : v; },
  n(k, d) { const v = Q.get(k); return parseFloat(v === null || v === '' ? d : v); },
  at(t) { return Math.max(0, t - D.ANTECIPA); },
  get SH() { return parseFloat(css('--sh')) || 10; },
  inclina(i) { return P.TILT ? (i % 2 ? P.TILT : -P.TILT) : 0; },
  brl: n => 'R$ ' + Math.round(n).toLocaleString('pt-BR'),

  /* "Nome|detalhe@0.4;Outro|x@1.2" → [{nome, det, t}] */
  itens(k, d, campos) {
    return D.q(k, d).split(';').filter(Boolean).map(s => {
      const [resto, t] = s.split('@');
      const p = resto.split('|'), o = {t: parseFloat(t)};
      campos.forEach((c, i) => o[c] = p[i]);
      return o;
    });
  },

  cue(t, tipo, extra = {}) {
    window.__cues.push({t: Math.round(Math.max(0, t) * 1000) / 1000, tipo, ...extra});
  },

  entra(alvo, t, dy = 26) {
    return D.tl.fromTo(alvo, {opacity: 0, y: dy}, {opacity: 1, y: 0,
      duration: P.ENT, ease: P.EASE}, D.at(t));
  },

  /* A peça cai e aterrissa: a sombra nasce em 0 e cresce até --sh junto com a
     queda, que freia sem quicar — o "peso" do neobrutal está na sombra dura, não na
     mola. Quem quer o quique pede: {ease: D.P.MOLA} ou D.P.HEROI. */
  pousa(alvo, t, o = {}) {
    const el = $$(alvo); if (!el.length) return;
    const rot = o.rot ?? 0;
    D.tl.fromTo(el, {x: o.dx ?? 0, y: o.dy ?? -P.QUEDA, scale: o.s ?? 1.02,
      rotation: rot + (o.dr ?? P.TILT * 2.5), '--shx': '0px'},
      {x: 0, y: 0, scale: 1, rotation: rot, '--shx': D.SH + 'px',
      duration: P.ENT, ease: o.ease || P.POUSA}, D.at(t));
    D.tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .16, ease: 'none'}, D.at(t));
    if (o.som) D.cue(t, o.som);
  },
  lista(alvos, t, passo = D.PASSO, o = {}) {
    $$(alvos).forEach((a, i) => D.pousa(a, t + i * passo, {rot: D.inclina(i), ...o}));
  },

  /* etiqueta que bate: um pouco maior e torta, assenta no tamanho sem quicar (a 1,6 com
     back.out a escala caía 0,25 num quadro e passava 15 % do ponto) */
  carimbo(alvo, t, rot = P.ROT) {
    if (!$$(alvo).length) return;
    D.cue(t, 'stamp');
    D.tl.fromTo(alvo, {opacity: 0, scale: 1.15, rotation: rot - 3},
      {opacity: 1, scale: 1, rotation: rot, duration: .38, ease: P.POUSA}, D.at(t));
  },

  /* o herói do painel: um por painel */
  heroi(alvo, t) {
    D.cue(t, 'impact');
    return D.tl.fromTo(alvo, {opacity: 0, scale: .55, y: 50, rotation: -P.TILT * 3},
      {opacity: 1, scale: 1, y: 0, rotation: 0, duration: P.ENT * 1.8, ease: P.HEROI}, D.at(t));
  },

  /* Divide o texto em palavras mascaradas. Anda pelos nós de texto, então <b>,
     <i> e as linhas do D.cabe continuam onde estavam. Rode DEPOIS do cabe:
     o cabe reescreve o innerHTML e jogaria fora estes nós. */
  divide(el) {
    const ws = [];
    const walk = node => [...node.childNodes].forEach(n => {
      if (n.nodeType === 3) {
        if (!n.textContent.trim()) return;
        const fr = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(s => {
          if (!s) return;
          if (/^\s+$/.test(s)) { fr.appendChild(document.createTextNode(s)); return; }
          const m = document.createElement('span'); m.className = 'mw';
          const w = document.createElement('span'); w.className = 'w'; w.textContent = s;
          m.appendChild(w); fr.appendChild(m); ws.push(w);
        });
        n.replaceWith(fr);
      } else if (n.nodeType === 1 && !n.classList.contains('mw')) walk(n);
    });
    walk(el);
    return ws;
  },
  palavras(alvo, t, passo = .055) {
    const el = $(alvo); if (!el || !el.textContent.trim()) return [];
    const ws = D.divide(el);
    gsap.set(el, {opacity: 1});
    ws.forEach((w, i) => D.tl.fromTo(w, {yPercent: 115, rotation: P.TILT * 4},
      {yPercent: 0, rotation: 0, duration: P.ENT * 1.1, ease: P.EASE}, D.at(t) + i * passo));
    return ws;
  },
  marca(alvo, t) {
    const bs = $$(alvo); if (!bs.length) return;
    D.tl.fromTo(bs, {backgroundSize: '0% 88%'}, {backgroundSize: '100% 88%',
      duration: .5, ease: 'power3.inOut', stagger: .12}, t);
  },
  /* a frase do painel: sobe por palavra, e o marcador varre depois da última */
  titulo(alvo, t, passo = .055) {
    const el = $(alvo); if (!el || !el.textContent.trim()) return t;
    const ws = D.palavras(el, t, passo);
    const fim = t + ws.length * passo + .1;
    D.marca([...el.querySelectorAll('b')], fim);
    return fim;
  },

  /* Número que sobe. Chame DEPOIS do cabe, com o MAIOR valor já escrito no
     elemento — o cabe mede o que está lá. Aqui ele volta pro valor de partida.
     `expo.out` corre no começo e freia no fim: a conta acontece, o número
     assenta, e o soco de escala marca a chegada. */
  conta(alvo, de, para, t, dur = P.ENT * 1.9, fmt = D.brl) {
    const el = $(alvo), o = {v: de};
    const w = n => { el.textContent = fmt(n); };
    w(de);
    D.cue(t, 'tick-roll', {dur: +dur.toFixed(3)});
    if (!el.__c0) { el.__c0 = 1; D.tl.call(() => w(de), null, 0); }
    const tw = D.tl.to(o, {v: para, duration: dur, ease: 'expo.out',
      onUpdate: () => w(o.v)}, D.at(t));
    D.tl.to(el, {scale: 1.07, duration: .14, ease: 'power2.out', yoyo: true, repeat: 1}, D.at(t) + .06);
    return tw;
  },

  /* o painel inteiro respira: aproximação lenta, um movimento só. O will-change faz o
     Chromium ampliar a camada em vez de redesenhar a letra a cada escala, que andava em
     degrau (5 quadros parados em 89); a letra perde ~8 % de nitidez no fim, invisível até 5 %. */
  camera(dur, de = 1.0, para = 1.035) {
    gsap.set('#stage', {willChange: 'transform'});
    return D.tl.fromTo('#stage', {scale: de, rotation: -P.TILT * .25},
      {scale: para, rotation: P.TILT * .25, duration: dur, ease: 'none'}, 0);
  },

  /* Micro-movimento contínuo. yPercent, não y: y é da entrada e da saída, e
     dois tweens na mesma propriedade brigam. Termina onde começou. */
  flutua(alvos, t0, t1, amp = 2, fase = 0) {
    $$(alvos).forEach((el, i) => {
      const k = i + fase, per = 2.2 + (k % 3) * .35;
      const n = Math.floor((t1 - t0 - i * .15) / per);
      if (n < 1) return;
      D.tl.to(el, {yPercent: k % 2 ? -amp : amp, duration: per / 2, ease: 'sine.inOut',
        yoyo: true, repeat: n * 2 - 1}, t0 + i * .15);
    });
  },
  respira(alvo, t0, t1, s = 1.025) {
    const per = 1.8, n = Math.floor((t1 - t0) / per);
    if (n < 1) return;
    D.tl.to(alvo, {scale: s, duration: per / 2, ease: 'sine.inOut', yoyo: true, repeat: n * 2 - 1}, t0);
  },

  /* Um foco que ANDA: nasce no primeiro item e desliza até cada um no instante
     em que é dito. Fica atrás do item, deslocado — lê como a sombra dele virando
     marcador. Mede offset, que ignora transform: pode medir com a peça no ar. */
  desliza(barra, alvos, tempos, o = {}) {
    const b = $(barra), els = $$(alvos); if (!b || !els.length) return;
    const off = o.off ?? D.SH * 1.9;
    els.forEach((el, i) => {
      const r = {left: el.offsetLeft + off, top: el.offsetTop + off,
        width: el.offsetWidth, height: el.offsetHeight};
      const t = D.at(tempos[i]) + (o.atraso ?? .14);
      if (i === 0) {
        gsap.set(b, r);
        D.tl.fromTo(b, {opacity: 0, scaleX: .15, transformOrigin: 'left center'},
          {opacity: 1, scaleX: 1, duration: .45, ease: P.EASE}, t);
      } else {
        D.tl.to(b, {...r, duration: .5, ease: P.MOLA}, t);
        D.cue(t + .1, 'swish');
      }
    });
  },

  /* Saída dentro da peça: levanta, perde a sombra e some, em cascata curta. */
  sai(alvos, t) {
    if (D.q('sai', '1') === '0') return;
    const el = $$(alvos); if (!el.length) return;
    (D._saidas = D._saidas || []).push({el, t});
  },

  /* Digita um texto letra a letra. Cada letra é um span que aparece por
     `display` — seekável, e o cursor anda junto sem medir nada. */
  digita(alvo, t, passo = .07) {
    const el = $(alvo); if (!el) return 0;
    const tx = el.textContent; el.textContent = '';
    const ls = [...tx].map(ch => { const s = document.createElement('span'); s.className = 'l'; s.textContent = ch; s.style.display = 'none'; el.appendChild(s); return s; });
    ls.forEach((s, i) => D.tl.set(s, {display: 'inline-block'}, t + i * passo));
    D.cue(t, 'type', {dur: +(ls.length * passo).toFixed(3)});
    return t + ls.length * passo;
  },
  /* anel que pulsa a partir de um ponto, em loop até t1 */
  pulsa(alvo, t0, t1, per = 1.1) {
    const el = $$(alvo);
    el.forEach((a, k) => {
      for (let t = t0 + k * per / el.length; t < t1 - .3; t += per) {
        D.tl.fromTo(a, {scale: .6, opacity: .95}, {scale: 1.7, opacity: 0, duration: Math.min(per * .9, t1 - t), ease: 'power2.out', immediateRender: false}, t);   // o último anel termina no t1, não depois do fim da peça
      }
    });
  },

  /* Captura real dentro da peça: ?img=url. Imagem, ou vídeo se terminar em
     .mp4/.mov/.webm (o quadro do vídeo segue a timeline; num render busca por
     busca, vídeo pode atrasar um quadro — prefira imagem, ou componha o vídeo
     por baixo). Sem url, o marcador listrado diz o que vai ali. */
  midia(caixa, url, rotulo = 'captura', ajuste = 'cover') {
    const c = $(caixa); if (!c) return null;
    if (!url) {
      c.insertAdjacentHTML('beforeend', `<div class="vazio"><span>${rotulo}</span></div>`);
      return null;
    }
    const ehVideo = /\.(mp4|mov|webm)(\?|$)/i.test(url);
    const m = document.createElement(ehVideo ? 'video' : 'img');
    m.src = url; m.className = 'mid'; m.style.objectFit = ajuste;
    if (ehVideo) { m.muted = true; m.playsInline = true; m.preload = 'auto'; D._videos.push(m); }
    c.appendChild(m);
    return m;
  },
  _videos: [],

  /* Encolhe a fonte até CADA linha caber sem quebrar — o mesmo da v1, agora
     síncrono porque roda dentro do D.monta, com a fonte já carregada.
     `alvo`: 1 (palco) · 0.4 (fração do palco) · '.fx' (ancestral) · ['.item', .36] */
  cabe(sel, minimo = 24, alvo = 1) {
    const medir = el => {
      const cx = getComputedStyle(el);
      return el.clientWidth - parseFloat(cx.paddingLeft) - parseFloat(cx.paddingRight);
    };
    const palco = medir(document.getElementById('stage'));
    document.querySelectorAll(sel).forEach(el => {
      if (!el.textContent.trim()) return;
      const [quem, fr] = Array.isArray(alvo) ? alvo : [alvo, 1];
      const caixa = typeof quem === 'string' ? el.closest(quem) : null;
      const limite = (caixa ? medir(caixa) : palco * quem) * fr;
      el.innerHTML = el.innerHTML.split(/<br\s*\/?>/i)
        .map(l => `<span style="display:block;white-space:nowrap">${l}</span>`).join('');
      const linhas = [...el.children];
      let px = parseFloat(getComputedStyle(el).fontSize);
      // mede a linha E a própria caixa: um filho maior que a coluna também vaza
      const vaza = () => linhas.some(l => l.scrollWidth > limite) || (el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1);
      while (px > minimo && vaza()) {
        px -= 2;
        el.style.fontSize = px + 'px';
      }
    });
  },

  /* Espera a fonte de verdade (a do display desta direção e a mono), roda a
     montagem e só então publica __tl/__duration/__ready. `fn` devolve a
     duração; sem número, vale tl.duration(). */
  monta(fn) {
    const fam = css('--fd').split(',')[0];
    const cargas = ['900 100px ', '800 100px ', '600 60px '].map(w => w + fam)
      .concat(['700 40px "IBM Plex Mono"', '600 40px "IBM Plex Mono"']);
    Promise.all([window.__folha, window.__tema])
      .then(() => Promise.all(cargas.map(f => document.fonts.load(f).catch(() => null))))
      .then(() => document.fonts.ready)
      // imagem de captura precisa estar decodificada: a peça mede a proporção dela
      // Já carregada basta (naturalWidth existe); decode() sem prazo pode nunca
      // voltar com a página em segundo plano e travava o __ready (achado na varredura).
      .then(() => Promise.all([...document.images].map(i => i.complete && i.naturalWidth ? null
        : Promise.race([i.decode ? i.decode().catch(() => null) : null, new Promise(r => { i.addEventListener('load', r, {once: true}); i.addEventListener('error', r, {once: true}); setTimeout(r, 6000); })]))))
      .then(() => Promise.all(D._videos.map(v => v.readyState >= 2 ? null : new Promise(r => { v.addEventListener('loadeddata', r, {once: true}); v.addEventListener('error', r, {once: true}); setTimeout(r, 8000); }))))
      .then(() => {
        const tl = D.tl = gsap.timeline({paused: true});
        if (D._videos.length) tl.eventCallback('onUpdate', () => D._videos.forEach(v => { v.currentTime = Math.max(0, tl.time() + (parseFloat(v.dataset.off) || 0)); }));
        const d0 = fn(tl);
        const dur = typeof d0 === 'number' && d0 > 0 ? d0 : tl.duration();
        /* Saídas agendadas DEPOIS de saber a duração, pra caberem nela. Antes a
           cascata (.34 s + até .28 s de stagger) passava até .17 s do fim: o render
           cortava a peça no meio da saída e o último quadro ficava com meio
           elemento na tela. Agora a cascata e o tempo de cada um encolhem até
           caber na janela que sobra. Achado pela varredura (nucleo/qa.js). */
        (D._saidas || []).forEach(({el, t}) => {
          const t0 = Math.max(0, Math.min(t, dur - .2)), jan = Math.max(.2, Math.min(.45, dur - t0 - .01));
          const cascata = Math.min(.28, .05 * (el.length - 1), jan * .4);
          D.cue(t0, 'whoosh-out');
          tl.to(el, {opacity: 0, y: -P.QUEDA * .7, scale: .94, '--shx': '0px', rotation: i => -D.inclina(i) * 2,
            duration: Math.min(.34, jan - cascata), ease: P.SAI, stagger: {amount: cascata}}, t0);
        });
        tl.to({}, {duration: .001}, Math.max(0, dur - .001));
        tl.time(0);
        window.__duration = dur;
        window.__cues = window.__cues.filter(c => c.t <= dur).sort((a, b) => a.t - b.t);
        window.__tl = tl;
        window.__ready = true;
        if (D.vivo) tl.play();
      });
  },
};
})();
