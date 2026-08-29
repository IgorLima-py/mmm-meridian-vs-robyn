# Status

_Atualizado: 2026-08-28, fim do dia (Karen — desktop GPU)_

## Onde estamos

**Fases 1, 3 e 4 CONCLUÍDAS na Karen** (a 4 com uma pendência opcional de
escalada). Todos os extratos estão em `runs/*/results/` no schema
pré-registrado; o scorer da Fase 5 já pode consumi-los.

- **Fase 3 (Meridian 1.8.0):** nacional × 5 seeds — todos convergiram
  (max R-hat ≤ 1.02; AKS escolheu 17–36 knots; 5–11 min/run na GPU). Geo × 2
  seeds a 7×2000/2000/1000 após 2 escaladas documentadas: seed102 convergiu
  (1.024); seed101 ficou em 1.118 **puxado só pelos efeitos de tempo** (mu_t/
  knot_values; mídia 1.077) — publicado assim, `rhat_by_param` no JSON.
  Decisões e emendas: `runs/meridian/DECISIONS.md`.
- **Fase 4 (Robyn 3.12.1):** 5 seeds no spec pré-registrado 2000×5 (commit
  `d7f716e`): só seed105 passa o critério de convergência do próprio Robyn.
  Emenda RD (uma escalada 4000×5 para 101–104): **seed101 re-rodou a 4000×5 e
  convergiu por completo** (JSON atual); a escalada de 102–104 foi
  interrompida (encerramento da sessão — "mata tudo") e **não rodou**.
  Decisões: `runs/robyn/DECISIONS.md`. Regra de seleção aplicada conforme
  `analysis/SELECTION_RULE.md` (caminho "clusters" em todos os seeds).

## Próximo passo imediato

- **Karen (retomar aqui é o ideal):** terminar a escalada pendente —
  `wsl -d Ubuntu -u igor --cd /mnt/c/<repo> -- Rscript runs/robyn/run_robyn.R --iterations=4000 102 103 104`
  (~20 min/seed, CPU). Depois commit dos 3 JSONs e Fase 5.
- **Dell:** a Fase 5 (scoring + gráficos) já é possível com os extratos
  atuais — `python analysis/scoring.py --results runs --data data/sim --out
  analysis/out` — mas 3 dos 5 JSONs do Robyn ainda podem ser substituídos
  pela escalada; se for começar antes dela, tratar números como preliminares
  e re-rodar o scorer depois (é barato e regenerável).
- Fase 5 pode rodar em qualquer máquina (Python puro). Fase 6 (artigo) idem.

## Pendências

- Escalada Robyn 4000×5 para seeds 102–104 (Karen; opcional porém decidida na
  emenda RD — os 2000×5 commitados já satisfazem o gate como "não-convergência
  documentada").
- Fase 5: scoring + 3 gráficos (ROI vs verdade, curvas, cobertura/spread).
- Fase 6: artigo (~1000 palavras) + README público.

## Preso a esta máquina (Karen)

- Ambientes WSL2 (Meridian GPU, Robyn multi-core) — reproduzíveis do zero em
  outra máquina com admin via `envs/*.sh` (ordem no topo de `ENVIRONMENT.md`).
- Outputs pesados (gitignored): `outputs/meridian/*.pkl`,
  `outputs/robyn/seed*/OutputModels.rds|OutputCollect.rds`.

## O que foi tentado e não funcionou (hoje)

- `robyn_run(quiet=TRUE)` crasha no 3.12.1 ("object 'pb' not found") — custou
  um run 2000×5; nunca passar `quiet` (fricção F8, `envs/ENVIRONMENT.md`).
- Primeira reconstrução de curva do Robyn pegou o elemento errado do retorno
  de `saturation_hill` (lista `x_saturated`+`inflexion`) — o self-check em
  m=1 vs xDecompAgg pegou o erro na hora; corrigido, agora bate < 1%.
- Geo do Meridian não convergiu a 500/500 nem 1000/1000 (efeitos de tempo dos
  156 knots semanais); 2000/2000 resolveu para seed102, quase para seed101 —
  três tentativas documentadas, sem quarta.
- Dois reboots no meio de runs (sessão esgotada + BIOS) — nada perdido além
  de tempo de computação; runs re-rodados.
