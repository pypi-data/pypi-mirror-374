import torch as T
import numpy as np
import torch.nn.functional as F

from multiagent_auction.agent import Agent
from multiagent_auction.buffer import ReplayBuffer

class MADDPG:
    """
    Main class that implements the Multi-Agent Deep Deterministic Policy Gradient (MADDPG) algorithm.

    This class manages a group of agents that learn in a shared multi-agent environment.
    Each agent is trained using actor-critic methods, considering both its own state and
    the states and actions of other agents.

    Parameters:
    - alpha, beta (float): learning rates for actor and critic networks.
    - input_dims (int): dimension of the input state.
    - tau (float): soft update parameter for target networks.
    - gamma (float): discount factor for future rewards.
    - BS (int): batch size.
    - fc1, fc2 (int): number of neurons in hidden layers.
    - n_actions (int): number of actions per agent.
    - n_agents (int): number of agents in the environment.
    - total_eps (int): total number of training episodes.
    - noise_std (float): standard deviation of Gaussian noise for exploration.
    - tl_flag (bool): boolean flag for transfer learning.
    - extra_players (int): number of "ghost" agents to be added.
    """
    
    def __init__(self,
                 alpha: float=0.000025, 
                 beta: float=0.00025, 
                 input_dims: int=1, 
                 tau: float=0.001, 
                 gamma: float=0.99, 
                 BS: int=64, 
                 fc1: int=64, 
                 fc2: int=64, 
                 n_actions: int=1, 
                 n_agents: int=2, 
                 total_eps: int=100000, 
                 noise_std: float=0.2, 
                 tl_flag: bool=False, 
                 extra_players: int=0):
        self.agents = []
        self.num_agents = n_agents
        for _ in range(n_agents):
            self.agents.append(Agent(alpha=alpha, beta=beta, input_dims=input_dims, 
                                     tau=tau, batch_size=BS, layer1_size=fc1, 
                                     layer2_size=fc2, n_agents=self.num_agents,
                                     n_actions=n_actions, total_eps=total_eps, 
                                     noise_std=noise_std, tl_flag=tl_flag,
                                     extra_players=extra_players))
            
        self.batch_size = BS
        self.gamma = gamma
        self.max_size = 1000000
        self.memory = ReplayBuffer(self.max_size, input_dims, n_actions, self.num_agents)
        self.short_memory = ReplayBuffer(1, input_dims, n_actions, self.num_agents)

    def _create_ghosts(self, array: np.ndarray, num_tiles: int) -> np.ndarray:
        """
        Adds ghost agents by replicating the first column of the input array multiple times.

        Args:
            array (np.ndarray): Array of shape (batch_size, num_agents - 1)
            num_tiles (int): Number of ghost agents to append

        Returns:
            np.ndarray: Extended array with ghost agent columns
        """
        first_column = np.expand_dims(array[:, 0], axis=1)
        tiled = np.tile(first_column, (1, num_tiles))
        return np.concatenate([array, tiled], axis=1)

    def _get_others_actions(self, idx: int, others_states: T.tensor, network: str='target_actor') -> T.tensor:
        """
        Computes the actions of all agents except the one with index `idx`.

        Args:
            idx (int): Index of the current agent
            others_states (Tensor): Tensor with shape (batch_size, num_agents - 1)
            network (str): Network to use ('target_actor' or 'actor')

        Returns:
            Tensor: Concatenated actions from other agents
        """
        indexes = list(range(self.num_agents))
        indexes.remove(idx)
        actions = []
        for i in range(len(indexes)):
            state_col = others_states[:, i].reshape(-1, 1)
            agent_net = getattr(self.agents[indexes[i]], network)
            actions.append(agent_net.forward(state_col))
        return T.cat(actions, dim=1)

    def _train_critic(self, agent, state: T.tensor, action: T.tensor, reward: T.tensor, others_states: T.tensor, 
                      others_actions: T.tensor, target_actions: T.tensor, others_target_actions: T.tensor) -> None:
        """
        Trains the critic network of a given agent.

        Computes the target Q-values and applies gradient descent to minimize the critic loss.

        Args:
            agent: Agent whose critic is being trained
            state, action, reward: Tensors for current agent
            others_states, others_actions: Tensors for other agents
            target_actions: Predicted target actions of the current agent
            others_target_actions: Predicted target actions of other agents
        """
        critic_value_ = agent.target_critic.forward(state, target_actions, others_states, others_target_actions)
        critic_value = agent.critic.forward(state, action, others_states, others_actions)

        # alinhar device/dtype e evitar lista em Python
        dev  = critic_value_.device
        dtyp = critic_value_.dtype

        # garante que reward está no mesmo device/dtype
        reward = reward.to(device=dev, dtype=dtyp)

        # target = reward + gamma * critic_value_
        target = reward + self.gamma * critic_value_.squeeze(-1)
        target = target.view(self.batch_size, 1)  # (B, 1)

        agent.critic.train()
        agent.critic.optimizer.zero_grad()
        critic_loss = F.mse_loss(target, critic_value)
        critic_loss.backward()
        agent.critic.optimizer.step()

    def _train_actor(self, agent, idx: int, state: T.tensor, others_states: T.tensor, flag: bool, num_tiles: int) -> None:
        """
        Trains the actor network of a given agent.

        Computes the policy loss and applies gradient ascent to maximize expected Q-values.

        Args:
            agent: Agent whose actor is being trained
            idx (int): Index of the current agent
            state: Tensor of the agent's states
            others_states: Tensor of other agents' states
            flag (bool): Whether to add ghost agents
            num_tiles (int): Number of ghost agents
        """
        agent.critic.eval()
        agent.actor.optimizer.zero_grad()
        mu = agent.actor.forward(state)

        others_mus = self._get_others_actions(idx, others_states, network='target_actor')
        if flag:
            first_column_others_mus = others_mus[:, 0].unsqueeze(1)
            tiled_others_mus = T.cat([first_column_others_mus] * num_tiles, dim=1)
            others_mus = T.cat([others_mus, tiled_others_mus], dim=1)

        agent.actor.train()
        actor_loss = -agent.critic.forward(state, mu, others_states, others_mus)
        actor_loss = T.mean(actor_loss)
        actor_loss.backward()
        agent.actor.optimizer.step()
        agent.update_network_parameters()

    def _learn_from_memory(self, memory, idx: int, flag: bool, num_tiles: int) -> None:
        """
        Executes one learning step using the given memory buffer.

        Args:
            memory: Replay buffer (long or short)
            idx (int): Index of the agent being trained
            flag (bool): Whether to include ghost agents
            num_tiles (int): Number of ghost agents to add
        """
        if memory.mem_cntr < self.batch_size:
            return

        agent = self.agents[idx]
        device = agent.critic.device

        state, action, reward, others_states, others_actions = memory.sample_buffer(self.batch_size)
        state = T.tensor(state, dtype=T.float).to(device)
        action = T.tensor(action, dtype=T.float).to(device)
        reward = T.tensor(reward, dtype=T.float).to(device)

        if flag:
            others_states = self._create_ghosts(others_states, num_tiles)
            others_actions = self._create_ghosts(others_actions, num_tiles)

        others_states = T.tensor(others_states, dtype=T.float).to(device)
        others_actions = T.tensor(others_actions, dtype=T.float).to(device)

        agent.target_actor.eval()
        agent.target_critic.eval()
        agent.critic.eval()

        target_actions = agent.target_actor.forward(state)

        others_target_actions = self._get_others_actions(idx, others_states, network='target_actor')
        if flag:
            first_column = others_target_actions[:, 0].unsqueeze(1)
            tiled = T.cat([first_column] * num_tiles, dim=1)
            others_target_actions = T.cat([others_target_actions, tiled], dim=1)

        self._train_critic(agent, state, action, reward, others_states, others_actions,
                           target_actions, others_target_actions)

        self._train_actor(agent, idx, state, others_states, flag, num_tiles)

    def remember(self, state: T.tensor, action: T.tensor, reward: T.tensor, others_states: T.tensor, 
                 others_actions: T.tensor) -> None:
        """
        Stores a transition in both long-term and short-term memory buffers.

        Args:
            state, action, reward: Agent's transition tuple
            others_states, others_actions: Transitions of the other agents
        """
        self.memory.store_transition(state, action, reward, others_states, others_actions)
        self.short_memory.store_transition(state, action, reward, others_states, others_actions)

    def learn(self, idx: int, flag: bool=False, num_tiles: int=3) -> None:
        """
        Performs a learning step for the agent with index `idx`.

        Uses both the long-term and short-term memory buffers.

        Args:
            idx (int): Index of the agent being trained
            flag (bool): Whether to use ghost agents
            num_tiles (int): Number of ghost agents to add
        """
        self._learn_from_memory(self.memory, idx, flag, num_tiles)
        self._learn_from_memory(self.short_memory, idx, flag, num_tiles)