import pygame
import sys
pygame.init()

WINDOW_SIZE = (650, 550)
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Drawing Board")

penColor = (0, 0, 0)
penSize = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLOR_INACTIVE = pygame.Color("lightskyblue3")
COLOR_ACTIVE = pygame.Color("dodgerblue2")

penTool = pygame.image.load("pen.png")
penTool = pygame.transform.scale(penTool, (50, 50))

eraserTool = pygame.image.load("eraser.png")
eraserTool = pygame.transform.scale(eraserTool, (30, 30))

class Board:
    def __init__(self, surface, toolbar):
        self.surface = surface
        self.toolbar = toolbar
        self.pen = Pen(self.surface, penColor, penSize)
        self.mode = None

    def penMode(self, mouseX, mouseY):
        self.mode = "pen"
        self.pen.draw(mouseX, mouseY, self.toolbar, self.pen.color, self.pen.size)

    def clicked(self, mouseX, mouseY, button, drawings):
        if button.text == "Pen":
            self.penMode(mouseX, mouseY)
        elif button.text == "Erase":
            self.mode = "eraser"
        elif button.text == "Clear":
            self.mode = "clear"
            drawings.clear()
            self.penMode(mouseX, mouseY)

class Pen:
    def __init__(self, surface, color, size):
        self.surface = surface
        self.color = color
        self.size = size

    def draw(self, x, y, toolbar, color, size):
        if not(toolbar.x <= x <= toolbar.x+toolbar.width and toolbar.y <= y <= toolbar.y+toolbar.height):
            pygame.draw.rect(self.surface, color, (x, y, size, size))

    def setSize(self, size):
        self.size = size

    def setColor(self, color):
        self.color = color


class Button:
    def __init__(self, surface, color, x, y, width, height, fontSize, text):
        self.surface = surface
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fontSize = fontSize
        self.text = text
        self.font = pygame.font.SysFont("comicsans", fontSize)
        self.rect = pygame.Rect(x, y, width, height)

    def display(self):
        self.rect = pygame.draw.rect(self.surface, self.color, (self.x, self.y, self.width, self.height))
        self.surface.blit(self.font.render(self.text, True, (0, 0, 0)),
                          (self.x + self.fontSize - len(self.text), self.y + self.fontSize//10))


class Entry:
    def __init__(self, surface, color, x, y, width, height, fontSize, fontColor):
        self.surface = surface
        self.color = color
        self.x = x
        self.y = y
        self.originalWidth = width
        self.width = width
        self.height = height
        self.fontSize = fontSize
        self.fontColor = fontColor
        self.clicked = False
        self.text = ""
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont("Arial", fontSize)
        self.text_surface = self.font.render(self.text, True, fontColor)
        self.MAX_SIZE = 50

    def display(self):
        pygame.draw.rect(self.surface, self.color, (self.x, self.y, self.width, self.height), 3)
        self.surface.blit(self.text_surface, (self.x+5, self.y))

    def updateText(self, key):
        self.text += chr(key)
        self.set_text_surface()
        width = max(self.width, self.text_surface.get_width()+10)
        self.width = width

    def backspace(self):
        self.text = self.text[:-1]
        self.set_text_surface()

    def set_text_surface(self):
        self.text_surface = self.text_surface = self.font.render(self.text, True, self.fontColor)

    def sendText(self, board):
        if self.text.isnumeric():
            int_text = int(self.text)
            if int_text > self.MAX_SIZE:
                self.text = str(self.MAX_SIZE)
                self.set_text_surface()
                self.width = self.originalWidth
                board.pen.size = self.MAX_SIZE
            elif int_text < 1:
                self.text = "1"
                self.set_text_surface()
                board.pen.size = 1
            else:
                board.pen.size = int_text
        else:
            self.text = ""
            self.set_text_surface()
            self.width = self.originalWidth
        board.mode = "pen"

    def keyPressed(self, key, board):
        try:
            if key == pygame.K_BACKSPACE:
                self.backspace()
            elif key == pygame.K_RETURN:
                self.sendText(board)
            else:
                self.updateText(key)
        except ValueError:
            pass

class ToolBar:
    def __init__(self, surface, color, x, y, width, height):
        self.surface = surface
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_palette = []
        self.colors = [(255, 0, 0), (255, 180, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255),
                       (128, 0, 128), (255, 100, 200), (0, 0, 0), (123, 63, 0)]
        self.penSizeEntry = Entry(self.surface, COLOR_INACTIVE, 20, self.y + (self.height-40),
                                  100, 30, 25, (0, 0, 255))
        self.board = None
        self.font = pygame.font.SysFont("Arial", 15)

    def display(self, buttons):
        self.color_palette.clear()
        pygame.draw.rect(self.surface, self.color, (self.x, self.y, self.width, self.height))

        for button in buttons:
            button.display()
            buttonX = button.x
            buttonY = button.y
            buttonWidth = button.width

        x = buttonX+buttonWidth+50
        y = buttonY
        for index, color in enumerate(self.colors):
            rect = pygame.draw.rect(self.surface, color, (x, y, 20, 20))
            self.color_palette.append(rect)
            x += 25
            if (index+1) % 3 == 0:
                x = buttonX+buttonWidth+50
                y += 25

        self.surface.blit(self.font.render("Pen Size:", True, (0, 0, 0)),
                          (20, self.penSizeEntry.y - self.penSizeEntry.height + 8))
        self.penSizeEntry.display()

    def color_clicked(self, color):
        self.board.pen.color = color

    def checkEntryClick(self, pos):
        if self.penSizeEntry.rect.collidepoint(pos):
            self.penSizeEntry.clicked = True
            self.penSizeEntry.color = COLOR_ACTIVE

        else:
            self.penSizeEntry.clicked = False
            self.penSizeEntry.color = COLOR_INACTIVE

    def get_board(self, board):
        self.board = board


def set_cursor(surface, board, toolbar):
    mouseX, mouseY = pygame.mouse.get_pos()
    if not(toolbar.x <= mouseX <= toolbar.x + toolbar.width and
           toolbar.y <= mouseY <= toolbar.y + toolbar.height):
        pygame.mouse.set_visible(False)
        if board.mode == "pen":
            surface.blit(penTool, (mouseX, mouseY-(penSize+10)))
        elif board.mode == "eraser":
            surface.blit(eraserTool, (mouseX, mouseY))
        elif board.mode is None:
            pygame.mouse.set_visible(True)
    else:
        pygame.mouse.set_visible(True)


def main():
    width, height = (WINDOW_SIZE[0], 150)
    toolbar = ToolBar(window, (210, 210, 210), 0, WINDOW_SIZE[1]-height, width, height, )
    drawings = []

    board = Board(window, toolbar)
    toolbar.get_board(board)

    buttonsAttributes = ({"text": "Pen", "x":20},
                         {"text": "Erase", "x":180},
                         {"text": "Clear", "x": 340})
    buttons = []
    for button in buttonsAttributes:
        b = Button(window, WHITE, button["x"], toolbar.y + toolbar.height//5.5, 133, 53, 35,
                   button["text"])
        buttons.append(b)

    pen = board.pen

    running = True
    while running:
        window.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:
                mouse = pygame.mouse.get_pos()
                toolbar.checkEntryClick(mouse)
                if board.mode == "pen":
                    drawings.append([mouse, pen.color, pen.size])
                elif board.mode == "eraser":
                    for d, c, s in drawings:
                        if mouse[0] <= d[0] <= mouse[0]+pen.size and mouse[1] <= d[1] <= mouse[1]+pen.size:
                            drawings.remove([d, c, s])

            if event.type == pygame.MOUSEBUTTONDOWN:
                toolbar.checkEntryClick(event.pos)
                for index, button in enumerate(buttons):
                    if button.rect.collidepoint(event.pos):
                        mouseX, mouseY = pygame.mouse.get_pos()
                        board.clicked(mouseX, mouseY, button, drawings)

                for index, color in enumerate(toolbar.color_palette):
                    if color.collidepoint(event.pos):
                        board.mode = "pen"
                        toolbar.color_clicked(toolbar.colors[index])

            if event.type == pygame.KEYDOWN:
                if toolbar.penSizeEntry.clicked:
                    toolbar.penSizeEntry.keyPressed(event.key, board)

        for drawing, color, size in drawings:
            pen.draw(drawing[0], drawing[1], toolbar, color, size)

        set_cursor(window, board, toolbar)

        toolbar.display(buttons)
        pygame.display.update()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
