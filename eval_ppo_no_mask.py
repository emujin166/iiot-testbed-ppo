from _env import SimulationEnvironment
from _config import envConfiguration
from _graph import ConveyorGraph
from ppo_agent_no_mask import Agent
import matplotlib.pyplot as plt

#1. Set up the env 
config = envConfiguration()
graph = ConveyorGraph(config.conveyor)
env = SimulationEnvironment(config, graph)
env.setUpEnv()

#2. Hyperparameters
batch_size = 64
n_epochs = 4
gamma = 0.9995
alpha = 0.0002
policy_clip = 0.05
state = env.getActualState(0)

#3. Init Agent
agent = Agent(n_actions=env.config.env_ActionSpace, #how do the hyperparameters affect the learning 
              gamma=gamma,
              alpha=alpha,
              policy_clip=policy_clip,
              batch_size=batch_size,
              n_epochs=n_epochs,
              input_dims=[len(state)])

agent.load_models()

#4. Training
episodes = 10000
best_reward = 0
reward_history = []
all_rewards = 0
for ep in range(episodes):
    env.setUpEnv()
    done, duration, obs, mask, _ = env.start()
    states = []

    while not done:
        action, prob, val = agent.choose_action(obs, mask)
        done, duration, newobs, newmask, rest = env.step(action)

        states.append(state)
        obs = newobs
        mask = newmask
        
    reward, details = env.calcReward()
    additional_action_reward = details[-2]

    for k, state in enumerate(states):
        done = (k == (len(states)-1))
        #print("Done", len(states)) wozu ist done? und die Laenge der States sind immer anders
        all_rewards = reward + additional_action_reward[k]
        
    
    finished = details[-1] if details else 0
    print(f"Episode {ep} Reward per Episode {all_rewards:.2f} Duration: {duration} Produkte {finished}/64")

    reward_history.append(all_rewards)

x = [i+1 for i in range(len(reward_history))]
plt.plot(x, reward_history)
plt.xlabel("Episode")
plt.ylabel("Rewards")
plt.title("PPO Evaluation on Testbed Simulation (without Action Masking)")
plt.grid(True)
plt.savefig("/Users/macbookair/Desktop/researchUni/git/plot/eval_plot_no_mask_01")
plt.show()

    