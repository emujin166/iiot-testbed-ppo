import random
import numpy as np
import matplotlib.pyplot as plt
import copy
import pickle

class DeterministicRandom:
    def __init__(self, config):
        self.config = config
        self.indexNextOperationFluctuations = -1
        self.randomOperationFluctuations = []

        self.poisson_event_entry_times_lookup = config.poisson_event_entry_times_lookup
        self.indexNextEvent= -1
        self.randomEventEntryTimes = []
        self.randomEventDurationTimes = []


    def setUp(self):
        # OperationFluctuations
        for i in range(self.config.ammount_of_OperationFluctuations):
            self.randomOperationFluctuations.append(
                random.randint(-self.config.uncertainty_in_operation_times, 
                                self.config.uncertainty_in_operation_times))
                  
        # Generate the Events
        #t = []
        lenLookUp = len(self.poisson_event_entry_times_lookup)-1
        for i in range(self.config.ammount_of_FailureEvents):
            #t.append(i)
            index = random.randint(0, lenLookUp)
            self.randomEventEntryTimes.append(self.poisson_event_entry_times_lookup[index])
            self.randomEventDurationTimes.append(self.generate_event_length())
        
        #new = copy.deepcopy(self.randomEventEntryTimes)
        #new.sort()
        #plt.plot(t, new)
        #plt.xlabel('Events')
        #plt.ylabel('Time (Seconds)')
        #plt.title('Distribution function of the failures entry times (for 100,000 events)')
        #plt.grid()
        #plt.show()
            
    def getRandomNextOperationFluctuations(self):
        self.indexNextOperationFluctuations += 1
        if self.indexNextOperationFluctuations > len(self.randomOperationFluctuations)-1:
            self.indexNextOperationFluctuations = 0
        return self.randomOperationFluctuations[self.indexNextOperationFluctuations]
    
    def getRandomNextRandomEvent(self):
        self.indexNextEvent += 1
        if self.indexNextEvent > len(self.randomEventEntryTimes)-1:
            self.indexNextEvent = 0
        return self.randomEventEntryTimes[self.indexNextEvent] , self.randomEventDurationTimes[self.indexNextEvent] 


    def generate_event_length(self):
        min_length = 30     #30     #60
        max_length = 720    #720    #1440
        mean_length = (max_length + min_length) / 2
        std_deviation = (max_length - min_length) / 6  # Wähle eine passende Standardabweichung
        event_length = np.random.normal(loc=mean_length, scale=std_deviation)        
        # Stelle sicher, dass die Längen im Intervall [min_length, max_length] liegen
        event_length = np.clip(event_length, min_length, max_length)        
        return event_length

