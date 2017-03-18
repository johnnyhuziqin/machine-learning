import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import numpy as np

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.previous_st = None
        self.previous_act = None
        self.previous_r = 0
        self.trial_cnt = 0
        self.gamma = 0

    
    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        #e_decay = 0.02

        #if self.epsilon > e_decay:
        #    self.epsilon = self.epsilon - e_decay

        #env = Environment()
        t = self.trial_cnt
        self.trial_cnt += 1
        a = 0.97
        #self.epsilon = a**t 
        self.epsilon = 1 - a**((1000-t)/10) 
        #self.epsilon -= 0.001
        #self.epsilon = a**(t/10)
        print "the counter is:",t   

        if testing == True:
            self.epsilon = 0
            self.alpha = 0
            self.trial_cnt = 0

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        
        # Set 'state' as a tuple of relevant data for the agent        
        #state = (waypoint,is_red_light,is_no_conflict)
        state = (waypoint,inputs['light'],inputs['left'],inputs['right'],inputs['oncoming'])
        #print state
        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
        
        return max(self.Q[state].values())


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0

        if self.learning:
            self.Q.setdefault(state, {action: 0.0  for action in self.valid_actions})
        print "the Q size:",len(self.Q)
        

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state
        
        
        if self.learning == False:
            k = random.randint(0,len(self.valid_actions)-1)
            action = self.valid_actions[k]
        else:
            if  random.random() < self.epsilon :
                prior_list = []  #hu: want to priorly explore those action whose have not yet been done
                for k in self.Q[state]:
                    if self.Q[state][k] == 0:
                        prior_list.append(k)
                if len(prior_list) > 0:
                    action = random.choice(prior_list)
                else:              
                    action = random.choice(self.valid_actions)      
            else:
                
                actions = self.Q[state]
                max_key = None
                max_val = min(actions)
                for key in actions:
                    if actions[key] > max_val:
                        max_val = actions[key]
                        max_key = key

                #for some case, if there exist more than one max Q
                max_key_list = []
                for key in actions:
                    if actions[key] == max_val:
                        max_key_list.append(key)
                if len(max_key_list)>1:
                    print "there exist more than one max Q"        

                #print "max_key_list:",max_key_list    
                action = random.choice(max_key_list)
        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.previous_st != None:
            #qsa = self.Q[self.previous_st][self.previous_act]
            #self.Q[self.previous_st][self.previous_act] = (1- self.alpha)*qsa + self.alpha*(self.previous_r + self.get_maxQ(state))
            bias = 0
            #print "learning %r,%r"%(self.previous_st[0],self.previous_act)
              
            #self.Q[self.previous_st][self.previous_act] = self.previous_r + self.alpha*(self.get_maxQ(state)) #+ bias
            #self.Q[self.previous_st][self.previous_act] = (1 - self.alpha)*self.Q[self.previous_st][self.previous_act] \
            #+ self.alpha*(self.previous_r + self.gamma*self.get_maxQ(state))
            self.Q[state][action] = self.Q[state][action] + self.alpha * (reward - self.Q[state][action])
        #    print "we learn prev st:%r prev act:%r r:%r st:%r maxQ:%r"%(self.previous_st,self.previous_act,reward,state,self.get_maxQ(state))
        
        
        self.previous_st = state    
        self.previous_act = action
        self.previous_r = reward
        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment(verbose = False)
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent,learning = True,epsilon = 1,alpha = 0.6)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent,enforce_deadline = True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env,update_delay = 0.001,display = False,log_metrics = True,optimized = True)
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(tolerance = 0.01,n_test = 30)


if __name__ == '__main__':
    run()