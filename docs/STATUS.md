# Status

_Atualizado: 2026-08-28 (Karen — desktop GPU)_

## Onde estamos

**Fase 1 CONCLUÍDA na Karen.** Os dois smoke tests passaram (gate da fase).

Feito nesta sessão:

- **WSL2 + Ubuntu 26.04** instalados. Exigiu habilitar SVM na BIOS (virtualização
  vinha desligada de fábrica) — reboot no meio da instalação.
- **Ambiente Meridian:** Python 3.12.14 (uv), `google-meridian[and-cuda]==1.8.0`,
  TF 2.21.0 com XLA/CUDA na RTX 4070 Super. O wheel do TF 2.21 não enxerga as
  libs CUDA do pip (sem RUNPATH) — corrigido com preload via `sitecustomize.py`,
  já dentro do `envs/setup_meridian.sh`.
- **Ambiente Robyn:** R 4.5.2 + Robyn 3.12.1 (CRAN) + nevergrad 1.0.12 em venv
  Python 3.10, `RETICULATE_PYTHON` pinado no `~/.Renviron`. Faltavam
  `cmake`/`libuv1-dev`/`libnlopt-dev` no apt (a compilação CRAN morreu 2×) —
  adicionados ao `envs/apt_base.sh`.
- **Smoke Meridian:** modelinho nos dados-exemplo amostrou na GPU (2 chains ×
  100 draws, 151 s — dominado por compilação XLA). **Smoke Robyn:**
  `dt_simulated_weekly`, 200 iter × 1 trial, 26 s em **11 cores** (multi-core
  confirmado, o motivo do WSL2).
- `envs/`: scripts idempotentes (`apt_base.sh`, `setup_meridian.sh`,
  `setup_robyn.sh`), smoke tests, lockfiles, `ENVIRONMENT.md` com o friction
  log M7 (F1–F7).

**Aprendizado para a Fase 4:** com exposure em `paid_media_vars`, o Robyn nomeia
os hiperparâmetros pelos nomes de **exposição** (`facebook_I_alphas`), não pelos
de spend — errar isso quebra fundo no `hyper_collector` com erro críptico
(fricção F7 no ENVIRONMENT.md).

## Próximo passo imediato

- **Karen:** **Fase 3** (runs Meridian sobre `data/sim/` — nacional × 5 seeds +
  braço geo) e depois **Fase 4** (runs Robyn). Exportar no schema de
  `analysis/RESULTS_SCHEMA.md` para `runs/<tool>/results/`; decisões em
  `runs/<tool>/DECISIONS.md`. Outputs pesados ficam em pasta ignorada na Karen.
- **Dell:** em espera até existirem `runs/*/results/*.json` (aí Fase 5).

## Pendências

- Fases 3–4 na Karen → Fases 5–6 no Dell.
- Ambientes WSL vivem só na Karen e não viajam pelo git; qualquer máquina
  reproduz com os scripts de `envs/` (ordem no topo do `ENVIRONMENT.md`).

## O que foi tentado e não funcionou

- `wsl --install` antes do reboot reporta sucesso do WSL mas a distro Ubuntu não
  registra (virtualização ainda desligada) — refeito pós-BIOS com
  `wsl --install -d Ubuntu --no-launch`.
- TF 2.21 out-of-the-box com zero GPUs visíveis (RUNPATH ausente no wheel) —
  diagnóstico via `LD_LIBRARY_PATH`; fix permanente no setup script.
- Compilação CRAN interrompida deixa locks `00LOCK-*` em `~/R/library` — limpar
  antes de retomar.
- Primeira versão do `smoke_robyn.R` com hiperparâmetros nomeados por spend →
  erro no `hyper_collector` (ver aprendizado acima).
