// Cenário noturno: estrelas e pirilampos (ativado no modo escuro).
window.Night = (function () {
  var nightElements = null;

  function create(sceneFrame) {
    if (!sceneFrame || nightElements) return;

    var container = document.createElement('div');
    container.className = 'scene-stars';

    for (var i = 0; i < 100; i++) {
      var star = document.createElement('div');
      star.className = 'scene-star';
      var size = Math.random() * 3 + 1;
      star.style.left = (Math.random() * 1100 + 20) + 'px';
      star.style.top = (Math.random() * 300 + 20) + 'px';
      star.style.width = size + 'px';
      star.style.height = size + 'px';
      star.style.animation = 'star-twinkle ' + (Math.random() * 2 + 1.5) + 's ease-in-out infinite alternate';
      star.style.animationDelay = (Math.random() * 3) + 's';
      container.appendChild(star);
    }
    sceneFrame.appendChild(container);

    var fireflies = [];
    for (var i = 0; i < 10; i++) {
      var ff = document.createElement('div');
      ff.className = 'firefly';
      ff.style.left = (Math.random() * 60 + 20) + '%';
      ff.style.top = (Math.random() * 40 + 15) + '%';
      ff.style.width = (Math.random() * 4 + 3) + 'px';
      ff.style.height = ff.style.width;
      ff.style.animation = 'firefly-float ' + (Math.random() * 4 + 4) + 's ease-in-out infinite';
      ff.style.animationDelay = (Math.random() * 4) + 's';
      sceneFrame.appendChild(ff);
      fireflies.push(ff);
    }

    nightElements = { container: container, fireflies: fireflies };
  }

  function destroy() {
    if (!nightElements) return;
    if (nightElements.container && nightElements.container.parentNode) {
      nightElements.container.parentNode.removeChild(nightElements.container);
    }
    for (var i = 0; i < nightElements.fireflies.length; i++) {
      if (nightElements.fireflies[i].parentNode) {
        nightElements.fireflies[i].parentNode.removeChild(nightElements.fireflies[i]);
      }
    }
    nightElements = null;
  }

  return { create: create, destroy: destroy };
})();
