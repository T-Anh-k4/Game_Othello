import pygame # type: ignore
import random
import copy

#  utility functions
def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    """Check to determine which directions are valid from current cell"""
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
    """Load an image into the game, and scale the image"""
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img, size)
    return img

def loadSpriteSheet(sheet, row, col, newSize, size):
    """creates an empty surface, loads a portion of the spritesheet onto the surface, then return that surface as img"""
    image = pygame.Surface((32, 32)).convert_alpha()
    image.blit(sheet, (0, 0), (row * size[0], col * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, newSize)
    image.set_colorkey('Black')
    return image

def evaluateBoard(grid, player):
    score = 0
    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            score -= col
    return score


class Othello:
    def __init__(self):
        pygame.init()
        self.player_avatar = pygame.image.load("assets/player.png")
        self.player_avatar = pygame.transform.scale(self.player_avatar, (80, 50))

        self.AI_avatar = pygame.image.load("assets/AI.png")
        self.AI_avatar = pygame.transform.scale(self.AI_avatar, (80, 50))

        # Tạo nút Quit và Restart
        self.quit_button = pygame.Rect(870, 600, 150, 50)
        self.restart_button = pygame.Rect(870, 670, 150, 50)
        self.button_font = pygame.font.SysFont('Times New Roman', 20, True, False)

        self.confirm_restart = False

        self.screen = pygame.display.set_mode((1100, 800))
        pygame.display.set_caption('Othello')

        self.player1 = 1
        self.player2 = -1
        self.currentPlayer = 1
        self.time = 0
        self.rows = 8
        self.columns = 8
        self.gameOver = False

        self.grid = Grid(self.rows, self.columns, (80, 80), self)
        self.computerPlayer = ComputerPlayer(self.grid)
        self.RUN = True

    def run(self):
        while self.RUN:
            result = self.input()
            if result == "main_menu":
                pygame.quit()  # Đóng pygame trước khi quay về
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
                return "quit"  # Trả về 'quit' để thoát hoàn toàn

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Xử lý nút Quit
                if self.quit_button.collidepoint(mouse_pos):
                    return "main_menu"

                    # Xử lý nút Restart
                elif self.restart_button.collidepoint(mouse_pos) and not self.confirm_restart:
                    self.confirm_restart = True
                    return

                # Xử lý hộp thoại xác nhận Restart
                if self.confirm_restart:
                    if self.yes_button.collidepoint(mouse_pos):
                        self.reset_game()
                        self.confirm_restart = False
                    elif self.no_button.collidepoint(mouse_pos):
                        self.confirm_restart = False
                    return

                # Xử lý game over và nút Play Again
                if self.gameOver:
                    # Kiểm tra xem click có trong vùng nút Play Again không
                    if 350 <= mouse_pos[0] <= 550 and 420 <= mouse_pos[1] <= 470:
                        self.reset_game()
                        return

                # Phần xử lý click chuột bình thường
                elif event.button == 3:  # Right click
                    self.grid.printGameLogicBoard()

                elif event.button == 1 and self.currentPlayer == 1:  # Left click
                    x, y = mouse_pos
                    if 80 <= x < 80 + self.columns * 80 and 80 <= y < 80 + self.rows * 80:
                        col, row = (x - 80) // 80, (y - 80) // 80
                        validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                        if validCells and (row, col) in validCells:
                            self.make_move(row, col)

    def reset_game(self):
        """Reset game về trạng thái ban đầu"""
        self.grid.newGame()
        self.currentPlayer = self.player1
        self.gameOver = False
        self.time = pygame.time.get_ticks()
        self.grid.player1Score = 2  # Reset điểm về giá trị ban đầu
        self.grid.player2Score = 2

    def make_move(self, row, col):
        """Xử lý một nước đi hợp lệ"""
        self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, row, col)
        swappableTiles = self.grid.swappableTiles(row, col, self.grid.gridLogic, self.currentPlayer)
        for tile in swappableTiles:
            self.grid.animateTransitions(tile, self.currentPlayer)
            self.grid.gridLogic[tile[0]][tile[1]] *= -1
        self.currentPlayer *= -1
        self.time = pygame.time.get_ticks()

    def update(self):
        if self.currentPlayer == -1 and not self.gameOver:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.gameOver = True
                    return

                cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, 5, -64, 64, -1)
                self.make_move(cell[0], cell[1])

        # Cập nhật điểm và kiểm tra kết thúc game
        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)
        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
            self.gameOver = True

    def draw_confirm_dialog(self):
        # Tạo overlay mờ
        overlay = pygame.Surface((1100, 800), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # Vẽ hộp thoại
        dialog_rect = pygame.Rect(350, 300, 400, 200)
        pygame.draw.rect(self.screen, (50, 50, 70), dialog_rect)
        pygame.draw.rect(self.screen, (100, 100, 120), dialog_rect, 3)

        # Vẽ text
        font = pygame.font.SysFont('Times New Roman', 24, True, False)
        text = font.render("Bạn có chắc muốn chơi lại?", True, (255, 255, 255))
        self.screen.blit(text, (550 - text.get_width() // 2, 350))

        # Vẽ nút Yes
        self.yes_button = pygame.Rect(450, 400, 80, 50)
        pygame.draw.rect(self.screen, (100, 200, 100), self.yes_button)
        yes_text = font.render("Có", True, (255, 255, 255))
        self.screen.blit(yes_text, (490 - yes_text.get_width() // 2, 415))

        # Vẽ nút No
        self.no_button = pygame.Rect(570, 400, 80, 50)
        pygame.draw.rect(self.screen, (200, 100, 100), self.no_button)
        no_text = font.render("Không", True, (255, 255, 255))
        self.screen.blit(no_text, (610 - no_text.get_width() // 2, 415))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)

        # Vẽ avatar
        self.screen.blit(self.player_avatar, (895, 420))
        self.screen.blit(self.AI_avatar, (895, 150))

        # Xác định màu nút (có hover hay không)
        mouse_pos = pygame.mouse.get_pos()
        quit_color = (200, 0, 0) if self.quit_button.collidepoint(mouse_pos) else (255, 0, 0)
        restart_color = (0, 200, 0) if self.restart_button.collidepoint(mouse_pos) else (0, 255, 0)

        # Vẽ nút Quit
        pygame.draw.rect(self.screen, quit_color, self.quit_button)
        quit_text = self.button_font.render("Thoát", True, (255, 255, 255))
        self.screen.blit(quit_text, (925, 615))

        # Vẽ nút Restart
        pygame.draw.rect(self.screen, restart_color, self.restart_button)
        restart_text = self.button_font.render("Chơi lại", True, (255, 255, 255))
        self.screen.blit(restart_text, (915, 685))

        # Vẽ hộp thoại xác nhận nếu cần
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

        self.font = pygame.font.SysFont('Times New Roman', 20, True, False)

    def newGame(self):
        """Khởi tạo lại game mới"""
        self.tokens.clear()  # Xóa tất cả các quân cờ
        self.gridLogic = self.regenGrid(self.y, self.x)  # Tạo lại bàn cờ
        self.player1Score = 2  # Đặt lại điểm số
        self.player2Score = 2

    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        spriteSheet = pygame.image.load('assets/wood.png').convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j]+str(i)] = loadSpriteSheet(spriteSheet, j, i, (self.size), (32, 32))
        return imageDict

    def createbgimg(self):
        gridBg = [
            ['C0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'E0'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'E2'],
        ]
        image = pygame.Surface((960, 960))
        for j, row in enumerate(gridBg):
            for i, img in enumerate(row):
                image.blit(self.bg[img], (i * self.size[0], j * self.size[1]))
        return image

    def regenGrid(self, rows, columns):
        """generate an empty grid for logic use"""
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
        textImg = self.font.render(f'{player} : {score}', 1, 'White')
        return textImg

    def endScreen(self):
        if self.GAME.gameOver:
            # Tạo surface cho màn hình kết thúc
            endScreenImg = pygame.Surface((400, 200))
            endScreenImg.fill((50, 50, 50))

            # Xác định người thắng
            if self.player1Score > self.player2Score:
                result_text = "Player (White) Wins!"
            elif self.player2Score > self.player1Score:
                result_text = "AI (Black) Wins!"
            else:
                result_text = "It's a Tie!"

            # Hiển thị kết quả và điểm số
            font_large = pygame.font.SysFont('Arial', 30, True, False)
            font_small = pygame.font.SysFont('Arial', 24, True, False)

            result = font_large.render(result_text, True, (255, 255, 255))
            score_text = font_small.render(f"White: {self.player1Score}  -  Black: {self.player2Score}", True,
                                           (255, 255, 255))

            # Vẽ nút Play Again
            new_game_btn = pygame.Rect(120, 120, 160, 50)
            pygame.draw.rect(endScreenImg, (0, 200, 0), new_game_btn)
            new_game_text = font_small.render("Play Again", True, (0, 0, 0))

            # Đặt vị trí các thành phần
            endScreenImg.blit(result, (200 - result.get_width() // 2, 40))
            endScreenImg.blit(score_text, (200 - score_text.get_width() // 2, 80))
            endScreenImg.blit(new_game_text, (200 - new_game_text.get_width() // 2, 135))

            return endScreenImg
        return None

    def drawGrid(self, window):
        window.blit(self.gridBg, (0, 0))

        window.blit(self.drawScore('White', self.player1Score), (900, 500))
        window.blit(self.drawScore('Black', self.player2Score), (900, 100))

        for token in self.tokens.values():
            token.draw(window)

        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        if self.GAME.currentPlayer == 1:
            for move in availMoves:
                pygame.draw.rect(window, 'White', (80 + (move[1] * 80) + 30, 80 + (move[0] * 80) + 30, 20, 20))

        if self.GAME.gameOver:
            # Hiển thị màn hình kết thúc ở giữa màn hình
            end_screen = self.endScreen()
            if end_screen:
                window.blit(end_screen, (350, 300))

    def printGameLogicBoard(self):
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.gridLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()

    def findValidCells(self, grid, curPlayer):
        """Performs a check to find all empty cells that are adjacent to opposing player"""
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
                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))
                elif grid[checkX][checkY] == player:
                    RUN = False
                    break
                elif grid[checkX][checkY] == 0:
                    currentLine.clear()
                    RUN = False
                checkX += difX
                checkY += difY

                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    RUN = False

            if len(currentLine) > 0:
                swappableTiles.extend(currentLine)

        return swappableTiles

    def findAvailMoves(self, grid, currentPlayer):
        """Takes the list of validCells and checks each to see if playable"""
        validCells = self.findValidCells(grid, currentPlayer)
        playableCells = []

        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue
            swapTiles = self.swappableTiles(x, y, grid, currentPlayer)

            #if len(swapTiles) > 0 and cell not in playableCells:
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
        self.posX = 80 + (gridY * 80)
        self.posY = 80 + (gridX * 80)
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
    def __init__(self, gridObject):
        self.grid = gridObject

    def computerHard(self, grid, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        #if depth == 0:
        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, evaluateBoard(grid, player)
            return bestMove, Score

        #if len(availMoves) == 0:
        #    bestMove, Score = None, evaluateBoard()
        #    return bestMove, Score

        if player < 0:
            bestScore = -64
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.computerHard(newGrid, depth-1, alpha, beta, player *-1)

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player > 0:
            bestScore = 64
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.computerHard(newGrid, depth-1, alpha, beta, player)

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

if __name__ == '__main__':
    game = Othello()
    game.run()
    pygame.quit()