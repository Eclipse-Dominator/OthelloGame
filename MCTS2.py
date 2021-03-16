'''
MCTS tree search
based on wikipedia's steps
'''
from collections import defaultdict
from Othello import OthelloBoard
import random
import numpy as np
from Interface import Move, State


class MC_Tree:
    def __init__(self, exploration, player):
        self._wins = defaultdict(float)
        self._visits = defaultdict(lambda: 0.000001)
        self._children = defaultdict(set)
        self._exploration = exploration
        self.player = player
        

    def child_from_parent(self, parent, move):
        for child in self._children[parent]:
            if child.last_move == move:
                return child
        return parent.getChild(move)

    def playOut(self, node):
        parent_to_leaf, node = self._select_leaf(node)
        leaf = self._expand(node)
        if leaf:
            score = self._simulate(leaf)
            parent_to_leaf += [leaf]
        else:
            score = self._simulate(node)
        self._backpropagate(parent_to_leaf, score)

    def choose(self, node, options="robust"):
        if options == "robust":
            def func(x): return self._visits[x]
        elif options == "max":
            def func(x): return self._wins[x]/self._visits[x]
        return max(self._children[node], key=func).last_move

    def _select_leaf(self, node):
        branch = []
        while 1:
            if node not in self._children or node.terminal:
                return branch + [node], node
            newChild = self._expand(node)
            if newChild:
                return branch + [newChild], newChild
            branch.append(node)
            if len(self._children[node]) == 1:
                node = list(self._children[node])[0]
                continue
            node = max(self._children[node], key=lambda x: self.UCB(node, x))

    def UCB(self, parent_node, node):
        explore_value = np.sqrt(self._visits[parent_node])
        if parent_node.currentTurn is self.player:
            exploit_value = self._wins[node]/self._visits[node]
        else:
            exploit_value = 1 - self._wins[node]/self._visits[node]
        return exploit_value + self._exploration * explore_value

    def _expand(self, node):
        if len(node.unexploredPoints):
            newChild = node.getChild(
                Move(node.currentTurn, node.unexploredPoints.pop()))
            self._children[node].add(newChild)
            return newChild
        return None

    def _simulate(self, node):
        game = node.getCopy()
        while not game.checkGameEnd():
            randMove = Move(game.currentTurn, random.choice(
                game.getAvailablePoints()))
            game.placeMove(randMove)
        if game.whiteScore == game.blackScore:
            return 0.5
        if self.player is State.White:
            return 1 if game.whiteScore > game.blackScore else 0
        else:
            return 1 if game.blackScore > game.whiteScore else 0

    def _backpropagate(self, node_array, result):
        for node in node_array:
            self._visits[node] += 1
            self._wins[node] += result


class Node(OthelloBoard):
    def __init__(self, state, last_move=None):
        super().__init__()
        self.load_compact_info(state)
        self.last_move = last_move
        self.terminal = self.checkGameEnd()
        self.unexploredPoints = [] if self.terminal else self.getAvailablePoints()
        random.shuffle(self.unexploredPoints)

    def getChild(self, move):
        obj = self.getCopy()
        obj.placeMove(move)
        return Node(obj.compact_info, last_move=move)
