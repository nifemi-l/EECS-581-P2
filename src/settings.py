
import pygame 
from pygame import mixer
import os 

# Screen setup
pygame.init()  # start pygame
clock = pygame.time.Clock() # for smooth animation

WIDTH, HEIGHT = 800, 600  # seight height and width of the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # create the screen
pygame.display.set_caption("Minesweeper")  # title the program

# Colors
WHITE = (255, 255, 255)  # define white on the RGB scale
BLACK = (0, 0, 0)  # define black on the RGB scale
BLUE = (0, 0, 255)  # define blue on the RGB scale
GREEN = (0, 200, 0)  # define green on the RGB scale
RED = (200, 0, 0)  # define red on the RGB scale
DARK_RED = (150, 20, 20) # define darker red for mine background
PURPLE = (200, 0, 200) # define purple on the RGB scale
GRAY = (100, 100, 100)  # define grey on the RGB scale
LIGHT_GRAY = (200, 200, 200)  # define light grey on the RGB scale
CONFETTI_COLORS = [(255, 99, 132), (255, 205, 86), (75, 192, 192), (54, 162, 235), (153, 102, 255), (255, 159, 64)] # define colors for win scenario

# Fonts
font = pygame.font.Font(None, 60)  # Bigger font for titles
small_font = pygame.font.Font(None, 36)  # Smaller font for buttons/text

# Game states
MENU = "menu"  # define the menu state
PLAYING = "playing"  # define the playing state
WIN = "win"  # define the winning state
LOSE = "lose"  # define the losing state

# Difficulties
EASY = "easy"
MEDIUM = "medium"
HARD = "hard"

# grid settings
GRID_SIZE = 10  # set each blank space between squares to be 10 pixels
TILE_SIZE = 40  # set each square to be 40 pixels
GRID_START_X = (WIDTH - GRID_SIZE * TILE_SIZE) // 2  # calucate the middle of the board so that the board is centred
GRID_START_Y = 100  # place the top of the board slightly from the top

MINE = 3  # define mine as 3 (the value of an array should be 3 when a mine is placed there)
DIRS8 = [(-1, -1), (-1, 0), (-1, 1),
         # create a matrix to easily be able to refference the adjactent tiles for recusive uncovering.
         (0, -1), (0, 1),
         (1, -1), (1, 0), (1, 1)]

CONFETTI_TARGET = 180 # Set number of particles to generation



# define visual asset path variables
# Get the project root directory (one level up from the src directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
NUM_DIR = os.path.join(ASSETS_DIR, "numbers")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")

