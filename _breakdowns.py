import random
import numpy as np

class Breakdown:
    def __init__(self, config, deterministicRandom):
        self.config = config        
        self.deterministicRandom = deterministicRandom
        self.simulation_step = 0
        self.nextEventKey = 0
        self.eventCalender = {}

    def setUp(self):
        self.simulation_step = 0
        self.nextEventKey = 0
        self.eventCalender = {}
        self.fillEventCalender()

    def generate_random_failure(self, para):
        # Generiere den Zeitpunkt des Eintritts (exponentialverteilt)
        time_of_failure_exponential = random.expovariate(1 / para["exp_lambda"])  # Verwende die inverse Rate für expovariate
        
        # Generiere einen zufälligen Offset (normalverteilt)
        offset = max(0, random.gauss(para["mean_offset"], para["std_dev_offset"]))
        
        # Berechne den Zeitpunkt des Eintritts als Summe aus exponentialverteiltem Zeitpunkt und Offset
        time_of_failure = max(para["min_time"], min(para["max_time"], time_of_failure_exponential + offset))
        
        # Generiere die Dauer des Ausfalls (normalverteilt)
        duration_of_failure = max(para["min_duration"], min(para["max_duration"], random.gauss(para["mean_ausfallzeit"], para["std_dev_ausfallzeit"])))
        
        
        return int(time_of_failure), int(duration_of_failure)

    def sortEventCalender(self):
        self.eventCalender = dict(sorted(self.eventCalender.items()))

    def fillEventCalender(self):
        #print("fillEventCalender")
        #abstände = []
        #dauern = []
        for s in self.config.stations:
            operations = s["Operations"]
            for op in operations:                 
                akktumulierteZeit = 0
                lastFailure = 0
                while akktumulierteZeit < self.config.max_steps:

                    time_of_failure, duration_of_failure = self.deterministicRandom.getRandomNextRandomEvent()

                    akktumulierteZeit += time_of_failure
                    #abstand = akktumulierteZeit-lastFailure
                    #lastFailure = akktumulierteZeit
                    #abstände.append(abstand)
                    #dauern.append(duration_of_failure)
                    #print("S=",s["Id"] ,"Op=", op, "time_of_failure",  akktumulierteZeit, "duration_of_failure" ,duration_of_failure, "Abstand=", abstand)

                    event = [
                                self.nextEventKey,      # Key
                                s["Id"],                # StationId
                                op,                     # OpId
                                akktumulierteZeit,      # GeplanteEintrittsZeit
                                duration_of_failure,    # Dauer des Fehlers
                                0                       # realeEintrittsZeit
                            ]
                    if akktumulierteZeit not in self.eventCalender:
                        self.eventCalender[akktumulierteZeit] = []
                    self.eventCalender[akktumulierteZeit].append(event)
        
                    akktumulierteZeit += duration_of_failure 
                    self.nextEventKey += 1
                
        
        # Zum Debuggen Statische Events hinzufügen
        debugTime = 10
        if debugTime not in self.eventCalender:
            self.eventCalender[debugTime] = []
        #self.eventCalender[debugTime].append([self.nextEventKey, 'S1', '10', 10, 15, 0])
        #self.nextEventKey += 1
        #self.eventCalender[debugTime].append([self.nextEventKey, 'S6', '10', 10, 25, 0])
        #self.nextEventKey += 1
        

        ########## START - PLOTTEN der verteilunegn
        #import matplotlib.pyplot as plt
        #import numpy as np
        #from collections import Counter

        # Use a Counter to count the number of instances in x
        #c = Counter(abstände)
        #plt.bar(c.keys(), c.values())
        #plt.show()

        #c = Counter(dauern)
        #plt.bar(c.keys(), c.values())
        #plt.show()
        #die()
        ########## ENDE - PLOTTEN der verteilunegn
                        
        self.sortEventCalender()

    
    def getRemainingEvents(self, time):
        self.simulation_step = time
        self.sortEventCalender()
        keys = self.eventCalender.keys()
        relevantEvents = []
        for k in keys:
            if int(k) <= int(self.simulation_step):
                relevantEvents.append(self.eventCalender[k])
                #print(k, "Dieses Event ist relevant")
        #die()
        flattened_list = [item for sublist in relevantEvents for item in sublist]
        return flattened_list
    
    def setEventAsStarted(self, geplanteEintrittsZeit, key):

        content = self.eventCalender[geplanteEintrittsZeit]
        for k, e in enumerate(content):
            if e[0] == key:
                content[k][5] = self.simulation_step
                #print("t=",self.simulation_step,"Passendes Event=",key," gefunden und geplanteEintrittsZeit= ", geplanteEintrittsZeit, "aktualisert")
        self.eventCalender[geplanteEintrittsZeit] = content

    def setEventAsFinished(self, geplanteEintrittsZeit, key):
        content = self.eventCalender[geplanteEintrittsZeit]
        keyToRemove = None
        for k, e in enumerate(content):
            if e[0] == key:
                keyToRemove = k

        content.pop(keyToRemove)
        if len(content)==0:
            #print("Es verbleiben keine Events mehr unter diesem Key")
            self.eventCalender.pop(geplanteEintrittsZeit)
        else:
            #print("Es verbleiben noch Events, also die reduzierte Liste zuweisen")
            self.eventCalender[geplanteEintrittsZeit] = content




            	

