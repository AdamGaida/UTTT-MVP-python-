import math
import random


class TreeNode():
    def __init__(self, board, parent):
        self.board = board
        self.is_terminal = board.is_win(board.main_board) or board.is_draw(board.main_board)
        self.is_fully_expanded = self.is_terminal
        self.parent = parent
        self.visits = 0
        self.score = 0
        self.children = {}


class MCTS():
    def search(self, initial_state):
        self.root = TreeNode(initial_state, None)
        for _ in range(1000):
            node = self.select(self.root)
            score = self.rollout(node.board)
            self.backpropagate(node, score)
        return self.get_best_move(self.root, 0)

    def select(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        legal_moves = node.board.generate_states()
        for move in legal_moves:
            new_state = node.board.make_move(*move)
            if str(new_state.sub_boards) not in node.children:
                new_node = TreeNode(new_state, node)
                node.children[str(new_state.sub_boards)] = new_node
                if len(legal_moves) == len(node.children):
                    node.is_fully_expanded = True
                return new_node

    def rollout(self, board):
        i=0
        while not board.is_win(board.main_board) and not board.is_draw(board.main_board)  and i <= 100:
            try:
                state = random.choice(board.generate_states())
                board.make_move(state[0], state[1], state[2], state[3])
                i+=1
            except:
                return 0
        if board.is_win(board.main_board):
            return 1 if board.player_2 == 'o' else -1
        else:
            return 0

    def backpropagate(self, node, score):
        while node is not None:
            node.visits += 1
            node.score += score
            node = node.parent

    def get_best_move(self, node, exploration_constant):
        best_score = float('-inf')
        best_moves = []
        for child_node in node.children.values():
            current_player = 1 if child_node.board.player_2 == 'x' else -1
            move_score = current_player * child_node.score / child_node.visits + exploration_constant * math.sqrt(
                math.log(node.visits / child_node.visits))
            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]
            elif move_score == best_score:
                best_moves.append(child_node)
        return random.choice(best_moves)


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
#eknokn'tohnkr"g
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

        mcts = MCTS()

        while True:
            self.print_board()
            legal_moves = self.generate_states()

            # Human player's turn
            if self.player_1 == 'x':
                user_input = input(f"Player 'x' move > ")

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
                        print('Player "x" has won the game!\n')
                        break

                    if self.is_draw(self.main_board):
                        self.print_board()
                        print('Game is drawn!\n')
                        break

                except Exception as e:
                    print('  Error:', e)
                    print('  Illegal command!')

            # AI's turn
            else:
                print("AI is making a move...")
                best_move = mcts.search(self)
                self = best_move.board

                if self.is_win(self.main_board):
                    self.print_board()
                    print('AI has won the game!\n')
                    break

                if self.is_draw(self.main_board):
                    self.print_board()
                    print('Game is drawn!\n')
                    break


if __name__ == '__main__':
    board = Board('x')
    board.game_loop()
