import pygame
import random
import copy

# Cấu hình chung
class Config:
    AI_DELAY = {"easy": 500, "normal": 500, "hard": 1000}
    MINIMAX_DEPTH = 6

# Utility functions
def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    validdirections = []
    if x != minX: validdirections.append((x-1, y))
    if x != minX and y != minY: validdirections.append((x-1, y-1))
    if x != minX and y != maxY: validdirections.append((x-1, y+1))
    if x!= maxX: validdirections.append((x+1, y))
    if x != maxX and y != minY: validdirections.append((x+1, y-1))
    if x != maxX and y != maxY: validdirections.append((x+1, y+1))
    if y != minY: validdirections.append((x, y-1))
    if y != maxY: validdirections.append((x, y+1))
    return validdirections

def loadImages(path, size):
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img, size)
    return img

def evaluateBoard(grid, player, grid_obj):
    score = 0
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    edges = [(x, y) for x in range(8) for y in range(8) if (x in (0, 7) or y in (0, 7)) and (x, y) not in corners]

    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            if col == player:
                score += 1
                if (y, x) in corners:
                    score += 20
                elif (y, x) in edges:
                    score += 5
            elif col == -player:
                score -= 1
                if (y, x) in corners:
                    score -= 20
                elif (y, x) in edges:
                    score -= 5

    player_moves = len(grid_obj.findAvailMoves(grid, player))
    opponent_moves = len(grid_obj.findAvailMoves(grid, -player))
    score += (player_moves - opponent_moves) * 2
    return score

class Othello:
    def __init__(self, mode="normal"):
        pygame.init()
        self.config = Config()
        self.mode = mode

        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound("assets/soundnd.mp3")

        self.player_avatar = pygame.image.load("assets/player.png")
        self.player_avatar = pygame.transform.scale(self.player_avatar, (50, 50))
        self.AI_avatar = pygame.image.load("assets/AI.png")
        self.AI_avatar = pygame.transform.scale(self.AI_avatar, (50, 50))

        self.quit_button = pygame.Rect(750, 570, 150, 60)
        self.restart_button = pygame.Rect(750, 490, 150, 60)
        self.button_font = pygame.font.SysFont('Times New Roman', 28, True, False)
        self.label_font = pygame.font.SysFont('Times New Roman', 32, True, False)

        self.confirm_restart = False

        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption(f'Othello - Chế độ {self.mode.capitalize()}')
        self.background = pygame.image.load("assets/img.png")
        self.background = pygame.transform.scale(self.background, (1000, 700))

        self.player1 = 1
        self.player2 = -1
        self.currentPlayer = 1
        self.time = 0
        self.rows = 8
        self.columns = 8
        self.gameOver = False

        self.cell_size = (80, 80)
        self.grid = Grid(self.rows, self.columns, self.cell_size, self)
        self.computerPlayer = ComputerPlayer(self.grid, self.mode)
        self.RUN = True

    def run(self):
        while self.RUN:
            result = self.input()
            if result == "main_menu":
                return "main_menu"
            if result == "quit":
                self.RUN = False

            self.update()
            self.draw()
        pygame.quit()
        return "quit"

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.quit_button.collidepoint(mouse_pos):
                    return "main_menu"

                elif self.restart_button.collidepoint(mouse_pos) and not self.confirm_restart:
                    self.confirm_restart = True
                    return

                if self.confirm_restart:
                    if self.yes_button.collidepoint(mouse_pos):
                        self.reset_game()
                        self.confirm_restart = False
                    elif self.no_button.collidepoint(mouse_pos):
                        self.confirm_restart = False
                    return

                if self.gameOver:
                    if 300 <= mouse_pos[0] <= 500 and 350 <= mouse_pos[1] <= 400:
                        self.reset_game()
                        return

                elif event.button == 3:
                    self.grid.printGameLogicBoard()

                elif event.button == 1 and self.currentPlayer == 1:
                    x, y = mouse_pos
                    if 50 <= x < 50 + self.columns * self.cell_size[0] and 30 <= y < 30 + self.rows * self.cell_size[1]:
                        col, row = (x - 50) // self.cell_size[0], (y - 30) // self.cell_size[1]
                        validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                        if validCells and (row, col) in validCells:
                            self.make_move(row, col)

    def reset_game(self):
        self.grid.newGame()
        self.currentPlayer = self.player1
        self.gameOver = False
        self.time = pygame.time.get_ticks()
        self.grid.player1Score = 2
        self.grid.player2Score = 2

    def make_move(self, row, col):
        self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, row, col)
        swappableTiles = self.grid.swappableTiles(row, col, self.grid.gridLogic, self.currentPlayer)

        self.move_sound.play()

        for tile in swappableTiles:
            self.grid.animateTransitions(tile, self.currentPlayer)
            self.grid.gridLogic[tile[0]][tile[1]] = self.currentPlayer
        self.currentPlayer *= -1
        self.time = pygame.time.get_ticks()

    def update(self):
        if not self.gameOver:
            new_time = pygame.time.get_ticks()
            availMoves = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
            if self.currentPlayer == -1 and new_time - self.time >= self.config.AI_DELAY[self.mode]:
                if not availMoves:
                    self.currentPlayer *= -1
                    availMoves = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                    if not availMoves:
                        self.gameOver = True
                    return
                cell = self.computerPlayer.get_move(self.grid.gridLogic, self.currentPlayer, self.mode)
                if cell:
                    self.make_move(cell[0], cell[1])
                else:
                    self.currentPlayer *= -1
            elif not availMoves:
                self.currentPlayer *= -1
                availMoves = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                if not availMoves:
                    self.gameOver = True
        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)

    def draw_confirm_dialog(self):
        overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        dialog_rect = pygame.Rect(300, 250, 400, 200)
        pygame.draw.rect(self.screen, (50, 50, 70), dialog_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 120), dialog_rect, 3, border_radius=10)

        font = pygame.font.SysFont('Times New Roman', 28, True, False)
        text = font.render("Bạn có chắc muốn chơi lại?", True, (255, 255, 255))
        self.screen.blit(text, (500 - text.get_width() // 2, 300))

        self.yes_button = pygame.Rect(400, 350, 80, 50)
        pygame.draw.rect(self.screen, (70, 70, 70), self.yes_button.move(2, 2), border_radius=10)
        pygame.draw.rect(self.screen, (100, 200, 100), self.yes_button, border_radius=10)
        yes_text = font.render("Có", True, (255, 255, 255))
        self.screen.blit(yes_text, (440 - yes_text.get_width() // 2, 365))

        self.no_button = pygame.Rect(520, 350, 80, 50)
        pygame.draw.rect(self.screen, (70, 70, 70), self.no_button.move(2, 2), border_radius=10)
        pygame.draw.rect(self.screen, (200, 100, 100), self.no_button, border_radius=10)
        no_text = font.render("Không", True, (255, 255, 255))
        self.screen.blit(no_text, (560 - no_text.get_width() // 2, 365))

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Draw board with shadow
        shadow_board = pygame.Rect(55, 35, 640, 640)
        pygame.draw.rect(self.screen, (50, 50, 50), shadow_board, border_radius=10)
        self.grid.drawGrid(self.screen)

        # Draw info panel with semi-transparent background
        shadow_panel = pygame.Rect(705, 35, 250, 640)
        pygame.draw.rect(self.screen, (50, 50, 50), shadow_panel, border_radius=20)
        info_panel = pygame.Rect(700, 30, 250, 640)
        panel_surface = pygame.Surface((250, 640), pygame.SRCALPHA)
        panel_surface.fill((255, 255, 255, 230))
        self.screen.blit(panel_surface, (700, 30))
        pygame.draw.rect(self.screen, (200, 200, 200), info_panel, 2, border_radius=20)

        # Computer info (top)
        panel_center_x = 825  # Center of the panel (700 + 250/2)
        self.screen.blit(self.AI_avatar, (panel_center_x - self.AI_avatar.get_width() // 2, 80))
        if self.currentPlayer == -1:  # AI's turn
            pygame.draw.circle(self.screen, (0, 200, 0), (740, 105), 14)
        computer_text = self.label_font.render("Computer", True, (0, 0, 0))
        self.screen.blit(computer_text, (panel_center_x - computer_text.get_width() // 2, 140))
        black_score = self.grid.drawScore('Black', self.grid.player2Score)
        self.screen.blit(black_score, (panel_center_x - black_score.get_width() // 2, 180))

        # Divider line
        pygame.draw.line(self.screen, (200, 200, 200), (720, 260), (930, 260), 2)

        # Player info (middle)
        self.screen.blit(self.player_avatar, (panel_center_x - self.player_avatar.get_width() // 2, 280))
        if self.currentPlayer == 1:  # Player's turn
            pygame.draw.circle(self.screen, (0, 200, 0), (740, 305), 14)
        player_text = self.label_font.render("Player", True, (0, 0, 0))
        self.screen.blit(player_text, (panel_center_x - player_text.get_width() // 2, 340))
        white_score = self.grid.drawScore('White', self.grid.player1Score)
        self.screen.blit(white_score, (panel_center_x - white_score.get_width() // 2, 380))

        # Draw Restart and Quit buttons (bottom)
        mouse_pos = pygame.mouse.get_pos()
        restart_color = (0, 180, 0) if self.restart_button.collidepoint(mouse_pos) else (0, 200, 0)
        quit_color = (180, 180, 180) if self.quit_button.collidepoint(mouse_pos) else (200, 200, 200)

        pygame.draw.rect(self.screen, (50, 50, 50), self.restart_button.move(4, 4), border_radius=10)
        pygame.draw.rect(self.screen, restart_color, self.restart_button, border_radius=10)
        restart_text = self.button_font.render("Restart", True, (255, 255, 255))
        self.screen.blit(restart_text, (panel_center_x - restart_text.get_width() // 2, 505))

        pygame.draw.rect(self.screen, (50, 50, 50), self.quit_button.move(4, 4), border_radius=10)
        pygame.draw.rect(self.screen, quit_color, self.quit_button, border_radius=10)
        quit_text = self.button_font.render("Quit", True, (0, 0, 0))
        self.screen.blit(quit_text, (panel_center_x - quit_text.get_width() // 2, 585))

        if self.confirm_restart:
            self.draw_confirm_dialog()
        pygame.display.update()

class Grid:
    def __init__(self, rows, columns, size, main):
        self.GAME = main
        self.y = rows
        self.x = columns
        self.size = size
        self.whitetoken = loadImages('assets/WhiteToken.png', size)
        self.blacktoken = loadImages('assets/BlackToken.png', size)
        self.transitionWhiteToBlack = [loadImages(f'assets/BlackToWhite{i}.png', self.size) for i in range(1, 4)]
        self.transitionBlackToWhite = [loadImages(f'assets/WhiteToBlack{i}.png', self.size) for i in range(1, 4)]
        self.bg = self.loadBackGroundImages()

        self.tokens = {}
        self.gridBg = self.createbgimg()
        self.gridLogic = self.regenGrid(self.y, self.x)

        self.player1Score = 0
        self.player2Score = 0
        self.font = pygame.font.SysFont('Times New Roman', 28, True, False)

    def newGame(self):
        self.tokens.clear()
        self.gridLogic = self.regenGrid(self.y, self.x)
        self.player1Score = 2
        self.player2Score = 2

    def loadBackGroundImages(self):
        green_surface = pygame.Surface(self.size)
        green_surface.fill((0, 80, 0))
        return {'green': green_surface}

    def createbgimg(self):
        image = pygame.Surface((self.x * self.size[0], self.y * self.size[1]))
        for j in range(self.y):
            for i in range(self.x):
                image.blit(self.bg['green'], (i * self.size[0], j * self.size[1]))
                pygame.draw.rect(image, (0, 0, 0), (i * self.size[0], j * self.size[1], self.size[0], self.size[1]), 2)
        return image

    def regenGrid(self, rows, columns):
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)
        self.insertToken(grid, 1, 3, 3)
        self.insertToken(grid, -1, 3, 4)
        self.insertToken(grid, 1, 4, 4)
        self.insertToken(grid, -1, 4, 3)
        return grid

    def calculatePlayerScore(self, player):
        score = 0
        for row in self.gridLogic:
            for col in row:
                if col == player:
                    score += 1
        return score

    def drawScore(self, player, score):
        textImg = self.font.render(f'Score: {score}', True, (0, 0, 0))
        return textImg

    def endScreen(self):
        if self.GAME.gameOver:
            endScreenImg = pygame.Surface((400, 200))
            endScreenImg.fill((50, 50, 50))

            if self.player1Score > self.player2Score:
                result_text = "Player (White) Wins!"
            elif self.player2Score > self.player1Score:
                result_text = "AI (Black) Wins!"
            else:
                result_text = "It's a Tie!"

            font_large = pygame.font.SysFont('Times New Roman', 30, True, False)
            font_small = pygame.font.SysFont('Times New Roman', 24, True, False)

            result = font_large.render(result_text, True, (255, 255, 255))
            score_text = font_small.render(f"White: {self.player1Score}  -  Black: {self.player2Score}", True, (255, 255, 255))

            new_game_btn = pygame.Rect(120, 120, 160, 50)
            pygame.draw.rect(endScreenImg, (70, 70, 70), new_game_btn.move(2, 2), border_radius=10)
            pygame.draw.rect(endScreenImg, (0, 200, 0), new_game_btn, border_radius=10)
            new_game_text = font_small.render("Play Again", True, (255, 255, 255))

            endScreenImg.blit(result, (200 - result.get_width() // 2, 40))
            endScreenImg.blit(score_text, (200 - score_text.get_width() // 2, 80))
            endScreenImg.blit(new_game_text, (200 - new_game_text.get_width() // 2, 135))

            return endScreenImg
        return None

    def drawGrid(self, window):
        window.blit(self.gridBg, (50, 30))

        for token in self.tokens.values():
            token.draw(window)

        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        if self.GAME.currentPlayer == 1:
            for move in availMoves:
                s = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 255, 128), (20, 20), 20)
                window.blit(s, (50 + (move[1] * self.size[0]) + 20, 30 + (move[0] * self.size[1]) + 20))

        if self.GAME.gameOver:
            end_screen = self.endScreen()
            if end_screen:
                window.blit(end_screen, (300, 250))

    def printGameLogicBoard(self):
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.gridLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()

    def findValidCells(self, grid, curPlayer):
        validCellToClick = []
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                if grid[gridX][gridY] != 0:
                    continue
                DIRECTIONS = directions(gridX, gridY)

                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]

                    if checkedCell == 0 or checkedCell == curPlayer:
                        continue

                    if (gridX, gridY) in validCellToClick:
                        continue

                    validCellToClick.append((gridX, gridY))
        return validCellToClick

    def swappableTiles(self, x, y, grid, player):
        surroundCells = directions(x, y)
        if len(surroundCells) == 0:
            return []

        swappableTiles = []
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            difX, difY = checkX - x, checkY - y
            currentLine = []

            RUN = True
            while RUN:
                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    RUN = False
                    continue
                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))
                elif grid[checkX][checkY] == player:
                    if currentLine:
                        swappableTiles.extend(currentLine)
                    RUN = False
                else:
                    currentLine.clear()
                    RUN = False
                checkX += difX
                checkY += difY

        return swappableTiles

    def findAvailMoves(self, grid, currentPlayer):
        validCells = self.findValidCells(grid, currentPlayer)
        playableCells = []

        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue
            swapTiles = self.swappableTiles(x, y, grid, currentPlayer)

            if len(swapTiles) > 0:
                playableCells.append(cell)

        return playableCells

    def insertToken(self, grid, curplayer, y, x):
        tokenImage = self.whitetoken if curplayer == 1 else self.blacktoken
        self.tokens[(y, x)] = Token(curplayer, y, x, tokenImage, self.GAME)
        grid[y][x] = self.tokens[(y, x)].player

    def animateTransitions(self, cell, player):
        if player == 1:
            self.tokens[(cell[0], cell[1])].transition(self.transitionWhiteToBlack, self.whitetoken)
        else:
            self.tokens[(cell[0], cell[1])].transition(self.transitionBlackToWhite, self.blacktoken)

class Token:
    def __init__(self, player, gridX, gridY, image, main):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = 50 + (gridY * main.cell_size[0])
        self.posY = 30 + (gridX * main.cell_size[1])
        self.GAME = main
        self.image = image

    def transition(self, transitionImages, tokenImage):
        for i in range(30):
            self.image = transitionImages[i // 10]
            self.GAME.draw()
        self.image = tokenImage

    def draw(self, window):
        window.blit(self.image, (self.posX, self.posY))

class ComputerPlayer:
    def __init__(self, gridObject, mode):
        self.grid = gridObject
        self.mode = mode

    def random_move(self, grid, player):
        availMoves = self.grid.findAvailMoves(grid, player)
        if availMoves:
            return random.choice(availMoves)
        return None

    def greedy_move(self, grid, player):
        availMoves = self.grid.findAvailMoves(grid, player)
        if not availMoves:
            return None
        best_move = None
        max_flips = -1
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        for move in availMoves:
            x, y = move
            flips = len(self.grid.swappableTiles(x, y, grid, player))
            if (flips > max_flips) or (flips == max_flips and (x, y) in corners):
                max_flips = flips
                best_move = move
        return best_move

    def minimax_move(self, grid, depth, alpha, beta, player):
        availMoves = self.grid.findAvailMoves(grid, player)
        if depth == 0 or not availMoves:
            return None, evaluateBoard(grid, player, self.grid)

        if player < 0:
            bestScore = -float('inf')
            bestMove = None
            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, grid, player)
                if not swappableTiles:
                    continue
                grid[x][y] = player
                old_values = [(tile[0], tile[1], grid[tile[0]][tile[1]]) for tile in swappableTiles]
                for tile in swappableTiles:
                    grid[tile[0]][tile[1]] = player
                _, value = self.minimax_move(grid, depth-1, alpha, beta, -player)
                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                grid[x][y] = 0
                for tile_x, tile_y, old_val in old_values:
                    grid[tile_x][tile_y] = old_val
                if beta <= alpha:
                    break
            return bestMove, bestScore
        else:
            bestScore = float('inf')
            bestMove = None
            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, grid, player)
                if not swappableTiles:
                    continue
                grid[x][y] = player
                old_values = [(tile[0], tile[1], grid[tile[0]][tile[1]]) for tile in swappableTiles]
                for tile in swappableTiles:
                    grid[tile[0]][tile[1]] = player
                _, value = self.minimax_move(grid, depth-1, alpha, beta, -player)
                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                grid[x][y] = 0
                for tile_x, tile_y, old_val in old_values:
                    grid[tile_x][tile_y] = old_val
                if beta <= alpha:
                    break
            return bestMove, bestScore

    def get_move(self, grid, player, mode):
        newGrid = copy.deepcopy(grid)
        if mode == "easy":
            return self.random_move(newGrid, player)
        elif mode == "normal":
            return self.greedy_move(newGrid, player)
        else:
            move, _ = self.minimax_move(newGrid, self.grid.GAME.config.MINIMAX_DEPTH, -float('inf'), float('inf'), player)
            return move

if __name__ == "__main__":
    game = Othello()
    game.run()