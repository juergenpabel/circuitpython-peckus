import time

class StateMachine:

    def __init__(self, name):
        self.name = name
        self.currentState = None
        self.states = {}
        self.transitions = set()
        self.stopwatch = time.time()


    class State:
        def __init__(self, name, onEnter, onUpdate, onExit):
            self.name = name
            self.onEnter = self.NullCheck(onEnter)
            self.onUpdate = self.NullCheck(onUpdate)
            self.onExit = self.NullCheck(onExit)
        def NullCheck(self, action):
            if action == None:
                return lambda: {}
            return action
    class Transition:
        def __init__(self, origin, condition, destination, transitionProc):
            self.origin = origin
            self.condition = condition
            self.destination = destination
            self.transitionProc = transitionProc
        
    


    def GetCurrentState(this):
        return this.currentState

    def GetTimeSinceTransition(self):
        return time.time() - self.stopwatch

    def AddState(self, name, onEnter=None, onUpdate=None, onExit=None):
        state = self.State(name, onEnter, onUpdate, onExit);
        self.states[name] = state

    def AddTransition(self, origin, condition, destination, tranistionProc=None):
        self.transitions.add(self.Transition(origin, condition, destination, tranistionProc))

    def SetState(self,name):
        self.stopwatch = time.time()

        self.currentState = self.states[name]
        self.currentState.onEnter()

    def Update(self):
        self.currentState.onUpdate()

        for transition in self.transitions:
            if transition.origin == self.currentState.name:
                if transition.condition():
                    self.currentState.onExit()
                    if transition.transitionProc != None:
                        transition.transitionProc()
                    print("going from ",transition.origin, " to ", transition.destination)

                    self.SetState(transition.destination)