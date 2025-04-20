import pygame
from othello import Othello

class LevelMenu:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Reversi - Chọn Cấp Độ")
        self.background = pygame.image.load("assets/img.png")
        self.background = pygame.transform.scale(self.background, (1000, 700))
        self.back_icon = pygame.image.load("assets/back.png")
        self.back_icon = pygame.transform.scale(self.back_icon, (40, 40))
        self.WHITE = (255, 255, 255)
        self.DARK_GREEN = (0, 100, 0)
        self.BLACK = (0, 0, 0)
        self.font = pygame.font.Font(None, 70)
        self.button_font = pygame.font.SysFont("Times New Roman", 20)
        self.title_font = pygame.font.SysFont("Times New Roman", 80, bold=True)
        self.layout_width, self.layout_height = 600, 80
        self.layout_x = (1000 - self.layout_width) // 2
        self.layout_y = 700 - 100
        self.layout_rect = pygame.Rect(self.layout_x, self.layout_y, self.layout_width, self.layout_height)
        self.button_y = self.layout_y + 15
        self.button_width, self.button_height = 180, 50
        self.buttons = [
            {"text": "DỄ", "rect": pygame.Rect(self.layout_x + 10, self.button_y, self.button_width, self.button_height), "mode": "easy"},
            {"text": "BÌNH THƯỜNG", "rect": pygame.Rect(self.layout_x + 210, self.button_y, self.button_width, self.button_height), "mode": "normal"},
            {"text": "KHÓ", "rect": pygame.Rect(self.layout_x + 410, self.button_y, self.button_width, self.button_height), "mode": "hard"},
        ]
        self.back_button = {
            "image": self.back_icon,
            "rect": pygame.Rect(20, 20, 40, 40),
            "hover_rect": pygame.Rect(15, 15, 50, 50)
        }
        self.hovered_button = None
        self.running = True

    def draw_ui(self):
        self.screen.blit(self.background, (0, 0))
        title_surface = self.title_font.render("Chọn Cấp Độ", True, self.WHITE)
        title_rect = title_surface.get_rect(center=(1000 // 2, 100))
        self.screen.blit(title_surface, title_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.layout_rect, border_radius=15)
        for button in self.buttons:
            color = self.DARK_GREEN
            rect = button["rect"]
            if button == self.hovered_button:
                rect = rect.inflate(10, 5)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            text_surface = self.button_font.render(button["text"], True, self.WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
        rect = self.back_button["hover_rect"] if self.back_button == self.hovered_button else self.back_button["rect"]
        self.screen.blit(self.back_button["image"], rect)

    def animate_button(self, button):
        if button == self.back_button:
            original_rect = button["rect"].copy()
            for i in range(5):
                button["rect"].inflate_ip(4, 4)
                self.draw_ui()
                pygame.display.flip()
                pygame.time.delay(20)
            button["rect"] = original_rect
        else:
            original_rect = button["rect"].copy()
            for i in range(5):
                button["rect"].inflate_ip(4, 2)
                self.draw_ui()
                pygame.display.flip()
                pygame.time.delay(20)
            button["rect"] = original_rect

    def run(self):
        while self.running:
            self.draw_ui()
            mouse_pos = pygame.mouse.get_pos()
            self.hovered_button = None
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    self.hovered_button = button
                    break
            if self.back_button["rect"].collidepoint(mouse_pos):
                self.hovered_button = self.back_button
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button["rect"].collidepoint(event.pos):
                            self.animate_button(button)
                            pygame.mixer.music.stop()  # Dừng nhạc trước khi vào game
                            game = Othello(mode=button["mode"])
                            result = game.run()
                            if result == "quit":
                                return "quit"
                            # Nếu result == "main_menu", thoát để quay lại main.py
                            return "main_menu"
                    if self.back_button["rect"].collidepoint(event.pos):
                        self.animate_button(self.back_button)
                        pygame.time.delay(200)
                        return "main_menu"
            pygame.display.flip()
        return "quit"