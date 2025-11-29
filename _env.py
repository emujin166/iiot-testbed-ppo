import random
import copy

from _utilities import *
from _env_resources import Carrier
from _mes import ManufacturingExecutionSystem
from _breakdowns import Breakdown
from _deterministicRandom import DeterministicRandom
import networkx as nx
from collections import Counter


class SimulationEnvironment:
    def __init__(self, config, graph):
        self.config = config
        self.graph = graph
        self.mes = ManufacturingExecutionSystem(config)
        self.random = DeterministicRandom(config)
        self.breakdowns = Breakdown(config, self.random)

        self.switch_tokens = {}
        self.bypass_tokens = {}

        for slot in self.config.conveyor:
            if slot[2] == "intersection":
                self.switch_tokens[slot[5]] = False
        for slot in self.config.conveyor:
            if slot[2] == "bypass":
                self.bypass_tokens[slot[5]] = False
        
        self.simulation_step = 0
        self.stations = None
        self.conveyor = None
        self.needDecisionFor = {}
        self.currentInquiryOfTheAgent = {}
        self.finishedProducts = []
        # Decision History
        self.DecisionId = 0
        self.decisionTracking = {}
        self.apply_addtional_desc_old = []
        self.apply_addtional_desc_new = []
        self.observeCar = None
               
    def resetVars(self):
        self.simulation_step = 0
        self.stations = None
        self.conveyor = None
        self.stations = copy.deepcopy(self.config.stations)
        self.conveyor = copy.deepcopy(self.config.conveyor)

        self.needDecisionFor = {}
        self.currentInquiryOfTheAgent = {}

        self.mes = None
        self.breakdowns = None
        self.random = None
        self.mes = ManufacturingExecutionSystem(self.config)
        self.random = DeterministicRandom(self.config)
        self.breakdowns = Breakdown(self.config, self.random)


        self.updateSimulationTime(0)
        self.mes.setUpMES()
        self.setUpCarriers()
        self.finishedProducts = []
        
        self.random.setUp()
        self.breakdowns.setUp() # Verlangt, dass random setuped ist

        # Decision History
        self.nextDecisionId = 0
        self.decisionTracking = {}
        self.apply_addtional_desc_old = []
        self.apply_addtional_desc_new = []
        self.observeCar = None
        
    def getNextDecisionIdAndCountUp(self):
        retVal = self.nextDecisionId
        self.nextDecisionId += 1
        return retVal
    
    def generate_state_count_per_decision(self, target_decision_id):
        state_count_per_decision = {}

        for decisions in self.decisionTracking.values():
            for decision_id, decision_data in decisions.items():
                if decision_id == target_decision_id:
                    state_count = {"W": 0, "T": 0, "S": 0, "L": 0, "U": 0, "P": 0, "A": 0, "F": 0}
                    for time_point, state in decision_data.items():
                        if state in state_count:
                            state_count[state] += 1
                    state_count_per_decision[decision_id] = state_count

        return state_count_per_decision
    
    def generateCarrierHistoryEntry(self, car, state):
        # Alte Histroie übernehmen
        car.update_history(self.simulation_step, state)

        # decisionTracking = {
        #   10: {     #Carrier = 10
        #           300:    {   # DecisionId
        #                       86000 : "W",     #Zeitpunkt 86000
        #                       86001 : "W",     #Zeitpunkt 86001
        #                   }
        #       }
        # }

        # neue Historie
        currentDecisionId = car.getCurrentDecisionId()
        carId = car.id
        currentTime = self.simulation_step
        if currentDecisionId != None:
            # Der Carrier agiert, weil eine Entscheing getroffen wurde
            # (Falls der Wert==None, dann weil kein Auftrag zugewiesen)
            if car.id not in self.decisionTracking:
                self.decisionTracking[carId] = {}
            
            if currentDecisionId not in self.decisionTracking[carId]:
                self.decisionTracking[carId][currentDecisionId] = {}

            
            self.decisionTracking[carId][currentDecisionId][currentTime] = state
            
            
                


    def setUpCarriers(self):
        # Prepare History for carriers
        emptyHistory = []
        for i in range(self.config.max_steps+10):
            emptyHistory.append(None)
        # Generate Carrier and palce on the conveyor belt
        for id in range(self.config.ammount_of_carriers):
            car = Carrier(id)
            car.update_all_switch_tokens(self.switch_tokens)
            car.update_all_bypass_tokens(self.bypass_tokens)
            car.update_whole_history(emptyHistory)

            foundFreeSlot = False
            while foundFreeSlot != True:
                slotID = random.randint(0, len(self.conveyor)-1)
                if self.conveyor[slotID][6] == None and (self.conveyor[slotID][2] == "station" or self.conveyor[slotID][2] == "normal"):

                    # Leeren Slot gefunden, Carrier zuweisen
                    self.conveyor[slotID][6] = car
                    foundFreeSlot = True
                    #print("Carrier", car.id  ," auf Slot:", slotID, " zugewiesen (Typ=" ,self.conveyor[slotID][2], ")")

    def getUncertainOperationTime(self, opTime):   
        retVal = opTime + self.random.getRandomNextOperationFluctuations()
        #print("-- getUncertainOperationTime in=", opTime, "out=", retVal)   
        return retVal
  

    def updateSimulationTime(self, t):
        self.simulation_step = t
        self.mes.updateSimulationTime(t)


    def setUpEnv(self):
        #print("### -> Begin setup ")
        self.resetVars()
        #print("### <- End setup ")
    
    def start(self):
        return self.stepUntilNextDecision()
    
    def exportStates(self):
        data = {
            "simulation_step"   : self.simulation_step,
            "stations"          : self.stations,
            "conveyor"          : self.conveyor,
            "needDecisionFor"   : self.needDecisionFor,
            "currentInquiryOfTheAgent"  : self.currentInquiryOfTheAgent,
            "mes"               : self.mes,
            "finishedProducts"  : self.finishedProducts,
            "breakdowns"        : self.breakdowns,
            "random"            : self.random,
            "nextDecisionId"    : self.nextDecisionId,
            "decisionTracking"  : self.decisionTracking
        }
        return data 
    
    def importStates(self, newSelf):
        self.simulation_step            = copy.deepcopy(newSelf["simulation_step"])
        self.stations                   = copy.deepcopy(newSelf["stations"])
        self.conveyor                   = copy.deepcopy(newSelf["conveyor"])
        self.needDecisionFor            = copy.deepcopy(newSelf["needDecisionFor"])
        self.currentInquiryOfTheAgent   = copy.deepcopy(newSelf["currentInquiryOfTheAgent"])
        self.mes                        = copy.deepcopy(newSelf["mes"])
        self.finishedProducts           = copy.deepcopy(newSelf["finishedProducts"])
        self.breakdowns                 = copy.deepcopy(newSelf["breakdowns"])
        self.random                     = copy.deepcopy(newSelf["random"])
        self.nextDecisionId             = copy.deepcopy(newSelf["nextDecisionId"])
        self.decisionTracking           = copy.deepcopy(newSelf["decisionTracking"])
        


    def getActualState(self, askingSlot): 
        # State=
        #       |----------------- Slot --------------|
        #       |- Slot that requests a decision
        #       |- Slot is occupied with a Carrier
        #       |- Product on Carrier is family A
        #       |- Product on Carrier is family B
        #       |- Upcoming operations -> Op10
        #       |- Upcoming operations -> Op20
        #       |- Upcoming operations -> Op30
        #       |- Upcoming operations -> Op40
        #       |- Upcoming operations -> Op50
        #       |- Upcoming operations -> Op60
        #       |- Upcoming operations -> Op70
        #       |- Upcoming operations -> Op80
        #       |- Upcoming operations -> Op90

        #       |----------------- Maschine --------------|
        #       |- Maschine is in State Idel
        #       |- Maschine is quipped with product family A
        #       |- Maschine is quipped with product family B
        #       |- For each offered Operation 
        #         |- Operation available

        allBits = []
        #   0   Slot that requests a decision
        #   1   Slot is occupied
        #   2   Product family = A
        #   3   Product family = B
        #   4.. all Ops

        for slotKey, slot in enumerate(self.conveyor): 

            allBits.append(int(slotKey == askingSlot))

            car = slot[6]
            if car != None:             
                # Slot is occupied
                allBits.append(1)   
                # Add all possible product families
                for f in self.config.product_families:                    
                    if car.getProductFamily() == f:
                        allBits.append(1)
                    else:
                        allBits.append(0)
                # Add all possible operations    
                for op in self.config.all_possible_operationss:
                    if car.order != None:
                        allBits.append(int(op in car.order.workplan))
                    else:
                        allBits.append(0)
                    
            else:
                # Slot is not occupied
                allBits.append(0)   
                # Add all possible product families
                for f in self.config.product_families:
                    allBits.append(0)
                # Add all possible operations    
                for wp in self.config.all_possible_operationss:
                    allBits.append(0)

        for stationKey, station in enumerate(self.stations): 
            if station["State"] == "Idel":
                # Maschine is in State Idel
                allBits.append(1)   
            else:                
                # Maschine is not in State Idel
                allBits.append(0) 

            # Add all possible product families
            for f in self.config.product_families:  
                if station["EquippedProductFamily"] == f:
                    allBits.append(1)
                else:
                    allBits.append(0)
            
            for OpId in station["Operations"]:
                if self.stations[stationKey]["Operations"][OpId]["BreakdownState"]:
                    allBits.append(0) # not available, as in malfunction
                else:
                    allBits.append(1) # available, as not in malfunction
                            
        
        #print(len(allBits))
        #die(allBits)
        return allBits

    def getAvailableActionSpace(self): #action space
        carId = list(self.currentInquiryOfTheAgent.keys())[0]

        self.currentInquiryOfTheAgent[carId]["allPathOptions"] = []
        nextOp = self.currentInquiryOfTheAgent[carId]["nextOp"]
        start_node = self.currentInquiryOfTheAgent[carId]["location"] 
        stationsOptionsIds = []
        stationsOptionsLocations = []
        allPathOptionsForAgent = []
        for k, station in enumerate(self.config.stations):
            #!!*********Von str auf int geändert*********
            #if str(nextOp) in station["Operations"].keys(): Änderung 
            if nextOp in station["Operations"]:
                # Die Option wird von der Station angeboten
                # if station["Operations"][str(nextOp)]["BreakdownState"] == False: # Die Operation hat keinen Störungsfall und ist eine Alternative
                # Der Agent darf auch Stationen wählen, die aktuell in Störung sind, dann muss er halt mit der Entscheidung leben....    
                stationsOptionsIds.append(k)
                stationsOptionsLocations.append(station["Location"])
        #print("-- Optionen für die nextOp=", nextOp , "sind=", stationsOptionsIds, "auf Slots" , stationsOptionsLocations)

        # Nun ermitteln welche Pfade zur Verfügung stehen
        # Beispielaufruf für die Pfade zwischen den Stationen 0 und 72
        for key, target_node in enumerate(stationsOptionsLocations):         
            alternative_paths = self.graph.find_paths_with_restrictions(start_node, target_node)
            #print(start_node,"->", target_node, "alternative_paths", alternative_paths)
            if len(alternative_paths) == 0:
                #print("LEN alternative_paths = 0")
                alternative_paths = [[]]
            for alt in alternative_paths:
                #print("AltPath=" , alt)
                switches = []
                for a in alt:
                    try:
                        if a[1] != None:
                            switches.append(a[1])
                    except:
                        print("Fehler")
                switches.sort()
                
                optKey = self.graph.all_possible_path_options.index(switches)
                #print("stationsOptionsLocations=", key, "index=", optKey)
                optKey += key*len(self.graph.all_possible_path_options)
                
                allPathOptionsForAgent.append(optKey)
                self.currentInquiryOfTheAgent[carId]["allPathOptions"].append([optKey, stationsOptionsIds[key], target_node, switches, start_node])
        allPathOptionsForAgent.sort()

        if len(allPathOptionsForAgent) == 0:
            print("keine allPathOptionsForAgent")
            #print("start_node", start_node)
            #print("nextOp", nextOp)
            #print("stationsOptionsIds", stationsOptionsIds)
            #print("stationsOptionsLocations", stationsOptionsLocations)
            die() 

        retVal = []
        for i in range(self.config.env_ActionSpace):
            retVal.append(i in allPathOptionsForAgent)
        #print(retVal)
        
        return retVal, [stationsOptionsIds, stationsOptionsLocations]



    def checkIfADecisionForAnEmptyCarrierIsNeeded(self):
        retval = False
        for slotKey, slot in enumerate(self.conveyor):
            car = slot[6]
            if car != None and (car.product == None) and (car.state == "belt") and (slot[2] == "station"):  
                #print("-- Found an empty Carrier C=", car.id)

                # Noch kein Produkt auf dem Carrier, also eines zuweisen
                p, o = self.mes.getAndStartNextJob()
                if p == None and o == None:
                    # Keine weiteren Jobs mehr vorhanden
                    return False
                retval = True
                car.placeProductOnCarrier(p, o)
                car.update_all_switch_tokens(self.switch_tokens)
                car.update_all_bypass_tokens(self.bypass_tokens)
                nextOp = p.setNextOperation(o.workplan, self.simulation_step)
                if nextOp == None:
                    print("Diese Nachricht sollte niemals sichtbar sein, die nächste Operation ist false")                       
                self.needDecisionFor[car.id] = {
                    "carId"     : car.id,
                    "location"  : slot[0],
                    "station"   : slot[5],
                    "nextOp"    : nextOp
                }
                car.update_lastProcessing(self.simulation_step)
                #print("-- t=",self.simulation_step," Neuer Job zugewiesen - Carrier=",car.id ,"an Station=" , slot[5], "Slot=", slot[0], "nextOp=" , nextOp)
        return retval
    
    def getStationKey(self, stationId):
        for k,station_data in enumerate(self.stations):
            if station_data["Id"] == stationId:
                return k

    def shouldAskAgain(self, car, nextDestination, slot):


        newDecisionNeeded = False

        nextOp = car.product.getNextOperation()
        prodId = car.product.getProductId()

        slotDest = self.conveyor[nextDestination]
        stationKeyDest = self.getStationKey(slotDest[5])

        #BreakdownState = self.stations[stationKeyDest]["Operations"][str(nextOp)]["BreakdownState"] Änderung
        BreakdownState = self.stations[stationKeyDest]["Operations"][nextOp]["BreakdownState"]
        stationState = None
        stationKey = None
        for sKey, station in enumerate(self.stations):
            if (station["Id"] == slot[5]):
                stationState = station["State"]
                stationKey = sKey
                break


        if BreakdownState == True and (stationState == "Idel"): 
            #print("") 
            #print("T="+ str(self.simulation_step)+ " BreakdownState für Prod="+str(prodId)+" Op=" + str(nextOp) + "erkannt, soll der Carrier="+str(car.id)+"(Pos="+str(slot[0])+", askedAgainState="+str(askedAgainState)+" StationState="+str(stationState)+")  wirklich dahin (Station="+str(slotDest[5])+" - Slot="+str(nextDestination)+"?")
            car.setAskedAgainTrue()
            car.update_all_switch_tokens(self.switch_tokens)
            car.update_all_bypass_tokens(self.bypass_tokens)
            #print("carid=",car.id," car.getAskedAgain()", car.getAskedAgain())


            self.stations[stationKey]["Carrier"] = car
            self.stations[stationKey]["State"] = "AskAgain"
            #print("T="+ str(self.simulation_step)+ " BreakdownState - Station auf AskAgain gesetzt")
            self.needDecisionFor[car.id] = {
                "carId"     : car.id,
                "location"  : slot[0],                      #start_node
                "station"   : slot[5],
                "nextOp"    : nextOp
            }
            
            car.changeStateToMachine()

            if self.observeCar == None:
                self.observeCar = car.id
            
            newDecisionNeeded = True
        
        return newDecisionNeeded
    

    def getAllPrecursor(self, currentlocation, input=""):
        out = input 

        currentCar = self.conveyor[currentlocation][6]
        if currentCar != None:
            typ = self.conveyor[currentlocation][2]
            if typ == "station":
                #Ermittle den State
                getProductId = ""
                for stationKey, station in enumerate(self.stations):
                    if (station["Location"] == currentlocation):
                        state = station["State"]
                        #if state == "Idel" and station["Carrier"] != None:
                typ += "("+state+")"

            try:
                getProductId = currentCar.product.getProductId()
            except:
                getProductId = None
            
            carState = currentCar.state

            out += " -> ["+str(currentlocation)+"-"+ str(typ) + "]=" + str(self.conveyor[currentlocation][6].id) + "(Pid="+ str(getProductId) + " carState="+ str(carState) + ")" 


        straight = self.conveyor[currentlocation][1][0]
        straightCar = self.conveyor[straight][6]
        
        free = True
        if straightCar == None:
            out += " -> ["+str(straight)+"]=Frei" 
        else:
            free = False

        
        if free == False:
            #rufe Rekursiv auf
            out = self.getAllPrecursor(straight, out)
            
        return out
        
    def stepUntilNextDecision(self):
        #Gibt folgende Liste zurück
        # 0 = Finished
        # 1 = duration
        # 2 = actualState
        #print()
        #print("### -> Begin stepUntilNextDecision ###")
        while self.mes.productionFinished() == False and self.simulation_step < self.config.max_steps:
            
            self.checkBreakdowns()

            self.checkIfADecisionForAnEmptyCarrierIsNeeded()


            ########################################################################
            # Die notwendigen Entscheidungen für die Agenten aufbereiten und Anfragen
            ########################################################################
            for car in self.needDecisionFor:                
                # Agent muss entscheiden, wo die nächste Operation ausgeführt werden soll, und welchen Weg der Carrier bis dahin nehmen soll
                poped = self.needDecisionFor.pop(car)
                #print("-- Anfrage für Carrier=", car, "vorbereitet", poped)
                self.currentInquiryOfTheAgent[car] = poped

                #print("### <- End stepUntilNextDecision ###")
                avaActSpc, [stationsOptionsIds, stationsOptionsLocations] = self.getAvailableActionSpace()
                return False, self.simulation_step, self.getActualState(poped["location"]), avaActSpc, [poped["station"], poped["location"], poped["nextOp"], stationsOptionsIds, stationsOptionsLocations]
            


            ########################################################################
            # Einen Schritt weiter steppen - Entscheidungen der Agenten ausführen
            ########################################################################
            self.simulation_step += 1

            #if self.simulation_step % 1000 == 0:
            #    print("t=", self.simulation_step)

            ####################################
            # conveyor
            ####################################
            for i in range(2):
                # muss 2x durchlaufen werden, falls nachfolgende Carrier zuerst betrachett werden
                # TODO: es muss so lange durchlaufen werden, bis alle Carrier bearbeitet wurden
                for slotKey, slot in enumerate(self.conveyor):
                    #slot =
                    #   0  =  SlotID
                    #   1  =  [nextSlotIDs] -> (normal, aktivation#1, activation#2)
                    #   2  =  typ        
                    #   3  =  [PositonX,PositionY]
                    #   4  =  color
                    #   5  =  description
                    #   6  =  Carrier



                    car = slot[6]
                    if car != None and car.state == "belt" and car.lastProcessing < self.simulation_step:                    
                        # Nur Slots betrachten, die Carrier beinhalten
                        # Der Carrier befindet sich im Zusatnd belt, 
                        # und wurde in diesem Zeitschritt noch nicht betrachtet,
                        # Das transportband darf ihn also bearbeiten 

                        # Der Transport ist abhänig vom aktuellen Typ des Slots
                        alternatives = slot[1]
                        if (slot[2] == "normal" or slot[2] == "critical_i" or slot[2] == "critical_b"):
                            # Init
                            critical_section_is_free = False
                            no_critical_section_and_fellow_is_free = False
                            
                            # Diese Slot-Typen haben selbst nur eine Pfad alternative.
                            # Doch bevor weitertranstortiert wird, müssen wir prüfen:
                            # Ist der nächste Knoten eine Weiche oder ein ByPass?
                            # Dieses sind kritische Abschnitte, weswegen auch die nachfolger betrachtet werden müssen
                            follower = self.conveyor[alternatives[0]]
                            if len(follower[1]) > 1:
                                #print("-- Der nächste Knoten ist ein kritischer Abschnitt")
                                critical_section_is_free = True
                                #print("-- Checked Switch/Bypass:" , follower[0])
                                if self.conveyor[follower[0]][6] != None:
                                    # Der Knoten selbst ist belegt
                                    critical_section_is_free = False
                                else:
                                    for alternativ in follower[1]:
                                        #print("-- Checked Alternative option:" , alternativ)
                                        if self.conveyor[alternativ][6] != None: 
                                            # einer der Pfade ist belegt
                                            critical_section_is_free = False
                                #print("-- Ist der kritische Abschnitt frei?" , critical_section_is_free)
                            else:
                                # Der Nächste Knoten ist kein kritischer Abschnitt, abwer ist dieser auch leer?
                                no_critical_section_and_fellow_is_free = (self.conveyor[alternatives[0]][6] == None)
                            
                            if no_critical_section_and_fellow_is_free or critical_section_is_free:
                                
                                # Der Nachfolger ist leer, also kann bedenkenlos weitertranspotiert werden
                                self.conveyor[alternatives[0]][6] = car  # Nächsten Slot zuweisen
                                self.conveyor[slotKey][6] = None         # Aus aktuellem Slot entfernen 
                                car.update_lastProcessing(self.simulation_step)
                                #print("t=", self.simulation_step, "C=", car.id, "W=", slotKey ,"->", alternatives[0], "NextDestination=", car.getNextDestination())
                                self.generateCarrierHistoryEntry(car, "T")
                            else:
                                #print("t=", self.simulation_step, "WAITING", "C=", car.id, "W=", slotKey ,"->", alternatives[0])
                                self.generateCarrierHistoryEntry(car, "W")

                        elif (slot[2] == "intersection"):
                            # Init
                            critical_section_is_free = True

                            # checken, ob die Nachfolger frei sind
                            for alternativ in alternatives:
                                #print("-- Carrier at intersection - checked Alternative option:" , alternativ)
                                if self.conveyor[alternativ][6] != None: 
                                    # einer der Pfade ist belegt
                                    critical_section_is_free = False
                            #print("-- Carrier at intersection - Ist der kritische Abschnitt frei?" , critical_section_is_free)
                            
                            if critical_section_is_free:

                                # Alle Nachfolger sind leer, also kann bedenkenlos weitertranspotiert werden
                                path = int(car.get_switch_token_and_reset(slot[5]))
                            
                                self.conveyor[alternatives[path]][6] = car  # Nächsten Slot zuweisen
                                self.conveyor[slotKey][6] = None            # Aus aktuellem Slot entfernen 
                                car.update_lastProcessing(self.simulation_step)
                                #print("t=", self.simulation_step, "C=", car.id, "W=", slotKey ,"->", alternatives[path], "NextDestination=", car.getNextDestination(), "gewählter Pfad=", path,)
                                self.generateCarrierHistoryEntry(car, "T")
                            else:
                                self.generateCarrierHistoryEntry(car, "W")

                        elif (slot[2] == "bypass"):
                            # Init
                            critical_section_is_free = True

                            # checken, ob die Nachfolger frei sind
                            for alternativ in alternatives:
                                #print("-- Carrier at bypass - checked Alternative option:" , alternativ)
                                if self.conveyor[alternativ][6] != None: 
                                    # einer der Pfade ist belegt
                                    critical_section_is_free = False
                            #print("-- Carrier at bypass - Ist der kritische Abschnitt frei?" , critical_section_is_free)
                            
                            if critical_section_is_free:

                                # Alle Nachfolger sind leer, also kann bedenkenlos weitertranspotiert werden
                                path = int(car.get_bypass_token_and_reset(slot[5]))
                                
                                self.conveyor[alternatives[path]][6] = car  # Nächsten Slot zuweisen
                                self.conveyor[slotKey][6] = None            # Aus aktuellem Slot entfernen 
                                car.update_lastProcessing(self.simulation_step)
                                #print("t=", self.simulation_step, "C=", car.id, "W=", slotKey ,"->", alternatives[path], "NextDestination=", car.getNextDestination(),"gewählter Pfad=", path)
                                self.generateCarrierHistoryEntry(car, "T")
                            else:
                                self.generateCarrierHistoryEntry(car, "W")

                        elif (slot[2] == "station"):
                            # Der Carrier befindet sich an einer Station
                            nextDestination = car.getNextDestination()
                            newDecisionNeeded = False

                            if nextDestination == slot[0]:
                                #print("Der Carrier=", car.id, "mit Op=", car.product.getNextOperation()," soll hier an Station=", slot[5] ,"bearbeitet werden")
                                found = False
                                for stationKey, station in enumerate(self.stations):
                                    if (station["Id"] == slot[5]) and station["State"] == "Idel":
                                        found = True
                                        self.stations[stationKey]["Carrier"] = car
                                        self.stations[stationKey]["State"] = "CarrierAssigned"
                                if found == False:
                                    print("äää - Die Masschine ist nicht frei" )
                                # Den Carrier in den zustand maschiene versetzten.
                                # Sorgt dafür, dass er im weiteren nicht mehr vom Transportband betrachtet wird 
                                car.changeStateToMachine()
                                self.generateCarrierHistoryEntry(car, "P")
                            else:
                                
                                if nextDestination == None:
                                    #print("Der Carrier=", car.id, " hat aktuell kein Ziel")
                                    pass
                                else:
                                    #print("Der Carrier=", car.id, " hat ein anderes Ziel=", self.conveyor[car.getNextDestination()][5])
                                    #newDecisionNeeded = self.shouldAskAgain(car, nextDestination, currentLocation=slot[0])
                                    ######
                                    if self.config.askAgainIfMalfunctionWasDetected == True:
                                        askedAgainState = car.getAskedAgain()
                                        if askedAgainState == False:
                                            # Das produkt in diesem Step wurde bisher kein zweites mal angefragt, also fortfahren

                                            newDecisionNeeded = self.shouldAskAgain(car, nextDestination, slot)

                                        

                                    
                                    
                                    
                                    
                                    
                                    ############
                                    pass
                                # Der Carrier hat ein anderes/oder kein Ziel
                                # Aber kann der Carrier weiter transportiert werden?
                                # Der Nächste Knoten ist kein kritischer Abschnitt, abwer ist dieser auch leer?
                                fellow_is_free = (self.conveyor[alternatives[0]][6] == None)
                                
                                if fellow_is_free:
                                    if newDecisionNeeded:
                                        self.generateCarrierHistoryEntry(car, "A")
                                        car.update_lastProcessing(self.simulation_step)
                                    else:                           
                                        # Der Nachfolger ist leer, also kann bedenkenlos weitertranspotiert werden
                                        self.conveyor[alternatives[0]][6] = car  # Nächsten Slot zuweisen
                                        self.conveyor[slotKey][6] = None                                # Aus aktuellem Slot entfernen 
                                        car.update_lastProcessing(self.simulation_step)
                                        #print("t=", self.simulation_step, "C=", car.id, "W=", slotKey ,"->", alternatives[0], "NextDestination=", car.getNextDestination())
                                        self.generateCarrierHistoryEntry(car, "T")
                                else:
                                    self.generateCarrierHistoryEntry(car, "W")


                                
            ####################################
            # Machine
            ####################################
            # States:

            # Idel
            # CarrierAssigned # Done by conveyor-section
            # SetUp # ony if nesseasary
            # Load
            # |--> Process
            # ^--- Ask # agents where to perform the next operation
            # Unload
            # Idel


            for stationKey, station in enumerate(self.stations):
                car =  self.stations[stationKey]["Carrier"]
                if car != None and (car.lastProcessing < self.simulation_step):                         

                    # ##################################################################
                    # State = CarrierAssigned
                    # ##################################################################
   
                    if station["State"] == "CarrierAssigned":                        
                        self.stations[stationKey]["Progress"] = 1

                        if station["EquippedProductFamily"] == car.getProductFamily():
                            # Gleiche Familien, also kann direkt das Produkt in die Maschine geladen werden
                            self.stations[stationKey]["State"] = "Load"
                        else:
                            self.stations[stationKey]["State"] = "SetUp"
                        
                    # ##################################################################
                    # State = SetUp
                    # ##################################################################

                    elif station["State"] == "SetUp":
                        if station["Progress"] >= station["SetupTime"]:
                            # Umrüstung vollendet
                            self.stations[stationKey]["Progress"] = 1
                            self.stations[stationKey]["EquippedProductFamily"] = car.getProductFamily()
                            self.stations[stationKey]["State"] = "Load"                            
                        else:
                            # Der UmrüstForttschritt muss weitergeführt werden    
                            self.stations[stationKey]["Progress"] += 1
                        # Carrier wurde bearbeitet
                        car.update_lastProcessing(self.simulation_step)
                        self.generateCarrierHistoryEntry(car, "S")

                    
                    # ##################################################################
                    # State = Load
                    # ##################################################################

                    elif station["State"] == "Load":
                        if station["Progress"] >= station["LoadTime"]:
                            # Laden vollendet
                            #opOnCarrier = str(car.product.getNextOperation())
                            opOnCarrier = car.product.getNextOperation()
                            if opOnCarrier not in self.stations[stationKey]['Operations']:
                                #print('Station kann nicht OP')
                                pass
                            elif self.stations[stationKey]["Operations"][opOnCarrier]["BreakdownState"]:
                                # Operation ist nicht verfügabr wir müssen warten...
                                self.stations[stationKey]["Progress"] = 1
                                self.stations[stationKey]["State"] = "WaitingFixingFailure"    
                            else:
                                # Operation ist verfügabr, Prozess starten
                                self.stations[stationKey]["Progress"] = 1
                                self.stations[stationKey]["State"] = "Process"
               
                        else:
                            # Der Belade-Forttschritt muss weitergeführt werden    
                            self.stations[stationKey]["Progress"] += 1
                        # Carrier wurde bearbeitet
                        car.update_lastProcessing(self.simulation_step)
                        self.generateCarrierHistoryEntry(car, "L")
                    
                    # ##################################################################
                    # State = WaitingFixingFailure (F)
                    # ##################################################################

                    elif station["State"] == "WaitingFixingFailure": 
                        # Die Station kan die gefoderte operation gerade nicht ausführen
                        #opOnCarrier = str(car.product.getNextOperation()) Änderung
                        opOnCarrier = car.product.getNextOperation()

                        if self.stations[stationKey]["Operations"][opOnCarrier]["BreakdownState"]:
                            # Operation ist nicht verfügabr wir müssen warten...
                            self.stations[stationKey]["State"] = "WaitingFixingFailure"    
                        else:
                            # Operation ist verfügabr, Prozess starten
                            self.stations[stationKey]["State"] = "Process"       
                     

                        #print("Carrier=", car.id, "muss darauf warten, dass die Störung der Operation=", opOnCarrier, "behoben wird.")
                        # Carrier wurde bearbeitet
                        car.update_lastProcessing(self.simulation_step)
                        self.generateCarrierHistoryEntry(car, "F")
                    

                    # ##################################################################
                    # State = Process
                    # ##################################################################

                    elif station["State"] == "Process":
                        if station["Progress"] == 1:
                            #nextOp = str(car.product.getNextOperation()) Änderung
                            nextOp = car.product.getNextOperation()
                            self.stations[stationKey]["IndividualOperationTime"] = self.getUncertainOperationTime(self.stations[stationKey]["Operations"][nextOp]["OperationsTime"])
                            

                        if station["Progress"] >= self.stations[stationKey]["IndividualOperationTime"]:
                            # Process vollendet
                            self.stations[stationKey]["Progress"] = 1                            
                            nextOp = car.product.setNextOperation(car.order.workplan, self.simulation_step)
                            car.setAskedAgainFalse()
                            if nextOp == None:
                                #print("-- t=",self.simulation_step,"Produkt=", car.product.id, "Order=",car.order.id, "family=", car.order.family, "WP", car.order.workplan , "fertiggestellt - Carrier=",car.id)
                          
                                #print("-- Es wurde die letzet Operation ausgeführt, Produkt vom Carrier entfernen")
                                p = car.removeProductFromCarrier(self.simulation_step)
                                self.stations[stationKey]["State"] = "Unload"
                                self.finishedProducts.append(p)
                            else:
                                #print("-- Es gibt eine Folgeoperation=", nextOp)
                                #print("-- Aufnehmen in needDecisionFor")
                                # Aufarbeiten der Entscheidung
                                self.stations[stationKey]["State"] = "Ask" 
                                self.needDecisionFor[car.id] = {
                                    "carId"     : car.id,
                                    "location"  : self.stations[stationKey]["Location"],
                                    "station"   : self.stations[stationKey]["Id"],
                                    "nextOp"    : nextOp
                                }
                        else:
                            # Der Prozess-Forttschritt muss weitergeführt werden    
                            self.stations[stationKey]["Progress"] += 1
                        # Carrier wurde bearbeitet
                        car.update_lastProcessing(self.simulation_step)
                        self.generateCarrierHistoryEntry(car, "P")

                    # ##################################################################
                    # State = Ask
                    # ################################################################## 
                    elif station["State"] == "Ask":
                        #print("-- Wir befinden uns in ASK - nun müsste nochmal geprüft werden, ob die Entscheidung mit diser Station übereinstimmt")
                        #nextOp = str(car.product.getNextOperation())
                        #self.stations[stationKey]["IndividualOperationTime"] = self.getUncertainOperationTime(self.stations[stationKey]["Operations"][nextOp]["OperationsTime"])
                        if car.getNextDestination() == self.stations[stationKey]["Id"]:
                            #print("-- !!!!!!!!!!!!!! -  die nachfolgende Operation wird auf der gleichen Maschien ausgeführt") 
                            # Soll auf der gleichen Maschien ausgeführt werden, aber ist das aktuell überhaupt möglich?
                            opOnCarrier = car.product.getNextOperation()
                            if self.stations[stationKey]["Operations"][opOnCarrier]["BreakdownState"]:
                                # Operation ist nicht verfügabr wir müssen warten...
                                self.stations[stationKey]["State"] = "WaitingFixingFailure"    
                            else:
                                # Operation ist verfügabr, Prozess starten
                                self.stations[stationKey]["State"] = "Process"       
                        else:
                            #print("-- !!!!!!!!!!!!!! -  die nachfolgende Operation wird auf einer anderen Maschien ausgeführt")
                            self.stations[stationKey]["State"] = "Unload"      
                        car.update_lastProcessing(self.simulation_step)
                        self.generateCarrierHistoryEntry(car, "A")
                    
                    # ##################################################################
                    # State = Unload
                    # ##################################################################

                    elif station["State"] == "Unload":
                        if station["Progress"] >= station["LoadTime"]:
                            # Unload vollendet
                            self.stations[stationKey]["Progress"] = 0
                            self.stations[stationKey]["State"] = "Idel"
                            self.stations[stationKey]["Carrier"] = None # Carrier aus Station entfernen
                            car.changeStateToBelt()                         
                        else:
                            # Der Entlade-Forttschritt muss weitergeführt werden    
                            self.stations[stationKey]["Progress"] += 1
                        # Carrier wurde bearbeitet
                        car.update_lastProcessing(self.simulation_step)
                        self.generateCarrierHistoryEntry(car, "U")
                    #print("t=", self.simulation_step, "S=", self.stations[stationKey]["Id"], "C=", car.id, "StationState=", station["State"] ,"Progress", station["Progress"])


                    elif station["State"] == "AskAgain":
                        #print("-- Wir befinden uns in AskAgain")
                        if car.getNextDestination() == self.stations[stationKey]["Id"]:
                            print("  ###########################  Die nächste operation soll hier stattfinden")
                            self.stations[stationKey]["State"] = "CarrierAssigned"    
                        else:
                            # Die nächste Station ist nicht diese hier
                            self.stations[stationKey]["Progress"] = 0
                            self.stations[stationKey]["State"] = "Idel"
                            self.stations[stationKey]["Carrier"] = None # Carrier aus Station entfernen
                            car.changeStateToBelt() 
                        
                        foundCarriers = 0  
                        prodIds = []  
                        for slotKey, slot in enumerate(self.conveyor):
                            car2 = slot[6]     
                            if car2 != None:
                                foundCarriers += 1

                            try:
                                prodID = car2.product.getProductId()
                                prodIds.append(prodID)
                            except:
                                prodID = None
                        #print("Wie viele Carrier existieren noch?" , foundCarriers, prodIds)
                        
                        #print("Wurde die neue Entscheidung bereits auf den Carrier angewendet?") 
                               
                        car.update_lastProcessing(self.simulation_step)
                        self.generateCarrierHistoryEntry(car, "A")
        
        #                                                               poped["station"], poped["location"], poped["nextOp"], stationsOptionsIds, stationsOptionsLocations
        return True, self.simulation_step, self.getActualState(0), [], [False, False, False, [], []]

    def getCarWithCarId(self, carId):
        for slot in self.conveyor:
           car = slot[6] 
           if car != None and carId == car.id:
               return car

    def step(self, action):
        # In der Funktion "stepUntilNextDecision" wurden die Parameter aufbereitet, mit denen die KI angefragt wurde.
        # Jetzt, wo wir hier die Antwort der KI erhalten, können wir auf diese Werte zugreifen.
        carId = list(self.currentInquiryOfTheAgent.keys())[0]
        #print("### -> Begin step ###", self.currentInquiryOfTheAgent[carId])
        # 0 = optKey, 
        # 1 = stationsOptionsIds[key], 
        # 2 = target_node, 
        # 3 = switches, 
        # 4 = start_node        
        car = self.getCarWithCarId(carId)
        AskedAgain = car.getAskedAgain()  

        for x in self.currentInquiryOfTheAgent[carId]["allPathOptions"]:        
            if x[0] == action:
                # Wir haben alle zur Entscheidung gehörigen Daten
                # Nun muss die Entscheidung dem Carrier zugewiesen werden 
                #print("x=", x)
                #print("Convoyer" , self.conveyor[x[4]])
                #ar = self.conveyor[x[4]][6]
                #print("-- carID=", car.id, "getAskedAgain=",car.getAskedAgain())              
                #print("-- Ausführung - Aus",len(self.currentInquiryOfTheAgent[carId]["allPathOptions"]),"Optionen, hat Agent Aktion=", action, "für Carrier=", car.id ,"gewählt")
                nextDecisionId = self.getNextDecisionIdAndCountUp()
                if AskedAgain:
                    self.apply_addtional_desc_old.append(car.getCurrentDecisionId())
                    self.apply_addtional_desc_new.append(nextDecisionId)


                # Reset all old decisions
                car.update_all_switch_tokens(self.switch_tokens)
                car.update_all_bypass_tokens(self.bypass_tokens)

                # Set the new decisions for switches
                for switch in x[3]:
                    car.update_one_switch_token(switch, True)
                #print("-- Aktualisierte Switch Tokens", car.switch_tokens)
                # Set the new decisions for bypasses
                for bypass in self.graph.bypass_affected_stations:
                    if bypass[0] == self.conveyor[x[2]][5]:
                        car.update_one_bypass_token(bypass[2], True)
                        #print("MATCHED", "bypass",bypass, "x" ,x, "--" , bypass[0] , "vs" ,self.conveyor[x[2]][5])
                #print("-- bypass_affected_stations" , self.graph.bypass_affected_stations)
                #print("-- Aktualisierte ByPass Tokens", car.bypass_tokens)

                # Set the new target based on the decision
                car.update_next_destination(x[2])
                # setNextDecisionId to Carrier (importent for Tracking)
                car.setCurrentDecisionId(nextDecisionId)

                #if car.getAskedAgain():
                    #print("Der Carrier wurde ein zweites mal angefragt:", car.id, "Altes Ziel", oldDestination, "Neues Ziel=" ,car.getNextDestination(), "nextop=" , car.product.getNextOperation())

        # Reset currentInquiryOfTheAgent
        self.currentInquiryOfTheAgent = {}
        #print("### <- End step ###")

        return self.stepUntilNextDecision()
    
  
    def calcReward(self):
        makespan = self.simulation_step
        #print(self.decisionTracking)
        #die()
        decision_filter = []
        additional_action_reward = []

        for i in range(self.nextDecisionId):
            # decision_filter aufbauen, Alle apply_addtional_desc (Entscheidungen die ein zweites mal angefragt wurden), sollen nicht gerlernt werden 
            #decision_filter.append(i not in self.apply_addtional_desc)
            tempReward = 0
            add_tempReward = 0
            # Wenn AskAgain aufgerufen wurde,dann zählt hier muss auch die folge Entscheidung hier mit berücksichtigt werden.
            index = [ii for ii ,e in enumerate(self.apply_addtional_desc_old) if e == i]
            if len(index) > 0:                
                index = index[0]
                add = self.apply_addtional_desc_new[index]
                perState = self.generate_state_count_per_decision(add)
                if add in perState:
                    perState = perState[add]
                    add_tempReward += perState["W"]
                    add_tempReward += perState["T"]
                    add_tempReward += perState["S"]
                    add_tempReward += perState["L"]
                    add_tempReward += perState["U"]
                    add_tempReward += perState["P"]
                    add_tempReward += perState["F"] * 3
                    #print("Epi=",i, "+Epi=", add, "add_tempReward", add_tempReward)

            perState = self.generate_state_count_per_decision(i)
            if i in perState:
                perState = perState[i]
                tempReward += perState["W"]
                tempReward += perState["T"]
                tempReward += perState["S"]
                tempReward += perState["L"]
                tempReward += perState["U"]
                tempReward += perState["P"]
                tempReward += perState["F"] * 3
            #print("i=", i, "tempReward=", tempReward, "detail=", perState)
            additional_action_reward.append((add_tempReward + tempReward)*-0.05)



        # Init
        bonus = 0
        penalty = 0

        overallWaiting          = 0
        overallTransport        = 0
        overallSetUp            = 0
        overallProduction       = 0
        overallFailure          = 0
        productionTimes         = []


        # Aufbearbeitung der notwendigen Daten        
        for f in self.finishedProducts:
            productionTimes.append(f.production_time)

        for slotID, slot in enumerate(self.conveyor):
            if self.conveyor[slotID][6] != None:
                # Count the occurrences of different elements in the history list
                history_counter = Counter(self.conveyor[slotID][6].history)
                # Update the overall counts based on the occurrences
                overallWaiting += history_counter["W"]
                overallTransport += history_counter["T"]
                overallSetUp += history_counter["S"]
                overallProduction += history_counter["P"]
                overallFailure += history_counter["F"]

        lenFinishedProducts = len(self.finishedProducts)
        if lenFinishedProducts == 0:
            meanProductionTime = self.config.max_steps
            meanOverallWaiting = self.config.max_steps
            meanOverallTransport = self.config.max_steps
            meanOverallProduction = self.config.max_steps
            meanOverallSetUp = self.config.max_steps
            meanOverallFailure = self.config.max_steps
        else:
            meanProductionTime =  sum(productionTimes) / lenFinishedProducts
            meanOverallWaiting = overallWaiting/lenFinishedProducts
            meanOverallTransport = overallTransport/lenFinishedProducts
            meanOverallProduction = overallProduction/lenFinishedProducts
            meanOverallSetUp = overallSetUp/lenFinishedProducts
            meanOverallFailure = overallFailure/lenFinishedProducts

        lenUnfinishedProducts = self.config.ammount_of_Products - lenFinishedProducts
        if lenUnfinishedProducts > 0:
            #print("Es wurden nur ", lenFinishedProducts , "anstatt von" , self.config.ammount_of_Products , "Produkten gefertigt")
            pass

        # Berechnung des Bonuns und der Bestrafung

        #bonus += 3*reamingTime
        #penalty += overallWaiting
        #penalty += overallTransport
        #penalty += 50*overallSetUp
        #penalty += 10*meanProductionTime

        #overallTransport -=10000
        #overallWaiting -=20000


        offsetOverallProduction = -150
        offsetOverallTransport = -450
        offsetOverallWaiting = -170
        offsetOverallSetUp = 0

        #penalty += 20*(meanOverallProduction + offsetOverallProduction)
        #penalty += 10*(meanOverallTransport +offsetOverallTransport)
        #penalty += 7.5*(meanOverallWaiting +offsetOverallWaiting) 
        #penalty += 50*(meanOverallSetUp +offsetOverallSetUp)
        #penalty += meanProductionTime # Vorher
        #penalty += lenUnfinishedProducts*1000
        if lenFinishedProducts == 0:
            makespanPerProduct = 1000 #wenn nichts fertiggestellt wurde, ist die penalty 1000 automatisch
        else:
            makespanPerProduct = makespan / lenFinishedProducts #wenn es z.b für 500 Steps nur ein Produkt fertigstellt: 500/1 = 500 penalty, weil es lange braucht, um so eine wenige Menge fertigzustellen

        penalty += makespanPerProduct
        #penalty += meanProductionTime # Vorher
    

        #                      P |  T |  W |  S || Reward
        #2023-17-10 - 08:55 
        # Faktoren            10 |  5 |  5 | 40 ||  /1
        # Offset             -180|-500|-200|-20 || 1000
        #2023-17-10 - 09:10 
        # Faktoren            10 |  8 |  5 | 30 ||  /1
        # Offset            -180 |-500|-200|  0 || 2000
        #2023-17-10 - 09:15 
        # Faktoren            20 |  10 |7.5| 50 ||  /1
        # Offset            -150 |-450|-175|  0 || 4000


        reward = bonus - penalty
       

        # Reward clippen - keinen Negativen Reward auszahlen
        #if reward <=0:
        #    reward = 0
        #reward /= 1000
        reward += 200
        #reward = int(reward)
        
        
        #print("")
        #print("t=", self.simulation_step)
        #print("meanProductionTime=", meanProductionTime)
        #print("reamingTime=", reamingTime)c
        #print("overallWaiting=", overallWaiting)
        #print("overallTransport=", overallTransport)
        
        #print("meanOverallProduction=", meanOverallProduction)
        #print("meanOverallWaiting=", meanOverallWaiting)
        #print("meanOverallTransport", meanOverallTransport)        
        #print("meanOverallSetUp=", meanOverallSetUp)
        #print("")
        #print("reward=", reward)
    
        return reward, [meanOverallProduction, meanOverallWaiting, meanOverallTransport, meanOverallSetUp, meanProductionTime, meanOverallFailure, additional_action_reward, lenFinishedProducts]

    def checkBreakdowns(self):
        #print(self.simulation_step, "checkBreakdowns")
        relevantEvents = self.breakdowns.getRemainingEvents(self.simulation_step)        
        if len(relevantEvents) >0:
            for event in relevantEvents:
                # 0 = EventKey
                # 1 = StationId
                # 2 = OpId
                # 3 = geplanteEintrittsZeit
                # 4 = Dauer des Fehlers
                # 5 = realeEintrittsZeit
                EventKey                = event[0]
                StationId               = event[1]
                OpId                    = event[2]
                geplanteEintrittsZeit   = event[3]
                dauer                   = event[4]
                realeEintrittsZeit      = event[5]
                #print("Wir heben ein Störungsereignis, dass wir betrachten müssen")
                #print(event)
                if realeEintrittsZeit != 0:
                    # Die Störung ist bereits aktiv
                    # Aber kann sie auch wieder beendet werden?
                    if self.simulation_step >= (realeEintrittsZeit+dauer):
                        for stationKey, station in enumerate(self.stations):
                            if station["Id"] == StationId:                                
                                self.stations[stationKey]["Operations"][OpId]["BreakdownState"] = False
                                self.breakdowns.setEventAsFinished(geplanteEintrittsZeit,EventKey)
                                #print("t=", self.simulation_step, " Die Station=" , StationId, "Beendet die Störung - Event=", event)  
                                #print("Station=", self.stations[stationKey])  
                else:
                    for stationKey, station in enumerate(self.stations):
                        failureAssigned = False
                        if station["Id"] == StationId:
                            # passende Station gefunden
                            if station["State"] == "Idel":
                                # Die Station ist gerade frei, also Störung zuweisen
                                failureAssigned = True
                                #print("t=", self.simulation_step, " Die Station=" , StationId, "befindet sich in =" ,station["State"] , "Event=", event,"ausführbar")  
                                #print("Station=", self.stations[stationKey])  
                            elif station["State"] == "SetUp" or station["State"] == "Load" or station["State"] == "Process":
                                #cheken welche Operation gerade ausgeführt wird...
                                opOnCarrier = station["Carrier"].product.getNextOperation()
                                if str(OpId) != str(opOnCarrier):
                                    # Die Operationen unterscheiden sich, die Station darf in störung gehen 
                                    #print("Station befindet sich in:" , station["State"], "und führt die Op:", opOnCarrier , "aus, es wird Op:" , OpId, "nun in Störung gesetzt")
                                    failureAssigned = True
                                    #print("t=", self.simulation_step, " Die Station=" , StationId, "befindet sich in =" ,station["State"] , "Event=", event,"nicht ausführbar")    
                        if failureAssigned == True:
                            self.stations[stationKey]["Operations"][OpId]["BreakdownState"] = True
                            self.breakdowns.setEventAsStarted(geplanteEintrittsZeit,EventKey)
