import numpy as np
from copy import deepcopy

class Board():
    def __init__(self, player_1, board=None):
        self.player_1 = player_1
        self.player_2 = 'o' if player_1 == 'x' else 'x'
        self.empty_square = '.'
        self.sub_boards = np.full((3, 3, 3, 3), '.', dtype=str)
        self.main_board = np.full((3, 3), self.empty_square, dtype=str)
        self.last_move = ()

        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)

    def print_board(self):
        for i in range(3):
            for x in range(3):
                for j in range(3):
                    print("|", end="")
                    for y in range(3):
                        print(f" {self.sub_boards[i, j, x, y]}", end="")
                print("|")
            print('-' * 21)

    def generate_states(self):
        actions = []
        last_move = self.last_move

        # Check if it's the first move
        if not last_move:
            # Allow moves in any small square of the entire board
            for big_row in range(3):
                for big_col in range(3):
                    for small_row in range(3):
                        for small_col in range(3):
                            if self.sub_boards[big_row, big_col, small_row, small_col] == self.empty_square:
                                actions.append((big_row, big_col, small_row, small_col))
        else:
            big_row, big_col = last_move[2], last_move[3]
            if self.main_board[big_row, big_col] == self.empty_square:
                for small_row in range(3):
                    for small_col in range(3):
                        if self.sub_boards[big_row, big_col, small_row, small_col] == self.empty_square:
                            actions.append((big_row, big_col, small_row, small_col))
            else:
                for big_row in range(3):
                    for big_col in range(3):
                        if self.main_board[big_row, big_col] == self.empty_square:
                            for small_row in range(3):
                                for small_col in range(3):
                                    if self.sub_boards[big_row, big_col, small_row, small_col] == self.empty_square:
                                        actions.append((big_row, big_col, small_row, small_col))
        return actions

    def make_move(self, big_row, big_col, small_row, small_col):
        board = deepcopy(self)
        board.sub_boards[big_row, big_col, small_row, small_col] = board.player_1

        if self.is_win(board.sub_boards[big_row, big_col]):
            board.main_board[big_row, big_col] = board.player_1
        elif self.is_draw(board.sub_boards[big_row, big_col]):
            board.main_board[big_row, big_col] = "x/o"

        board.player_1, board.player_2 = board.player_2, board.player_1
        board.last_move = (big_row, big_col, small_row, small_col)
        return board

    def is_draw(self, board):
        return not any(self.empty_square in row for row in board)

    def is_win(self, board):
        for col in range(3):
            if all(board[row, col] == self.player_1 for row in range(3)):
                return True

        for row in range(3):
            if all(board[row, col] == self.player_1 for col in range(3)):
                return True

        if all(board[i, i] == self.player_1 for i in range(3)):
            return True

        if all(board[i, 2 - i] == self.player_1 for i in range(3)):
            return True

        return False

    def game_loop(self):
        print('\n Ultimate Tic Tac Toe \n')
        print('  Type "exit" to quit the game')
        print('  Move format [big row, big col, small row, small col]: example 1,2,2,3 ')

        while True:
            self.print_board()
            legal_moves = self.generate_states()

            user_input = input(f"Player '{self.player_1}' move > ")

            if user_input == 'exit':
                break

            if user_input == '':
                continue

            try:
                big_row, big_col, small_row, small_col = map(lambda x: int(x) - 1, user_input.split(','))
                if (big_row, big_col, small_row, small_col) not in legal_moves:
                    print(' Illegal move!')
                    continue

                self = self.make_move(big_row, big_col, small_row, small_col)

                if self.is_win(self.main_board):
                    self.print_board()
                    print(f'Player "{self.player_2}" has won the game!\n')
                    break

                if self.is_draw(self.main_board):
                    self.print_board()
                    print('Game is drawn!\n')
                    break

            except Exception as e:
                print('  Error:', e)
                print('  Illegal command!')


if __name__ == '__main__':
    board = Board('x')
    board.game_loop()
