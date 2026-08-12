# import torch
# import torch.nn as nn

# policy -> value function(sitation quality) -> model(algorithm) -> environment -> reward -> policy

# class ActorCritic(nn.Module):
#     def __init__(self, state_dim: int = 258, action_dim: int = 4):
#         super().__init__()
#         self.actor = nn.Sequential(
#             nn.Linear(state_dim, 128),
#             nn.Tanh(),
#             nn.Linear(128, 64),
#             nn.Tanh(),
#             nn.Linear(64, action_dim),
#             nn.Softmax(dim=-1)
#         )
#         self.critic = nn.Sequential(
#             nn.Linear(state_dim, 128),
#             nn.Tanh(),
#             nn.Linear(128, 64),
#             nn.Tanh(),
#             nn.Linear(64, 1)
#         )

#     def forward(self, state: torch.Tensor):
#         probs = self.actor(state)
#         value = self.critic(state)
#         return probs, value





import torch
import torch.nn as nn


# Actor-Critic is a Reinforcement Learning architecture.
#
# Actor  -> decides WHAT ACTION the agent should take.
# Critic -> evaluates HOW GOOD the current situation/state is.
#
# Example:
# A robot is trying to escape a maze.
#
# Actor might say:
#   Left  = 10%
#   Right = 70%
#   Up    = 15%
#   Down  = 5%
#
# Critic might say:
#   "This position looks pretty good" -> value = 8.4
#
class ActorCritic(nn.Module):

    def __init__(self, state_dim: int = 258, action_dim: int = 4):
        super().__init__()

        # state_dim = number of input features describing the environment.
        # Here the agent receives 258 values representing the current state.
        #
        # action_dim = number of actions available to the agent.
        # Here we have 4 possible actions.
        #
        # Example:
        # 0 = Left
        # 1 = Right
        # 2 = Up
        # 3 = Down


        # =========================================================
        # ACTOR NETWORK
        # =========================================================
        # The Actor decides which action should be taken.
        #
        # Input:
        #     Current state (258 values)
        #
        # Output:
        #     Probability of taking each of the 4 actions.
        #
        # Example output:
        #     [0.10, 0.60, 0.20, 0.10]
        #
        # This means the agent believes action 1 is the best choice.

        self.actor = nn.Sequential(

            # First hidden layer
            # Converts 258 state features into 128 learned features.
            nn.Linear(state_dim, 128),

            # Activation function.
            # Adds non-linearity so the network can learn complex behaviour.
            nn.Tanh(),

            # Second hidden layer
            # Compresses 128 features into 64 useful features.
            nn.Linear(128, 64),

            nn.Tanh(),

            # Output layer
            # Produces one score for every possible action.
            nn.Linear(64, action_dim),

            # Converts the action scores into probabilities.
            #
            # Example:
            # Raw scores  -> [1.2, 3.5, 0.5, -1.0]
            # Softmax     -> [0.08, 0.82, 0.07, 0.03]
            #
            # All probabilities add up to 1.
            nn.Softmax(dim=-1)
        )


        # =========================================================
        # CRITIC NETWORK
        # =========================================================
        # The Critic does NOT choose an action.
        #
        # It estimates how valuable/good the current state is.
        #
        # Input:
        #     Same 258-value state
        #
        # Output:
        #     ONE number representing expected future reward.
        #
        # Higher value -> promising state
        # Lower value  -> bad/unpromising state

        self.critic = nn.Sequential(

            # 258 state features -> 128 learned features
            nn.Linear(state_dim, 128),

            nn.Tanh(),

            # 128 -> 64 features
            nn.Linear(128, 64),

            nn.Tanh(),

            # Only ONE output because the critic estimates
            # one value V(state).
            nn.Linear(64, 1)
        )


    def forward(self, state: torch.Tensor):

        # Give the current state to the Actor.
        #
        # It returns probabilities for all possible actions.
        #
        # Example:
        # probs = [0.1, 0.6, 0.2, 0.1]
        probs = self.actor(state)


        # Give the SAME state to the Critic.
        #
        # It returns an estimate of how good this state is.
        #
        # Example:
        # value = 7.8
        value = self.critic(state)


        # Return both:
        #
        # probs -> used to decide/select an action
        # value -> used to judge the state and improve learning
        return probs, value