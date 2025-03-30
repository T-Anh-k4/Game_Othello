import pygame
import subprocess

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reversi")

# Tải ảnh nền
background = pygame.image.load("assets/img.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Màu sắc
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)


# Font chữ
font = pygame.font.Font(None, 70)
button_font = pygame.font.SysFont("Times New Roman", 20)
level_font = pygame.font.SysFont("Times New Roman", 50)


# Layout trắng chứa nút
layout_width, layout_height = 600, 80
layout_x = (WIDTH - layout_width) // 2
layout_y = HEIGHT - 100
layout_rect = pygame.Rect(layout_x, layout_y, layout_width, layout_height)

# Nút menu
button_y = layout_y + 15  # Đặt nút trong layout trắng
button_width, button_height = 180, 50
button_spacing = 30  # Khoảng cách giữa các nút

buttons = [
    {"text": "CHƠI MỚI", "rect": pygame.Rect(layout_x + 10, button_y, button_width, button_height)},
    {"text": "CÀI ĐẶT", "rect": pygame.Rect(layout_x + 210, button_y, button_width, button_height)},
    {"text": "THOÁT", "rect": pygame.Rect(layout_x + 410, button_y, button_width, button_height)},
]

hovered_button = None

# Nút tròn (Hướng dẫn)
circle_radius = 30
circle_x, circle_y = WIDTH - 50, 50


def draw_ui():
    screen.blit(background, (0, 0))

    # Vẽ layout trắng
    pygame.draw.rect(screen, WHITE, layout_rect, border_radius=15)

    # Vẽ các nút
    for button in buttons:
        color = DARK_GREEN
        rect = button["rect"]
        if button == hovered_button:
            rect = rect.inflate(10, 5)  # Phóng to khi hover
        pygame.draw.rect(screen, color, rect, border_radius=10)
        text_surface = button_font.render(button["text"], True, WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    # Vẽ nút tròn hướng dẫn
    pygame.draw.circle(screen, DARK_GREEN, (circle_x, circle_y), circle_radius)
    help_text = button_font.render("?", True, WHITE)
    screen.blit(help_text, help_text.get_rect(center=(circle_x, circle_y)))


def show_help():
    help_screen = True
    while help_screen:
        screen.fill(WHITE)

        # Vẽ nền xám nhạt để dễ nhìn
        pygame.draw.rect(screen, LIGHT_GRAY, (100, 50, WIDTH - 200, HEIGHT - 150), border_radius=20)

        help_text = level_font.render("Hướng dẫn chơi Reversi", True, BLACK)
        screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, 70))

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
        x_offset = 120  # Đặt khoảng cách lề trái cố định để căn chỉnh số thứ tự

        for rule in rules:
            if rule[0].isdigit():  # Nếu là dòng bắt đầu bằng số, canh lề trái cố định
                rule_text = button_font.render(rule, True, BLACK)
                screen.blit(rule_text, (x_offset, y_offset))
            else:  # Nếu là dòng mô tả tiếp theo, lùi vào một chút
                rule_text = button_font.render(rule, True, BLACK)
                screen.blit(rule_text, (x_offset + 30, y_offset))
            y_offset += 40

        back_text = button_font.render("Nhấn ESC để quay lại", True, DARK_GREEN)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 150))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                help_screen = False


def main():
    global hovered_button
    running = True
    while running:
        draw_ui()
        mouse_pos = pygame.mouse.get_pos()
        hovered_button = None

        for button in buttons:
            if button["rect"].collidepoint(mouse_pos):
                hovered_button = button
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (event.pos[0] - circle_x) ** 2 + (event.pos[1] - circle_y) ** 2 <= circle_radius ** 2:
                    show_help()
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["text"] == "THOÁT":
                            running = False
                        elif button["text"] == "CHƠI MỚI":
                            pygame.quit()
                            subprocess.run(["python", "level.py"])


        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
