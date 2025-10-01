from random import random
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

        """
        # Medium and hard are not complete.

        elif self.difficulty == MEDIUM:
            self.medium_ai_move()

        elif self.difficulty == HARD:
            self.hard_ai_move()
        """
        # If the difficulty for some reason is not easy, medium, or hard, just pass.
            # This should never occur.
        
        """
        else:
            pass
        """
        
    def easy_ai_move(self):
        
        """
        Easy AI purely makes random moves

        Generate a random location on the grid using random values and reveal it.
        """

        # Use a bool to keep track if a valid move has been made.
            # For example, if it randomly selects a square that has been revealed, it should randomly choose a new square and try again.
        made_move = False

        # Until the ai reveals a square, keep randomly selecting squares til it reveals one and makes a move.
        while made_move == False:
            # Randomly generate 
            for i in range(10):
                for j in range(10):
                    rand_i = random.randint(1,10)
                    rand_j = random.randint(1,10)

                    # Make move with random grid location.
                        # If random square is not revealed, remove flag if it has one, and reveal it.
                    if self.revealed[rand_i][rand_j] == False:
                        if self.flagged[rand_i][rand_j] == True:
                            self.flagged[rand_i][rand_j] = False
                        self.revealed[rand_i][rand_j] = True
                        made_move = True
        

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
        
        

    def hard_ai_move(self):
        
        If difficulty_setting = hard
            The AI will be able to "cheat" and will make moves to eventually reveal the entire board.
            Is essentially all knowing

            
        for i in range(10):
            for j in range(10):
                if grid[i][j] == 0 and revealed[i][j] == False: # and flagged == False? Should still reveal everything if a flagged square happens to be safe right?
                    revealed[i][j] = True
        
    """