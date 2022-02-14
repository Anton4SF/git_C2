class Ship:
    _directions = ('H', 'V')

    def __init__(self, coord, direction, size):
        self.__size = size
        self.__life = size
        self.__full_coord = []
        if coord is not None and coord != "":
            coord = coord.replace(" ", "")
            if coord[0].isalpha() and coord[1:].isdigit():
                self.__coord = coord.upper()
            elif coord[-1].isalpha() and coord[0:-1].isdigit():
                self.__coord = (coord[-1] + coord[0:-1]).upper()
            else:
                raise ValueError(f"Coordinate in {self.__repr__()} is incorrect")
        else:
            raise ValueError(f"Coordinate in {self.__repr__()} is empty")
        if direction.upper() in self.__class__._directions:
            self.__direction = direction.upper()
        else:
            raise ValueError(f"Direction in {self.__repr__()} is unknown")

    def __repr__(self):
        return f"{str(self.__class__).replace('__main__.', '')}"

    def take_damage(self):
        self.__life -= 1
        if self.__life > 0:
            return True
        else:
            return False

    @property
    def get_size(self):
        return self.__size

    @property
    def get_life(self):
        return self.__life

    @property
    def get_coord(self):
        return self.__coord

    @property
    def get_direction(self):
        return self.__direction

    @property
    def full_coord(self):
        return self.__full_coord

    @full_coord.setter
    def full_coord(self, coord_list):
        self.__full_coord = coord_list.copy()


class Aircarrier(Ship):
    def __init__(self, coord, direction):
        super(Aircarrier, self).__init__(coord, direction, 5)


class Cruiser(Ship):
    def __init__(self, coord, direction):
        super(Cruiser, self).__init__(coord, direction, 4)


class Frigate(Ship):
    def __init__(self, coord, direction):
        super(Frigate, self).__init__(coord, direction, 3)


class Destroyer(Ship):
    def __init__(self, coord, direction):
        super(Destroyer, self).__init__(coord, direction, 2)


class Patrol(Ship):
    def __init__(self, coord, direction):
        super(Patrol, self).__init__(coord, direction, 1)
