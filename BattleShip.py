from class_battlefield import BattleField
from class_ship import *
from platform import system as os
from os import system
from random import choice
from time import sleep


class Game:
    # service method for pretty output
    @staticmethod
    def clean_screen():
        sys = os()
        if sys == 'Linux':
            system('clear')
        elif sys == 'Windows':
            system('cls')
        else:
            for i in range(100):
                print('\n')

    # initialization of game field
    @staticmethod
    def create_user_field():
        while True:
            try:
                size = int(input("Введите размер игрового поля от 0 до 26:\n"))
            except ValueError:
                print("Введено недопустимое значние, не являющееся целым числом")
            else:
                try:
                    result = BattleField(size, 'player')
                except ValueError as error:
                    if str(error).find("is out of proper range") >= 0:
                        print("Введено значение вне допустимого диапазона")
                    else:
                        print("Произошла неизвестная ошибка")
                else:
                    return result

    # create field for pc's ships from reference (player's field)
    @staticmethod
    def create_pc_field(reference_field):
        size = reference_field.get_size
        return BattleField(size, 'pc')
    
    # print out player's field and pc's field side by side (user's field is on the left)
    @staticmethod
    def print_fields(user_field, pc_filed):
        user_field_row = user_field.iter_field()
        pc_field_row = pc_filed.iter_field()
        for i in range(user_field.get_size + 1):
            print(f"{next(user_field_row)}    {next(pc_field_row)}")
        print()

    # initialization of player's fleet by placing ships on field one by one
    @staticmethod
    def place_user_ships(field):
        while True:
            try:
                ship_type = int(input("Выберите тип размещаемого корабля (введите номер пункта из доступных):\n"
                                      "1. Авианосец\n"
                                      "2. Крейсер\n"
                                      "3. Фрегат\n"
                                      "4. Эсминец\n"
                                      "5. Катер\n"
                                      "0. Прекратить размещение кораблей\n"))
            except ValueError:
                print("Введено недопустимое значние, не являющееся целым числом")
                continue
            if ship_type == 0:
                Game.clean_screen()
                field.print_field()
                print("Расстановка кораблей завершена")
                break
            if ship_type not in range(0, 6):
                print("Выбран неизвестный тип корабля!")
                continue
            ship_coord = input("Введите координаты корабля, ближайшие к началу отсчёта координат:\n")
            ship_direction = input("Введите направление корабля: H - горизонтальное, V - вертикальное:\n")
            try:
                if ship_type == 1:
                    ship = Aircarrier(ship_coord, ship_direction)
                elif ship_type == 2:
                    ship = Cruiser(ship_coord, ship_direction)
                elif ship_type == 3:
                    ship = Frigate(ship_coord, ship_direction)
                elif ship_type == 4:
                    ship = Destroyer(ship_coord, ship_direction)
                elif ship_type == 5:
                    ship = Patrol(ship_coord, ship_direction)
            except ValueError as error:
                if str(error).find("is incorrect") >= 0:
                    print("Введены некорректные координаты!")
                elif str(error).find("is empty") >= 0:
                    print("Координаты не были введены!")
                elif str(error).find("Direction in") >= 0:
                    print("Введено неизвестное направление корабля!")
                else:
                    print("Произошла неизвестная ошибка")
            else:
                try:
                    field.place_ship(ship)
                except ValueError as error:
                    if str(error).find("is out of field") >= 0:
                        print("Корабль выходит за пределы поля!")
                    elif str(error).find("crosses other ship position") >= 0:
                        print("Корабль пересекается с другим кораблём!")
                    elif str(error).find("is near other ship position") >= 0:
                        print("Корабль соприкасается с другим кораблём!")
                    else:
                        print("Произошла неизвестная ошибка")
                else:
                    Game.clean_screen()
                    Game.print_fields(user_field, pc_field)

    # initialization of pc's fleet of symmetrical power with player's fleet
    @staticmethod
    def place_pc_ships(field, reference_field):
        # get ships from reference field
        composition = reference_field.fleet_composition
        # generate list of ship sizes: one item - one ship, item value - size of ship
        composition_detailed = []
        for size, number in composition.items():
            for _ in range(number):
                composition_detailed.append(size)
        # get full list of available coords on field
        full_coord_range = field.get_full_notation
        for i in composition_detailed:
            # exclude fields which are exactly not available
            full_occupied_fields = field.get_occupied_fields
            full_forbidden_fields = field.get_forbidden_fields
            selection_range = [j for j in full_coord_range
                               if j not in full_occupied_fields
                               and j not in full_forbidden_fields]
            while True:
                # generate random position and direction for ship
                rnd_position = choice(selection_range)
                rnd_direction = choice(['V', 'H'])
                # create ship
                if i == 1:
                    ship = Patrol(rnd_position, rnd_direction)
                elif i == 2:
                    ship = Destroyer(rnd_position, rnd_direction)
                elif i == 3:
                    ship = Frigate(rnd_position, rnd_direction)
                elif i == 4:
                    ship = Cruiser(rnd_position, rnd_direction)
                elif i == 5:
                    ship = Aircarrier(rnd_position, rnd_direction)
                # and try to place it on field
                try:
                    field.place_ship(ship)
                except ValueError:
                    # perform another attempt if failed
                    continue
                else:
                    # or go to next ship
                    break

    @staticmethod
    def battle(user_field, pc_field):
        starts_first = choice(['player', 'pc'])
        if starts_first == 'player':
            print("Первым стреляет игрок")
            while True:
                player_win = Game.user_shot(pc_field)
                if player_win:
                    break
                pc_win = Game.pc_shot(user_field)
                if pc_win:
                    break
        else:
            print("Первым стреляет компьютер")
            while True:
                pc_win = Game.pc_shot(user_field)
                if pc_win:
                    break
                player_win = Game.user_shot(pc_field)
                if player_win:
                    break

    @staticmethod
    def user_shot(pc_field):
        print("Ход игрока")
        go_on = True
        while go_on:
            Game.clean_screen()
            Game.print_fields(user_field, pc_field)
            shot = input("Введите координаты для залпа:\n")
            if shot is not None and shot != "":
                shot = shot.replace(" ", "")
                if shot[0].isalpha() and shot[1:].isdigit():
                    shot = shot.upper()
                elif shot[-1].isalpha() and shot[0:-1].isdigit():
                    shot = (shot[-1] + shot[0:-1]).upper()
                else:
                    print(f"Введена строка, не являющаяся допустимыми координатам")
                    continue
            try:
                hit = pc_field.exec_shot(shot)
            except ValueError as error:
                if str(error).find("is out of field") >= 0:
                    print("Нет такой координаты на поле!")
                    continue
                elif str(error).find("already was attacked previously") >= 0:
                    print("По этой точке уже делался выстрел!")
                    continue
            else:
                if hit:
                    print(f"Есть попадание в точке {shot}!")
                    any_alive = pc_field.fleet_exists
                    if any_alive:
                        print("Ещё один залп.")
                        sleep(3)
                        go_on = True
                    else:
                        print("Победа игрока! Все корабли противника уничтожены!")
                        sleep(10)
                        go_on = False
                        return True
                else:
                    print(f"Мимо, переход хода.")
                    sleep(3)
                    go_on = False
                    return False

    @staticmethod
    def pc_shot(user_field):
        print("Ход компьютера")
        full_coord_range = user_field.get_full_notation
        go_on = True
        while go_on:
            Game.clean_screen()
            Game.print_fields(user_field, pc_field)
            selection_range = []
            fired_fields = user_field.get_fired_fields
            if len(user_field.last_hit) > 0:
                selection_range = user_field.get_neighbor_coord(user_field.last_hit, 'cross')
                if len(selection_range) == 0:
                    user_field.last_hit = ""
                    selection_range = [i for i in full_coord_range
                                       if i not in fired_fields]
            else:
                selection_range = [i for i in full_coord_range
                                   if i not in fired_fields]
            shot = choice(selection_range)
            print(f"Компьютер стреляет по {shot}")
            hit = user_field.exec_shot(shot)
            if hit:
                print(f"Есть попадание в точке {shot}!")
                user_field.last_hit = shot
                any_alive = user_field.fleet_exists
                sleep(3)
                if any_alive:
                    go_on = True
                else:
                    print("Победа компьютера! Все корабли противника уничтожены!")
                    sleep(10)
                    go_on = False
                    return True
            else:
                print(f"Мимо, переход хода.")
                sleep(3)
                go_on = False
                return False


if __name__ == "__main__":
    user_field = Game.create_user_field()
    pc_field = Game.create_pc_field(user_field)
    Game.clean_screen()
    Game.print_fields(user_field, pc_field)
    Game.place_user_ships(user_field)
    Game.place_pc_ships(pc_field, user_field)
    Game.clean_screen()
    Game.print_fields(user_field, pc_field)
    Game.battle(user_field, pc_field)
