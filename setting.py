import pygame
import os

class SettingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.WIDTH, self.HEIGHT = 1000, 700
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BUTTON_GREEN = (30, 100, 60)
        self.HOVER_GREEN = (50, 140, 80)
        self.SLIDER_COLOR = (50, 150, 50)
        self.SLIDER_HANDLE_COLOR = (100, 200, 100)

        self.font_title = pygame.font.SysFont('arial', 64, bold=True)
        self.font_text = pygame.font.SysFont('arial', 20)

        self.background = pygame.image.load("assets/img.png")
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))

        self.sound_icon = pygame.image.load("assets/sound.png")
        self.sound_icon = pygame.transform.scale(self.sound_icon, (50, 50))

        self.panel_rect = pygame.Rect(self.WIDTH // 2 - 300, 480, 600, 120)
        self.sound_rect = pygame.Rect(self.panel_rect.left + 80, self.panel_rect.top + 50, 50, 50)
        self.back_rect = pygame.Rect(self.panel_rect.right - 180, self.panel_rect.top + 50, 100, 50)

        self.slider_width = 250
        self.slider_height = 10
        self.slider_x = 340
        self.slider_y = 555

        self.slider_rect = pygame.Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height)
        self.slider_handle_rect = pygame.Rect(self.slider_x, self.slider_y - 5, 20, 20)

        self.volume = self.load_volume()
        pygame.mixer.music.set_volume(self.volume / 100)

    def load_volume(self):
        if os.path.exists("volume.txt"):
            try:
                with open("volume.txt", "r") as f:
                    vol = int(f.read())
                    return max(0, min(vol, 100))
            except:
                return 50
        return 50

    def save_volume(self):
        with open("volume.txt", "w") as f:
            f.write(str(self.volume))

    def run(self):
        running = True
        while running:
            self.screen.blit(self.background, (0, 0))
            pygame.draw.rect(self.screen, self.WHITE, self.panel_rect, border_radius=20)

            setting_text = self.font_text.render("Setting", True, self.BLACK)
            self.screen.blit(setting_text, (self.WIDTH // 2 - setting_text.get_width() // 2, self.panel_rect.top + 10))

            self.screen.blit(self.sound_icon, self.sound_rect.topleft)

            mouse_pos = pygame.mouse.get_pos()
            color = self.HOVER_GREEN if self.back_rect.collidepoint(mouse_pos) else self.BUTTON_GREEN
            pygame.draw.rect(self.screen, color, self.back_rect, border_radius=10)
            back_text = self.font_text.render("Back", True, self.WHITE)
            self.screen.blit(back_text, (self.back_rect.x + 35, self.back_rect.y + 10))

            pygame.draw.rect(self.screen, self.SLIDER_COLOR, self.slider_rect)

            self.slider_handle_rect.x = self.slider_rect.left + (self.volume / 100) * self.slider_rect.width - self.slider_handle_rect.width // 2
            pygame.draw.rect(self.screen, self.SLIDER_HANDLE_COLOR, self.slider_handle_rect)

            volume_text = self.font_text.render(f"Volume: {self.volume}%", True, self.BLACK)
            self.screen.blit(volume_text, (self.WIDTH // 2 - volume_text.get_width() // 2, self.slider_rect.top - 40))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.sound_rect.collidepoint(event.pos):
                        print("Toggled sound!")
                    elif self.back_rect.collidepoint(event.pos):
                        self.save_volume()
                        return "main_menu"
                    elif self.slider_rect.collidepoint(event.pos):
                        self.volume = int((event.pos[0] - self.slider_rect.left) / self.slider_rect.width * 100)
                        self.volume = max(0, min(self.volume, 100))
                        pygame.mixer.music.set_volume(self.volume / 100)

                elif event.type == pygame.MOUSEMOTION:
                    if event.buttons[0] == 1 and self.slider_rect.collidepoint(event.pos):
                        self.volume = int((event.pos[0] - self.slider_rect.left) / self.slider_rect.width * 100)
                        self.volume = max(0, min(self.volume, 100))
                        pygame.mixer.music.set_volume(self.volume / 100)

            pygame.display.flip()
