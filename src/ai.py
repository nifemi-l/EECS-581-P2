"""
File Name: ai.py
Module: src
Function: Create the ai_solver class and its necessary functions and helper functions to make moves to solve games at 3 different "difficulties"
Inputs: None
Outputs: None
Authors:
    Blake Carlson
    Logan Smith
    Jack Bauer
Creation Date: 9/28/2025

NOTE: All code in the file was authored by 1 or more of the authors. No outside sources were used for code
"""

# Import random and the context for the difficulties from settings
import random
from settings import EASY, MEDIUM, HARD

# Creates the ai_solver class, which each instance is a able to solve minesweeper games on 3 different "difficulty" settings.
class ai_solver():

    def __init__(self, difficulty, grid, counts, revealed, flagged):
        # When an ai_solver object is created, it stores all the info about the current game state.

        # The difficulty the user has selected (EASY, MEDIUM, HARD)
        self.difficulty = difficulty
        # 2D list of the board showing which squares are mined / safe.
        self.grid = grid
        # 2D list of the board showing the adjacent mine counts for each square.
        self.counts = counts
        # 2D list of the board showing which squares have been revealed to the player / ai.
        self.revealed = revealed
        # 2D list of the board showing which squares currently have flags on them, and which ones do not.
        self.flagged = flagged

    def make_move(self):
        # Takes the current board state, and calls the respective ai_move function corresponding to the player selected difficulty.
        if self.difficulty == EASY:
            return self.easy_ai_move()
        elif self.difficulty == MEDIUM:
            return self.medium_ai_move()
        elif self.difficulty == HARD:
            return self.hard_ai_move()
        
        # If the difficulty for some reason is not EASY, MEDIUM, or HARD, just return None, None, None indicating the ai makes no move.
            # This should in theory never occur.
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
        Medium AI actually makes deductions about the current game state to logically reveal squares that it guarantees are safe and flag squares it guarantees are mines.
        It makes random moves as a last resort if it cannot guarantee reveal a square or flag anything.

        NOTE: Flagging a square DOES NOT "take up a turn", so if a flag gets placed, the ai will get multiple consecutive moves. It will continue getting moves until a square is revealed.

        Medium move pseudocode / logic:

        Follow 3 or 4 rules in order:

            1: If the board is entirely covered / no squares have yet to be revealed, no information can be deduced from it.
                Make a random first move to begin the game. It should always be safe.

            2: If # of flagged neighbors of a revealed cell equals that cell's number, AI should reveal all the other squares.
                Ex: A cell shows 2. It has 2 neighbors flagged and 4 unrevealed neighbors, reveal all them since 2 showing = 2 flagged

            3: If a revealed cell has same number of hidden neighbors as its number, flag all hidden neighbors.
                Ex: A 3 is shown and only had 3 unrevealed adjacent squares. Means they all should be mines, flag them.
            
            4: If none of the following rules can be used, the best option is a random reveal
                It says randomly reveal an unrevealed square
                    However, I want to attempt to optimize for revealing squares with lowest adjacent counts first.
                        Ex: Randomly make a guess for a square that has 1 neighboring mine over a square with 3.

        NOTE: Returned value is tuple with cell location and flag / reveal. 
            So for stuff like "flag all adjacent cells" it must systematically check all and pick first occurance (so next run gets others).
        """

        # Step 1: If no squares are revealed, that means the ai must make the first move. It makes the first move randomly.

        is_new_board = self.is_first_move()
        if is_new_board:
            self.rand_reveal()

        # Step 2: Check if adj_eq_flags returns anything, if so return that square and action.

        to_reveal = self.adj_eq_flags()
        if (to_reveal != (None, None, None)):
            return to_reveal

        # Step 3: Check if hidden_hidden_neighbor_eq_num returns anything, if so return that square and action.

        to_flag = self.hidden_neighbor_eq_num()
        if (to_flag != (None, None, None)):
            return to_flag

        # Step 4: Randomly choose a revealed square to reveal an adjacent unrevealed square to. Prioritizes squares with lowest numbers of adjacent mines.
        
        random_reveal = self.rand_reveal()
        if (random_reveal != (None, None, None)):
            return random_reveal
        
        # "Step 5": Should never occur, but if it does, return None, None, None to show no move is made.
        return None, None, None

    def hard_ai_move(self):
        # Hard AI cheats by iterating through all the squares on the board, revealing the first found square that is not revealed and does not have a mine.
        for i in range(10):
            for j in range(10):
                # If the next cell that is not revealed does not have a mine on it, reveal it.
                if self.grid[i][j] == 0 and self.revealed[i][j] == False:
                    # If this cell happens to be flagged (even though it has no mine), remove the flag before revealing it.
                    if self.flagged[i][j] == True:
                        self.flagged[i][j] = False
                    # Returns the coordinates the cell and reveal indicating it should be revealed.
                    return i, j, "reveal"
    
    """
    Helper functions for each step of medium_ai_move. Should make each step more readable and compact.
        Steps 1 and 4 | rand_reveal : Reveals an unrevealed cell randomly.
        Step 2        | hidden_neighbor_eq_num : Checks for squares with the same number of hidden neighbors and adjacent mines, then flag them
        Step 3        | adj_eq_flags : Checks for squares where # of adjacent mines = # of adjacent flags, reveal the rest
    """

    """ 
    hidden_neighbor_eq_num checks for squares that have the same number of adjacent hidden squares as the number of adjacent squares with mines.
        If those match up, that means all the remaining currently hidden squares must have a mine, and can safely be flagged.

        Ex: Here is a sample 3x3 situation where this occurs, with empty brackets indicating the square has not been revealed yet
            [0] [0] [1]
            [0] [1] [2]
            [1] [1] [ ]
        When the one in the middle is checked, it knows 1 adjacent square must have a mine, but all the squares around it except for the bottom right have been revealed and do not have mines
        So, it determines that the hidden square on the bottom right must have a mine and flags it.
    """
    def hidden_neighbor_eq_num(self):
        # Iterates through all the squares on the board.
        for i in range(10):
            for j in range(10):
                # Only checks squares that have already been revealed.
                if self.revealed[i][j] == True:
                    # Retrieves the amount of squares to the current square are hidden (and not flagged), how many are flagged, and how many adjacent squares have mines.
                    hidden_adj_count = self.adj_hidden_squares(i, j)
                    flagged_adj_count = self.adj_flagged_squares(i, j)
                    count = self.counts[i][j]
                    # If the number of mines in the adjacent squares is equal to the amount that are unrevealed and not flagged, that means all the others should be safe to flag.
                    if (hidden_adj_count > 0) and (hidden_adj_count + flagged_adj_count) == count:
                        # Finds one of the squares that is adjacent and hidden, but not flagged and returns its coordinates with the action "flag", indicating the square should be flagged.
                        action_i, action_j = self.find_next_adj_hidden(i, j)
                        if action_i is not None:
                            return action_i, action_j, "flag"
        # If the entire board has no squares that are guaranteed safe to be flagged, it returns None, None, None, telling the solver to advance to the next step.
        return None, None, None

    """
    adj_eq_flags checks for squares that have the same number of adjacent squares with mines as adjacent squares that are flagged.
        If those match up, that means all the other adjacent squares must be safe to reveal (assuming the flags were correctly placed)

        Ex: Here is a sample 3x3 section where this occurs, empty brackets indicating unrevealed squares.
            [ ] [2] [0]
            [ ] [2] [1]
            [1] [1] [1]
        When the square in the middle is checked, it sees that there are 2 unrevealed and unflagged adjacent squares. It also sees that its # of adjacent squares with mines is 2.
        This means both those squares are safe to be flagged.
        So it will then find and return the coordinates for one of these squares with the action "flag" indicating the square can be safely flagged.
    """
    def adj_eq_flags(self):
        # Iterates through all the squares on the board.
        for i in range(10):
            for j in range(10):
                # Only checks squares that have already been revealed.
                if self.revealed[i][j] == True:
                    # Retrieves the amount of squares to the current square are hidden (and not flagged), how many are flagged, and how many adjacent squares have mines.
                    hidden_adj_count = self.adj_hidden_squares(i, j)
                    flagged_adj_count = self.adj_flagged_squares(i, j)
                    count = self.counts[i][j]
                    # If there is at least 1 unrevealed and unflagged square, and the # of adjacent squares with mines equals the # of adjacent squares that are flagged, all the hidden squares can be safely revealed.
                    if hidden_adj_count > 0 and flagged_adj_count == count:
                        # Finds an adjacent square that is hidden and not flagged, and returns its coordinates with the action reveal, indicating the square can be revealed.
                        action_i, action_j = self.find_next_adj_hidden(i, j)
                        if action_i is not None:
                            return action_i, action_j, "reveal"
        # If the entire board has no squares that are guaranteed safe to be revealed, it returns None, None, None, telling the solver to advance to the next step.
        return None, None, None

    # Rand_reveal randomly reveals a square on the board that is both not revealed and is not flagged. Used either to start the game or as a last resort when no other move can be performed safely.
    def rand_reveal(self):
        # Add all unrevealed and unflagged squares on the board into a "candidate list".
        candidate_squares = []
        for i in range(10):
            for j in range(10):
                if self.revealed[i][j] == False and self.flagged[i][j] == False:
                    candidate_squares.append((i, j))
        
        # Randomly selects a square from the candidate list and reveals it.
            # Subtract 1 from length since randint includes the upper endpoint.
        options = len(candidate_squares) - 1
        rand_option = random.randint(0, options)
        # Extracts the i and j positions from the randomly selected option.
        rand_i, rand_j = candidate_squares[rand_option]
        # Returns the coordinates of the chosen square and the action to reveal it.
        return rand_i, rand_j, "reveal"   

    """
    Some helper functions for the helper functions
    """
    # Helper function that takes in the coordinates of a particular square, and returns the number of adjacent squares to itself that are both hidden and not flagged. 
    def adj_hidden_squares(self, i, j):
        # Initializes the adjacent flag count wtih 0.
        count = 0
        # Creates 2 lists which all combinations will be added to the coordinates given to the function to check its (up to) 8 adjacent square.
        for adj_i in [-1, 0, 1]:
            for adj_j in [-1, 0, 1]:
                # Makes sure the square being checked itself is not included in the count of flagged squares.
                if (adj_i != 0 or adj_j != 0):
                    temp_i = i + adj_i
                    temp_j = j + adj_j
                    # Check if temp_row and temp_col are valid grid coordinates.
                    # If it is a valid square that is both hidden and not flagged, increase the current count by 1.
                    if ((0 <= temp_i < 10) and (0 <= temp_j < 10)):
                        if self.revealed[temp_i][temp_j] == False and self.flagged[temp_i][temp_j] == False:
                            count += 1
        # After checking all the adjacent squares, returns the final count of adjacent squares that are both hidden and not flagged.
        return count
    
    # Helper function that takes in the coordinates of a particular square, and returns the number of adjacent squares to itself that are flagged. 
    def adj_flagged_squares(self, i, j):
        # Initializes the adjacent flag count wtih 0.
        count = 0
        # Creates 2 lists which all combinations will be added to the coordinates given to the function to check its (up to) 8 adjacent square.
        for adj_i in [-1, 0, 1]:
            for adj_j in [-1, 0, 1]:
            # Makes sure the square being checked itself is not included in the count of flagged squares.
                if (adj_i != 0 or adj_j != 0):
                    temp_i = i + adj_i
                    temp_j = j + adj_j
                    # Check if temp_row and temp_col are valid grid coordinates.
                    # If it is a valid square and is flagged, increase the current count by 1.
                    if ((0 <= temp_i < 10) and (0 <= temp_j < 10)):
                        if self.flagged[temp_i][temp_j] == True:
                            count += 1
        # After checking all the adjacent squares, returns the final count of adjacent squares that are flagged.
        return count
    
    # Helper function that takes in the coordinates of a particular square and returns the coordinates of the first found square adjacent to it that is unrevealed and not flagged.
    # If no squares around the current cell are unrevealed and without a flag, returns None, None.
    def find_next_adj_hidden(self, i, j):
        # Creates 2 lists which all combinations will be added to the coordinates given to the function to check its (up to) 8 adjacent square.
        for adj_i in [-1, 0, 1]:
            for adj_j in [-1, 0, 1]:
                # Makes sure the square being checked itself is not being considered as the next adjacent hidden square.
                if (adj_i != 0 or adj_j != 0):
                    temp_i = i + adj_i
                    temp_j = j + adj_j
                    # Check if temp_row and temp_col are valid grid coordinates.
                    # If it is a valid square and is not flagged and not revealed, return the coordinates of the square.
                    if 0 <= temp_i < 10 and 0 <= temp_j < 10:
                        if (self.revealed[temp_i][temp_j] == False) and (self.flagged[temp_i][temp_j] == False):
                            return temp_i, temp_j
        # If the current square has no adjacent squares that are not revealed and not flagged, return None, None.
        return None, None
    

    # Helper function that takes in the coordinates of a particular square and returns the coordinates of the first found square adjacent to it that is flagged.
    # If no squares around the current cell are flagged, returns None, None.
        # The same thing as find_next_adj_hidden() but instead returns the first adjacent cell found that is flagged.
    def find_next_adj_flagged(self, i, j):
        # Creates 2 lists which all combinations will be added to the coordinates given to the function to check its (up to) 8 adjacent square.
        for adj_i in [-1, 0, 1]:
            for adj_j in [-1, 0, 1]:
                # Makes sure the square being checked itself is not being considered as the next adjacent hidden square.
                if (adj_i != 0 or adj_j != 0):
                    temp_i = i + adj_i
                    temp_j = j + adj_j
                    # Check if temp_row and temp_col are valid grid coordinates.
                    # If it is a valid square and is flagged, return the coordinates of the square.
                    if ((0 <= temp_i < 10) and (0 <= temp_j < 10)):
                        if self.flagged[temp_i][temp_j] == True:
                            return temp_i, temp_j
        # If none of the current squares adjacent square are flagged, return None, None.
        return None, None

    # Checks if the board if completely unrevealed so the AI would be making the first move of the game.
    # Returns a boolean corresponding to whether its making the first move or not.
    def is_first_move(self):
        for i in range(10):
            for j in range(10):
                if self.revealed[i][j] == True:
                    return False
        return True