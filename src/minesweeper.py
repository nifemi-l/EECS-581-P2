# Filename: Minesweeper.py
# Module: src
# Function: Run the "Minesweeper" game and its main loop.
# Primary functions include the following:
#   get grid pos funtion: used to figure out where a mouse click coresponds to which square in teh 2d array strucutre
#   draw grid fuinction: used to draw the grid and the items in it
#   get_remaining_flags func: used to calaculate and display how many mines are left if the user has been correct in flag placement
#   Others: See their respective declarations, definitions, and documentation for further detail. They are not intended for use outside of this file.
# The program takes in mouse clicks from the user as input and outputs the current state of the minsweeper board
# No external code was used (no Chat GPT or stack overflow)
# Created by Nevan Snider on Sept 3rd, with contributions from Evan Rogerson, Spencer Rodenberg, Kyle Whitmer, and Karsten Wolter
# With additions and edits by: Blake Carlson, Nifemi Lawal, Logan Smith, Jack Bauer, Dellie Wright

import pygame  # import pygame, the main GUI we used in order to create images and track mouse clicks.
import random  # import random to randomly pick mine locations
import os # Access visual asset path
from collections import deque  # Queue for flood-fill
from button import Button
from game_assets import flag_sprite, mines_sprite, numbers_sprites, load_circular_profile
from auth import AuthContext  # simple local auth (token/user.json)
from pfp_helper import save_profile_image  # copy chosen image to assets
from game_timer import GameTimer # Track game time
from ai import ai_solver
from time import sleep

from settings import (
    clock, screen, WIDTH, HEIGHT, sfx, 
    WHITE, BLACK, GREEN, RED, LIGHT_RED, DARK_RED, PURPLE, GRAY, LIGHT_GRAY, CONFETTI_COLORS, BLUE,
    font, small_font, tiny_font,
    MENU, PLAYING, WIN, LOSE,
    GRID_SIZE, TILE_SIZE, GRID_START_X, GRID_START_Y,
    MINE, DIRS8, CONFETTI_TARGET, ASSETS_DIR,
    EASY, MEDIUM, HARD,
    AI_INTERACTIVE, AI_AUTOMATIC, AI_MANUAL,
    current_theme, switch_theme, get_current_theme
)

state = MENU  # start in the main menu
counter_value = 10  # adjustable number in main menu
difficulty = MEDIUM # default to medium
mode = AI_INTERACTIVE # default to interactive mode

# declare ai (defualt none)
ai = None

# declare turn order
player_turn = True

# global confetti list
confetti = []

# initialize the game timer 
game_time = GameTimer()

# High score notification variables
show_high_score_notification = False  # Flag to show the notification
notification_start_time = 0  # When the notification started
NOTIFICATION_DURATION = 3.0  # How long to show notification in seconds

# Load the auth context to manage token/username/pfp
auth = AuthContext()

PROFILE_DIAMETER = 56  # profile picture diameter
PROFILE_MARGIN = 65    # margin from edge
PROFILE_TOP_MARGIN = 10  # margin from top edge

def resolve_profile_path():  # Pick user pfp if logged in, else guest
    # Check if the user is logged in
    if auth.is_logged_in():
        # Try to get the user's profile picture path, or use an empty string if not set
        p = auth.get_pfp_path() or ""
        # If a path exists and the file exists on disk, return it
        if p and os.path.exists(p):
            return p
    # If not logged in or no valid pfp, return the default profile image path
    return os.path.join(ASSETS_DIR, "images", "default_profile.jpg")

# Load the initial avatar surface using the resolved profile path and the wanted diameter
profile_surface = load_circular_profile(resolve_profile_path(), PROFILE_DIAMETER)  # Load initial avatar

# Buffer to hold the username input during signup
signup_input = ""  # Username buffer during signup

# Buffer to hold the path input during set profile picture
setpfp_input = ""  # path buffer during set pfp
setpfp_error = ""  # Error message when set pfp path is invalid

# Buttons for the main menu (shown conditionally by login state)
start_button = Button(WIDTH // 2 - 100, 170, 200, 60, "Start Game", GREEN, (0, 255, 0))  # Start
settings_button = Button(WIDTH // 2 - 100, 240, 200, 60, "Settings", PURPLE, (255, 0, 255)) # Settings
easy_button = Button(WIDTH // 2 - 100, 240, 200, 60, "Easy", GREEN, (0, 255, 0)) # Difficulty menu: easy
medium_button = Button(WIDTH // 2 - 100, 310, 200, 60, "Medium", (160, 160, 0), (210, 210, 40)) # Difficulty menu: medium
hard_button = Button(WIDTH // 2 - 100, 380, 200, 60, "Hard", RED, (255, 0, 0)) # Difficulty menu: hard
mode_interactive_button = Button(WIDTH // 2 - 100, 420, 200, 60, "Interactive", (0, 200, 200), (0, 255, 255)) # Mode menu: interactive
mode_automatic_button = Button(WIDTH // 2 - 100, 490, 200, 60, "Automatic", (0, 0, 200), (0, 0, 255)) # Mode menu: automatic
mode_manual_button = Button(WIDTH // 2 - 100, 560, 200, 60, "Manual", (200, 0, 200), (255, 0, 255)) # Mode menu: manual
settings_continue_button = Button(WIDTH // 2 - 100, 560, 200, 60, "Continue", GRAY, (150, 150, 150)) # Mode menu: manual
sign_in_create_button = Button(WIDTH // 2 - 100, 310, 200, 60, "Sign In / Create", BLUE, (32, 96, 255))  # Sign in or create
change_pfp_button = Button(WIDTH // 2 - 100, 310, 200, 60, "Change PFP", GRAY, (150, 150, 150))  # set pfp
logout_button = Button(WIDTH // 2 - 100, 380, 200, 60, "Logout", RED, (255, 0, 0))  # Logout
quit_button = Button(WIDTH // 2 - 100, 450, 200, 60, "Quit", RED, (255, 0, 0))  # Quit
plus_button = Button(WIDTH // 2 + 60, 550, 60, 60, "+", GRAY, (150, 150, 150))  # Inc bombs
minus_button = Button(WIDTH // 2 - 120, 550, 60, 60, "-", GRAY, (150, 150, 150))  # Dec bombs
mute_button = Button(WIDTH - 120, HEIGHT - 260 , 100, 40 , "Mute", GRAY, (150, 150, 150)) # Mode menu: manual
skip_button = Button(WIDTH - 500, HEIGHT - 260 , 100, 40 , "Skip", GRAY, (150, 150, 150)) # Mode menu: manual

# Theme toggle buttons
dark_mode_button = Button(WIDTH // 2 - 110, 420, 100, 50, "Dark", GRAY, (150, 150, 150))  # Dark mode button
light_mode_button = Button(WIDTH // 2 + 10, 420, 100, 50, "Light", GRAY, (150, 150, 150))  # Light mode button

def load_user_theme():
    """Load the user's theme preference and switch to it"""
    theme_pref = auth.get_theme_preference()
    switch_theme(theme_pref)
    update_theme_button_styles()

def update_theme_button_styles():
    """Update theme button colors based on current theme"""
    theme = get_current_theme()
    if theme['background'] == (0, 0, 0):  # Dark theme active
        dark_mode_button.color = GREEN
        dark_mode_button.hover_color = (0, 255, 0)
        light_mode_button.color = GRAY
        light_mode_button.hover_color = (150, 150, 150)
    else:  # Light theme active
        dark_mode_button.color = GRAY
        dark_mode_button.hover_color = (150, 150, 150)
        light_mode_button.color = GREEN
        light_mode_button.hover_color = (0, 255, 0)


# define the grid that the thing will be mapped to
grid = [[0 for i in range(10)] for j in range(10)]

# track revealed tiles
revealed = [[False for i in range(10)] for j in range(10)]

# track flagged tiles
flagged = [[False for i in range(10)] for j in range(10)]

counts = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

squarePickList = [0 for i in range(100)]  # allow the board to pick any item to have a mine on it

first_click_done = False

def draw_sfx_info(surface):
    if not sfx.enabled:
        return
    # Panel geometry (bottom-center)
    panel_w, panel_h = WIDTH // 4, WIDTH // 6 
    panel_x = WIDTH - panel_w 
    panel_y = HEIGHT - panel_h - 80

    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    # Background + border (rounded corners)
    pygame.draw.rect(surface, (45, 45, 45), panel_rect, border_radius=12)
    pygame.draw.rect(surface, WHITE, panel_rect, 2, border_radius=12)

    # Title
    title = "Now Playing an 8-bit Version of:"
    title_surf = tiny_font.render(title, True, WHITE)
    surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2,
                              panel_rect.top + 15))

    # Current song name
    msg = sfx.song_name
    title_surf = tiny_font.render(msg, True, WHITE)
    surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2,
                              panel_rect.top + 30))

    # Album Info
    msg = "- A Kind Of Blue - Miles Davis"
    title_surf = tiny_font.render(msg, True, WHITE)
    surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2,
                              panel_rect.top + 45))
    # Setting button coordinates
    pad = 1
    btn_w, btn_h = 100, 44
    btn_x = panel_rect.right - pad - btn_w
    btn_y = panel_rect.bottom - pad - btn_h 

    # Drawing buttons
    mute_button.rect.topleft = (btn_x, btn_y)
    mute_button.draw(surface, tiny_font)
    skip_button.rect.topleft = (btn_x - btn_w - 5, btn_y)
    skip_button.draw(surface, tiny_font)

def setup_grid():
    # reset the grid back to the original state
    for i in range(10):  # iterate over rows
        for j in range(10):  # iterate over colums
            grid[i][j] = 0  # Set value to 0
            revealed[i][j] = False  # Set it to not revealed
            flagged[i][j] = False  # Set it to not flagged


    # put 1 number for every 100 square
    for i in range(100):
        squarePickList[i] = i # Set the item to the index


# Converts mouse coordinates to grid positions
def get_grid_pos(mouse_x, mouse_y):
    # converts mouse coordinates to grid positions
    # check if click was in grid area
    if (GRID_START_X <= mouse_x <= GRID_START_X + GRID_SIZE * TILE_SIZE and
            GRID_START_Y <= mouse_y <= GRID_START_Y + GRID_SIZE * TILE_SIZE):

        # calculate which row and column was clicked
        col = (mouse_x - GRID_START_X) // TILE_SIZE
        row = (mouse_y - GRID_START_Y) // TILE_SIZE

        # Make sure of valid grid position
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            return row, col
    return None, None  # Result if click was out of grid


# Function to drawr the grid visuaully so the user can see it
def draw_grid():
    # draws column letters A-J
    for col in range(GRID_SIZE):
        x = GRID_START_X + col * TILE_SIZE  # get start pos
        y = GRID_START_Y - 25
        letter = chr(ord('A') + col)  # iterate through different numbers
        col_letters = small_font.render(letter, True, get_current_theme()['text'])  # create the character
        screen.blit(col_letters, (x + TILE_SIZE // 2 - col_letters.get_width() // 2,
                                  y))  # draw onto another object (in this case the tile)

    # draws row numbers 1-10
    for row in range(GRID_SIZE):
        x = GRID_START_X - 30  # get start pos
        y = GRID_START_Y + row * TILE_SIZE
        number = str(row + 1)  # iterate through numbers
        row_numbers = small_font.render(number, True, get_current_theme()['text'])  # create the character
        screen.blit(row_numbers, (x,
                                  y + TILE_SIZE // 2 - row_numbers.get_height() // 2))  # draw onto another object (in this case the tile)

    # draws the grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = GRID_START_X + col * TILE_SIZE  # create the tiles
            y = GRID_START_Y + row * TILE_SIZE

            # draw tile background
            if revealed[row][col]:
                if grid[row][col] == MINE:  # tile turns red if revealed tile is a mine
                    pygame.draw.rect(screen, DARK_RED, (x, y, TILE_SIZE, TILE_SIZE))
                    screen.blit(mines_sprite, (x + 10, y + 10))
                else:  # otherwise the revealed tile turns light gray
                    pygame.draw.rect(screen, get_current_theme()['grid_revealed'], (x, y, TILE_SIZE, TILE_SIZE))
                    n = counts[row][col]  # Show numbers on revealed tiles
                    if n > 0:  # Generate a number on tiles that have nearby mines
                        screen.blit(numbers_sprites[n], (x + 10, y + 10))
            else:  # when not revealed tile is gray
                pygame.draw.rect(screen, get_current_theme()['grid_tile'], (x, y, TILE_SIZE, TILE_SIZE))

            # draw tile border
            pygame.draw.rect(screen, get_current_theme()['grid_border'], (x, y, TILE_SIZE, TILE_SIZE), 2)

            if flagged[row][col] and not revealed[row][col]:
                # Load flag sprite when tile is flagged
                if flag_sprite:
                    screen.blit(flag_sprite, (x + 10, y + 10))


# returns remaining amount of flags (total mines on grid - tiles flags)
def get_remaining_flags():
    flags_used = sum(sum(1 for c in row if c) for row in
                     flagged)  # calculate the number of flags used by counting the flags currently placed
    return counter_value - flags_used  # subtract the flags used from the total flags set by the user at the beggining of the program.


# True while cell is inside the 10x10 grid
def in_bounds(r, c):
    return 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE


# Use a matrix of adjacent-mine counts for each cell to show numbers and decide how far to auto-reveal
def compute_counts(grid):
    counts = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]  # check for nerby 0s
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == MINE:  # check for nearby mines to know if its a 0
                counts[r][c] = -1
                continue
            n = 0
            for dr, dc in DIRS8:  # code that only runs if the num is a 0
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc) and grid[nr][nc] == MINE:
                    n += 1
            counts[r][c] = n
    return counts


# Ensures the player clicks on a blank space, and if not, regenerates the board until that space is blank
def ensure_first_click_safe(fr, fc, grid):
    # allows usage of global variables
    global counts, squarePickList

    # while the grid the player clicks on does not contain a mine and is not bordering any mines
    while not ((grid[fr][fc] != MINE) and (counts[fr][fc] == 0)):
        print("Generate board")

        # reset the grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                grid[r][c] = 0

        # resets pick list
        squarePickList = [i for i in range(GRID_SIZE * GRID_SIZE)]

        # code from the main loop for board generation, just done again
        for i in range(counter_value):
            # pick a random value
            randomIndex = random.randrange(len(squarePickList))
            # remove it so it doesn't get picked again
            randomValue = squarePickList.pop(randomIndex)
            # extract the row and column
            row = randomValue % 10
            column = randomValue // 10
            # print("Row: " , row, " - Coloumn: ", column, " - Item: " , i+1, " - Deleted: " , randomValue, " - Deleted2: " , squarePickList[randomValue-i])
            # mark the item as a mine
            grid[row][column] = int(3)

        # Compute numbers for drawing/reveal logic
        counts = compute_counts(grid)

        # print(grid)

        print(grid)

    return


# Reveal the starting cell if its count is 0, breadth-first reveal adjacent zeros and border numbers.
def flood_reveal(sr, sc, grid, counts, revealed, flagged):
    # exit if the tile is already revealed or flagged
    if revealed[sr][sc] or flagged[sr][sc]:
        return
    # note that the tile should be counted as discoved
    revealed[sr][sc] = True
    # if the the tile isn't a 0, do not reveal more tiles
    if counts[sr][sc] != 0:
        return
    # create a queque of surrounding tiles
    q = deque([(sr, sc)])
    while q:
        # iterate until the queue is empty
        r, c = q.popleft()
        # Check all possible neighboring row/col locations for possible tiles
        for dr, dc in DIRS8:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):  # Check location is on grid, unflagged, not a mine
                continue
            if flagged[nr][nc] or grid[nr][nc] == MINE:
                continue
            if not revealed[nr][nc]:
                revealed[nr][nc] = True
                if counts[nr][nc] == 0:  # add found zero tiles to queue
                    q.append((nr, nc))


# Reveal every mine cell upon loss
def reveal_all_mines(grid, revealed):
    # iterate through all rows and columns
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            # check if its a mine
            if grid[r][c] == MINE:
                # reveal the mine if the user failed
                revealed[r][c] = True


# All non-mine tiles are revealed - win condition.
def check_win(grid, revealed):
    # iterate through all rows and columns
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            # check to see if there are any non-mines that aren't revealed
            if grid[r][c] != MINE and not revealed[r][c]:
                return False
    # if theere are no tiles still needing to be uncovered than the user has won.
    return True

# Create 140 confetti particles for win scenario scene
def spawn_confetti():
        return {"x": random.uniform(0, WIDTH), "y": random.uniform(-120, -10),
                "x2": random.uniform(-1, 1), "y2": random.uniform(.5, 8),
                "size": random.randint(4, 8), "color": random.choice(CONFETTI_COLORS),
                "life": random.uniform(5, 8)}

# Start confetti animation
def start_confetti(n = 140):
    global confetti
    confetti = [spawn_confetti() for _ in range(n)]

# add gravity, motion, to confetti particles
def update_confetti(dt):
    gravity = 200 * dt
    for p in confetti: # define particle motion
        p["x"] += p["x2"]
        p["y"] += p["y2"]
        p["y2"] += gravity
        p["life"] -= dt
    # keep the moving particles visible
    confetti[:] = [p for p in confetti if p["life"] > 0 and p["y"] < HEIGHT + 30]
    # spawn more particles
    while len(confetti) < CONFETTI_TARGET:
        confetti.append(spawn_confetti())

# draw confetti particles during win scenario
def draw_confetti(surface):
    for p in confetti:
        surface.fill(p["color"], (int(p["x"]), int(p["y"]), int(p["size"]), int(p["size"])))

# Using the screen object, print the end of game message
def draw_game_end_message(surface, win: bool):
    # Set the message and text color
    message, text_color = ("You win!", GREEN) if win else ("You lose!", LIGHT_RED)
    return_message = "Click anywhere to return to Menu"

    # Render the message surfaces using font and text color
    message_surface = font.render(message, True, text_color)
    return_surface = small_font.render(return_message, True, get_current_theme()['text'])

    # Calculate box size and position (bottom center, above the bottom margin)
    box_width = 450
    box_height = 120
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT - box_height - 15  # 15px above the bottom

    # Draw a themed rectangle as the background box
    pygame.draw.rect(surface, get_current_theme()['notification_bg'], (box_x, box_y, box_width, box_height), border_radius=12)
    pygame.draw.rect(surface, get_current_theme()['notification_border'], (box_x, box_y, box_width, box_height), 2, border_radius=12) # Add border color

    # Draw the message and return text centered in the box 
    surface.blit(
        message_surface,
        (WIDTH // 2 - message_surface.get_width() // 2, box_y + 20)
    )
    surface.blit(
        return_surface,
        (WIDTH // 2 - return_surface.get_width() // 2, box_y + box_height - 40)
    )

# Draw profile picture, username, and high score in the top-right corner
def draw_profile_and_info(surface):
    # If the profile surface is loaded, draw it in the top-right corner
    if profile_surface:
        # Set the x and y position of the profile picture
        px = WIDTH - PROFILE_MARGIN - PROFILE_DIAMETER
        py = PROFILE_TOP_MARGIN
        surface.blit(profile_surface, (px, py)) # Draw the profile picture at the calculated position on the screen
        
        # Display username and high score below profile picture if logged in
        if auth.is_logged_in():
            uname = auth.get_username() or "" # Get the username of the logged in user
            if uname:
                name_surf = small_font.render(uname, True, get_current_theme()['text']) # Render the username as a surface
                name_x = px + PROFILE_DIAMETER // 2 - name_surf.get_width() // 2
                name_y = py + PROFILE_DIAMETER + 6 # Set the y position of the username
                surface.blit(name_surf, (name_x, name_y))
                
                # Display high score below username in gold color
                high_score = auth.get_high_score()
                # Render the high score as a surface
                score_surf = small_font.render(f"Best: {high_score}", True, (255, 215, 0))  # Gold color
                # Set the x position of the high score
                score_x = px + PROFILE_DIAMETER // 2 - score_surf.get_width() // 2
                score_y = name_y + 30 # Set the y position of the high score
                surface.blit(score_surf, (score_x, score_y))

def draw_high_score_notification(surface):
    # Draw a green notification box for new high score
    message = "New High Score!"
    message_surface = small_font.render(message, True, get_current_theme()['text'])
    
    # Box dimensions
    box_width = 300
    box_height = 60
    box_x = WIDTH // 2 - box_width // 2 # Set the x position of the box as the middle of the screen
    box_y = 50  # Set the y position of the box as the top of the screen
    
    # Draw green background box with themed border
    pygame.draw.rect(surface, (0, 180, 0), (box_x, box_y, box_width, box_height), border_radius=8)
    pygame.draw.rect(surface, get_current_theme()['notification_border'], (box_x, box_y, box_width, box_height), 2, border_radius=8)
    
    # Draw message centered in the box
    surface.blit(
        message_surface,
        (WIDTH // 2 - message_surface.get_width() // 2, box_y + 20)
    )

# Main Game Loop
setup_grid() # Setup the grid
sfx.start_bgmusic()

# Load user's theme preference
load_user_theme()

running = True

while running:
    dt = clock.tick(60) / 1000.0 # seconds since last frame

    # Fill background with theme color every frame
    screen.fill(get_current_theme()['background'])

    # Handle AI updates outside the user input processing and response loop
    draw_sfx_info(screen)
    if state == PLAYING:
        # --- AI MOVE (automatic or interactive) ---
        if ai and not player_turn:
            sleep(0.5)
            row, col, action = ai.make_move()
            if row is not None and col is not None:
                if action == "reveal":
                    if not flagged[row][col] and not revealed[row][col]:
                        if not first_click_done:  # Ensure a mine isn't initially clicked
                            ensure_first_click_safe(row, col, grid)
                            sfx.play_square_revealed()
                            counts = compute_counts(grid)
                            first_click_done = True
                            # Remake the ai object with the new board
                            ai = ai_solver(difficulty, grid, counts, revealed, flagged)
                            # Start the game timer
                            game_time.start()
                        if grid[row][col] == MINE:  # Check for loss
                            sfx.play_loss()
                            revealed[row][col] = True
                            reveal_all_mines(grid, revealed)  # reveal all mines on loss
                            state = LOSE
                            # Stop the game timer
                            game_time.stop()
                        else:  # Check win condition
                            sfx.play_square_revealed()
                            flood_reveal(row, col, grid, counts, revealed, flagged)
                            revealed[row][col] = True
                            if check_win(grid, revealed):
                                state = WIN
                                sfx.play_win()
                                start_confetti() # add confetti animation
                                # Stop the game timer
                                game_time.stop()
                                # Calculate and update high score (only for logged-in users since they have a high score and guest doesn't)
                                if auth.is_logged_in():
                                    # Get the elapsed time in seconds
                                    elapsed_seconds = game_time.get_elapsed_time_seconds()
                                    # Avoid division by zero
                                    if elapsed_seconds > 0:
                                        # Calculate the score
                                        score = (counter_value * 1000) // elapsed_seconds  # Higher score = better
                                        # Check if the score is a new high score
                                        is_new_high = auth.set_high_score(score)
                                        # Show notification if it's a new high score
                                        if is_new_high:
                                            # Show notification if it's a new high score (for 3s)
                                            show_high_score_notification = True # Global toggle
                                            # Set the notification start time to the current time
                                            notification_start_time = pygame.time.get_ticks()
                elif action == "flag":
                    if not revealed[row][col]:
                        if flagged[row][col]:
                            sfx.play_flag_popped()
                            flagged[row][col] = False
                        elif get_remaining_flags() > 0:
                            sfx.play_flag_placed()
                            flagged[row][col] = True  # flag only if flags remain
            if mode == AI_INTERACTIVE and action != "flag":
                # In AUTOMATIC, keep player_turn = False so the AI moves again next frame.
                # Also, since flags don't count as moves, don't progress to the next turn if the action
                # taken was to place a flag.
                player_turn = True

    # Handle events/inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Close window
            running = False
        if skip_button.is_clicked(event):
            sfx.change_song()
        elif mute_button.is_clicked(event):
            if sfx.enabled:
                if not sfx.muted:
                    mute_button.text = "Unmute"
                    sfx.music_channel.set_volume(0)
                    sfx.muted = True
                else:
                    mute_button.text = "Mute"
                    sfx.music_channel.set_volume(0.1)
                    sfx.muted = False

        # MENU state logic
        if state == MENU:
            sfx.stop_sfx()
            if start_button.is_clicked(event):
                sfx.play_square_revealed()
                state = PLAYING
                # Reset high score notification when starting new game
                show_high_score_notification = False
                # Reset the game timer
                game_time.reset()
                # Add the game code here, or a call to some other module
                print("Generate board")

                for i in range(counter_value):
                    # pick a random value
                    randomIndex = random.randrange(len(squarePickList))
                    # remove it so it doesn't get picked again
                    randomValue = squarePickList.pop(randomIndex)
                    # extract the row and column
                    row = randomValue % 10
                    column = randomValue // 10
                    # print("Row: " , row, " - Coloumn: ", column, " - Item: " , i+1, " - Deleted: " , randomValue, " - Deleted2: " , squarePickList[randomValue-i])
                    # mark the item as a mine
                    grid[row][column] = int(3)

                # Compute numbers for drawing/reveal logic
                counts = compute_counts(grid)
                first_click_done = False

                # Define AI & turn order
                ai = None
                player_turn = True

                # If an AI mode is selected, make a solver instance
                if mode == AI_AUTOMATIC or mode == AI_INTERACTIVE:
                    ai = ai_solver(difficulty, grid, counts, revealed, flagged)
                    if mode == AI_AUTOMATIC:
                        player_turn = False

                # print(grid)
                print(grid)

                # generate a list of squares that can be chosen


            # logged-in only: change pfp
            elif auth.is_logged_in() and change_pfp_button.is_clicked(event):
                state = "set_pfp"  # path input state
                setpfp_input = ""
            # logged-in only: logout
            elif auth.is_logged_in() and logout_button.is_clicked(event):
                auth.logout()
                profile_surface = load_circular_profile(resolve_profile_path(), PROFILE_DIAMETER)
            # logged-out only: sign in or create
            elif (not auth.is_logged_in()) and sign_in_create_button.is_clicked(event):
                state = "signup"  # username input state
                signup_input = ""
            # quit the game if the user presses quit
            elif quit_button.is_clicked(event):
                running = False  # Quit game

            elif plus_button.is_clicked(event):
                # check that the user doens't have more than the max bombs (20)
                if (counter_value < 20):
                    counter_value += 1  # Increase # bombs in menu

            elif minus_button.is_clicked(event):
                # check that the user doens't have less than the min bombs (10)
                if (counter_value > 10):
                    counter_value -= 1  # Decrease # bombs in menu

            elif settings_button.is_clicked(event):
                state = "settings"

        elif state == "settings":
            if easy_button.is_clicked(event):
                difficulty = EASY
            if medium_button.is_clicked(event):
                difficulty = MEDIUM
            if hard_button.is_clicked(event):
                difficulty = HARD
            if mode_interactive_button.is_clicked(event):
                mode = AI_INTERACTIVE
            if mode_automatic_button.is_clicked(event):
                mode = AI_AUTOMATIC
            if mode_manual_button.is_clicked(event):
                mode = AI_MANUAL
            if dark_mode_button.is_clicked(event):
                switch_theme("dark")
                auth.set_theme_preference("dark")
                update_theme_button_styles()
            if light_mode_button.is_clicked(event):
                switch_theme("light")
                auth.set_theme_preference("light")
                update_theme_button_styles()
            if settings_continue_button.is_clicked(event):
                state = MENU

        # PLAYING state logic
        elif state == PLAYING:
            # --- PLAYER INPUT ---
            if event.type == pygame.MOUSEBUTTONDOWN and mode != AI_AUTOMATIC:
                mouse_x, mouse_y = event.pos  # get coordinates of mouse
                row, col = get_grid_pos(mouse_x, mouse_y)  # convert coordinates to grid position

                if row is not None and col is not None:  # check if click is in grid
                    if event.button == 1:  # a left click
                        if not flagged[row][col]:  # can't reveal a flagged tile
                            if revealed[row][col]:
                                # already revealed, ignore this click entirely
                                continue
                            if not first_click_done:  # Ensure a mine isn't initially clicked
                                ensure_first_click_safe(row, col, grid)
                                sfx.play_square_revealed()
                                counts = compute_counts(grid)
                                first_click_done = True
                                # Remake the ai object with the new board
                                ai = ai_solver(difficulty, grid, counts, revealed, flagged)
                                # Start the game timer
                                game_time.start()
                            if grid[row][col] == MINE:  # Check for loss
                                sfx.play_loss()
                                revealed[row][col] = True
                                reveal_all_mines(grid, revealed)  # reveal all mines on loss
                                state = LOSE
                                # Stop the game timer
                                game_time.stop()
                            else:  # Check win condition
                                sfx.play_square_revealed()
                                flood_reveal(row, col, grid, counts, revealed, flagged)
                                revealed[row][col] = True
                                if check_win(grid, revealed):
                                    state = WIN
                                    sfx.play_win()
                                    start_confetti() # add confetti animation
                                    # Stop the game timer
                                    game_time.stop()
                                    # Calculate and update high score (only for logged-in users since they have a high score and guest doesn't)
                                    if auth.is_logged_in():
                                        # Get the elapsed time in seconds
                                        elapsed_seconds = game_time.get_elapsed_time_seconds()
                                        # Avoid division by zero
                                        if elapsed_seconds > 0:
                                            # Calculate the score
                                            score = (counter_value * 1000) // elapsed_seconds  # Higher score = better
                                            # Check if the score is a new high score
                                            is_new_high = auth.set_high_score(score)
                                            # Show notification if it's a new high score
                                            if is_new_high:
                                                # Show notification if it's a new high score (for 3s)
                                                show_high_score_notification = True # Global toggle
                                                # Set the notification start time to the current time
                                                notification_start_time = pygame.time.get_ticks()
                            if mode == AI_INTERACTIVE:
                                player_turn = False
                    elif event.button == 3:  # a right click
                        # check that the flagged tile isn't revealed
                        if not revealed[row][col]:
                            # if the user has flags flag it but if they don't have flags don't do anything
                            if flagged[row][col]:
                                sfx.play_flag_popped()
                                flagged[row][col] = False
                            elif get_remaining_flags() > 0:
                                sfx.play_flag_placed()
                                flagged[row][col] = True  # flag only if flags remain


        # SIGNUP state
        elif state == "signup":
            if event.type == pygame.KEYDOWN:
                # Submit on Enter
                if event.key == pygame.K_RETURN:
                    if signup_input.strip():
                        # Issue a token for the user
                        auth.issue_token(signup_input.strip())
                        # Load the user's profile picture
                        profile_surface = load_circular_profile(resolve_profile_path(), PROFILE_DIAMETER)
                        state = MENU
                # Go back on '0' without changes
                elif event.key == pygame.K_0:
                    state = MENU
                # Backspace
                elif event.key == pygame.K_BACKSPACE:
                    signup_input = signup_input[:-1]
                # Regular character input
                else:
                    if event.unicode.isprintable():
                        # Add the input to the buffer
                        signup_input += event.unicode

        # SET_PFP state
        elif state == "set_pfp":
            if event.type == pygame.KEYDOWN:
                # Submit on Enter
                if event.key == pygame.K_RETURN:
                    # Save the user's profile picture under a username-specific filename
                    username = auth.get_username() or "guest"
                    saved = save_profile_image(setpfp_input.strip(), username)
                    if saved:
                        # Set the user's profile picture path
                        auth.set_pfp_path(saved)
                        # Load the user's profile picture
                        profile_surface = load_circular_profile(resolve_profile_path(), PROFILE_DIAMETER)
                        state = MENU
                        setpfp_error = ""  # clear any previous error on success
                    else:
                        # Show an error and stay on this screen
                        setpfp_error = "Invalid path or unreadable image. Try again or press 0 to go back."
                # Go back on '0'
                elif event.key == pygame.K_0:
                    state = MENU
                # Backspace
                elif event.key == pygame.K_BACKSPACE:
                    setpfp_input = setpfp_input[:-1]
                # Regular character input (clear error when typing)
                else:
                    if event.unicode.isprintable():
                        setpfp_input += event.unicode
                        setpfp_error = ""

        # WIN and LOSE state logic
        elif state in [WIN, LOSE]:
            # check for win/lose everythime the user clicks (no need to waste resources as the board state only changes when clicks occur)
            if event.type == pygame.MOUSEBUTTONDOWN:
                state = MENU

                # reset the grid back to the original state
                for i in range(10):
                    for j in range(10):
                        grid[i][j] = 0
                        revealed[i][j] = False
                        flagged[i][j] = False

                # reset the pick list
                squarePickList = [0 for i in range(100)]
                for i in range(100):
                    squarePickList[i] = i

                # Reset mine counts
                counts = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

                # Reset first click check
                first_click_done = False

                # Reset the game timer
                game_time.reset()

                # Reset high score notification
                show_high_score_notification = False

                # Code here to reset values when going back to the menu

    # Drawing (depends on state)
    # Where the game should be drawn, visuals and images
    if state == MENU:
        # Title
        title_surf = font.render("Minesweeper", True, get_current_theme()['text'])
        title_x = WIDTH // 2 - title_surf.get_width() // 2
        title_y = 60
        screen.blit(title_surf, (title_x, title_y))

        # Build vertical stack of primary buttons (made it dynamic and dependent on the login state)
        primary_buttons = [start_button]
        # Add the settings button
        primary_buttons.append(settings_button)
        if auth.is_logged_in():
            # if the user is logged in, add the change pfp and logout buttons
            primary_buttons += [change_pfp_button, logout_button]
        else:
            # If the user is not logged in, add the sign in or create button
            primary_buttons += [sign_in_create_button]
        # Add the quit button
        primary_buttons.append(quit_button)

        # Layout values
        stack_spacing = 18
        # Set the top y position of the buttons
        stack_top_y = title_y + title_surf.get_height() + 20
        # Set the width of the buttons
        button_width = 200
        # Set the height of the buttons
        button_height = 60
        # Set the x position of the buttons
        stack_x = WIDTH // 2 - button_width // 2

        # Position buttons in a tidy vertical stack
        current_y = stack_top_y
        for btn in primary_buttons:
            # Set the position of the buttons
            btn.rect.topleft = (stack_x, current_y)
            # Set the y position of the buttons
            current_y += button_height + stack_spacing

        # Bottom controls row: center minus, counter, plus near bottom
        bottom_margin = 20
        # Set the y position of the buttons
        row_y = HEIGHT - bottom_margin - button_height // 2
        # Set the x position of the buttons
        side_gap = 110
        # Set the position of the buttons
        minus_button.rect.center = (WIDTH // 2 - side_gap, row_y)
        # Set the position of the buttons
        plus_button.rect.center = (WIDTH // 2 + side_gap, row_y)

        # Draw buttons
        for btn in primary_buttons:
            # Draw the buttons
            btn.draw(screen, small_font)
        # Draw the minus button
        minus_button.draw(screen, font)
        # Draw the plus button
        plus_button.draw(screen, font)

        # Counter centered between +/-
        counter_surf = font.render(str(counter_value), True, get_current_theme()['text'])
        # Set the x position of the counter
        counter_x = WIDTH // 2 - counter_surf.get_width() // 2
        # Set the y position of the counter
        counter_y = row_y - counter_surf.get_height() // 2
        # Draw the counter
        screen.blit(counter_surf, (counter_x, counter_y))

        # playing status
        playing_info = small_font.render("Current Status: MENU", True, get_current_theme()['text'])
        screen.blit(playing_info, (10, 10))

        # difficulty display
        difficulty_setting = small_font.render(f"AI Difficulty: {difficulty.upper()}", True, get_current_theme()['text'])
        screen.blit(difficulty_setting, (10, 200))

        # mode display
        mode_setting = small_font.render(f"AI Mode: {mode.upper()}", True, get_current_theme()['text'])
        screen.blit(mode_setting, (10, 240))

        # Profile picture, username, and high score
        draw_profile_and_info(screen)

    elif state == "settings":
            # difficulty display
            difficulty_display = small_font.render("SELECT AI DIFFICULTY", True, get_current_theme()['text'])
            screen.blit(difficulty_display, (WIDTH // 2 - 300, 60))

            # settings
            spacing = 160

            # Set the position of the buttons
            easy_button.rect.center = (WIDTH // 2 - spacing, 160)
            easy_button.draw(screen, small_font)
            # Set the position of the buttons
            medium_button.rect.center = (WIDTH // 2 - spacing, 240)
            medium_button.draw(screen, small_font)
            # Set the position of the buttons
            hard_button.rect.center = (WIDTH // 2 - spacing, 320)
            hard_button.draw(screen, small_font)

            # mode display
            mode_display = small_font.render("SELECT AI MODE", True, get_current_theme()['text'])
            screen.blit(mode_display, (WIDTH // 2 + 60, 60))

            # Set the position of the buttons
            mode_interactive_button.rect.center = (WIDTH // 2 + spacing, 160)
            mode_interactive_button.draw(screen, small_font)
            # Set the position of the buttons
            mode_automatic_button.rect.center = (WIDTH // 2 + spacing, 240)
            mode_automatic_button.draw(screen, small_font)
            # Set the position of the buttons
            mode_manual_button.rect.center = (WIDTH // 2 + spacing, 320)
            mode_manual_button.draw(screen, small_font)

            # Output display
            current_difficulty_display = small_font.render(f"Set to: {difficulty.upper()}", True, get_current_theme()['text'])
            screen.blit(current_difficulty_display, (WIDTH // 2 - 260, 380))
            current_mode_display = small_font.render(f"Set to: {mode.upper()}", True, get_current_theme()['text'])
            screen.blit(current_mode_display, (WIDTH // 2 + 60, 380))

            # Theme selection section - moved down for better spacing
            theme_display = small_font.render("SELECT THEME", True, get_current_theme()['text'])
            screen.blit(theme_display, (WIDTH // 2 - theme_display.get_width() // 2, 440))
            
            # Position and draw theme buttons with more spacing
            dark_mode_button.rect.center = (WIDTH // 2 - 50, 490)
            light_mode_button.rect.center = (WIDTH // 2 + 50, 490)
            dark_mode_button.draw(screen, small_font)
            light_mode_button.draw(screen, small_font)

            # Add the continue button with much more spacing from bottom
            settings_continue_button.rect.center = (WIDTH // 2, 580)
            settings_continue_button.draw(screen, small_font)

    # What should be displayed during each state
    elif state == PLAYING:
        draw_grid()

        # Instructions
        info_surf = small_font.render("Left click: Reveal | Right click: Flag", True, get_current_theme()['text'])
        screen.blit(info_surf, (10, HEIGHT - 30))

        # playing status
        playing_info = small_font.render("Current Status: Playing", True, get_current_theme()['text'])
        screen.blit(playing_info, (10, 10))
        
        # game timer display
        if game_time.running:
            # Get the elapsed time and set up the surface
            timer_info = small_font.render(f"Time: {game_time.get_elapsed_time()}", True, get_current_theme()['text'])
            # Draw the game time info
            screen.blit(timer_info, (10, 40))

        # Turn display
        if auth.is_logged_in():
            username = auth.get_username()
        else:
            username = "Player"
        turn_string = "Turn: " + (username if player_turn else "AI")
        turn_display = small_font.render(turn_string, True, get_current_theme()['text'])
        screen.blit(turn_display, (10, HEIGHT - 60))

        # Profile picture, username, and high score
        draw_profile_and_info(screen)

        remaining_flags_text = small_font.render(f"Flags Remaining: {get_remaining_flags()}", True, get_current_theme()['text'])
        x = WIDTH - remaining_flags_text.get_width() - 10
        y = HEIGHT - remaining_flags_text.get_height() - 10
        screen.blit(remaining_flags_text, (x, y))

    # SIGNUP screen UI
    elif state == "signup":
        # Set the prompt
        prompt = small_font.render("Enter username (Enter submit, 0 back):", True, get_current_theme()['text'])
        # Set the x position of the prompt
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 40))
        # Set the typed input
        typed = small_font.render(signup_input, True, get_current_theme()['text'])
        # Draw the typed input
        screen.blit(typed, (WIDTH // 2 - typed.get_width() // 2, HEIGHT // 2))

    # SET_PFP screen UI
    elif state == "set_pfp":
        # Set the prompt
        prompt = small_font.render("Enter image path (Enter submit, 0 back):", True, get_current_theme()['text'])
        # Draw the prompt
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 60))
        # Set the typed input
        typed = small_font.render(setpfp_input, True, get_current_theme()['text'])
        # Draw the typed input
        screen.blit(typed, (WIDTH // 2 - typed.get_width() // 2, HEIGHT // 2 - 20))
        # If there is an error, show it in red below the input
        if setpfp_error:
            error_surf = small_font.render(setpfp_error, True, RED)
            screen.blit(error_surf, (WIDTH // 2 - error_surf.get_width() // 2, HEIGHT // 2 + 20))

    # if the user wins
    elif state == WIN:
        draw_grid() # show board with no mines uncovered
        update_confetti(dt)
        draw_confetti(screen)

        # tell the user they won
        draw_game_end_message(screen, True)

        # playing status
        playinginfo = small_font.render("Current Status: WIN", True, get_current_theme()['text'])
        screen.blit(playinginfo, (10, 10))
        
        # Display final time
        timer_text = small_font.render(f"Time: {game_time.get_elapsed_time()}", True, get_current_theme()['text'])
        screen.blit(timer_text, (10, 40))
        
        # Profile picture, username, and high score
        draw_profile_and_info(screen)
        
        # Draw high score notification if active
        if show_high_score_notification:
            # Draw high score notification for a duration of 3 seconds
            elapsed_notif = (pygame.time.get_ticks() - notification_start_time) / 1000.0
            if elapsed_notif < NOTIFICATION_DURATION:
                draw_high_score_notification(screen)
            else:
                # Hide notification after duration expires
                show_high_score_notification = False

    # if the user loses
    elif state == LOSE:
        draw_grid() # Show the board with all mines revealed

        # tell the user they lost
        draw_game_end_message(screen, False)

        # playing status
        playinginfo = small_font.render("Current Status: LOSE", True, get_current_theme()['text'])
        screen.blit(playinginfo, (10, 10))
        
        # Display final time
        timer_text = small_font.render(f"Time: {game_time.get_elapsed_time()}", True, get_current_theme()['text'])
        screen.blit(timer_text, (10, 40))
        
        # Profile picture, username, and high score
        draw_profile_and_info(screen)

    # Update screen
    pygame.display.flip()

# Exit
pygame.quit()
