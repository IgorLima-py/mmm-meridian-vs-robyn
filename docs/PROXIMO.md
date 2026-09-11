# Próximo

Ponteiro de UMA fatia. A fila inteira está em `docs/ROADMAP.md` — este arquivo
é só o topo dela, resolvido agora. Lido pelo hook `SessionStart` e pelo `/oi`;
avançado pelo `/tchau` só depois que o `verificar:` abaixo estiver satisfeito.

chat: C8
titulo: Portão de publicação — a licença e as últimas conferências
perfil: uma decisão do Igor + comandos; nada de análise nem de escrita
modelo: sonnet
esforco: low
forma: sessao
maquina: any
plan-mode: nao
objetivo: Fechar a única coisa que ainda separa a peça de um repositório público — ela não tem `LICENSE`. Apresentar as opções de licença para o Igor escolher, escrever o arquivo depois que ele escolher, citar a licença no README, e rodar as conferências finais antes do go/no-go. Publicar não é desta fatia: é decisão de data, e é do Igor.

## Contexto mínimo para abrir

- **O C6 fechou com `VERDICT: SHIP`.** Nove rodadas do `publication-auditor`,
  sete BLOCK e duas SHIP. O registro público está em `analysis/AUDIT.md` — leia
  a seção "What the audit did not resolve" antes de dizer qualquer coisa sobre
  o estado da peça. A narrativa da sessão está no `docs/STATUS.md`.
- **A licença é decisão do Igor, não sua.** O repo tem código (simulador,
  scoring, figuras) e uma peça escrita. O arranjo usual é uma licença
  permissiva para o código (MIT ou Apache-2.0) mais CC BY 4.0 para o artigo.
  Apresente as opções com uma linha cada sobre o que mudam para quem quer
  reusar o simulador ou citar o artigo, e **só escreva o arquivo depois que ele
  escolher**. Não invente licença por conta própria.
- **O que NÃO é desta fatia.** Não publique. Não mexa no artigo, no README nem
  nas figuras além de citar a licença — a peça passou por nove rodadas de
  auditoria e cada edição nova já se mostrou capaz de introduzir erro. Se achar
  algo errado, anote no `STATUS.md` e fale com o Igor; não corrija de improviso.
- **As conferências finais são comandos, não leitura:** clone limpo, venv novo
  a partir de `envs/analysis.lock.txt`, as seis chamadas da camada 1 do README,
  e conferir que a última linha do `analysis/AUDIT.md` ainda lê `VERDICT: SHIP`.
  O parágrafo "Verified, not asserted" do README está datado de 2026-09-11; se
  você rodar noutro dia e nada tiver mudado, a data continua correta — ela
  descreve o passe que validou este estado, não o dia em que você leu.
- **Quatro decisões do Igor continuam abertas** e estão listadas no fim da
  seção do C6 no `docs/STATUS.md`: publicar (data), declarar vs. regerar a
  contradição da D5 (`BACKLOG` 9), o degrau do oráculo com inclinação 1
  (`BACKLOG` 8), e o tamanho do artigo (1.835 palavras, acima da faixa do C4,
  com nota datada no `ROADMAP`). Nenhuma bloqueia a publicação.

**verificar:** `LICENSE` existe na raiz, o README nomeia a licença, e um clone limpo roda as seis chamadas da camada 1 sem falha.
