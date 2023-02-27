from random import randint
from BoardClasses import Move
from BoardClasses import Board
from math import sqrt, log
from random import choice
from time import time
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
    
    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        move = self.mcts(move, self.color)

        self.board.make_move(move,self.color)
        return move

    def mcts(self, move, turnPlayer):
        #set-up root node
        rootNode = Node(move, turnPlayer)
        self.populateMoves(rootNode)

        #no need to search if theres only one
        if(len(rootNode.unvisitedChildren) == 1):
            return rootNode.unvisitedChildren[0].move

        timeLimit = time() + 7

        while time() < timeLimit:
            #select
            leafNode = self.selectLeafNode(rootNode)
            #expand
            rolloutNode = self.expandNode(leafNode)
            #rollout
            result = self.rollout(rolloutNode.move, rolloutNode.turnPlayer)
            #backup
            self.backpropagate(rolloutNode, result)


        mostFrequentNode = self.mostVisited(rootNode)
        return mostFrequentNode.move

        

    def selectLeafNode(self, curNode):
        #return current node if not fully expanded or terminal
        if curNode.unvisitedChildren != [] or curNode.visitedChildren == []:
            return curNode
        else:
            bestMove = None
            UCTmax = float("-inf")
            #find the best move
            for node in curNode.visitedChildren:
                UCT = node.getUCT()
                if UCT > UCTmax:
                    bestMove = node
                    UCTmax = UCT
            #traverse next node
            self.board.make_move(bestMove.move, curNode.turnPlayer)
            return self.selectLeafNode(bestMove)

    def expandNode(self, curNode):
        #generate moves if they haven't already
        if curNode.expanded == False:
            self.populateMoves(curNode)

        #get random move
        if curNode.unvisitedChildren != []:
            nextNode = choice(curNode.unvisitedChildren)
            curNode.moveToVisited(nextNode)
            #traverse next node
            self.board.make_move(nextNode.move, curNode.turnPlayer)
            return nextNode
        
        return curNode

    #make random moves until we reach game ending state
    def rollout(self, move, turnPlayer):
        #if no moves can be made, return result
        if self.board.get_all_possible_moves(turnPlayer) == []:
            return self.board.is_win(turnPlayer)

        piece = choice(self.board.get_all_possible_moves(turnPlayer))
        nextMove = choice(piece)

        self.board.make_move(nextMove, turnPlayer)
        if turnPlayer == 1:
            result = self.rollout(nextMove, 2)
        else:
            result = self.rollout(nextMove, 1)
        self.board.undo()
        return result

    def backpropagate(self, curNode, result):
        while curNode != None:
            curNode.updateNode(result)
            if curNode.parent != None:
                self.board.undo()
            curNode = curNode.parent
        return

    #returns most visited node
    def mostVisited(self, curNode):
        mostFrequent = None
        mostVisits = 0

        for node in curNode.visitedChildren:
            if node.visits > mostVisits:
                mostFrequent = node
                mostVisits = node.visits
        return mostFrequent
    
    #fetch children nodes
    def populateMoves(self, curNode):
        for movelist in self.board.get_all_possible_moves(curNode.turnPlayer):
            for move in movelist:
                newNode = Node(move, curNode.prevPlayer, curNode)
                curNode.addUnvisitedChild(newNode)
        curNode.expanded = True







        

class Node():

    def __init__(self, move = None, turnPlayer = None, parent = None):
        self.move = move
        self.parent = parent
        self.wins = 0
        self.visits = 0
        self.expanded = False
        self.unvisitedChildren = []
        self.visitedChildren = []
        self.turnPlayer = turnPlayer
        if(turnPlayer == 1):
            prevPlayer = 2
        else:
            prevPlayer = 1
        self.prevPlayer = prevPlayer

    def getUCT(self):
        constant = sqrt(2)
        UCT = (self.wins/self.visits) + constant * sqrt(2*log(self.parent.visits)/self.visits)
        return UCT

    #check this condition
    def updateNode(self, result):
        self.incVisits()
        if(self.turnPlayer == result):
            self.incWins()

    #incrementing
    def incVisits(self):
        self.visits += 1
    
    def incWins(self):
        self.wins += 1

    #list manipulation
    def moveToVisited(self, child):
        self.removeUnvisitedChild(child)
        self.addVisitedChild(child)

    def addUnvisitedChild(self, child):
        self.unvisitedChildren.append(child)

    def removeUnvisitedChild(self, child):
        self.unvisitedChildren.remove(child)

    def addVisitedChild(self, child):
        self.visitedChildren.append(child)