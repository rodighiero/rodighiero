// The network view, inlined by home.html in the same <script> as scripts-gallery.js:
// buildNetwork is called from setView there, and assigns its networkApi.
// ── Network view ──
// Built once, on first open: the graph is baked offline, so nothing is fetched or
// re-rendered. networkApi, assigned last, is the built flag.
function buildNetwork() {
  var dataNode = document.getElementById('net-data');
  if (!dataNode) return;
  var data = JSON.parse(dataNode.textContent);
  var pubs = data.nodes;
  var idxBySlug = {};
  pubs.forEach(function(p, i) { idxBySlug[p.slug] = i; });

  // One detached clone of each gallery card, copied out per selection. Every node
  // has its card: both come from the same _publications.
  var cardCache = {};
  function cardFor(slug) {
    if (!(slug in cardCache)) {
      var src = document.querySelector('.publication[data-slug="' + CSS.escape(slug) + '"]');
      cardCache[slug] = src.cloneNode(true);
      cardCache[slug].removeAttribute('style');
    }
    return cardCache[slug].cloneNode(true);
  }

  // Both baked by scripts/layout-network.js; a copy here would drift silently.
  var NODE_RADIUS = data.params.node_radius;
  var CANVAS = data.canvas;

  function svgEl(name, attrs) {
    var e = document.createElementNS('http://www.w3.org/2000/svg', name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  function el(name, cls, text) {
    var e = document.createElement(name);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  var svg = document.getElementById('net');
  var stage = document.querySelector('#network-view .stage');
  var root = svg.appendChild(svgEl('g'));
  var linkLayer = root.appendChild(svgEl('g', { class: 'links' }));
  var nodeLayer = root.appendChild(svgEl('g', { class: 'nodes' }));
  var labelLayer = root.appendChild(svgEl('g', { class: 'labels' }));

  function clearSelection() {
    if (selectedNode === null) return;
    selectedNode = null;
    unhighlight();
    details.hidden = true;
    lede.hidden = false;
  }
  svg.addEventListener('click', clearSelection);

  function dimensions() { return { w: stage.clientWidth, h: stage.clientHeight }; }
  // (bx, by) are the baked canvas positions; fitLayout() scales them into the stage.
  var nodes = pubs.map(function(p, i) {
    return { i: i, slug: p.slug, title: p.title, bx: p.x, by: p.y, tr: !!p.tr };
  });
  var links = data.links.map(function(l) {
    var s = nodes[l.source], t = nodes[l.target];
    return { source: s, target: t, translation: !!(s.tr || t.tr), fallback: !!l.fb };
  });
  // Index-parallel to nodes and links, built once: an index is the only lookup.
  var nodeEls = [];
  var labelEls = [];
  var linkEls = [];
  var selectedNode = null;

  var neighborsByIdx = nodes.map(function() { return []; });
  links.forEach(function(l) {
    neighborsByIdx[l.source.i].push(l.target.i);
    neighborsByIdx[l.target.i].push(l.source.i);
  });

  function placeNodes() {
    links.forEach(function(l, k) {
      var line = linkEls[k];
      line.setAttribute('x1', l.source.x);
      line.setAttribute('y1', l.source.y);
      line.setAttribute('x2', l.target.x);
      line.setAttribute('y2', l.target.y);
    });
    nodes.forEach(function(n, i) {
      var t = 'translate(' + n.x + ',' + n.y + ')';
      nodeEls[i].setAttribute('transform', t);
      labelEls[i].setAttribute('transform', t);
    });
  }

  /* Uniform scale and centre (object-fit: contain), so markers, labels and strokes
     keep their pixel sizes. Labels stack upward in an overflow:hidden stage, so the
     graph is nudged down by LABEL_HEADROOM for the highest one — cheaper than raising
     FIT_MARGIN, which would reshuffle every node. */
  var LABEL_HEADROOM = 16;
  function fitLayout() {
    var dim = dimensions();
    var usableH = dim.h - LABEL_HEADROOM;
    var scale = Math.min(dim.w / CANVAS.w, usableH / CANVAS.h);
    var offX = (dim.w - CANVAS.w * scale) / 2;
    var offY = LABEL_HEADROOM + (usableH - CANVAS.h * scale) / 2;
    nodes.forEach(function(n) {
      n.x = offX + n.bx * scale;
      n.y = offY + n.by * scale;
    });
  }

  function select(n) {
    selectedNode = n;
    showDetails(n);
    highlight(n);
  }
  function wireNode(g, n) {
    g.addEventListener('mouseenter', function() {
      // The mouse takes over from the keyboard: only the hovered node stays lit.
      var active = document.activeElement;
      if (active && active !== g && active.classList.contains('node')) {
        active.blur();
      }
      setNodeHover(n.i, true);
    });
    g.addEventListener('mouseleave', function() { setNodeHover(n.i, false); });
    g.addEventListener('click', function(e) {
      e.stopPropagation();
      select(n);
    });
    // Keyboard parity: focus is hover, Enter/Space is click.
    g.addEventListener('focus', function() { setNodeHover(n.i, true); });
    g.addEventListener('blur', function() { setNodeHover(n.i, false); });
    g.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        select(n);
      } else if (e.key === 'Escape') {
        clearSelection();
      }
    });
  }

  // Drawn once, in array order; afterwards only coordinates move and classes toggle.
  function build() {
    fitLayout();

    links.forEach(function(l) {
      var line = svgEl('line', { class: 'link' });
      line.classList.toggle('translation', l.translation);
      line.classList.toggle('fallback', l.fallback);
      linkEls.push(linkLayer.appendChild(line));
    });

    nodes.forEach(function(n) {
      var g = svgEl('g', { class: 'node', tabindex: 0, role: 'button', 'aria-label': n.title });
      g.appendChild(svgEl('circle', { class: 'hit', r: 12 }));
      g.appendChild(svgEl('circle', { class: 'marker', r: NODE_RADIUS }));
      g.appendChild(svgEl('circle', { class: 'ring', r: NODE_RADIUS + 2 }));
      wireNode(g, n);
      nodeEls.push(nodeLayer.appendChild(g));
      labelEls.push(labelLayer.appendChild(svgEl('text')));
    });

    placeNodes();
  }

  // Labels are measured in the live label's font, not counted in characters.
  var measureText = (function() {
    var ctx = document.createElement('canvas').getContext('2d'), font = '';
    return function(s) {
      if (!font && labelEls.length) {
        var cs = getComputedStyle(labelEls[0]);
        font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
      }
      ctx.font = font;
      return ctx.measureText(s).width;
    };
  })();

  // A label line's widest, in CSS px (clamped again to the stage in setLabel).
  var LABEL_MAX_W = 230;
  var LINE_H = 13;

  // Wrapped once per title and budget; long titles gain lines, never an ellipsis.
  var titleLines = {};
  function wrapTitle(title, budget) {
    var key = budget + '|' + title;
    if (key in titleLines) return titleLines[key];
    // French punctuation after a space sticks to the word before it.
    var words = [];
    title.split(/\s+/).forEach(function(tok) {
      if (words.length && /^[:;?!»]+$/.test(tok)) words[words.length - 1] += ' ' + tok;
      else words.push(tok);
    });
    var n = words.length;
    // Width of words[i..j), measured joined so spaces and kerning count.
    var w = [];
    for (var i = 0; i < n; i++) {
      w.push([]);
      for (var j = i + 1; j <= n; j++) w[i].push(measureText(words.slice(i, j).join(' ')));
    }
    function width(i, j) { return w[i][j - i - 1]; }
    // The budget decides the line count (greedily), the balance below the breaks.
    var k = 1, cur = words[0];
    for (var g = 1; g < n; g++) {
      var cand = cur + ' ' + words[g];
      if (measureText(cand) > budget) { k++; cur = words[g]; } else { cur = cand; }
    }
    if (k <= 1) { titleLines[key] = [title]; return titleLines[key]; }
    /* Greedy strands a short word on the last line of a third of the titles, so the
       k lines are refilled for minimum raggedness (squared slack, by DP). */
    var INF = Infinity, dp = [], ch = [];
    for (var a = 0; a <= n; a++) {
      dp.push([]); ch.push([]);
      for (var b = 0; b <= k; b++) { dp[a].push(INF); ch[a].push(0); }
    }
    dp[n][0] = 0;
    for (var p = n - 1; p >= 0; p--) {
      for (var l = 1; l <= k; l++) {
        for (var q = p + 1; q <= n; q++) {
          var lw = width(p, q);
          // A lone overlong word still gets its line rather than a mid-word break.
          if (lw > budget && q > p + 1) break;
          if (dp[q][l - 1] === INF) continue;
          var slack = budget - lw, cost = slack * slack + dp[q][l - 1];
          if (cost < dp[p][l]) { dp[p][l] = cost; ch[p][l] = q; }
        }
      }
    }
    var lines = [], at = 0, left = k;
    while (left > 0) {
      var to = ch[at][left];
      lines.push(words.slice(at, to).join(' '));
      at = to; left--;
    }
    titleLines[key] = lines;
    return lines;
  }
  // Node hover and focus, and the neighbour rows that mirror them.
  function setNodeHover(idx, on) {
    nodeEls[idx].classList.toggle('hover', on);
    labelEls[idx].classList.toggle('hover', on);
    setLabel(labelEls[idx], on ? nodes[idx].title : '', nodes[idx]);
  }
  /* Always above the node, stacked upward (LABEL_HEADROOM pays for the height);
     sideways it slides back inside the stage rather than clip. At most one label
     shows, so none can collide. */
  function setLabel(textEl, title, n) {
    textEl.textContent = '';  // drops any tspans from the last title
    if (!title) return;
    var dim = dimensions();
    var lines = wrapTitle(title, Math.min(LABEL_MAX_W, dim.w * 0.42));
    var half = 0;
    lines.forEach(function(line) { half = Math.max(half, measureText(line)); });
    half /= 2;
    var dx = 0;
    if (n.x - half < 2) dx = 2 - (n.x - half);
    else if (n.x + half > dim.w - 2) dx = dim.w - 2 - (n.x + half);
    lines.forEach(function(line, i) {
      var tspan = svgEl('tspan', { x: dx, y: -12 - (lines.length - 1 - i) * LINE_H });
      tspan.textContent = line;
      textEl.appendChild(tspan);
    });
  }

  function highlight(d) {
    var neighbors = new Set(neighborsByIdx[d.i]);
    neighbors.add(d.i);
    nodes.forEach(function(n, i) {
      var near = neighbors.has(i);
      nodeEls[i].classList.toggle('dimmed', !near);
      nodeEls[i].classList.toggle('highlight', i === d.i);
      nodeEls[i].classList.toggle('connected', near && i !== d.i);
      labelEls[i].classList.toggle('dimmed', !near);
    });
    links.forEach(function(l, k) {
      var touches = l.source.i === d.i || l.target.i === d.i;
      linkEls[k].classList.toggle('dimmed', !touches);
      linkEls[k].classList.toggle('highlight', touches);
    });
    // No pinned label: the selection's title is in the details panel.
  }
  function unhighlight() {
    nodeEls.forEach(function(g, i) {
      g.classList.remove('dimmed', 'highlight', 'connected');
      labelEls[i].classList.remove('dimmed');
      setLabel(labelEls[i], '');
    });
    linkEls.forEach(function(line) { line.classList.remove('dimmed', 'highlight'); });
  }

  var details = document.getElementById('network-details');
  var lede = document.querySelector('#network-view .lede');
  function showDetails(d) {
    lede.hidden = true;
    var pub = pubs[d.i];
    // The same `related` list the publication pages show, as node indices.
    var top = (pub.related || [])
      .map(function(r) { return [idxBySlug[r.slug], r.sim]; })
      .filter(function(t) { return t[0] != null; });
    // DOM calls, so textContent does the escaping.
    var parts = [cardFor(pub.slug)];
    if (top.length) {
      var box = el('div', 'neighbors');
      box.appendChild(el('h3', null, 'Three closest by embedding'));
      var ol = box.appendChild(el('ol'));
      top.forEach(function(t) {
        var j = t[0], s = t[1];
        var li = ol.appendChild(el('li'));
        // Floored, so a score just under STRONG_SIM never reads as clearing it.
        li.appendChild(el('span', 'sim', (Math.floor(s * 100) / 100).toFixed(2)));
        var body = li.appendChild(el('div', 'nb-body'));
        var a = body.appendChild(el('a', null, pubs[j].title));
        a.href = pubs[j].url;
        li.addEventListener('mouseenter', function() { setNodeHover(j, true); });
        li.addEventListener('mouseleave', function() { setNodeHover(j, false); });
      });
      parts.push(box);
    }
    details.replaceChildren(...parts);
    details.hidden = false;
  }

  build();

  // null means no filter. Misses leave the tab order and the accessibility tree too.
  function filter(slugs) {
    nodes.forEach(function(n, i) {
      var shown = !slugs || slugs.has(n.slug);
      nodeEls[i].classList.toggle('filtered-out', !shown);
      nodeEls[i].setAttribute('tabindex', shown ? 0 : -1);
      if (shown) nodeEls[i].removeAttribute('aria-hidden');
      else nodeEls[i].setAttribute('aria-hidden', 'true');
      labelEls[i].classList.toggle('filtered-out', !shown);
    });
    links.forEach(function(l, k) {
      var shown = !slugs || (slugs.has(l.source.slug) && slugs.has(l.target.slug));
      linkEls[k].classList.toggle('filtered-out', !shown);
    });
  }
  /* Re-fit whenever the stage changes size, whatever the cause (a column change, the
     view being shown, a resize while hidden). A hidden stage is 0×0 and is skipped. */
  new ResizeObserver(function() {
    var dim = dimensions();
    if (!dim.w || !dim.h) return;
    fitLayout();
    placeNodes();
  }).observe(stage);

  networkApi = { filter: filter, clearSelection: clearSelection };
}
