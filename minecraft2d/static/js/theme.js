window.Theme = (function () {
  var elements = [];

  function create(sceneFrame) {
    destroy();
    if (!sceneFrame) return;
    if (document.body.classList.contains('dark-mode')) {
      createNight(sceneFrame);
    } else {
      createDay(sceneFrame);
    }
  }

  function createDay(sceneFrame) {
    var clouds = document.createElement('div');
    clouds.className = 'scene-clouds';
    for (var i = 0; i < 4; i++) {
      var cloud = document.createElement('div');
      clouds.appendChild(cloud);
    }
    sceneFrame.appendChild(clouds);
    elements.push(clouds);
  }

  function createNight(sceneFrame) {
    var starsContainer = document.createElement('div');
    starsContainer.className = 'scene-stars';
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
      starsContainer.appendChild(star);
    }
    sceneFrame.appendChild(starsContainer);
    elements.push(starsContainer);

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
      elements.push(ff);
    }
  }

  function destroy() {
    for (var i = 0; i < elements.length; i++) {
      if (elements[i].parentNode) {
        elements[i].parentNode.removeChild(elements[i]);
      }
    }
    elements = [];
  }

  return { create: create, destroy: destroy };
})();

(function () {
  var themeToggle = document.getElementById('theme-toggle');
  var storageKey = 'minecraft2d-theme';

  function applyTheme(theme) {
    var isDark = theme === 'dark';
    document.body.classList.toggle('dark-mode', isDark);

    if (themeToggle) {
      themeToggle.textContent = isDark ? 'Modo claro' : 'Modo escuro';
      themeToggle.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    }

    window.Theme.create(document.getElementById('scene-frame'));
  }

  var saved = localStorage.getItem(storageKey);
  applyTheme(saved === 'dark' ? 'dark' : 'light');

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var next = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
      localStorage.setItem(storageKey, next);
      applyTheme(next);
    });
  }
})();
