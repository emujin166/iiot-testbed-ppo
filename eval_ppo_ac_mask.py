from _env import SimulationEnvironment
from _config import envConfiguration
from _graph import ConveyorGraph
from ppo_agent_ac_mask import Agent
import matplotlib.pyplot as plt

#1. Set up the env and load the best weights 
config = envConfiguration()
graph = ConveyorGraph(config.conveyor)
env = SimulationEnvironment(config, graph)
env.setUpEnv()

#2. Hyperparameters 
batch_size = 64
alpha = 0.0002
gamma = 0.995
policy_clip = 0.05
n_epochs = 4
state = env.getActualState(0)

#3. Init Agent and load the weights
agent = Agent(n_actions=env.config.env_ActionSpace, 
              batch_size=batch_size,
              gamma=gamma,
              alpha=alpha,
              policy_clip=policy_clip,
              n_epochs=n_epochs,
              input_dims=[len(state)])

agent.load_models()

#4. Training 
episodes = 10000
all_reward = 0
best_reward = 0
reward_history = []
for ep in range(episodes):
    states = []

    env.setUpEnv()
    done, duration, obs, mask, _ = env.start()

    while not done:
        action, prob, val = agent.choose_action(obs,mask)
        done, duration, newobs, newmask, _ = env.step(action)

        obs = newobs
        mask = newmask

        reward, details = env.calcReward()
        additional_action_reward = details[-2]

        for k, state in enumerate(states):
            all_reward = reward + additional_action_reward[k]

        finished = details[-1] if details else 0
        print(f"Episode {ep} Reward per Episode {all_reward} Duration {duration} Produkte: {finished}/64")

        reward_history.append(all_reward)

x = [i+1 for i in range(len(reward_history))]
plt.plot(x, reward_history)
plt.title("PPO Evaluation on Testbed Simulation (with Action Masking)")
plt.xlabel("Episode")
plt.ylabel("Rewards")
plt.grid(True)
plt.savefig("/Users/macbookair/Desktop/researchUni/git/plot/eval_plot_ac_mask_01")
plt.show()
        
                