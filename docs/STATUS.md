# Status

_Atualizado: 2026-09-09 (sessão C3 — Karen, desktop GPU — C3 fechado)_

## Sessão C3 (09/09) — Fase 5: scoring, os três gráficos, e oito rodadas de auditoria

Karen (RTX 4070 Super), mas **nada aqui precisou de GPU, WSL2 ou R** — C3 é
Python puro sobre arquivos commitados e roda no Dell igual.

**O que foi feito.** `analysis/figures.py` (novo) desenha os três gráficos da
Fase 5 em `analysis/figures/`; ele chama `scoring.run_scoring()` em vez de
recalcular, e importa `simulation.checks.channel_snr` para ordenar os canais,
de modo que gráfico e gate C7 não conseguem divergir. Para isso o cálculo do
C7 virou função reutilizável em `simulation/checks.py` (saída idêntica,
verificada). `analysis/FIGURES.md` (novo) registra as seis decisões de desenho
(D-F1..D-F6). `docs/PLAN.md` Fase 5 fechada. `envs/analysis.lock.txt` (novo)
pina a camada de análise — matplotlib era a dependência que faltava — e
`envs/ENVIRONMENT.md` ganhou a seção correspondente.

**Decisão de desenho que manda no resto:** a terceira série dos gráficos 1 e 2
é o oráculo **L3** (estima o próprio baseline, como as duas ferramentas
precisam fazer), não o L2. O `analysis/ORACLE.md` continua usando L2 na tabela
por canal, porque lá a pergunta é de teto ("era recuperável por alguém?"). Os
dois documentos agora explicam essa divisão em vez de se contradizerem.

**O scorer mudou e o `summary.md` ficou mais informativo.** `analysis/scoring.py`
agora imprime, por tool-arm: quantos seeds passaram no check de convergência da
própria ferramenta, a **spec de run** (lida de `run.convergence_detail` — Robyn
em iterations x trials, Meridian em adapt/burnin, com aviso explícito quando a
spec é mista) e, por canal, o erro relativo **com sinal e absoluto** mais a
coluna `effect share − spend share (pp)`. Nada disso altera M1–M5; o
`rssd_pull` pré-registrado ficou intocado.

### A auditoria reprovou oito vezes. Leia isto antes do C4.

Rodei o `publication-auditor` oito vezes: BLOCK com 6, 2, 1, 2, (sem veredito),
(sem veredito), 1 e 3 achados. **Todos os achados numéricos eram reais.** Os
que importam para quem continuar:

- **A coluna do Robyn no `ORACLE.md` estava desatualizada** desde a escalada do
  C1: cobertura 0.20 → **0.16**, viés −0.506 → **−0.540**, |erro| 0.538 →
  **0.555**, e todos os cinco erros por canal mudaram. A afirmação "search e tv
  são os piores do Robyn" ficou falsa (são search e social).
- **A história de convergência do Robyn estava errada por um seed.** O
  `runs/robyn/DECISIONS.md` registra **quatro** seeds falhando a 2000×5; o
  seed101 só convergiu depois da escalada. E os extratos commitados são **spec
  mista** (101–104 a 4000×5, 105 a 2000×5) — coisa que não estava em lugar
  nenhum e agora viaja nas três legendas e no `summary.md`.
- **Assimetria de divulgação, e era contra nós.** As ressalvas do Robyn estavam
  em todo lugar; as do Meridian, em lugar nenhum. O braço **geo** do Meridian
  rodou a **2000/2000** (4x a spec pré-registrada, terceira tentativa) com
  **64 e 122 divergências** contra 1–6 por run national, e o seed102 conta como
  convergido carregando 122. O `runs/meridian/DECISIONS.md` registrava
  divergências das tentativas **descartadas** e nunca das publicadas — corrigido
  por emenda datada, lida dos extratos, sem re-run.
- **A inversão aparece nas DUAS ferramentas.** O braço geo do Meridian inverte
  por completo: ooh **0.161** é o canal mais preciso dele e o menor erro por
  canal que qualquer uma das duas ferramentas alcança — em cima do canal menos
  recuperável do cenário. As cinco células menores da tabela são todas do
  oráculo e todas em tv. Isso muda o enquadramento do artigo e é o gancho mais
  forte do C4.
- **O dial de correlação tv–ooh nunca acertou o alvo.** Realizado 0.34, 0.37,
  0.38, 0.38, 0.61 contra alvo pré-registrado de ~0.4–0.5: **zero de cinco**
  dentro. O que segurou os dados foi o gate C2, mais largo, [0.30, 0.65].
- **O mecanismo de encolhimento estava mal descrito.** "Cada ferramenta encolhe
  para um valor característico" não descreve o Meridian: ele **comprime** para
  a banda 0.74–1.24 (fator 1.7 contra 4.4 da verdade), com a mediana do prior
  (1.22) no **teto** da banda, não no centro. O Robyn sim colapsa: banda
  0.68–0.73, fator 1.08.

### O que foi tentado e falhou — não repita

- **Script de patch que faz vários `replace` e grava só no fim.** Uma asserção
  falha no meio e **descarta as edições anteriores**, silenciosamente. Isso
  aconteceu duas vezes e nas duas eu relatei correções que não existiam no
  disco. Regra que sai daí: **um arquivo por script, e `grep` de verificação
  depois de gravar** — nunca confiar no "ok" impresso.
- **`replace()` sem asserção.** Um `s.replace(a, b)` que não casa imprime "ok" e
  não faz nada. Toda substituição precisa de `assert a in s`.
- **Heredoc do Bash com `
` dentro de string Python:** o `
` chega como
  newline real e a busca nunca casa. Construir com `chr(92) + "n"`.
- **Auditoria ampla estoura o limite de 40 turnos sem dar veredito** — aconteceu
  duas vezes seguidas, ~200k tokens sem resultado. **Auditoria estreita** (três
  arquivos, uma pergunta, orçamento de turnos declarado, "veredito parcial se
  faltar turno") deu veredito em 15–25 chamadas. Usar só essa forma.
- **`SendMessage` para subagente não existe neste build** — não dá para retomar
  um auditor que estourou o limite; só relançar.
- **Média entre seeds antes do módulo cancela sinal e lisonjeia.** Foi assim que
  publiquei "0.4pp" onde o valor honesto por célula canal-seed é **0.54pp**.
  Agregação sempre por célula, e a agregação usada tem de estar dita.

### Pendências que o C4 herda

- **Uma auditoria só teve veredito parcial.** O último BLOCK tinha 3 achados;
  dois foram corrigidos e o terceiro era "os arquivos novos estão untracked",
  que este commit resolve por construção. **Não houve rodada de auditoria sobre
  o estado commitado** — vale rodar uma estreita no início do C4.
- **A limitação do M5 está documentada, não corrigida.** O `rssd_pull` pontua o
  Meridian (0.085) acima do Robyn (0.067) porque mede deslocamento sem teto: o
  Meridian passa do spend share, o Robyn pousa em cima. A métrica ficou como
  pré-registrada e a coluna nova `effect share − spend share` foi posta ao lado.
- **Números na prosa das legendas são literais escritos à mão** em
  `figures.py` (64, 122, 2000/2000, 4000x5, 92%, as razões da curva de tv, as
  versões das ferramentas). Foram lidos dos JSONs commitados, mas **nada no
  pipeline pega um literal obsoleto** se um run for re-exportado. Lista
  exaustiva no `analysis/FIGURES.md`.
- **O lado R não é pinado** (`install.packages("Robyn")` sem versão;
  `nevergrad.lock.txt` é escrito pelo script, não lido). Dito em dois lugares e
  virou item 7 do `docs/BACKLOG.md`.
- **`docs/REASSESSMENT_2026-09-08.md` ganhou nota de snapshot** em vez de ser
  reescrito: os números do Robyn nele estão superados, e a nota diz para onde ir.
- O mini-arm de sensibilidade da Fase 5 foi **descartado da v1** de propósito
  (o oráculo responde a mesma pergunta com cinco seeds, e re-rodar ferramenta
  depois de ver resultado é o que a pré-registração existe para impedir). Item
  6 do backlog, para a v2, pré-registrado.

**Nada preso a esta máquina.** C4 é escrita e roda em qualquer PC.


## Sessão C2 (09/09) — gate de sinal/ruído por canal, C2 fechado

Mesma máquina da sessão C1 anterior (Karen, RTX 4070 Super). Trabalho
puramente de código/docs, não precisou de GPU nem de WSL2.

**O que foi feito:** adicionado o check **C7** em `simulation/checks.py` —
sinal-to-noise por canal (desvio padrão da contribuição nacional verdadeira do
canal / desvio padrão do ruído de receita nacional, janela de medição), com
piso `SNR_FLOOR = 0.15` definido no topo do módulo. É **WARN, nunca FAIL**:
imprime uma linha por canal por seed e só adiciona a warnings list se abaixo
do piso — nunca ao `failures`, então nunca derruba o exit code.

Rodei `python -m simulation.checks` nos 5 seeds: exit 0 em todos, e os
números batem com `analysis/ORACLE.md` (tv ~1.7-2.1, search ~0.34-0.46, social
~0.31-0.37 — todos acima do piso; ooh ~0.09-0.12 e display ~0.09-0.11 — os
dois abaixo do piso, em **todo** seed, sem exceção). Isso é exatamente o
achado que o oráculo já tinha isolado por outro caminho (fit OLS com os
parâmetros verdadeiros) — o gate barato concorda com o gate caro.

Documentei o gate em `docs/PLAN.md` §3 (novo parágrafo depois do bullet de
"Simulator checks") e `data/README.md` (nova seção depois da variance share),
os dois citando `analysis/oracle.py` como o passo de verdade-terreno
pré-registrado que qualquer cenário futuro deve rodar antes de comprometer
uma GPU — deixei explícito que C7 é um proxy barato, não substitui o oráculo.

**Nada ficou pela metade.** Não houve nada tentado e abandonado nesta
sessão — a mudança era pequena e totalmente especificada no `docs/PROXIMO.md`,
rodou de primeira.

**Verificação do `verificar:`** confirmada linha a linha:
`python -m simulation.checks` → exit 0; `grep -c 'signal-to-noise' docs/PLAN.md
data/README.md` → `1` e `2` (ambos não-zero).

**Arquivos tocados:** `simulation/checks.py`, `docs/PLAN.md`, `data/README.md`.
Nenhum dado gerado foi tocado (`data/sim/` não muda com este check).

`docs/ROADMAP.md`: C2 → `done`. `docs/PROXIMO.md` avançou para **C3** —
opus/high (julgamento analítico), já desbloqueado desde que C1 fechou na
sessão anterior. Nada preso a esta máquina: C3 é escrita e análise, roda em
qualquer PC.

## Sessão C1, retomada (09/09) — C1 fechado, escalada não resolveu convergência

Reabri no mesmo dia, mesma máquina (Karen, RTX 4070 Super confirmada de novo).
Rodei a escalada 4000×5 para os seeds 102, 103 e 104 com o comando corrigido
(`bash -lc "cd ... && ..."` em vez de `wsl --cd`) — terminou em ~1h,
desatendido, sem erro.

**Resultado, e é um achado, não um problema:** os três seeds rodaram os 4000
iterações completas, mas **nenhum convergiu** pelo critério próprio do Robyn
(DECOMP.RSSD falhou nos três; NRMSE falhou só no 102). Dobrar as iterações não
resolveu a não-convergência que já tinha sido documentada a 2000×5. Estado
final dos cinco seeds do Robyn: 101 convergido (4000×5), 102/103/104 não
convergidos (4000×5), 105 convergido (2000×5, spec original, nunca escalado).
Fechei a emenda RD em `runs/robyn/DECISIONS.md` com os números exatos de cada
seed (sd/med do DECOMP.RSSD e NRMSE, runtime).

Rodei os três gates (`/score`): todos passaram limpo. A cobertura do intervalo
do Robyn nacional caiu de ~20% (estimativa anterior, pré-escalada) para
**16%** com o dado final. `analysis/out/summary.md` foi regenerado e
commitado.

`docs/ROADMAP.md`: C1 → `done`. C3 também desbloqueou (dependia só do C1), mas
o ponteiro `docs/PROXIMO.md` avançou para **C2** — mesmo perfil mecânico
(sonnet/medium) desta sessão, roda em qualquer máquina, sem pré-requisito. C3
é opus/high (julgamento analítico) e fica pra quando o Igor pedir
explicitamente.

**Também nesta sessão:** o Igor levantou três perguntas sobre o desenho do
dataset (granularidade de canal por veículo digital, uso do reach&frequency
nativo do Meridian, o fato de eu ter dito impreciso que "nenhuma ferramenta
modela frequência" — o Meridian aceita um tipo de canal RF, só não foi usado
aqui de propósito, pra manter a comparação like-for-like). Viraram os itens 4
e 5 do `docs/BACKLOG.md` (v2, pós-publicação), em vez de mudar o `docs/PLAN.md`
da v1.

## Sessão C1, primeira tentativa (09/09) — escalada interrompida, nada perdido

Esta sessão tentou rodar a escalada 4000x5 do Robyn para os seeds 102, 103 e
104 (a pendência do C1). O run foi **interrompido antes de terminar** porque a
máquina (Karen) precisa ser desligada. **Nenhum JSON foi escrito** — o processo
foi morto durante o feature engineering do seed102 (~1% do trabalho de um
único seed), então `runs/robyn/results/` está exatamente como estava:
seed101 em 4000x5, seeds 102–105 em 2000x5. `git status` limpo, nada para
reverter.

**Fricção nova, documentada para não ser redescoberta:** `wsl -d Ubuntu -u igor
--cd <path> -- <comando>` funciona em **foreground** mas falha em
**background** com `WSL/ERROR_PATH_NOT_FOUND` (código de saída 127) — testado
três vezes, inclusive com um comando trivial (`pwd`) sem nada de específico do
Robyn. A forma que funciona em background é trocar o flag `--cd` por
`bash -lc "cd <path> && <comando>"`. `docs/PROXIMO.md` já foi atualizado com o
comando corrigido.

**Próximo passo, ao reabrir nesta máquina:** rodar de novo o comando corrigido
em `docs/PROXIMO.md` para os três seeds (102, 103, 104) — nenhum progresso
parcial existe para aproveitar, é um restart limpo. `docs/ROADMAP.md` marca o
C1 como `doing` (não `next`) para deixar claro que já foi tentado uma vez. O
ponteiro `docs/PROXIMO.md` **não avançou** — o `verificar:` do C1 continua
insatisfeito.

## Onde estamos

**Fases 1, 3 e 4 concluídas** (a 4 com uma pendência de escalada). Esta sessão
não rodou modelo nenhum: ela reavaliou o projeto depois do lançamento do
Meridian GeoX, construiu o teste que faltava para a peça ser publicável, e
montou a infraestrutura de Claude Code do repo.

A partir de agora a **fila de trabalho vive no `docs/ROADMAP.md`** (C0–C6, com
máquina, modelo e esforço recomendados por tarefa). Este arquivo continua sendo
a narrativa: o que falhou, o que ficou pela metade, o que está preso a esta
máquina. O `/oi` lê só a tabela do roadmap; este documento é lido sob demanda.

## O que esta sessão fez

**1. Reavaliação 360 → `docs/REASSESSMENT_2026-09-08.md`.** Reverificação de
Meridian, Robyn, GeoX, GeoLift e PyMC-Marketing contra fontes primárias em
08/09. O que mudou desde o planejamento de 27/08:

- **Meridian 2.0.0 saiu em 03/09** (mudou o backend padrão de TensorFlow para
  JAX, mais 6 breaking changes). Os runs deste repo são **1.8.0** — decisão:
  ficar na 1.8.0 para a v1 e tratar a defasagem como achado sobre churn de
  ferramenta, não como dívida.
- **Meridian GeoX foi 0.1.1 → 1.0.0 → 1.0.1 em 48 h.** O extra de instalação
  funciona; o nome correto é `geox` (`pip install "google-meridian[geox]"`),
  não `meridian-geox`. Decisão: **sem braço GeoX na v1** — exigiria subir para
  2.0.0 e re-rodar tudo, e o Robyn só aceita point-estimate como calibração, o
  que transformaria a comparação em demo de feature do Meridian.
- **Robyn:** último commit no `main` em 27/06/2025, CRAN 3.12.1 em 02/07/2025,
  não arquivado. Estrelas: Meridian 1522 × Robyn 1513 — passou, mas por nove.
  A afirmação defensável é sobre cadência de manutenção, não popularidade.
- **PyMC-Marketing chegou a 1.0.0 estável em 07/08/2026** (backlog v2 fica mais
  barato e mais credível, mas continua fora da v1).
- **Heusch (arXiv 2608.21128, 21/08/2026) NÃO rodou as ferramentas** — ele
  implementou o próprio modelo observacional. O gap que este projeto ocupa
  continua aberto.

**2. O oráculo — o teste que faltava.** `analysis/oracle.py` +
`analysis/ORACLE.md` + `runs/oracle/results/` (20 JSONs, 4 degraus × 5 seeds,
no mesmo schema, pontuados pelo mesmo harness).

Motivo: as duas ferramentas erraram o ROI em ~50% na mesma direção, e isso é
indistinguível de um bug nosso na ground truth. O oráculo recebe a forma
funcional e os parâmetros verdadeiros e só estima os betas.

- **O harness está limpo:** com receita sem ruído, o oráculo recupera os betas
  com erro máximo de 1,2e-14. Gerador, ground truth, schema e scorer concordam.
- **Recuperabilidade é por canal.** tv (sinal/ruído 1,91), search (0,39) e
  social (0,34) são recuperáveis — o oráculo erra 4%, 15% e 24%, e as
  ferramentas erram 34–76%. ooh (0,11) e display (0,10) **não são** — o oráculo
  erra 97% e 76%, e nenhum estimador faria melhor.
- **A armadilha:** as ferramentas *parecem* melhores justamente em ooh e
  display, porque os ROIs verdadeiros ali (0,8 e 1,2) estão perto do valor para
  onde cada uma encolhe. Ler a tabela de erro de uma ferramenta sozinha inverte
  a ordem — completamente no Robyn, parcialmente no Meridian.
- **O encolhimento é das ferramentas:** viés do oráculo −0,01 a +0,12; Meridian
  −0,31; Robyn −0,51. E o degrau do oráculo que estima o próprio baseline cobre
  a verdade 92% das vezes contra 90% nominal, enquanto Meridian cobre 60% e
  Robyn 20% — "o dado era difícil" não desculpa.

Consequência para a peça: a tese deixa de ser "qual ferramenta chegou mais
perto" (empate técnico: 0,533 × 0,538) e passa a ser "a verdade estava nos
dados? em quais canais? e o que cada ferramenta faz quando não estava".

**3. Infraestrutura Claude Code (C0).** `.claude/settings.json`, dois hooks,
o subagente `publication-auditor`, a skill `/score`, o `docs/ROADMAP.md`, e `/oi` e
`/tchau` reescritos junto com as seções correspondentes do `CLAUDE.md`.

## O que foi tentado e falhou — leia antes de repetir

- **O `.gitignore` engolia toda a infraestrutura.** Ele terminava com
  `.claude/*` + `!.claude/commands/`, então `settings.json`, `agents/`,
  `skills/` e `hooks/` seriam ignorados e **nunca chegariam à outra máquina**.
  Corrigido com negações explícitas. Verificado com `git check-ignore -v`.
- **`!analysis/out/summary.csv` não funcionava** sob `analysis/out/`: o git não
  desce em diretório excluído, então negação lá dentro nunca vale. A regra teve
  de virar `analysis/out/*` (o conteúdo, não o diretório).
- **Prometi `analysis/out/summary.csv` e o scorer gera `summary.md`.** Alinhado
  para o arquivo que existe de verdade, em quatro lugares.
- **O hook de commit bloqueou meu próprio comando de teste**, porque a string
  de teste continha a frase proibida e o matcher pegou. Os testes tiveram de
  montar a frase em runtime. É a prova mais forte de que ele funciona.
- **`attribution` não existe na doc de settings.** Procurei a página inteira:
  nenhum campo controla o trailer `Co-Authored-By`. Não gravei campo não
  verificado — o default já mantém o trailer, que é o comportamento desejado.
- **`.git/index.lock` órfão de 31/08**, 0 bytes, sem processo git — resíduo de
  um dos reboots registrados no handoff anterior. **Ele teria feito o `/tchau`
  falhar.** Removido. Se `git add` reclamar de lock, cheque a data do arquivo e
  se há processo git antes de remover.
- **A auditoria adversarial reprovou o meu próprio trabalho** — ver abaixo.

## A auditoria que reprovou o ORACLE.md (e o que foi corrigido)

Rodei o `publication-auditor` contra o `analysis/ORACLE.md` recém-escrito:
`VERDICT: BLOCK`, 7 achados bloqueantes, todos verificados e reais:

1. **A coluna "Meridian" na tabela por canal misturava os braços national e
   geo**, enquanto oráculo e Robyn eram national-only — denominador diferente
   para uma ferramenta numa comparação de três, e o pool incluía um run não
   convergido. Corrigido para national-only. O ooh do Meridian é **0,55**, não
   0,44, o que enfraquece parte da afirmação original sobre "melhores canais".
   **O mesmo erro estava no `REASSESSMENT`** e foi corrigido lá também.
2. **"57–76%"** era 34–76%: o piso escolhido inflava a falha das ferramentas.
3. **Convergência subdeclarada.** Eu citava só Meridian geo seed101. São
   **quatro** runs: mais Robyn national 102, 103 e 104. Usar "Robyn cobre 20%"
   como evidência sem dizer que 3 dos 5 seeds não convergiram era exatamente a
   acusação de cherry-picking que este projeto existe para evitar. Rotulado em
   todo lugar onde número do Robyn aparece.
4. **Proveniência.** Sinal/ruído, CV do regressor, correlações e o teste sem
   ruído não saíam de nenhum script commitado — foram gerados no terminal.
   Violação direta da regra dura nº 3. Corrigido na raiz: `python
   analysis/oracle.py --diagnostics` agora emite todos eles.
5. **Ao regenerar, as correlações publicadas estavam erradas:** eu disse
   0,79–0,95 (é **0,66–0,94**) e 0,02–0,24 para os demais pares (é **−0,05 a
   0,09**, com um par negativo, ooh–search, que eu havia omitido).
6. Viés do oráculo "+0,07 a +0,12" contradizia a própria tabela (L3 = −0,008).
7. Citação errada (`PLAN D5` onde é `PLAN §3`), √8 onde é √6, e "erro 0,0" onde
   é 1,2e-14.

**Lição para as próximas sessões:** rodar o auditor **antes** de considerar
qualquer texto pronto, não depois. Ele achou erro numérico real em documento
que eu tinha acabado de escrever e revisar.

## Colisão com o canon do playbook — resolvida, leia antes de mexer em `.claude/`

No fim desta sessão o push foi **rejeitado**: o commit `2d3fd21` ("instala o
canon do playbook") tinha subido do outro lado enquanto o trabalho corria, e
colidia com a infraestrutura recém-construída em quatro arquivos.

Resolução, decidida pelo Igor e aplicada por rebase (`eb8fd1f`):

- **O canon vence nos comandos.** `/oi`, `/tchau`, `/360`, `hooks/sessao-abre.ps1`
  e `.gitattributes` ficaram **idênticos** ao canon — verificado com
  `git diff origin/main -- <arquivo>` em cada um. As versões que esta sessão
  havia escrito para `/oi` e `/tchau` foram descartadas.
- **`settings.json` virou união:** os `deny` do canon (que incluem
  `git reset --hard` e `git clean -fd`, que a versão local não tinha) mais os
  `allow` dos três gates de Python, `git push` em `ask`, os caminhos de chaves
  negados, `PYTHONUTF8=1`, e os **três** hooks convivendo (o `SessionStart` do
  canon + os dois desta sessão).
- **`.gitignore`:** as duas versões tinham feito **a mesma correção de forma
  independente** (negações para `.claude/settings.json|skills|agents|hooks`).
  Ficou a do canon, que ainda ignora `settings.local.json` explicitamente.
- **O que é só deste repo ficou por cima:** `guard_publication.py`,
  `warn_py_syntax.py`, `publication-auditor`, a skill `/score`, o oráculo e a
  reavaliação.

**Regra que sai disso:** mudança de infraestrutura que vale para todo projeto
do Igor vai para o **playbook**, não para cá. Só o que é específico deste repo
mora em `.claude/` local. Está escrito no `CLAUDE.md`.

Consequências estruturais:

- `ROADMAP.md` saiu da raiz e virou **`docs/ROADMAP.md`**, que é onde o canon
  procura, com um campo **`verificar:`** checável por fatia (o `/tchau` usa ele
  para decidir se avança o ponteiro).
- **`docs/PROXIMO.md`** passa a ser o ponteiro de UMA fatia. Os nomes das
  chaves não foram inventados: saíram do consumidor real, o parser em
  `.claude/hooks/sessao-abre.ps1` (`perfil`, `modelo`, `esforco`, `chat`,
  `titulo`, `forma`, `maquina`, `plan-mode`, `objetivo`) mais `verificar:`, que
  o `/tchau` lê. Os templates oficiais vivem no playbook e **não estão neste
  repo** — se divergirem, o playbook manda.
- **`docs/DESVIOS.md`** criado, sem nenhuma linha (não houve desvio).

**Não é preciso rodar o `/360` para formatar isto.** A análise 360 e o desenho
das fatias já foram feitos à mão nesta sessão; o `/360` serve para *refazer* o
roadmap, e o próprio comando avisa que refazer um roadmap bom é queimar
opus/max para chegar no mesmo lugar.

## C7 — PyMC-Marketing promovido do backlog

`d63afc9`. Continua **pós-publicação** e `blocked` atrás do C6, mas agora está
escrito com a armadilha que ninguém deve redescobrir: **o PyMC-Marketing usa
saturação logística por padrão, não Hill**. O gerador usa Hill exatamente
porque Hill é a interseção das famílias do Meridian e do Robyn (PLAN D3) — e
não é a default do PyMC. Rodar no default mediria o descasamento de forma
funcional, não a ferramenta. A escolha (configurar Hill e declarar, ou tratar o
logístico como cenário separado) tem de ser pré-registrada num
`runs/pymc/DECISIONS.md` **antes** do primeiro run.

O motivo de fazer o C7 mudou: a metade *defensiva* ("três ferramentas erraram,
logo não é bug meu") foi absorvida pelo oráculo, que prova a mesma coisa melhor.
O que sobra é a pergunta aberta — Meridian ancora no prior de ROI, Robyn no
spend share, e um terceiro ancora em quê?

## Próximo passo imediato

- **Karen (esta máquina):** **C1** — a escalada do Robyn.
  `wsl -d Ubuntu -u igor --cd /mnt/c/<repo> -- Rscript runs/robyn/run_robyn.R --iterations=4000 102 103 104`
  (~20 min/seed, CPU, desatendido). Nunca passar `quiet` (fricção F8).
- **Qualquer máquina, em paralelo:** **C2** — piso de sinal/ruído por canal no
  `simulation/checks.py`.
- Detalhe, definition of done e estimativa de cada um: `docs/ROADMAP.md`.

## Pendências

- **C1 fechado** (09/09, sessão retomada). Os cinco extratos do Robyn seguem
  specs documentados (101 e 102-104 a 4000×5, 105 a 2000×5 por já ter
  convergido) — não é mais um "misto" não explicado, é um resultado
  registrado em `runs/robyn/DECISIONS.md`. **3 dos 5 seeds do Robyn continuam
  não convergidos** mesmo a 4000×5 — isso não muda até a peça, só fica mais
  bem documentado. `ORACLE.md` e `REASSESSMENT` citam a cifra antiga (~20%
  cobertura); atualizar para 16% quando qualquer um dos dois for revisado de
  novo (não é bloqueante — só desatualizado).
- **C2** o gate de recuperabilidade.
- **C3–C6** scoring + gráficos, artigo, README público, auditoria final.
- **Subagente e skill só carregam no próximo start da sessão.** Hooks e
  `settings.json` recarregam na hora (verificado). `publication-auditor` e
  `/score` já apareceram no fim desta sessão, então estão ativos.
- **A detecção de máquina por GPU vai pedir permissão uma vez por sessão.** A
  regra `PowerShell(...)` foi tirada do `allow` por não ter sido possível
  verificá-la; o hook `SessionStart` do canon injeta o estado do repositório
  mas **não** detecta a GPU, então o passo continua sendo do `/oi`.
- **`verificar:` do C1 corrigido:** a contagem de iterações fica em
  `run.convergence_detail.iterations`, não em `extras`. A primeira versão do
  campo apontava para o lugar errado e foi consertada antes de qualquer uso.

## Preso a esta máquina (Karen)

- Ambientes WSL2 (Meridian GPU, Robyn multi-core) — reproduzíveis do zero em
  outra máquina com admin via `envs/*.sh` (ordem no topo de `ENVIRONMENT.md`).
- Outputs pesados (gitignored, ~1,2 GB): `outputs/meridian/*.pkl`,
  `outputs/robyn/seed*/OutputModels.rds|OutputCollect.rds`.
- **C1 só roda aqui** (precisa do R no WSL2). C2 em diante roda em qualquer
  máquina — Python puro sobre arquivos commitados.

## Fricções anteriores que continuam valendo

- `robyn_run(quiet=TRUE)` crasha no 3.12.1 (`object 'pb' not found`) — nunca
  passar `quiet` (F8, `envs/ENVIRONMENT.md`).
- Geo do Meridian não convergiu a 500/500 nem 1000/1000; 2000/2000 resolveu
  para seed102 e quase para seed101 — três tentativas documentadas, sem quarta.
- Reconstrução de curva do Robyn: pegar o elemento certo do retorno de
  `saturation_hill`; o self-check em m=1 vs `xDecompAgg` pega o erro na hora.
