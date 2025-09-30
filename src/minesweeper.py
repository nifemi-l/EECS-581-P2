# Classes include the following:
#   Button class: used to detect and respond to mouse clicks
#   get grid pos funtion: used to figure out where a mouse click coresponds to which square in teh 2d array strucutre
#   draw grid fuinction: used to draw the grid and the items in it
#   get_remaining_flags func: used to calaculate and display how many mines are left if the user has been correct in flag placement
# The program takes in mouse clicks from the user as input and outputs the current state of the minsweeper board
# No external code was used (no Chat GPT or stack overflow)
# Created by Nevan Snider on Sept 3rd, with contributions from Evan Rogerson, Spencer Rodenberg, Kyle Whitmer, and Karsten Wolter

import pygame  # import pygame, the main GUI we used in order to create images and track mouse clicks.
from pygame import mixer
import random  # import random to randomly pick mine locations
import os # Access visual asset path
from collections import deque  # Queue for flood-fill
from button import Button
from game_assets import flag_sprite, mines_sprite, numbers_sprites, load_circular_profile
from auth import AuthContext  # simple local auth (token/user.json)
from pfp_helper import save_profile_image  # copy chosen image to assets
from sfx import SFX

from settings import (
    clock, screen, WIDTH, HEIGHT,
    WHITE, BLACK, GREEN, RED, DARK_RED, PURPLE, GRAY, LIGHT_GRAY, CONFETTI_COLORS, BLUE,
    font, small_font,
    MENU, PLAYING, WIN, LOSE,
    GRID_SIZE, TILE_SIZE, GRID_START_X, GRID_START_Y,
    MINE, DIRS8, CONFETTI_TARGET, ASSETS_DIR,
    EASY, MEDIUM, HARD
)

state = MENU  # start in the main menu
counter_value = 10  # adjustable number in main menu
difficulty = MEDIUM # default to medium

# global confetti list
confetti = []

# Load the auth context to manage token/username/pfp
auth = AuthContext()

PROFILE_DIAMETER = 56  # profile picture diameter
PROFILE_MARGIN = 10    # margin from edge

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
select_difficulty_button = Button(WIDTH // 2 - 100, 240, 200, 60, "Select Difficulty", PURPLE, (255, 0, 255)) # Difficulty selection
easy_button = Button(WIDTH // 2 - 100, 240, 200, 60, "Easy", GREEN, (0, 255, 0)) # Difficulty menu: easy
medium_button = Button(WIDTH // 2 - 100, 310, 200, 60, "Medium", (0, 200, 200), (0, 255, 255)) # Difficulty menu: medium
hard_button = Button(WIDTH // 2 - 100, 380, 200, 60, "Hard", RED, (255, 0, 0)) # Difficulty menu: hard
sign_in_create_button = Button(WIDTH // 2 - 100, 310, 200, 60, "Sign In / Create", BLUE, (32, 96, 255))  # Sign in or create
change_pfp_button = Button(WIDTH // 2 - 100, 310, 200, 60, "Change PFP", GRAY, (150, 150, 150))  # set pfp
logout_button = Button(WIDTH // 2 - 100, 380, 200, 60, "Logout", RED, (255, 0, 0))  # Logout
quit_button = Button(WIDTH // 2 - 100, 450, 200, 60, "Quit", RED, (255, 0, 0))  # Quit
plus_button = Button(WIDTH // 2 + 60, 550, 60, 60, "+", GRAY, (150, 150, 150))  # Inc bombs
minus_button = Button(WIDTH // 2 - 120, 550, 60, 60, "-", GRAY, (150, 150, 150))  # Dec bombs


# define the grid that the thing will be mapped to
grid = [[0 for i in range(10)] for j in range(10)]

# track revealed tiles
revealed = [[False for i in range(10)] for j in range(10)]

# track flagged tiles
flagged = [[False for i in range(10)] for j in range(10)]

counts = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

squarePickList = [0 for i in range(100)]  # allow the board to pick any item to have a mine on it

first_click_done = False

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
        col_letters = small_font.render(letter, True, WHITE)  # create the character
        screen.blit(col_letters, (x + TILE_SIZE // 2 - col_letters.get_width() // 2,
                                  y))  # draw onto another object (in this case the tile)

    # draws row numbers 1-10
    for row in range(GRID_SIZE):
        x = GRID_START_X - 30  # get start pos
        y = GRID_START_Y + row * TILE_SIZE
        number = str(row + 1)  # iterate through numbers
        row_numbers = small_font.render(number, True, WHITE)  # create the character
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
                    pygame.draw.rect(screen, LIGHT_GRAY, (x, y, TILE_SIZE, TILE_SIZE))
                    n = counts[row][col]  # Show numbers on revealed tiles
                    if n > 0:  # Generate a number on tiles that have nearby mines
                        screen.blit(numbers_sprites[n], (x + 10, y + 10))
            else:  # when not revealed tile is gray
                pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE))

            # draw tile border
            pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 2)

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

# Main Game Loop
setup_grid() # Setup the grid
sfx = SFX(pygame.mixer)
sfx.start_bgmusic()

running = True

while running:
    dt = clock.tick(60) / 1000.0 # seconds since last frame

    # Fill background black every frame
    screen.fill(BLACK)

    # Handle events/inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Close window
            running = False

        # MENU state logic
        if state == MENU:
            sfx.sfx_channel.stop()
            if start_button.is_clicked(event):
                sfx.play_square_revealed()
                state = PLAYING
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

            elif select_difficulty_button.is_clicked(event):
                state = "select_difficulty"

        elif state == "select_difficulty":
            if easy_button.is_clicked(event):
                difficulty = EASY
                state = MENU
            if medium_button.is_clicked(event):
                difficulty = MEDIUM
                state = MENU
            if hard_button.is_clicked(event):
                difficulty = HARD
                state = MENU

        # PLAYING state logic
        elif state == PLAYING:
            # check if the user presses any mouse button
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos  # get coordinates of mouse
                row, col = get_grid_pos(mouse_x, mouse_y)  # convert coordinates to grid position

                if row is not None and col is not None:  # check if click is in grid
                    if event.button == 1:  # a left click
                        if not flagged[row][col]:  # can't reveal a flagged tile
                            if not first_click_done:  # Ensure a mine isn't initially clicked
                                ensure_first_click_safe(row, col, grid)
                                sfx.play_square_revealed()
                                counts = compute_counts(grid)
                                first_click_done = True
                            if grid[row][col] == MINE:  # Check for loss
                                sfx.play_loss()
                                revealed[row][col] = True
                                reveal_all_mines(grid, revealed)  # reveal all mines on loss
                                state = LOSE
                            else:  # Check win condition
                                sfx.play_square_revealed()
                                flood_reveal(row, col, grid, counts, revealed, flagged)
                                revealed[row][col] = True
                                if check_win(grid, revealed):
                                    state = WIN
                                    sfx.play_win()
                                    start_confetti() # add confetti animation
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

                # Code here to reset values when going back to the menu

    # Drawing (depends on state)
    # Where the game should be drawn, visuals and images
    if state == MENU:
        # Title
        title_surf = font.render("Minesweeper", True, WHITE)
        title_x = WIDTH // 2 - title_surf.get_width() // 2
        title_y = 60
        screen.blit(title_surf, (title_x, title_y))

        # Build vertical stack of primary buttons (made it dynamic and dependent on the login state)
        primary_buttons = [start_button]
        # Add the difficulty select button
        primary_buttons.append(select_difficulty_button)
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
        counter_surf = font.render(str(counter_value), True, WHITE)
        # Set the x position of the counter
        counter_x = WIDTH // 2 - counter_surf.get_width() // 2
        # Set the y position of the counter
        counter_y = row_y - counter_surf.get_height() // 2
        # Draw the counter
        screen.blit(counter_surf, (counter_x, counter_y))

        # playing status
        playinginfo = small_font.render("Current Status: MENU", True, WHITE)
        screen.blit(playinginfo, (10, 10))

        # difficulty display
        difficulty_setting = small_font.render(f"AI Difficulty: {difficulty.upper()}", True, WHITE)
        screen.blit(difficulty_setting, (10, 40))

        # Profile picture (top-right)
        if profile_surface:
            # Set the x position of the profile picture
            px = WIDTH - PROFILE_MARGIN - PROFILE_DIAMETER
            # Set the y position of the profile picture
            py = PROFILE_MARGIN
            # Draw the profile picture
            screen.blit(profile_surface, (px, py))
            # Draw username under avatar when logged in
            if auth.is_logged_in():
                uname = auth.get_username() or ""
                if uname:
                    name_surf = small_font.render(uname, True, WHITE)
                    name_x = px + PROFILE_DIAMETER // 2 - name_surf.get_width() // 2
                    name_y = py + PROFILE_DIAMETER + 6
                    screen.blit(name_surf, (name_x, name_y))

    elif state == "select_difficulty":
            # difficulty display
            difficulty_display = small_font.render("SELECT AI DIFFICULTY", True, WHITE)
            screen.blit(difficulty_display, (WIDTH // 2 - 130, 60))

            # Set the position of the buttons
            easy_button.rect.center = (WIDTH // 2, 160)
            easy_button.draw(screen, small_font)
            # Set the position of the buttons
            medium_button.rect.center = (WIDTH // 2, 240)
            medium_button.draw(screen, small_font)
            # Set the position of the buttons
            hard_button.rect.center = (WIDTH // 2, 320)
            hard_button.draw(screen, small_font)

    # What should be displayed during each state
    elif state == PLAYING:
        draw_grid()

        # Instructions
        info_surf = small_font.render("Left click: Reveal | Right click: Flag", True, WHITE)
        screen.blit(info_surf, (10, HEIGHT - 30))

        # playing status
        playinginfo = small_font.render("Current Status: Playing", True, WHITE)
        screen.blit(playinginfo, (10, 10))
        # Draw the profile picture in the top-right corner during the PLAYING state
        if profile_surface:  # Check if the profile image surface was loaded successfully
            px = WIDTH - PROFILE_MARGIN - PROFILE_DIAMETER  # Calculate the x-coordinate for the profile picture (right-aligned with margin)
            py = PROFILE_MARGIN  # Set the y-coordinate for the profile picture (top margin)
            screen.blit(profile_surface, (px, py))  # Draw the profile picture at the calculated position on the screen
            # Draw username under avatar when logged in
            if auth.is_logged_in():
                uname = auth.get_username() or ""
                if uname:
                    name_surf = small_font.render(uname, True, WHITE)
                    name_x = px + PROFILE_DIAMETER // 2 - name_surf.get_width() // 2
                    name_y = py + PROFILE_DIAMETER + 6
                    screen.blit(name_surf, (name_x, name_y))

        remaining_flags_text = small_font.render(f"Flags Remaining: {get_remaining_flags()}", True, WHITE)
        x = WIDTH - remaining_flags_text.get_width() - 10
        y = HEIGHT - remaining_flags_text.get_height() - 10
        screen.blit(remaining_flags_text, (x, y))

    # SIGNUP screen UI
    elif state == "signup":
        # Set the prompt
        prompt = small_font.render("Enter username (Enter submit, 0 back):", True, WHITE)
        # Set the x position of the prompt
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 40))
        # Set the typed input
        typed = small_font.render(signup_input, True, WHITE)
        # Draw the typed input
        screen.blit(typed, (WIDTH // 2 - typed.get_width() // 2, HEIGHT // 2))

    # SET_PFP screen UI
    elif state == "set_pfp":
        # Set the prompt
        prompt = small_font.render("Enter image path (Enter submit, 0 back):", True, WHITE)
        # Draw the prompt
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 60))
        # Set the typed input
        typed = small_font.render(setpfp_input, True, WHITE)
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
        win_surf = font.render("You Win!", True, GREEN)
        screen.blit(win_surf, (WIDTH // 2 - win_surf.get_width() // 2, HEIGHT // 2))

        # give options to return to menu
        info_surf = small_font.render("Click anywhere to return to Menu", True, WHITE)
        screen.blit(info_surf, (WIDTH // 2 - info_surf.get_width() // 2, HEIGHT // 2 + 50))

        # playing status
        playinginfo = small_font.render("Current Status: WIN", True, WHITE)
        screen.blit(playinginfo, (10, 10))

    # if the user loses
    elif state == LOSE:
        draw_grid() # Show the board with all mines revealed
        # tell the user they lost
        lose_surf = font.render("You Lose!", True, RED)
        screen.blit(lose_surf, (WIDTH // 2 - lose_surf.get_width() // 2, HEIGHT // 2))

        # give options to return to menu
        info_surf = small_font.render("Click anywhere to return to Menu", True, WHITE)
        screen.blit(info_surf, (WIDTH // 2 - info_surf.get_width() // 2, HEIGHT // 2 + 50))

        # playing status
        playinginfo = small_font.render("Current Status: LOSE", True, WHITE)
        screen.blit(playinginfo, (10, 10))

    # Update screen
    pygame.display.flip()

# Exit
pygame.quit()


