/* Stops the spinner nice-ui.css draws behind a resource view's frame. Not every
 * view paints an opaque page over it — DataTables leaves its body transparent.
 * Scripts arrive at the end of the page, so a frame may already have loaded.
 */
(function () {
  'use strict';
  var frames = document.querySelectorAll('iframe[data-module="data-viewer"]');
  Array.prototype.forEach.call(frames, function (frame) {
    function loaded() { frame.classList.add('is-loaded'); }
    frame.addEventListener('load', loaded);
    try {
      var doc = frame.contentDocument;
      if (doc && doc.readyState === 'complete' && doc.URL !== 'about:blank') loaded();
    } catch (e) {
      loaded();
    }
  });
})();
