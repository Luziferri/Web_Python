// Cenário noturno: estrelas e pirilampos (ativado no modo escuro).
window.Night = (function () {
  var nightElements = null;

  function create(sceneFrame) {
    if (!sceneFrame || nightElements) return;

    // Contentor para as estrelas (usa box-shadow para evitar centenas de elementos DOM).
    var container = document.createElement('div');
    container.className = 'scene-stars';

    // Gera 100 estrelas com posições e tamanhos aleatórios na área do céu.
    var starShadows = [];
    for (var i = 0; i < 100; i++) {
      var x = Math.random() * 1000 + 20;
      var y = Math.random() * 280 + 20;
      var size = Math.random() * 2 + 0.5;
      starShadows.push(x + 'px ' + y + 'px 0 ' + size + 'px rgba(255,255,255,' + (Math.random() * 0.6 + 0.4) + ')');
    }
    container.style.boxShadow = starShadows.join(', ');
    container.style.animation = 'star-twinkle ' + (Math.random() * 2 + 2) + 's ease-in-out infinite alternate';
    sceneFrame.appendChild(container);

    // Gera 10 pirilampos com posições, tamanhos e durações de animação aleatórias.
    var fireflies = [];
    for (var i = 0; i < 10; i++) {
      var ff = document.createElement('div');
      ff.className = 'firefly';
      ff.style.left = (Math.random() * 60 + 20) + '%';
      ff.style.top = (Math.random() * 40 + 15) + '%';
      ff.style.width = (Math.random() * 4 + 3) + 'px';
      ff.style.height = ff.style.width;
      ff.style.animationDuration = (Math.random() * 4 + 4) + 's';
      ff.style.animationDelay = (Math.random() * 4) + 's';
      ff.style.animationName = 'firefly-float';
      ff.style.animationIterationCount = 'infinite';
      ff.style.animationTimingFunction = 'ease-in-out';
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
