"""Meridian smoke test, stage 2 (PLAN Phase 1 gate): a tiny model on Meridian's
own sample data must sample on the GPU. Wall-clock is recorded in
envs/ENVIRONMENT.md (setup cost, not a benchmark).

Run: ~/venvs/meridian/bin/python envs/smoke_meridian_model.py
"""
import time

import tensorflow as tf

assert tf.config.list_physical_devices("GPU"), "GPU required for this smoke test"

from meridian.data import test_utils
from meridian.model import model, spec

data = test_utils.sample_input_data_revenue(n_media_channels=3, seed=1)
mmm = model.Meridian(input_data=data, model_spec=spec.ModelSpec())

t0 = time.time()
mmm.sample_prior(5, seed=1)
t_prior = time.time() - t0

t0 = time.time()
mmm.sample_posterior(n_chains=2, n_adapt=100, n_burnin=50, n_keep=100, seed=1)
t_post = time.time() - t0

post = mmm.inference_data.posterior
print("posterior dims:", dict(post.sizes))
print(f"sample_prior: {t_prior:.1f}s, sample_posterior: {t_post:.1f}s")
print("smoke stage 2 OK")
