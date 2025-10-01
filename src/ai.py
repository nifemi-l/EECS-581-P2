import random
from settings import EASY, MEDIUM, HARD
class ai_solver():

    def __init__(self, difficulty, grid, counts, revealed, flagged):
        self.difficulty = difficulty
        self.grid = grid
        self.counts = counts
        self.revealed = revealed
        self.flagged = flagged

    def make_move(self):
        # Call the respective ai_move function depending on the difficulty the player selected.

        if self.difficulty == EASY:
            return self.easy_ai_move()
        elif self.difficulty == MEDIUM:
            return self.medium_ai_move()
        elif self.difficulty == HARD:
            return self.hard_ai_move()
        # If the difficulty for some reason is not easy, medium, or hard, just pass.
            # This should never occur.
        else:
            return None, None, None

    def easy_ai_move(self):
        """
        Easy AI purely makes random moves.
        Generate a random location on the grid using random values and return it as a reveal action.

        Uses the rand_reveal function to randomly reveal a square.
        """        
        return self.rand_reveal()



        
    def medium_ai_move(self):
        """
        Medium move pseudocode / logic:

        Follow 3 or 4 rules in order:
            1: If a revealed cell has same number of hidden neighbors as its number, flag all hidden neighbors.
                Ex: A 3 is shown and only had 3 unrevealed adjacent squares. Means they all should be mines, flag them.
            2: If # of flagged neighbors of a revealed cell equals that cell's number, AI should reveal all the other squares.
                Ex: A cell shows 2. It has 2 neighbors flagged and 4 unrevealed neighbors, reveal all them since 2 showing = 2 flagged
            3: Use the 1-2-1 pattern rule. If 3 consecutive adjacent cells show 1-2-1, the two outer neighbors are mines, the inner is safe.
                So Flag the outer squares, reveal the inner squares
                Ex: Board shows
                        1 - 2 - 1 (# Of Adj Mines)
                    Values are:
                        M - S - M (M = Mine, S = Safe)
            4: If none of the following rules can be used, the best option is a random reveal
                It says randomly reveal an unrevealed square
                    However, I want to attempt to optimize for revealing squares with lowest adjacent counts first.
                        Ex: Randomly make a guess for a square that has 1 neighboring mine over a square with 3.

            NOTE: Returned value is tuple with cell location and flag / reveal. 
                So for stuff like "flag all adjacent cells" it must systematically check all and pick first occurance (so next run gets others).
        """
        # Step 0: If board has every square unrevealed / no moves have been made
        is_new_board = self.is_first_move()
        if is_new_board:
            print("step 0")
            return self.rand_reveal()


        # NOTE: Swapping step 1 and step 2 tends to perform better, more testing is needed.

        # Step 2: Check if adj_eq_flags returns anything, if so return that square and action.
        to_flag = self.adj_eq_flags()
        if (to_flag != (None, None, None)):
            return to_flag

        # Step 1: Check if hidden_hidden_neighbor_eq_num returns anything, if so return that square and action.
        
        to_reveal = self.hidden_neighbor_eq_num()
        if (to_reveal != (None, None, None)):
            return to_reveal

        

        
        
        """
        # Step 3: Look for 1-2-1 patterns, and find a square to reveal or flag (some might already be revealed / flagged) if so, return the square and action.
        found_1_2_1 = self.find_1_2_1()
        if (found_1_2_1 != None):
            return found_1_2_1
        """
        # Step 4: Randomly choose a revealed square to reveal an adjacent unrevealed square to. Prioritizes squares with lowest numbers of adjacent mines.
        print("made to rand reveal")
        random_reveal = self.rand_reveal()
        if (random_reveal != (None, None, None)):
            return random_reveal
        
        # Step 5: Should never occur, but if it does, return None.
        return None, None, None



    def hard_ai_move(self):
        # Hard AI cheats by iterating through all the squares on the board, revealing the first found square that is not revealed and does not have a mine.
        for i in range(10):
            for j in range(10):
                # If the next cell that is not revealed does not have a mine on it, reveal it.
                if self.grid[i][j] == 0 and self.revealed[i][j] == False:
                    # If this cell happens to be flagged (even though it has no mine), remove the flag.
                    if self.flagged[i][j] == True:
                        self.flagged[i][j] = False
                    # Reveal the cell and returns to finish the function so only 1 move is made.
                    return i, j, "reveal"
    

    """
    Helper functions for each step of medium_ai_move. Should make each step more readable and compact.
        Step 1 | hidden_neighbor_eq_num : Checks for squares with the same number of hidden neighbors and adjacent mines, then flag them
        Step 2 | adj_eq_flags : Checks for squares where # of adjacent mines = # of adjacent flags, reveal the rest
        Step 3 | find_1_2_1 : Looks for the pattern of consequtive squares with values 1_2_1, which means the squares directly next to the ones are mines.
        Step 4 | rand_reveal : Reveals an unrevealed cell randomly, prioritizing squares with lower adjacent mine counts.
    """


    def hidden_neighbor_eq_num(self):
        for i in range(10):
            for j in range(10):
                if self.revealed[i][j] == True:
                    hidden_adj_count = self.adj_hidden_squares(i, j)
                    flagged_adj_count = self.adj_flagged_squares(i, j)
                    count = self.counts[i][j]

                    if (hidden_adj_count > 0) and (hidden_adj_count + flagged_adj_count) == count:
                        action_i, action_j = self.find_next_adj_hidden(i, j)
                        if action_i is not None:
                            return action_i, action_j, "flag"
        return None, None, None
                

    def adj_eq_flags(self):
        for i in range(10):
            for j in range(10):
                if self.revealed[i][j] == True:
                    hidden_adj_count = self.adj_hidden_squares(i, j)
                    flagged_adj_count = self.adj_flagged_squares(i, j)
                    count = self.counts[i][j]

                    if hidden_adj_count > 0 and flagged_adj_count == count:
                        action_i, action_j = self.find_next_adj_hidden(i, j)
                        if action_i is not None:
                            return action_i, action_j, "reveal"
        return None, None, None
    
    

    def rand_reveal(self):
        for num in range(100):
            rand_i = random.randint(0, 9)
            rand_j = random.randint(0, 9)
            if not self.revealed[rand_i][rand_j]:
                # If flagged, ignore (main loop handles flags)
                return rand_i, rand_j, "reveal"
        return None, None, None

    """
    Some helper functions for the helper functions
    """
    # Count adj squares that are hidden
    def adj_hidden_squares(self, i, j):
        count = 0
        for adj_i in [-1, 0, 1]:
            for adj_j in [-1, 0, 1]:
                if (adj_i != 0 or adj_j != 0):
                    temp_i = i + adj_i
                    temp_j = j + adj_j
                    if ((0 <= temp_i < 10) and (0 <= temp_j < 10)):
                        if self.revealed[temp_i][temp_j] == False and self.flagged[temp_i][temp_j] == False:
                            count += 1
        return count
    
    # Count adj squares that have a flag
    def adj_flagged_squares(self, i, j):
        count = 0
        for adj_i in [-1, 0, 1]:
            for adj_j in [-1, 0, 1]:
            # Check to make sure not adjusting the count of where the mine is
                if (adj_i != 0 or adj_j != 0):
                    temp_i = i + adj_i
                    temp_j = j + adj_j
                    # Check if temp_row and temp_col are in bounds. If so, recursively reveal
                    if ((0 <= temp_i < 10) and (0 <= temp_j < 10)):
                        if self.flagged[temp_i][temp_j] == True:
                            count += 1
        return count
    
    def find_next_adj_hidden(self, i, j):
        for adj_i in [-1, 0, 1]:
            for adj_j in [-1, 0, 1]:
                if adj_i != 0 or adj_j != 0:
                    temp_i = i + adj_i
                    temp_j = j + adj_j
                    if 0 <= temp_i < 10 and 0 <= temp_j < 10:
                        if (self.revealed[temp_i][temp_j] == False) and (self.flagged[temp_i][temp_j] == False):
                            return temp_i, temp_j
        return None, None
    

    def find_next_adj_flagged(self, i, j):
        for adj_i in [-1, 0, 1]:
            for adj_j in [-1, 0, 1]:
                if (adj_i != 0 or adj_j != 0):
                    temp_i = i + adj_i
                    temp_j = j + adj_j
                    if ((0 <= temp_i < 10) and (0 <= temp_j < 10)):
                        if self.flagged[temp_i][temp_j] == True:
                            return temp_i, temp_j
        return None, None
    


    def is_first_move(self):
        for i in range(10):
            for j in range(10):
                if self.revealed[i][j] == True:
                    return False
        return True
    

    """
    def find_1_2_1(self):
        pass
    """

    """
    def vert_1_2_1(self, i, j):
        pass

    def horiz_1_2_1(self, i, j):
    """

    