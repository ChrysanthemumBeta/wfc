import random, os, time, colorama

#constants
BOARD_SIZE = (10, 10)
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
DIRS = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        
#functions
def AllCollapsed(board):
    for tile in board:
        if tile.collapsedState == None:
            return False
    return True

def GetLowestEntropy(board):
    lowest = 100
    lowestTiles = []
    for tile in board:
        if len(tile.possibilities) < lowest and len(tile.possibilities) > 1:
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

def GetTile(x, y, board):
    for tile in board:
        if tile.x == x and tile.y == y:
            return tile
    return False

def DrawBoard(board):
    for y in range(BOARD_SIZE[1]):
        print("".join(str(GetTile(x, y, board)) for x in range(BOARD_SIZE[1])))

def GetPossible(tile):
    tile.possibleConnections = {0:[],1:[],2:[],3:[]}
    for char in tile.possibilities:
        for i, dir in enumerate(CHAR_DATA[char]):
            for possibleTile in CHAR_DATA.keys():
                data = CHAR_DATA[possibleTile]
                if data[DIR_COMPLEMENTS[i]] == dir:
                    tile.possibleConnections[i].append(possibleTile)



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
       





#classes
class Tile:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.possibilities = CHARS
        self.collapsedState = None
    def Collapse(self):
        self.collapsedState = random.choice(self.possibilities)
        self.possibilities = [self.collapsedState]
    def __str__(self):
        if self.collapsedState == None:
            return str(hex(len(self.possibilities)))[2:]
        else:
            return self.collapsedState



board = CreateBoard(BOARD_SIZE[0], BOARD_SIZE[1])
GetPossible(GetTile(0,0,board))
InitiallyPossible = GetTile(0,0,board).possibleConnections
for tile in board:
        tile.possibleConnections = InitiallyPossible

random.seed(2)

startX, startY = random.randint(0, BOARD_SIZE[0] - 1), random.randint(0, BOARD_SIZE[1] - 1)

startTile = GetTile(startX, startY, board)
startTile.Collapse()
GetPossible(startTile)

Propagate(startX, startY, board)

print(GetTile(0,1,board).possibleConnections)

while not AllCollapsed(board):
    lowest = random.choice(GetLowestEntropy(board))
    if lowest != None:
        lowest.Collapse()
        Propagate(lowest.x, lowest.y, board)
        DrawBoard(board)
        input()

    else:
        break


DrawBoard(board)

