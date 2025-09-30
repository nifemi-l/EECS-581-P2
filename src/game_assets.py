import os
import random
import pygame
from settings import ASSETS_DIR, NUM_DIR, SOUND_DIR 
from PIL import Image, ImageDraw


def load_image(path):
    image = pygame.image.load(path).convert_alpha()
    return image

# Convert visual assets to pygame surface

# Sprites
flag_sprite = load_image(os.path.join(ASSETS_DIR, "images", "flag.png")) # load in the flag visual
mines_sprite = load_image(os.path.join(ASSETS_DIR, "images", "mines.png")) # load in the mines visual
# load in the mines visual # load each number visual for possibly 1-8 neighboring mines and build a list
numbers_sprites = {n: load_image(os.path.join(NUM_DIR, f"{n}.png")) for n in range(1, 9)}


def load_circular_profile(image_path, diameter):
    """Load an image w/ Pillow, resize, apply a circular alpha mask, and return a pygame Surface."""
    try:
        # Open the image file and make sure it has an alpha channel
        img = Image.open(image_path).convert("RGBA")
    except Exception:
        # If the image can't be loaded, just return None
        return None

    try:
        # Resize the image to a square with the given diameter
        img = img.resize((diameter, diameter), Image.LANCZOS)

        # Create a new mask (black by default)
        mask = Image.new("L", (diameter, diameter), 0)
        # Get a drawing context for the mask
        draw = ImageDraw.Draw(mask)
        # Draw a white circle that fills the mask
        draw.ellipse((0, 0, diameter, diameter), fill=255)
        # Apply the mask to the image as its alpha channel
        img.putalpha(mask)

        # Get the mode (should be RGBA)
        mode = img.mode
        # Get the size (width, height)
        size = img.size
        # Get the raw bytes of the image
        data = img.tobytes()
        # Turn the image data into a pygame Surface with alpha
        surface = pygame.image.fromstring(data, size, mode).convert_alpha()
        # Return the finished surface
        return surface
    except Exception:
        # If anything goes wrong, return None
        return None
