import pygame

class GameTimer:
    def __init__(self):
        # Set the start time to 0
        self.start_time = 0
        # Set the running flag to False
        self.running = False
        # Set the final time to 0
        self.final_time = 0

    def start(self):
        # Get the current time and set it as the start time
        self.start_time = pygame.time.get_ticks()
        # Set the running flag to True 
        self.running = True
        # Reset the final time to 0 when starting
        self.final_time = 0
    
    def stop(self):
        # Only stop the timer if it is running
        if self.running:
            # Set the final time using the current time
            self.final_time = pygame.time.get_ticks() - self.start_time
        # Set the running flag to False
        self.running = False

    def format_time(self, raw_time):
        # Format the time into minutes and seconds
        '''Logic:
        # - 60000 milliseconds = 1 minute, so integer div gives the number of full minutes
        # - The remainder (raw_time % 60000) is the leftover milliseconds after minutes
        # - Remainder is then divided by 1000 to get the number of seconds
        '''
        # Calculate the number of minutes
        minutes = raw_time // 60000
        # Calculate the number of seconds
        seconds = (raw_time % 60000) // 1000
        # Return the time in the format of minutes:seconds
        return f"{minutes:02d}:{seconds:02d}"
        
    def get_elapsed_time(self):
        if self.running:
            # Calculate the elapsed time
            elapsed_time = pygame.time.get_ticks() - self.start_time
        else:
            # Use the final time
            elapsed_time = self.final_time
        # Format the time
        formatted_time = self.format_time(elapsed_time)
        # Return the formatted time
        return formatted_time

    def get_elapsed_time_seconds(self):
        # Get elapsed time in seconds as an integer for score calculation
        if self.running:
            # Get the elapsed time in milliseconds
            elapsed_time = pygame.time.get_ticks() - self.start_time
        else:
            # Use the final time
            elapsed_time = self.final_time
        return elapsed_time // 1000  # Convert milliseconds to seconds

    def reset(self):
        # Reset the start time
        self.start_time = 0
        # Reset the running flag
        self.running = False
        # Reset the final time
        self.final_time = 0