import random, os, time, json, cProfile, pygame
from colorama import Fore, Back, Style

#constants
USE_OPTIMISED_GET_TILE = True
#Optmised method 71.28% faster than non optimised
#OLD - 30x30 - 15.39
#NEW - 30x30 - 4.42
USE_OPTIMISED_GET_LOWEST_ENTROPY = True

WINDOW_WIDTH = 550
WINDOW_HEIGHT = 550

BOARD_SIZE = [32, 22]
#"example": ["top", "right", "bottom", "left"]
CHAR_DATA = {    
    "║" : [1, 0, 1, 0],
    "╔" : [0, 1, 1, 0],
    "╗" : [0, 0, 1, 1],
    "╚" : [1, 1, 0, 0],
    "╝" : [1, 0, 0, 1],
    "╬" : [1, 1, 1, 1],
    "╠" : [1, 1, 1, 0],
    "╣" : [1, 0, 1, 1],
    "═" : [0, 1, 0, 1],
    "╦" : [0, 1, 1, 1],
    "╩" : [1, 1, 0, 1],
    " " : [0, 0, 0, 0]
    }
CHARS = list(CHAR_DATA.keys())
DIR_COMPLEMENTS = {
    0 : 2,
    1 : 3,
    2 : 0,
    3 : 1
    }
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
COLOUR_THRESHOLD = {
    0.7 : Fore.RED,
    0.5 : Fore.LIGHTRED_EX,
    0.3 : Fore.YELLOW,
    0 : Fore.GREEN
    }

COLOURS = {
    Fore.RED: (255, 0, 0),
    Fore.LIGHTRED_EX: (227, 72, 86),
    Fore.YELLOW: (193, 156, 0),
    Fore.GREEN: (0, 255, 0)
    }

WEIGHTS = {
    "║" : 0.8,
    "╔" : 0.1,
    "╗" : 0.1,
    "╚" : 0.1,
    "╝" : 0.1,
    "╬" : 0.1,
    "╠" : 0.1,
    "╣" : 0.1,
    "═" : 0.8,
    "╦" : 0.1,
    "╩" : 0.1,
    " " : 0.8
}

CHAR_W = 0
CHAR_H = 0
pygame.font.init()
FONT = pygame.font.SysFont("consolas", 20)

EntropyDict = {}

#functions
def GetClosestColour(possibilities):
    perc = (possibilities/ len(CHARS))
    for thresh in COLOUR_THRESHOLD:
        if perc >= thresh:
            return COLOUR_THRESHOLD[thresh]

def AllCollapsed(board):
    for tile in board:
        if type(tile) != int and not tile.collapsed:
           return False
    return True

def EvenMoreOptimisedGetLowestEntropy(board):
    lowestTiles = [tile for tile in EntropyDict[board[-1]] if not tile.collapsed]
    while lowestTiles == []:
        board[-1] += 1
        lowestTiles = [tile for tile in EntropyDict[board[-1]] if not tile.collapsed]
    return lowestTiles

def OptimisedGetLowestEntropy(board):
    lowest = 100
    lowestTiles = []
    for tile in board:
       if type(tile) != int:
            if len(tile.possibilities) <= lowest and not tile.collapsed:
                lowest = len(tile.possibilities)
                lowestTiles.append(tile)
    return [tile for tile in lowestTiles if len(tile.possibilities) == lowest]

def GetLowestEntropy(board):
    lowest = 100
    lowestTiles = []
    for tile in board:
        if len(tile.possibilities) < lowest and len(tile.possibilities) >= 1 and not tile.collapsed:
            lowest = len(tile.possibilities)
    for tile in board:
        if len(tile.possibilities) == lowest:
            lowestTiles.append(tile)
    return lowestTiles

def CreateBoard(size_X, size_Y):
    tiles = []
    for x in range(size_X):
        for y in range(size_Y):
            tiles.append(Tile(x, y))
    return tiles

def GetPossible(tile):
    tile.possibleConnections = {0:[],1:[],2:[],3:[]}
    for char in tile.possibilities:
        for i, dir in enumerate(CHAR_DATA[char]):
            for possibleTile in CHAR_DATA.keys():
                data = CHAR_DATA[possibleTile]
                if data[DIR_COMPLEMENTS[i]] == dir:
                    tile.possibleConnections[i].append(possibleTile)

def GetTile(x, y, board, debug=False):
    if USE_OPTIMISED_GET_TILE:
        if x >= 0 and x < BOARD_SIZE[0] and y >= 0 and y < BOARD_SIZE[1]:
            index = (x*BOARD_SIZE[1]) + y
            return board[index]
        else:
            if debug: print(x, y)
    else:
        for i, tile in enumerate(board):
            if tile.x == x and tile.y == y:
                return tile
    return False

def DrawBoard(board):
    if not pygameVis:
        for y in range(BOARD_SIZE[1]):
            print("".join(str(GetTile(x, y, board)) for x in range(BOARD_SIZE[0])))
    else:
        dis.fill(0)
        for tile in board:
            if type(tile) != int:
                s = FONT.render(str(tile), False, COLOURS[GetClosestColour(len(tile.possibilities))])
                if s.get_height() == 23:
                    dis.blit(s, ((tile.x*CHAR_W) + CHAR_W/2, (tile.y*2*CHAR_W) - 3))
                else:
                    dis.blit(s, ((tile.x*CHAR_W) + CHAR_W/2, (tile.y*2*CHAR_W)))
        pygame.display.flip()
        
        pass


def Propagate(x, y, board, debug=False):
    stack = [GetTile(x, y, board)]
    while len(stack) > 0:
        original = stack[0]
        GetPossible(original)
        del stack[0]

        for i, dir in enumerate(DIRS):
            AdjX = original.x + dir[0]
            AdjY = original.y + dir[1]
            adjacentTile = GetTile(AdjX, AdjY, board)
            if debug: print(dir, adjacentTile, AdjX, AdjY, original.x, original.y)
            if adjacentTile != False:
                possibilites = len(adjacentTile.possibilities)
                adjacentTile.possibilities = [state for state in adjacentTile.possibilities if state in original.possibleConnections[i]]
                if debug: print(original.possibleConnections[i])
                newPossibilites = len(adjacentTile.possibilities)
                if possibilites > newPossibilites:
                    stack.append(adjacentTile)
                    EntropyDict[possibilites].remove(adjacentTile)
                    EntropyDict[newPossibilites].append(adjacentTile)
                    if newPossibilites < board[-1]:
                        board[-1] = newPossibilites
        if debug:
            DrawBoard(board)
            print(len(stack))
            input()
      
def GetWeights(possibilities):
    return [WEIGHTS[state] for state in possibilities]

#classes
class Tile:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.possibilities = CHARS
        self.collapsedState = None
        self.collapsed = False
    def Collapse(self):
        self.collapsedState = random.choices(self.possibilities, GetWeights(self.possibilities))[0]
        self.possibilities = [self.collapsedState]
        self.collapsed = True
    def CollapseTo(self, state):
        if state in self.possibilities:
            self.collapsedState = state
            self.possibilities = [self.collapsedState]
            self.collapsed = True
    def __str__(self):
        if self.collapsedState == None:
            possibilities = len(self.possibilities)
            if pygameVis:
                return str(hex(possibilities))[2:]
            return GetClosestColour(possibilities) + str(hex(possibilities))[2:]
        else:
            if pygameVis:
                return self.collapsedState
            return Fore.GREEN + self.collapsedState + Style.RESET_ALL



pygameVis = input("Use pygame visualisation (y/n): ").lower().startswith("y")

dis = None


if pygameVis:
    import pygame
    pygame.init()
    pygame.font.init()
    dis = pygame.display.set_mode((400,400))
    for char in CHARS:
        print(char, str(FONT.render(char, True, (255, 255, 255)).get_height()))
    s = FONT.render(" ", True, (255, 255, 255))
    CHAR_W = s.get_width()
    CHAR_H = 20
    pygame.display.flip()



if input("Use custom size (y/n): ").lower().startswith("y"):
    print(Fore.RED + "WARNING:" + Style.RESET_ALL + " Bigger values will make the generation take longer")
    BOARD_SIZE[0] = int(input("X size (int): "))
    BOARD_SIZE[1] = int(input("Y size (int): "))
    if pygameVis:
        if BOARD_SIZE[0] * CHAR_W > WINDOW_WIDTH:
            BOARD_SIZE[0] = WINDOW_WIDTH // CHAR_W
        if BOARD_SIZE[1] * CHAR_H > WINDOW_HEIGHT:
            BOARD_SIZE[1] = WINDOW_HEIGHT // CHAR_H

board = CreateBoard(BOARD_SIZE[0], BOARD_SIZE[1])

#Setup for lowest Entropy
board.append(100)

GetPossible(GetTile(0,0,board))
InitiallyPossible = GetTile(0,0,board).possibleConnections

for i in range(1, len(GetTile(0,0,board).possibilities) + 1):
    EntropyDict[i] = []



for tile in board:
    if tile != 100:
        tile.possibleConnections = InitiallyPossible
        EntropyDict[len(tile.possibilities)].append(tile)

seed = random.randint(-10000, 10000)
random.seed(seed)


timeDelay = 0.1

if input("Cut off edges (y/n): ").lower().startswith("y"):
    #top/bottom row
    for x in range(BOARD_SIZE[0]):
        topEdgeTile = GetTile(x, 0, board)
        topEdgeTile.CollapseTo(" ")
        GetPossible(topEdgeTile)
        Propagate(x, 0, board)
        bottomEdgeTile = GetTile(x, BOARD_SIZE[1]-1, board)
        bottomEdgeTile.CollapseTo(" ")
        GetPossible(bottomEdgeTile)
        Propagate(x, BOARD_SIZE[1]-1, board)
    #left/right column
    for y in range(BOARD_SIZE[1]):
        leftEdgeTile = GetTile(0, y, board)
        leftEdgeTile.CollapseTo(" ")
        GetPossible(leftEdgeTile)
        Propagate(0, y, board)
        RightEdgeTile = GetTile(BOARD_SIZE[0]-1, y, board)
        RightEdgeTile.CollapseTo(" ")
        GetPossible(RightEdgeTile)
        Propagate(BOARD_SIZE[0]-1, y, board)
showProgress = input("Show progress (y/n): ").lower().startswith("y")
if showProgress: timeDelay = float(input("Enter time delay between updates (float): "))
useWeights = input("Use weights (y/n): ").lower().startswith("y")

startTime = 0

def wfc():
    global startTime
    startX, startY = random.randint(1, BOARD_SIZE[0] - 2), random.randint(1, BOARD_SIZE[1] - 2)

    startTime = time.time()

    startTile = GetTile(startX, startY, board)
    startTile.Collapse()
    GetPossible(startTile)

    Propagate(startX, startY, board)

    while not AllCollapsed(board):
        lowest = None
        if USE_OPTIMISED_GET_LOWEST_ENTROPY:
            lowest = random.choice(EvenMoreOptimisedGetLowestEntropy(board))
        else:
            lowest = random.choice([tile for tile in OptimisedGetLowestEntropy(board) if not tile.collapsed])
        if lowest != None:
            lowest.Collapse()
            Propagate(lowest.x, lowest.y, board)
            if showProgress:
                os.system("cls")
                DrawBoard(board)
                time.sleep(timeDelay)
        else:
            break

cp = cProfile.Profile()
cp.enable()
wfc()
cp.disable()
DrawBoard(board)
print("seed: {}".format(seed))
print("Board of size {}x{} generated and drawn in {:.2f} seconds".format(BOARD_SIZE[0], BOARD_SIZE[1], (time.time()-startTime)))
cp.print_stats(sort='time')

if pygameVis:
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False

