import sys
import math
import numpy as np

# 15x15
# 9 sectors 5x5, top left 1
# N, E, S, W directions only
# Goto cells not visited only (by myself)
# Multiple attacks: 
# > torpedo:
# - charges 3 | distance 4
# - damage 2 on target cell, 1 next (even diagonal), even myself, not through islands



class Env:
    """
    Class for map infos
    """
    def __init__(self):
        self.height = None
        self.width = None
        self.player_first = None
        self.grid = None
        
        # History
        self.positions = None
        

    def init_history(self):
        self.positions = pd.DataFrame(columns = ['x', 'y'])


    def read_input(self, input):
        """ Set attributes with game inputs """
        
        # Set grid size and first player
        input_1 = [int(i) for i in input().split()]
        
        self.width = input_1[0]
        self.height = input_1[1]
        self.player_first = input_1[2]
        
        # Collect input grid composition (islands and sea)
        input_grid = []
        for h in range(self.height):
            input_grid.append(list(input()))

        # Make bool array from the list of lists
        # True means island, False otherwise (*1 to get numbers)
        self.grid = (np.array(input_grid) == 'x') * 1
    

    def init_position(self):
        """
        Define the initial position randomly based on empty grid space
        """
        # List indexes of empty positions
        empty_positions = np.where(self.grid.flatten() == 1)[0]
        # Choose 1 index randomly
        init_idx = np.random.choice(empty_positions)
        # Translate into x,y positions
        x, y = np.unravel_index(init_idx, self.grid.shape)
        print("{} {}".format(x, y))


    def append_history(self):
        """
        Append history with previous values
        """
        self.positions.append({'x': self.x, 'y': self.y})


if __name__ == '__main__':
            
    # Init env grid
    env = Env()
    env.read_input(input)
    env.init_position()

    
    # game loop
    while True:
        x, y, my_life, opp_life, torpedo_cooldown, sonar_cooldown, silence_cooldown, mine_cooldown = [int(i) for i in input().split()]
        sonar_result = input()
        opponent_orders = input()
    
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
    
        print("MOVE N TORPEDO")
    
        