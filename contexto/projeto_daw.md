|     |     | Instituto | Politécnico | de Setúbal |     |
| --- | --- | --------- | ----------- | ---------- | --- |
EscolaSuperiordeCiênciasEmpresariais
|                 |         | Desenvolvimento | de                   | Aplicações | Web         |
| --------------- | ------- | --------------- | -------------------- | ---------- | ----------- |
|                 | Projeto | Final -         | Jogo Web             | de Gestão  | de Recursos |
|                 |         |                 | AnoLetivo: 2025/2026 |            |             |
| 1 Enquadramento |         | e Objetivo      | Geral                |            |             |
NocontextodoDesenvolvimentodeAplicaçõesWeb,acapacidadedeintegrarfrontendintera-
tivocombackendrobustoemcontextodeaplicaçãofuncionaleescalávelconstituiumacom-
petênciaessencialparafuturosprofissionaisdeTecnologiasdeInformação.
Opresenteprojetotemcomoobjetivoconsolidarosconhecimentostrabalhadosnoslabora-
tóriosnoscomponentesdeprogramaçãoJavaScript(DOM,estruturasdedados,persistência)
eprogramaçãoservidoremPython/Flask(MVC,autenticação,persistênciaembasededados,
lógicadenegócio).
Oprojetoconsistenodesenvolvimentodeumjogowebdegestãoderecursos,ondeouti-
lizadorconstróiegereumreino/aldeia/quinta/loja(temalivre),gerindoconstruções,recursos
epossibilidadesdeinteraçãocomoutrosjogadores.
Otemaélivre,masamecânicaerequisitostécnicossãofixos. Ogrupodeve:
• ImplementarumbackendemFlaskcombasededados
• CriarumfrontendresponsivocomHTML/CSS/JavaScript
• Implementarumsistemadeautenticaçãobásico
| • Implementaramecânicacoredojogo: |     |     | construções,recursos,tempo |     |     |
| --------------------------------- | --- | --- | -------------------------- | --- | --- |
• Documentarecomunicaroprojetodeformaclara
Adiferençafundamentalemrelaçãoaoslaboratórioséqueoestudanteassumeopapelde
programador full-stack completo: design da arquitetura, implementação backend, desenvolvi-
mentofrontend,testesedocumentação.
1

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
| 2 Objetivos | Específicos |     |     |     |     |     |
| ----------- | ----------- | --- | --- | --- | --- | --- |
Aoconcluiresteprojeto,ogrupodeverádemonstrarqueécapazde:
• ArquitetarumaaplicaçãowebseguindoopadrãoMVC
• Implementarumsistemadeautenticaçãobásicocomgestãodesessões
• Desenharumesquemadebasededadosadequadoaosrequisitos
• CriarumbackendemFlaskqueimplementealógicadenegóciodojogo
• DesenvolverumfrontenddinâmicoquecomuniquecomobackendviarequisiçõesHTTP
• Gerirestadosdaaplicação(inventários,construções,utilizadores)
• Documentaraarquitetura,APIeinstruçõesdeexecução
• Apresentaredefenderotrabalhorealizado
| 3 Dimensão | dos Grupos |     |     |     |     |     |
| ---------- | ---------- | --- | --- | --- | --- | --- |
Os grupos deverão ter no máximo 3 elementos, por se considerar o número adequado para
assegurarequilíbrioentrepartilhadetrabalho,diversidadedeperspetivasecapacidadedeco-
ordenaçãonodesenvolvimento.
Gruposde2elementospoderãoserautorizados,assumindoogrupooriscodareduçãode
diversidade. Trabalhosindividuaisserãoaceitesmassãofortementedesaconselhados, tanto
pelacargadetrabalhocomopelalimitaçãodeaprendizagemcolaborativa.
| 4 Requisitos | de Trabalho | e   | Entregáveis |     |     |     |
| ------------ | ----------- | --- | ----------- | --- | --- | --- |
OtrabalhodeveráincluiroscomponentesindicadosnaTabela1.
Tabela1:Resumodoscomponentesentregáveisdotrabalho
| Componente     |     | Conteúdoexigido                |     |     | Formato     |      |
| -------------- | --- | ------------------------------ | --- | --- | ----------- | ---- |
| CódigoBackend  |     | Flask,rotas,lógica,basededados |     |     | Python(.py) |      |
| CódigoFrontend |     | HTML,CSS,JavaScript            |     |     | HTML,CSS,JS |      |
| BasedeDados    |     | Esquemadedadosimplementado     |     |     | Formato     | ade- |
|                |     |                                |     |     | quado       | ao   |
projeto
| Documentação | Téc- | API,arquitetura,instruções |           |          | PDF ou | Mark- |
| ------------ | ---- | -------------------------- | --------- | -------- | ------ | ----- |
| nica         |      |                            |           |          | down   |       |
| Relatório    |      | Contextualização,          | decisões, | resulta- | PDF    |       |
dos
| CódigoFonte |     | Código        | organizado | em pas- | Pasta      | compri- |
| ----------- | --- | ------------- | ---------- | ------- | ---------- | ------- |
|             |     | tas/ficheiros |            |         | mida(.zip) |         |
2

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
5 Especificações Técnicas
5.1 MecânicaCoredoJogo
5.1.1 TemaLivre
Otemaélivre. Exemplosválidos:
• GestãodeAldeia: construções(cabana,moinho,quartel),população,defesa
• TycoondeLoja: produtos,balcões,atendimento,lucro
• GestãodeQuinta: campos,colheitas,animais,produção
• ConstruçãodeImobiliário: lotes,casas,lucrocomrendas
• EspaçoSideral: estações,recursos,pesquisa
• Qualqueroutrotemadesdequerespeiteosrequisitosmecânicos
5.1.2 RequisitosMecânicosObrigatórios
1. SistemadeRecursos
• Pelomenos2tiposderecursosprimários(ex: ouroemadeira,ouenergiaepopulação,
etc.)
• Recursoscomeçamcomquantidadesiniciaisaoregistarnovoutilizador
• Interfaceclaramostrandoquantidadeatualemtemporeal
2. Construções/Estruturas
• Mínimode3tiposdeconstruçõesdistintos
• Cadaconstruçãotem: custo(emrecursos),tempodeconstrução,funcionalidade
• Número adequado de slots de construção por utilizador (posições/locais onde cons-
truir)
• Cadaslotsópodeterumaconstruçãoactivaporvez
3. MecânicadeTempo
• Construçõestemtempodeconstrução(1minutoa10minutosrecomendado)
• Apósconclusão,utilizadorrecebenotificação
• Construçõespodemter"tarefas"quelevamtempoeretornambónusderecursos
4. SistemadeTarefas/Ordens
• Cadaconstruçãopodereceberumaordem(ex: "Minerar","Comerciar","Defender")
• TarefalevaXtempo(5minutosa1hora)
• Aocompletar,retornabónusemrecursos(quantidadefixaoupercentual)
• Utilizador deve ir à construção (carregar em botão) para recolher o retorno após con-
clusão
• Interfaceindicaclaramenteoestado: processando,concluída,recolhida
3

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
5. InterfacedeUtilizador
• Dashboardprincipalmostrandoestadodaaldeia/quinta/loja
• Visualizaçãoclaradasconstruçõeserespetivosslots
• Indicadoresdeprogressoparaconstruçõesetarefas
• Históricodeaçõesrecentes
5.2 AutenticaçãoeSistemadeUtilizadores
5.2.1 RequisitosMínimos
• Registo: formuláriocomusername,emailepassword
• Login: autenticaçãocomusernameepassword
• Logout: encerramentodesessão
• PersistênciadeSessão: manterutilizadorautenticadoentrevisitas(cookies/sessões)
• ProteçãoBásica: validaçãodeentrada,proteçãocontraSQLinjection(usarORMcorreto)
5.3 ExemplosdeSuperaçãodosRequisitosMínimos
Para além do que é pedido no enunciado principal, o grupo pode superar os mínimos atra-
vés de escolhas adicionais de qualidade, profundidade técnica ou abrangência funcional. Os
exemplosseguintesnãosãoobrigatórios,masilustramformasdeatingirumníveldeexecução
correspondenteadesempenhosuperior.
5.3.1 AutenticaçãoeSegurança
• Registoavançadocomavatar,verificaçãodeemailouseleçãodedificuldadeinicial
• Recuperaçãodeconta/reposiçãodepassword
• Perfildeutilizadorcomestatísticas,históricoderealizaçõesoupersonalização
• Medidas adicionais de segurança, como 2FA, rate limiting no login ou hashing reforçado de
passwords
5.3.2 InteraçãoentreJogadores
Umadasformasdesuperarosrequisitosmínimosconsisteemacrescentarmecanismosinter-
jogadores. Exemplospossíveis:
1. Ataque/Conflito
• Utilizadorpodeatacaroutrojogador
• Rouboderecursos(parcial)oudanoaconstruções
• Sistemasimplesdedefesa(construçãodefensivareduzdano)
2. Comércio/Troca
• Utilizadorpodeenviarpropostadetrocaparaoutro
• Trocaderecursosporacordomútuo
4

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
• Sistemadeaceitação/rejeição
3. Aliança/Cooperação
• Utilizadorespodemformaralianças/clãs
• Bónuscooperativos(ex: 5%maisrecursosseemaliança)
• Chatoumensagensentremembros
4. Ranking/Leaderboard
• Leaderboardpúblicoordenadoporpontuação(totalderecursosacumulados,constru-
ções,etc.)
• Atualizaçãoemtemporeal
• Badgesparatop3jogadores
5. EventosGlobais
• Eventoúnicoqueafetatodososjogadores(mudançadetaxaderecursos,bonustem-
poral)
• Criadomanualmentepeloadminouautomaticamente
• Mecânicasinterjogadoresmaisricasoumelhorintegradasnofluxoprincipaldojogo
• Sistemasdealiança,comércio,rankingoueventosglobaiscommaiorprofundidadefuncional
• Melhorequilíbrioentrecompetiçãoecooperação,comfeedbackclaroparaoutilizador
5.3.3 QualidadeGlobaldaSolução
• Interfacemaispolida,intuitivaeconsistente
• Organizaçãotécnicaespecialmenteclaraemodular
• Melhorcoberturadetestes,validaçãodeerroserobustezgeral
• Funcionalidadesadicionaisquefaçamsentidonocontextodojogoeestejambemintegradas
5.4 StackTécnicoObrigatório
5.4.1 Backend
• Framework: Flask(Python)
• Arquitetura: PadrãoMVC
• Base de Dados: solução de persistência adequada ao projeto (ex: SQLite, PostgreSQL ou
outra)
• AcessoaDados: SQLAlchemyouabordagemequivalente,quandoaplicável
• Autenticação: Flask-Logincomsessõesbásicas
• Validação: Validaçãodeentradaemrotas(tipos,ranges,etc.)
5

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
5.4.2 Frontend
• HTML:HTML5semântico
• CSS:CSS3comflexbox/gridpararesponsividade
• JavaScript: JavaScript(semdependênciaspesadasdefrontendemversãobase)
• Responsividade: Funcionaemdesktop,tabletemobile
• Atualizações: FetchAPIpararequisiçõesaobackend
5.4.3 Desenvolvimento
• ControlodeVersão: Git+GitHub/GitLab(recomendadoparatrabalhoemequipa)
• Ambiente: Virtualenvironment(venv)ouDocker
6 Metodologia
Otrabalhodeverárefletirasetapasdodesenvolvimentofull-stackweb:
Planear→Design→Backend→Frontend→Integração→Testes→Deploy
O desenvolvimento será acompanhado em contexto de aula e parcialmente realizado em
trabalho autónomo. Recomenda-se, fortemente, a divisão clara de tarefas e comunicação re-
gularentreosmembrosdogrupo.
6.1 PlaneamentoSugerido
6.1.1 Fase1: PlaneamentoeDesign(Semana1)
• Definirtemadojogoemecânicadetalhada
• Desenharwireframesdainterface
• Esquematizarbasededados
• Criardocumentodedesign/vision
6.1.2 Fase2: Backend(Semana2-3)
• Implementarmodelosdedados(Flask-SQLAlchemy)
• Criarrotasdeautenticação(registo,login,logout)
• Implementarasrotasdobackenddojogo(construções,recursos,tarefas)
• Implementarlógicadeconstruçõeserecursos
• Implementarsistemadetempo(computareatualizar)
6

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
6.1.3 Fase3: Frontend(Semana3-4)
• Criarlayoutresponsivo(HTML/CSS)
• Implementarpáginasdeautenticação
• Criardashboardprincipaldojogo
• Implementarcomponentes(construções,recursos,tarefas)
• IntegraçãocomrequisiçõesFetchaobackend
6.1.4 Fase4: Integração,TesteseDocumentação(Semana5)
• Testesdeintegração(frontend+backend)
• Correçãodebugseotimização
• Documentarasrotasdobackend(formatoeparâmetrosesperados)
• Instruçõesdeinstalaçãoeexecução
• Prepararapresentação
7 Gestão e Organização
7.1 PrazodeEntrega
AentregadotrabalhofinaldeveserrealizadanaplataformaMoodleatéaodia12dejunhode
2026,às23:59. Ésuficienteumasubmissãoporgrupo.
7.2 ApresentaçãoeDiscussãoFinal
Naúltimasemanadeaulas,apósaentrega,serárealizadaumaapresentaçãoediscussãodo
projetocomtodososelementosdogrupo.
SituaçãodeImprevisto
Caso ocorra algum imprevisto que impeça a entrega no prazo (problema de ligação à
internet,problematécniconaplataformaMoodle,etc.),ogrupodeve,obrigatoriamente,
procederàentregafísicadoprojetonodiaseguinteatéàs12h00naportariadaescola.
Instruçõesparaentregafísica:
1. Guardar todos os ficheiros (projeto, relatório, documentação) numa pen USB ou
dispositivodearmazenamentoexternoequivalente
2. Entregarnaportariadaescola
3. A pen deve estar claramente identificada com: nome do grupo, disciplina (DAW),
nomedoprojeto
4. Indicarnoenvelope/rótulo: "Endereçadoaoresponsáveldadisciplina"
Importante: Estaviaéapenasparasituaçõesdeimprevistogenuíno. Atrasossemjusti-
ficaçãoválidaresultarãoempenalização.
7

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
Conteúdoaentregar
Devemsersubmetidososseguintesficheiros:
1. projeto_nome_grupo.zip–Códigofontecompleto(backend+frontend)
2. relatorio_nome_grupo.pdf–Relatóriotécnico(5–15páginas)
3. api_documentacao.md–Documentaçãodasrotasdobackend
4. README.md–Instruçõesdeinstalaçãoeexecução
5. base_dados.sql–EsquemaSQLdabasededados
Opcionalmente,podeserincluídoumlinkparadeploydaaplicaçãofuncionalemservidor
online(Heroku,PythonAnywhere,etc.).
7.3 RecomendaçõesparaOrganização
Recomenda-se:
• Organizarocódigoempastas/módulosclaros
• UtilizarGit/GitHub(ouGitLab)paracontrolodeversãoepartilhadeficheirosentreosmem-
brosdogrupo
• CriarumREADME.mdcominstruçõesdeinstalaçãoeexecução
• Documentarasrotasdobackenddeformaclara
• IncluirumficheirocomoesquemaSQLouinstruçõesdecriaçãodabasededados
Sugestõesadicionaisparamelhoraraqualidadedotrabalhoserãofornecidasaolongodas
semanas.
8 Critérios de Avaliação
Oprojetoseráavaliadoemcincodimensões:
1. Frontend – Interface, usabilidade, organização visual, responsividade e integração com o
backend.
2. Backend – Modelação de dados, implementação da lógica, rotas, autenticação e robustez
doservidor.
3. ExtensãodeFuncionalidades–Alcancefuncionaldoprojeto,riquezadasmecânicasimple-
mentadaseintegraçãodasfuncionalidadesadicionais.
4. Qualidade da Implementação – Clareza do código, estrutura da solução, consistência téc-
nica,validaçãoefiabilidadegeral.
5. Documentação–QualidadedoREADME,instruçõesdeexecução,documentaçãotécnicae
clarezadacomunicaçãodotrabalho.
Cadaumadestasdimensõesseráapreciadanumaescalade0a4pontos:
8

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
• 0–Nãocumpreocritérioouaevidênciaapresentadaéinsuficiente
• 1–Cumprimentomuitoincompletooucomfalhassignificativas
• 2–Satisfazosmínimosaceitáveis
• 3–Cumprecomqualidadeoqueépedidonesseponto
• 4–Superaclaramenteoqueépedidonoenunciadonesseponto
Osexemplosapresentadosnasecçãodesuperaçãodosrequisitosmínimosdevemseren-
tendidoscomoreferênciaspossíveisparaatingirumnível4,enãocomochecklistobrigatória.
Nota: Aclassificaçãofinalresultadaapreciaçãoglobaldotrabalhoentreguenestasdimen-
sõesedodesempenhoindividualdecadaelementonaapresentação/discussãofinal. Asclas-
sificaçõesindividuaispodemserdiferentesdentrodomesmogrupoe,nolimite,umestudante
podeobter0valoresnumprojetoclassificadocom20valoressenãodemonstrarconhecimento
mínimosobreoquefoiimplementado.
9 Checklist
Emseguidaéapresentadaumachecklistquepodeauxiliarnaverificaçãodoprogressodotra-
balho.
□ Temadojogodefinidoenarrativaclara
□ Documentodedesigncriado(wireframes,mecânica)
□ Esquema/modelodedadosdesenhado
□ EndpointsdaAPIdefinidos
□ ProjetoFlaskcomestruturaMVCimplementada
□ Modelosdedadosimplementados(User,Building,Task,Resource,etc.)
□ Autenticação(registo,login,logout)funcional
□ Sistemadesessãoimplementado
□ Lógicadeconstruçõesfuncionante(criar,destruir,listar)
□ Sistemaderecursosfuncionante(ganhar,gastar,atualizar)
□ Sistemadetempoimplementado(tarefascompletamapósXtempo)
□ Mecanismoderecolhamanualdetarefasconcluídasfuncionante
□ Rotasdobackendfuncionaisetestadas
□ FrontendHTML/CSSresponsivocriado
□ Dashboardprincipalfuncional
□ IntegraçãoFrontend/BackendcomFetchAPI
□ (Opcional)Sistemainterjogadoresimplementado
9

DesenvolvimentodeAplicaçõesWeb ProjetoFinal-JogoWebdeGestãodeRecursos
□ README.mdcominstruçõesdeinstalação
□ Rotasdobackenddocumentadas
□ Relatóriotécnicoescrito(5–15páginas)
□ Apresentaçãopreparada(slidesoudemo)
□ AplicaçãotestadaemFirefox/Chrome/Safari
□ Segurança: validaçãodeentrada
□ Performance: carregamentorápido,semtimeout
□ Dadosdeexemplocriados(seeddata)
□ (Opcional)CódigoversionadoemGitcomhistóricosignificativo
10 Resultado Esperado
O grupo deverá demonstrar uma aplicação web full-stack coerente, funcional e bem funda-
mentada,evidenciandodomíniodosconceitosabordadosnaunidadecurricular(autenticação,
MVC,HTML/CSS/JavaScript)ecapacidadedeaplicartécnicasdeengenhariadesoftware(de-
sign,testes,documentação).
Otrabalhodeverefletirprofissionalismonaabordagemaoproblema,rigortécniconaimple-
mentação,segurançaadequadaeclarezanacomunicaçãodosresultados.
Ojogodeveserjogável,funcionaledivertido,mesmoquesimples.Nãoéesperadoumjogo
dequalidadecomercial,massimumaprovadeconceitosólida.
Bomdesenvolvimento!
11 Referências
• FlaskDocumentation. (2025). WelcometoFlask. https://flask.palletsprojects.com/
• https://flask-sqlalchemy.palletsprojects.com/
• MDNWebDocs.(2025).FetchAPI.https://developer.mozilla.org/en-US/docs/Web/API/
Fetch_API
• MDNWebDocs. (2025). HTML.https://developer.mozilla.org/en-US/docs/Web/HTML
• Fowler,M.(2002). PatternsofEnterpriseApplicationArchitecture. Addison-Wesley.
• OWASP.(2025).Top10WebApplicationSecurityRisks.https://owasp.org/www-project-top-ten/
10