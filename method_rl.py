from _env import SimulationEnvironment
from _config import envConfiguration
from _graph import ConveyorGraph
from ppo_agent import Agent
import pickle
import matplotlib.pyplot as plt
#print ('Einlesen des Datasets')
#with open ('/Users/macbookair/Desktop/researchUni/git/iiot-testbed/evalDataset.pkl', 'rb') as file:
#    dataSets = pickle.load(file) #pickle wird verwendet, um aus einer binären Datei ein serialisiertes Objekt zu lesen und zu desialisieren. 'rb' bedeutet Binärlesemodus

#1. Env initialisieren
config = envConfiguration() #Machinen slot als env
graph = ConveyorGraph(config.conveyor)
env = SimulationEnvironment(config=config, graph=graph)

#this part is very important, always set up the env before the training loop and inside the training loop
env.setUpEnv() # reset and setup the env

#2. Hyperparameter initiliasieren
batch_size = 64
n_epochs = 4
alpha = 0.0002
gamma = 0.9995
policy_clip = 0.05
state = env.getActualState(0) #1378 Dimensions aka states. KANN MAN NICHT ENV_STATE_SPACE nehmen?

#3. Agent initialisieren 
agent = Agent(n_actions=env.config.env_ActionSpace, 
              batch_size=batch_size, 
              alpha=alpha, 
              gamma=gamma, 
              n_epochs=n_epochs, 
              policy_clip=policy_clip, 
              input_dims=[len(state)])

#4. Learning loop
ep_rewards = []
reward_history = []
all_rewards = 0
print('Episode\tReward\tSteps')
episodes = 1000
for ep in range(episodes):
    actions = []
    probs = []
    vals = []
    dones = []
    states = []
    observations = []
    rewards = []
    masks = []

    #1.Reset the env
    env.setUpEnv()

    #2. Get obs
    done, duration, obs, mask, _  = env.start()
    steps = 0

    #3. Train the agent
    while not done:
        action, prob, val = agent.choose_action(obs, mask) #mask ist eine Liste von bools die sagt welche Aktionen gültig sind
        done, duration, newobs, newmask, rest = env.step(action)
        #Zwischenspeichern
        actions.append(action)
        probs.append(prob)
        vals.append(val)
        dones.append(done)
        observations.append(obs)
        states.append(state),
        masks.append(mask)

        obs = newobs #aktualisieren
        mask = newmask #aktualisieren
    
    reward, details = env.calcReward()
    additional_action_reward = details[-2]

    for k, state in enumerate(states):
        done = (k == len(states)-1)
        all_rewards = reward + additional_action_reward[k]
        agent.remember(observations[k], actions[k], probs[k], vals[k], all_rewards, done, masks[k])
    agent.learn() #man kann jede 100 Episoden lernen

    #wenn details welche Einträge hat, nimm das letzte (lenfinishedProdukts), sonst setze es zu 0
    finished = details[-1] if details else 0
    print(f'Episode: {ep} Reward per Ep: {all_rewards:.2f} Duration: {duration} Produkte {finished}/64')

    #Alle rewards 
    reward_history.append(all_rewards)


#5. Plot
x = [i+1 for i in range(len(reward_history))]
plt.plot(x, reward_history)
plt.xlabel('Episode')
plt.ylabel('Rewards')
plt.title('PPO on IIOT Testbed Simulation')
plt.grid(True)
plt.savefig('/Users/macbookair/Desktop/researchUni/git/plot/plot03')
plt.show()

#Bei RL sind die Strafen extrem hoch, hat wahrscheinlich damit zu tun, dass es ziemlich viele steps (duration) genommen wird
#Aber bei Heuristische Methode ist die Belohnung const bei -800 und duration const -86400 
#Der Grund: ?


#Die besten Gewichte pro 50 Episoden speichern und damit evaluirung machen 