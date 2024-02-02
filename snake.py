from collections import deque
import msvcrt
import os
from random import randint
import sys
import time

RESET_TEXT = '\u001b[0m'
COLOR_GREEN = '\u001b[32m'  # Green
COLOR_RED = '\u001b[31m'  # Red
BOLD_TEXT = '\u001b[1m'
BORDER_SYMBOL = '-'
CH_BACKGROUND = '\u001b[47;1m'
FOOD_CH = COLOR_RED + BOLD_TEXT + '*' + RESET_TEXT
SNAKE_BODY_CH = CH_BACKGROUND + ' '
DEFAULT_SPEED = 10  # Symbols per second
TITLE = COLOR_GREEN + BOLD_TEXT + 'S N A K E' + RESET_TEXT
DIRECTIONS = {
    'w': (-1, 0, 's'),
    'a': (0, -1, 'd'),
    's': (1, 0, 'w'),
    'd': (0, 1, 'a')
}


class Snake:
    def __init__(self, total_rows, total_cols):
        self.total_rows: int = total_rows
        self.total_cols: int = total_cols
        self.field: list[list[bool]] = [
            [False] * total_cols for _ in range(total_rows)
        ]
        self.create_field()

        self.start_row: int = (self.total_rows - 4) // 2 + 3
        self.start_col: int = self.total_cols // 2

        self.body = deque(maxlen=((self.total_rows - 4) * self.total_cols))
        self.head_pos: tuple(int, int) = (self.start_row, self.start_col)
        self.tail_pos: tuple(int, int) = (self.start_row, self.start_col)
        self.body.append(self.head_pos)
        self.body.append(self.tail_pos)

        self.food_pos: tuple(int, int)
        self.score: int = 0

    def clear_screen(self):
        # PH for other systems/terminals
        os.system('cls')

    def create_field(self):
        self.clear_screen()
        title = f'{TITLE}     SCORE: '
        sys.stdout.write(title + '\n')
        sys.stdout.write(BORDER_SYMBOL * self.total_cols + '\n')
        sys.stdout.write('\n' * (self.total_rows - 4))
        sys.stdout.write(BORDER_SYMBOL * self.total_cols)
        self.field[0] = [True] * self.total_cols
        self.field[1] = [True] * self.total_cols
        self.field[self.total_rows - 1] = [True] * self.total_cols
        self.field[self.total_rows - 2] = [True] * self.total_cols

    def draw_game_over(self):
        self.clear_screen()
        print(f'GAME OVER! Your score: {self.score}')
        sys.exit()

    def is_collision(self, row, col):
        if self.field[row - 1][col - 1] is True:
            return True
        return False

    def is_food(self, row, col):
        if (row, col) == self.food_pos:
            self.place_food()
            self.score += 1
            self.update_score()
            return True
        return False

    def restore_cursor_position(func):
        def wrapper(self, *args):
            sys.stdout.write('\u001b[s')
            func(self, *args)
            sys.stdout.write('\u001b[u')
            sys.stdout.flush()
        return wrapper

    def update_score(self):
        self.add_letter(1, 22, str(self.score))

    @restore_cursor_position
    def add_letter(self, row, col, letter):
        sys.stdout.write(f'\u001b[{row};{col}H' + letter)

    @restore_cursor_position
    def delete_letter(self, row, col):
        sys.stdout.write(f'\u001b[{row};{col}H' + ' ')
        self.field[row - 1][col - 1] = False

    def place_food(self):
        food_row = randint(3, self.total_rows - 3)
        food_col = randint(1, self.total_cols)
        if (food_row - 1, food_col - 1) in self.body:
            self.place_food()
        else:
            self.food_pos = (food_row, food_col)
            self.add_letter(*self.food_pos, FOOD_CH)

    def move_body(self, row, col):
        self.head_pos = (row, col)
        self.body.append(self.head_pos)
        self.add_letter(row, col, SNAKE_BODY_CH)
        self.field[row - 1][col - 1] = True
        if not self.is_food(*self.head_pos):
            self.tail_pos = self.body.popleft()
            self.delete_letter(*self.tail_pos)

    def run_snake(self):
        delta_row: int = 0
        delta_col: int = 1
        row: int = self.start_row
        col: int = self.start_col
        last_key: str = None
        curr_speed: int = DEFAULT_SPEED
        ignored_key: str = 'a'  # Default

        self.update_score()
        self.place_food()

        while True:
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()
                if key in DIRECTIONS and key != ignored_key:
                    if key == last_key:
                        curr_speed += DEFAULT_SPEED
                    else:
                        curr_speed = DEFAULT_SPEED
                    last_key = key
                    delta_row, delta_col, ignored_key = DIRECTIONS[key]
            row = (row + delta_row - 1) % self.total_rows + 1
            col = (col + delta_col - 1) % self.total_cols + 1
            if self.is_collision(row, col):
                self.draw_game_over()
            self.move_body(row, col)
            time.sleep(1 / curr_speed)


if __name__ == '__main__':
    # rows, cols = map(int, os.popen('stty size', 'r').read().split())
    cols, rows = os.get_terminal_size()
    snake = Snake(rows, cols)
    snake.run_snake()
