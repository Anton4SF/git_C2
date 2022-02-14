class BattleField:
    _x_notation = ['line', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'L', 'K',
                   'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    _y_notation = list(range(0, 28))
    _cell_markers = {"empty": b'\xE2\xAC\x9C'.decode("utf-8"),
                     "ship": b'\xE2\xAC\x9B'.decode("utf-8"),
                     "miss": b'\xE2\x8A\xA1'.decode("utf-8"),
                     "hit": b'\xE2\x8A\xA0'.decode("utf-8")}
    _neighbors_modes = ('cross', 'all')
    _owner = ('player', 'pc')

    def __init__(self, size, owner):
        if 0 < size <= 26:
            self.__size = size
        else:
            raise ValueError(f"Field size in {self.__repr__()} is out of proper range")
        if owner in self.__class__._owner:
            self.__owner = owner
        else:
            raise ValueError(f"User in {self.__repr__()} is unknown")
        self.__field = []                                    # list of lists for all battle field coordinates init
        for _ in range(self.__size + 1):                     # and generate
            self.__field.append(["empty" for _ in range(self.__size + 1)])
        self.__field[0][0] = ""
        self.__x_notation = self.__class__._x_notation[0:self.__size + 1]  # names for X coordinates
        self.__y_notation = self.__class__._y_notation[0:self.__size + 1]  # names for Y coordinates
        for i in self.__x_notation[1:]:                                    # add X notations on top
            self.__field[0][self.__x_notation.index(i)] = i
        for i in self.__y_notation[1:]:                                    # add Y notations on left
            self.__field[i][0] = i
        self.__fleet = []                                                  # list of ship objects
        self.__occupied_fields = []                                        # ships positions
        self.__forbidden_fields = []                                       # forbidden positions around ships
        self.__attacked_fields = []                                        # positions which already were shot
        self.__last_shot = ""  # stores information about last successful shot which pc made on player's field

    def __repr__(self):
        return f"{str(self.__class__)}"

    # check if coordinate given in notation like 'C12' belongs to field
    def __belongs_field(self, coord):
        if coord[0] in self.__x_notation[1:] and int(coord[1:]) in self.__y_notation[1:]:
            return True
        else:
            return False

    # takes coordinate in notation like 'C12' and returns as list of indexes in self.__field [12, 3]
    def __translate_coord(self, coord):
        return [self.__y_notation.index(int(coord[1:])), self.__x_notation.index(coord[0])]

    # marks cell with coordinate given in notation like 'C12' with marker defined as mark from self._cell_markers.keys()
    def __mark_coord(self, coord, mark):
        if self.__belongs_field(coord):
            coord_yx = self.__translate_coord(coord)
        else:
            raise ValueError(f"Coordinate {coord} is out of field in {self.__repr__()}")
        if mark in self.__class__._cell_markers.keys():
            self.__field[coord_yx[0]][coord_yx[1]] = mark
        else:
            raise ValueError(f"Marker {mark} is illegal in {self.__repr__()}")

    # converts row of field given as list into printable line,
    # during conversion "empty", "ship", "miss" and "hit" strings will be converted into corresponding symbols,
    # other strings and values will be returned without conversion
    def __field_row_to_string(self, row):
        result = ""
        for i in row:
            if i in self.__class__._cell_markers.keys():
                if (i == "empty") or (i == "ship" and self.__owner == "pc"):
                    result += f"{self.__class__._cell_markers['empty']:^3}"
                else:
                    result += f"{self.__class__._cell_markers[i]:^3}"
            else:
                result += f"{str(i):^3}"
        return result

    # iterate over entire field row by row and print each row out
    def print_field(self):
        for i in self.__field:
            print(self.__field_row_to_string(i))

    # generator function, iterate over entire field and returns one properly formatted string in one turn
    def iter_field(self):
        for i in self.__field:
            yield self.__field_row_to_string(i)

    # get list of strings with entire coordinates of ship in notation like ['C2', 'C3', 'C4']
    # if generated coordinates run out of field, generation stops,
    # for further use of obtained coordinates check the len(list)
    def __get_ship_full_coord(self, ship):
        result = []
        if ship.get_direction == 'H':
            start = self.__x_notation.index(ship.get_coord[0])
            for i in range(start, start + ship.get_size):
                try:
                    result.append(self.__x_notation[i] + str(ship.get_coord[1:]))
                except IndexError:
                    break
        elif ship.get_direction == 'V':
            start = self.__y_notation.index(int(ship.get_coord[1:]))
            for i in range(start, start + ship.get_size):
                try:
                    result.append(ship.get_coord[0] + str(self.__y_notation[i]))
                except IndexError:
                    break
        else:
            raise ValueError(f"Direction in {self.__repr__()} is unknown")
        return result

    # get list of strings with coordinates of neighbor cells of given cell in notation like ['C2', 'C3', 'C4']
    # supports two modes - 'cross' and 'all' - returning up to 4 or 8 coordinates respectively
    # returns only coordinates belonging to field and which were not already fired
    # fired coordinates are excluded for purpose of better selection of next pc's move
    def get_neighbor_coord(self, coord, mode):
        result = []
        if not self.__belongs_field(coord):
            raise ValueError(f"Coordinate {coord} is out of field in {self.__repr__()}")
        if mode not in self._neighbors_modes:
            raise ValueError(f"Neighbors search mode {mode} is illegal in {self.__repr__()}")
        left_edge, right_edge = False, False
        if mode == 'cross' or mode == 'all':
            try:
                result.append(self.__x_notation[self.__x_notation.index(coord[0]) - 1] + coord[1:])
            except IndexError:
                left_edge = True
            try:
                result.append(self.__x_notation[self.__x_notation.index(coord[0]) + 1] + coord[1:])
            except IndexError:
                right_edge = True
            result.append(coord[0] + str(int(coord[1:]) - 1))
            result.append(coord[0] + str(int(coord[1:]) + 1))
        if mode == 'all':
            if left_edge is False:
                result.append(self.__x_notation[self.__x_notation.index(coord[0]) - 1] + str(int(coord[1:]) - 1))
                result.append(self.__x_notation[self.__x_notation.index(coord[0]) - 1] + str(int(coord[1:]) + 1))
            if right_edge is False:
                result.append(self.__x_notation[self.__x_notation.index(coord[0]) + 1] + str(int(coord[1:]) - 1))
                result.append(self.__x_notation[self.__x_notation.index(coord[0]) + 1] + str(int(coord[1:]) + 1))
        result_validated = []
        for i in result:
            if self.__belongs_field(i) and i not in self.__attacked_fields:
                result_validated.append(i)
        return result_validated

    # get list of strings with forbidden coordinates around ship in notation like ['C2', 'C3', 'C4']
    # input full_coord takes full list of ship's coordinates
    def __get_ship_forbidden_coord(self, full_coord):
        result = []
        for i in full_coord:
            result.extend(self.get_neighbor_coord(i, 'all'))
        result_validated = []
        for i in result:
            if i not in full_coord:
                result_validated.append(i)
        result_validated = list(set(result_validated))
        return result_validated

    # take object of class Ship or it's ancestors, validate it and place on field
    def place_ship(self, ship):
        full_coord = self.__get_ship_full_coord(ship)
        if len(full_coord) < ship.get_size:
            raise ValueError(f"Ship {ship} is out of field in {self.__repr__()}")
        else:
            for i in full_coord:
                if i in self.__occupied_fields:
                    raise ValueError(f"Ship {ship} crosses other ship position at {full_coord} in {self.__repr__()}")
                if i in self.__forbidden_fields:
                    raise ValueError(f"Ship {ship} is near other ship position at {full_coord} in {self.__repr__()}")
            self.__fleet.append(ship)
            ship.full_coord = full_coord.copy()
            self.__occupied_fields.extend(full_coord)
            for i in full_coord:
                self.__mark_coord(i, 'ship')
            self.__forbidden_fields.extend(self.__get_ship_forbidden_coord(full_coord))

    # determines to which ship of fleet the coordinate given as 'C12' belongs,
    # returns either link to object from self.__fleet or false if no ship was found
    def __which_ship(self, coord):
        for i in self.__fleet:
            if coord in i.full_coord:
                return i
        return False

    # execute shot to coordinate given in notation like 'C12'
    # if shot hits the ship, returns True, else returns False,
    # if ship was killed with the shot, all surrounding cells will be marked as attacked
    def exec_shot(self, coord):
        if self.__belongs_field(coord):
            if coord in self.__occupied_fields:
                ship = self.__which_ship(coord)
                if ship.take_damage() is False:
                    for i in self.__get_ship_forbidden_coord(ship.full_coord):
                        self.__attacked_fields.append(i)
                        self.__mark_coord(i, 'miss')
                    self.__fleet.remove(ship)
                self.__occupied_fields.remove(coord)
                self.__attacked_fields.append(coord)
                self.__mark_coord(coord, 'hit')
                return True
            elif coord in self.__attacked_fields:
                raise ValueError(f"Coordinate {coord} already was attacked previously in {self.__repr__()}")
            else:
                self.__attacked_fields.append(coord)
                self.__mark_coord(coord, 'miss')
                return False
        else:
            raise ValueError(f"Coordinate {coord} is out of field in {self.__repr__()}")

    @property
    def get_size(self):
        return self.__size

    @property
    def get_full_notation(self):
        full_coord_range = []
        for i in self.__y_notation[1:]:
            for j in self.__x_notation[1:]:
                full_coord_range.append(f"{j}{i}")
        return full_coord_range
    
    @property
    def get_fired_fields(self):
        return self.__attacked_fields

    @property
    def get_occupied_fields(self):
        return self.__occupied_fields

    @property
    def get_forbidden_fields(self):
        return self.__forbidden_fields

    @property
    def fleet_exists(self):
        return bool(len(self.__fleet))

    @property
    def fleet_composition(self):
        result = {}
        for i in self.__fleet:
            size = i.get_size
            if size in result.keys():
                result[size] += 1
            else:
                result[size] = 1
        return result

    @property
    def last_hit(self):
        return self.__last_shot

    @last_hit.setter
    def last_hit(self, coord):
        self.__last_shot = coord
