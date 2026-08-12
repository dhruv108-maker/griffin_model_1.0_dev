import gymnasium as gym
from gymnasium import spaces
import numpy as np

class GriffinSearchEnv(gym.Env):
    """
    Action Space:
      0: RETRIEVE (Query top-k candidate pool)
      1: EXPAND_CONTEXT (Include adjacent paragraphs)
      2: ACCEPT_EVIDENCE (Commit current candidate)
      3: REJECT_EVIDENCE (Discard current candidate)
    """
    def __init__(self, topics: list, paragraphs: list):
        super().__init__()
        self.topics = topics
        self.paragraphs = paragraphs
        self.current_topic_idx = 0
        self.current_para_idx = 0
        self.visited_evidence = set()

        self.action_space = spaces.Discrete(4)
        # Vector state: [Topic Emb (128), Current Context Emb (128), Coverage Memory (1), Steps (1)]
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(258,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_topic_idx = 0
        self.current_para_idx = 0
        self.visited_evidence.clear()
        return self._get_obs(), {}

    def _get_obs(self):
        topic_vec = np.random.randn(128).astype(np.float32)
        ctx_vec = np.random.randn(128).astype(np.float32)
        coverage = np.array([len(self.visited_evidence) / max(1, len(self.topics))], dtype=np.float32)
        step_ratio = np.array([self.current_para_idx / max(1, len(self.paragraphs))], dtype=np.float32)
        return np.concatenate([topic_vec, ctx_vec, coverage, step_ratio])

    def step(self, action: int):
        reward = 0.0
        terminated = False
        
        if action == 0:  # RETRIEVE
            reward += 0.1
        elif action == 1:  # EXPAND_CONTEXT
            reward += 0.05
        elif action == 2:  # ACCEPT
            pair_key = (self.current_topic_idx, self.current_para_idx)
            if pair_key in self.visited_evidence:
                reward -= 1.0  # Penalty for duplicate
            else:
                self.visited_evidence.add(pair_key)
                reward += 2.0  # Reward for accepted evidence
        elif action == 3:  # REJECT
            reward -= 0.1

        self.current_para_idx += 1
        if self.current_para_idx >= len(self.paragraphs):
            self.current_topic_idx += 1
            self.current_para_idx = 0

        if self.current_topic_idx >= len(self.topics):
            terminated = True

        return self._get_obs(), reward, terminated, False, {}