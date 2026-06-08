// Tudo começa quando o DOM está carregado (dentro da matéria: Lab 04 - DOMContentLoaded).
function initGame() {
  // Guardar referências a elementos do DOM (dentro da matéria: Lab 05 - getElementById).
  var steeve = document.getElementById('steeve');
  var sceneFrame = document.getElementById('scene-frame');
  var sceneGrid = document.getElementById('scene-grid');
  var inventoryMain = document.getElementById('inventory-main');
  var inventoryHotbar = document.getElementById('inventory-hotbar');
  var slotsGrid = document.getElementById('slots-grid');
  var logsList = document.getElementById('logs-list');
  var buildingButtons = document.getElementsByClassName('building-option');

  // Variáveis de estado: tamanho do tile, colunas, posição do jogador, construção selecionada.
  // Uso de variáveis: Lab 04 ✅.
  var baseTileSize = 96;
  var sceneScale = 1 / 3;
  var tileSize = Math.round(baseTileSize * sceneScale);
  var mapColumns = 12;
  var minimumColumns = 12;
  var mapRows = 2;
  var selectedBuildingKey = 'cabana';
  // localStorage para persistir posição entre recarregamentos (dentro da matéria: Lab 06 - LocalStorage).
  var steeveTile = parseInt(localStorage.getItem('steeve-tile'), 10) || 2;
  var walkLimit = mapColumns - 1;
  var latestStatePayload = null;
  var previousInventory = {
    wood: -1,
    stone: -1,
    iron: -1
  };

  function scaleSceneValue(value) {
    return Math.round(value * tileSize / baseTileSize);
  }

  // Ajusta tamanho base dos tiles conforme a largura do ecrã.
  // Media queries com JS (fora da matéria: window.innerWidth não foi ensinado nos labs de JS).
  function getBaseTileSize() {
    if (window.innerWidth <= 720) {
      return Math.max(24, Math.round(baseTileSize * sceneScale * 0.75));
    }

    return Math.round(baseTileSize * sceneScale);
  }

  // Adapta o número de colunas ao espaço disponível no ecrã.
  // (fora da matéria: clientWidth / getBoundingClientRect não foram ensinados nos labs).
  function updateSceneMetrics() {
    var frameWidth = 0;
    var computedColumns = 0;

    if (!sceneFrame) {
      tileSize = getBaseTileSize();
      walkLimit = mapColumns - 1;
      return;
    }

    frameWidth = sceneFrame.clientWidth || sceneFrame.getBoundingClientRect().width || window.innerWidth;

    if (window.innerWidth <= 430) {
      var maxMin = frameWidth / minimumColumns;
      tileSize = maxMin > 32 ? maxMin : 32;
      tileSize = parseInt(tileSize, 10);
    } else {
      tileSize = getBaseTileSize();
    }

    computedColumns = parseInt(frameWidth / tileSize, 10);
    if (frameWidth % tileSize !== 0) { computedColumns = computedColumns + 1; }
    mapColumns = minimumColumns > computedColumns ? minimumColumns : computedColumns;
    walkLimit = mapColumns - 1;

    if (steeveTile > walkLimit) {
      steeveTile = walkLimit;
    }

    sceneFrame.style.setProperty('--scene-tile-size', tileSize + 'px');
  }

  // Desenha o cenário (tiles de relva, terra e pedras) no ecrã.
  // createElement / appendChild / innerHTML / className / setAttribute: Lab 05 ✅.
  // onclick em elementos dinâmicos: Lab 05 ✅.
  // fetch API + promises: fora da matéria (Lab 04-06 não ensinam fetch nem promises).
  function buildScene(stones) {
    var row;
    var column;
    var stoneByColumn = {};

    if (!sceneGrid) {
      return;
    }

    updateSceneMetrics();

    sceneGrid.innerHTML = '';

    for (var si = 0; si < (stones || []).length; si++) {
      var stone = (stones || [])[si];
      stoneByColumn[parseInt(stone.column, 10)] = stone;
    }

    for (row = 0; row < mapRows; row += 1) {
      for (column = 0; column < mapColumns; column += 1) {
        var tile = document.createElement('img');
        var isGrassRow = row === mapRows - 1;
        var isDirtRow = row === 0;
        var stone = isDirtRow ? stoneByColumn[column] : null;

        tile.className = 'scene-tile';
        tile.src = isGrassRow ? '/static/img/relva.png' : (stone && stone.available ? '/static/img/stone.png' : '/static/img/terra.png');
        tile.alt = isGrassRow ? 'Relva' : (stone && stone.available ? 'Pedra' : 'Terra');
        tile.setAttribute('data-col', '' + column);
        tile.style.left = (column * tileSize) + 'px';
        tile.style.bottom = (row * tileSize) + 'px';
        tile.style.width = tileSize + 'px';
        tile.style.height = tileSize + 'px';

        // Clique para minerar pedra (fetch/post: fora da matéria dos labs de JS).
        if (stone && stone.available) {
          tile.className = 'scene-tile scene-stone';
          tile.style.zIndex = '2';
          tile.style.pointerEvents = 'auto';
          tile.setAttribute('draggable', 'false');
          tile.setAttribute('tabindex', '-1');

          tile.onclick = function (ev) {
            var clicked = ev.target;
            if (!clicked) return;
            var col = parseInt(clicked.getAttribute('data-col'), 10);

            if (clicked.getAttribute('data-mined')) return;

            if (!canInteractWithColumn(col)) {
              alert('Estás muito longe da pedra. Aproxima-te 1 tile.');
              return;
            }

            clicked.setAttribute('data-mined', '1');
            clicked.style.pointerEvents = 'none';

            requestJson('/api/mine-stone', { column: col })
              .then(function (payload) {
                if (!payload.ok) {
                  alert(payload.payload.message || 'Não foi possível minerar a pedra.');
                  clicked.setAttribute('data-mined', '');
                  clicked.style.pointerEvents = 'auto';
                  return;
                }

                clicked.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
                clicked.style.opacity = '0.35';
                clicked.style.transform = 'translateY(-12px) scale(0.95)';

                setTimeout(function () {
                  refreshState();
                }, 250);
              }).catch(function () {
                alert('Erro de rede ao minerar a pedra.');
                clicked.setAttribute('data-mined', '');
                clicked.style.pointerEvents = 'auto';
              });
          };
        }

        // Contador visual de cooldown da pedra (criação dinâmica de elementos: Lab 05 ✅).
        if (stone && !stone.available) {
          var stoneBadge = document.createElement('div');
          stoneBadge.className = 'stone-timer-badge';
          stoneBadge.setAttribute('data-col', '' + column);
          stoneBadge.style.position = 'absolute';
          stoneBadge.style.left = (column * tileSize + scaleSceneValue(6)) + 'px';
          stoneBadge.style.bottom = (row * tileSize + (tileSize * 0.9) + scaleSceneValue(2)) + 'px';
          stoneBadge.style.zIndex = '3';
          stoneBadge.style.background = 'rgba(0,0,0,0.6)';
          stoneBadge.style.color = '#fff';
          stoneBadge.style.padding = scaleSceneValue(4) + 'px ' + scaleSceneValue(6) + 'px';
          stoneBadge.style.borderRadius = '6px';
          stoneBadge.style.fontSize = Math.max(10, scaleSceneValue(12)) + 'px';
          stoneBadge.textContent = '' + (stone.seconds_left || 0);
          sceneGrid.appendChild(stoneBadge);
        }

        sceneGrid.appendChild(tile);
      }
    }
  }

  // Animação visual para remover elementos (style.opacity/transform: Lab 04 ✅).
  // parentNode.removeChild: Lab 05 ✅.
  function deleteItem(element, options) {
    var node = element;
    var delay = 0;

    if (!node) {
      return;
    }

    options = options || {};
    delay = typeof options.delay === 'number' ? options.delay : 250;

    node.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    node.style.opacity = '0';
    node.style.transform = 'scale(0.9)';

    setTimeout(function () {
      if (node.parentNode) {
        node.parentNode.removeChild(node);
      }
    }, delay);
  }

  // Posiciona o Steve visualmente no tile correto (style.left/bottom: Lab 04 ✅).
  // localStorage: Lab 06 ✅.
  function setSteevePosition() {
    if (!steeve) {
      return;
    }

    if (steeveTile < 0) {
      steeveTile = 0;
    }

    if (steeveTile > walkLimit) {
      steeveTile = walkLimit;
    }

    steeve.style.left = (steeveTile * tileSize) + 'px';
    steeve.style.bottom = ((tileSize * mapRows) - parseInt(tileSize / 12, 10)) + 'px';
    steeve.style.width = 'auto';
    steeve.style.height = (tileSize * 3) + 'px';
    localStorage.setItem('steeve-tile', '' + steeveTile);

    //localização do machado
    var axeEl = document.getElementById('steeve-axe');
    if (axeEl) {
      axeEl.style.left = (steeveTile * tileSize + Math.round(tileSize * 1.2)) + 'px';
      axeEl.style.bottom = (tileSize * mapRows + Math.round(tileSize * 1)) + 'px';
    }
  }

  // Mostra ou esconde o machado ao lado do Steve (funcionalidade extra do projeto).
  // createElement / className / appendChild / style: Lab 05 ✅.
  function renderAxe(hasAxe, axeLevel) {
    var axeEl = document.getElementById('steeve-axe');
    if (!hasAxe) {
      if (axeEl) { axeEl.style.display = 'none'; }
      return;
    }
    if (!axeEl) {
      axeEl = document.createElement('div');
      axeEl.id = 'steeve-axe';
      axeEl.className = 'steeve-axe-badge';
      if (sceneFrame) { sceneFrame.appendChild(axeEl); }
    }
    var axeImg = '/static/img/machado.png';
    if (axeLevel >= 4) {
      axeImg = '/static/img/machado_diamante.png';
    } else if (axeLevel >= 3) {
      axeImg = '/static/img/machado_ferro.png';
    } else if (axeLevel >= 2) {
      axeImg = '/static/img/machado_pedra.png';
    }
    axeEl.style.display = 'flex';
    axeEl.innerHTML = '<img src=\"' + axeImg + '\" alt=\"Machado\" class=\"axe-icon\"><span class=\"axe-level\">Nv.' + axeLevel + '</span>';
    axeEl.style.left = (steeveTile * tileSize + Math.round(tileSize * 2.8)) + 'px';
    axeEl.style.bottom = (tileSize * mapRows + Math.round(tileSize * 2.0)) + 'px';
  }

  // _parseDatetime: ❌ fora (labs nao usam timestamps). Necessario para calcular tempo restante.
  function _parseDatetime(str) {
    if (!str) { return 0; }
    var parts = str.split('T');
    var dateParts = parts[0].split('-');
    var timeParts = (parts[1] || '00:00:00').split(':');
    var year = parseInt(dateParts[0], 10) || 0;
    var month = (parseInt(dateParts[1], 10) - 1) || 0;
    var day = parseInt(dateParts[2], 10) || 1;
    var hour = parseInt(timeParts[0], 10) || 0;
    var minute = parseInt(timeParts[1], 10) || 0;
    // strip any fractional seconds or timezone suffix (e.g. "05.123Z" or "05+01:00")
    var secPart = (timeParts[2] || '0').toString().replace(/[^0-9].*$/, '');
    var second = parseInt(secPart, 10) || 0;

    // Use UTC to match server's datetime.utcnow() values
    return Date.UTC(year, month, day, hour, minute, second);
  }

  // Move o Steve para a esquerda ou direita.
  // classList.add/remove: Lab 05 ✅.
  function moveSteeve(direction) {
    steeveTile += direction;

    if (steeve) {
      if (direction < 0) {
        steeve.classList.add('facing-left');
      } else {
        steeve.classList.remove('facing-left');
      }
    }

    setSteevePosition();
  }

  function getPlayerTile() {
    return steeveTile;
  }

  // Atualiza todos os timers de slots que tenham `data-ready-at` sem refazer o estado do servidor.
  // Mantém a contagem regressiva fluida entre refreshes do payload.
  function updateSlotTimers() {
    var states = document.getElementsByClassName('slot-state');
    for (var i = 0; i < states.length; i++) {
      var el = states[i];
      var secondsLeft = parseInt(el.getAttribute('data-seconds-left'), 10);
      if (isNaN(secondsLeft)) continue;
      if (secondsLeft <= 0) {
        el.removeAttribute('data-seconds-left');
        continue;
      }
      secondsLeft -= 1;
      el.setAttribute('data-seconds-left', '' + secondsLeft);
      var mins = Math.floor(secondsLeft / 60);
      var secs = secondsLeft % 60;
      var baseLabel = el.classList.contains('working') ? 'A processar' : 'A construir';
      el.textContent = baseLabel + ' (' + (mins > 0 ? mins + 'm ' : '') + secs + 's)';
      if (secondsLeft === 0) {
        // remove attribute; server refresh will update real state
        el.removeAttribute('data-seconds-left');
      }
    }
  }

  // Verifica se o jogador está a 1 tile de distância (dentro da matéria: lógica JS básica ✅).
  function canInteractWithColumn(column) {
    var diff = getPlayerTile() - column;
    return (diff >= -1 && diff <= 1);
  }

  // Faz um pedido POST ao servidor com body JSON.
  // fetch + .then() + .catch() + promises:
  //   Fora da matéria (Lab 04-06 não ensinam fetch nem promises; o projeto final menciona Fetch API).
  function requestJson(url, body) {
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body || {})
    }).then(function (response) {
      return response.json().then(function (payload) {
        return { ok: response.ok, payload: payload };
      });
    });
  }

  function formatState(state) {
    if (state === 'building') {
      return 'A construir';
    }

    if (state === 'ready') {
      return 'Pronto';
    }

    if (state === 'working') {
      return 'A processar';
    }

    if (state === 'collectable') {
      return 'Concluída';
    }

    return 'Vazio';
  }

  // Renderiza o histórico de ações (createElement, appendChild, textContent: Lab 05 ✅).
  // new Date() / getHours / getMinutes: Lab 04 ✅.
  function renderLogs(logs) {
    if (!logsList) {
      return;
    }

    logsList.innerHTML = '';

    for (var li = 0; li < logs.length; li++) {
      var log = logs[li];
      var card = document.createElement('article');
      var message = document.createElement('p');
      var time = document.createElement('time');
      var d = new Date(log.created_at);
      var h = d.getHours();
      var m = d.getMinutes();

      card.className = 'log-card';
      message.textContent = log.message;
      time.textContent = (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;

      card.appendChild(message);
      card.appendChild(time);
      logsList.appendChild(card);
    }
  }

  // Cria os cartões de slot de construção dinamicamente.
  // createElement / className / textContent / appendChild / onclick: Lab 05 ✅.
  // for loop: Lab 04 ✅.
  // hasAxe / axeLevel: ✅ (parametros de funcao). Funcionalidade extra do projeto (machado).
  function renderSlots(slots, buildings, hasAxe, axeLevel) {
    if (!slotsGrid) {
      return;
    }

    slotsGrid.innerHTML = '';

    for (var sli = 0; sli < slots.length; sli++) {
      var slot = slots[sli];
      var building = slot.building_type ? buildings[slot.building_type] : null;
      var card = document.createElement('article');
      var header = document.createElement('div');
      var title = document.createElement('strong');
      var state = document.createElement('span');
      var meta = document.createElement('div');
      var actionBox = document.createElement('div');

      card.className = 'slot-card';
      card.setAttribute('data-slot-id', slot.id);

      header.className = 'slot-title';
      title.textContent = 'Slot ' + slot.slot_number;
      state.className = 'slot-state ' + slot.state;
      state.textContent = formatState(slot.state);

      if ((slot.state === 'working' || slot.state === 'building') && typeof slot.seconds_left !== 'undefined') {
        // usa seconds_left enviado pelo servidor (inteiro em segundos)
        var diff = Math.max(0, parseInt(slot.seconds_left, 10) || 0);
        state.setAttribute('data-seconds-left', '' + diff);
        var mins = Math.floor(diff / 60);
        var secs = diff % 60;
        var baseLabel = slot.state === 'working' ? 'A processar' : 'A construir';
        state.textContent = baseLabel + ' (' + (mins > 0 ? mins + 'm ' : '') + secs + 's)';
      }

      header.appendChild(title);
      header.appendChild(state);
      card.appendChild(header);

      meta.className = 'slot-meta';
      meta.textContent = building ? building.name + ' · ' + building.description : 'Sem construção';
      card.appendChild(meta);

      if (slot.state === 'ready' && slot.building_type === 'cabana') {
        var costWood, costStone, costIron;
        if (axeLevel === 0) {
          costWood = 15; costStone = 0; costIron = 0;
        } else if (axeLevel === 1) {
          costWood = 20; costStone = 20; costIron = 0;
        } else {
          costWood = 15 + (axeLevel * 8);
          costStone = 8 + (axeLevel * 5);
          costIron = 3 + (axeLevel - 1) * 2;
        }
        var costEl = document.createElement('div');
        costEl.className = 'slot-cost';
        var costParts = [];
        costParts.push(costWood + ' madeira');
        if (costStone > 0) costParts.push(costStone + ' pedra');
        if (costIron > 0) costParts.push(costIron + ' ferro');
        costEl.textContent = 'Custo: ' + costParts.join(' · ');
        card.appendChild(costEl);
      }

      actionBox.className = 'slot-actions';

      (function (slotId, slotBuildingType) {
        if (slot.state === 'empty') {
          var buildButton = document.createElement('button');
          buildButton.className = 'slot-action build';
          buildButton.textContent = 'Construir aqui';
          buildButton.onclick = function () {
            buildSlot(slotId);
          };
          actionBox.appendChild(buildButton);
        }

        if (slot.state === 'ready') {
          var taskText = 'Iniciar tarefa';
          if (slotBuildingType === 'cabana') {
            taskText = hasAxe ? 'Upgrade Machado Nivel ' + (axeLevel + 1) : 'Fabricar Machado';
          }
          var taskButton = document.createElement('button');
          taskButton.className = 'slot-action task';
          taskButton.textContent = taskText;
          taskButton.onclick = function () {
            startTask(slotId);
          };
          actionBox.appendChild(taskButton);
        }

        if (slot.state === 'collectable') {
          var collectText = 'Recolher recompensa';
          if (slotBuildingType === 'cabana') {
            collectText = hasAxe ? 'Recolher Upgrade' : 'Recolher Machado';
          }
          var collectButton = document.createElement('button');
          collectButton.className = 'slot-action collect';
          collectButton.textContent = collectText;
          collectButton.onclick = function () {
            collectTask(slotId);
          };
          actionBox.appendChild(collectButton);
        }
      })(slot.id, slot.building_type);

      card.appendChild(actionBox);
      slotsGrid.appendChild(card);
    }
  }

  // Cria uma slot visual do inventário (createElement / className / appendChild: Lab 05 ✅).
  function createInventorySlot(item) {
    var slot = document.createElement('div');
    slot.className = 'inventory-slot';

    if (!item || item.amount <= 0) {
      return slot;
    }

    var itemNode = document.createElement('div');
    var icon = document.createElement('img');
    var amount = document.createElement('span');

    itemNode.className = 'inventory-item';
    if (item.changed) {
      itemNode.classList.add('item-enter');
    }

    icon.src = item.icon;
    icon.alt = item.label;
    icon.setAttribute('draggable', 'false');

    amount.className = 'inventory-number';
    amount.textContent = '' + item.amount;

    itemNode.appendChild(icon);
    itemNode.appendChild(amount);
    slot.appendChild(itemNode);
    return slot;
  }

  // Organiza e desenha os recursos do inventário no ecrã.
  // createElement / appendChild / innerHTML / classList: Lab 05 ✅.
  // for loop: Lab 04 ✅.
  function renderInventory(user) {
    var totalMainSlots = 27;
    var totalHotbarSlots = 9;
    var items = [
      {
        key: 'wood',
        label: 'Madeira',
        amount: parseInt(user.wood || 0, 10),
        icon: '/static/img/madeira.png'
      },
      {
        key: 'stone',
        label: 'Pedra',
        amount: parseInt(user.stone || 0, 10),
        icon: '/static/img/pedra.png'
      },
      {
        key: 'iron',
        label: 'Ferro',
        amount: parseInt(user.iron || 0, 10),
        icon: '/static/img/iron.png'
      }
    ];
    var index;

    if (!inventoryMain || !inventoryHotbar) {
      return;
    }

    inventoryMain.innerHTML = '';
    inventoryHotbar.innerHTML = '';

    for (var ii = 0; ii < items.length; ii++) {
      var item = items[ii];
      item.changed = previousInventory[item.key] !== item.amount;
      previousInventory[item.key] = item.amount;
    }

    for (index = 0; index < totalMainSlots; index += 1) {
      inventoryMain.appendChild(createInventorySlot(items[index] || null));
    }

    for (index = 0; index < totalHotbarSlots; index += 1) {
      inventoryHotbar.appendChild(createInventorySlot(items[totalMainSlots + index] || null));
    }
  }

  var skinFilters = {
    'default': '',
    'gold': 'brightness(1.2) sepia(0.6) saturate(2)',
    'dark': 'brightness(0.5) contrast(1.3)',
    'fire': 'brightness(1.1) hue-rotate(-20deg) saturate(2.5)',
    'ender': 'brightness(0.9) hue-rotate(280deg) saturate(1.5)'
  };

  // Atualiza toda a interface com dados do servidor (chama as funções de renderização).
  function renderState(payload) {
    latestStatePayload = payload;
    renderInventory(payload.user);

    renderSlots(payload.slots, payload.buildings, payload.user.has_axe, payload.user.axe_level);
    renderAxe(payload.user.has_axe, payload.user.axe_level);
    setSteevePosition();
    renderLogs(payload.logs);
    buildScene(payload.stones || []);
    if (payload.trees) {
      renderTrees(payload.trees);
    }

    if (steeve && payload.user.skin) {
      steeve.style.filter = skinFilters[payload.user.skin] || '';
    }
  }

  // Desenha árvores e tocos com contadores de tempo.
  // createElement / className / appendChild / style / onclick / setAttribute: Lab 05 ✅.
  // fetch + promises: fora da matéria dos labs de JS.
  function renderTrees(trees) {
    if (!sceneGrid) return;
    var existingTrees = sceneGrid.getElementsByClassName('scene-tree');
var existingStumps = sceneGrid.getElementsByClassName('scene-tree-stump');
var existing = [];
for (var ei = 0; ei < existingTrees.length; ei++) { existing.push(existingTrees[ei]); }
for (var ei = 0; ei < existingStumps.length; ei++) { existing.push(existingStumps[ei]); }
    for (var ei2 = 0; ei2 < existing.length; ei2++) {
      if (existing[ei2].parentNode) { existing[ei2].parentNode.removeChild(existing[ei2]); }
    }

    for (var ti = 0; ti < trees.length; ti++) {
      var t = trees[ti];
      var column = parseInt(t.column, 10);
      var row = mapRows - 1;
      var treeLeft = (column - 2) * tileSize;
      var treeBottom = row * tileSize + Math.round(tileSize * 0.87);

      if (t.available) {
        var tree = document.createElement('img');
        tree.className = 'scene-tree';
        tree.src = '/static/img/tree.png';
        tree.alt = 'Árvore';
        tree.setAttribute('data-col', '' + column);
        tree.style.left = treeLeft + 'px';
        tree.style.bottom = treeBottom + 'px';
        tree.style.width = (tileSize * 5) + 'px';
        tree.style.height = 'auto';
        tree.style.pointerEvents = 'auto';
        tree.setAttribute('draggable', 'false');
        tree.setAttribute('tabindex', '-1');

        // Clique para cortar árvore via fetch (fetch + promises: fora da matéria dos labs de JS).
        tree.onclick = function (ev) {
          var clicked = ev.target;
          if (!clicked) return;
          var col = parseInt(clicked.getAttribute('data-col'), 10);

          if (clicked.getAttribute('data-chopped')) return;

          if (!canInteractWithColumn(col)) {
            alert('Estás muito longe da árvore. Aproxima-te 1 tile.');
            return;
          }

          clicked.setAttribute('data-chopped', '1');
          clicked.style.pointerEvents = 'none';

          requestJson('/api/chop', { column: col })
            .then(function (payload) {
              if (!payload.ok) {
                alert(payload.payload.message || 'Não foi possível cortar a árvore.');
                clicked.setAttribute('data-chopped', '');
                clicked.style.pointerEvents = 'auto';
                return;
              }

              clicked.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
              clicked.style.opacity = '0.35';
              clicked.style.transform = 'translateY(-20px) scale(0.9)';
              deleteItem(clicked, { delay: 300 });
              setTimeout(function () { if (clicked.parentNode) { clicked.parentNode.removeChild(clicked); } }, 400);
            }).catch(function () {
              alert('Erro de rede ao cortar a árvore.');
              clicked.setAttribute('data-chopped', '');
              clicked.style.pointerEvents = 'auto';
            });
        };

        sceneGrid.appendChild(tree);
      } else {
        // Toco com contador (elementos dinâmicos: Lab 05 ✅).
        var stump = document.createElement('div');
        stump.className = 'scene-tree-stump';
        stump.setAttribute('data-col', '' + column);
        stump.style.position = 'absolute';
        stump.style.left = (column * tileSize + (tileSize / 8)) + 'px';
        stump.style.bottom = treeBottom + 'px';
        stump.style.width = (tileSize * 1.8) + 'px';
        stump.style.height = (tileSize * 1.0) + 'px';
        stump.style.pointerEvents = 'none';

        var badge = document.createElement('div');
        badge.className = 'tree-timer-badge';
        badge.setAttribute('data-col', '' + column);
        badge.style.position = 'absolute';
        badge.style.right = '6px';
        badge.style.top = '-20px';
        badge.style.background = 'rgba(0,0,0,0.6)';
        badge.style.color = '#fff';
        badge.style.padding = '4px 6px';
        badge.style.borderRadius = '6px';
        badge.style.fontSize = '12px';
        badge.textContent = '' + (t.seconds_left || 0);

        stump.appendChild(badge);
        sceneGrid.appendChild(stump);
      }
    }
  }

  // Pedido GET para obter estado do jogo (fetch/promises: fora da matéria dos labs de JS).
  function refreshState() {
    fetch('/api/state')
      .then(function (response) {
        return response.json();
      })
      .then(function (payload) {
        renderState(payload);
      });
  }

  // Função genérica para enviar ações POST ao servidor via fetch.
  function sendAction(url, body) {
    requestJson(url, body)
      .then(function (response) {
        if (!response.ok) {
          alert(response.payload.message || 'Ocorreu um erro.');
          return;
        }

        refreshState();
      });
  }

  function removeInventoryResource(resource, amount) {
    sendAction('/api/inventory/remove', {
      resource: resource,
      amount: amount
    });
  }

  function buildSlot(slotId) {
    sendAction('/api/build/' + slotId, { building_key: selectedBuildingKey });
  }

  function startTask(slotId) {
    sendAction('/api/task/' + slotId + '/start', {});
  }

  function collectTask(slotId) {
    sendAction('/api/task/' + slotId + '/collect', {});
  }

  // Configuração inicial do cenário (style.width/maxWidth: Lab 04 ✅).
  if (sceneFrame) {
    sceneFrame.style.width = '100%';
    sceneFrame.style.maxWidth = 'none';
  }

  if (steeve) {
    steeve.style.zIndex = '3';
  }

  buildScene([]);
  setSteevePosition();

  // Botões de seleção de construção com classList: Lab 05 ✅.
  for (var bi = 0; bi < buildingButtons.length; bi++) {
    (function (button) {
      button.onclick = function () {
        for (var bj = 0; bj < buildingButtons.length; bj++) {
          buildingButtons[bj].classList.remove('selected');
        }

        button.classList.add('selected');
        selectedBuildingKey = button.getAttribute('data-building-key');
      };
    })(buildingButtons[bi]);
  }

  if (buildingButtons[0]) {
    buildingButtons[0].classList.add('selected');
  }

  // Botões de movimento (esquerda/direita). addEventListener: Lab 04 ✅.
  var moveLeftBtn = document.getElementById('btn-move-left');
  var moveRightBtn = document.getElementById('btn-move-right');

  if (moveLeftBtn) {
    moveLeftBtn.addEventListener('click', function () { moveSteeve(-1); });
  }
  if (moveRightBtn) {
    moveRightBtn.addEventListener('click', function () { moveSteeve(1); });
  }

  // Teclado: setas e A/D para andar. addEventListener: Lab 04 ✅.
  document.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowLeft' || event.key === 'a' || event.key === 'A') {
      moveSteeve(-1);
    }
    if (event.key === 'ArrowRight' || event.key === 'd' || event.key === 'D') {
      moveSteeve(1);
    }
  });

  // Redesenha o cenário quando a janela muda (window.onresize: fora da matéria dos labs).
  window.onresize = function () {
    if (!sceneFrame) {
      return;
    }

    if (latestStatePayload) {
      renderState(latestStatePayload);
      return;
    }

    buildScene([]);
    setSteevePosition();
  };

  // Carrega estado inicial (fetch: fora da matéria dos labs de JS).
  refreshState();

  // Atualização periódica do estado (setInterval: Lab 04 ✅).
  setInterval(function () {
    refreshState();
  }, 1000);

  // Atualização local dos timers para manter a contagem regressiva fluida entre refreshes.
  setInterval(function () {
    updateSlotTimers();
  }, 1000);

}

initGame();
