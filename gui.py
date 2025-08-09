import tkinter as tk
from ai import State, Human, Player, RuleBased
import numpy as np

COLS = 3
ROWS = 3
WINCONDITION = 3
class GameGUI:
    def __init__(self, master, row, col):
        self.master = master
        self.master.title("Game X/O - GUI")

        self.buttons = [[None for _ in range(COLS)] for _ in range(ROWS)]

        self.human = Human("Người chơi")
        self.ai = Player("p2", 0)
        self.ai.loadPolicy("policy_p1")
        self.game = State(self.human, self.ai, ROWS, COLS, WINCONDITION)
        self.row = ROWS
        self.col = COLS
        self.create_board()

    def create_board(self):
        for i in range(self.row):
            for j in range(self.col):
                btn = tk.Button(self.master, text="", font=("Arial", 24), width=5, height = 3,
                                command=lambda x=i, y=j: self.on_click(x, y))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

    def on_click(self, x, y):
        if self.game.board[x][y] != 0 or self.game.isEnd:
            return
        self.game.updateState((x, y))
        self.update_gui()

        win = self.game.winner((x, y))
        if win is not None:
            self.end_game(win)
            return

        ai_action = self.ai.chooseAction(self.game.availablePositions(), self.game.board, self.game.playerSymbol)
        self.game.updateState(ai_action)
        self.update_gui()

        win = self.game.winner(ai_action)
        if win:
            self.end_game(win)

    def update_gui(self):
        for i in range(self.row):
            for j in range(self.col):
                val = self.game.board[i][j]
                if val == 1:
                    self.buttons[i][j].config(text="X", state="disabled")
                elif val == -1:
                    self.buttons[i][j].config(text="O", state="disabled")

    def end_game(self, result):
        msg = "Hòa!"
        if result == 1:
            msg = "You win"
            self.ai.savePolicy()
        elif result == -1:
            msg = "AI Win"
            self.ai.savePolicy()
        tk.messagebox.showinfo("Kết thúc", msg)
        self.master.quit()

if __name__ == "__main__":
    import tkinter.messagebox
    root = tk.Tk()
    app = GameGUI(root, ROWS, COLS)
    root.mainloop()
