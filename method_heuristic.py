import random
import pickle
import networkx as nx

random.seed(42)

def chooseShortestPath(myEnv, rest):
    # 0 = [poped["station"]
    # 1 = poped["location"]
    # 2 = poped["nextOp"]
    # 3 = stationsOptionsIds
    # 4 = stationsOptionsLocations

    start_node = rest[1]
    stationsOptionsLocations = rest[4]        
    Distance = []
    DecisionKey = []
        
    for key, target_node in enumerate(stationsOptionsLocations):         
        alternative_paths = [nx.shortest_path(myEnv.graph.G, source=start_node, target=target_node)]   
        switches = []
        try:
            alt = myEnv.graph.pathsToIntersections(alternative_paths) 
            if str(alt) == "[]":    
                pass
            else:    
                for a in alt[0]:
                    try:     
                        if a[1] != None:
                            switches.append(a[1])
                    except:
                        print("Fehler1")
                        pass
                    switches.sort()

            optKey = myEnv.graph.all_possible_path_options.index(switches)
                #offset ermitteln
            optKey += key*len(myEnv.graph.all_possible_path_options)

            Distance.append(len(alternative_paths[0]))
            DecisionKey.append(optKey)
                #print("Von=", start_node , "nach", target_node, "optKey=" ,optKey)
                #print("alternative_paths", alternative_paths, alt)   
        except:
                #print("Von=", start_node , "nach", target_node)
                #print("alternative_paths", alternative_paths, alt)   
            print("Fehler2")
                #die()
        
    index_min = min(range(len(Distance)), key=Distance.__getitem__)
    #print("Min Distance=" , index_min, "Decision", DecisionKey[index_min],"Distance", Distance, "DecisionKey" , DecisionKey)

    action = DecisionKey[index_min]
    return action

def chooseLongestPath(myEnv, rest):
    # 0 = [poped["station"]
    # 1 = poped["location"]
    # 2 = poped["nextOp"]
    # 3 = stationsOptionsIds
    # 4 = stationsOptionsLocations

    start_node = rest[1]
    stationsOptionsLocations = rest[4]        
    Distance = []
    DecisionKey = []
    #print("############")  
    for key, target_node in enumerate(stationsOptionsLocations): 
        alternative_paths = [myEnv.graph.longest_path(start_node, target_node)]   
        switches = []
        try:
            alt = myEnv.graph.pathsToIntersections(alternative_paths) 
            if str(alt) == "[]":    
                pass
            else:    
                for a in alt[0]:
                    try:     
                        if a[1] != None:
                            switches.append(a[1])
                    except:
                        print("Fehler1")
                        pass
                    switches.sort()

            optKey = myEnv.graph.all_possible_path_options.index(switches)
            #offset ermitteln
            optKey += key*len(myEnv.graph.all_possible_path_options)

            Distance.append(len(alternative_paths[0]))
            DecisionKey.append(optKey)
                
            #print("Von=", start_node , "nach", target_node, "optKey=" ,optKey)
            #print("alternative_paths", alternative_paths, alt)   
        except:
            #print("Von=", start_node , "nach", target_node)
            #print("alternative_paths", alternative_paths, alt)   
            print("Fehler2")
            #die()
        
    index_max = max(range(len(Distance)), key=Distance.__getitem__)
    #print("Max Distance",Distance[index_max],  "Max DistanceKey=" , index_max, "Decision", DecisionKey[index_max],"Distance", Distance, "DecisionKey" , DecisionKey)

    action = DecisionKey[index_max]
    return action

def get_random_true_index(lst):
    # Filtere die Indizes, bei denen der Wert True ist
    true_indices = [i for i, value in enumerate(lst) if value]

    if true_indices:
        # Wähle einen zufälligen Index aus der Liste der True-Indizes
        random_true_index = random.choice(true_indices)
        return random_true_index
    else:
        # Falls es keine True-Werte gibt, gib None zurück
        return None
    
def get_first_true_index(lst):
    # Filtere die Indizes, bei denen der Wert True ist
    true_indices = [i for i, value in enumerate(lst) if value]

    if true_indices:
        # Wähle einen zufälligen Index aus der Liste der True-Indizes
        random_true_index = true_indices[0]
        return random_true_index
    else:
        # Falls es keine True-Werte gibt, gib None zurück
        return None