import envpool.python.xla_template
import numpy as np

num_envs = 8
env = envpool.make("Pong-v5", env_type="gym", num_envs=num_envs)
obs = env.reset()
for _ in range(5000):
    act = np.random.randint(0, 5, size=num_envs)
    obs, rew, term, trunc, info = env.step(act)
    if any(term) or any(trunc):
        print(np.logical_or(term, trunc))
