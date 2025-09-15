import pygame

import random #import random to randomly pick mine locations

from collections import deque # Queue for flood-fill

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Menu with Buttons")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 60)      # Bigger font for titles
small_font = pygame.font.Font(None, 36)  # Smaller font for buttons/text

# Game states
MENU = "menu"
PLAYING = "playing"
WIN = "win"
LOSE = "lose"

state = MENU  # start in the main menu
counter_value = 10  # adjustable number in main menu

#grid settings
GRID_SIZE = 10
TILE_SIZE = 40
GRID_START_X = (WIDTH - GRID_SIZE * TILE_SIZE) //2
GRID_START_Y = 50

MINE = 3
DIRS8 = [(-1,-1), (-1,0),(-1,1),
         (0,-1),        (0,1),
         (1,-1), (1,0), (1,1)]

#Sprites
flag_sprite = pygame.image.load("flag.png")

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
start_button = Button(WIDTH//2 - 100, 200, 200, 60, "Start Game", GREEN, (0, 255, 0))
quit_button = Button(WIDTH//2 - 100, 280, 200, 60, "Quit", RED, (255, 0, 0))
plus_button = Button(WIDTH//2 + 60, 360, 60, 60, "+", GRAY, (150, 150, 150))
minus_button = Button(WIDTH//2 - 120, 360, 60, 60, "-", GRAY, (150, 150, 150))

#define the grid that the thing will be mapped to
grid = [[0 for i in range(10)] for j in range(10)]

#track revealed tiles
revealed = [[False for i in range(10)] for j in range(10)]

#track flagged tiles
flagged = [[False for i in range(10)] for j in range(10)]

counts = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
first_click_done = False

#reset the grid back to the original state
for i in range(10):
    for j in range(10):
        grid[i][j] = 0
        revealed[i][j] = False
        flagged[i][j] = False

squarePickList = [0 for i in range(100)]

#put 1 number for every 100 square
for i in range (100):
    squarePickList[i]  = i

def get_grid_pos(mouse_x, mouse_y):
    #converts mouse coordinates to grid positions
    #check if click was in grid area
    if (GRID_START_X <= mouse_x <= GRID_START_X + GRID_SIZE * TILE_SIZE and
        GRID_START_Y <= mouse_y <= GRID_START_Y + GRID_SIZE * TILE_SIZE):

        #calculate which row and column was clicked
        col = (mouse_x - GRID_START_X) // TILE_SIZE
        row = (mouse_y - GRID_START_Y) // TILE_SIZE

        #make sure of valid grid position
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            return row, col
    return None, None  #result if click was out of grid

def draw_grid():
    #draws the grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = GRID_START_X + col * TILE_SIZE
            y = GRID_START_Y + row * TILE_SIZE

            #draw tile background
            if revealed[row][col]:
                if grid[row][col] == MINE:  #tile turns red if revealed tile is a mine
                    pygame.draw.rect(screen, RED, (x, y, TILE_SIZE, TILE_SIZE))
                else: #otherwise the revealed tile turns light gray
                    pygame.draw.rect(screen, LIGHT_GRAY, (x, y, TILE_SIZE, TILE_SIZE))
                    n = counts[row][col] # Show numbers on revealed tiles
                    if n > 0:
                        num_surf = small_font.render(str(n), True, WHITE)
                        screen.blit(num_surf, (x + TILE_SIZE//2 - num_surf.get_width()//2,
                                               y + TILE_SIZE//2 - num_surf.get_height()//2))
            else: #when not revealed tile is gray
                pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE))

            #draw tile border
            pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 2)

            if flagged[row][col] and not revealed[row][col]:
                #load flag sprite when tile is flagged
                if flag_sprite:
                    screen.blit(flag_sprite, (x + 10, y + 10))

# True while cell is inside the 10x10 grid
def in_bounds(r, c):
    return 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE

# Use a matrix of adjacent-mine counts for each cell to show numbers and decide how far to auto-reveal
def compute_counts(grid):
    counts = [[0]*GRID_SIZE for _ in range (GRID_SIZE)]
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == MINE:
                counts[r][c] = -1
                continue
            n = 0
            for dr, dc in DIRS8:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc) and grid[nr][nc] == MINE:
                    n += 1
            counts[r][c] = n
    return counts

# Move the mine in the case it is landed on during the first click
def ensure_first_click_safe(fr, fc, grid):
    if grid[fr][fc] != MINE:
        return
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] != MINE and (r, c) != (fr, fc):
                grid[fr][fc] = 0
                grid[r][c] = MINE
                return

# Reveal the starting cell if its count is 0, breadth-first reveal adjacent zeros and border numbers.
def flood_reveal(sr, sc, grid, counts, revealed, flagged):
    if revealed[sr][sc] or flagged[sr][sc]:
        return
    revealed[sr][sc] = True
    if counts[sr][sc] != 0:
        return
    q = deque([(sr, sc)])
    while q:
        r, c = q.popleft()
        for dr, dc in DIRS8:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            if flagged[nr][nc] or grid[nr][nc] == MINE:
                continue
            if not revealed[nr][nc]:
                revealed[nr][nc] = True
                if counts[nr][nc] == 0:
                    q.append((nr, nc))

# Reveal every mine cell upon loss
def reveal_all_mines(grid, revealed):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == MINE:
                revealed[r][c] = True

# All non-mine tiles are revealed - win condition.
def check_win(grid, revealed):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] != MINE and not revealed[r][c]:
                return False
    return True

# Main Game Loop
running = True
while running:
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
                    #pick a random value
                    randomIndex = random.randrange(len(squarePickList))
                    #remove it so it doesn't get picked again
                    randomValue = squarePickList.pop(randomIndex)
                    #extract the row and column
                    row=randomValue%10
                    column =randomValue//10
                    #print("Row: " , row, " - Coloumn: ", column, " - Item: " , i+1, " - Deleted: " , randomValue, " - Deleted2: " , squarePickList[randomValue-i])
                    #mark the item as a mine
                    grid[row][column] = int(3)

                # Compute numbers for drawing/reveal logic
                counts = compute_counts(grid)
                first_click_done = False

                    #print(grid)

                print(grid)


                #generate a list of squares that can be chosen



            elif quit_button.is_clicked(event):
                running = False  # Quit game

            elif plus_button.is_clicked(event):
                if(counter_value < 20):
                    counter_value += 1  # Increase # bombs in menu

            elif minus_button.is_clicked(event):
                if(counter_value > 10):
                    counter_value -= 1  # Decrease # bombs in menu

        # PLAYING state logic
        elif state == PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos #get coordinates of mouse
                row, col = get_grid_pos(mouse_x, mouse_y) #convert coordinates to grid position

                if row is not None and col is not None: #check if click is in grid
                    if event.button == 1: #a left click
                        if not flagged[row][col]:#can't reveal a flagged tile
                            if not first_click_done: # Ensure a mine isn't initially clicked
                                ensure_first_click_safe(row, col, grid)
                                counts = compute_counts(grid)
                                first_click_done = True
                            if grid[row][col] == MINE: # Check for loss
                                revealed[row][col] = True
                                reveal_all_mines(grid, revealed)
                                state = LOSE
                            else: # Check win condition
                                flood_reveal(row, col, grid, counts, revealed, flagged)
                                revealed[row][col] = True
                                if check_win(grid, revealed):
                                    state = WIN
                    elif event.button == 3:#a right click
                        if not revealed[row][col]:
                            flagged[row][col] = not flagged[row][col]#able to toggle flag

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    state = WIN
                    # Win condition code
                elif event.key == pygame.K_l:
                    state = LOSE
                    # Lose condition code

        # WIN and LOSE state logic
        elif state in [WIN, LOSE]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                state = MENU


                #reset the grid back to the original state
                for i in range(10):
                    for j in range(10):
                        grid[i][j] = 0
                        revealed[i][j] = False
                        flagged[i][j] = False

                #reset the pick list
                squarePickList = [0 for i in range(100)]
                for i in range (100):
                    squarePickList[i]  = i

                # Reset mine counts
                counts = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]

                # Reset first click check
                first_click_done = False

                # Code here to reset values when going back to the menu

    # Drawing (depends on state)
    # Where the game should be drawn, visuals and images
    if state == MENU:
        # Title
        title_surf = font.render("Minesweeper", True, WHITE)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 100))

        # Draw buttons
        start_button.draw(screen, small_font)
        quit_button.draw(screen, small_font)
        plus_button.draw(screen, font)
        minus_button.draw(screen, font)

        # Draw counter value in between + and -
        counter_surf = font.render(str(counter_value), True, WHITE)
        screen.blit(counter_surf, (WIDTH//2 - counter_surf.get_width()//2, 370))

    # What should be displayed during each state
    elif state == PLAYING:
        draw_grid()

        # Instructions
        info_surf = small_font.render("Left click: Reveal | Right click: Flag | W: Win | L: Lose", True, WHITE)
        screen.blit(info_surf, (10, HEIGHT - 30))

    elif state == WIN:
        win_surf = font.render("You Win!", True, GREEN)
        screen.blit(win_surf, (WIDTH//2 - win_surf.get_width()//2, HEIGHT//2))

        info_surf = small_font.render("Click anywhere to return to Menu", True, WHITE)
        screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, HEIGHT//2 + 50))

    elif state == LOSE:
        lose_surf = font.render("You Lose!", True, RED)
        screen.blit(lose_surf, (WIDTH//2 - lose_surf.get_width()//2, HEIGHT//2))

        info_surf = small_font.render("Click anywhere to return to Menu", True, WHITE)
        screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, HEIGHT//2 + 50))

    # Update screen
    pygame.display.flip()

# Exit
pygame.quit()

