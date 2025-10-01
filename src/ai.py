import random
from settings import EASY, MEDIUM, HARD
class ai_solver():

    def __init__(self, difficulty, grid, revealed, flagged):
        self.difficulty = difficulty
        self.grid = grid
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
        """        
        # Try up to 100 times to find an unrevealed square
        for _ in range(100):
            rand_i = random.randint(0, 9)
            rand_j = random.randint(0, 9)
            # Pick the first unrevealed square
            if not self.revealed[rand_i][rand_j]:
                # If flagged, ignore (main loop handles flags)
                return rand_i, rand_j, "reveal"

        # If no move possible (all revealed), return None
        return None, None, None

        
    def medium_ai_move(self):
        pass

    """
        Medium move pseudocode / logic:

        1: Check for guaranteed safe moves using already revealed squares
        2: If no "guaranteed" safe moves, guess using best odds
            Ex: guessing between 1 in 3 spots is better than guessing between 1 in 2. 

        1:
            How do you guarantee a square is safe?
                Use flags as mine indicators
            Steps:
                Flag corners/archs with 1's
                    Reveal squares around squares that have # of adj flags = adj mines
                Check if # of unrevealed squares surrounding a revealed square = # of adj mines - placed flags

                1-2-1 rule
                X O X
        """  

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