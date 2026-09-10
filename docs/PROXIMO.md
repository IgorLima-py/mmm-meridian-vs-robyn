# Próximo

Ponteiro de UMA fatia. A fila inteira está em `docs/ROADMAP.md` — este arquivo
é só o topo dela, resolvido agora. Lido pelo hook `SessionStart` e pelo `/oi`;
avançado pelo `/tchau` só depois que o `verificar:` abaixo estiver satisfeito.

chat: C6
titulo: Auditoria adversarial até o veredito SHIP
perfil: leitura adversarial da peça inteira + correção do que ela reprovar
modelo: opus
esforco: max
forma: sessao
maquina: any
plan-mode: nao
objetivo: Rodar o `publication-auditor` contra a peça terminada — artigo, README, figuras e resultados — e agir em cada achado até o veredito ser SHIP. É o último portão antes de publicar, e o trabalho dele é achar o que todas as passadas anteriores deixaram passar.

## Contexto mínimo para abrir

- **C5 fechou.** O `README.md` agora tem ~215 linhas e é a porta de entrada
  pública: pergunta, resposta condicional sem vencedor, duas tabelas de número
  com legenda de proveniência, fig1 embutida, duas camadas de reprodução,
  tabela de versões com o risco do `tfp-nightly`, e o limite do lado R. O
  artigo (`article/meridian-vs-robyn.md`, 1.299 palavras) **não foi tocado** —
  ele já está em `VERDICT: SHIP` e tem 1 palavra de folga até o teto do C4.
- **A auditoria agora tem uma superfície maior do que no C4.** Ela precisa
  cobrir o README também, e o README repete números do artigo: os agregados por
  braço, a tabela de recuperabilidade por canal e os tempos de run. Todo número
  repetido é uma chance nova de divergir de `analysis/out/summary.md`.
- **Como rodar o auditor, pelo que o C4 aprendeu:** a forma ampla (mandar ele
  auditar tudo de uma vez) **estoura o limite de turnos** e volta sem veredito
  — aconteceu no C3 e no C4. O que funciona é **rodada estreita**: um alvo por
  chamada (o artigo; depois o README; depois as figuras/legendas), 7-17
  chamadas cada, cada uma voltando com veredito próprio.
- **Ele indicia, não conserta.** Cada BLOCK vira correção feita à mão aqui, ou
  vira ressalva explícita na seção de limitações com o motivo de não ter sido
  corrigida. As duas saídas são aceitáveis; ignorar não é.
- **A saída da auditoria é commitada** sob `analysis/` — é isso que mostra ao
  leitor que a peça foi revisada adversarialmente e contra o quê.
- **Duas decisões abertas que o Igor precisa fechar, e o auditor vai bater
  nelas:** (1) **não existe `LICENSE`** — repo público sem licença é repo que
  ninguém pode reusar legalmente; (2) o README não diz mais "work in progress",
  então publicar passa a ser uma decisão de data, não de estado.
- **Item opcional herdado do C5, não bloqueante:** o gerador escreve CRLF no
  Windows enquanto o git guarda LF, então `git status` acusa os CSVs como
  modificados depois de re-gerar. O conteúdo é idêntico e o README documenta
  isso honestamente. Fazer o gerador escrever LF explícito eliminaria a
  ressalva — é meia hora e não pertence ao C6.

**verificar:** a saída do `publication-auditor` está commitada sob `analysis/` e sua última linha lê `VERDICT: SHIP`.
