"""Meridian smoke test, stage 1 (PLAN Phase 1 gate): TF sees the GPU and
meridian imports. Stage 2 (tiny model on sample data) lives in
smoke_meridian_model.py once the env exists.

Run: ~/venvs/meridian/bin/python envs/smoke_meridian_gpu.py
"""
import time

t0 = time.time()
import tensorflow as tf  # noqa: E402

print("tensorflow", tf.__version__)
gpus = tf.config.list_physical_devices("GPU")
print("GPUs visible:", gpus)
assert gpus, "TensorFlow does not see any GPU"

with tf.device("/GPU:0"):
    x = tf.random.normal([2000, 2000], seed=7)
    y = tf.linalg.matmul(x, x)
print("matmul on GPU OK, checksum", float(tf.reduce_sum(y)))

import meridian  # noqa: E402

print("meridian", meridian.__version__)
print(f"smoke stage 1 OK in {time.time() - t0:.1f}s")
