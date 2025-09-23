import pygame
from settings import WHITE
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
