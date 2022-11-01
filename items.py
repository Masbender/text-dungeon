from random import randint, choice
from extra import gather_input, clear_console
import entities

player = entities.player

class Item:
    enchantable = False
    enchantments = 0
    
    def __init__(self, name, value, uses):
        self.name = name
        self.value = int(value * randint(7, 13) / 10) # 70% to 130% of value
        self.uses = uses
        self.maxUses = uses

    def degrade(self):
        # if INT is less than 0, there's a 10 * INT % chance that item degrades twice
        if player.intelligence < 0:
            if randint(0, -99) > player.intelligence * 10:
                self.uses -= 1
            self.uses -= 1
        # for every level of INT, there is a 10% that the item doesn't degrade
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

    def get_name(self):
        message = ""

        if self.status() != "":
            message += self.status() + " "

        message += self.name

        if self.enchantment > 0:
            message += f" (+{self.enchantment})"
        elif self.enchantment < 0:
            message += f" (-{-self.enchantment})"

        return message
        
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
    enchantable = True
    
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
            suffix = "broken"
        elif self.uses <= self.maxUses / 3:
            suffix = "damaged"
        elif self.uses <= self.maxUses * 2 / 3:
            suffix = "worn"

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
        print(f"It does {self.damage + self.enchantment} damage, with a {self.bleedChance} in 6 chance to inflict bleeding for {self.bleedDuration} turns.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot inflict bleeding.")

        if enchantment < 0:
            print(f"The {self.name} is cursed")
        elif enchantment > 0:
            print(f"The {self.name} is blessed")
    
    def attack(self, enemies):
        damageDealt = self.damage + player.strength - int(self.uses <= 0) + self.enchantment
        
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
            target.hurt(damageDealt, message + ", leaving them bleeding")
        else:
            target.hurt(damageDealt, message + "!")

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
        print(f"It does {self.damage + self.enchantment} damage and pierces {self.armorPiercing - 1} to {self.armorPiercing} points of armor.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot pierce armor.")

        if enchantment < 0:
            print(f"The {self.name} is cursed")
        elif enchantment > 0:
            print(f"The {self.name} is blessed")
    
    def attack(self, enemies):
        damageDealt = self.damage + player.strength - int(self.uses <= 0) + self.enchantment

        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]

        # does damage and prints message, armor piercing has some randomness
        message = f"You stab the {target.name} with your spear for _ damage!"
        target.hurt(damageDealt, message, (self.armorPiercing - randint(0, 1)) * int(self.uses > 0))

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
        print(f"It does {self.damage + self.enchantment} damage, with a {self.stunChance} in 12 chance to inflict stun.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot stun.")

        if enchantment < 0:
            print(f"The {self.name} is cursed")
        elif enchantment > 0:
            print(f"The {self.name} is blessed")
    
    def attack(self, enemies):
        damageDealt = self.damage + player.strength - int(self.uses <= 0) + self.enchantment
        
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
            target.hurt(damageDealt, message + ", leaving them stunned")
        else:
            target.hurt(damageDealt, message + "!")

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
        print(f"It does {self.damage + self.enchantment} damage, and {self.firstHitDamage} extra damage towards enemies with full health.")
        print("Daggers add your dexterity to your attack, but ignore strength.")
        if self.uses < 0:
            print("Because it's broken it does less damage and doesn't gain bonus damage towards enemies with full health.")
        if enchantment < 0:
            print(f"The {self.name} is cursed")
        elif enchantment > 0:
            print(f"The {self.name} is blessed")

    def attack(self, enemies):
        damageDealt = self.damage + player.dexterity - int(self.uses <= 0) + self.enchantment
        
        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]
        
        # applies first hit damage
        if target.health == target.maxHealth and self.uses > 0:
            damageDealt += self.firstHitDamage

        # does damage and prints message
        message = f"You hit {target.name} with your mace for _ damage!"
        target.hurt(damageDealt, message)

        self.degrade() # degrade is called when the item does something
        return True

class Armor(Item):
    enchantable = True
    
    def status(self):
        suffix = ""
        if self.uses <= self.maxUses / 3:
            suffix = "damaged"
        elif self.uses <= self.maxUses * 2 / 3:
            suffix = "worn"

        return f"{suffix}"

    def equip(self):
        if player.armor != None:
            player.inventory.append(player.armor)
            player.armor.unequip()
        player.armor = self
        player.inventory.remove(self)

    def attack(self, enemies):
        return self.consume(None)
    
class HeavyArmor(Armor):
# gives defense to player but lowers DEX
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " armor", 35 + (25 * level), 20 + (12 * level))

        self.armorClass = level + 1
        self.dexLoss = 1
        if material == "iron" or material == "steel":
            self.dexLoss += 1

    def inspect(self):
        suffix = self.status()
        if suffix == "":
            suffix = "new"
            
        print(f"The {self.name} looks {suffix.replace('(', '').replace(')', '')}.")
        print(f"When equipped it gives you {self.armorClass + self.enchantment} armor class but lowers your dexterity by {self.dexLoss}.")

        if enchantment < 0:
            print(f"The {self.name} is cursed")
        elif enchantment > 0:
            print(f"The {self.name} is blessed")

    def consume(self, floor):
        self.equip()

        # applies stats
        player.armorClass += self.armorClass + self.enchantment
        player.dexterity -= self.dexLoss

        print("You put on the " + self.name)
        return True

    def unequip(self):
        # this is where it unequips
        player.armorClass -= self.armorClass + self.enchantment
        player.dexterity += self.dexLoss

class Ring(Item):
    enchantable = True
    
    def status(self):
        return ""

    def equip(self):
        if player.ring != None:
            player.inventory.append(player.ring)
            player.ring.unequip()
        player.ring = self
        player.inventory.remove(self)

    def attack(self, enemies):
        return self.consume(None)
    
class BuffRing(Ring):
# boosts one stat by 1 level
# 0 = stealth, 1 = dodge, 2 = health, 3 = resistance, 4 = awareness
    def __init__(self, ID = -1):
        super().__init__("ring of ", 45, 1)
        # decides what stat is boosted
        self.statID = ID
        if ID < 0:
            self.statID = randint(0, 4)
            
        self.stat = ["stealth", "dodge", "health", "resistance", "awareness"][self.statID]
        self.name += ["shadows", "evasion", "resilience", "immunity", "vision"][self.statID]

    def inspect(self):
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1

        print([
            f"The ring of shadows increases your stealth by {1 + enchantment} level",
            f"The ring of evasion increases your chance to dodge by {5 + 5 * enchantment}%",
            f"The ring of resilience increases your health by {2 + 2 * enchantment}",
            f"The ring of immunity increases your resistance to disease and injury by {1 + enchantment} level",
            f"The ring of vision increases your awareness of nearby threats by {1 + enchantment} level"
        ][self.statID])

        if enchantment < 0:
            print(f"The {self.name} is cursed")
        elif enchantment > 0:
            print(f"The {self.name} is blessed")

    def consume(self, floor):
        self.equip()
        
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1
        
        if self.stat == "stealth":
            player.stealth += 1 + enchantment
            
        elif self.stat == "dodge":
            player.dodge += 5 + 5 * enchantment
            
        elif self.stat == "health":
            player.maxHealth += 2 + 2 * enchantment
            player.health += 2 + 2 * enchantment
            
        elif self.stat == "resistance":
            player.resistance += 1 + enchantment

        elif self.stat == "awareness":
            player.awareness += 1 + enchantment
        
        print("You put on the " + self.name)
        return True

    def unequip(self):
        if self.stat == "stealth":
            player.stealth -= 1 + enchantment
            
        elif self.stat == "dodge":
            player.dodge -= 5 + 5 * enchantment
            
        elif self.stat == "health":
            player.maxHealth -= 2 + 2 * enchantment
            player.health -= 2 + 2 * enchantment
            
        elif self.stat == "resistance":
            player.resistance -= 1 + enchantment

        elif self.stat == "awareness":
            player.awareness -= 1 + enchantment

class Medicine(Item): 
    def __init__(self, name, value, uses, healing, effectApplied = None, effectDuration = 0, effectsCured = []):
        super().__init__(name, value, uses)
        self.healing = healing
        self.effectApplied = effectApplied
        self.effectDuration = effectDuration
        self.effectsCured = effectsCured

    def attack(self, enemies):
    # attack does the same thing as consume
        return self.consume(None)

    def consume(self, floor):
        self.degrade()
        # heals and apples regeneration
        healingDone = player.heal(self.healing + randint(-1, 1))

        if self.effectApplied != None:
            player.affect(self.effectApplied, self.effectDuration)

        # cures bleeding
        removedEffects = []
        for i in range(len(player.effects)):
            if type(player.effects[i]) in self.effectsCured:
                removedEffects.append(player.effects[i].name)
                player.effects[i].reverse()
                player.effects.pop(i)
                player.effectDurations.pop(i)

        # prints out a message based on healing and removed effects
        message = f"the {self.name} restores {healingDone} health"
        if removedEffects != []:
            message += " and cures "
            if len(removedEffects) == 1:
                message += removedEffects[0]
            else:
                for i in range(len(removedEffects)):
                    if i == len(removedEffects) - 1:
                        message += ", and "
                    else:
                        message += ", "

                    message += removedEffects[i]

        print(message)

        return True

class Bandage(Medicine):
# cures bleeding, heals some health, and applies regeneration
    def __init__(self):
        super().__init__("bandage", 30, 3, 4, entities.Regeneration, 6, [entities.Bleeding])

    def inspect(self):
        print(f"The {self.name} has {self.uses} uses remaining.")
        print(f"It heals around 3 HP and heals an addition 1 HP per turn for 6 turns.")
        print(f"Cures bleeding.")

    def degrade(self):
    # value is based on uses
        super().degrade()
        self.value = 10 * self.uses

# see gen_enemy() in entities.py for explanation
class Rations(Medicine):
# heals a lot of health but can't be used in combat
    def __init__(self):
        super().__init__("rations", 20, 1, 7, entities.WellFed, 3)

    def status(self):
        return ""
        
    def inspect(self):
        print("Eating the rations will heal around 7 health, and 6 more health over 3 turns.")
        print("You don't have enough time to eat this during combat.")

    def attack(self, enemies):
        print("you don't have enough time to eat!")
        return False

class Bomb(Item):
    def __init__(self):
        super().__init__("bomb", 40, 1)

    def status(self):
        return ""

    def inspect(self):
        print("The bomb can destroy walls, possibly revealing secrets.")
        print("It can also be used in combat to harm all enemies.")

    def attack(self, enemies):
        for enemy in enemies:
            enemy.hurt(15, f"The bomb does _ damage to {enemy.name}!")

        player.inventory.remove(self)
        return True

    def dig(self):
        player.inventory.remove(self)
        print("the bomb explodes, after the rubble clears you see that the wall has collapsed")
        return True

class Key(Item):
    def __init__(self, tier):
        self.type = ["iron", "gold", "crystal"][tier]
        super().__init__(self.type + " key", (35 * tier) + 15, 1)

    def status(self):
        return ""

    def inspect(self):
        print(f"This key can open a {self.type} lock.")

    def unlock(self, lockType):
        if self.type == lockType:
            player.inventory.remove(self)
            print("the door opens")
            return True
        else:
            print("they key doesn't fit")
            return False


# number 1 through 16 is chosen
# if standardLoot = [(Rations, 8), (Bandage, 14), (Bomb, 16)]
# there is a 8 in 16 chance for rations, 6 in 16 chance for bandage, and 2 in 16 for bomb
standardLoot = [(Rations, 8), (Bandage, 14), (Bomb, 16)]

gearLoot = [(Sword, 2), (Mace, 4), (Spear, 6), (Dagger, 8), (HeavyArmor, 12), (BuffRing, 16)]

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
            chosenItem = None

            # quality improves the material of some items
            if not chosenItem in [Ring]:
                # can be higher quality
                if randint(1, 4) == 1:
                    quality += 1

                gearLevel = (quality + 2) // 3
                if gearLevel > 3:
                    gearLevel = 3
                    
                chosenItem = item[0](gearLevel)

            else:
                chosenItem = item[0]()

            if chosenItem.enchantable:
                chosenItem.enchantment = randint(-1, 1)

            return chosenItem