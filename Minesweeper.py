# Classes include the following:
#   Button class: used to detect and respond to mouse clicks
#   get grid pos funtion: used to figure out where a mouse click coresponds to which square in teh 2d array strucutre
#   draw grid fuinction: used to draw the grid and the items in it
#   get_remaining_flags func: used to calaculate and display how many mines are left if the user has been correct in flag placement
# The program takes in mouse clicks from the user as input and outputs the current state of the minsweeper board
# No external code was used (no Chat GPT or stack overflow)
# Created by Nevan Snider on Sept 3rd, with contributions from Evan Rogerson, Spencer Rodenberg, Kyle Whitmer, and Karsten Wolter

import pygame  # import pygame, the main GUI we used in order to create images and track mouse clicks.

import random  # import random to randomly pick mine locations

import os # access visual asset path

from collections import deque  # Queue for flood-fill

pygame.init()  # start pygame

clock = pygame.time.Clock() # for smooth animation

# Screen setup
WIDTH, HEIGHT = 800, 600  # seight height and width of the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # create the screen
pygame.display.set_caption("Minesweeper")  # title the program

# Colors
WHITE = (255, 255, 255)  # define white on the RGB scale
BLACK = (0, 0, 0)  # define black on the RGB scale
GREEN = (0, 200, 0)  # define green on the RGB scale
RED = (200, 0, 0)  # define red on the RGB scale
DARK_RED = (150, 20, 20) # define darker red for mine background
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

state = MENU  # start in the main menu
counter_value = 10  # adjustable number in main menu

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
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
NUM_DIR    = os.path.join(ASSETS_DIR, "numbers")

# Convert visual assets to pygame surface
def load_image(path):
    image = pygame.image.load(path).convert_alpha()
    return image

# Sprites
flag_sprite = load_image(os.path.join(ASSETS_DIR, "flag.png")) # load in the flag visual
mines_sprite = load_image(os.path.join(ASSETS_DIR, "mines.png"))
# load in the mines visual # load each number visual for possibly 1-8 neighboring mines and build a list
numbers_sprites = {n: load_image(os.path.join(NUM_DIR, f"{n}.png")) for n in range(1, 9)}

# global confetti list
confetti = []

# Button Class
class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=WHITE):
        """Create a button with position, size, colors, and label text."""
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface, font):
        """Draw the button (changes color when hovered)."""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        # Draw rectangle (with hover effect)
        pygame.draw.rect(surface, self.hover_color if is_hovered else self.color, self.rect, border_radius=10)

        # Draw text centered inside the button
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Check if the button is clicked with left mouse button."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# Buttons for the main menu
start_button = Button(WIDTH // 2 - 100, 200, 200, 60, "Start Game", GREEN, (0, 255, 0))  # create sstart button
quit_button = Button(WIDTH // 2 - 100, 280, 200, 60, "Quit", RED, (255, 0, 0))  # create quit button
plus_button = Button(WIDTH // 2 + 60, 360, 60, 60, "+", GRAY, (150, 150, 150))  # create add mine button
minus_button = Button(WIDTH // 2 - 120, 360, 60, 60, "-", GRAY, (150, 150, 150))  # create remove mine button

# define the grid that the thing will be mapped to
grid = [[0 for i in range(10)] for j in range(10)]

# track revealed tiles
revealed = [[False for i in range(10)] for j in range(10)]

# track flagged tiles
flagged = [[False for i in range(10)] for j in range(10)]

counts = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
first_click_done = False

# reset the grid back to the original state
for i in range(10):  # iterate over rows
    for j in range(10):  # iterate over colums
        grid[i][j] = 0  # set value to 0
        revealed[i][j] = False  # set it to not revealed
        flagged[i][j] = False  # set it to not flagged

squarePickList = [0 for i in range(100)]  # allow the board to pick any item to have a mine on it

# put 1 number for every 100 square
for i in range(100):
    squarePickList[i] = i


# converts mouse coordinates to grid positions
def get_grid_pos(mouse_x, mouse_y):
    # converts mouse coordinates to grid positions
    # check if click was in grid area
    if (GRID_START_X <= mouse_x <= GRID_START_X + GRID_SIZE * TILE_SIZE and
            GRID_START_Y <= mouse_y <= GRID_START_Y + GRID_SIZE * TILE_SIZE):

        # calculate which row and column was clicked
        col = (mouse_x - GRID_START_X) // TILE_SIZE
        row = (mouse_y - GRID_START_Y) // TILE_SIZE

        # make sure of valid grid position
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            return row, col
    return None, None  # result if click was out of grid


# function to drawr the grid visuaully so the user can see it
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
                    if n > 0:  # generate a number on tiles that have nearby mines
                        screen.blit(numbers_sprites[n], (x + 10, y + 10))
            else:  # when not revealed tile is gray
                pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE))

            # draw tile border
            pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 2)

            if flagged[row][col] and not revealed[row][col]:
                # load flag sprite when tile is flagged
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
            if start_button.is_clicked(event):
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
                                counts = compute_counts(grid)
                                first_click_done = True
                            if grid[row][col] == MINE:  # Check for loss
                                revealed[row][col] = True
                                reveal_all_mines(grid, revealed)  # reveal all mines on loss
                                state = LOSE
                            else:  # Check win condition
                                flood_reveal(row, col, grid, counts, revealed, flagged)
                                revealed[row][col] = True
                                if check_win(grid, revealed):
                                    state = WIN
                                    start_confetti() # add confetti animation
                    elif event.button == 3:  # a right click
                        # check that the flagged tile isn't revealed
                        if not revealed[row][col]:
                            # if the user has flags flag it but if they don't have flags don't do anything
                            if flagged[row][col]:
                                flagged[row][col] = False
                            elif get_remaining_flags() > 0:
                                flagged[row][col] = True  # flag only if flags remain

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
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 100))

        # Draw buttons
        start_button.draw(screen, small_font)
        quit_button.draw(screen, small_font)
        plus_button.draw(screen, font)
        minus_button.draw(screen, font)

        # Draw counter value in between + and -
        counter_surf = font.render(str(counter_value), True, WHITE)
        screen.blit(counter_surf, (WIDTH // 2 - counter_surf.get_width() // 2, 370))

        # playing status
        playinginfo = small_font.render("Current Status: MENU", True, WHITE)
        screen.blit(playinginfo, (10, 10))

    # What should be displayed during each state
    elif state == PLAYING:
        draw_grid()

        # Instructions
        info_surf = small_font.render("Left click: Reveal | Right click: Flag", True, WHITE)
        screen.blit(info_surf, (10, HEIGHT - 30))

        # playing status
        playinginfo = small_font.render("Current Status: Playing", True, WHITE)
        screen.blit(playinginfo, (10, 10))

        reaming_flags_text = small_font.render(f"Flags Remaining: {get_remaining_flags()}", True, WHITE)
        screen.blit(reaming_flags_text, (550, 10))

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

