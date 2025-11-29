import copy

class Carrier:

    def __init__(self, id):
        self.id = id
        self.order = None
        self.product = None
        self.state = "belt" # belt, machine
        self.lastProcessing = -1
        self.nextDestination = None
        self.switch_tokens = {}
        self.bypass_tokens = {}
        self.history = []
        self.currentDecisionId = None
        self.askedAgain = False

    def getProductFamily(self):
        retVal = None
        if self.order != None:
            retVal = self.order.family
        return retVal

    def placeProductOnCarrier(self, p, o):
        self.product = p
        self.order = o

    def removeProductFromCarrier(self,time):
        self.product.product_finished(time)
        self.order.product_finished(time)
        retVal = self.product

        self.order = None
        self.product = None
        self.nextDestination = None
        self.currentDecisionId = None
        return retVal



    def update_lastProcessing(self, t):
        self.lastProcessing = t

    ######### currentDecisionId

    def getCurrentDecisionId(self):
        return self.currentDecisionId
    
    def setCurrentDecisionId(self, actionID):
        self.currentDecisionId = actionID

    def getAskedAgain(self):
        return self.askedAgain

    def setAskedAgainTrue(self):
        self.askedAgain = True
    
    def setAskedAgainFalse(self):
        self.askedAgain = False

    ######### State

    def changeStateToBelt(self):
        self.state = "belt"

    def changeStateToMachine(self):
        self.state = "machine"

    ######## nextDestination
    
    def update_next_destination(self, target_node):
        self.nextDestination = target_node

    def getNextDestination(self):
        return self.nextDestination
      
      
    ######## History
    
    def update_whole_history(self, hist):
        self.history = copy.deepcopy(hist) 

    def update_history(self, key, value):
        try:
            self.history[key] = value
        except:
            print("Fehler beim Hinzufügen:", key, value)
            #die()

    ######## Switch

    def update_all_switch_tokens(self, tokens):
        self.switch_tokens = copy.deepcopy(tokens) 
    
    def update_one_switch_token(self, key, value):
        self.switch_tokens[key] = value
    
    def get_switch_token_and_reset(self, key):
        old = self.switch_tokens[key]
        self.switch_tokens[key] = False
        return old
    
    ######### bypass

    def update_all_bypass_tokens(self, tokens):
        self.bypass_tokens = copy.deepcopy(tokens) 
    
    def update_one_bypass_token(self, key, value):
        self.bypass_tokens[key] = value

    def get_bypass_token_and_reset(self, key):
        old = self.bypass_tokens[key]
        self.bypass_tokens[key] = False
        return old