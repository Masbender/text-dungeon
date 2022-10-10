from random import randint
from extra import gather_input
import entities

player = entities.player

class Item:
    def __init__(self, name, value, uses):
        self.name = name
        self.value = int(value * randint(7, 13) / 10) # 70% to 130% of value
        self.uses = uses
        self.maxUses = uses

    def degrade(self):
        # if INT is less than 0, there's a 7.5 * INT % chance that item degrades twice
        if player.intelligence < 0:
            if randint(0, -99) > player.intelligence * 7.5:
                self.uses -= 1
            self.uses -= 1
            return True
        # for every level of INT, there is a 7.5% that the item doesn't degrade
        else:
            if randint(0, 99) < player.intelligence * 7.5:
                return False
            else:
                self.uses -= 1
                return True

    def status(self):
        return f"({uses} of {maxUses} uses)"
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

class Sword(Item):
# does damage to target and can inflict bleeding
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " sword", 30 + (20 * level), 15 + (10 * level))
        
        self.damage = 4 + level
        self.bleedDuration = 3
        self.bleedChance = 2 # bleedChance is _ of 6

        if level >= 1:
            bleedChance += 1
        if level >= 2:
            bleedDuration += 1
        if level >= 3:
            bleedChance += 1
            bleedDuration += 1

    def status(self):
        prefix = ""
        if self.uses < self.maxUses / 3:
            prefix = "damaged"
        elif slef.uses < self.maxUses * 2 / 3:
            prefix = "worn"

        return f"({prefix})"

    def attack(self, enemies):
        self.degrade() # degrade is called when the item does something

        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)
            
        target = enemies[gather_input("Who do you attack?", options)]

        message = f"You swing your sword at the {target.name} for _ damage"
        if randint(0, 5) < self.bleedChance:
            bleedApplied = target.affect(entities.Bleeding, self.bleedDuration)
            target.hurt(self.damage + player.strength, message + ", leaving them bleeding!")
        else:
            target.hurt(self.damage + player.strength, message + "!")

        return True