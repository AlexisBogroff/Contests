# Coders Strike Back: Bot single pod
# Credit: Alexis Bogroff
# alexis.bogroff.contact@gmail.com

import sys
import math
from statistics import variance
import pandas as pd

# V0: power directly toward checkpoint
# V1:[solved!] braking system - power opposite direction when approaching
# -> (perfect if no checkpoint is in the same direction)
# V1.1: Transformed to classes and functions
# V2:[not yet working] Mind remembers checkpoints' position and assesses strats
# + pod assesses states (drifting)

# TODO: drift in the right direction
# TODO: transform into pandas vectorial
# TODO: use shield in place of break-drift when opponent is close enough (400units)

"""
GAME VARIABLES:

inputs:
- x: x position of my pod
- y: y position of my pod
- checkpoint_x: x position of the next check point
- checkpoint_y: y position of the next check point
- checkpoint_dist: distance with //
- checkpoint_angle: angle with //

Other variables:
- x_prev: x previous position of my pod
- y_prev: y previous position of my pod
- x_delta: x progression between prev and current position
- y_delta: y progression between prev and current position
- checkpoint_dist_delta
- checkpoint_angle_delta

Ps:
Chronological lists are used in the (unatural) order of the appening.
i.e. oldest element first [t0, t1, t2, ... t]
"""

class Agent:
    """
    Mother class for Pod and opponents
    """
    def __init__(self, x = None, y = None):
        # Core
        self.x = x
        self.y = y
        # Analytics
        self.x_history = []
        self.y_history = []



class Environment:
    """
    Infos on map and other
    - (x,y)=(0,0)= top left pixel
    - it is possible to live outside the visual and come back
    """
    def __init__(self):
        self.game_iter = 0
        # Constants
        self.MAP_HEIGHT = 9000
        self.MAP_WIDTH = 16000
        self.CHECKPOINT_RAYON = 600

    def iter_loop(self):
        """ Increment game loop counter """
        self.game_iter += 1



class Mind:
    """
    Intelligence of the agent
    - remember (checkpoints position, etc.)
    - think (assess optimal strat, etc.)
    """
    
    def __init__(self):
        # Booleans
        self.all_cp_registered = False
        self.strats_assessed = False
        # Ckpts map
        self.checkpoints = {
            'count': 0,
            'map': {},
            }

        # Limits
        self.TOLERANCE_ANGLE_STRAIGHT = 15
        self.THRESHOLD_DO_STRAT = .8
        self.STRAT_CIRCLE_TOLERANCE_VAR = 10
        
        # Structures detected
        self.general_structure = None


    def assess_optimal_trajectory(self):
        """
        Assess optimal trajectory
        returns a list of coordinates to follow from initialcp to initialcp
        """
        if self.general_structure == 'circle':  # equi triangle
            
            # generate 3 intermediate points supposedly on the circle
            # -------------------------------------------------------
            # A is 1, B is 2, C is 3
            
            # Retrieve pcs positions
            A = self.get_cp_position(1)
            B = self.get_cp_position(2)
            C = self.get_cp_position(3)
            
            # Compute distance of segments
            AB = self.get_dist_btw_2points(A, B)
            BC = self.get_dist_btw_2points(B, C)
            AC = self.get_dist_btw_2points(A, C)
            
            # Generate semi-distant points on the straight line btw cps
            semiAB_x = A[0] + (B[0] - A[0]) / 2
            semiAB_y = A[1] + (B[1] - A[1]) / 2
            
            semiBC_x = B[0] + (C[0] - B[0]) / 2
            semiBC_y = B[1] + (C[1] - B[1]) / 2
            
            semiAC_x = C[0] + (A[0] - C[0]) / 2
            semiAC_y = C[1] + (A[1] - C[1]) / 2

            # Compute central point
            central_x = (A[0] + B[0] + C[0]) / 3
            central_y = (A[1] + B[1] + C[1]) / 3
            
            # Compute spread btw semi points and center
            spread_semiAB_x = semiAB_x - central_x
            spread_semiAB_y = semiAB_y - central_y
            
            spread_semiBC_x = semiBC_x - central_x
            spread_semiBC_y = semiBC_y - central_y

            spread_semiAC_x = semiAC_x - central_x
            spread_semiAC_y = semiAC_y - central_y

            # Spread-out the points from the center
            out_semiAB_x = semiAB_x + spread_semiAB_x
            out_semiAB_y = semiAB_y + spread_semiAB_y

            out_semiBC_x = semiBC_x + spread_semiBC_x
            out_semiBC_y = semiBC_y + spread_semiBC_y

            out_semiAC_x = semiAC_x + spread_semiAC_x
            out_semiAC_y = semiAC_y + spread_semiAC_y

            # Group coordinates
            out_semiAB = [out_semiAB_x, out_semiAB_y]
            out_semiBC = [out_semiBC_x, out_semiBC_y]
            out_semiAC = [out_semiAC_x, out_semiAC_y]
            
            #print("A, B", A, B, file=sys.stderr)
            #print("\nsemiAB_x, y", semiAB_x, semiAB_y, file=sys.stderr)
            #print("central_x, y", central_x, central_y, file=sys.stderr)
            #print("spread_semiAB_x, y", spread_semiAB_x, spread_semiAB_y, file=sys.stderr)
            #print("out_semiAB, y", out_semiAB, file=sys.stderr)
            
            #print("\noptimal trajectory semi points"
            #   "\n",out_semiAB, out_semiBC, out_semiAC,file=sys.stderr)
            return out_semiAB, out_semiBC, out_semiAC
            

    def assess_state(self):
        """
        Assess the current state of the pod:
        - drifting:
        -- medium/fast speed AND
        -- (abs(angle) > straight) OR ((distx, disty) not reduced as much as with a stragith line
        """
        # TODO
        pass


    def checkpoint_add(self, cp_x, cp_y, dic_strats):
        """
        Add a checkpoint to the ckpts map
        """
        # Increment counter
        self.checkpoints['count'] += 1
        
        # Take counter as name for the new checkpoint
        ckpt_name = self.checkpoints['count']
        
        # List of strats along with their grade
        dic_strats_grade = {}
        for strat in dic_strats:
            dic_strats_grade[strat] = 0
    
        # Add new ckpt to map
        self.checkpoints['map'][ckpt_name] = {
            'order': ckpt_name,
            'position': (cp_x, cp_y),
            'strats_to_use': dic_strats_grade
            }
        
        print("NEW CHECKPOINT:", ckpt_name, file=sys.stderr)


    def cp_assess_map_structure(self):
        """
        Assess map structure to recognize forms that
        can be exploited with a strat well adapted
        
        """
        
        # ASSESS IF CIRCLE STRUCTURE
        # --------------------------
        
        # works only if 3 checkpoints (triangle):
        if self.checkpoints['count'] == 3:
            
            # Retrieve pcs positions
            A = self.get_cp_position(1)
            B = self.get_cp_position(2)
            C = self.get_cp_position(3)
            
            # Compute distance of segments
            AB = self.get_dist_btw_2points(A, B)
            BC = self.get_dist_btw_2points(B, C)
            AC = self.get_dist_btw_2points(A, C)
            
            # Circle: if segments are equal
            print('AB', AB, file=sys.stderr)
            print('BC', BC, file=sys.stderr)
            print('AC', AC, file=sys.stderr)
            
            # Compute relative diff (return formula)
            diffs = [(BC-AB)/AB, (AC-BC)/BC, (AB-AC)/AC]
            diffs_var = variance(diffs)
            
            print("diffs_var", diffs_var*100, file=sys.stderr)
            
            if diffs_var * 100 < self.STRAT_CIRCLE_TOLERANCE_VAR:
                self.general_structure = 'circle'
                print("strat circle", file=sys.stderr)
                
        else:
            # Retrieve pcs positions
            #for cp_name in self.checkpoints['map']:
            #    get_cp_position(self, cp_name)
            pass
        

    def cp_all_registered(self, x_input, y_input):
        """
        Check if all cp are registered.
        """
        # Check if current checkpoint name is 1
        # AND that there are more than one checkpoint registered
        curr_cp_name = self.get_cp_name(x_input, y_input)
        
        if curr_cp_name == 1 and self.checkpoints['count'] > 1:
            return True
        
            
    def cp_is_registered(self, x_input, y_input):
        """
        Check if ckpt already registered
        
        if (x, y) match:
            return True (else False)
            
        Nb: once it has more than one checkpoint
        it verifies if the current checkpoint is 
        the first one. In that case all checkpoints
        have been discoverd and registered.
        """
        for ckpt_name in self.checkpoints['map']:
            x_stored, y_stored = self.checkpoints['map'][ckpt_name]['position']
                    
            # Compare input vs stored positions
            if x_input == x_stored and y_input == y_stored:
                return True
        
        return False
    
    
    def cp_strats_assessor(self, cp_curr_name, dic_strats):
        """
        Assess optimal strats given checkpoint relative position
        
        Nb: for now, only once a game (since its only based on distance
        between checkpoints, which do not change)
        """
        # Retrieve names of prev and next ckpts:
        cp_prev_name, cp_next_name = self.get_cp_neighbors_name(cp_curr_name)
        print('cp_curr_name', cp_curr_name, file=sys.stderr)

        # Retrieve position of: curr, prev and next ckpts:
        pos_curr_cp = self.get_cp_position(cp_curr_name)
        pos_prev_cp = self.get_cp_position(cp_prev_name)
        pos_next_cp = self.get_cp_position(cp_next_name)

        # Compute cp angle
        cp_angle = self.get_cp_angle(pos_prev_cp, pos_curr_cp, pos_next_cp)


        # Assess strats
        # -------------
        # *** Full_straight ***
        # > Good if prev-curr-next form a line
        # HowTo: Compute the angle at the checkpoint
        # - The gap must be relative to the total distance btw prev and next
        # - also relative to its own distance
        # TODO: use the relative distance to compare angle eligibility
        # TODO: add more granularity (ie find a better metric)

        # Evaluate the strat (given it is adapted if line is very straight)
        if abs(cp_angle) < self.TOLERANCE_ANGLE_STRAIGHT:
            print("Grade = 1 since angle:", cp_angle, file=sys.stderr)
            grade = 1.
        else:
            print("Grade = 0 since angle:", cp_angle, file=sys.stderr)
            grade = 0.
        
        # Update grade in the list of strats for this cp
        self.checkpoints['map'][cp_curr_name]['strats_to_use'][dic_strats['full_straight']['name']] = grade

        # *** Break_drift ***
        # Good if prev-curr-next form a turnaround
        # TODO


    def cp_strats_manager(self, dic_strats):
        """
        Launch the strats evaluation for each cp
        """
        # Only assess for straight line for now
        for cp in self.checkpoints['map']:
            self.cp_strats_assessor(cp, dic_strats)
        
        # Change bool
        self.strats_assessed = True
        
        print("Strats", self.checkpoints['map'], file=sys.stderr)


    def get_cp_position(self, cp_name):
        return self.checkpoints['map'][cp_name]['position']
        

    def get_cp_name(self, x_input, y_input):
        """
        Get the current checkpoint name, given its position
        """
        for ckpt_name in self.checkpoints['map']:
            x_stored, y_stored = self.checkpoints['map'][ckpt_name]['position']
                    
            # Compare input vs stored positions
            if x_input == x_stored and y_input == y_stored:
                return ckpt_name
        
    
    def get_cp_prev(self, curr_cp):
        """
        Get the previous cp name and position
        """
        cp_prev_name, _ = self.get_cp_neighbors_name(curr_cp)
        cp_prev_pos = self.get_cp_position(cp_prev_name)
        
        return cp_prev_name, cp_prev_pos
        
    
    def get_structure_opti_strat(self):
        """
        Returns the name and grade of the optimal strategy
        based on the general map structure
        """
        strat_name = self.general_structure
        strat_grade = 1
        
        return strat_name, strat_grade
        

    def get_dist_btw_2points(self, A, B):
        """
        Compute distances between two points
        """
        # Retrieve variables
        xa = A[0]; ya = A[1]
        xb = B[0]; yb = B[1]

        # Compute segments' size
        AB = math.sqrt((xb - xa)**2 + (yb - ya)**2)
        
        return AB


    def get_cp_angle(self, A, B, C):
        """
        Compute the angle of the cp between prev and next cps
        TODO: compute a real angle
        """
        # Retrieve variables
        xa = A[0]; ya = A[1]
        xb = B[0]; yb = B[1]
        xc = C[0]; yc = C[1]
        
        # Compute slopes
        dab = (yb - ya) / (xb - xa)
        dbc = (yc - yb) / (xc - xb)

        error = abs(dab - dbc) * 100
        
        return error


    def get_cp_opti_strat(self, cp_x, cp_y):
        """
        Return name and grade for highest grade cp strategy
        """
        if self.strats_assessed:
            # Get current checkpoint name
            cp_curr_name = self.get_cp_name(cp_x, cp_y)
            
            # Sort strategies based on their grade for curr checkpoint
            cp_dic_strats = self.checkpoints['map'][cp_curr_name]['strats_to_use']
            cp_strats_ordered = sorted(cp_dic_strats, key = cp_dic_strats.get, reverse = True)
            
            # Extract highest grade strat and name
            cp_strat_opti_name = cp_strats_ordered[0]
            cp_strat_opti_grade = cp_dic_strats[cp_strat_opti_name]

        else:
            cp_strat_opti_name, cp_strat_opti_grade = None, None
            
        return cp_strat_opti_name, cp_strat_opti_grade


    def get_cp_neighbors_name(self, cp_curr_name):
        """
        Returns prev and next checkpoints' name
        - prev of cp 1 is list_cp[-1]
        - next of cp_last is list_cp[0]
        """
        list_names = [name for name in self.checkpoints['map']]
        
        temp_cp_curr_name = cp_curr_name - 1
        
        # if first cp
        if temp_cp_curr_name == 0:
            cp_prev_name = list_names[-1]
            cp_next_name = list_names[temp_cp_curr_name + 1]
        # if last cp
        elif temp_cp_curr_name + 1 == list_names[-1]:
            cp_prev_name = list_names[temp_cp_curr_name - 1]
            cp_next_name = list_names[0]
        else:
            # if middle cp
            cp_next_name = list_names[temp_cp_curr_name + 1]
            cp_prev_name = list_names[temp_cp_curr_name - 1]

        return cp_prev_name, cp_next_name
        

    def select_apply_strategy(self, pod, env):
        """
        [Core Mind function]

        Evaluates, selects and applies a strategy based on:
        - low-level info (relative positions, speed, etc.)
        - high-level (cp map, state, etc.)

        Evaluate: build a list of dics, with ordered strategies names and grades
        [ {'strat_v': grade_v}, {'strat_c': grade_c}, ... ]
        with grade_v > grade_c
        """
        #if env.game_iter < 4:  # 4 because need speed calculation to be done
        #    pod.strat_full_straight(env)

        
        if env.game_iter > 3:
        
            # EVALUATE
            # ========
        
            # Strategies based on clear general structure
            structure_strat_opti_name, structure_strat_opti_grade = self.get_structure_opti_strat()
            
            # Strategies based on cp relative position only (cp_strats_ordered)
            cp_strat_opti_name, cp_strat_opti_grade = self.get_cp_opti_strat(pod.checkpoint_x, pod.checkpoint_y)
    
            # Field strategies (field_strat_opti_name)
            field_strat_opti_name, field_strat_opti_grade = pod.evaluate_opti_strat()


            # SELECT
            # ======
            
            # If a structure strat exist, select it above the rest
            if structure_strat_opti_name:
                strat_opti_name = structure_strat_opti_name
            else:
                # Select the field strat if no cp_strat exist
                if not cp_strat_opti_name:
                    strat_opti_name = field_strat_opti_name
                else:
                    # Select the highest grade
                    if cp_strat_opti_grade > field_strat_opti_grade:
                        strat_opti_name = cp_strat_opti_name
                    else:
                        strat_opti_name = field_strat_opti_name
        
        
        
        elif env.game_iter <= 3:
            strat_opti_name = pod.dic_strats['full_straight']['name']
        
        
        # DISPLAY AND APPLY
        # =================

        # Launch strat parametizer
        pod.strat_launcher(strat_opti_name, env)
        
        # Display infos
        printer_game_info(env, pod, verbose=2)
        
        # Execute strat
        pod._action()


    def updt_cp_map(self, cp_x, cp_y):
        """
        Add new checkpoints' location to the map (cp_x, cp_y)
        """
        # Add checkpoint if not yet registered
        if not self.cp_is_registered(cp_x, cp_y):
            mind.checkpoint_add(cp_x, cp_y, pod.dic_strats)
        
        # check if all cp are registered
        mind.all_cp_registered = mind.cp_all_registered(cp_x, cp_y)



class Opponent(Agent):
    """
    Infos on the opponents
    """
    def __init__(self):
        Agent.__init__(self)


    def get_inputs(self, list_inputs):
        """
        Retrieve game parameters' values to act upon
        """
        list_inputs = [int(i) for i in input().split()]    
        self.x                = list_inputs[0]
        self.y                = list_inputs[1]



class Pod(Agent):
    """
    Infos and functionalities to drive the pod
    """
    def __init__(self, env, x = None, y = None):
        Agent.__init__(self, x, y)
        # *** Actions ***
        # Main
        self.x_target = None
        self.y_target = None
        self.thrust = None
        # Additional
        self._boost_available = True
        
        # *** Infos ***
        # Pod
        self.speed = None
        self.strat = ''
        self.state = ''
        # Env
        self.checkpoint_x = None
        self.checkpoint_y = None
        self.checkpoint_dist = None
        self.checkpoint_angle = None
        # Histories
        # - high level
        self.strat_history = []
        self.state_history = []
        # - low level
        self.thrust_history = []
        self.speed_history = []
        self.checkpoint_history_x = []
        self.checkpoint_history_y = []
        self.checkpoint_dist_history = []
        self.checkpoint_angle_history = []
        
        # *** Mind ***
        self.map_checkpoints_pos = {}
        
        # *** Limits ***
        # Rules
        self._THRUST_LIMITS = (0, 100)
        # Empirical
        self.ANGLE_TOLERANCE_STRAIGHT = range(-45, 45)
        self.ANGLE_TOLERANCE_BOOST = range(-3, 4)
        self._DIST_BOOST_OPTI = 8000
        self.ANGLE_MARGIN = 150
        self.DIST_CHECKPOINT_MARGIN = 4 * env.CHECKPOINT_RAYON
        self.DIST_CHECKPOINT_MARGIN_VERY_FAST = 6 * env.CHECKPOINT_RAYON
        self.MAX_SPPED = 3000
        self.SPEED_MARGIN = .5 * self.MAX_SPPED  # (1500)
        self.SPEED_MARGIN_VERY_FAST = .8 * self.MAX_SPPED  # (2400)

        # *** Other ***
        # Strategies
        self.dic_strats = {
            'full_straight': {
                'name': 'full_straight',
                'option': 'boost'
            },
            'mollo': {
                'name': 'mollo'
            },
            'break_drift': {
                'name': 'break_drift'
            },
            'circle': {
                'name': 'circle'
            }
        }


    def _action(self):
        """
        Execute the strategy by printing direction
        and thrust in the desired format: "x y thrust"
        eg. "6000 1500 100"
        """
        # Set vars
        x = self.x_target
        y = self.y_target
        thrust = self.thrust

        # Execute strat
        print("{x} {y} {thrust}".format(x=x, y=y, thrust=thrust))
        

    def compute_acceleration(self):
        """
        Compute acceleration
        """
        # TODO acc = checkpoint_dist_prev - checkpoint_dist
        acc = None
        
        return acc


    def compute_delta_position(self, size_step = 3, oldest_hist_iter = 0):
        """
        Compute the difference between positions (oldest to most recent):
        x-n, ..., x-2, x-1, x
        y-n, ..., y-2, y-1, y
        """
        # TODO: use [-1:-2:-1] to get last element and [-1:-3:-1] to get last then second last
        # Include current position in a temp hist
        hist_x = self.x_history[-oldest_hist_iter:] + [self.x]
        hist_y = self.y_history[-oldest_hist_iter:] + [self.y]
        # Compute difference (from the oldest - reversed)
        list_delta_x = [t-tn for (t, tn) in zip(hist_x[size_step::size_step], hist_x[::size_step])]
        list_delta_y = [t-tn for (t, tn) in zip(hist_y[size_step::size_step], hist_y[::size_step])]
        
        return list_delta_x, list_delta_y


    def compute_speed(self, env, n_hist = 0):
        """
        1. Assess the overall delta distance
        2. Assess the relative speed

        avg_iter (None or >1): compute average speed on n iters
        """
        # Get deltas
        list_dx, list_dy = self.compute_delta_position()

        print("list_dx", list_dx, file=sys.stderr)
        print("list_dy", list_dy, file=sys.stderr)
        
        # Compute avg deltas (get the last or n last elements)
        avg_dx = abs(sum(list_dx[-1:-(n_hist+2):-1]) / (n_hist + 1))
        avg_dy = abs(sum(list_dy[-1:-(n_hist+2):-1]) / (n_hist + 1))
        
        print("avg_dx", avg_dx, file=sys.stderr)
        print("avg_dy", avg_dy, file=sys.stderr)
        # Compute speed ratio
        
        speed = avg_dx + avg_dy
        print("speed", speed, file=sys.stderr)
        
        return speed


    def evaluate_opti_strat(self):
        """
        Evaluate opti strat based on low level info (pos, speed, etc.)

        return: strat_opti_name, strat_opti_grade
        """
        # Distance from next checkpoint
        print("self.checkpoint_dist", self.checkpoint_dist, file=sys.stderr)
        print("self.checkpoint_dist", self.DIST_CHECKPOINT_MARGIN, file=sys.stderr)



        # Extreme speed + proximity
        #if self.checkpoint_dist < self.DIST_CHECKPOINT_MARGIN_VERY_FAST:
        #if self.speed > SPEED_MARGIN_VERY_FAST:
        #        strat_opti_name = self.dic_strats['break_drift']['name']

        # Far
        elif self.checkpoint_dist >= self.DIST_CHECKPOINT_MARGIN:
            # Away > assess angle
            if self.checkpoint_angle in self.ANGLE_TOLERANCE_STRAIGHT:
                # Aligned > Straight and full power (or boost)
                strat_opti_name = self.dic_strats['full_straight']['name']
            else:
                # Desaxed > straight medium thrust
                strat_opti_name = self.dic_strats['mollo']['name']

        else:
            # Approaching > assess speed:
            print("self.speed", self.speed, file=sys.stderr)
            if self.speed > self.SPEED_MARGIN:
                # Fast > Full thrust in opposite direction (to brake)
                strat_opti_name = self.dic_strats['break_drift']['name']
            else:
                # Slow > straight medium thrust
                strat_opti_name = self.dic_strats['mollo']['name']
        
        # TODO: find clever way to assess grade
        strat_opti_grade = .7
        
        return strat_opti_name, strat_opti_grade


    def get_inputs(self, list_inputs):
        """
        Retrieve game parameters' values to act upon
        """
        list_inputs = [int(i) for i in input().split()]    
        self.x                = list_inputs[0]
        self.y                = list_inputs[1]
        self.checkpoint_x     = list_inputs[2]
        self.checkpoint_y     = list_inputs[3]
        self.checkpoint_dist  = list_inputs[4]
        self.checkpoint_angle = list_inputs[5]


    def strat_circle(self):
        """
        If an equilateral triangle is detected, circle around
        Sets x, y, and thrust
        """
        # Get curr targeted checkpoint name
        cp_name = mind.get_cp_name(self.checkpoint_x, self.checkpoint_y)
        # Get cp prev name
        cp_prev_name, cp_prev_pos = mind.get_cp_prev(cp_name)

        # Get positions
        pod = (self.x, self.y)
        curr_cp = (self.checkpoint_x, self.checkpoint_y)
        semiAB, semiBC, semiAC = mind.assess_optimal_trajectory()
        
        # Get distances btw pod and cp_prev, curr_cp
        dist_pod_prev_cp = mind.get_dist_btw_2points(pod, cp_prev_pos)
        dist_pod_target_cp = mind.get_dist_btw_2points(pod, curr_cp)
        
        # If closer to previosus cp, goto outsemi, else goto next cp
        if cp_name == 1:
            print("cp_name", cp_name, file=sys.stderr)
            print("dist_pod_prev_cp", dist_pod_prev_cp * 2/3, file=sys.stderr)
            print("dist_pod_target_cp", dist_pod_target_cp, file=sys.stderr)
            if dist_pod_prev_cp < dist_pod_target_cp * 2/4:
                print("semi", file=sys.stderr)
                self.x_target = round(semiAC[0])
                self.y_target = round(semiAC[1])
            else:
                print("cp", file=sys.stderr)
                self.x_target = self.checkpoint_x
                self.y_target = self.checkpoint_y
        
        elif cp_name == 2:
            if dist_pod_prev_cp < dist_pod_target_cp * 2/4:
                self.x_target = round(semiAB[0])
                self.y_target = round(semiAB[1])
            else:
                self.x_target = self.checkpoint_x
                self.y_target = self.checkpoint_y
        
        elif cp_name == 3:
            if dist_pod_prev_cp < dist_pod_target_cp *2/4:
                self.x_target = round(semiBC[0])
                self.y_target = round(semiBC[1])
            else:
                self.x_target = self.checkpoint_x
                self.y_target = self.checkpoint_y

        self.thrust = 94 # max(self._THRUST_LIMITS)
        
        self.strat = self.dic_strats['circle']['name']
        

    def strat_full_straight(self, env):
        """
        Set x_target, y_target and thrust: 
        > Full thrust and straight to the next checkpoint
        > (1) Boost: if on the extreme parts of the map and far from checkpoint
        """
        # Direction straight
        self.x_target = self.checkpoint_x
        self.y_target = self.checkpoint_y
        # Thrust
        self.thrust = max(self._THRUST_LIMITS)
        # Boost?
        if self._boost_available:
            # If distance to drive is long enough
            if self.checkpoint_dist > self._DIST_BOOST_OPTI:
                # If the pod is in the right|left most part of the map
                if self.x < 2*env.MAP_WIDTH//10 or self.x > 8*env.MAP_WIDTH//10:
                    # If the angle is 0 toward the checkpoint
                    if self.checkpoint_angle in self.ANGLE_TOLERANCE_BOOST:
                        self.thrust = 'BOOST'
                        self._boost_available = False
                        print('/!\ BOOST /!\ ', file=sys.stderr)
        
        # Store strat infos
        if self.thrust == 'BOOST':
            self.strat = self.dic_strats['full_straight']['name'] + \
                   '-' + self.dic_strats['full_straight']['option']
        else:
            self.strat = self.dic_strats['full_straight']['name']
        

    def strat_launcher(self, strat_name, env):
        """
        Launch a strat
        """
        if strat_name == self.dic_strats['full_straight']['name']:
            self.strat_full_straight(env)
        elif strat_name == self.dic_strats['mollo']['name']:
            self.strat_mollo()
        elif strat_name == self.dic_strats['break_drift']['name']:
            self.strat_break_drift()
        elif strat_name == self.dic_strats['circle']['name']:
            self.strat_circle()
        else:
            raise ValueError("Strategy name not recognized:", strat_name, file=sys.stderr)


    def strat_mollo(self):
        """
        Set x_target, y_target and thrust:
        > Medium/slow thrust and toward next checkpoint
        """
        # Medium thrust
        self.thrust = 60
        # Direction straight
        self.x_target = self.checkpoint_x
        self.y_target = self.checkpoint_y
        
        # Store strat infos
        self.strat = self.dic_strats['mollo']['name']
        

    def strat_break_drift(self, angle = None):
        """
        Set x_target, y_target and thrust:
        > Full thrust in opposite direction
        """
        # Full thrust
        self.thrust = max(self._THRUST_LIMITS)
        
        # Opposite direction (toward prev position)
        self.x_target =  self.x_history[-1]
        self.y_target = self.y_history[-1]
        
        # Store strat infos
        self.strat = self.dic_strats['break_drift']['name']


    def update_history(self):
        """
        Append history with new old values
        """
        # *** Hight level ***
        
        pod.strat_history.append(pod.strat)
        pod.state_history.append(pod.state)
        
        # *** Low level ***
        
        # Position pod
        pod.x_history.append(pod.x)
        pod.y_history.append(pod.y)
        
        # Checkpoint
        pod.checkpoint_history_x.append(pod.checkpoint_x)
        pod.checkpoint_history_y.append(pod.checkpoint_y)
        pod.checkpoint_dist_history.append(pod.checkpoint_dist)
        pod.checkpoint_angle_history.append(pod.checkpoint_angle)
        
        # Thrust
        pod.thrust_history.append(pod.thrust)



def printer_game_info(env, pod, verbose=1):
    """
    Display infos on pod variables (position, target, speed) and 
    current strategy, on the opponent, and other variables of the game
    
    verbose 1:
    - pod mode, pod state
    verbose 2:
    - pod position (curr, prev)
    - checkpoint pos, dist, angle
    """
    # High level infos (states)
    # -------------------------
    
    # Pod mode (strat)
    print("Mode: {mode}".format(mode = pod.strat), file=sys.stderr)

    # Pod state (eg.drifting) TODO
    #print("State: {state}".format(state = pod.state), file=sys.stderr)
    
    # Low level infos (positions)
    # ---------------------------
    if verbose == 1:
        
        # Pod current position
        print("\nPod position:"
              "\ncurr: ({pos_pod_x_cur}, {pos_pod_y_cur})"
              .format(pos_pod_x_cur = pod.x, \
                pos_pod_y_cur = pod.y), \
                file=sys.stderr)
    
        # Pod previous position
        if env.game_iter > 1:
            print("prev: ({pos_pod_x_prev}, {pos_pod_y_prev})"
                  .format(pos_pod_x_prev = pod.x_history[-1], \
                    pos_pod_y_prev = pod.y_history[-1]), \
                    file=sys.stderr)
        
        
    if verbose == 2:
        # Checkpoint position
        print("\nCheckpoint:"
              "\npos: ({pos_checkpoint_x}, {pos_checkpoint_y})"
              "\ndist: {dist_checkpoint}"
              "\nangle: {angle_checkpoint}"
              .format(pos_checkpoint_x = pod.checkpoint_x, \
                pos_checkpoint_y = pod.checkpoint_y, \
                dist_checkpoint = pod.checkpoint_dist, \
                angle_checkpoint = pod.checkpoint_angle), \
                file=sys.stderr)
    
        # Position targeted
        print("\nPosition targeted:"
              "\nx, y", pod.x_target, pod.y_target, \
              file=sys.stderr)
        
        # Opponent position
        # TODO
        


# =================================================================
#                            GAME
# =================================================================


# Init main classes
env = Environment()
pod = Pod(env)
opponent = Opponent()
mind = Mind()


# GAME LOOP
while True:
    # UPDATE VARIABLES
    # ----------------

    # Update game loop count
    env.iter_loop()

    # Append history
    if env.game_iter > 1:
        pod.update_history()

    # Get new inputs
    pod.get_inputs(input)
    opponent.get_inputs(input)

    # Compute dynamic variables
    if env.game_iter > 3:
        pod.speed = pod.compute_speed(env)
        pod.acceleration = pod.compute_acceleration()


    # MIND: MODELIZE GAME
    # -------------------

    # Store checkpoints location
    if not mind.all_cp_registered:
        mind.updt_cp_map(pod.checkpoint_x, pod.checkpoint_y)

    # FIRST TOUR FINISHED: Assess strategies for each checkpoint
    if  mind.all_cp_registered and not mind.strats_assessed:
        # Assess map structure
        mind.cp_assess_map_structure()
        
        # Assess strats
        mind.cp_strats_manager(pod.dic_strats)

    # Asseess state (drifting?)
    mind.assess_state()


    # SELECT STRATEGY
    # ---------------
    
    mind.select_apply_strategy(pod, env)
