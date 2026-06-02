function initTheme() {
  var themeToggle = document.getElementById('theme-toggle');
  var storageKey = 'minecraft2d-theme';

  function applyTheme(theme) {
    var isDark = theme === 'dark';

    if (isDark) {
      document.body.className = document.body.className + ' dark-mode';
    } else {
      document.body.className = document.body.className.replace(' dark-mode', '');
    }

    if (themeToggle) {
      themeToggle.textContent = isDark ? 'Modo claro' : 'Modo escuro';
      themeToggle.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    }

    if (window.Night) {
      if (isDark) {
        var sf = document.getElementById('scene-frame');
        if (sf) { window.Night.create(sf); }
      } else {
        window.Night.destroy();
      }
    }
  }

  function getInitialTheme() {
    var saved = localStorage.getItem(storageKey);
    if (saved === 'dark' || saved === 'light') {
      return saved;
    }
    return 'light';
  }

  applyTheme(getInitialTheme());

  if (!themeToggle) {
    return;
  }

  themeToggle.onclick = function () {
    var nextTheme = document.body.className.indexOf('dark-mode') !== -1 ? 'light' : 'dark';
    localStorage.setItem(storageKey, nextTheme);
    applyTheme(nextTheme);
  };
}

initTheme();
