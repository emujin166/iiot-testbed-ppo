


class Product:
    def __init__(self, id, order_id):
        self.id = id
        self.order_id = order_id
        self.history = []
        self.time_production_start = None
        self.time_production_end = None
        self.production_time = None
        self.next_Operation = None
 
    def print(self):
        print("pid=", self.id, "oid=", self.order_id, "duration=", (self.time_production_end-self.time_production_start))
    
    def getProductId(self):
        return self.id

    def getNextOperation(self):
        return self.next_Operation
    
    def product_started(self, time):
        self.time_production_start = time

    def product_finished(self, time):
        self.next_Operation = None
        self.time_production_end = time
        self.production_time = self.time_production_end - self.time_production_start

    def setNextOperation(self,wp,time):
        nextOp = None
        if self.next_Operation == None:
            nextOp = wp[0]
            self.product_started(time)
        else:
            #print("WP", wp)
            oldIndex = wp.index(self.next_Operation)
            nextIndex = oldIndex+1
            #print("oldIndex", oldIndex)
            #print("nextIndex", nextIndex)
            if len(wp) > nextIndex:
                nextOp = wp[nextIndex]
            else:
                # Der nächste Index existiert nicht
                pass
        
        self.next_Operation = nextOp
        return nextOp


        


class Order:
    def __init__(self, id, family, workplan, ammount):
        self.id = id
        self.ammount = ammount
        self.family = family
        self.workplan = workplan
        self.in_production = 0
        self.allradey_finished = 0
        self.time_started = False
        self.time_finished = False

    def product_started(self, time):
        if self.time_started == False:
            self.time_started = time
        self.in_production += 1 

    def product_finished(self, time):
        self.allradey_finished += 1 
        if self.isOrderFinished() ==  True:
            self.time_finished = time

    def isOrderFinished(self):
        retVal = False
        if self.ammount == self.allradey_finished:
            retVal = True
        return retVal
    
    def print_order(self):
        print("Order:" + str(self.id) + "Ammount:" + str(self.ammount) + " Family:" + str(self.family) + " Workplan:" + str(self.workplan))
