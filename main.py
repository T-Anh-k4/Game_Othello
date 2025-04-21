import os

import pygame
import sys
from level import LevelMenu
from setting import SettingScreen

class MainMenu:
    def __init__(self):
        pygame.init()
        volume = 50
        if os.path.exists("volume.txt"):
            try:
                with open("volume.txt", "r") as f:
                    volume = int(f.read())
                    volume = max(0, min(volume, 100))
            except:
                volume = 50
        pygame.mixer.music.load("assets/theme.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("Reversi")
        self.background = pygame.image.load("assets/img.png")
        self.background = pygame.transform.scale(self.background, (1000, 700))
        self.WHITE = (255, 255, 255)
        self.DARK_GREEN = (0, 100, 0)
        self.BLACK = (0, 0, 0)
        self.LIGHT_GRAY = (220, 220, 220)
        self.font = pygame.font.Font(None, 70)
        self.button_font = pygame.font.SysFont("Times New Roman", 20)
        self.level_font = pygame.font.SysFont("Times New Roman", 50)
        self.layout_width, self.layout_height = 600, 80
        self.layout_x = (1000 - self.layout_width) // 2
        self.layout_y = 700 - 100
        self.layout_rect = pygame.Rect(self.layout_x, self.layout_y, self.layout_width, self.layout_height)
        self.button_y = self.layout_y + 15
        self.button_width, self.button_height = 180, 50
        self.buttons = [
            {"text": "CHƠI MỚI", "rect": pygame.Rect(self.layout_x + 10, self.button_y, self.button_width, self.button_height)},
            {"text": "CÀI ĐẶT", "rect": pygame.Rect(self.layout_x + 210, self.button_y, self.button_width, self.button_height)},
            {"text": "THOÁT", "rect": pygame.Rect(self.layout_x + 410, self.button_y, self.button_width, self.button_height)},
        ]
        self.circle_radius = 30
        self.circle_x, self.circle_y = 1000 - 50, 50
        self.hovered_button = None
        self.running = True

    def draw_ui(self):
        self.screen.blit(self.background, (0, 0))
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
        pygame.draw.circle(self.screen, self.DARK_GREEN, (self.circle_x, self.circle_y), self.circle_radius)
        help_text = self.button_font.render("?", True, self.WHITE)
        self.screen.blit(help_text, help_text.get_rect(center=(self.circle_x, self.circle_y)))

    def show_help(self):
        help_screen = True
        while help_screen:
            self.screen.fill(self.WHITE)
            pygame.draw.rect(self.screen, self.LIGHT_GRAY, (100, 50, 1000 - 200, 700 - 150), border_radius=20)
            help_text = self.level_font.render("Hướng dẫn chơi Reversi", True, self.BLACK)
            self.screen.blit(help_text, (1000 // 2 - help_text.get_width() // 2, 70))
            rules = [
                "1. Trò chơi Othello (Reversi) chơi trên bàn cờ 8x8.",
                "2. Hai người chơi lần lượt đặt quân cờ (đen và trắng).",
                "3. Khi đặt quân, nếu kẹp quân đối phương giữa quân của mình thì tất cả quân ",
                "kẹp giữa sẽ bị lật màu thành quân của bạn.",
                "4. Nếu một người chơi không có nước đi hợp lệ, lượt sẽ chuyển cho đối thủ.",
                "5. Trò chơi kết thúc khi bàn cờ đầy hoặc không ai có thể đi thêm.",
                "6. Người có nhiều quân cờ nhất khi kết thúc sẽ chiến thắng."
            ]
            y_offset = 150
            x_offset = 120
            for rule in rules:
                if rule[0].isdigit():
                    rule_text = self.button_font.render(rule, True, self.BLACK)
                    self.screen.blit(rule_text, (x_offset, y_offset))
                else:
                    rule_text = self.button_font.render(rule, True, self.BLACK)
                    self.screen.blit(rule_text, (x_offset + 30, y_offset))
                y_offset += 40
            back_text = self.button_font.render("Nhấn ESC để quay lại", True, self.DARK_GREEN)
            self.screen.blit(back_text, (1000 // 2 - back_text.get_width() // 2, 700 - 150))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    help_screen = False

    def run(self):
        while self.running:
            self.draw_ui()
            mouse_pos = pygame.mouse.get_pos()
            self.hovered_button = None
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    self.hovered_button = button
                    break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (event.pos[0] - self.circle_x) ** 2 + (event.pos[1] - self.circle_y) ** 2 <= self.circle_radius ** 2:
                        self.show_help()
                    for button in self.buttons:
                        if button["rect"].collidepoint(event.pos):
                            if button["text"] == "THOÁT":
                                self.running = False
                            elif button["text"] == "CHƠI MỚI":
                                level_menu = LevelMenu(self.screen)
                                result = level_menu.run()
                                if result == "quit":
                                    self.running = False
                                elif result == "main_menu":
                                    pygame.mixer.music.play(-1)
                            elif button["text"] == "CÀI ĐẶT":
                                setting_screen = SettingScreen(self.screen)
                                result = setting_screen.run()
                                if result == "quit":
                                    self.running = False
                                # elif result == "main_menu":
                                #     pygame.mixer.music.play(-1)
            pygame.display.flip()
        return "quit"

if __name__ == "__main__":
    try:
        menu = MainMenu()
        menu.run()
    finally:
        pygame.quit()
        sys.exit()