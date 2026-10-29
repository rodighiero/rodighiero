// The publication page's print path, inlined by publication.html after scripts-site.js
// (whose promoteLazyImages it calls).
/* Print only once the lazy figures have loaded: Cmd/Ctrl+P and the Print button wait
   here, beforeprint covers the browser's own menu. false: nothing to wait for. */
var pendingPrint = null;
function printWhenImagesReady() {
  if (pendingPrint) return true;
  // complete includes failed images: they have already settled, so don't wait again.
  var imgs = Array.from(document.querySelectorAll('img')).filter(function(i) { return !i.complete; });
  if (imgs.length === 0) return false;
  pendingPrint = Promise.all(imgs.map(function(img) {
    return new Promise(function(resolve) {
      function done() {
        clearTimeout(timer);
        img.removeEventListener('load', done);
        img.removeEventListener('error', done);
        resolve();
      }
      img.addEventListener('load', done);
      img.addEventListener('error', done);
      var timer = setTimeout(done, 5000);
    });
  })).then(function() { pendingPrint = null; window.print(); });
  // Register listeners first, including for images already in the browser's cache.
  promoteLazyImages();
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
