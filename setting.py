import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reversi - Setting")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_GREEN = (30, 100, 60)
HOVER_GREEN = (50, 140, 80)
SLIDER_COLOR = (50, 150, 50)
SLIDER_HANDLE_COLOR = (100, 200, 100)

# Fonts
font_title = pygame.font.SysFont('arial', 64, bold=True)
font_text = pygame.font.SysFont('arial', 20)

# Load images
background = pygame.image.load("assets/img.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

sound_icon = pygame.image.load("assets/sound.png")
sound_icon = pygame.transform.scale(sound_icon, (50, 50))

# Rects
panel_rect = pygame.Rect(WIDTH//2 - 300, 480, 600, 120)
sound_rect = pygame.Rect(panel_rect.left + 80, panel_rect.top + 50, 50, 50)
back_rect = pygame.Rect(panel_rect.right - 180, panel_rect.top + 50, 100, 50)

# Volume slider settings
slider_width = 250
slider_height = 10
slider_x = 340
slider_y = 555

slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
slider_handle_rect = pygame.Rect(slider_x, slider_y - 5, 20, 20)

volume = 50  # Volume level (0 to 100)

# Main loop
running = True
while running:
    screen.blit(background, (0, 0))

    # Draw bottom white rounded panel
    pygame.draw.rect(screen, WHITE, panel_rect, border_radius=20)

    # Draw "Setting" text centered
    setting_text = font_text.render("Setting", True, BLACK)
    screen.blit(setting_text, (WIDTH // 2 - setting_text.get_width() // 2, panel_rect.top + 10))

    # Draw sound icon
    screen.blit(sound_icon, sound_rect.topleft)

    # Draw "Back" button
    mouse_pos = pygame.mouse.get_pos()
    color = HOVER_GREEN if back_rect.collidepoint(mouse_pos) else BUTTON_GREEN
    pygame.draw.rect(screen, color, back_rect, border_radius=10)
    back_text = font_text.render("Back", True, WHITE)
    screen.blit(back_text, (back_rect.x + 35, back_rect.y + 10))

    # Draw volume slider background
    pygame.draw.rect(screen, SLIDER_COLOR, slider_rect)

    # Draw volume slider handle (position it according to the volume value)
    slider_handle_rect.x = slider_rect.left + (volume / 100) * slider_rect.width - slider_handle_rect.width // 2
    pygame.draw.rect(screen, SLIDER_HANDLE_COLOR, slider_handle_rect)

    # Draw the current volume value text
    volume_text = font_text.render(f"Volume: {volume}%", True, BLACK)
    screen.blit(volume_text, (WIDTH // 2 - volume_text.get_width() // 2, slider_rect.top - 40))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if sound_rect.collidepoint(event.pos):
                print("Toggled sound!")
            elif back_rect.collidepoint(event.pos):
                print("Back to menu...")
                running = False
            elif slider_rect.collidepoint(event.pos):  # Check if mouse is clicked on slider
                volume = int((event.pos[0] - slider_rect.left) / slider_rect.width * 100)
                volume = max(0, min(volume, 100))  # Ensure volume is between 0 and 100

        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] == 1 and slider_rect.collidepoint(event.pos):  # Mouse drag on the slider
                volume = int((event.pos[0] - slider_rect.left) / slider_rect.width * 100)
                volume = max(0, min(volume, 100))  # Ensure volume is between 0 and 100

    pygame.display.flip()

pygame.quit()
sys.exit()
