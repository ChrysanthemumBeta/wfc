import random, os, time, json
from colorama import Fore, Back, Style

#constants
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

#functions
def GetClosestColour(possibilities):
    perc = (possibilities/ len(CHARS))
    for thresh in COLOUR_THRESHOLD:
        if perc >= thresh:
            return COLOUR_THRESHOLD[thresh]

def AllCollapsed(board):
    for tile in board:
        if not tile.collapsed:
           return False
    return True

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

def GetTile(x, y, board):
    for tile in board:
        if tile.x == x and tile.y == y:
            return tile
    return False

def DrawBoard(board):
    for y in range(BOARD_SIZE[1]):
        print("".join(str(GetTile(x, y, board)) for x in range(BOARD_SIZE[0])))

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
                if possibilites > len(adjacentTile.possibilities):
                    stack.append(adjacentTile)
                    GetPossible(adjacentTile)
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
            return GetClosestColour(possibilities) + str(hex(possibilities))[2:]
        else:
            return Fore.GREEN + self.collapsedState + Style.RESET_ALL


if input("Use custom size (y/n): ").lower().startswith("y"):
    print(Fore.RED + "WARNING:" + Style.RESET_ALL + " Bigger values will make the generation take longer")
    BOARD_SIZE[0] = int(input("X size (int): "))
    BOARD_SIZE[1] = int(input("Y size (int): "))
board = CreateBoard(BOARD_SIZE[0], BOARD_SIZE[1])
GetPossible(GetTile(0,0,board))
InitiallyPossible = GetTile(0,0,board).possibleConnections
for tile in board:
        tile.possibleConnections = InitiallyPossible

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
    


startX, startY = random.randint(1, BOARD_SIZE[0] - 2), random.randint(1, BOARD_SIZE[1] - 2)

startTime = time.time()

startTile = GetTile(startX, startY, board)
startTile.Collapse()
GetPossible(startTile)

Propagate(startX, startY, board)

prevLowest = []

while not AllCollapsed(board):
    lowest = random.choice([tile for tile in GetLowestEntropy(board) if not tile.collapsed])
    prevLowest.append(lowest)
    if lowest != None:
        lowest.Collapse()
        Propagate(lowest.x, lowest.y, board)
        if showProgress:
            DrawBoard(board)
            os.system("cls")
            time.sleep(timeDelay)
    else:
        break


DrawBoard(board)

print("seed: {}".format(seed))
print("Board of size {}x{} generated and drawn in {:.2f} seconds".format(BOARD_SIZE[0], BOARD_SIZE[1], (time.time()-startTime)))

