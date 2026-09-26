// The publication page's print path, inlined by publication.html after scripts-site.js
// (whose promoteLazyImages it calls).
/* Print only once the lazy figures have loaded: Cmd/Ctrl+P and the Print button wait
   here, beforeprint covers the browser's own menu. false: nothing to wait for. */
function printWhenImagesReady() {
  var imgs = Array.from(document.querySelectorAll('img')).filter(function(i) { return !i.complete || i.naturalWidth === 0; });
  if (imgs.length === 0) return false;
  promoteLazyImages();
  Promise.all(imgs.map(function(img) {
    return new Promise(function(resolve) {
      img.addEventListener('load', resolve, { once: true });
      img.addEventListener('error', resolve, { once: true });
      setTimeout(resolve, 5000);
    });
  })).then(function() { window.print(); });
  return true;
}

window.addEventListener('beforeprint', function() { promoteLazyImages(); });

window.addEventListener('keydown', function(e) {
  if (e.key.toLowerCase() !== 'p' || !(e.metaKey || e.ctrlKey) || e.shiftKey || e.altKey) return;
  if (printWhenImagesReady()) e.preventDefault();
});

document.querySelectorAll('.print-btn').forEach(function(btn) {
  btn.addEventListener('click', function() { if (!printWhenImagesReady()) window.print(); });
});
