import pygame
from settings import WHITE, get_current_theme
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

        # Get theme-appropriate colors for gray buttons in light mode
        theme = get_current_theme()
        button_color = self.color
        hover_color = self.hover_color
        
        # If this is a gray button in light theme, use lighter colors
        if (theme['background'] == (245, 245, 220) and  # Light theme
            self.color == (100, 100, 100)):  # Gray button
            button_color = theme['light_button_bg']
            hover_color = theme['light_button_hover']

        # Draw rectangle (with hover effect)
        pygame.draw.rect(surface, hover_color if is_hovered else button_color, self.rect, border_radius=10)

        # Draw text centered inside the button
        text_color = self.text_color if self.text_color != WHITE else get_current_theme()['text']
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Check if the button is clicked with left mouse button."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
