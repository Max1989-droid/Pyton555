# ✸✸✸ Морской бой ✸✸✸

from random import randint

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы игрового поля"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.field = [["0"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "   | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1}  | " + " | ".join(row) + " |"

        if self.hide:
            res = res.replace("■", "0")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = color.RED + "X" + color.END
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print(color.RED + "Корабль уничтожен!" + color.END)
                    return False
                else:
                    print(color.RED + "Корабль повреждён!" + color.END)
                    return True

        self.field[d.x][d.y] = color.RED + "✸" + color.END
        print("Промах!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(color.YELLOW + f"Ход компьютера: {d.x + 1} {d.y + 1}" + color.END)
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input(color.PURPLE + "Ваш ход: " + color.END).split()

            if len(cords) != 2:
                print(color.RED + "Введите 2 координаты! " + color.END)
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(color.RED + "Введите числа! " + color.END)
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print(color.PURPLE + "------------------------")
        print("    Приветствуем вас    ")
        print("         в игре         ")
        print("       морской бой      ")
        print("------------------------" + color.END)
        print(color.YELLOW + "    формат ввода: x y   ")
        print("    x - номер строки    ")
        print("    y - номер столбца   " + color.END)

    def print_boards(self):
        print(color.PURPLE + "-" * 20)
        print("Доска пользователя:" + color.END)
        print(self.us.board)
        print(color.YELLOW + "-" * 20)
        print("Доска компьютера:" + color.END)
        print(self.ai.board)
        print(color.RED + "-" * 20 + color.END)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            print(color.PURPLE + "-" * 20)
            print("Доска пользователя:" + color.END)
            print(self.us.board)
            print(color.YELLOW + "-" * 20)
            print("Доска компьютера:" + color.END)
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print(color.PURPLE + "✅ Ходит пользователь!" + color.END)
                repeat = self.us.move()
            else:
                print(color.YELLOW + "✅ Ходит компьютер!" + color.END)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print(color.PURPLE + "-" * 20)
                print("✸✸✸Пользователь выиграл!✸✸✸" + color.END)
                break

            if self.us.board.defeat():
                self.print_boards()
                print(color.YELLOW + "-" * 20)
                print("✸✸✸Компьютер выиграл!✸✸✸" + color.END)
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()