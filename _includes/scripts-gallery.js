// The homepage's gallery, filters, view toggle and bio collapse, inlined by home.html in
// one <script> with scripts-network.js (setView may call buildNetwork at boot). Liquid:
// the layout defines TYPE_LABELS, and _mobile_max is interpolated below.
var publications = document.querySelectorAll('.publication');
var searchInput = document.getElementById('search-input');
var noResults = document.getElementById('no-results');
var filterCount = document.getElementById('filter-count');
var container = document.getElementById('publications');
var viewButtons = document.querySelectorAll('.view-toggle button');
var total = publications.length;
// The masonry packs every tile; count, search and network read .publication only.
var tiles = container.querySelectorAll(':scope > .card');
var specialCards = container.querySelectorAll('.action, .filter, .event');

// ── Masonry layout (gallery only) ──
// The tokens are read from styles-base.css, never copied. The card width is the
// constant: as many CARD_W columns as fit, up to MAX_COLS; one full-width below two.
var rootStyle = getComputedStyle(document.documentElement);
var GAP_X = parseFloat(rootStyle.getPropertyValue('--card-gap'));
var CARD_W = parseFloat(rootStyle.getPropertyValue('--card-w'));
var PAGE_PAD = 2 * parseFloat(rootStyle.getPropertyValue('--page-gutter'));
var MAX_COLS = 4;
function gridWidth(n) { return n * CARD_W + GAP_X * (n - 1); }
function columnCount(w) {
  return Math.max(1, Math.min(MAX_COLS, Math.floor((w + GAP_X) / (CARD_W + GAP_X))));
}
var MAX_CONTENT = gridWidth(MAX_COLS);
var pageWidth = null; // the last width written, to spot real changes
/* Sizes the body to exactly what the column count spans, so every block ends where
   the last card does, and publishes the count as --cols (to compute with) and
   data-cols (for rules that can't). clientWidth, never innerWidth, which counts a
   classic scrollbar and makes the grid overhang the body. Returns what it wrote, so
   layoutMasonry needn't read it back. The graph's ResizeObserver catches its own
   stage changes. */
function syncPageWidth() {
  var avail = Math.min(document.documentElement.clientWidth, MAX_CONTENT + PAGE_PAD) - PAGE_PAD;
  var cols = columnCount(avail);
  var width = (cols === 1 ? avail : gridWidth(cols)) + PAGE_PAD;
  if (width !== pageWidth) {
    pageWidth = width;
    document.body.style.maxWidth = width + 'px';
    document.body.style.setProperty('--cols', cols);
    document.body.dataset.cols = cols;
  }
  return { avail: avail, cols: cols };
}
/* On the way into the network view: drop the widths, transforms and gap marks (the
   details panel clones a card, which must not inherit them), but keep the container's
   height — clearing it collapses the page on the way back, and the browser clamps
   the scroll position. With the transforms gone there is nothing to travel from. */
function clearMasonry() {
  tiles.forEach(function(p) {
    p.style.width = '';
    p.style.transform = '';
    p.removeAttribute('data-gap');
    p.style.removeProperty('--gap-span');
  });
  lastCols = null;
  placedY = [];
  lastHeight = 0;
}
// The last pass's column count (null: nothing to travel from), each tile's y, and
// the container height — remembered rather than parsed back out of the styles.
var lastCols = null;
var placedY = [];
var lastHeight = 0;
// Years between two stacked tiles, for the gap mark; 0 where either has no year
// (Forthcoming, events, the network and cluster tiles).
function gapSpan(above, below) {
  var a = parseInt(above.dataset.year, 10);
  var b = parseInt(below.dataset.year, 10);
  return isNaN(a) || isNaN(b) ? 0 : Math.abs(a - b);
}
// `synced` is syncPageWidth()'s result when the caller has just run it.
function layoutMasonry(synced) {
  // Before the view check: a resize in network view must resize the page too.
  var sync = synced || syncPageWidth();
  if (document.body.dataset.view !== 'gallery') return;
  var cols = sync.cols;
  /* A column-count change re-packs the gallery and travels like a filter change —
     except across the one-column boundary, where every card also changes width, which
     can only happen instantly. */
  var animate = lastCols !== null && lastCols !== cols && cols > 1 && lastCols > 1
    && motionOK();
  lastCols = cols;
  var colWidth = cols === 1 ? sync.avail : CARD_W;
  // A quarter of a card, not of the column: at one column that would be a card tall.
  var gapY = CARD_W / 4;
  var colHeights = new Array(cols).fill(0);
  tiles.forEach(function(p) {
    p.style.width = colWidth + 'px';
  });
  /* Read every height in one pass, then write. checkVisibility() is "does it generate
     a box" — display:none on the tile (filter) or via CSS (mobile) — and ignores the
     pre-.ready visibility:hidden, so the first pass still measures. null: not placed. */
  var heights = [];
  tiles.forEach(function(p) {
    heights.push(p.checkVisibility() ? p.getBoundingClientRect().height : null);
  });
  /* Pack into numbers first: the resulting height decides whether the change may
     animate, and a transform written outside the armed class cannot be taken back. */
  var slots = [];
  var gaps = []; // each tile's gap-mark span; undefined when nothing is below it
  /* No two graph-miniature tiles (network + clusters) in the same column in a row,
     so they read as small multiples rather than a stripe. Not at one column. */
  var lastMediaCol = -1;
  var colLast = new Array(cols).fill(-1); // the tile last placed in each column
  tiles.forEach(function(p, idx) {
    if (heights[idx] === null) { slots.push(null); return; }
    var media = p.matches('.action, .filter');
    var skip = media && cols > 1 ? lastMediaCol : -1;
    var minCol = -1; // the shortest column, bar `skip`
    for (var c = 0; c < cols; c++) {
      if (c === skip) continue;
      if (minCol < 0 || colHeights[c] < colHeights[minCol]) minCol = c;
    }
    if (media) lastMediaCol = minCol;
    var above = colLast[minCol];
    if (above >= 0) gaps[above] = gapSpan(tiles[above], p);
    colLast[minCol] = idx;
    var y = colHeights[minCol];
    slots.push({ x: minCol * (colWidth + GAP_X), y: y });
    colHeights[minCol] = y + heights[idx] + gapY;
  });
  var height = Math.max(0, Math.max(...colHeights) - gapY);
  /* A pass that shortens the page below the reader gets its scroll position clamped;
     a slide under that jump reads as the page coming apart, so it cuts instead. */
  if (animate) {
    var docHeight = document.documentElement.scrollHeight - lastHeight + height;
    if (window.scrollY > docHeight - window.innerHeight) animate = false;
  }
  // Arm before writing, and cut the tiles moving further than a screen.
  var snapped = [];
  if (animate) armTileMotion();
  tiles.forEach(function(p, idx) {
    var slot = slots[idx];
    if (!slot) return;
    if (animate && (placedY[idx] === undefined
          || Math.abs(slot.y - placedY[idx]) > window.innerHeight)) {
      p.classList.add('snapping');
      snapped.push(p);
    }
    p.style.transform = 'translate(' + slot.x + 'px,' + slot.y + 'px)';
    // The attribute is what CSS selects on, the property what it computes with;
    // 0 is a real span, so the test is explicit.
    if (gaps[idx] === undefined) {
      p.removeAttribute('data-gap');
      p.style.removeProperty('--gap-span');
    } else {
      p.setAttribute('data-gap', '');
      p.style.setProperty('--gap-span', gaps[idx]);
    }
    placedY[idx] = slot.y;
  });
  container.style.height = height + 'px';
  lastHeight = height;
  container.classList.add('ready');
  if (snapped.length) {
    // Flush the jumps, then hand the transition back for the next change.
    void container.offsetWidth;
    snapped.forEach(function(p) { p.classList.remove('snapping'); });
  }
}
/* A scheduled pass exists for one reason: the page's width may have changed (a
   resize, or the bio collapse taking a scrollbar with it). Above one column the width
   is quantized to the grid, so most frames of a drag find nothing to do. A pass
   queued before a synchronous layout finds nothing changed either. No pass on image
   load: every thumbnail carries its dimensions. */
var layoutFrame = 0;
function layoutIfPageResized() {
  var before = pageWidth;
  var sync = syncPageWidth(); // in every view: the page resizes in network view too
  if (pageWidth !== before) layoutMasonry(sync);
}
function scheduleWidthPass() {
  if (layoutFrame) return;
  layoutFrame = requestAnimationFrame(function() { layoutFrame = 0; layoutIfPageResized(); });
}
window.addEventListener('resize', scheduleWidthPass);

// ── Thumbnail warming ──
// A lazy or filtered-out card has no picture yet the first time it returns, so once
// the page settles, promote whatever is still lazy.
function warmThumbnails() { promoteLazyImages(container); }
function warmWhenIdle() {
  if (window.requestIdleCallback) requestIdleCallback(warmThumbnails, { timeout: 2000 });
  else setTimeout(warmThumbnails, 500);
}
if (document.readyState === 'complete') warmWhenIdle();
else window.addEventListener('load', warmWhenIdle, { once: true });

// ── Animating between states ── both helpers fall through to fn() on reduced motion.
var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
function motionOK() { return !reduceMotion.matches; }

// A view switch: the two views share nothing, so a cross-fade is the whole effect.
function withCrossfade(fn) {
  if (!document.startViewTransition || !motionOK()) { fn(); return; }
  document.startViewTransition(fn);
}

/* A filter change in the gallery. Deliberately not a view transition, which animates
   rasterised snapshots (a photo once dropped out mid-slide): the masonry's own
   transforms move the real tiles. A surviving tile slides, a leaving one is cut, an
   arriving one takes its slot outright and fades in. */
var TILE_MOVE_MS = parseFloat(rootStyle.getPropertyValue('--tile-move')) * 1000;
var ARM_SLACK_MS = 80; // the spring still settles just past its nominal duration
var animatingTimer = null;
/* Arms the tile transition for one change (a filter, or a column-count change) and
   disarms it after, since ordinary passes must stay instant. Re-arming extends it. */
function armTileMotion() {
  container.classList.add('animating');
  clearTimeout(animatingTimer);
  animatingTimer = setTimeout(function() {
    container.classList.remove('animating');
  }, TILE_MOVE_MS + ARM_SLACK_MS);
}
function withTileTransition(fn) {
  cancelPendingSearch(); // a deliberate change supersedes a pending typed one
  // In network view the graph fades its own nodes; the page just cross-fades.
  if (document.body.dataset.view !== 'gallery') { withCrossfade(fn); return; }
  if (!motionOK()) { fn(); layoutMasonry(); return; }

  var before = new Set();
  tiles.forEach(function(p) { if (p.style.display !== 'none') before.add(p); });

  armTileMotion();
  fn();
  var entering = [];
  tiles.forEach(function(p) {
    if (p.style.display === 'none' || before.has(p)) return;
    p.classList.add('entering');
    entering.push(p);
  });
  // Synchronous, in the same task as the display changes: one style change to animate.
  layoutMasonry();
  if (entering.length) {
    // Flush the pinned state, then release it: only opacity moves.
    void container.offsetWidth;
    entering.forEach(function(p) { p.classList.remove('entering'); });
  }
}

// Typing animates too, once a burst of keystrokes settles; per keystroke the tiles
// would restart mid-flight. Reduced motion filters instantly, without the delay.
var SEARCH_SETTLE = 180;
var searchTimer = null;
function cancelPendingSearch() {
  if (searchTimer !== null) { clearTimeout(searchTimer); searchTimer = null; }
}
function searchFromInput() {
  cancelPendingSearch();
  if (!motionOK()) { applySearch(); layoutMasonry(); return; }
  searchTimer = setTimeout(function() {
    searchTimer = null;
    withTileTransition(applySearch);
  }, SEARCH_SETTLE);
}

// ── View toggle ──
// Mirrors the state into the query string (replaceState: no history entries). Only
// user changes call it, so an incoming shared URL is left alone.
function updateURL() {
  var params;
  try { params = new URLSearchParams(location.search); } catch (e) { return; }
  var view = document.body.dataset.view;
  if (view && view !== 'gallery') params.set('view', view); else params.delete('view');
  // While a type/cluster filter is on, the box holds its label, not a query.
  var q = structuredFilterActive() ? '' : searchInput.value.trim();
  if (q) params.set('q', q); else params.delete('q');
  if (activeType) params.set('type', activeType); else params.delete('type');
  if (activeCluster) params.set('cluster', activeCluster.id); else params.delete('cluster');
  var qs = params.toString();
  history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
}
var urlTimer = null;
function scheduleURLUpdate() {
  clearTimeout(urlTimer);
  urlTimer = setTimeout(updateURL, 200);
}

/* Declared before the boot call to setView, which reads them and may build the
   network: declared later, `var` hoisting would run the initializers after it and
   null out a networkApi already built. */
var matchedSlugs = null;
var networkApi = null;    // { filter(slugs), clearSelection() }, once built
var activeType = null;    // from ?type=
var activeCluster = null; // { id, slugs }

function setView(view, persist) {
  var prev = document.body.dataset.view;
  document.body.dataset.view = view;
  if (persist !== false) {
    try { localStorage.setItem('publicationView', view); } catch (e) {}
    // So a resize back from mobile restores this choice, not the one at load.
    document.documentElement.dataset.preferredView = view;
    updateURL();
  }
  viewButtons.forEach(function(b) {
    b.setAttribute('aria-pressed', b.dataset.view === view ? 'true' : 'false');
  });
  updateViewButtonLabels();
  // Leaving the network view means it was built.
  if (prev === 'network' && view !== 'network') networkApi.clearSelection();
  // Both branches lay out synchronously, so the view is settled before it paints.
  if (view === 'gallery') {
    layoutMasonry();
  } else if (view === 'network') {
    clearMasonry();
    // The stage sits on the gallery's columns, so write the width first; the graph's
    // ResizeObserver refits it as the stage appears.
    syncPageWidth();
    if (!networkApi) buildNetwork();
    networkApi.filter(matchedSlugs); // catch up with any filter set meanwhile
  }
}
// Clicking the active view button clears the filter; say so, since nothing else does.
function updateViewButtonLabels() {
  var currentView = document.body.dataset.view;
  var hasFilter = searchInput.value.length > 0 || structuredFilterActive();
  viewButtons.forEach(function(b) {
    var v = b.dataset.view;
    var label = v === currentView && hasFilter ? 'Clear search filter'
      : v.charAt(0).toUpperCase() + v.slice(1) + ' view';
    b.setAttribute('aria-label', label);
    b.setAttribute('title', label);
  });
}
/* The CSS boundary, asked as the same media query: innerWidth would count the
   scrollbar, and in between the toggle could be hidden with the network still live. */
var mobileQuery = window.matchMedia('(max-width: {{ _mobile_max }}px)');
function applyResponsiveView() {
  var view = mobileQuery.matches ? 'gallery'
    : document.documentElement.dataset.preferredView || 'gallery';
  if (document.body.dataset.view !== view) setView(view, false);
}
// Clears the search and any type/cluster filter, travelling like any filter change.
function resetFilters() {
  if (!searchInput.value && !structuredFilterActive()) return;
  withTileTransition(function() {
    clearStructuredFilter();
    searchInput.value = '';
    applySearch();
    updateURL();
  });
}
viewButtons.forEach(function(b) {
  b.addEventListener('click', function() {
    var clicked = this.dataset.view;
    if (document.body.dataset.view === clicked) {
      // The active button resets: clear the filter and any node selection.
      resetFilters();
      if (clicked === 'network') networkApi.clearSelection();
    } else {
      withCrossfade(function() { setView(clicked); });
    }
  });
});
setView(document.body.dataset.view, false); // written by the script under <body>
mobileQuery.addEventListener('change', applyResponsiveView);

// ── Bio toggle ──
// `height: auto` does not interpolate, so the travel pins the pixel height, flips
// the state, and hands the height back to the stylesheet when it ends. Never at rest.
var bioToggle = document.querySelector('.bio-toggle');
var bioShell = document.getElementById('bio');
// On cancel too, or an interrupted toggle would leave a pin behind. The clip goes
// with it, since an open shell must not clip the trimmed first line.
function releaseBioHeight(e) {
  if (e.target !== bioShell || e.propertyName !== 'height') return;
  bioShell.style.height = '';
  bioShell.style.overflow = '';
  if (document.body.dataset.view === 'gallery') scheduleWidthPass(); // the scrollbar may go
}
function setBioVisible(visible, persist, animate) {
  if (animate && motionOK()) {
    // scrollHeight ignores the clip, so one read gives both ends of the travel.
    var full = bioShell.scrollHeight;
    bioShell.style.overflow = 'hidden';
    bioShell.style.height = (visible ? 0 : full) + 'px';
    void bioShell.offsetHeight;
    bioShell.style.height = (visible ? full : 0) + 'px';
  } else {
    bioShell.style.height = '';
    bioShell.style.overflow = '';
  }
  document.documentElement.dataset.bioVisible = visible ? '1' : '0';
  bioToggle.setAttribute('aria-expanded', visible ? 'true' : 'false');
  var label = visible ? 'Hide profile' : 'Show profile';
  bioToggle.setAttribute('aria-label', label);
  bioToggle.setAttribute('title', label);
  bioShell.inert = !visible; // keep a collapsed masthead out of the tab order
  if (persist !== false) {
    try { localStorage.setItem('bioVisible', visible ? '1' : '0'); } catch (e) {}
  }
  // A scrollbar appearing or going is a width change; this covers reduced motion,
  // where releaseBioHeight never fires.
  if (document.body.dataset.view === 'gallery') scheduleWidthPass();
}
// Sync the button and inert state to what <head> restored.
setBioVisible(document.documentElement.dataset.bioVisible !== '0', false, false);
bioToggle.addEventListener('click', function() {
  setBioVisible(document.documentElement.dataset.bioVisible === '0', true, true);
});
bioShell.addEventListener('transitionend', releaseBioHeight);
bioShell.addEventListener('transitioncancel', releaseBioHeight);

function normalize(s) {
  return s.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
}

publications.forEach(function(p) {
  p._haystack = normalize(p.getAttribute('data-search') || '');
});

function updateCount(visible) {
  filterCount.textContent = visible === total
    ? 'Showing all ' + total
    : 'Showing ' + visible + ' of ' + total;
}

var activeFilterLabel = null; // the box's text while a type/cluster filter is on

function structuredFilterActive() {
  return activeType !== null || activeCluster !== null;
}

/* Decides which tiles show; never lays out. The caller asks for the pack, since only
   it knows whether it must be synchronous (inside a tile transition it must). */
function applySearch() {
  var structured = structuredFilterActive(); // then the box holds a label, not a query
  var query = structured ? '' : searchInput.value;
  var tokens = query ? normalize(query).split(/\s+/).filter(Boolean) : [];
  var filterActive = tokens.length > 0 || structured;
  var matched = new Set();
  publications.forEach(function(p) {
    var slug = p.dataset.slug;
    var match = tokens.every(function(t) { return p._haystack.indexOf(t) !== -1; })
      && (activeType === null || p.dataset.type === activeType)
      && (activeCluster === null || activeCluster.slugs.has(slug));
    p.style.display = match ? '' : 'none';
    if (match) matched.add(slug);
  });
  // Special cards are chrome, not results.
  specialCards.forEach(function(c) { c.style.display = filterActive ? 'none' : ''; });
  matchedSlugs = filterActive ? matched : null;
  // Only while the graph shows; setView applies matchedSlugs on the way in.
  if (networkApi && document.body.dataset.view === 'network') networkApi.filter(matchedSlugs);
  noResults.hidden = matched.size !== 0;
  updateCount(matched.size);
  updateViewButtonLabels();
}

try {
  var _params = new URLSearchParams(location.search);
  var _initialQ = _params.get('q');
  if (_initialQ) searchInput.value = _initialQ;
  var _initialType = _params.get('type');
  if (_initialType) {
    activeType = _initialType;
    showFilterInInput(TYPE_LABELS[_initialType] || _initialType, false);
  }
  var _initialCluster = _params.get('cluster');
  if (_initialCluster) {
    var _cEl = document.querySelector('[data-action="cluster:' + _initialCluster + '"]');
    if (_cEl && _cEl.dataset.slugs) setClusterFilter(_cEl, _initialCluster, false);
  }
} catch (e) {}
// Packed now, or a shared filter link would paint the whole gallery for a frame.
applySearch();
layoutMasonry();

/* The one place a cluster filter is built. Membership rides on the card's data-slugs,
   from the same network.json the graph reads. */
function setClusterFilter(card, id, focus) {
  activeCluster = { id: id, slugs: new Set(card.dataset.slugs.split(' ')) };
  activeType = null;
  showFilterInInput(card.dataset.filterLabel || '', focus);
}
/* A type/cluster filter is shown as its label in the box, so deleting the text clears
   it. No focus on load, where the reader has touched nothing. */
function showFilterInInput(label, focus) {
  activeFilterLabel = label;
  searchInput.value = label;
  if (focus === false) return;
  // preventScroll, or the focus scroll cancels scrollToResults' glide mid-way.
  searchInput.focus({ preventScroll: true });
  var n = searchInput.value.length;
  try { searchInput.setSelectionRange(n, n); } catch (e) {}
}
function clearStructuredFilter() {
  activeType = null;
  activeCluster = null;
  activeFilterLabel = null;
}
/* A cluster card can be clicked far down the gallery while its results pack at the
   top, so bring the reader up — never down — to the foot of the bio panel (the top
   when it is collapsed), before the filter runs so the tiles rearrange in view.
   Past a screen of travel it cuts rather than glides. */
function scrollToResults() {
  if (document.body.dataset.view !== 'gallery') return;
  var target = 0;
  if (document.documentElement.dataset.bioVisible === '1') {
    target = Math.max(0, window.scrollY + bioShell.getBoundingClientRect().bottom);
  }
  if (target >= window.scrollY) return;
  var far = window.scrollY - target > window.innerHeight;
  window.scrollTo({ top: target, behavior: (far || !motionOK()) ? 'auto' : 'smooth' });
}

/* Action cards: view:<name> switches view, cluster:<id> sets a filter. They hide once
   a filter is on, so clearing goes through Escape and the search box. */
document.querySelectorAll('[data-action]').forEach(function(btn) {
  // The card hides as it filters; a mousedown would leave a stray text selection.
  btn.addEventListener('mousedown', function(e) { e.preventDefault(); });
  btn.addEventListener('click', function() {
    var parts = (btn.dataset.action || '').split(':');
    var verb = parts[0], val = parts[1];
    if (verb === 'view' && val) {
      withCrossfade(function() { setView(val); });
      return;
    }
    if (verb !== 'cluster' || !val || !btn.dataset.slugs) return;
    scrollToResults();
    withTileTransition(function() {
      setClusterFilter(btn, val);
      applySearch();
      updateURL();
    });
  });
});

searchInput.addEventListener('input', function() {
  // Backspacing a type/cluster label keeps the filter; emptying the box or typing
  // anything that no longer prefixes the label releases it into a text search.
  var v = searchInput.value;
  if (structuredFilterActive()
      && (v === '' || activeFilterLabel === null || activeFilterLabel.indexOf(v) !== 0)) {
    clearStructuredFilter();
  }
  searchFromInput();
  scheduleURLUpdate();
});

// "/" focuses the search; Escape resets filters, selection, focus and text selection.
document.addEventListener('keydown', function(e) {
  var t = e.target;
  var typing = t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable);
  if (e.key === '/' && !typing && !e.metaKey && !e.ctrlKey && !e.altKey) {
    e.preventDefault();
    searchInput.focus();
  } else if (e.key === 'Escape') {
    resetFilters();
    if (networkApi) networkApi.clearSelection();
    // Blur outright: Safari's Full Keyboard Access ring ignores `outline: none`.
    var active = document.activeElement;
    if (active && active !== document.body) active.blur();
    var sel = window.getSelection();
    if (sel) sel.removeAllRanges();
  }
});

// The whole card links to its page, sparing inner links and text selection.
publications.forEach(function(p) {
  var href = p.querySelector('h2 a').getAttribute('href');
  p.addEventListener('click', function(e) {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (e.target.closest('a')) return;
    var sel = window.getSelection();
    if (sel && sel.toString().length > 0) return;
    window.location.href = href;
  });
});
