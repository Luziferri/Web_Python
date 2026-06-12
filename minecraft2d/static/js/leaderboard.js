function obterUrlLeaderboard() {
    var el = document.getElementById("leaderboard-config");
    if (!el) return "/api/leaderboard";
    try {
        var cfg = JSON.parse(el.textContent);
        return cfg.apiLeaderboard || "/api/leaderboard";
    } catch (_) {
        return "/api/leaderboard";
    }
}

function atualizarRanking() {
    var url = obterUrlLeaderboard();
    fetch(url)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            var lista = document.getElementById("ranking-list");
            lista.innerHTML = "";

            for (var i = 0; i < data.ranking.length; i++) {
                var jogador = data.ranking[i];
                var li = document.createElement("li");
                li.classList.add("ranking-item");

                var posicao = i + 1;
                var spanInfo = document.createElement("span");
                var spanPontos = document.createElement("span");

                var textoPrefixo = posicao + "\u00ba ";

                if (posicao === 1) {
                    li.classList.add("badge-1");
                    textoPrefixo = "\ud83e\udd47 " + textoPrefixo;
                } else if (posicao === 2) {
                    li.classList.add("badge-2");
                    textoPrefixo = "\ud83e\udd48 " + textoPrefixo;
                } else if (posicao === 3) {
                    li.classList.add("badge-3");
                    textoPrefixo = "\ud83e\udd49 " + textoPrefixo;
                }

                spanInfo.textContent = textoPrefixo + jogador.username;
                spanPontos.textContent = jogador.score + " pts";

                li.appendChild(spanInfo);
                li.appendChild(spanPontos);
                lista.appendChild(li);
            }
        })
        .catch(function(erro) { console.error("Erro ao carregar o ranking:", erro); });
}

atualizarRanking();
setInterval(atualizarRanking, 5000);
