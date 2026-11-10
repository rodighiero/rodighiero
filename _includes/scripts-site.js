// Shared by both layouts, each inlining it in its own <script>: kept apart from the
// page's own script, so an error there cannot take the mode toggle down with it.

// Lazy images inside `root` go eager: homepage thumbnails, figures before printing.
function promoteLazyImages(root) {
  (root || document).querySelectorAll('img[loading="lazy"]').forEach(function(img) {
    img.loading = 'eager';
  });
}

/* Invoker commands: a button names its target and verb in the markup (commandfor,
   command) and the target hears a `command` event, so a handler lives on the element it
   acts on. Browsers from before the feature (Chrome 135, Firefox 144, Safari 26.2) get
   the same event dispatched from the click. Custom verbs only, prefixed `--`. */
if (!('commandForElement' in HTMLButtonElement.prototype)) {
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('button[commandfor][command]');
    if (!btn || btn.disabled) return;
    var target = document.getElementById(btn.getAttribute('commandfor'));
    if (!target) return;
    var ev = new Event('command', { cancelable: true });
    ev.command = btn.getAttribute('command');
    ev.source = btn;
    target.dispatchEvent(ev);
  });
}

// Mode toggle
(function() {
  var html = document.documentElement;
  // A manual choice retints the browser toolbar too: the two theme-color metas in
  // site-head.html follow only the system setting, so both take the page's own background.
  function syncThemeColor() {
    var bg = getComputedStyle(document.body).backgroundColor;
    document.querySelectorAll('meta[name="theme-color"]').forEach(function(m) { m.content = bg; });
  }
  if (html.classList.contains('dark') || html.classList.contains('light')) syncThemeColor();
  document.querySelector('.mode-toggle').addEventListener('click', function() {
    var isDark = html.classList.contains('dark') ||
      (!html.classList.contains('light') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    html.classList.remove('dark', 'light');
    var next = isDark ? 'light' : 'dark';
    html.classList.add(next);
    syncThemeColor();
    try { localStorage.setItem('colorScheme', next); } catch (e) {}
  });
})();

/* Copy the formatted citation: the button's --copy command lands on the .cite-data it
   names. Unguarded: #live-msg is in both layouts, and every .cite-btn is emitted with
   its .cite-data. */
(function() {
  var liveMsg = document.getElementById('live-msg');
  document.querySelectorAll('.cite-btn').forEach(function(btn) {
    var label = btn.textContent;
    var resetTimer;
    var data = document.getElementById(btn.getAttribute('commandfor'));
    data.addEventListener('command', async function(e) {
      if (e.command !== '--copy') return;
      clearTimeout(resetTimer);
      btn.disabled = true;
      btn.classList.remove('copied');
      try {
        await navigator.clipboard.writeText(data.textContent.trim());
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        liveMsg.textContent = 'Citation copied to clipboard.';
      } catch (e) {
        // Includes browsers where the Clipboard API is unavailable.
        btn.textContent = 'Copy failed';
        liveMsg.textContent = 'Could not copy citation. Please try again.';
      } finally {
        btn.disabled = false;
        resetTimer = setTimeout(function() {
          btn.textContent = label;
          btn.classList.remove('copied');
          liveMsg.textContent = '';
        }, 1500);
      }
    });
  });
})();
