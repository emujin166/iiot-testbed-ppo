import pickle
import numpy as np

class envConfiguration:
    def __init__(self,):

        ####################################################################
        # costs-Calcuation
        self.FactorMakespan = 1
        self.FactorWaiting = 2
        self.FactorTransport = 3
        self.FactorSetUp = 5
        self.FactorFailure = 2
        self.FactorUnfinished = 10000
        self.FactorProfit = 75

        #self.home_path = "/data/walrus/ws/dahe839f-WsHeik/heik/testbed_v5/"

        #####################################################################
        ### PPO SARL
        self.ppo_sarl_output_folder      = "ppo_output"
        self.ppo_sarl_checkpoint_folder  = "ppo_checkpoints"
        self.ppo_sarl_name          = "PPO_SARL"
        self.ppo_sarl_batch_size    = 128
        self.ppo_sarl_n_epochs      = 4
        self.ppo_sarl_alpha         = 0.0003    # learning_rate
        self.ppo_sarl_gamma         = 0.99                    
        self.ppo_sarl_gae_lambda    = 0.95      # Smoothing parameter
        self.ppo_sarl_policy_clip   = 0.2       # Sorgt dafür, dass der Loss angehoben wird
        self.ppo_sarl_hidden1       = 1024  #8192 #1024
        self.ppo_sarl_hidden2       = 128   #1024 #128
        self.ppo_sarl_evalMode      = False     # True = Deterministic

        ### PPO MARL
        self.ppo_marl_output_folder      = "ppo_output"
        self.ppo_marl_checkpoint_folder  = "ppo_checkpoints"
        self.ppo_marl_name          = "PPO_MARL"
        self.ppo_marl_batch_size    = 128
        self.ppo_marl_n_epochs      = 4
        self.ppo_marl_alpha         = 0.0003    # learning_rate
        self.ppo_marl_gamma         = 0.99                    
        self.ppo_marl_gae_lambda    = 0.95      # Smoothing parameter
        self.ppo_marl_policy_clip   = 0.2       # Sorgt dafür, dass der Loss angehoben wird
        self.ppo_marl_hidden1       = 1024  #8192 #1024
        self.ppo_marl_hidden2       = 128   #1024 #128
        self.ppo_marl_evalMode      = False     # True = Deterministic

        #####################################################################

        self.env_ActionSpace = 30
        self.env_state_space = 1378
        self.checkpointAfter = 50
        self.modelExportAfter= 2500        

        #####################################################################

        self.avgOverLastRuns = 50

        #####################################################################
        self.askAgainIfMalfunctionWasDetected = False
        self.ammount_of_episodes = 200000
        self.ammount_of_eval_episodes = 1000
        self.simulation_duration = 1    # in Days
        self.steps_per_second = 1       # determines the increment
        self.max_steps = (self.simulation_duration * 60 * 60 * 24) * self.steps_per_second
        self.uncertainty_in_operation_times = 1

        self.ammount_of_carriers = 16
        self.ammount_of_Products = 64


        self.product_workplans = [
            [10,20,30,40,50,60,70,80,90],
            [10,20,30,40,50,60,70,   90],
            [10,20,30,   50,60,70,   90],
            [10,20,         60,70,   90],
            [10,20,30,40,            90],
            [10,20,30,40,50,         90],
        ]#    A B  C  D   E  F  G  H  I
        self.all_possible_operationss = [10,20,30,40,50,60,70,80,90]
        self.lot_size_min = 1
        self.lot_size_max = 3
        self.product_families = ["A", "B"]

        self.ammount_of_OperationFluctuations = 10 * 1000
        self.ammount_of_FailureEvents = 10 * 1000

        self.conveyor = [
    #   0       1               2           3           4       5       6        
    #[SlotID, [nextSlotIDs -> normal, aktivation#1, activation#2,... ], "typ", [PositonX,PositionY], color, description, Carrier]
        [  0,  [  1      ],  "station",     [21, 1],"green",	"S1" , None],
        [  1,  [  2      ],  "normal",      [20, 1],"darkgray",	False, None],
        [  2,  [  3      ],  "normal",      [19, 1],"darkgray",	False, None],
        [  3,  [  4      ],  "normal",      [18, 1],"darkgray",	False, None],
        [  4,  [  5      ],  "normal",      [17, 1],"darkgray",	False, None],
        [  5,  [  6      ],  "normal",      [16, 1],"darkgray",	False, None],
        [  6,  [  7      ],  "station",     [15, 1],"green",	"S2" , None],
        [  7,  [  8      ],  "normal",      [14, 1],"darkgray",	False, None],
        [  8,  [  9,  84 ],  "intersection",[13, 1],"red",		"I1" , None],
        [  9,  [  10     ],  "critical_i",  [12, 1],"coral",	False, None],
        [  10, [  11     ],  "normal",      [11, 1],"darkgray",	False, None],
        [  11, [  12     ],  "normal",      [10, 1],"darkgray",	False, None],
        [  12, [  13     ],  "station",     [ 9, 1],"green",	"S3" , None],
        [  13, [  14     ],  "normal",      [ 8, 1],"darkgray",	False, None],
        [  14, [  15,  85],  "intersection",[ 7, 1],"darkgray",	"I2" , None],
        [  15, [  16     ],  "critical_i",  [ 6, 1],"darkgray",	False, None],
        [  16, [  17     ],  "normal",      [ 5, 1],"darkgray",	False, None],
        [  17, [  18     ],  "normal",      [ 4, 1],"darkgray",	False, None],
        [  18, [  19     ],  "normal",      [ 3, 1],"darkgray",	False, None],
        [  19, [  20     ],  "normal",      [ 2, 1],"darkgray",	False, None],
        [  20, [  21     ],  "normal",      [ 1, 1],"darkgray",	False, None],
        [  21, [  22     ],  "normal",      [ 1, 2],"darkgray",	False, None],
        [  22, [  23     ],  "normal",      [ 1, 3],"darkgray",	False, None],
        [  23, [  24,  92],  "bypass",      [ 2, 3],"red",		"B1" , None],
        [  24, [  25     ],  "critical_b",  [ 3, 3],"darkgray",	False, None],
        [  25, [  26     ],  "normal",      [ 4, 3],"darkgray",	False, None],
        [  26, [  27     ],  "normal",      [ 5, 3],"darkgray",	False, None],
        [  27, [  28     ],  "normal",      [ 6, 3],"darkgray",	False, None],
        [  28, [  29     ],  "normal",      [ 7, 3],"darkgray",	False, None],
        [  29, [  30     ],  "normal",      [ 8, 3],"darkgray",	False, None],
        [  30, [  31     ],  "station",     [ 9, 3],"green",	"S5" , None],
        [  31, [  32     ],  "normal",      [10, 3],"darkgray",	False, None],
        [  32, [  33,  86],  "intersection",[11, 3],"darkgray",	"I3" , None],
        [  33, [  34     ],  "critical_i",  [12, 3],"darkgray",	False, None],
        [  34, [  35     ],  "normal",      [13, 3],"darkgray",	False, None],
        [  35, [  36     ],  "normal",      [14, 3],"darkgray",	False, None],
        [  36, [  37     ],  "normal",      [15, 3],"darkgray",	False, None],
        [  37, [  38     ],  "normal",      [16, 3],"darkgray",	False, None],
        [  38, [  39,  87],  "intersection",[17, 3],"darkgray",	"I4" , None],
        [  39, [  40     ],  "critical_i",  [18, 3],"darkgray",	False, None],
        [  40, [  41     ],  "normal",      [19, 3],"darkgray",	False, None],
        [  41, [  42     ],  "normal",      [20, 3],"darkgray",	False, None],
        [  42, [  43     ],  "station",     [21, 3],"darkgray",	"S6" , None],
        [  43, [  44     ],  "normal",      [22, 3],"darkgray",	False, None],
        [  44, [  45     ],  "normal",      [23, 3],"darkgray",	False, None],
        [  45, [  46     ],  "normal",      [24, 3],"darkgray",	False, None],
        [  46, [  47     ],  "normal",      [25, 3],"darkgray",	False, None],
        [  47, [  48     ],  "normal",      [26, 3],"darkgray",	False, None],
        [  48, [  49     ],  "station",     [27, 3],"green",	"S7" , None],
        [  49, [  50     ],  "normal",      [28, 3],"darkgray",	False, None],
        [  50, [  51,  88],  "intersection",[29, 3],"darkgray",	"I5" , None],
        [  51, [  52     ],  "critical_i",  [30, 3],"darkgray",	False, None],
        [  52, [  53     ],  "normal",      [31, 3],"darkgray",	False, None],
        [  53, [  54     ],  "normal",      [32, 3],"darkgray",	False, None],
        [  54, [  55     ],  "station",     [33, 3],"green",	"S8" , None],
        [  55, [  56     ],  "normal",      [34, 3],"darkgray",	False, None],
        [  56, [  57,  89],  "intersection",[35, 3],"darkgray",	"I6" , None],
        [  57, [  58     ],  "critical_i",  [36, 3],"darkgray",	False, None],
        [  58, [  59     ],  "normal",      [37, 3],"darkgray",	False, None],
        [  59, [  60,  97],  "bypass",      [38, 3],"darkgray",	"B2" , None],
        [  60, [  61     ],  "critical_b",  [39, 3],"darkgray",	False, None],
        [  61, [  62     ],  "normal",      [40, 3],"darkgray",	False, None],
        [  62, [  63     ],  "normal",      [41, 3],"darkgray",	False, None],
        [  63, [  64     ],  "normal",      [41, 2],"darkgray",	False, None],
        [  64, [  65     ],  "normal",      [41, 1],"darkgray",	False, None],
        [  65, [  66     ],  "normal",      [40, 1],"darkgray",	False, None],
        [  66, [  67     ],  "station",     [39, 1],"green",	"S10", None],
        [  67, [  68     ],  "normal",      [38, 1],"darkgray",	False, None],
        [  68, [  69     ],  "normal",      [37, 1],"darkgray",	False, None],
        [  69, [  70     ],  "normal",      [36, 1],"darkgray",	False, None],
        [  70, [  71     ],  "normal",      [35, 1],"darkgray",	False, None],
        [  71, [  72     ],  "normal",      [34, 1],"darkgray",	False, None],
        [  72, [  73     ],  "station",     [33, 1],"darkgray",	"S11", None],
        [  73, [  74     ],  "normal",      [32, 1],"darkgray",	False, None],
        [  74, [  75,  90],  "intersection",[31, 1],"darkgray",	"I7" , None],
        [  75, [  76     ],  "critical_i",  [30, 1],"darkgray",	False, None],
        [  76, [  77     ],  "normal",      [29, 1],"darkgray",	False, None],
        [  77, [  78     ],  "normal",      [28, 1],"darkgray",	False, None],
        [  78, [  79     ],  "station",     [27, 1],"green",	"S12", None],
        [  79, [  80     ],  "normal",      [26, 1],"darkgray",	False, None],
        [  80, [  81,  91],  "intersection",[25, 1],"darkgray",	"I8" , None],
        [  81, [  82     ],  "critical_i",  [24, 1],"darkgray",	False, None],
        [  82, [  83     ],  "normal",      [23, 1],"darkgray",	False, None],
        [  83, [  0      ],  "normal",      [22, 1],"darkgray",	False, None],
        [  84, [  34     ],  "critical_i",  [13, 2],"darkgray",	False, None],
        [  85, [  28     ],  "critical_i",  [ 7, 2],"darkgray",	False, None],
        [  86, [  10     ],  "critical_i",  [11, 2],"darkgray",	False, None],
        [  87, [  4      ],  "critical_i",  [17, 2],"darkgray",	False, None],
        [  88, [  76     ],  "critical_i",  [29, 2],"darkgray",	False, None],
        [  89, [  70     ],  "critical_i",  [35, 2],"darkgray",	False, None],
        [  90, [  52     ],  "critical_i",  [31, 2],"darkgray",	False, None],
        [  91, [  46     ],  "critical_i",  [25, 2],"darkgray",	False, None],
        [  92, [  93     ],  "critical_b",  [ 2, 4],"darkgray",	False, None],
        [  93, [  94     ],  "normal",      [ 2, 5],"darkgray",	False, None],
        [  94, [  95     ],  "normal",      [ 3, 5],"darkgray",	False, None],
        [  95, [  96     ],  "station",     [ 4, 5],"green",	"S4" , None],
        [  96, [  25     ],  "normal",      [ 4, 4],"darkgray",	False, None],
        [  97, [  98     ],  "critical_b",  [38, 4],"darkgray",	False, None],
        [  98, [  99     ],  "normal",      [38, 5],"darkgray",	False, None],
        [  99, [  100    ],  "normal",      [39, 5],"darkgray",	False, None],
        [  100,[  101    ],  "station",     [40, 5],"green",	"S9" , None],
        [  101,[  61     ],  "normal",      [40, 4],"darkgray",	False, None],         
    ]
    
        '''self.stations = [
        ############################################################ - S1
        {   
            "Id"            :   "S1",    
            "Location"      :   0,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   2,
            "UnloadTime"    :   2,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "10": {
                    "BreakdownState" : False,
                    "OperationsTime" : 27,
                    },
                "90": {
                    "BreakdownState" : False,
                    "OperationsTime" : 26,
                    },
            }, 
            "Carrier"       : None
        },
        ############################################################
        {
            "Id"            :   "S2",    
            "Location"      :   6,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "60": {
                    "BreakdownState" : False,
                    "OperationsTime" : 29,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S3",    
            "Location"      :   12,           # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "70": {
                    "BreakdownState" : False,
                    "OperationsTime" : 31,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S4",    
            "Location"      :   95,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   5,
            "UnloadTime"    :   5,
            "SetupTime"     :   20,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "30": {
                    "BreakdownState" : False,
                    "OperationsTime" : 32,
                    },
                "40": {
                    "BreakdownState" : False,
                    "OperationsTime" : 28,
                    },
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S5",    
            "Location"      :   30,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   2,
            "UnloadTime"    :   2,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "50": {
                    "BreakdownState" : False,
                    "OperationsTime" : 27,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S6",    
            "Location"      :   42,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   2,
            "UnloadTime"    :   2,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "10": {
                    "BreakdownState" : False,
                    "OperationsTime" : 26,
                    },
                "90": {
                    "BreakdownState" : False,
                    "OperationsTime" : 27,
                    },
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S7",    
            "Location"      :   48,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "70": {
                    "BreakdownState" : False,
                    "OperationsTime" : 33,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S8",    
            "Location"      :   54,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "20": {
                    "BreakdownState" : False,
                    "OperationsTime" : 32,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S9",    
            "Location"      :   100,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   5,
            "UnloadTime"    :   5,
            "SetupTime"     :   20,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "20": {
                    "BreakdownState" : False,
                    "OperationsTime" : 34,
                    },
                "30": {
                    "BreakdownState" : False,
                    "OperationsTime" : 36,
                    },
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S10",    
            "Location"      :   66,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   2,
            "UnloadTime"    :   2,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "50": {
                    "BreakdownState" : False,
                    "OperationsTime" : 27,
                    }
            }, 
            "Carrier"       : None
        },
        ############################################################
        {
            "Id"            :   "S11",    
            "Location"      :   72,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "80": {
                    "BreakdownState" : False,
                    "OperationsTime" : 26,
                    }
            }, 
            "Carrier"       : None
        },
        ############################################################
        {
            "Id"            :   "S12",    
            "Location"      :   78,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                "60": {
                    "BreakdownState" : False,
                    "OperationsTime" : 32,
                    }
            }, 
            "Carrier"       : None
        }
    ]'''
        self.stations = [
        ############################################################ - S1
        {   
            "Id"            :   "S1",    
            "Location"      :   0,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   2,
            "UnloadTime"    :   2,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                10: {
                    "BreakdownState" : False,
                    "OperationsTime" : 27,
                    },
                90: {
                    "BreakdownState" : False,
                    "OperationsTime" : 26,
                    },
            }, 
            "Carrier"       : None
        },
        ############################################################
        {
            "Id"            :   "S2",    
            "Location"      :   6,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                60: {
                    "BreakdownState" : False,
                    "OperationsTime" : 29,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S3",    
            "Location"      :   12,           # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                70: {
                    "BreakdownState" : False,
                    "OperationsTime" : 31,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S4",    
            "Location"      :   95,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   5,
            "UnloadTime"    :   5,
            "SetupTime"     :   20,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                30: {
                    "BreakdownState" : False,
                    "OperationsTime" : 32,
                    },
                40: {
                    "BreakdownState" : False,
                    "OperationsTime" : 28,
                    },
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S5",    
            "Location"      :   30,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   2,
            "UnloadTime"    :   2,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                50: {
                    "BreakdownState" : False,
                    "OperationsTime" : 27,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S6",    
            "Location"      :   42,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   2,
            "UnloadTime"    :   2,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                10: {
                    "BreakdownState" : False,
                    "OperationsTime" : 26,
                    },
                90: {
                    "BreakdownState" : False,
                    "OperationsTime" : 27,
                    },
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S7",    
            "Location"      :   48,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                70: {
                    "BreakdownState" : False,
                    "OperationsTime" : 33,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S8",    
            "Location"      :   54,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                20: {
                    "BreakdownState" : False,
                    "OperationsTime" : 32,
                    }
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S9",    
            "Location"      :   100,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   5,
            "UnloadTime"    :   5,
            "SetupTime"     :   20,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                20: {
                    "BreakdownState" : False,
                    "OperationsTime" : 34,
                    },
                30: {
                    "BreakdownState" : False,
                    "OperationsTime" : 36,
                    },
            }, 
            "Carrier"       : None
                },
        ############################################################
        {
            "Id"            :   "S10",    
            "Location"      :   66,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   2,
            "UnloadTime"    :   2,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                50: {
                    "BreakdownState" : False,
                    "OperationsTime" : 27,
                    }
            }, 
            "Carrier"       : None
        },
        ############################################################
        {
            "Id"            :   "S11",    
            "Location"      :   72,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   15,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                80: {
                    "BreakdownState" : False,
                    "OperationsTime" : 26,
                    }
            }, 
            "Carrier"       : None
        },
        ############################################################
        {
            "Id"            :   "S12",    
            "Location"      :   78,            # SlotID
            "State"         :   "Idel",
            "Progress"      :   0,
            "LoadTime"      :   1,
            "UnloadTime"    :   1,
            "SetupTime"     :   10,
            "IndividualOperationTime"   :   -1,
            "EquippedProductFamily" :   "A",  
            "Operations"    :   {
                60: {
                    "BreakdownState" : False,
                    "OperationsTime" : 32,
                    }
            }, 
            "Carrier"       : None
        }
    ]
        # Poisson_event_entry_times
        #generate LookupTable
        try:
            print("OPEN")
            with open('poisson_event_entry_times_lookup.pkl', 'rb') as f:
                self.poisson_event_entry_times_lookup = pickle.load(f)
        except:
            print("generate new file: poisson_event_entry_times_lookup")
            self.poisson_event_entry_times_lookup = self.generate_poisson_event_entry_times()
            with open('poisson_event_entry_times_lookup.pkl', 'wb') as f:
                pickle.dump(self.poisson_event_entry_times_lookup, f)

    def custom_poisson_lambda(self, t):
        if t < 800:
            return 0.02  # Anfangs höhere Rate
        elif t < 2400:
            return 0.005  # Niedrigere Rate
        else:
            return 0.02  # Erhöhte Rate

    def generate_poisson_event_entry_times(self):
        min_time = 180
        max_time = 3600
        event_times = []
        t = min_time

        while t <= max_time:
            poisson_rate = self.custom_poisson_lambda(t)
            time_to_next_event = np.random.poisson(poisson_rate)
            if t + time_to_next_event > max_time:
                break
            t += time_to_next_event
            event_times.append(t)
        return event_times