from _config import envConfiguration
from _graph import ConveyorGraph
from _env import SimulationEnvironment
from method_heuristic import *
import pickle
import matplotlib.pyplot as plt
#####################################




# Setup the environment
myConfig = envConfiguration()
myConfig.askAgainIfMalfunctionWasDetected = False
myGraph = ConveyorGraph(myConfig.conveyor) # describe the conveyor graph and is responsible for the navigation
myGraph.plot_conveyor_graph()
myEnv = SimulationEnvironment(myConfig, myGraph) # describe the environment




evalRewards = []
evalMeanOverallProduction = []
evalMeanOverallWaiting = []
evalMeanOverallTransport = []
evalMeanOverallSetUp = []
evalMeanProductionTime = []
evalMeanFailureTime = []
evalDuration = []
evalFinishedProducts = []

#######################
# Episoden aus Dataset
print("Einlesen des Datasets")
with open('evalDataset.pkl', 'rb') as f:
    dataSets = pickle.load(f)

for i, d in enumerate(dataSets):
    myEnv.importStates(d)
#######################

#######################
# Zufällige Episoden 
#for i in range(myConfig.ammount_of_eval_episodes):
#    myEnv.setUpEnv()
#######################    

    done, duration, state, availableActionSpace, rest = myEnv.start()
    while not done:
        
        # Annahme: Die Switche funktionieren immer
        #action = chooseShortestPath(myEnv, rest)
        #action = chooseLongestPath(myEnv, rest)
        action = get_random_true_index(availableActionSpace)

        # Action 
        done, duration, state, availableActionSpace,rest = myEnv.step(action) #0-29 
        #state-obs space
        #availableaction - action space

    # Calc Reward
    reward, [meanOverallProduction, meanOverallWaiting, meanOverallTransport, meanOverallSetUp, meanProductionTime, meanOverallFailure, additional_action_reward, finishedProducts] = myEnv.calcReward()
    evalRewards.append(reward)
    evalMeanOverallProduction.append(meanOverallProduction)
    evalMeanOverallWaiting.append(meanOverallWaiting)
    evalMeanOverallTransport.append(meanOverallTransport)
    evalMeanOverallSetUp.append(meanOverallSetUp)
    evalMeanProductionTime.append(meanProductionTime)
    evalMeanFailureTime.append(meanOverallFailure)
    evalDuration.append(duration)
    evalFinishedProducts.append(finishedProducts)
    print("############### - Episode=" , i, "Reward=", reward, "duration="+str(duration), "finished="+str(finishedProducts), "CT="+str(meanProductionTime), "F="+str(meanOverallFailure), "W="+str(meanOverallWaiting), "T="+str(meanOverallTransport), "S="+str(meanOverallSetUp))


print("#############################################")
print("#############################################")
print("#############################################")
print(f"finishedProducts= {finishedProducts}/64")
print("evalRewards=", sum(evalRewards) / len(evalRewards))
print("evalMeanOverallProduction=", sum(evalMeanOverallProduction) / len(evalMeanOverallProduction))
print("evalMeanOverallWaiting=", sum(evalMeanOverallWaiting) / len(evalMeanOverallWaiting))
print("evalMeanOverallTransport=", sum(evalMeanOverallTransport) / len(evalMeanOverallTransport))
print("evalMeanOverallSetUp=", sum(evalMeanOverallSetUp) / len(evalMeanOverallSetUp))
print("evalMeanProductionTime=", sum(evalMeanProductionTime) / len(evalMeanProductionTime))
print("evalMeanFailureTime=", sum(evalMeanFailureTime) / len(evalMeanProductionTime))
print("evalDuration=", sum(evalDuration) / len(evalDuration))
print("evalFinishedProducts=", sum(evalFinishedProducts) / len(evalFinishedProducts))

x = [i+1 for i in range(len(evalRewards))]
plt.plot(x, evalRewards)
plt.xlabel('Episode')
plt.ylabel('Rewards')
plt.title('PPO on IIOT Testbed Simulation')
plt.grid(True)
plt.savefig('/Users/macbookair/Desktop/researchUni/git/plot/plot4')
plt.show()