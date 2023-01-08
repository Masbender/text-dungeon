from random import randint, choice
from extra import gather_input, clear_console
import entities
import color

c = color

player = entities.player

class Item:
    enchantable = False
    enchantment = 0
    
    usePrompt = None # if this is None, then the inventory won't provide use as an options
    
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
    # runs when an item is added to inventory
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
                print(self.name + " has broken, it is much weaker now.")
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

    def attack(self, enemies):
        damageDealt = self.damage - 2 * int(self.uses <= 0) + self.enchantment

        options = [] # gets a list of enemy names
        for enemy in enemies:
            options.append(enemy.name)

        # gets player input
        self.target = enemies[gather_input("Who do you attack?", options)]
        
        return damageDealt

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
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)
        
        # applies bleeding
        bleedingApplied = False
        if randint(0, 5) < self.bleedChance and self.uses > 0:
            bleedingApplied = self.target.affect(entities.Bleeding, self.bleedDuration)

        # does damage and prints message
        message = f"You swing the {self.name} at the {self.target.name} for _ damage"
        if bleedingApplied:
            self.target.hurt(damageDealt, player.strength, message + ", leaving them bleeding")
        else:
            self.target.hurt(damageDealt, player.strength, message + "!")

        self.degrade() # degrade is called when the item does something
        return True

class JudgementSword(Sword):
# same as sword but extra damage and burning against undead
    def __init__(self):
        super().__init__(1)
        self.name = "Bane of the Undead" 
        self.value *= 2
        self.bleedChance += 1
        self.bleedDuration += 1

    def inspect(self):
        super().inspect()
        print("Stronger against undead enemies.")

    def attack(self, enemies):
        super().attack(enemies)

        # sets undead on fire
        if self.target.undead:
            self.target.affect(entities.Burned, 4)
            self.target.health -= 3
            print(f"{self.target.name} is burned by the sword, taking 4 extra damage.")
    
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
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        # does damage and prints message, armor piercing has some randomness
        message = f"You stab the {self.target.name} with the {self.name} for _ damage!"
        self.target.hurt(damageDealt, player.strength, message, (self.armorPiercing - randint(0, 1)) * int(self.uses > 0))

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
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)
        
        # applies stun
        stunApplied = False
        if randint(0, 11) < self.stunChance and self.uses > 0:
            stunApplied = True
            self.target.stunned = True

        # does damage and prints message
        message = f"You hit the {self.target.name} with your {self.name} for _ damage"
        if stunApplied:
            self.target.hurt(damageDealt, player.strength, message + ", leaving them stunned")
        else:
            self.target.hurt(damageDealt, player.strength, message + "!")

        self.degrade() # degrade is called when the item does something
        return True

class FlamingMace(Mace):
# same as mace can set enemies on fire
    def __init__(self):
        super().__init__(1)
        self.name = "Flaming Mace"
        self.value *= 2
        self.maxUses -= 5
        self.uses -= 5
        self.stunChance += 1

    def inspect(self):
        super().inspect()
        print("It also sets enemies on fire.")

    def attack(self, enemies):
        super().attack(enemies)

        if self.target.affect(entities.OnFire, randint(2, 3)):
            print(f"{self.target.name} is set on fire.")

        return True
        
class Dagger(Weapon):
# does damage to target but uses DEX not STR, strong vs surprised enemies
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level):
        super().__init__("dagger", level)

        self.damage = 4 + level
        self.sneakBonus = (level + 3) // 2

    def inspect(self):
        print(f"It does {self.damage + self.enchantment} damage, and {self.sneakBonus} extra damage towards surprised enemies.")
        print("Daggers use dexterity (DEX) instead of strength (STR).")
        if self.uses < 0:
            print("Because it's broken it does less damage and doesn't gain bonus damage towards enemies with full health.")

    def attack(self, enemies):
        damageDealt = super().attack(enemies)
        
        # applies stealth bonus damage
        for effect in self.target.effects:
            if isinstance(effect, entities.Surprised):
                damageDealt += self.sneakBonus
                break

        # does damage and prints message
        message = f"You stab {self.target.name} with your {self.name} for _ damage!"
        self.target.hurt(damageDealt, player.dexterity, message)

        self.degrade() # degrade is called when the item does something
        return True

class EbonyDagger(Dagger):
# same as a dagger, but gain max health per kill
    def __init__(self):
        super().__init__(1)
        self.name = "Ebony Dagger"
        self.value *= 2
        self.maxUses -= 5
        self.uses -= 5
        self.sneakBonus += 1

    def inspect(self):
        super().inspect()
        print("The Ebony Dagger increases your maximum health for every kill.")

    def attack(self, enemies):
        super().attack(enemies)

        # applies ebony dagger's effect
        if self.target.health <= 0:
            player.maxHealth += 1
            print("You absorb " + self.target.name + "'s power.")
        
        return True
    
class Armor(Item):
    enchantable = True

    usePrompt = "equip"
    
    def status(self):
        suffix = ""
        if self.uses <= self.maxUses / 3:
            suffix = "damaged"
        elif self.uses <= self.maxUses * 2 / 3:
            suffix = "worn"

        return f"{suffix}"

    def get_name(self):
        if self == player.armor:
            return super().get_name() + " (equipped)"
            
        return super().get_name()

    def put_on(self):
        if player.armor != None:
            #player.inventory.append(player.armor)
            player.armor.unequip()
        player.armor = self
        #player.inventory.remove(self)

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

    def consume(self, floor):
        self.equip()
        self.put_on()

    def equip(self):
        player.armorClass += self.armorClass + self.enchantment
        player.update_dexterity(-self.dexLoss)

    def unequip(self):
        # this is where it unequips
        player.armorClass -= self.armorClass + self.enchantment
        player.update_dexterity(self.dexLoss)

class Cloak(Armor):
# provides 0 base armor, but +1 stealth
    def __init__(self):
        super().__init__("cloak", 40, 25)

    def inspect(self):
        print(f"When equipped it gives you {self.enchantment} armor class and increases your stealth by 1.")

    def consume(self, floor):
        self.equip()
        self.put_on()

    def equip(self):
        # applies stats
        player.armorClass += self.enchantment
        player.stealth += 1

    def unequip(self):
        player.armorClass -= self.enchantment
        player.stealth -= 1

class ShadowCloak(Armor):
# same as cloak, but enchantments affect stealth, not armor
# starts enchanted
    def __init__(self):
        super().__init__("Cloak of Shadows", 70, 30)
        self.enchantment += 1

    def inspect(self):
        enchantment = self.enchantment
        if enchantment < 0: # ensures that -1 enchantment means -1 stealth
            enchantment -= 1
            
        print(f"When equipped it gives you 0 armor class but increases your stealth by {1 + enchantment}.")

    def consume(self, floor):
        self.equip()
        self.put_on()

    def equip(self):
        enchantment = self.enchantment
        if enchantment < 0: # ensures that -1 enchantment means -1 stealth
            enchantment -= 1

        # applies stats
        player.stealth += 1 + enchantment

    def unequip(self):
        enchantment = self.enchantment
        if enchantment < 0: # ensures that -1 enchantment means -1 stealth
            enchantment -= 1
        
        player.stealth -= 1 + enchantment
        
class Ring(Item):
    enchantable = True

    usePrompt = "equip"
    
    def status(self):
        return ""

    def get_name(self):
        if self == player.ring:
            return super().get_name() + " (equipped)"
            
        return super().get_name()

    def put_on(self):
        if player.ring != None:
            #player.inventory.append(player.ring)
            player.ring.unequip()
        player.ring = self
        #player.inventory.remove(self)

    def attack(self, enemies):
        return self.consume(None)

    def unequip(self):
        return False

class InfernoRing(Ring):
# increases strength, but burns you when attacked
    enchantable = True

    def __init__(self):
        super().__init__("Ring of Rage", 65, 1)

    def inspect(self):
        print("Increases your strength (STR) by 2.")
        print("When you are attacked, you might be burned (-1 AC).")
        print("The duration of burned depends on this items enchantment level.")

    def consume(self, floor):
        self.equip()
        self.put_on()

    def equip(self):
        player.strength += 2
        player.infernoRing = True

    def unequip(self):
        player.strength -= 2
        player.infernoRing = False

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
            f"Increases your stealth by {1 + enchantment} level(s).",
            f"Increases your chance to dodge by {5 + 5 * enchantment}%.",
            f"Increases your health by {2 + 2 * enchantment}.",
            f"Increases your resistance to disease and injury by {1 + enchantment} level(s).",
            f"Increases your awareness of nearby threats by {1 + enchantment} level(s)."
        ][self.statID])

    def consume(self, floor):
        self.equip()
        self.put_on()

    def equip(self):
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
    usePrompt = "use"

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
        message = f"The {self.name} restores {healingDone} health"
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

        print(message + ".")

        return True

class Bandage(Medicine):
# cures bleeding, heals some health, and applies regeneration
    def __init__(self):
        super().__init__("bandage", 30, 3, 4, entities.Regeneration, 4, [entities.Bleeding])

    def inspect(self):
        print(f"It heals around 4 HP and heals an addition 1 HP per turn for 4 turns.")
        print(f"Cures bleeding.")
        print(f"\nYou currently have {c.health_status(player.health, player.maxHealth)} health.")

# see gen_enemy() in entities.py for explanation
class Rations(Medicine):
# heals a lot of health but can't be used in combat
    usePrompt = "consume"

    def __init__(self):
        super().__init__("rations", 20, 1, 7, entities.WellFed, 4)

    def status(self):
        return ""
        
    def inspect(self):
        print("Eating the rations will heal around 7 health, and 8 more health over 4 turns.")
        print("You don't have enough time to eat this during combat.")
        print(f"\nYou currently have {c.health_status(player.health, player.maxHealth)} health.")

    def attack(self, enemies):
        print("You don't have enough time to eat!")
        return False

class Scroll(Item):
# one use item that is more powerful with higher intelligence
    usePrompt = "read"

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
        print("Reverses every curse into blessings on all of your items.")
        print("With higher levels of intelligence (INT), it might make them even stronger.")
    
    def consume(self, floor):
        power = player.intelligence # intelligence boosts effectiveness
        
        for item in player.inventory: # cleanses each item
            if item.enchantment < 0:
                item.enchantment *= -1 # reverses curses

                if randint(0, 3) < power: # can improve item
                    item.enchantment += 1
                    print(f"{item.name} has been improved.")

        self.degrade()
        print("All of your items have been uncursed.")
        return True

class ScrollEnchant(Scroll):
# adds 1 + INT/2 levels of enchantment to an item
    def __init__(self):
        super().__init__("scroll of enchantment", 60)

    def inspect(self):
        print("This scroll will bless one of your items.")
        print("It cannot be used on items with a higher level than your intelligence (INT).")

    def consume(self, floor):
        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(item.get_name())

        itemIndex = gather_input("What item do you bless?", options)

        if itemIndex == 0: # 0 cancels
            return False
        else:
            itemIndex -= 1 # converts to proper index
            chosenItem = player.inventory[itemIndex]

            if chosenItem.enchantment > player.intelligence: # checks intelligence
                print("That item is too high of a level for your intelligence.")
                return False
            
            if chosenItem.enchantable: # checks if item is valid
                if chosenItem == player.armor or chosenItem == player.ring:
                    chosenItem.unequip()

                chosenItem.enchantment += 1
                print(chosenItem.name + " has been blessed.")
                self.degrade()

                if chosenItem == player.armor or chosenItem == player.ring:
                    chosenItem.equip()
                return True
            else:
                print(chosenItem.name + " cannot be enchanted.")
                return False

class ScrollRepair(Scroll):
# fully repairs and item, higher levels of int increase its max uses
    def __init__(self):
        super().__init__("scroll of repair", 50)

    def inspect(self):
        print("This scroll will fully restore the uses of one item.")
        print("Your intelligence (INT) can increase or decrease the item's durability.")

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
            if item.maxUses > 1 or item.uses < 1: # only works on items that have multiple max uses or have no uses remaining

                if item.maxUses > 1: # only improves items with multiple uses
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
            damage = 15

            # does less damage against bosses (discourages spamming bombs)
            if issubclass(type(enemy), entities.Boss):
                damage = 8

            enemy.hurt(damage, 0, f"The bomb does _ damage to {enemy.name}!")

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
            print("the lock opens")
            return True
        else:
            print("the key doesn't fit")
            return False


# number 1 through 16 is chosen
# if standardLoot = [(Rations, 8), (Bandage, 14), (Bomb, 16)]
# there is a 8 in 16 chance for rations, 6 in 16 chance for bandage, and 2 in 16 for bomb
class KnowledgeBook(Item):
# improves one stat
    usePrompt = "read"

    def __init__(self):
        super().__init__("book of knowledge", 70, 1)

    def status(self):
        return ""

    def inspect(self):
        print("Reading this will let you level up one stat.")

    def consume(self, floor):
        print(f"{player.strength} STR | {player.constitution} CON | {player.dexterity} DEX | {player.perception} PER | {player.intelligence} INT")
        
        options = ["cancel", "STR", "CON", "DEX", "PER", "INT"]
        chosenStat = gather_input("What stat do you improve?", options, False)

        if chosenStat == "cancel":
            return False

        if chosenStat == "STR":
            player.update_strength(1)
            print("Your attacks are stronger now.")
        elif chosenStat == "CON":
            player.update_constitution(1)
            print("Your health has been increased, diseases and injuries heal quicker.")
        elif chosenStat == "DEX":
            player.update_dexterity(1)
            print("You are stealthier, you are better at dodging.")
        elif chosenStat == "PER":
            player.update_perception(1)
            print("You're more aware, you are a better at bargaining.")
        elif chosenStat == "INT":
            player.update_intelligence(1)
            print("Your items break less, scrolls are stronger.")
        
        player.inventory.remove(self)
        return True

class SeeingOrb(Item):
# reveals the whole map, requires a scroll of repair
    usePrompt = "gaze"

    def __init__(self):
        super().__init__("Seeing Orb", 85, 1)

    def status(self):
        if self.uses == 0:
            return "uncharged"
        else:
            return "charged"

    def consume(self, floor):
        if self.uses == 0:
            print("The orb needs to be charged with a scroll of repair before using it again.")
            return False

        self.uses -= 1

        floor.map = floor.layout
        print("You gaze into the orb, the whole floor has been revealed.")
        
        return True

    def pickup(self):
        player.update_perception(1)

    def discard(self):
        player.update_perception(-1)

    def inspect(self):
        print("Looking into the orb will reveal the entire layout of the floor.")
        print("Once used, it requires a scroll of repair to recharge it.")
        print("Having this item increases your perception (PER) by 1.")

standardLoot = [(Rations, 7), (Bandage, 10), (ScrollRepair, 11), (ScrollRemoveCurse, 12), (ScrollEnchant, 13), (Bomb, 16)]

gearLoot = [(Sword, 2), (Mace, 4), (Spear, 6), (Dagger, 8), (Cloak, 9), (HeavyArmor, 12), (BuffRing, 16)]

rareLoot = [ShadowCloak, InfernoRing, SeeingOrb, EbonyDagger, FlamingMace]

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

def gen_loot():
    return choice(rareLoot)()
            
# generates an item such as a sword or armor
def gen_gear(quality):
    itemNum = randint(1, 16)

    for item in gearLoot:
        if itemNum <= item[1]:
            chosenItem = None

            # quality improves the material of some items
            if not item[0] in [BuffRing, Cloak]:
                # can be higher quality
                if randint(1, 4) == 1:
                    quality += 1

                gearLevel = (quality + 2) // 3
                if gearLevel > 3:
                    gearLevel = 3
                    
                chosenItem = item[0](gearLevel)

            else:
                chosenItem = item[0]()

            if type(chosenItem) in [Cloak]: # cloaks are better the further they're found
                chosenItem.enchantment += (quality + 2) // 5

            if chosenItem.enchantable:
                chosenItem.enchantment = randint(-1, 1)

            return chosenItem