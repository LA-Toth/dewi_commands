# Copyright 2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import random


class InvalidDie(ValueError):
    pass


class DieRoll:
    def __init__(self, count: int, sides: int, sides_str: str):
        self.count = count
        self.sides = sides
        self.sides_str = sides_str

    def roll(self):
        print(f'Rolling {self.count}d{self.sides_str}:')

        for i in range(self.count):
            roll = self._1_roll()
            if self.sides == 100:
                print(f'{i + 1:2d}: {roll:3d}%   =   {int(roll / 10) * 10:3d}  {roll % 10}')
            else:
                print(f'{i + 1:2d}: {roll:3d}')

    def _1_roll(self) -> int:
        return 1 + int(random.random() * self.sides)


class Die:
    def roll(self, dice: str | None = None):
        dice_str = dice or 'd6'

        dice = self._parse(dice_str)
        dice.roll()

        print()

    def _parse(self, dice_str: str) -> DieRoll:
        parts = dice_str.split('d')

        if len(parts) != 2:
            raise InvalidDie('A die must be in the form [COUNT]dTYPE, eg. d6 or 4d20, not: ' + dice_str)
        try:
            count = int(parts[0] or 1)
            if count < 1:
                raise InvalidDie('The dice count must be a non-negative integer, not: ' + parts[0])
        except ValueError:
            raise InvalidDie('The dice count must be a non-negative integer, not: ' + parts[0])

        if parts[1] in ['4', '6', '8', '10', '12', '20']:
            sides = int(parts[1])
        elif parts[1] == '%':
            sides = 100
        else:
            raise InvalidDie('The die sides must be 4, 6, 8, 10, 12, 20 or %, not: ' + parts[1])

        return DieRoll(count, sides, parts[1])
