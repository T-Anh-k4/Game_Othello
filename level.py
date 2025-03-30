import pygame
import subprocess
import sys
import os
# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reversi")

# Tải ảnh nền
background = pygame.image.load("assets/img.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Tải ảnh nút quay về (thay thế bằng đường dẫn hình ảnh của bạn)
back_icon = pygame.image.load("assets/back.png")
back_icon = pygame.transform.scale(back_icon, (40, 40))  # Điều chỉnh kích thước


# Màu sắc
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)
BLACK = (0, 0, 0)

# Font chữ
font = pygame.font.Font(None, 70)
button_font = pygame.font.SysFont("Times New Roman", 20)
level_font = pygame.font.SysFont("Times New Roman", 50)

# Tạo vùng layout trắng bao quanh nút
layout_width, layout_height = 600, 80
layout_x = (WIDTH - layout_width) // 2
layout_y = HEIGHT - 100
layout_rect = pygame.Rect(layout_x, layout_y, layout_width, layout_height)

# Tạo nút (di chuyển xuống dưới trong layout trắng)
button_y = layout_y + 15  # Đặt nút trong layout trắng
button_width, button_height = 180, 50
button_spacing = 30  # Khoảng cách giữa các nút

buttons = [
    {"text": "DỄ", "rect": pygame.Rect(layout_x + 10, button_y, button_width, button_height)},
    {"text": "BÌNH THƯỜNG", "rect": pygame.Rect(layout_x + 210, button_y, button_width, button_height)},
    {"text": "KHÓ", "rect": pygame.Rect(layout_x + 410, button_y, button_width, button_height)},
]

# Tạo nút quay về bằng hình ảnh
back_button = {
    "image": back_icon,
    "rect": pygame.Rect(20, 20, 40, 40),  # Kích thước phù hợp với icon
    "hover_rect": pygame.Rect(15, 15, 50, 50)  # Kích thước khi hover
}

hovered_button = None


def draw_ui():
    screen.blit(background, (0, 0))

    # Vẽ layout trắng
    pygame.draw.rect(screen, WHITE, layout_rect, border_radius=15)

    # Vẽ các nút level
    for button in buttons:
        color = DARK_GREEN
        rect = button["rect"]
        if button == hovered_button:
            rect = rect.inflate(10, 5)  # Phóng to khi hover
        pygame.draw.rect(screen, color, rect, border_radius=10)
        text_surface = button_font.render(button["text"], True, WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    # Vẽ nút quay về (icon)
    rect = back_button["hover_rect"] if back_button == hovered_button else back_button["rect"]
    screen.blit(back_button["image"], rect)


def animate_button(button):
    if button == back_button:
        # Animation riêng cho nút hình ảnh
        original_rect = button["rect"].copy()
        for i in range(5):
            button["rect"].inflate_ip(4, 4)
            draw_ui()
            pygame.display.flip()
            pygame.time.delay(20)
        button["rect"] = original_rect
    else:
        # Animation cho các nút thông thường
        original_rect = button["rect"].copy()
        for i in range(5):
            button["rect"].inflate_ip(4, 2)
            draw_ui()
            pygame.display.flip()
            pygame.time.delay(20)
        button["rect"] = original_rect


def main():
    global hovered_button
    running = True
    while running:
        draw_ui()
        mouse_pos = pygame.mouse.get_pos()
        hovered_button = None

        # Kiểm tra hover cho các nút level
        for button in buttons:
            if button["rect"].collidepoint(mouse_pos):
                hovered_button = button
                break

        # Kiểm tra hover cho nút quay về
        if back_button["rect"].collidepoint(mouse_pos):
            hovered_button = back_button

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Kiểm tra click vào các nút level
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        animate_button(button)
                        if button["text"] == "DỄ":
                            subprocess.run(["python", "othello.py"])  # Chạy game Othello
                        elif button["text"] == "BÌNH THƯỜNG":
                            # Thêm code cho mức độ bình thường
                            pass
                        elif button["text"] == "KHÓ":
                            # Thêm code cho mức độ khó
                            pass

                # Kiểm tra click vào nút quay về
                if back_button["rect"].collidepoint(event.pos):
                    animate_button(back_button)
                    pygame.time.delay(200)  # Chờ animation hoàn thành
                    pygame.display.quit()
                    subprocess.run(["python", "main.py"])  # Chạy lại file main.py
                    running = False  # Đóng cửa sổ hiện tại

        pygame.display.flip()

    pygame.quit()

def start_new_program(program_name):
    """Hàm hỗ trợ khởi chạy chương trình mới"""
    pygame.display.quit()  # Đóng display hiện tại
    try:
        # Sử dụng sys.executable để đảm bảo chạy cùng phiên bản Python
        subprocess.Popen([sys.executable, program_name])
    except Exception as e:
        print(f"Không thể khởi chạy {program_name}: {e}")
    finally:
        sys.exit(0)



if __name__ == "__main__":
    main()