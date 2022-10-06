from random import
import entities

p = entities.player

class Item:
    def __init__(self, name, value, uses):
        self.name = name
        self.value = value
        self.uses = uses
        self.maxUses = uses

    def degrade(self):
    # for every level of INT, there is a 7.5% that the item doesn't degrade
    # for every level of INT less than 0, there is a 7.5% that the item degrades twice
        if p.intelligence < 0:
            if randint(0, 99) > p.intelligence * -7.5:
                self.uses -= 1
            self.uses -= 1
            return True
        else:
            if randint(0, 99) < p.intelligence * 7.5:
                return False
            else:
                self.uses -= 1
                return True

    def attack(self, enemies):
    # performs the items use in combat
        return False

    def consume(self):
    # performs the items use when there is no special prompt
        return False

    def unlock(self, lockType):
    # checks if the item can open a lock
        return False

    def dig(Self):
    # checks if the item can dig through a wall
        return False