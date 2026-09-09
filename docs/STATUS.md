# Status

_Atualizado: 2026-09-09 (sessão iniciada em 08/09 — Karen, desktop GPU)_

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

- **C1** escalada Robyn 4000×5 para os seeds 102–104. Enquanto não fechar, os
  extratos commitados são um **misto de specs** (seed101 a 4000×5, os outros a
  2000×5) e **3 dos 5 seeds do Robyn não convergiram** — os dois fatos estão
  rotulados no `ORACLE.md` e no `REASSESSMENT`, mas precisam ser resolvidos ou
  divulgados explicitamente na peça.
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
