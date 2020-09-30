"""
Tic Tac Toe Player
"""

import math
import copy
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = 0
    for i in board:
        for j in i:
            if j==EMPTY:
                count +=1
    
    if count % 2 == 0 :
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    acts = set()

    for i in range(0,3):
        for j in range(0,3):
            if board[i][j]==EMPTY:
                acts.add((i,j))
    return acts

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action==None:
        raise Exception('Illegal move <NoneType>')
    i = action[0]
    j = action[1]

    if not((0 <= i and i < 3) and (0 <= j and j < 3)): # illegal cell position exception
        raise Exception('Illegal cell position <out of boundary>')
    if  board[i][j]!=EMPTY:
        raise Exception('Already filled cell <not empty>') # not empty cell exception

    currPlayer = player(board)
    nwBoard = copy.deepcopy(board)
    nwBoard[i][j] = currPlayer
    
    return nwBoard


        




def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if board[0][0]!=EMPTY:
        center = board[0][0]
        if center==board[0][1] and center==board[0][2] or center==board[1][0] and center==board[2][0]:
            return center
    if board[2][2]!=EMPTY:
        center = board[2][2]
        if center==board[2][1] and center==board[2][0] or center==board[1][2] and center==board[0][2]:
            return center
    if board[1][1]!=EMPTY:
        center = board[1][1]
        if center==board[2][2] and center==board[0][0] or center==board[0][2] and center==board[2][0] or center==board[0][1] and center==board[2][1] or center==board[1][0] and center==board[1][2]:
            return center

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # x or o wins
    if winner(board)!=None:
        return True
    
    # no one wins => tie or game progress

    # check tie
    for i in board:
        for j in i:
            if j==EMPTY:
                return False # if any empty cell exist => game progress / not terminated yet / False
    # no empty cell
    # then game ties => True terminated
    return True
    


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    win = winner(board)

    if win==X:
        return 1
    if win==O:
        return -1
    # tie
    return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    INF = 2 # since  |utiliy| < 2

    def max_value(board, gameLen, alpha, beta):
        if terminal(board):
            return (utility(board), None, gameLen)

        v = (-INF, None, gameLen)
        
        bag = []

        for action in actions(board):
            tmp = min_value(result(board, action), gameLen+1, alpha, beta)
            
            if v[0] < tmp[0] or (v[0]==tmp[0] and v[2]>tmp[2]):
                v = (tmp[0], action, tmp[2])
                bag.clear()
                bag.append(v)
            elif v[0]==tmp[0] and v[2]==tmp[2]:
                v = (tmp[0], action, tmp[2])
                bag.append(v)

            alpha = max(v[0], alpha)
            if beta < alpha: # beta <= alpha  // yapinca sacma sapan calisti nedenini tespit edemedim
                break
        random.seed()
        return bag[random.randint(0, len(bag)-1)]

    def min_value(board, gameLen, alpha, beta):
        if terminal(board):
            return (utility(board), None, gameLen)

        v = (INF, None, gameLen)

        bag = []

        for action in actions(board):
            tmp = max_value(result(board, action), gameLen+1, alpha, beta)

            if v[0] > tmp[0] or (v[0]==tmp[0] and v[2]>tmp[2]):
                v = (tmp[0], action, tmp[2])
                bag.clear()
                bag.append(v)
            elif v[0]==tmp[0] and v[2]==tmp[2]:
                v = (tmp[0], action, tmp[2])
                bag.append(v)
            
            beta = min(v[0], beta)
            if beta < alpha:
                break
        random.seed()
        return bag[random.randint(0, len(bag)-1)]

    # if game terminal => no move possible 
    if terminal(board):
        return None
    # not terminal => current player
    p = player(board)

    if p==X:
        return max_value(board, 0, -INF, +INF)[1]
    else: # if p==O
        return min_value(board, 0, -INF, +INF)[1]
