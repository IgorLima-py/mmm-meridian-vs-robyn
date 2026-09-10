# Próximo

Ponteiro de UMA fatia. A fila inteira está em `docs/ROADMAP.md` — este arquivo
é só o topo dela, resolvido agora. Lido pelo hook `SessionStart` e pelo `/oi`;
avançado pelo `/tchau` só depois que o `verificar:` abaixo estiver satisfeito.

chat: C5
titulo: README público e passe de reprodutibilidade
perfil: escrita pública + verificação mecânica em clone limpo
modelo: opus
esforco: high
forma: sessao
maquina: any
plan-mode: nao
objetivo: Reescrever o README para o leitor externo — a pergunta, a resposta condicional, os limites e como re-rodar — e provar num clone limpo que os quatro comandos rodam do zero numa máquina sem os ambientes de modelo. É o que transforma "confie em mim" em "rode você mesmo".

## Contexto mínimo para abrir

- **C4 fechou.** `article/meridian-vs-robyn.md` (1.299 palavras) passou por três
  rodadas do `publication-auditor` e está em `VERDICT: SHIP`. **Não reabra o
  artigo** sem motivo forte: cada frase dele carrega uma ressalva que a
  auditoria exigiu, e há **1 palavra de folga** até o teto de 1300 — qualquer
  acréscimo estoura o `verificar:` do C4.
- **O README atual tem 8 linhas** e diz "work in progress — not yet released".
  Ele é o arquivo a reescrever. O `docs/ROADMAP.md` abaixo do `<!-- HEADER-END -->`
  traz a definition of done completa do C5.
- **O que o README precisa carregar, e nada disso é opcional:** a pergunta, a
  resposta condicional (sem vencedor), a tabela de versões pinadas **incluindo
  a esquisitice do `tfp-nightly`**, e o limite honesto de reprodutibilidade —
  **o lado R não é pinado** (`install.packages("Robyn")` sem versão,
  `nevergrad.lock.txt` é escrito e não lido). Isso está dito em
  `envs/ENVIRONMENT.md` na seção "Where 'pinned' stops being true" e é item 7
  do `docs/BACKLOG.md`. Repetir no README, não esconder.
- **O passe de reprodutibilidade é mecânico, não retórico.** Clone em
  diretório vazio, `pip install -r envs/analysis.lock.txt`, e os quatro
  comandos do `verificar:` com exit 0 — sem WSL2, sem R, sem GPU. Só a camada
  de análise (Python puro) precisa rodar.
- **Atenção ao primeiro comando:** `python -m simulation.generate` reescreve
  `data/sim/`, que **já está commitado**. Se o clone limpo gerar bytes
  diferentes dos commitados, isso não é ruído — é falha do check C6
  (determinismo) e vira achado, não conserto silencioso.
- **`analysis/out/diagnostics.md` é novo** (fechou no C4) e é fonte citada pelo
  artigo. É gerado por `python analysis/oracle.py --diagnostics` e está
  des-ignorado por negação explícita no `.gitignore`.
- **Última etapa do C5 é o teste do público sobre o histórico inteiro:** nenhum
  hostname, nenhum caminho local absoluto, nenhum dado real, nenhuma frase
  proibida, em nenhum commit. O repo nasceu privado mas vai a público **com o
  histórico**.

**verificar:** um clone em diretório vazio roda `python -m simulation.generate`, `python -m simulation.checks`, `python analysis/oracle.py` e `python analysis/scoring.py` com exit 0 usando só as instruções do README, numa máquina sem os ambientes de modelo.
