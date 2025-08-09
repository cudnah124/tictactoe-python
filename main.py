import numpy as np
import random
from time import sleep
def create_board(x, y):
    return np.zeros((x, y), dtype = int)

def actions(board):
    return [(i, j) for i in range(3) for j in range(3) if board[i][j] == 0]

def random_place(board, player):
    loc = random.choice(actions(board))
    board[loc] = player
    return board

def human_place(board, player):
    while True:
        x = int(input("Nhap row:"))
        y = int(input("Nhap col:"))
        if (x, y) in actions(board):
            board[(x, y)] = player
            return board
        else:
            print("Nhap sai vi tri")

def player(board):
    player1 = len([(i, j) for i in range(3) for j in range(3) if board[i][j] == 1])
    player2 = len([(i, j) for i in range(3) for j in range(3) if board[i][j] == 2])

    if player1 <= player2:
        return 1
    return 2

def row_win(board, player):
    return any(all(cell == player for cell in row) for row in board)

def col_win(board, player):
    return any(all(row[i] == player for row in board) for i in range(3))

def diag_win(board, player):
    return all(board[i][i] == player for i in range(3))or all(board[i][2-i] == player for i in range(3))

def evaluate(board):
    for player in [1, 2]:
        if row_win(board, player) or col_win(board, player) or diag_win(board, player):
            return player
    return -1 if np.all(board != 0) else 0

def untility(result):
    if evaluate(result) == 1:
        return 1
    if evaluate(result) == 2:
        return -1
    return 0

def minimax(board, depth, maximizingPlayer = True):
    v = -float('inf') if maximizingPlayer else float('inf')
    best_score = v

    if evaluate(board) != 0:
        return untility(board)
    else:
        if depth < 9:
            if maximizingPlayer:
                best_score = -float('inf')
                for action in actions(board):
                    board[action] = 1
                    score = minimax(board, depth + 1, False)
                    board[action] = 0
                    best_score = max(best_score, score)
                return best_score
            else:
                best_score = float('inf')
                for action in actions(board):
                    board[action] = 2
                    score = minimax(board, depth + 1, True)
                    board[action] = 0
                    best_score = min(best_score, score)
                return best_score
        else:
            return 0 

def move(board, depth):
    score = 0
    best = -float('inf')
    res = ()
    if depth < 3:
        action = random.choice(actions(board))
        return action
    else:
        for action in actions(board):
            board[action] = 1
            score = minimax(board, depth + 1, False)
            board[action] = 0
            if score > best:
                best = score
                res = action
    return res

def play(chance):

    board = create_board(3, 3)

    idx = 0

    while evaluate(board) == 0:

        if chance == 1:
            n = move(board, idx)
            board[n] = 1

            print(board)
            sleep(1)

            idx +=  1
            chance = 2
            continue

        elif chance == 2:

            board = human_place(board, 2)

            print(board)
            sleep(1)

            idx += 1
            chance = 1

    return evaluate(board)


print(play(1))

    






