import random
from  _mes_resources import Order, Product


class ManufacturingExecutionSystem:
    # Die Lotsize bestimmt den Umfang der Bestellung
    # Ein Job beschreibt die Hersetllung eines konkreten Produktes

    def __init__(self, config):
        self.config = config
        self.order_list = []
        self.next_new_order_id = 0
        self.next_new_product_id = 0
        self.simulation_step = 0
        self.resetVars()

    def resetVars(self):
        self.order_list = []
        self.next_new_order_id = 0
        self.next_new_product_id = 0
        self.simulation_step = 0

    def updateSimulationTime(self, t):
        self.simulation_step = t
   
    def addOrder(self, ammount=1, family=None, workplan=None):
        self.next_new_order_id 
        
        if workplan is None:
            workplan = random.choice(self.config.product_workplans)
        if family is None:
            family=random.choice(self.config.product_families)

        self.order_list.append(
            Order(id=self.next_new_order_id, 
                    family=family,
                    workplan=workplan,
                    ammount=ammount))
        
        self.next_new_order_id += 1

    def productionFinished(self):
        retVal = True
        
        for o in self.order_list:
            if o.isOrderFinished() == False:               
               # Der Auftrag wurde nicht beendet beendet
               retVal = False
               break

        return retVal
    

    def setUpMES(self):
        self.resetVars()

        # Gernerate Random Orders
        generated_Products = 0
        productsToProduce = self.config.ammount_of_Products
        # EvalDataset#3
        #productsToProduce = random.randint(50,500)
        #print("Random productsToProduce=", productsToProduce)
        while generated_Products < productsToProduce:
            ammount = random.randint(self.config.lot_size_min , self.config.lot_size_max)
            if (generated_Products + ammount) > productsToProduce:
                ammount = productsToProduce - generated_Products 
            self.addOrder(ammount)
            generated_Products += ammount

        #print()
        #print("Auftragserstellung")
        #for x in self.order_list:
        #    x.print_order()

    def getAndStartNextJob(self):
        #print("Aufruf von getAndStartNextJob")
        # Abarbeitung erfolgt ohne Prio
        #print(self.order_list)
        for o in self.order_list:
            if o.in_production < o.ammount:
                o.product_started(self.simulation_step)                
                p = Product(self.next_new_product_id, o.id)
                self.next_new_product_id += 1
                return p, o 
        return None, None               
   
