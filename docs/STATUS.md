# Status

_Atualizado: 2026-08-27 (PC Dell — laptop sem admin)_

## Onde estamos

**Fase 2 CONCLUÍDA no Dell.** Go do Igor dado; execução começou.

Feito nesta sessão (além do planejamento e decisões de escopo já registrados):

- `simulation/` — gerador config-driven (adstock geométrico + Hill, 8 geos ×
  156 semanas, 5 canais), ground truth contrafactual, checks de sanidade.
  `python -m simulation.generate` + `python -m simulation.checks` (exit 0).
- `data/sim/seed101..105/` — geo.csv, national.csv, robyn.csv,
  ground_truth.json por seed (commitados; ~1 MB total).
- `analysis/` — RESULTS_SCHEMA.md (contrato agnóstico de ferramenta),
  SELECTION_RULE.md (regra Robyn pré-registrada), scoring.py (M1–M5;
  `--selftest` passou: distingue stub honesto de stub enviesado a spend-share).
- CLAUDE.md — reconhecimento de máquina no `/oi` (por GPU: NVIDIA = Karen,
  Intel = Dell) + papéis por máquina.
- Calibração: tv–ooh r 0.34–0.61; variância de mídia 23–35%; ROIs verdadeiros
  0.8–3.5; tv com curva S (mROI > ROI, intencional).

## Próximo passo imediato

**Depende da máquina** (o `/oi` identifica):

- **Karen (desktop GPU, admin):** executar a **Fase 1** do PLAN — WSL2 +
  Ubuntu (`wsl --install`, reboot), driver NVIDIA atual, venv Python 3.12 com
  `google-meridian[and-cuda]==1.8.0` + smoke test em GPU, R ≥ 4.2 + Robyn
  3.12.1 + nevergrad (venv 3.10, `RETICULATE_PYTHON` pinado) + smoke test
  multi-core. Checklist completo na Fase 1 do PLAN. Depois: Fases 3 e 4
  (runs Meridian e Robyn sobre `data/sim/`, exportando no schema de
  `analysis/RESULTS_SCHEMA.md` para `runs/<tool>/results/`).
- **Dell:** **nada bloqueante — o Dell está em espera até a Karen produzir
  runs.** A Fase 5 (scoring/gráficos) consome `runs/*/results/*.json` quando
  existirem. Único trabalho opcional de Dell enquanto isso: rascunhar os
  scripts de run + exporters (`runs/meridian/`, `runs/robyn/`) para a Karen só
  ajustar e executar — útil, mas código sem ambiente para testar; a Karen
  também pode escrevê-los na Fase 3/4.

## Pendências

- Fase 1 na Karen (ambientes) → Fases 3–4 (runs) → Fases 5–6 (Dell)

## O que foi tentado e não funcionou

- Calibração da simulação precisou de 3 iterações: cópia integral do calendário
  tv→ooh deu r=0.99 (corrigido: 75% de flights compartilhados com contagem
  determinística); amplitudes iniciais deram variância de mídia 0.45 (reduzidas);
  sorteio binomial de flights compartilhados era instável entre seeds (trocado
  por contagem exata). Detalhes nos parâmetros de `simulation/config.py`.
- `pandas.to_markdown` exige `tabulate` (não instalado no Dell) — removida a
  dependência; tabela markdown formatada manualmente em `scoring.py`.
