// Shared by both layouts, each inlining it in its own <script>: kept apart from the
// page's own script, so an error there cannot take the mode toggle down with it.

// Lazy images inside `root` go eager: homepage thumbnails, figures before printing.
function promoteLazyImages(root) {
  (root || document).querySelectorAll('img[loading="lazy"]').forEach(function(img) {
    img.loading = 'eager';
  });
}

// Mode toggle. The state is <meta name="color-scheme"> (site-scheme.html): `light dark`
// follows the system, `dark` or `light` is the reader's override, stored under colorScheme.
(function() {
  var meta = document.querySelector('meta[name="color-scheme"]');
  var systemDark = window.matchMedia('(prefers-color-scheme: dark)');
  // The two theme-color metas in site-head.html follow only the system setting, so an
  // override gives both the page's own background, and its removal gives them back.
  var themeMetas = Array.prototype.slice.call(document.querySelectorAll('meta[name="theme-color"]'));
  var themeDefaults = themeMetas.map(function(m) { return m.content; });
  function apply(scheme) {
    meta.content = scheme || 'light dark';
    var bg = scheme && getComputedStyle(document.body).backgroundColor;
    themeMetas.forEach(function(m, i) { m.content = bg || themeDefaults[i]; });
  }
  function override() { return meta.content === 'dark' || meta.content === 'light' ? meta.content : null; }
  if (override()) apply(override());
  document.querySelector('.mode-toggle').addEventListener('click', function() {
    var system = systemDark.matches ? 'dark' : 'light';
    // The opposite of what is on screen. Landing back on the system's own scheme is an
    // undo, so the override is dropped rather than stored: a stored match would pin the
    // page against the system's next change. Judged only here, never afterwards — an
    // override the system later comes to agree with is kept.
    var next = (override() || system) === 'dark' ? 'light' : 'dark';
    var stored = next === system ? null : next;
    apply(stored);
    try {
      if (stored) localStorage.setItem('colorScheme', stored);
      else localStorage.removeItem('colorScheme');
    } catch (e) {}
  });
  // A choice made in another tab.
  window.addEventListener('storage', function(e) {
    if (e.key !== 'colorScheme' && e.key !== null) return;
    apply(e.newValue === 'dark' || e.newValue === 'light' ? e.newValue : null);
  });
})();

/* Copy the formatted citation. Unguarded: #live-msg is in both layouts, and every
   .cite-btn is emitted beside its .cite-data. */
(function() {
  var liveMsg = document.getElementById('live-msg');
  // VoiceOver skips a message identical to the region's last one, even after it was
  // emptied; a trailing no-break space makes a repeat differ without being read aloud.
  var lastMsg = '';
  function announce(msg) {
    if (msg === lastMsg) msg += '\u00A0';
    liveMsg.textContent = lastMsg = msg;
  }
  document.querySelectorAll('.cite-btn').forEach(function(btn) {
    var label = btn.textContent;
    var resetTimer;
    btn.addEventListener('click', async function() {
      var data = btn.closest('article').querySelector('.cite-data');
      clearTimeout(resetTimer);
      btn.classList.remove('copied');
      try {
        await navigator.clipboard.writeText(data.textContent.trim());
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        announce('Citation copied to clipboard.');
      } catch (e) {
        // Includes browsers where the Clipboard API is unavailable.
        btn.textContent = 'Copy failed';
        announce('Could not copy citation. Please try again.');
      } finally {
        resetTimer = setTimeout(function() {
          btn.textContent = label;
          btn.classList.remove('copied');
          liveMsg.textContent = '';
        }, 1500);
      }
    });
  });
})();
