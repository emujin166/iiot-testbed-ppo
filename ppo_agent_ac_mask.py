#PPO Agent mit Action Masking on choose_action() and learn() function 

#Learning the policy to maximize the reward 
#Solving the Cartpole with PPO Clipping Objective
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.distributions.categorical import Categorical

#1. Memory class 
class PPOMemory:
    def __init__(self, batch_size): #constructor stores transitions 
        self.states = [] #env state the agent observed
        self.probs = [] #the probabilities assigned by the old policy when the action was taken
        self.vals = [] #critic values at time of acting
        self.actions = [] #what the agent actually did in those states
        self.rewards = [] #rewards from the env after each action
        self.dones = [] #making episode terminate
        self.masks = []
        self.batch_size = batch_size

    #sammle gespeicherte Arrays, berechne start_indices 
    #und gebe geschuffelte RANDOM mini-batches zurück
    def generate_batches(self): 
        n_states = len(self.states)
        batch_start = np.arange(0, n_states, self.batch_size)
        indices = np.arange(n_states, dtype=np.int64)
        #shuffling
        np.random.shuffle(indices)
        batches = [indices[i:i+self.batch_size] for i in batch_start]

        return np.array(self.states),\
                np.array(self.actions),\
                np.array(self.probs),\
                np.array(self.vals),\
                np.array(self.rewards),\
                np.array(self.dones),\
                np.array(self.masks),\
                batches 
    
    #append a data from a single timesteps 
    def store_memory(self, state, action, prob, val, reward, done, mask): 
        self.states.append(state)
        self.actions.append(action)
        self.probs.append(prob)
        self.vals.append(val)
        self.rewards.append(reward)
        self.dones.append(done)
        self.masks.append(mask)

    #clear the memory at every trajectory, weil die Daten nach einem Policy Update veraltet sind und neue Daten gebraucht werden 
    def clear_memory(self):
        self.states = []
        self.actions = []
        self.probs = []
        self.vals = []
        self.rewards = []
        self.dones = []
        self.masks = []

#2. Actor network: learns the policy bzw. given a state it outputs a probability distribution over actions (decides which action to take during rollout)
class ActorNetwork(nn.Module): #what action to take in each state?
    def __init__(self, n_actions, input_dims, alpha, fc1_dims=256, fc2_dims=256, chkpnt_dir=''):
        super(ActorNetwork, self).__init__()
        #file path for storing and saving weights (its restored seperately from critic weights)
        self.checkpoint_file = os.path.join(chkpnt_dir, '/Users/macbookair/Desktop/researchUni/uebung/rl/actor_weights') #store the path for saving weights
        #actor network 
        self.actor = nn.Sequential(
            nn.Linear(*input_dims, fc1_dims), #fully connected layers
            nn.ReLU(), #activation function for non linearity: if positive it outputs the input value, if negative it outputs 0
            nn.Linear(fc1_dims, fc2_dims), #hidden layer
            nn.ReLU(),
            nn.Linear(fc2_dims, n_actions), #output layer producing logits 
            nn.Softmax(dim=1) #softmax activation, which normalizes(converts) outputs(logits) into probabilities. Outputs discrete (0,1,2)
        )
        self.optimizer = optim.Adam(self.parameters(), lr=alpha) #Adam optimizer (adjusts LR during training)
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.to(self.device)

    #forward pass
    def forward(self,state):  #takes the state as input
        dist = self.actor(state)
        dist = Categorical(dist) #outputs a probability distribution over actions
        return dist
    
    def save_checkpoint(self):
        torch.save(self.state_dict(), self.checkpoint_file)

    def load_checkpoint(self):
        self.load_state_dict(torch.load(self.checkpoint_file, weights_only=True))

#3. Critic network is responsible for estimatic value function V(st). Means: given a state, how god is it expected to be( erwarteter Return)
#if only the actor is trained, learning would be too 'difficult'. So we use critic to reduce the variance in the policy gradient 
class CriticNetwork(nn.Module): #how good is the state?
    #critic network takes only state as input
    def __init__(self, input_dims, alpha, fc1_dims=256, fc2_dims=256, chkpt_dir=''):
        super(CriticNetwork, self).__init__()

        #file path for storing and saving weights (its restored seperately from actor weights)
        self.checkpoint_file = os.path.join(chkpt_dir, '/Users/macbookair/Desktop/researchUni/uebung/rl/critic_weights')
        self.critic = nn.Sequential(
            nn.Linear(*input_dims, fc1_dims), 
            nn.ReLU(), #activation function for non-linearity
            nn.Linear(fc1_dims, fc2_dims), #hidden layer
            nn.ReLU(),
            nn.Linear(fc2_dims, 1)
        )

        self.optimizer = optim.Adam(self.parameters(), lr=alpha) #optimizer for gradient updates
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.to(self.device)
    
    def forward(self, state):
        value = self.critic(state) #outputs single value per state
        return value
    
    #save and load critic weights 
    def save_checkpoint(self):
        torch.save(self.state_dict(), self.checkpoint_file)

    def load_checkpoint(self):
        self.load_state_dict(torch.load(self.checkpoint_file, weights_only=True))

#4. Agent network 
class Agent:
    def __init__(self, n_actions, input_dims, gamma=0.99, alpha = 0.0003, 
                 gae_lambda = 0.97, policy_clip=0.1, batch_size=64, n_epochs=10):
        
        #hyperparameters as attributes
        self.gamma = gamma
        self.policy_clip = policy_clip
        self.n_epochs = n_epochs
        self.gae_lambda = gae_lambda

        #actor and critic network building (value function)
        self.actor = ActorNetwork(n_actions, input_dims, alpha) #outputs action probabilities 
        self.critic = CriticNetwork(input_dims, alpha) #only state(observation in this case), outputs state values 
        self.memory = PPOMemory(batch_size) #replay buffer memory (stores state, action, old probab, value estimate, reward, done)

    #saves one transition into memory
    def remember(self, state, action, prob, val, reward, done, mask):
        self.memory.store_memory(state, action, prob, val, reward, done, mask)
    
    #save and load trained parameters 
    def save_models(self):
        print('... saving models ...')
        self.actor.save_checkpoint()
        self.critic.save_checkpoint()

    def load_models(self):
        print('... loading models ...')
        self.actor.load_checkpoint()
        self.critic.load_checkpoint()
    
    #takes the env observation and chooses an action
    """def choose_action(self, observation, mask):
        state = torch.tensor([observation], dtype=torch.float).to(self.actor.device) #torch wraps the 1d into 2d tensor then moves it to whatever device the actor is on 

        #Nur Trues filtern und mask anwenden (nur die valide Aktionen weitergeben) dist, val
        dist = self.actor(state) #gebe state an der Actor Funktion über
        value = self.critic(state) #gebe state an der Critic Funktion über
        action = dist.sample() #randomly picks an action according to the probabilities the actor gave

        #make the outputs simple numbers-not tensors
        probs = torch.squeeze(dist.log_prob(action)).item() #log-probab of the action (later for ppo)
        action = torch.squeeze(action).item() #the actual action 
        value = torch.squeeze(value).item() #the critics guess of how good the state is

        return action, probs, value"""
    
    def choose_action(self, observation, mask):
        # Observation → Tensor auf richtiges Device
        state = torch.tensor([observation], dtype=torch.float).to(self.actor.device)

        # Actor gibt eine Wahrscheinlichkeitsverteilung über alle möglichen Aktionen aus
        dist = self.actor(state)
        value = self.critic(state) #Critic gibt den Wert des aktuellen Zustands

        # Konvertiere Verteilung in Wahrscheinlichkeiten (z. B. softmax über logits). Probs hat die unmaskierten bools
        probs = dist.probs.clone().detach()  # oder dist.logits wenn dein Actor logits liefert

        # Mask anwenden: ungültige Aktionen auf 0 setzen
        mask_tensor = torch.tensor(mask, dtype=torch.bool).to(self.actor.device)
        mask_tensor = mask_tensor.unsqueeze(0)
        probs[~mask_tensor] = 0  # alle False auf 0 setzen und ungültige entfernen

        # Wenn alle 0 sind, gib Warnung aus (sollte nie passieren)
        if probs.sum() == 0:
            print("No valid actions available!")
            probs[mask_tensor] = 1.0

        # Normalisieren (sonst keine gültige Verteilung mehr)
        probs = probs / probs.sum(dim=1, keepdim=True)

        # Neue Verteilung mit maskierten Wahrscheinlichkeiten
        masked_dist = torch.distributions.Categorical(probs)

        # Aktion gemäß dieser gültigen Verteilung ziehen
        action = masked_dist.sample()
        log_prob = masked_dist.log_prob(action)

        # In einfache Zahlen umwandeln
        action = torch.squeeze(action).item()
        log_prob = torch.squeeze(log_prob).item()
        value = torch.squeeze(value).item()

        return action, log_prob, value

    
    #where ppo updates its networks 
    def learn(self): 
        for _ in range(self.n_epochs):
            state_arr, action_arr, old_prob_arr, vals_arr,\
            reward_arr, dones_arr, mask_arr, batches, = self.memory.generate_batches() #jeder 20 Episoden neue batches bekommen 

            #1. calculate advantage(how much the action was better than compared to avg expectation)
            values = vals_arr
            advantage = np.zeros(len(reward_arr), dtype=np.float32)

            #calculate gae(generalized advantage estimation): how much better was this action than expected?
            for i in range(len(reward_arr)-1):
                discount = 1 
                a_t = 0
                for k in range(i, len(reward_arr)-1):
                    a_t += discount*(reward_arr[k] + self.gamma*values[k+1] * (1-int(dones_arr[k])) - values[k])
                    discount *= self.gamma * self.gae_lambda
                advantage[i] = a_t
            
            #2. convert it to pytorch tensors and put it on cpu/gpu
            advantage = torch.tensor(advantage).to(self.actor.device)
            values = torch.tensor(values).to(self.actor.device) 

            #3. loop through mini batches and choose a mini batch of states, actions and old log probs
            for batch in batches:
                states = torch.tensor(state_arr[batch], dtype=torch.float).to(self.actor.device)
                old_probs = torch.tensor(old_prob_arr[batch]).to(self.actor.device)
                actions = torch.tensor(action_arr[batch]).to(self.actor.device)
                batch_mask = torch.tensor(mask_arr[batch], dtype=torch.bool).to(self.actor.device)

                #4. get new predictions
                dist = self.actor(states) #! nur bei available Aktionen berechnen
                critic_value = self.critic(states)
                critic_value = torch.squeeze(critic_value)

                #5. gültige Aktionen maskieren
                probs = dist.probs.detach().clone()
                probs[~batch_mask] = 0 # nur die gültigen Aktionen hier speichern
                probs = probs / probs.sum(dim = 1, keepdim = True) # normalisieren
                masked_dist = torch.distributions.Categorical(probs)

                #5. calculate prob ratios - how much did the prob of this action changed since last update
                new_probs = masked_dist.log_prob(actions)
                prob_ratio = (new_probs - old_probs).exp()

                #6. ppo clipping
                weighted_probs = advantage[batch] * prob_ratio
                #torch.clamp clamps all elements in input into the range min,max
                weighted_clipped_probs = torch.clamp(prob_ratio, 1-self.policy_clip, 1+self.policy_clip) * advantage[batch]
                #clipped surrogate loss-picks the smaller one-prevents from the policy changing too much in one step
                actor_loss = -torch.min(weighted_probs, weighted_clipped_probs).mean() 

                #7. critic loss with MSE
                returns = advantage[batch] + values[batch]
                critic_loss = (returns-critic_value)**2
                critic_loss = critic_loss.mean()

                #8. total loss & update both networks with Adam
                total_loss = actor_loss + 0.5*critic_loss
                self.actor.optimizer.zero_grad()
                self.critic.optimizer.zero_grad()
                total_loss.backward() #built in function from tensor
                self.actor.optimizer.step()
                self.critic.optimizer.step()

        #9. clear the memory and throw away the old data cuz we already updated the policy 
        self.memory.clear_memory()               

#Error: IndexError: The shape of the mask [64, 0] at index 1 does not match the shape of the indexed tensor [64, 30] at index 1s
#Das Problem: Weil die Batches sich verändern (und dabei auch die Aktionen), muss die Maskierung ebenfalls zugehörige Aktionen von jeweiligen Batches maskieren. Deswegen statisch Mask zuweisen funktioniert nicht

#how to measure efficiency of action masking in ppo: durch reward?