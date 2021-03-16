from Interface import *
from Minimax import minimax
from MCTS2 import *
import time


class OthelloGame:
    def __init__(self):
        self.board = OthelloBoard(show_moves=True)
        self.board.playOutMoves([])

    def readCoord(self, coordinate):
        coordinate = coordinate.strip()
        if coordinate == "" or coordinate == "-":
            return "-"
        if len(coordinate) < 2:
            return False
        letter = coordinate.lower()[0]
        number = coordinate[1:]
        if letter.isalpha() and number.isnumeric():
            return Point(ord(letter)-97, int(number)-1)

    def simulateGames(self, number):
        win = draw = lose = 0
        for num in range(number):
            print(f"Game {num+1}")
            self.board.playOutMoves([])
            MCTS_agent = MC_Tree(exploration=1.4, player=State.White)
            MCTS_node = Node(self.board.compact_info)
            while not self.board.checkGameEnd():
                if (self.board.currentTurn is State.Black):
                    node, s = minimax(self.board, 3, State.Black, 0.4)
                    user_move = node.history[len(self.board.history)]
                else:
                    for _ in range(50):
                        MCTS_agent.playOut(MCTS_node)
                    user_move = MCTS_agent.choose(MCTS_node)
                self.board.placeMove(user_move)
                MCTS_node = MCTS_agent.child_from_parent(MCTS_node, user_move)
            if (self.board.whiteScore > self.board.blackScore):
                win += 1
            elif (self.board.whiteScore < self.board.blackScore):
                lose += 1
            else:
                draw += 1
            print(self.board)
            print(
                f"Wins:{win} Lose:{lose} Draw:{draw} Total:{win+lose+draw}\nAve win rate:{win/(win+draw+lose)}")

    def gameLoop(self):
        self.board.playOutMoves([])
        MCTS_agent = MC_Tree(exploration=1.4, player=State.White)
        MCTS_node = Node(self.board.compact_info)
        while not self.board.checkGameEnd():
            print(self.board)
            print("Black:{}, White:{}".format(
                self.board.blackScore, self.board.whiteScore))
            print("{}'s turn".format(str(self.board.currentTurn)))
            if len(self.board.history):
                print("Last move:", self.board.history[-1])
            if (self.board.currentTurn is State.Black):
                #node, s = minimax(self.board, 3, State.Black, 0.4)
                #user_move = node.history[len(self.board.history)]

                user_move = self.readCoord(input("Enter your move: "))
                user_move = Move(State.Black, user_move)
            else:
                startTime = time.time()
                counter=0
                while time.time() - startTime <= 5:
                    MCTS_agent.playOut(MCTS_node)
                    counter+=1
                print(f"iterations done:{counter}")
                user_move = MCTS_agent.choose(MCTS_node)
                # player
                #user_move = self.readCoord(input("Enter your move: "))
            if user_move.point not in self.board.getAvailablePoints():
                print(f"{str(user_move)} is invalid")
                continue
            self.board.placeMove(user_move)
            MCTS_node = MCTS_agent.child_from_parent(MCTS_node, user_move)
        print(self.board)
        print("Black:{}\nWhite:{}".format(
            self.board.blackScore, self.board.whiteScore))
        print("Game End!")
        if (self.board.whiteScore > self.board.blackScore):
            print("White Wins!")
        elif (self.board.whiteScore < self.board.blackScore):
            print("Black Wins!")
        else:
            print("Draw!")


class OthelloBoard:
    def __init__(self, length=8, show_moves=False):
        # all 8 directions
        self.allDir = [(0, 1), (0, -1), (1, 0), (-1, 0),
                       (1, 1), (-1, -1), (1, -1), (-1, 1)]
        self.history = []
        self.length = length
        self.showMoves = show_moves

    def playOutMoves(self, moveHistory):
        cO = self.length//2
        cI = cO - 1
        self.currentTurn = State.Black
        self.othelloBoard = [[State.Empty] *
                             self.length for _ in range(self.length)]
        self.othelloBoard[cI][cI] = self.othelloBoard[cO][cO] = State.White
        self.othelloBoard[cO][cI] = self.othelloBoard[cI][cO] = State.Black
        self.blackScore = 2
        self.whiteScore = 2

        for move in moveHistory:
            self.placeMove(move)

    def isValidMove(self, move):
        if self.othelloBoard[move.point.x][move.point.y] is not State.Empty:
            return False
        for direction in self.allDir:
            if len(self.getFlankPoints(move, direction)):
                return True
        return False

    def getAvailablePoints(self, player=None):
        if not player:
            player = self.currentTurn
        moves = [Point(x, y) for x in range(0, self.length) for y in range(0, self.length)
                 if self.isValidMove(Move(player, Point(x, y)))]
        if len(moves) == 0:
            moves = ["-"]
        return moves

    def getFlankPoints(self, move, direction):
        # direction is a tuple of (change X, change Y)
        changeX, changeY = direction
        checkPosX = move.point.x + changeX
        checkPosY = move.point.y + changeY
        flippedPointsList = []
        while 0 <= checkPosX < self.length and 0 <= checkPosY < self.length:
            if self.othelloBoard[checkPosX][checkPosY] is State.Empty:
                return []
            if self.othelloBoard[checkPosX][checkPosY] is move.player:
                return flippedPointsList
            flippedPointsList.append(Point(checkPosX, checkPosY))
            checkPosX += changeX
            checkPosY += changeY
        return []

    def placeMove(self, move, check=True):
        if str(move.point) == "-":
            self.currentTurn = move.player.opposite
            self.history.append(move)
            return
        if check and not self.isValidMove(move):
            return False
        flankedList = [move.point]
        for direction in self.allDir:
            flankedList += self.getFlankPoints(move, direction)
        for point in flankedList:
            self.othelloBoard[point.x][point.y] = move.player

        if move.player is State.White:
            self.whiteScore += len(flankedList)
            self.blackScore -= len(flankedList) - 1
        else:
            self.blackScore += len(flankedList)
            self.whiteScore -= len(flankedList) - 1
        self.currentTurn = move.player.opposite
        self.history.append(move)

    def checkGameEnd(self):
        if (self.getAvailablePoints()[0] == "-"):
            nextPhase = self.getCopy()
            nextPhase.placeMove(Move(self.currentTurn, "-"))
            return nextPhase.getAvailablePoints()[0] == "-"

    def getCopy(self):
        ObjSelf = OthelloBoard()
        ObjSelf.othelloBoard = [[*x] for x in self.othelloBoard]
        ObjSelf.history = [*self.history]
        ObjSelf.blackScore = self.blackScore
        ObjSelf.whiteScore = self.whiteScore
        ObjSelf.currentTurn = self.currentTurn
        return ObjSelf

    @property
    def compact_info(self):
        # [0] indicate current player, 0/1 => black/white
        # [1] indicate board length, even integer
        # [2:] indicate flattened current board placement -1: empty, 0 black, 1 white
        flatBoard = [
            item.value for sublist in self.othelloBoard for item in sublist]
        return [self.currentTurn.value-1, len(self.othelloBoard)] + flatBoard

    def load_compact_info(self, cryptedInfo):
        self.currentTurn = State.White if cryptedInfo[0] else State.Black
        self.length, flat_board = cryptedInfo[1], cryptedInfo[2:]
        self.othelloBoard = []
        self.whiteScore = 0
        self.blackScore = 0

        def convertToState(x):
            if x == 1:
                self.blackScore += 1
                return State.Black
            if x == 2:
                self.whiteScore += 1
                return State.White
            return State.Empty

        i = 0
        for j in range(self.length, self.length**2+1, self.length):
            self.othelloBoard.append([convertToState(x)
                                      for x in flat_board[i:j]])
            i = j

    def __hash__(self):
        return hash(str(self.compact_info))

    def __str__(self):
        print_string = ' '.join(['']+[chr(num+97)
                                      for num in range(0, self.length)]) + '\n'

        if self.showMoves and "-" not in self.getAvailablePoints():
            transposeBoard = [[*x] for x in self.othelloBoard]
            for point in self.getAvailablePoints():
                transposeBoard[point.x][point.y] = "."
            transposeBoard = zip(*transposeBoard)
        else:
            transposeBoard = zip(*self.othelloBoard)
        for rowNum, row in enumerate(transposeBoard):
            print_string += "|".join([str(x)
                                      for x in ['', *row, rowNum+1]]) + '\n'
        return print_string


if __name__ == "__main__":
    game = OthelloGame()
    a = time.time()
    # game.simulateGames(100)
    game.gameLoop()
    print(f"Average time per game: {(time.time()-a)/100}s")
