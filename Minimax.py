from Interface import *


def getChildren(board):
    children = []
    for point in board.getAvailablePoints():
        obj = board.getCopy()
        obj.placeMove(Move(board.currentTurn, point))
        children.append(obj)
    return children


def evalBoardScore(board, player):
    net_diff = board.whiteScore - \
        board.blackScore if player is State.White else board.blackScore - board.whiteScore
    total_loss = 0
    count = 0
    for x in range(board.length):
        for y in range(board.length):
            stability_loss = 0
            for eachDir in board.allDir:
                stability_loss += len(board.getFlankPoints(
                    Move(player, Point(x, y)), eachDir))
            if stability_loss > 0:
                total_loss += stability_loss
                count += 1

        bonus = 0
        enCount = 1.0
        myCount = 1.0
        corner_pt = 2
        if board.othelloBoard[0][0] is player:
            myCount += .2
            bonus += corner_pt * myCount
        elif board.othelloBoard[0][0] is player.opposite:
            enCount += .2
            bonus -= corner_pt*enCount
            

        if board.othelloBoard[-1][-1] is player:
            myCount += .2
            bonus += corner_pt * myCount
        elif board.othelloBoard[-1][-1] is player.opposite:
            enCount += .2
            bonus -= corner_pt*enCount

        if board.othelloBoard[-1][0] is player:
            myCount += .2
            bonus += corner_pt * myCount
        elif board.othelloBoard[-1][0] is player.opposite:
            enCount += .2
            bonus -= corner_pt * enCount

        if board.othelloBoard[0][0-1] is player:
            myCount += .2
            bonus += corner_pt * myCount
        elif board.othelloBoard[0][-1] is player.opposite:
            enCount += .2
            bonus -= corner_pt * enCount

    return net_diff+(total_loss/count if count else 0)+bonus


def minimax(node, depth, player, aggressiveFactor=0.2):
    children = getChildren(node)
    score = evalBoardScore(node, player)
    if depth == 0 or len(children) == 0:
        # print(*node.history, sep="\n")
        return (node, score)

    b = [minimax(child, depth-1, player) for child in children]

    if player is node.currentTurn:
        node, s = max(b, key=lambda x: x[1])
        return (node, s*(1-aggressiveFactor) + score*aggressiveFactor)
    else:
        node, s = min(b, key=lambda x: x[1])
        return (node, s*(1-aggressiveFactor) + score*aggressiveFactor)
