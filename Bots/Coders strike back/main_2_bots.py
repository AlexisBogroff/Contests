# Coders Strike Back: multi bots control
# Credit: Alexis Bogroff
# alexis.bogroff.contact@gmail.com

import sys
import math
import pandas as pd

# V0: handles n bots, skeleton, dumb strat ok

# TODO
# 1. delete eval state ? (agent and pod extention)

class Env:
    """
    Class gathering map informations
    """
    def __init__(self, debug = False):
        self._lst_cp_x = []
        self._lst_cp_y = []
        self._cps_count = None
        self.laps = None

        # Callable Inputs() become variables inputs
        self.DEBUG = debug

    def analyze_map(self):
        """
        Analyze structures that can be taken advantage of:
        - all map: circle, square, snake
        - cp: dead-end, line-gate, curve-gate
        """
        raise NotImplementedError
        

    def get_cp_pos(self, cp_id):
        """ Obtain x,y for a given cp """
        x = self._lst_cp_x[cp_id]
        y = self._lst_cp_y[cp_id]
        return (x, y)


    def get_neighbors_cp(self, curr_cp_id):
        """ Get prev and next cp_ids """
        if curr_cp_id == 0:
            prev_cp_id = (self._cps_count - 1)
            next_cp_id = 1
        elif curr_cp_id == (self._cps_count - 1):
            next_cp_id = 0
            prev_cp_id = (self._cps_count - 2)
        else:
            prev_cp_id = curr_cp_id - 1
            next_cp_id = curr_cp_id + 1

        return (prev_cp_id, next_cp_id)

        
    def set_cps_lists(self, input):
        """
        Retrieve cp positions from game input
        """
        # Get input
        for i in range(self._cps_count):
            if not self.DEBUG:
                pos_cp = [int(j) for j in input().split()]
            else:
                pos_cp = [int(j) for j in input[i].split()]
            self._lst_cp_x.append(pos_cp[0])
            self._lst_cp_y.append(pos_cp[1])
                

    def set_cp_count(self, input):
        """ Retrieve cp count from game input """
        if not self.DEBUG:
            self._cps_count = int(input())
        else:
            self._cps_count = int(input)

        
    def set_laps(self, input):
        if not self.DEBUG:
            self.laps = int(input())
        else:
            self.laps = int(input)    


class Agent:
    """
    Mother class of Pod and Opponent
    Gather information on agents
    """
    counter_id = 0

    def __init__(self, debug = False):
        # Inputs
        self.x = None
        self.y = None
        self.vx = None
        self.vy = None
        self.angle = None
        self.cp_angle = None
        self.cp_id = None
        self.cp_x = None
        self.cp_y = None
        
        # Other
        self.history = None
        self.dist_bros = None
        self.dist_opponents = None

        # * State categories
        
        # Speed
        self.CAT_SPEED_SLOW     = 100
        self.CAT_SPEED_MEDIUM   = 300
        self.CAT_SPEED_FAST     = 450
        self.CAT_SPEED_VERYFAST = 650
        # Distance
        self.CAT_DIST_CONTACT = 400
        self.CAT_DIST_CP_AREA = 600
        self.CAT_DIST_CLOSE   = 1500
        self.CAT_DIST_FAR     = 2000
        self.CAT_DIST_VERYFAR = 6500
        # Angle
        self.CAT_ANGLE_STRAIGHT = 4
        self.CAT_ANGLE_SMOOTH = 10
        self.CAT_ANGLE_CURVE = 45
        self.CAT_ANGLE_RIGHT = 90
        self.CAT_ANGLE_BACK = 180

        # Increment counter
        Agent.counter_id += 1
        self.id = Agent.counter_id

        self.DEBUG = debug



    def history(self):
        """ Return last append row (most recent data) """
        return self.history.iloc[-1]

    @property
    def dist_cp(self):
        """ Compute distance pod to cp """
        return compute_dist_btw_2points(self.pos, self.cp)

    @property
    def speed(self):
        """ Return speed on combined x and y axes """
        return abs(self.vx) + abs(self.vy)

    @property
    def pos(self):
        """ Return pod position (x, y) """
        return (self.x, self.y)

    @property
    def cp(self, get_id=False):
        """ Return cp position, and id """
        if get_id:
            return (self.cp_x, self.cp_y), self.cp_id
        else:
            return (self.cp_x, self.cp_y)


    def init_history(self):
        """
        Create an empty dataframe with the desired columns
        """
        cols_part_1 = ['x', 'y', 'vx', 'vy', 'cp_id', 'cp_angle']
        cols_part_2 = ['cp_x', 'cp_y', 'dist_bros', 'dist_opponents']
        self.history = pd.DataFrame(columns = cols_part_1 + cols_part_2)


    def append_history(self):
        """
        Append history with new old values
        """
        # Aggregate state values
        dic_new_state = {
            'x':                self.x,
            'y':                self.y,
            'vx':               self.vx,
            'vy':               self.vy,
            'cp_id':            self.cp_id,
            'cp_angle':         self.cp_angle,
            'cp_x':             self.cp_x,
            'cp_y':             self.cp_y,
            'dist_bros':        self.dist_bros,
            'dist_opponents':   self.dist_opponents,
            }

        df_new_state = pd.DataFrame(dic_new_state)

        self.history.append(df_new_state)

    

    def get_relative_angle(self, A, B, CAD, precision = 0):
        """
        Return the relative angle between
        two points, given their absolute position and
        the absolute angle of point A with the EAST at 0

        Used for computing the angle between cp and the pod' nose
        It uses self.angle (which is absolute 0 toward EAST) and substracts
        the other part of the angle to get the remaining self.angle
        """
        # Construct a right rectangle ACB
        
        # Since game repair is EAST at 0, when point C
        # is positioned on different quarters of the gradient
        # circle, the resulting angle must be added
        # the corresponding quarter (0, 90, 180, 270)
        if B[0] > A[0] and B[1] <= A[1]:
            C = (B[0], A[1])
            BAC = 0
        
        elif B[0] <= A[0] and B[1] < A[1]:
            C = (A[0], B[1])
            BAC = 90

        elif B[0] < A[0] and B[1] >= A[1]:
            C = (B[0], A[1])
            BAC = 180

        elif B[0] >= A[0] and B[1] > A[1]:
            C = (A[0], B[1])
            BAC = 270


        # Measure segments AC and BC
        AC = compute_dist_btw_2points(A, C)
        BC = compute_dist_btw_2points(B, C)

        # Use trigo rule tan x = opposed/adjacent
        # to get angle x (BAC)
        BAC += math.degrees(math.atan(BC/AC))

        # When an angle goes further than 180 degrees,
        # say 190, it actually comes closer. So the following
        # applies a transformation to take this effect into account
        if CAD > 180:
            CAD = 360 - CAD
        if BAC > 180:
            BAC = 360 - BAC

        # Deduce angle (BAD)
        # Is the difference between the actual absolute angle (BAC)
        # and the straight most angle toward cp (CAD)
        BAD = CAD - BAC

        return round(BAD, precision)


    def set_cp(self, curr_cp_id, env):
        """ Set current cp position given cp_ip """
        self.cp_x, self.cp_y = env.get_cp_pos(curr_cp_id)
        self.cp_angle = self.get_relative_angle(self.pos, self.cp, self.angle)


    def get_game_loop_infos(self, input):
        """ Retrieve game loop informations """
        
        # Retrieve infos
        if not self.DEBUG:
            infos = [int(j) for j in input().split()]
        else:
            infos = [int(j) for j in input.split()]
        
        # Parse infos
        self.x = infos[0];    self.y = infos[1]
        self.vx = infos[2];   self.vy = infos[3]
        self.angle = infos[4]
        self.cp_id = infos[5]

    def dispaly_infos(self, verbose = 1):
        """ Display infos """
        if verbose == 1:
            # Agent cp infos
            print("cp_target: {} - ({}) ({})".format(self.cp_id, self.cp_x, self.cp_y), file=sys.stderr)
                    
        if verbose == 2:
            # Agent spacial infos
            print("\n-- Agent infos --", file=sys.stderr)
            print("\tPos: {} {}".format(self.x, self.y), file=sys.stderr)
            print("\tSpeed: {} {}".format(self.vx, self.vy), file=sys.stderr)
            print("\tAngle: {}".format(self.cp_angle), file=sys.stderr)


    def eval_mvt_cat(cat_angle, cat_speed_meta):
        """
        Evaluates the overall movement and return the
        corresponding category:
        - drifting
        - bombing
        """
        if cat_speed_meta == 'high':
            if cat_angle == 'straight':
                cat_mvt = 'bombing'
            elif cat_angle in ['smooth', 'curve']:
                cat_mvt = 'drifting'

        if not cat_mvt:
            cat_mvt = None
        # TODO: rebuild now that categories are dropped
        raise NotImplementedError



    def eval_state(self):
        """
        Evaluate the categories of state variables
        ie. interpret low level values

        # Personal
        - movement: straight, drifting
        
        # Others
        - dist brother: contact, close, far, very far
        - dist opponents: contact, close, far, very far
        """
        # ----- Personal -----
    
        cat_movement = self.eval_mvt_cat(self.cat_angle_cp, self.cat_speed_meta)


    def update_state_info(self, input, env):
        """
        Update low level personal state variables
        
        1. Retrieve infos
        2. Set cp position
        """
        # Retrieve state infos
        self.get_game_loop_infos(input)
        
        # Set target cp position
        self.set_cp(self.cp_id, env)



class Opponent(Agent):
    """ Class for opponents' information """
    def __init__(self):
        Agent.__init__(self)



class Pod(Agent):
    """
    Main class controlling the pod and
    aggrregating informations from the game
    """
    def __init__(self, debug = False):
        Agent.__init__(self, debug)
        # Instructions
        self.target_x = None
        self.target_y = None
        self.thrust   = None

        # Other
        self.strat    = None
        self.strat_fc = None
        self.boost_available = True


    def init_history(self):
        """
        Create an empty dataframe with the desired columns
        """
        agent_cols = ['x', 'y', 'vx', 'vy', 'cp_id', 'cp_angle', 'cp_x', 'cp_y']
        pod_cols1 = ['target_x', 'target_y', 'thrust', 'strat', 'boost_available']
        pod_cols2 = ['speed', 'dist_bros', 'dist_opponents']
        self.history = pd.DataFrame(columns = agent_cols + pod_cols1 + pod_cols2)


    def append_history(self):
        """
        Append history with new old values
        """
        # Aggregate state values
        dic_new_state = {
            'x':                self.x,
            'y':                self.y,
            'vx':               self.vx,
            'vy':               self.vy,
            'cp_id':            self.cp_id,
            'cp_angle':         self.cp_angle,
            'cp_x':             self.cp_x,
            'cp_y':             self.cp_y,
            'target_x':         self.target_x,
            'target_y':         self.target_y,
            'thrust':           self.thrust,
            'strat':            self.strat,
            'boost_available':   self.boost_available,
            'speed':            self.speed,
            'dist_bros':        self.dist_bros,
            'dist_opponents':   self.dist_opponents,
            }

        df_new_state = pd.DataFrame(dic_new_state, index=dic_new_state.keys())

        self.history.append(df_new_state)



    def do_strat(self):
        """ Execute action given target x,y and thrust """
        # Set strat
        self.strat_fc()
        # Execute
        print("{x} {y} {thrust}".format(x=self.target_x, y=self.target_y, thrust=self.thrust))


    def dispaly_infos(self, verbose = 1):
        """ Display low level infos (pos) and high level (strategy) """
        # High level infos
        print("*** Pod {} ***".format(self.id), file=sys.stderr)
        print("Strat: {}".format(self.strat), file=sys.stderr)

        # Low level infos
        Agent.dispaly_infos(self, verbose = verbose)


    def eval_state(self):
        """
        Evaluate state as an agent, plus:
        
        # Others
        - communication bro: (received msg, agree), (received, disagree), ...
        - opponents dist: contact, close, far, very far
        """
        Agent.eval_state(self)


    def evaluate_strategy(self, env):
        """
        Evaluate the strategy to apply for the pod:
        > Combine features:
        - map structure (all, indiv-cp)
        - state current and prev (personal, others)
        - next state and errors in prediction
        
        # TODO: grade strats by state

        [for now]:
        select between full_straight, break_drift and mollo
        """
        print("self.speed", self.speed, file=sys.stderr)
        # Far
        if self.dist_cp >= self.CAT_DIST_CLOSE:
            # Away > assess angle
            if abs(self.cp_angle) < self.CAT_ANGLE_BACK:
                # Aligned > Straight and full power (or boost)
                self.strat_fc = self.strat_full_straight
            else:
                # Desaxed > straight medium thrust
                self.strat_fc = self.strat_mollo

        else:
            # Approaching > assess speed:
            if self.speed > self.CAT_SPEED_FAST:
                # Fast > Full thrust in opposite direction (to brake)
                #self.strat_fc = self.strat_break
                self.strat_fc = self.strat_drift
            else:
                # Slow > straight medium thrust
                self.strat_fc = self.strat_mollo


        # print("dist", self.dist_cp, file=sys.stderr)
        # print("speed", self.speed, file=sys.stderr)
        # print("angle relative", self.cp_angle, file=sys.stderr)
        # # Proximity to cp max
        # if self.dist_cp <= self.CAT_DIST_CLOSE:
        #     #TODO: what if going from there?
        #     # elif going toward (approaching)
        #     if self.speed <= self.CAT_SPEED_SLOW:
        #         # Slow > go straight @ medium thrust
        #         self.strat_fc = self.strat_mollo
        #     else:
        #         # Fast > Full thrust in opposite direction (to brake)
        #         self.strat_fc = self.strat_break

        # elif self.dist_cp <= self.CAT_DIST_FAR:
        #     if self.speed <= self.CAT_SPEED_FAST:
        #         # Medium/Fast > go straight @ full thrust
        #         self.strat_fc = self.strat_full_straight
        #     else:
        #         # VeryFast > Full thrust in opposite direction (to brake)
        #         self.strat_fc = self.strat_break
        
        # elif self.dist_cp <= self.CAT_DIST_VERYFAR:
        #     # VeryFar
        #     if abs(self.cp_angle) < self.CAT_ANGLE_CURVE:
        #         self.strat_fc = self.strat_full_straight
        #     else:
        #         # Slightly desaxed > go mollo
        #         self.strat_fc = self.strat_mollo

        # else:
        #     if abs(self.cp_angle) < self.CAT_ANGLE_SMOOTH:
        #         # Aligned > Straight and full power (or boost)
        #         if self.boost_available:
        #             self.strat_fc = self.strat_boost
        #         else:
        #             self.strat_fc = self.strat_full_straight
            
        #     elif abs(self.cp_angle) < self.CAT_ANGLE_CURVE:
        #         # Slightly desaxed > go mollo
        #         self.strat_fc = self.strat_mollo



    def update_state_info(self, input, env):
        """
        Update state low level infos:
        - speed
        - dist_cp
        """
        Agent.update_state_info(self, input, env)


    def predict_state(self):
        """
        Predict the state reached after the action is done
        Permits to evaluate the correctness of strategies
        """
        raise NotImplementedError


    def evaluate_predictor(self):
        """
        Evaluate the next-state predictor
        """
        raise NotImplementedError


    def strat_mollo(self):
        """
        Strategy going straight by @ medium speed
        """
        self.target_x = self.cp_x
        self.target_y = self.cp_y
        self.thrust = 40
        self.strat = 'mollo'

    def strat_full_straight(self):
        """
        Strategy consisting of always going toward the next cp
        and at the same speed
        """
        self.target_x = self.cp_x
        self.target_y = self.cp_y
        self.thrust = 100
        self.strat = 'full_straight'
    
    def strat_boost(self):
        """ Boost straight """
        self.target_x = self.cp_x
        self.target_y = self.cp_y
        self.thrust = 'BOOST'
        self.strat = 'BOOST'
        self.boost_available = False

    def strat_temporize(self):
        """ Quasi-stop thrust and put nose straight """
        self.target_x = self.cp_x
        self.target_y = self.cp_y
        self.thrust = 40 # to maintain inertia
        self.strat = 'temporize'

    def strat_break(self):
        """ Full thrust in opposite direction (to break) """
        prev_cp_id = env.get_neighbors_cp(self.cp_id)[0]
        self.target_x = env.get_cp_pos(prev_cp_id)[0]
        self.target_y = env.get_cp_pos(prev_cp_id)[1]
        self.thrust = 100

        self.strat = 'break_drift'

    def strat_drift(self):
        """
        Full thrust toward next cp in order to
        pass the current one while drifting
        """
        next_cp_id = env.get_neighbors_cp(self.cp_id)[1]
        self.target_x = env.get_cp_pos(next_cp_id)[0]
        self.target_y = env.get_cp_pos(next_cp_id)[1]
        self.thrust = 100
        self.strat = 'drift'



def compute_dist_btw_2points(A, B, precision=1):
    """
    Compute distances between two points
    Inputs: (x,y)
    """
    # Retrieve variables
    xa = A[0]; ya = A[1]
    xb = B[0]; yb = B[1]

    # Compute segment' size
    AB = math.sqrt((xb - xa)**2 + (yb - ya)**2)
    
    return round(AB, precision)



if __name__ == '__main__':
    # ==========================================
    #                MAIN
    # ==========================================

    # Instanciate classes
    env = Env()
    pods = [Pod(), Pod()]
    opponents = [Opponent(), Opponent()]
    
    # Retrieve game init information
    env.set_laps(input)
    env.set_cp_count(input)
    env.set_cps_lists(input)

    # Identify map structures
    #env.analyze_map()
    for agent in pods + opponents:
        agent.init_history()

    # game loop
    while True:

        # Update state variables
        for agent in pods + opponents:
            agent.update_state_info(input, env)

        # Select and set strategy
        for pod in pods:
            pod.evaluate_strategy(env)

        # Execute strat
        for pod in pods:
            pod.do_strat()
            pod.dispaly_infos(verbose = 2)

        for pod in pods:
            pod.append_history()
