import numpy as np
import pickle
import random
import os
ROWS = 3
COLS = 3
WINCONDITION = 3
class State:
    def __init__(self, p1, p2, row, col, winCondition):
        self.row = row
        self.col = col
        self.board = np.zeros((row, col))
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        self.winCondition = winCondition
        #p1 plays first
        self.playerSymbol = 1

    def getHash(self):
        self.boardHash = str(self.board.reshape(self.row * self.col))
        return self.boardHash

    def winner(self, move):
        directions = [
                    [0, 1],   
                    [1, 0],   
                    [1, 1],   
                    [1, -1]   
                ]
        player = -1 if self.playerSymbol == 1 else 1

        row, col = move

        for [dx, dy] in directions:

            count = 1
                
            # // Check in positive direction
            for i in range(1, self.winCondition):
                newRow = row + i * dx
                newCol = col + i * dy
                if newRow >= 0 and newRow < self.row and newCol >= 0 and newCol < self.col and self.board[newRow][newCol] == player: 
                    count += 1
                else:
                    break
            # // Check in negative direction
            for i in range(1, self.winCondition):
                newRow = row - i * dx
                newCol = col - i * dy
                if newRow >= 0 and newRow < self.row and newCol >= 0 and newCol < self.col and self.board[newRow][newCol] == player: 
                    count += 1
                else:
                    break
                    
            if count >= self.winCondition:
               # // Highlight winning cells
               self.isEnd = True
               return 1 if player == 1 else -1
        
        #tie
        if len(self.availablePositions()) == 0:
            self.isEnd = True
            return 0

        #not end
        self.isEnd = False
        return None
    
    def check_winner(self, board):
            for i in range(self.row):
                if sum(board[i, :]) == 3:
                   return 1
                if sum(board[i, :]) == -3:
                    return -1
            for i in range(self.col):
                if sum(board[:, i]) == 3:
                    return 1
                if sum(board[:, i]) == -3:
                    return -1
            if sum([board[i, i] for i in range(self.col)]) == 3 or sum([board[i, self.col-i-1] for i in range(self.col)]) == 3:
                return 1
            if sum([board[i, i] for i in range(self.col)]) == -3 or sum([board[i, self.col-i-1] for i in range(self.col)]) == -3:
                return -1
            if not any(0 in row for row in board):
                return 0  # Draw
            return None
    
    def availablePositions(self):
        positions = [(i, j) for i in range(self.row) for j in range(self.col) if self.board[i, j] == 0]
        return positions
    
    def get_available_positions(self, board):
        return [(i, j) for i in range(self.row) for j in range(self.col) if board[i, j] == 0]
    
    def updateState(self, position):
        self.board[position] = self.playerSymbol
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

    def giveReward(self, result):

        if result == 1:
            self.p1.feedReward(1)
            self.p2.feedReward(-1)
        elif result == -1:
            self.p1.feedReward(-1)
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.1)
            self.p2.feedReward(0.1)

    def reset(self):
        self.board = np.zeros((self.row, self.col))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1

    #Use for minimax AI
    def minimax(self, board, depth, maximizingPlayer=True):
        result = self.check_winner(board)
        if result is not None:
            return result  # 1: AI win, -1: loss, 0: draw
        
        if maximizingPlayer:
            best_score = -float('inf')
            for action in self.get_available_positions(board):
                board[action] = 1  # AI is '1'
                score = self.minimax(board, depth + 1, False)
                board[action] = 0
                if score == 1:
                    return score
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for action in self.get_available_positions(board):
                board[action] = -1  # Opponent is '-1'
                score = self.minimax(board, depth + 1, True)
                board[action] = 0
                if score == -1:
                    return score
                best_score = min(best_score, score)
            return best_score
    
    # Move for MINIMAX AI
    def move(self, board, depth):
        score = 0
        best = -float('inf')
        res = ()
        if depth < 4:
            res = random.choice(self.get_available_positions(board))
        else:
            for action in self.get_available_positions(board):
                board[action] = 1
                score = self.minimax(board, depth + 1, True)
                board[action] = 0
                if score == 1:
                    res = action
                    break
                if score > best:
                    best = score
                    res = action
        return res

    def play(self, round = 100):
        winner = 0
        draw = 0
        looser = 0
        for i in range(round):
            idx = 0
            if i % 1000 == 0:
                print("Rounds {}".format(i))
                if i != 0:
                    print("Win rate{}".format(winner / i))
                    print("Loose rate{}".format(looser / i))
                    self.p1.exp_rate = max(0.01, self.p1.exp_rate * 0.99)
                    self.p2.exp_rate = max(0.01, self.p2.exp_rate * 0.99)
            
            while not self.isEnd:
                #PLayer 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
               
                idx += 1
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)

                win = self.winner(p1_action)
                if win is not None:
                    if win == 1:
                        winner += 1
                    else:
                        draw += 1
                    self.giveReward(win)
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break
                if idx > 60:
                    draw += 1
                    self.giveReward(0)
                    self.p1.reset()
                    self.p2.reset()
                    break
                else:
                    #Player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol)
                   
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)
                    idx += 1
                    win = self.winner(p2_action)
                    if win is not None:
                        
                        if win == -1:
                            looser += 1
                        else:
                            draw += 1
                        self.giveReward(win)
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break
                    if idx > 60:
                        draw += 1
                        self.giveReward(0)
                        self.p1.reset()
                        self.p2.reset()
                        break
                
    def play2(self, round):
        winner = 0
        draw = 0
        looser = 0
        
        for i in range(round):
            idx = 0
            if i % 1000 == 0:
                print("Rounds {}".format(i))
                if i != 0:
                    print("Win rate {}".format(winner / i))
                    print("Loose rate {}".format(looser / i))
                    print("Exp_Rate {}".format(self.p1.exp_rate))
                    self.p1.exp_rate = max(0.01, self.p1.exp_rate * 0.99)
                    
            while not self.isEnd:
                # Minimax-AI
                n = self.move(self.board, idx)

                self.updateState(n)
                idx +=  1
                
                win = self.winner(n)
                if win is not None:
                    if win == 1:
                        looser += 1
                    else:
                        draw += 1
                    self.giveReward(1)
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break
                
                else:
                    #RL-Learner
                    positions = self.availablePositions()
                    p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
                    #take action and update board state
                    self.updateState(p1_action)
                    idx += 1
                    board_hash = self.getHash()
                    self.p1.addState(board_hash)
                    # self.showBoard()
                    #check board status if it is end

                    win = self.winner(p1_action)
                    if win is not None:
                        if win == -1:
                            winner += 1
                        else:
                            draw += 1
                        self.giveReward(-1)
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break

    def showBoard(self):
        # p1: x  p2: o
            for i in range(0, self.row):
                print('-------------')
                out = '| '
                for j in range(0, self.col):
                    if self.board[i, j] == 1:
                        token = 'x'
                    if self.board[i, j] == -1:
                        token = 'o'
                    if self.board[i, j] == 0:
                        token = ' '
                    out += token + ' | '
                print(out)
            print('-------------')      

class Player:
    def __init__(self, name, exp_rate = 0.3):
        self.name = name
        self.states = []
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {}
    
    def getHash(self, board):
        boardHash = str(board.reshape(board.shape[0] * board.shape[1]))
        return boardHash
    def chooseAction(self, positions, current_board, symbol):
        if np.random.uniform(0, 1) <= self.exp_rate:
            #take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            value_max = -999
            for p in positions:
                next_board = current_board.copy()
                next_board[p] = symbol
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)

                if value >= value_max:
                    value_max = value
                    action = p
        return action
    
    def addState(self, state):
        self.states.append(state)

    def feedReward(self, reward):
        for st in reversed(self.states):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            self.states_value[st] += self.lr*(reward * self.decay_gamma - self.states_value[st])
            reward = self.states_value[st]
    
    def reset(self):
        self.states = []
    
    def savePolicy(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()
    
    def loadPolicy(self, file):
        fr = open(file, 'rb')
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            
            self.states_value = {}
        else:
            with open(file, 'rb') as fr:
                self.states_value = pickle.load(fr)
        fr.close()

class Random:
    def __init__(self, name, exp_rate = 0.3):
        self.name = name
        self.exp_rate = exp_rate
    
    def getHash(self, board):
        boardHash = str(board.reshape(board.shape[0] * board.shape[1]))
        return boardHash
    def chooseAction(self, positions, current_board, symbol):
        idx = np.random.choice(len(positions))
        action = positions[idx]
        return action
    
    def addState(self, state):
        pass


    def feedReward(self, reward):
        pass
    
    def reset(self):
        pass

class Human:
    def __init__(self, name):
        self.name = name
    
    def chooseAction(self, positons, row , col):
        action  = (row, col)
        if action in positons:
            return action

    def addState(self, state):
        pass

    def feedReward(self, reward):
        pass

    def reset(self):
        pass

class RuleBased:
    def __init__(self, name, winCondition=3, exp_rate=0.3):
        self.name = name
        self.exp_rate = exp_rate
        self.winCondition = winCondition

    def getHash(self, board):
        return str(board.reshape(board.shape[0] * board.shape[1]))

    def chooseAction(self, positions, board, symbol):
        opponent_symbol = -1 if symbol == 1 else 1
        best_score = -float('inf')
        best_action = None
        size = board.shape[0]
        center = size // 2
        best_opponent_score = 0
        opponent_score = 0
        opponent_action = None
        for pos in positions:
            score = 0

            # 1. Nếu đánh thắng → score cực cao
            test_board = board.copy()
            test_board[pos] = symbol
            if self.check_win(test_board, pos, symbol):
                return pos  # thắng luôn thì chọn ngay

            # 2. Nếu đối thủ đánh thắng → chặn lại
            test_board_opponent = board.copy()
            test_board_opponent[pos] = opponent_symbol
            if self.check_win(test_board_opponent, pos, opponent_symbol):
                return pos  # chặn ngay

            # 3. Ưu tiên chặn đối thủ
            test_board_self = board.copy()
            test_board_self[pos] = opponent_symbol
            opponent_score = self.evaluate_position(test_board_self, pos, opponent_symbol, is_opponent=True)
    
            # 4. Ưu tiên nối dài chuỗi của mình (4 quân liên tiếp thì rất tốt)
            test_board_self = board.copy()
            test_board_self[pos] = symbol
            score += self.evaluate_position(test_board_self, pos, symbol)

            # 5. Phạt các vị trí gần góc
            r, c = pos
            size = board.shape[0]
            if r in [0, 1, size-1, size-2] or c in [0, 1, size-1, size-2]:
                score -= 1  

            center = size // 2
            score -= abs(r - center) + abs(c - center)

            if score > best_score:
                best_score = score
                best_action = pos
            if opponent_score > best_opponent_score:
                best_opponent_score = opponent_score
                opponent_action = pos

        if best_score + 2  <= best_opponent_score and opponent_action is not None:
            return opponent_action
        return best_action

    def check_win(self, board, move, player):
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        row, col = move
        for dx, dy in directions:
            count = 1
            blocks = 0
            for d in [1, -1]:
                for step in range(1, self.winCondition):
                    r = row + step * dx * d
                    c = col + step * dy * d
                    if 0 <= r < board.shape[0] and 0 <= c < board.shape[1]:
                        if board[r][c] == player:
                            count += 1
                        elif board[r][c] != 0:
                            blocks += 1
                            break
                        else:
                            break
                    else:
                        blocks += 1
                        break
            if count >= self.winCondition:
                return True
        return False

    def evaluate_position(self, board, move, player, is_attack=True, is_opponent=False):
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        row, col = move
        max_score = 0

        for dx, dy in directions:
            count = 1
            blocks = 0
            for d in [1, -1]:
                for step in range(1, self.winCondition):
                    r = row + step * dx * d
                    c = col + step * dy * d
                    if 0 <= r < board.shape[0] and 0 <= c < board.shape[1]:
                        if board[r][c] == player:
                            count += 1
                        elif board[r][c] != 0:
                            blocks += 1
                            break
                        else:
                            break
                    else:
                        blocks += 1
                        break
            if is_opponent and count >= self.winCondition - 1 and blocks == 0:
                return 1000 # chặn đối thủ sắp thắng
            if count >= self.winCondition - 1 and blocks == 0:
                score = 1000  # open-ended almost-win
            elif count == self.winCondition - 1 and blocks == 1:
                score = 70  # 1-ended almost-win
            elif count == self.winCondition - 2 and blocks == 0:
                score = 50
            elif count == self.winCondition - 2 and blocks == 1:
                score = 10
            else:
                score = count + 5  # chuỗi ngắn hơn

            if not is_attack and count >= self.winCondition - 1:
                score = 100  # Nếu đối thủ sắp thắng thì cần chặn gấp
            elif not is_attack:
                score *= 0.5  # giảm ưu tiên cho phòng thủ

            max_score += score

        return max_score

    def addState(self, state): pass
    def feedReward(self, reward): pass
    def reset(self): pass
    def savePolicy(self): pass
    def loadPolicy(self, file): pass


def self_training(row=3, col=3, winCondition=3, random=False, type = 0):
    epoch = 0    
    while epoch < 10:
        print("Epoch {}".format(epoch))

        p1 = Player("p1", 0.1)
        p1.loadPolicy("policy_p1")

        if random:
            p2 = RuleBased("p2", winCondition=3)
            
        else:
            p2 = Player("p3", 0)
            p2.loadPolicy("policy_p1")
        
        if epoch % 2 == 0:
            
            st = State(p1, p2, row, col, winCondition)
        else:
            
            st = State(p2, p1, row, col, winCondition)

        if type == 0:
            st.play(10000)
        else:
            st.play2(10000)
        p1.savePolicy()
        epoch += 1
    

if __name__ == "__main__":
    self_training(row=ROWS, col=COLS, winCondition=WINCONDITION, random=False, type=0)  
    #random = True for RL vs Rule-based AI, False for RL vs RL
    #type = 0 for AI vs AI, 1 for AI vs Minimax


