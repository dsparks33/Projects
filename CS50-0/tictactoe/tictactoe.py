"""
Tic Tac Toe Player
"""

import math
import copy

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
    numX = sum(row.count(X) for row in board)
    numO = sum(row.count(O) for row in board)

    return X if numX == numO else O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    emptyPositions = set()
    for rowIdx, row in enumerate(board):
        for colIdx, cell in enumerate(row):
            if cell == EMPTY:
                emptyPositions.add((rowIdx, colIdx))
    
    return emptyPositions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if any(coord > 2 for coord in action):
        raise ValueError("Action out of range")
    XorO = player(board)
    boardCopy = copy.deepcopy(board)
    boardCopy[action[0]][action[1]] = XorO
    return boardCopy

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i]
        
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    
    return None  # No winner found

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    else:
        for row in board:
            if EMPTY in row:
                return False
        return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    aWinner = winner(board)
    return {'X': 1, 'O': -1}.get(aWinner, 0)

def maxValue (board):
    if terminal(board): return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, minValue(result(board, action)))
    return v

def minValue (board):
    if terminal(board): return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, maxValue(result(board, action)))
    return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    Assumes there is at least one open space on the board.
    """
    nextPlayer = player(board)
    currentValue = -1 if nextPlayer == X else 1

    for options in actions(board):
        tempBoard = result(board, options)
        resultValue = maxValue(tempBoard) if nextPlayer == X else minValue(tempBoard)
        if (nextPlayer == X and resultValue > currentValue) or (nextPlayer == O and resultValue < currentValue):
            currentValue, retOptions = resultValue, options

    return retOptions
