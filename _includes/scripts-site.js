// Shared by both layouts, each inlining it in its own <script>: kept apart from the
// page's own script, so an error there cannot take the mode toggle down with it.

// Lazy images inside `root` go eager: homepage thumbnails, figures before printing.
function promoteLazyImages(root) {
  (root || document).querySelectorAll('img[loading="lazy"]').forEach(function(img) {
    img.loading = 'eager';
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

/* Copy the formatted citation. Unguarded: #live-msg is in both layouts, and every
   .cite-btn is emitted beside its .cite-data. */
(function() {
  var liveMsg = document.getElementById('live-msg');
  document.querySelectorAll('.cite-btn').forEach(function(btn) {
    var label = btn.textContent;
    btn.addEventListener('click', function() {
      var data = btn.closest('article').querySelector('.cite-data');
      navigator.clipboard.writeText(data.textContent.trim()).then(function() {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        liveMsg.textContent = 'Citation copied to clipboard.';
        setTimeout(function() {
          btn.textContent = label;
          btn.classList.remove('copied');
          liveMsg.textContent = '';
        }, 1500);
      });
    });
  });
})();
