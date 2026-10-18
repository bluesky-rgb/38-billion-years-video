(function () {
  var d = document.getElementById('player'), v = document.getElementById('pv');
  function close() { v.pause(); v.removeAttribute('src'); v.load(); if (d.open) d.close(); }
  document.querySelectorAll('.play').forEach(function (b) {
    b.addEventListener('click', function () {
      document.getElementById('pt').textContent = b.dataset.title;
      document.getElementById('py').textContent = '和你的关系：' + b.dataset.you;
      v.src = b.dataset.src;
      if (d.showModal) d.showModal(); else d.setAttribute('open', '');
      var p = v.play(); if (p && p.catch) p.catch(function () {});
    });
  });
  document.getElementById('pc').addEventListener('click', close);
  d.addEventListener('close', function () { v.pause(); });
  d.addEventListener('click', function (e) { if (e.target === d) close(); });
})();
