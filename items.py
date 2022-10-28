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

        # destroys item if uses are at 0
        if self.uses == 0:
            # if it is reusable it says when it breaks
            if self.maxUses > 1:
                print(self.name + " has broken")
                
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

    def consume(self, floor):
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

    def unequip(self):
    # only used for equippable items such as armor or rings
        return False
class Weapon(Item):
    def __init__(self, name, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " " + name, 30 + (20 * level), 15 + (10 * level))

        self.damage = 4 + level

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

        # destroys item if uses are at 0
        if self.uses == 0:
            # if it is reusable it says when it breaks
            if self.maxUses > 1:
                print(self.name + " has broken, it is much weaker now")
                self.uses -= 1 # prevents intelligence making this message appear again, doesn't break though
        return True
    
    def status(self):
        suffix = ""
        if self.uses <= 0:
            suffix = "(broken)"
        elif self.uses <= self.maxUses / 3:
            suffix = "(damaged)"
        elif self.uses <= self.maxUses * 2 / 3:
            suffix = "(worn)"

        return f"{suffix}"
        
class Sword(Weapon):
# does damage to target and can inflict bleeding
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        super().__init__("sword", level)
        
        self.bleedDuration = 4
        self.bleedChance = 2 # bleedChance is _ in 6

        if level >= 1:
            self.bleedChance += 1
        if level >= 2:
            self.bleedDuration += 1
        if level >= 3:
            self.bleedChance += 1
            self.bleedDuration += 1

    def inspect(self):
        suffix = self.status()
        if suffix == "":
            suffix = "new"
            
        print(f"The {self.name} looks {suffix.replace('(', '').replace(')', '')}.")
        print(f"It does {self.damage} damage, with a {self.bleedChance} in 6 chance to inflict bleeding for {self.bleedDuration} turns.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot inflict bleeding.")
    
    def attack(self, enemies):
        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]
        
        # applies bleeding
        bleedingApplied = False
        if randint(0, 5) < self.bleedChance and self.uses > 0:
            bleedingApplied = target.affect(entities.Bleeding, self.bleedDuration)

        # does damage and prints message
        message = f"You swing your sword at the {target.name} for _ damage"
        if bleedingApplied:
            target.hurt(self.damage + player.strength - int(self.uses <= 0), message + ", leaving them bleeding")
        else:
            target.hurt(self.damage + player.strength - int(self.uses <= 0), message + "!")

        self.degrade() # degrade is called when the item does something
        return True

class Spear(Weapon):
# does damage to target and has some armor piercing
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        super().__init__("spear", level)

        self.damage = 4 + level
        self.armorPiercing = (level + 3) // 2 # level/AP : 0/1, 1/2, 2/2, 3/3

    def inspect(self):
        suffix = self.status()
        if suffix == "":
            suffix = "new"
            
        print(f"The {self.name} looks {suffix.replace('(', '').replace(')', '')}.")
        print(f"It does {self.damage} damage and pierces {self.armorPiercing - 1} to {self.armorPiercing} points of armor.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot pierce armor.")
    
    def attack(self, enemies):

        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]

        # does damage and prints message, armor piercing has some randomness
        message = f"You stab the {target.name} with your spear for _ damage!"
        target.hurt(self.damage + player.strength - int(self.uses <= 0), message, (self.armorPiercing - randint(0, 1)) * int(self.uses > 0))

        self.degrade() # degrade is called when the item does something
        return True

class Mace(Weapon):
# does damage to target and can stun
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        super().__init__("mace", level)
        
        self.damage = 4 + level
        self.stunChance = (level + 3) // 2 # _ in 12, level/stunChance : 0/1, 1/2, 2/2, 3/3

    def inspect(self):
        suffix = self.status()
        if suffix == "":
            suffix = "new"
            
        print(f"The {self.name} looks {suffix.replace('(', '').replace(')', '')}.")
        print(f"It does {self.damage} damage, with a {self.stunChance} in 12 chance to inflict stun.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot stun.")
    
    def attack(self, enemies):
        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]
        
        # applies stun
        stunApplied = False
        if randint(0, 11) < self.stunChance and self.uses > 0:
            stunApplied = True
            target.stunned = True

        # does damage and prints message
        message = f"You hit {target.name} with your mace for _ damage"
        if stunApplied:
            target.hurt(self.damage + player.strength - int(self.uses <= 0), message + ", leaving them stunned")
        else:
            target.hurt(self.damage + player.strength - int(self.uses <= 0), message + "!")

        self.degrade() # degrade is called when the item does something
        return True

class Dagger(Weapon):
# does damage to target but uses DEX not STR, strong vs full hp enemies
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        super().__init__("dagger", level)

        self.damage = 4 + level
        self.firstHitDamage = (level + 3) // 2

    def inspect(self):
        suffix = self.status()
        if suffix == "":
            suffix = "new"
            
        print(f"The {self.name} looks {suffix.replace('(', '').replace(')', '')}.")
        print(f"It does {self.firstHitDamage} extra damage towards enemies with full health.")
        print("Daggers add your dexterity to your attack, but ignore strength.")
        if self.uses < 0:
            print("Because it's broken it does less damage and doesn't gain bonus damage towards enemies with full health.")

    def attack(self, enemies):
        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]
        
        # applies first hit damage
        bonusDamage = 0
        if target.health == target.maxHealth and self.uses > 0:
            bonusDamage = self.firstHitDamage

        # does damage and prints message
        message = f"You hit {target.name} with your mace for _ damage!"
        target.hurt(self.damage + player.dexterity + bonusDamage - int(self.uses <= 0), message)

        self.degrade() # degrade is called when the item does something
        return True

class Armor(Item):
# gives defense to player but lowers DEX
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " armor", 35 + (25 * level), 20 + (12 * level))

        self.armorClass = level + 1
        self.dexLoss = 1
        if material == "iron" or material == "steel":
            self.dexLoss += 1

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
        print(f"When equipped it gives you {self.armorClass} armor class but lowers your dexterity by {self.dexLoss}.")

    def consume(self, floor):
        # this is where it equips
        if player.armor != None:
            player.inventory.append(player.armor)
            player.armor.unequip()
        player.armor = self
        player.inventory.remove(self)

        # applies stats
        player.armorClass += self.armorClass
        player.dexterity -= self.dexLoss

        print("You put on the " + self.name)
        return True

    def attack(self, enemies):
        return self.consume(None)

    def unequip(self):
        # this is where it unequips
        player.armorClass -= self.armorClass
        player.dexterity += self.dexLoss

class Ring(Item):
# boosts one stat by 1 level
# 0 = stealth, 1 = dodge, 2 = health, 3 = resistance, 4 = awareness
    def __init__(self, ID = -1):
        super().__init__("ring of ", 45, 1)
        # decides what stat is boosted
        self.statID = ID
        if ID < 0:
            self.statID = randint(0, 5)
            
        self.stat = ["stealth", "dodge", "health", "resistance", "awareness"][self.statID]
        self.name += ["shadows", "evasion", "resilience", "immunity", "vision"][self.statID]

    def status(self):
        return ""

    def inspect(self):
        print([
            "The ring of shadows increases your stealth by 1 level",
            "The ring of evasion increases your chance to dodge by 5%",
            "The ring of resilience increases your health by 2",
            "The ring of immunity increases your resistance to disease and injury by 1 level",
            "The ring of vision increases your awareness of nearby threats by 1 level"
        ][self.statID])

    def consume(self, floor):
        # this is where it equips
        if player.ring != None:
            player.inventory.append(player.ring)
            player.ring.unequip()
        player.ring = self
        player.inventory.remove(self)

        if self.stat == "stealth":
            player.stealth += 1
            
        elif self.stat == "dodge":
            player.dodge += 5
            
        elif self.stat == "health":
            player.maxHealth += 2
            player.health += 2
            
        elif self.stat == "resistance":
            player.resistance += 1

        elif self.stat == "awareness":
            player.awareness += 1
        
        print("You put on the " + self.name)
        return True

    def attack(self, enemies):
        return self.consume(None)
    def unequip(self):
        if self.stat == "stealth":
            player.stealth -= 1
            
        elif self.stat == "dodge":
            player.dodge -= 5
            
        elif self.stat == "health":
            player.maxHealth -= 2
            player.health -= 2
            
        elif self.stat == "resistance":
            player.resistance -= 1

        elif self.stat == "awareness":
            player.awareness -= 1
        
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
        for enemy in enemies:
            enemy.hurt(15, f"The bomb does _ damage to {enemy.name}!")

        self.degrade()
        return True

    def dig(self):
        self.degrade()
        print("the bomb explodes, after the rubble clears you see that the wall has collapsed")
        return True

# stores values in tuples, (item, chance)
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
        return self.consume(None)

    def consume(self, floor):
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
                
        message = f"the bandage restores {healingDone} health"
        if bleedingCured:
            print(message + " and stops your bleeding")
        else:
            print(message)

        return True

# see gen_enemy() in entities.py for explanation
class Rations(Item):
# heals a lot of health but can't be used in combat
    def __init__(self):
        super().__init__("rations", 20, 1)

    def status(self):
        return ""
    def inspect(self):
        print("Eating the rations will heal you for 6 to 8 health, and 6 more health over 3 turns.")
        print("You don't have enough time to eat this during combat.")
    def consume(self, floor):
        player.inventory.remove(self)

        healingDone = player.heal(randint(6, 8))
        player.affect(entities.WellFed, 3)

        print(f"eating the rations restores {healingDone} health")

        return True

    def attack(self, enemies):
        print("you don't have enough time to eat!")
        return False

# number 1 through 16 is chosen
# if standardLoot = [(Rations, 8), (Bandage, 14), (Bomb, 16)]
# there is a 8 in 16 chance for rations, 6 in 16 chance for bandage, and 2 in 16 for bomb
standardLoot = [(Rations, 8), (Bandage, 14), (Bomb, 16)]

gearLoot = [(Sword, 2), (Mace, 4), (Spear, 6), (Dagger, 8), (Armor, 12), (Ring, 16)]

rareLoot = []

# generates an item such as a bomb or bandage
def gen_item(quality):
    # higher quality items have higher numbers
    itemNum = randint(1, 16) + quality

    # makes sure that the chosen number isn't too high
    if itemNum > standardLoot[-1][1]:
        itemNum = standardLoot[-1][1]

    # goes through each item until it finds one with a larger number than selected
    for item in standardLoot:
        if itemNum <= item[1]:
            chosenItem = item[0]

            return chosenItem()

# generates an item such as a sword or armor
def gen_gear(quality):
    itemNum = randint(1, 16)

    for item in gearLoot:
        if itemNum <= item[1]:
            chosenItem = item[0]

            # quality improves the material of some items
            if not chosenItem in [Ring]:
                # can be higher quality
                if randint(1, 4) == 1:
                    quality += 1
                
                return chosenItem((quality + 2)//3)
        
            return chosenItem()