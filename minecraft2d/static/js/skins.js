var currentSkin = null;

function obterUrls() {
    var el = document.getElementById("skins-config");
    if (!el) return { apiSkins: "/api/skins", apiSkinSelect: "/api/skin/select" };
    try {
        return JSON.parse(el.textContent);
    } catch (_) {
        return { apiSkins: "/api/skins", apiSkinSelect: "/api/skin/select" };
    }
}

function carregarSkins() {
    var urls = obterUrls();
    fetch(urls.apiSkins)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            currentSkin = data.current_skin;
            atualizarUI();
        })
        .catch(function(erro) {
            console.error("Erro ao carregar skins:", erro);
        });
}

function atualizarUI() {
    var cards = document.querySelectorAll(".skin-card");
    for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        var skin = card.getAttribute("data-skin");
        var btn = card.querySelector(".skin-select-btn");
        if (skin === currentSkin) {
            card.classList.add("skin-selected");
            btn.textContent = "Ativa";
            btn.disabled = true;
        } else {
            card.classList.remove("skin-selected");
            btn.textContent = "Selecionar";
            btn.disabled = false;
        }
    }
    var status = document.getElementById("skin-status");
    if (currentSkin) {
        var cards2 = document.querySelectorAll(".skin-card[data-skin='" + currentSkin + "'] h3");
        var nome = currentSkin;
        if (cards2.length > 0) {
            nome = cards2[0].textContent;
        }
        status.textContent = "Skin ativa: " + nome;
    }
}

function selecionarSkin(skin) {
    var urls = obterUrls();
    fetch(urls.apiSkinSelect, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({skin: skin})
    })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.ok) {
                currentSkin = data.skin;
                atualizarUI();
            }
        })
        .catch(function(erro) {
            console.error("Erro ao selecionar skin:", erro);
        });
}

var botoes = document.querySelectorAll(".skin-select-btn");
for (var i = 0; i < botoes.length; i++) {
    (function(btn) {
        btn.onclick = function() {
            if (btn.disabled) return;
            var skin = btn.getAttribute("data-skin");
            selecionarSkin(skin);
        };
    })(botoes[i]);
}

carregarSkins();
