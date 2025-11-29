import matplotlib.pyplot as plt
import numpy as np
import pickle
import random
import subprocess
import torch as T #why white?

def die(text = ""):
    print("############################################################################")
    print()
    print()
    print()
    raise ValueError(text)

def writeLineInFile(file, content):
    ausgabe = ""
    for c in content:
        print(c)
        ausgabe += c + "\n"

    f = open(file+".txt", "a")
    f.write(ausgabe)
    f.close()

def logCheckpoint(filename, text):
    f = open(str(filename) + ".txt", "a")
    f.write(text + '\n')
    f.close()

def plot_learning_curve_reward(x, scores, figure_file, title):
    running_avg = np.zeros(len(scores))
    for i in range(len(running_avg)):
        running_avg[i] = np.mean(scores[max(0, i-50):(i+1)])
    plt.plot(x, running_avg)
    plt.title(str(title))
    plt.savefig(figure_file)
    plt.close('all')

def find_least_used_gpu():
    device = 'cpu'
    if T.cuda.is_available():
        # Ruft die Ausgabe von nvidia-smi ab
        smi_output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader'],
            encoding='utf-8'
        )
        # Umwandlung der Ausgabe in eine Liste der verfügbaren Speicherwerte
        gpu_memory = [int(x) for x in smi_output.strip().split('\n')]
        # Findet die GPU-Index mit dem meisten freien Speicher
        most_free_memory_idx = gpu_memory.index(max(gpu_memory))
        device = T.device(f'cuda:{most_free_memory_idx}')
    return device

def statsionNameToAgentId(sName):
    if str(sName) == "False":
        return 0
    return int(sName.replace("S", ""))-1