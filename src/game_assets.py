import os
import pygame
from settings import ASSETS_DIR, NUM_DIR


def load_image(path):
    image = pygame.image.load(path).convert_alpha()
    return image

# Convert visual assets to pygame surface

# Sprites
flag_sprite = load_image(os.path.join(ASSETS_DIR, "images", "flag.png")) # load in the flag visual
mines_sprite = load_image(os.path.join(ASSETS_DIR, "images", "mines.png")) # load in the mines visual
# load in the mines visual # load each number visual for possibly 1-8 neighboring mines and build a list
numbers_sprites = {n: load_image(os.path.join(NUM_DIR, f"{n}.png")) for n in range(1, 9)}