"""
File Name: settings.py
Module: src
Function: Store a series of constants and their related values for use throughout the application. Also initializes pygame.
Inputs: Assets from the assets folder to create constant path values.
Outputs: Initialized pygame, mixer. Any constant values that are imported by other areas of the application.
Authors:
    Blake Carlson
    Jack Bauer
    Nifemi Lawal
    Dellie Wright
Creation Date: 9/23/2025

NOTE: All code in the file was authored by 1 or more of the authors. No outside sources were used for code
"""
# Import sound effects class, pygame, and pygame's audio mixer
from sfx import SFX
import pygame 
from pygame import mixer
import os # For file path logic

# define visual asset path variables
# Get the project root directory (one level up from the src directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
NUM_DIR = os.path.join(ASSETS_DIR, "numbers")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")

# Screen setup
try:
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
except: 
    pass

pygame.init()  # start pygame
sfx = SFX(SOUND_DIR)
clock = pygame.time.Clock() # for smooth animation

WIDTH, HEIGHT = 850, 650  # Set height and width of the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # create the screen
pygame.display.set_caption("Minesweeper")  # title the program

# Colors
WHITE = (255, 255, 255)  # define white on the RGB scale
BLACK = (0, 0, 0)  # define black on the RGB scale
BLUE = (0, 0, 255)  # define blue on the RGB scale
GREEN = (0, 200, 0)  # define green on the RGB scale
RED = (200, 0, 0)  # define red on the RGB scale
LIGHT_RED = (220, 60, 60)  # a more readable light red
DARK_RED = (150, 20, 20) # define darker red for mine background
PURPLE = (200, 0, 200) # define purple on the RGB scale
GRAY = (100, 100, 100)  # define grey on the RGB scale
LIGHT_GRAY = (200, 200, 200)  # define light grey on the RGB scale
CONFETTI_COLORS = [(255, 99, 132), (255, 205, 86), (75, 192, 192), (54, 162, 235), (153, 102, 255), (255, 159, 64)] # define colors for win scenario

# Fonts
font = pygame.font.Font(None, 60)  # Bigger font for titles
small_font = pygame.font.Font(None, 36)  # Smaller font for buttons/text
tiny_font = pygame.font.Font(None, 18)  # Tiny font for sfx info

# Game states
MENU = "menu"  # define the menu state
PLAYING = "playing"  # define the playing state
WIN = "win"  # define the winning state
LOSE = "lose"  # define the losing state

# Difficulties
EASY = "easy"
MEDIUM = "medium"
HARD = "hard"

# Mode
AI_INTERACTIVE = "Interactive" # AI and player take turns
AI_AUTOMATIC = "Automatic" # AI plays the entire game
AI_MANUAL = "Manual" # Player only mode (no AI)

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

# Theme system
DARK_THEME = {
    'background': (0, 0, 0),          # BLACK
    'text': (255, 255, 255),          # WHITE  
    'grid_tile': (100, 100, 100),     # GRAY
    'grid_revealed': (200, 200, 200), # LIGHT_GRAY
    'grid_border': (0, 0, 0),         # BLACK
    'button_bg': (100, 100, 100),     # GRAY
    'button_hover': (150, 150, 150),  # Lighter gray
    'notification_bg': (45, 45, 45),  # Dark gray for message boxes
    'notification_border': (255, 255, 255), # WHITE border
}

LIGHT_THEME = {
    'background': (245, 245, 220),    # Beige
    'text': (32, 32, 32),            # Much darker gray for better readability
    'grid_tile': (180, 180, 180),    # Medium gray - more contrast
    'grid_revealed': (255, 255, 255), # Pure white - maximum contrast
    'grid_border': (64, 64, 64),     # Dark gray
    'button_bg': (200, 200, 200),    # Light gray
    'button_hover': (180, 180, 180), # Darker gray
    'light_button_bg': (150, 150, 150), # Lighter gray for better contrast
    'light_button_hover': (130, 130, 130), # Even lighter hover
    'notification_bg': (220, 220, 220), # Light gray for message boxes
    'notification_border': (64, 64, 64), # Dark gray border
}

# Current theme (defaults to dark)
current_theme = DARK_THEME

def switch_theme(theme_name):
    """Switch between dark and light themes"""
    global current_theme
    if theme_name == "dark":
        current_theme = DARK_THEME
    else:
        current_theme = LIGHT_THEME

def get_current_theme():
    """Get the current theme dictionary"""
    return current_theme




