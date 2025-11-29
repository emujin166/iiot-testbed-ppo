import networkx as nx
import matplotlib.pyplot as plt
from itertools import permutations

class ConveyorGraph:
    def __init__(self,conveyor):
        self.conveyor = conveyor
        self.positions = []
        self.nodecolors = []
        self.bypass_affected_stations = []
        self.G = None
        self.all_possible_path_options = []

        self.create_conveyor_graph()
        self.get_Bypass_affected_stations()
        self.generateAllpossiblepathoptions()

    def create_conveyor_graph(self):
    # Erstelle einen gerichteten Graphen
        self.G = nx.DiGraph()
        # Manuell Knoten erstellen und durchlaufen
        for i, section in enumerate(self.conveyor):
            start_node = section[0]
            self.positions.append((section[3][0], -section[3][1]))    
            self.nodecolors.append(section[4])
            self.G.add_node(start_node)  # Manuell Knoten hinzufügen

        # Manuell Kanten hinzufügen
        for i, section in enumerate(self.conveyor):
            start_node = section[0]
            next_sections = section[1]
            for next_section in next_sections:
                self.G.add_edge(start_node, next_section)

    def plot_conveyor_graph(self):
        node_colors = {
            "normal": "#B0B0B0",
            "station": "#369B00",
            "intersection": "#700000",
            "critical_i": "#990000",
            "bypass": "#002E4D",
            "critical_b": "#026EB7",
        }
        font_colors = {
            "normal": "#026EB7",
            "station": "#026EB7",
            "intersection": "#026EB7",
            "critical_i": "#026EB7",
            "bypass": "#026EB7",
            "critical_b": "#026EB7",
        }

        node_color_list = [node_colors[self.conveyor[i][2]] for i in range(len(self.conveyor))]
        font_color_list = [font_colors[self.conveyor[i][2]] for i in range(len(self.conveyor))]

        # Zeichne den Graphen
        plt.figure(figsize=(24, 3))
        nx.draw_networkx(self.G, self.positions, with_labels=True, node_size=300, node_color=node_color_list, font_color="#ffffff", font_size=10, font_weight="bold",
                        edge_color="gray", width=1, alpha=1, arrowsize=14)
        plt.title("Transportband-Graph")
        plt.show()

    def find_bypass_affected_stations_recursive(self, slot_id, bypass_y, visited, found_affected_station):
        visited.add(slot_id)

        affected_stations = set()

        # Suche nach der aktuellen Station
        current_section = next((s for s in self.conveyor if s[0] == slot_id), None)
        if current_section and current_section[2] == "station":
            if current_section[3][1] > bypass_y:
                affected_stations.add(current_section[5])
            found_affected_station = True  # Markiere, dass eine betroffene Station gefunden wurde

        # Wenn bereits eine betroffene Station gefunden wurde, stoppe die Rekursion
        if found_affected_station:
            return affected_stations

        # Überprüfe die nächsten Slot-IDs für den Bypass
        next_slot_ids = current_section[1]
        for next_slot_id in next_slot_ids:
            if next_slot_id not in visited:
                affected_stations.update(self.find_bypass_affected_stations_recursive(next_slot_id, bypass_y, visited, found_affected_station))

        return affected_stations

    def find_bypass_affected_stations(self, bypass_slot_id):
        bypass_section = next((s for s in self.conveyor if s[0] == bypass_slot_id), None)

        # Wenn es keine Bypass-Station gibt
        if not bypass_section:
            return set()

        bypass_y = bypass_section[3][1]  # Y-Koordinate des Bypass

        visited = set()  # Zur Vermeidung von Endlosschleifen bei Bypassen
        found_affected_station = False  # Zeigt an, ob eine betroffene Station gefunden wurde
        return self.find_bypass_affected_stations_recursive(bypass_slot_id, bypass_y, visited, found_affected_station)


    def get_Bypass_affected_stations(self):
        # Iteriere durch die Förderbandabschnitte
        for section in self.conveyor:
            if section[2] == "bypass":
                bypass_id = section[5]
                bypass_slot_id = section[0]
                affected_stations = self.find_bypass_affected_stations(bypass_slot_id)
                
                self.bypass_affected_stations.append([list(affected_stations)[0], bypass_slot_id, bypass_id])

        # Ausgabe der betroffenen Stationen für jeden Bypass
        for x in self.bypass_affected_stations:
            print("Bypass ", x[2], " betrifft die Stationen:", x[0], "an",  x[1])


    def find_all_paths(self, start, end, visited, path, paths):
        visited[start] = True
        path.append(start)

        if start == end:
            paths.append(list(path))
        else:
            for neighbor in self.G[start]:
                if not visited[neighbor]:
                    self.find_all_paths(neighbor, end, visited, path, paths)

        path.pop()
        visited[start] = False

    def remove_zeros(self, path):
        return [[node, option, decision] for node, option, decision in path if decision != 0]

    def remove_duplicates(self, paths):
        seen = []
        unique_paths = []
        for path in paths:
            # Convert the list to a tuple for hashing
            path_tuple = path
            if path_tuple not in seen:
                seen.append(path_tuple)
                unique_paths.append(path)
        return sorted(unique_paths, key=lambda x: (len(x), x))

    def find_paths_with_restrictions(self, start, end):
        visited = {node: False for node in self.G.nodes()}
        paths = []
        self.find_all_paths(start, end, visited, [], paths)

        alternative_paths = self.pathsToIntersections(paths)

        return alternative_paths

    def pathsToIntersections(self, paths):
        alternative_paths = []
        for path in paths:
            alternative_path = []
            for i in range(len(path)):
                node = path[i]
                if self.conveyor[node][2] == "intersection":
                    if i < len(path) - 1:
                        next_node = path[i + 1]
                        alternative_path.append([node, self.conveyor[node][5], self.conveyor[node][1].index(next_node)])
                    else:
                        alternative_path.append([None, None, None])
            alternative_paths.append(alternative_path)

        # Entfernen von Redundanzen
        unique_paths = self.remove_duplicates(alternative_paths)

        # Entfernen von Elementen mit dem Wert 0
        filtered_paths = [self.remove_zeros(path) for path in unique_paths if any(option != 0 for node, option, decision in path)]
        return filtered_paths
    
    def remove_duplicates_from_list(self,lst_of_lst):
        seen = set()
        result = []
        for inner_lst in lst_of_lst:
            inner_tuple = tuple(inner_lst)
            if inner_tuple not in seen:
                seen.add(inner_tuple)
                result.append(inner_lst)
        return result


    def generateAllpossiblepathoptions(self):
        all_alternative_paths = []
        for i, section in enumerate(self.conveyor):
            if section[2] == "station":
                for innerI, innerSection in enumerate(self.conveyor):
                    if innerSection[2] == "station":
                        alternative_paths = self.find_paths_with_restrictions(section[0], innerSection[0])
                        for alt in alternative_paths:
                            switches = []
                            for a in alt:
                                try:
                                    if a[1] != None:
                                        switches.append(a[1])
                                except:
                                    print("Fehler")
                            switches.sort()
                            #print("Add Alternative=", switches )
                            all_alternative_paths.append(switches)
                    

        # Aufruf der Funktion und Ausgabe des Ergebnisses
        self.all_possible_path_options = self.remove_duplicates_from_list(all_alternative_paths)
        self.all_possible_path_options.sort()
        #print("Alle Path options")
        #for k, path in enumerate(self.all_possible_path_options):
        #    print("Option=", k, "Path=", path)
        


    def find_longest_path(self, start, end, visited, path, longest_path):
        visited[start] = True
        path.append(start)

        if start == end:
            if len(path) > len(longest_path):
                longest_path[:] = list(path)
        else:
            for neighbor in self.G[start]:
                if not visited[neighbor]:
                    self.find_longest_path(neighbor, end, visited, path, longest_path)

        path.pop()
        visited[start] = False

    def longest_path(self, start, end):
        visited = {node: False for node in self.G.nodes()}
        longest_path = []
        self.find_longest_path(start, end, visited, [], longest_path)
        return longest_path

