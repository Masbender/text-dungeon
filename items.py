from random import randint, choice
from extra import gather_input, clear_console
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
            if randint(0, -99) > player.intelligence * 10:
                self.uses -= 1
            self.uses -= 1
        # for every level of INT, there is a 7.5% that the item doesn't degrade
        else:
            if randint(0, 99) < player.intelligence * 10:
                return False
            else:
                self.uses -= 1

        if self.uses == 0:
            player.inventory.remove(self)
        return True

    def status(self):
        return f"({self.uses})"
    def inspect(self):
        print(f"This is a {self.name} with {self.status()} uses")
        
    def attack(self, enemies):
    # performs the items use in combat
        print(f"{self.name} has no use here")
        return False

    def consume(self):
    # performs the items use when there is no special prompt
        print(f"{self.name} has no use here")
        return False

    def unlock(self, lockType):
    # checks if the item can open a lockwall
        print(f"{self.name} isn't a key")
        return False

    def dig(self):
    # checks if the item can dig through a wall
        print(f"{self.name} can't dig")
        return False

    def pickup(self):
    # runs when an item is added to inventory, switches passive variables
        return False

    def discard(self):
    # runs when an item is dropped or destroyed, reverses pickup
        return False

class Sword(Item):
# does damage to target and can inflict bleeding
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " sword", 30 + (20 * level), 15 + (10 * level))
        
        self.damage = 4 + level
        self.bleedDuration = 4
        self.bleedChance = 2 # bleedChance is _ in 6

        if level >= 1:
            self.bleedChance += 1
        if level >= 2:
            self.bleedDuration += 1
        if level >= 3:
            self.bleedChance += 1
            self.bleedDuration += 1

    def status(self):
        suffix = ""
        if self.uses <= self.maxUses / 3:
            suffix = "(damaged)"
        elif self.uses <= self.maxUses * 2 / 3:
            suffix = "(worn)"

        return f"{suffix}"

    def inspect(self):
        suffix = self.status()
        if suffix == "":
            suffix = "new"
            
        print(f"The {self.name} looks {suffix.replace('(', '').replace(')', '')}.")
        print(f"It does {self.damage} damage, with a {self.bleedChance} in 6 chance to inflict bleeding for {self.bleedDuration} turns.")
    
    def attack(self, enemies):
        self.degrade() # degrade is called when the item does something

        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]
        
        # applies bleeding
        bleedingApplied = False
        if randint(0, 5) < self.bleedChance:
            bleedingApplied = target.affect(entities.Bleeding, self.bleedDuration)

        # does damage and prints message
        message = f"You swing your sword at the {target.name} for _ damage"
        if bleedingApplied:
            target.hurt(self.damage + player.strength, message + ", leaving them bleeding")
        else:
            target.hurt(self.damage + player.strength, message + "!")

        return True

class Bandage(Item):
# cures bleeding, heals some health, and applies regeneration
    def __init__(self):
        super().__init__("bandage", 30, 3)

    def inspect(self):
        print(f"The {self.name} has {self.uses} uses remaining.")
        print(f"It heals 2 to 4 HP and heals an addition 1 HP per turn for 6 turns.")
        print(f"Cures bleeding.")

    def degrade(self):
    # value is based on uses
        super().degrade()
        self.value = 10 * self.uses

    def attack(self, enemies):
    # attack does the same thing as consume
        return self.consume()

    def consume(self):
        self.degrade()
        # heals and apples regeneration
        healingDone = player.heal(randint(2, 4))
        player.affect(entities.Regeneration, 6)

        # cures bleeding
        bleedingCured = False
        for i in range(len(player.effects)):
            if type(player.effects[i]) == entities.Bleeding:
                player.effects[i].reverse()
                player.effects.pop(i)
                player.effectDurations.pop(i)
                bleedingCured = True
                break
                
        clear_console()
        message = f"the bandage restores {healingDone} health"
        if bleedingCured:
            print(message + " and stops your bleeding")
        else:
            print(message)

        return True

class Spear(Item):
# does damage to target and has some armor piercing
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " spear", 30 + (20 * level), 15 + (10 * level))

        self.damage = 4 + level
        self.armorPiercing = (level + 3) // 2 # level/AP : 0/1, 1/2, 2/2, 3/3

    def status(self):
        suffix = ""
        if self.uses <= self.maxUses / 3:
            suffix = "(damaged)"
        elif self.uses <= self.maxUses * 2 / 3:
            suffix = "(worn)"

        return f"{suffix}"

    def inspect(self):
        suffix = self.status()
        if suffix == "":
            suffix = "new"
            
        print(f"The {self.name} looks {suffix.replace('(', '').replace(')', '')}.")
        print(f"It does {self.damage} damage and pierces {self.armorPiercing - 1} to {self.armorPiercing} points of armor.")
    
    def attack(self, enemies):
        self.degrade() # degrade is called when the item does something

        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]

        # does damage and prints message, armor piercing has some randomness
        message = f"You stab the {target.name} with your spear for _ damage!"
        target.hurt(self.damage + player.strength, message, self.armorPiercing - randint(0, 1))

        return True

class Mace(Item):
# does damage to target and can stun, strong vs skeletons
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " mace", 30 + (20 * level), 15 + (10 * level))
        
        self.damage = 4 + level
        self.stunChance = (level + 3) // 2 # _ in 12, level/stunChance : 0/1, 1/2, 2/2, 3/3

    def status(self):
        suffix = ""
        if self.uses <= self.maxUses / 3:
            suffix = "(damaged)"
        elif self.uses <= self.maxUses * 2 / 3:
            suffix = "(worn)"

        return f"{suffix}"

    def inspect(self):
        suffix = self.status()
        if suffix == "":
            suffix = "new"
            
        print(f"The {self.name} looks {suffix.replace('(', '').replace(')', '')}.")
        print(f"It does {self.damage} damage, with a {self.stunChance} in 12 chance to inflict stun.")
    
    def attack(self, enemies):
        self.degrade() # degrade is called when the item does something

        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]
        
        # applies stun
        stunApplied = False
        if randint(0, 11) < self.stunChance:
            stunApplied = True
            target.stunned = True

        # does damage and prints message
        message = f"You hit {target.name} with your mace for _ damage"
        if stunApplied:
            target.hurt(self.damage + player.strength, message + ", leaving them stunned")
        else:
            target.hurt(self.damage + player.strength, message + "!")

        return True

class Bomb(Item):
    def __init__(self):
        super().__init__("bomb", 40, 1)

    def degrade(self):
        self.uses = 0
        return 

    def status(self):
        return ""

    def inspect(self):
        print("The bomb can destroy walls, possible revealing secrets.")
        print("It can also be used in combat to harm all enemies.")

    def attack(self, enemies):
        self.degrade()
        message = f"The bomb does _ damage to {target.name}!"

        for enemy in enemies:
            enemy.hurt(15, message)

        return True

    def dig(self):
        self.degrade()
        print("the bomb explodes, after the rubble clears you see that the wall has collapsed")
        return True

# stores values in tuples, (item, chance)
standardLoot = [
    [Sword, Spear, Mace, Bandage],
    [Sword, Spear, Mace, Bomb]
]

rareLoot = []
            
def gen_loot(quality):
    chosenItem = choice(standardLoot[quality])

    if chosenItem in [Sword, Mace, Spear]:
        return chosenItem(quality)

    return chosenItem()