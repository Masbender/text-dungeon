from random import randint, choice
from extra import gather_input, clear_console
import entities
import color

c = color

player = entities.player

class Item:
    enchantable = False
    enchantment = 0
    
    def __init__(self, name, value, uses):
        self.name = name
        self.value = int(value * randint(9, 11) / 10) # 90% to 110% of value
        self.uses = uses
        self.maxUses = uses

    def degrade(self):
        # if INT is less than 0, there's a 10 * INT % chance that item degrades twice
        if player.intelligence < 0:
            if -randint(0, 99) > player.intelligence * 10:
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

            self.discard()
            if player.armor == self:
                player.armor = None
            elif player.ring == self:
                player.ring = None
            else:
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
            message += c.blessed(f" (+{self.enchantment})")
        elif self.enchantment < 0:
            message += c.cursed(f" (-{-self.enchantment})")

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

    def get_price(self, shop = False, returnString = False):
    # returns value based on uses and enchantment
    # shop indicates if the item is yours or a vendors
        price = int((self.value + (self.value * self.enchantment / 3)) * (self.uses / self.maxUses))

        if player.appraisal < price:
            if shop:
                price = int(price * 1.3)
            else:
                price = int(price * 0.7)

            if returnString:
                return str(price) + '?'

        if returnString:
            return str(price)
        else:
            return price

class Weapon(Item):
    enchantable = True
    
    def __init__(self, name, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " " + name, 10 + (20 * level), 15 + (10 * level))

        self.damage = 4 + level

    def degrade(self):
        # if INT is less than 0, there's a 7.5 * INT % chance that item degrades twice
        if player.intelligence < 0:
            if -randint(0, 99) > player.intelligence * 10:
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
        print(f"It does {self.damage + self.enchantment} damage, with a {self.bleedChance} in 6 chance to inflict bleeding for {self.bleedDuration} turns.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot inflict bleeding.")

        if self.enchantment < 0:
            print(f"The {self.name} is cursed")
        elif self.enchantment > 0:
            print(f"The {self.name} is blessed")
    
    def attack(self, enemies):
        damageDealt = self.damage - int(self.uses <= 0) + self.enchantment
        
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
            target.hurt(damageDealt, player.strength, message + ", leaving them bleeding")
        else:
            target.hurt(damageDealt, player.strength, message + "!")

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
        print(f"It does {self.damage + self.enchantment} damage and pierces {self.armorPiercing - 1} to {self.armorPiercing} points of armor.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot pierce armor.")

        if self.enchantment < 0:
            print(f"The {self.name} is cursed")
        elif self.enchantment > 0:
            print(f"The {self.name} is blessed")
    
    def attack(self, enemies):
        damageDealt = self.damage - int(self.uses <= 0) + self.enchantment

        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]

        # does damage and prints message, armor piercing has some randomness
        message = f"You stab the {target.name} with your spear for _ damage!"
        target.hurt(damageDealt, player.strength, message, (self.armorPiercing - randint(0, 1)) * int(self.uses > 0))

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
        print(f"It does {self.damage + self.enchantment} damage, with a {self.stunChance} in 12 chance to inflict stun.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot stun.")

        if self.enchantment < 0:
            print(f"The {self.name} is cursed")
        elif self.enchantment > 0:
            print(f"The {self.name} is blessed")
    
    def attack(self, enemies):
        damageDealt = self.damage - int(self.uses <= 0) + self.enchantment
        
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
        message = f"You hit the {target.name} with your mace for _ damage"
        if stunApplied:
            target.hurt(damageDealt, player.strength, message + ", leaving them stunned")
        else:
            target.hurt(damageDealt, player.strength, message + "!")

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
        print(f"It does {self.damage + self.enchantment} damage, and {self.firstHitDamage} extra damage towards enemies with full health.")
        print("Daggers add your dexterity to your attack, but ignore strength.")
        if self.uses < 0:
            print("Because it's broken it does less damage and doesn't gain bonus damage towards enemies with full health.")
        if self.enchantment < 0:
            print(f"The {self.name} is cursed")
        elif self.enchantment > 0:
            print(f"The {self.name} is blessed")

    def attack(self, enemies):
        damageDealt = self.damage - int(self.uses <= 0) + self.enchantment
        
        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        target = enemies[gather_input("Who do you attack?", options)]
        
        # applies first hit damage
        if target.health == target.maxHealth and self.uses > 0:
            damageDealt += self.firstHitDamage

        # does damage and prints message
        message = f"You stab {target.name} with your dagger for _ damage!"
        target.hurt(damageDealt, player.dexterity, message)

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

    def unequip(self):
        return False
    
class HeavyArmor(Armor):
# gives defense to player but lowers DEX
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]
        super().__init__(material + " armor", 20 + (25 * level), 20 + (12 * level))

        self.armorClass = level + 1
        self.dexLoss = 1
        if material == "iron" or material == "steel":
            self.dexLoss += 1

    def inspect(self):
        print(f"When equipped it gives you {self.armorClass + self.enchantment} armor class but lowers your dexterity by {self.dexLoss}.")

        if self.enchantment < 0:
            print(f"The {self.name} is cursed")
        elif self.enchantment > 0:
            print(f"The {self.name} is blessed")

    def consume(self, floor):
        self.equip()

        # applies stats
        player.armorClass += self.armorClass + self.enchantment
        player.update_dexterity(-self.dexLoss)

        print("You put on the " + self.name)
        return True

    def unequip(self):
        # this is where it unequips
        player.armorClass -= self.armorClass + self.enchantment
        player.update_dexterity(self.dexLoss)

class Cloak(Armor):
# provides 0 base armor, but +1 stealth
    def __init__(self, level):
        super().__init__("cloak", 40, 25)

    def inspect(self):
        print(f"When equipped it gives you {self.enchantment} armor class and increases your stealth by 1")

    def consume(self, floor):
        self.equip()

        # applies stats
        player.armorClass += self.enchantment
        player.stealth += 1

        print("You put on the cloak")
        return True

    def unequip(self):
        player.armorClass -= self.enchantment
        player.stealth -= 1
        
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

    def unequip(self):
        return False
    
class BuffRing(Ring):
# boosts one stat by 1 level
# 0 = stealth, 1 = dodge, 2 = health, 3 = resistance, 4 = awareness
    def __init__(self, ID = -1):
        super().__init__("ring of ", 50, 1)
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
            f"Increases your stealth by {1 + enchantment} level(s)",
            f"Increases your chance to dodge by {5 + 5 * enchantment}%",
            f"Increases your health by {2 + 2 * enchantment}",
            f"Increases your resistance to disease and injury by {1 + enchantment} level(s)",
            f"Increases your awareness of nearby threats by {1 + enchantment} level(s)"
        ][self.statID])

        if self.enchantment < 0:
            print(f"The {self.name} is cursed")
        elif self.enchantment > 0:
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
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1
            
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
        removedEffectsIndexes = []
        for i in range(len(player.effects)):
            if type(player.effects[i]) in self.effectsCured:
                removedEffectsIndexes.append(i)

        removedEffects = []
        removedEffectsIndexes.reverse()
        for i in removedEffectsIndexes:
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
        super().__init__("bandage", 30, 3, 4, entities.Regeneration, 4, [entities.Bleeding])

    def inspect(self):
        print(f"It heals around 4 HP and heals an addition 1 HP per turn for 4 turns.")
        print(f"Cures bleeding.")

# see gen_enemy() in entities.py for explanation
class Rations(Medicine):
# heals a lot of health but can't be used in combat
    def __init__(self):
        super().__init__("rations", 20, 1, 7, entities.WellFed, 4)

    def status(self):
        return ""
        
    def inspect(self):
        print("Eating the rations will heal around 7 health, and 8 more health over 4 turns.")
        print("You don't have enough time to eat this during combat.")

    def attack(self, enemies):
        print("you don't have enough time to eat!")
        return False

class Scroll(Item):
# one use item that is more powerful with higher intelligence
    def __init__(self, name, value):
        super().__init__(name, value, 1)

    def degrade(self):
        player.inventory.remove(self)
        return True

    def status(self):
        return ""

class ScrollRemoveCurse(Scroll):
# reverses curses from all items, has an INT in 4 chance to enchant
    def __init__(self):
        super().__init__("scroll of remove curse", 40)

    def inspect(self):
        print("Reverses every curse into blessings on all of your items")
        print("With higher levels of intelligence (INT), it might make them even stronger")
    
    def consume(self, floor):
        power = player.intelligence # intelligence boosts effectiveness
        
        for item in player.inventory: # cleanses each item
            if item.enchantment < 0:
                item.enchantment *= -1 # reverses curses

                if randint(0, 3) < power: # can improve item
                    item.enchantment += 1
                    print(f"{item.name} has been improved")

        self.degrade()
        print("all of your items have been uncursed")
        return True

class ScrollEnchant(Scroll):
# adds 1 + INT/2 levels of enchantment to an item
    def __init__(self):
        super().__init__("scroll of enchantment", 60)

    def inspect(self):
        print("This scroll will bless one of your items.")
        print("It's effect becomes stronger at higher levels of intelligence.")

    def consume(self, floor):
        power = player.intelligence // 2 # intelligence boosts effectiveness
        if power < 0: # power cannot be negative
            power = 0

        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(item.get_name())

        chosenItem = gather_input("What item do you upgrade?", options)

        if chosenItem == 0: # 0 cancels
            return False
        else:
            chosenItem -= 1 # converts to proper index
            if player.inventory[chosenItem].enchantable: # checks if item is valid
                player.inventory[chosenItem].enchantment += power + 1
                print(player.inventory[chosenItem].name + " has been improved")
                self.degrade()
                return True
            else:
                print(player.inventory[chosenItem].name + " cannot be enchanted")
                return False

class ScrollRepair(Scroll):
# fully repairs and item, higher levels of int increase its max uses
    def __init__(self):
        super().__init__("scroll of repair", 50)

    def inspect(self):
        print("This scroll will fully restore the uses of one item.")
        print("You intelligence (INT) can increase or decrease the item's durability.")

    def consume(self, floor):
        power = player.intelligence # intelligence boosts effectiveness

        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(item.get_name())

        chosenItem = gather_input("What item do you repair?", options)

        if chosenItem == 0: # 0 cancels
            return False
        else:
            chosenItem -= 1
            item = player.inventory[chosenItem]
            if item.maxUses > 1:
                item.maxUses += int(item.maxUses * power / 10)
                if power > 0:
                    print(item.name + " is more durable now")
                elif power < 0:
                    print(item.name + " is less durable now")
                    
                item.uses = item.maxUses
                print(item.name + " has been fully repaired")
                
                self.degrade()
                return True
            else:
                print(item.name + " does not work with the scroll of repair")
                return False
        
class Bomb(Item):
    def __init__(self):
        super().__init__("bomb", 35, 1)

    def status(self):
        return ""

    def inspect(self):
        print("Bombs can destroy walls, possibly revealing secrets.")
        print("It can be used in combat to harm all enemies.")

    def attack(self, enemies):
        for enemy in enemies:
            enemy.hurt(15, 0, f"The bomb does _ damage to {enemy.name}!")

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
class KnowledgeBook(Item):
# improves one stat
    def __init__(self):
        super().__init__("book of knowledge", 70, 1)

    def status(self):
        return ""

    def inspect(self):
        print("Reading this will let you improve one stat when you read it.")

    def consume(self, floor):
        print(f"{player.strength} STR | {player.constitution} CON | {player.dexterity} DEX | {player.perception} PER | {player.intelligence} INT")
        
        options = ["STR", "CON", "DEX", "PER", "INT"]
        chosenStat = gather_input("What stat do you improve?", options, False)

        if chosenStat == "STR":
            player.update_strength(1)
            print("your attacks are stronger now")
        elif chosenStat == "CON":
            player.update_constitution(1)
            print("your health and resistance to injury and disease has increased")
        elif chosenStat == "DEX":
            player.update_dexterity(1)
            print("your ability to dodge and go unnoticed has increased")
        elif chosenStat == "PER":
            player.update_perception(1)
            print("your ability to detect scams and enemies has increased")
        elif chosenStat == "INT":
            player.update_intelligence(1)
            print("the effectivenes of scrolls and durability of all items has increased")
        
        player.inventory.remove(self)
        return True


standardLoot = [(Rations, 6), (Bandage, 8), (ScrollRepair, 11), (ScrollRemoveCurse, 12), (ScrollEnchant, 13), (Bomb, 16)]

gearLoot = [(Sword, 2), (Mace, 4), (Spear, 6), (Dagger, 8), (Cloak, 9), (HeavyArmor, 12), (BuffRing, 16)]

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
            if not chosenItem in [Ring, Cloak]:
                # can be higher quality
                if randint(1, 4) == 1:
                    quality += 1

                gearLevel = (quality + 2) // 3
                if gearLevel > 3:
                    gearLevel = 3
                    
                chosenItem = item[0](gearLevel)

            else:
                chosenItem = item[0]()

            if type(chosenItem) in [Cloak]:
                chosenItem.enchantment += (quality + 2) // 5

            if chosenItem.enchantable:
                chosenItem.enchantment = randint(-1, 1)

            return chosenItem