# Próximo

Ponteiro de UMA fatia. A fila inteira está em `docs/ROADMAP.md` — este arquivo
é só o topo dela, resolvido agora. Lido pelo hook `SessionStart` e pelo `/oi`;
avançado pelo `/tchau` só depois que o `verificar:` abaixo estiver satisfeito.

chat: C4
titulo: Fase 6 — o artigo de ~1.000 palavras
perfil: escrita pública, enquadramento irreversível
modelo: opus
esforco: max
forma: sessao
maquina: any
plan-mode: nao
objetivo: Escrever o artigo em torno da tese revisada — as duas ferramentas erraram por cerca de metade, um oráculo com os parâmetros verdadeiros também errou, e a pergunta que importa é quais canais eram recuperáveis. É o entregável público: enquadramento errado não se remenda depois.

## Contexto mínimo para abrir

- **C3 fechou** (Fase 5). Os três gráficos estão em `analysis/figures/`, o
  scorer é `analysis/scoring.py`, e o desenho de cada gráfico está registrado
  em `analysis/FIGURES.md`. Ler `analysis/ORACLE.md` inteiro **antes** de
  escrever qualquer frase: ele é a interpretação de referência e a seção
  "What this does and does not license us to say" é o limite do que o artigo
  pode afirmar.
- **Todo número do artigo sai de `analysis/out/summary.md` ou de um JSON
  commitado em `runs/*/results/`.** O `analysis/out/metrics_long.csv` é
  gitignorado e não serve de fonte para número publicado.
- **Rodar o `publication-auditor` antes de considerar qualquer parágrafo
  pronto, não depois.** Na sessão do C3 ele reprovou oito vezes seguidas e
  achou erro numérico real em texto recém-revisado, inclusive alegações que eu
  havia relatado como corrigidas sem estarem. Ele é barato perto de publicar
  errado — e **auditoria estreita** (um arquivo, uma pergunta, ~20 chamadas)
  entrega veredito; auditoria ampla estoura o limite de turnos sem veredito.
- Ganchos que o artigo tem de carregar, todos verificados no C3: a inversão
  aparece **nas duas** ferramentas (o braço geo do Meridian inverte por
  completo); o Robyn devolve **um** ROI repetido cinco vezes; e o oráculo L3,
  na mesma base, calibra intervalo a 92% contra 90% nominal.

**verificar:** `article/` existe, contagem de palavras entre 800 e 1300, contém o título literal "What neither tool can tell you", e `grep -i` encontra "simulated" e "1.8.0" no texto.
