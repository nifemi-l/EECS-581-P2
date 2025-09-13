import pygame

import random #import random to randomly pick mine locations



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

#reset the grid back to the orinogal state
for i in range(10):
    for j in range(10):
        grid[i][j] = 0

squarePickList = [0 for i in range(100)]

#put 1 number for every 100 square
for i in range (100):
    squarePickList[i]  = i

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


                #reset the grid back to the orinogal state
                for i in range(10):
                    for j in range(10):
                        grid[i][j] = 0

                #reset the pick list
                squarePickList = [0 for i in range(100)]
                for i in range (100):
                    squarePickList[i]  = i                        



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
        play_surf = font.render("Game Playing...", True, WHITE)
        screen.blit(play_surf, (WIDTH//2 - play_surf.get_width()//2, HEIGHT//2))

        info_surf = small_font.render("Press W to Win, L to Lose", True, GREEN)
        screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, HEIGHT//2 + 50))

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
