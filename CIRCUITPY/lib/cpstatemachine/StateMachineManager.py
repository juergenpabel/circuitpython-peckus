from .StateMachine import StateMachine

temp = 0
class StateMachineManager:
    
    def __init__(self):
        self.stateMachines = {}

    def CreateStateMachine(self, name):
        sm = StateMachine(name)
        self.stateMachines[name] = sm
        return sm;

    def GetStateMachine(self,name):
        return self.stateMachines[name]

    def Update(self):
        for sm in self.stateMachines:
            self.stateMachines[sm].Update()

    def Test(self):
        smManager = StateMachineManager()

        sm = smManager.CreateStateMachine("first machine")

        sm.AddState("start", lambda: print("starting up!"), None,None)
        
        
        def onExit():
            global temp 
            print("temp is: " + str(temp))  
            temp = temp + 1

        sm.AddState("update", None,  onExit, lambda: print("Update complete") );
                    

        sm.AddTransition("start", lambda : True, "update", None);

        sm.AddState("end", lambda: print("End"));
        sm.AddTransition("update", lambda: temp>5, "end");


        sm.SetState("start");
        for n in range(10):
            smManager.Update()
