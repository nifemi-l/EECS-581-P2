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
            self.easy_ai_move()
        elif self.difficulty == MEDIUM:
            self.medium_ai_move()
        elif self.difficulty == HARD:
            self.hard_ai_move()
        # If the difficulty for some reason is not easy, medium, or hard, just pass.
            # This should never occur.
        else:
            pass

    def easy_ai_move(self):
        """
        Easy AI purely makes random moves
        Generate a random location on the grid using random values and reveal it.
        """        
        # Randomly generate a location on the grid
        for i in range(10):
            for j in range(10):
                rand_i = random.randint(0,9)
                rand_j = random.randint(0,9)
                # Check if random square is not revealed and is not flagged. If so, its a valid move
                if self.revealed[rand_i][rand_j] == False and self.flagged[rand_i][rand_j] == False:
                    # Make the move and return, ensuring only a single move is made.
                    self.revealed[rand_i][rand_j] = True
                    return

        
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
                    self.revealed[i][j] = True
                    return