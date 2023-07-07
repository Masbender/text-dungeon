
import math
from random import randint, choice
import textdungeon.color as color
import textdungeon.entities as entities
from textdungeon.extra import gather_input, slowprint, add_message

c = color

player = entities.player

class Item:
    name = "item"
    value = 10
    enchantValue = 0.4 # +20% of price per level of enchantment
    maxUses = 1

    enchantable = False
    enchantment = 0
    
    usePrompt = None # if this is None, then the inventory won't provide use as an options
    
    canDig = False # determines if an item can break walls

    def __init__(self):
        self.value = int(self.value * randint(9, 11) / 10) # 90% to 110% of value
        self.uses = self.maxUses

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
                add_message(c.red(self.name + " has broken"))

            self.discard()
            for key in player.gear.keys():
                if player.gear[key] == self:
                    player.gear[key] = None
                    self.unequip()
            
            player.inventory.remove(self)
        return True

    def status(self):
        return f"({self.uses} uses)"

    def get_name(self):
        message = ""

        if self.status() != "":
            message += self.status() + " "

        message += self.name

        if self.enchantment > 0:
            message += c.green(f" (+{self.enchantment})")
        elif self.enchantment < 0:
            message += c.red(f" (-{-self.enchantment})")

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

    def recharge(self):
    # runs for every item when player descends a floor
        return False
    
    def get_price(self):
        return int((self.value + (self.value * self.enchantValue * self.enchantment)) * (self.uses / self.maxUses / 2 + 0.5))

class Weapon(Item):
    enchantable = True
    enchantValue = 0.2
    
    def __init__(self, name, level):
        if type(self) in [Sword, Mace, Spear, Dagger]:
            material = ["bronze", "iron", "steel", "mithril"][level]
    
            self.name = material + " " + name
            self.value = 50 * level
            self.maxUses = 15 + (10 * level)
    
            self.damage = 4 + level

        super().__init__()

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
                add_message(c.red(self.name + " has broken, making it much weaker"))
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

        if len(enemies) == 1:
            self.target = enemies[0]
        else:
            options = [] # gets a list of enemy names
            for enemy in enemies:
                options.append(enemy.name)
    
            # gets player input
            self.target = enemies[gather_input("Who do you attack?", options)]

        self.degrade()
        
        return damageDealt

class Sword(Weapon):
# does damage to target and can inflict bleeding
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level = 0):
        super().__init__("sword", level)

        if type(self) == Sword:
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
        gcd = math.gcd(self.bleedChance, 6)
        print(f"Does {c.compare(self.damage + self.enchantment, self.damage)} damage, with a {self.bleedChance // gcd} in {6 // gcd} chance to inflict bleeding for {self.bleedDuration} turns.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot inflict bleeding.")
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        if self.target.dodge(player):
            print(f"{self.target.name} dodges your attack!")
            return True
            
        damageDealt = self.target.hurt(player, damageDealt)

        if randint(0, 5) < self.bleedChance and self.uses > 0:
            self.target.affect(entities.Bleeding(), self.bleedDuration)
            print(f"You attack {self.target.name} for {c.red(damageDealt)} damage, leaving them {c.effect(entities.Bleeding)}.")
        else:
            print(f"You attack {self.target.name} for {c.red(damageDealt)} damage.")

        return True

class CursedSword(Sword):
# same as sword but extra damage and burning against undead
    name = "Cursed Blade"
    value = 100
    maxUses = 16

    enchantment = -1
    enchantable = False

    damage = 5
    bleedChance = 3
    bleedDuration = 7

    usePrompt = "sacrifice health"
    
    def inspect(self):
        self.enchantment *= -1
        super().inspect()
        self.enchantment *= -1
        print(f"Becomes stronger when cursed {c.red('(-)')}, but weaker when blessed {c.green('(+)')}.")
        print("You can permanently sacrifice health to increase the swords strength. ")
        print(f"You currently have {c.health_status(player.health, player.maxHealth)} health.")

    def consume(self, floor):
        self.uses = self.maxUses
        healthLost = 1
        # becomes more expensive depending the level of curse
        if self.enchantment < 0:
            healthLost -= self.enchantment
            
        self.enchantment -= 1
        self.bleedDuration += 1
        player.maxHealth -= healthLost
        player.health -= healthLost

        player.affect(entities.Bleeding(), healthLost)

        print(f"Your sacrifice of {c.red(healthLost)} health makes the blade stronger.")
        return True
    
    def attack(self, enemies):
        self.enchantment *= -1
        super().attack(enemies)
        self.enchantment *= -1

        return True

class Spear(Weapon):
# does damage to target and has some armor piercing
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level = 0):
        super().__init__("spear", level)

        if type(self) == Spear:
            self.armorPiercing = (level + 3) // 2 # level/AP : 0/1, 1/2, 2/2, 3/3

    def inspect(self):
        print(f"Does {c.compare(self.damage + self.enchantment, self.damage)} damage and pierces {self.armorPiercing} points of armor class.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot pierce armor.")
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        if self.target.dodge(player):
            print(f"{self.target.name} dodges your attack!")
            return True
            
        damageDealt = self.target.hurt(player, damageDealt, self.armorPiercing)

        print(f"You attack {self.target.name} for {c.red(damageDealt)} damage.")
        return True

class EnchantedSpear(Spear):
# same as spear but has high piercing and ignores dodge
    name = "Enchanted Spear"
    value = 100
    maxUses = 25

    damage = 6
    armorPiercing = 10

    def inspect(self):
        super().inspect()
        print("This spear cannot be dodged.")

    def attack(self, enemies):
        dodgeChances = [] # saves and removes enemy dodge chance
        for enemy in enemies:
            dodgeChances.append(enemy.dodgeChance)
            enemy.dodgeChance = 0

        super().attack(enemies)

        for i in range(len(enemies)): # restores enemy dodge chance
            enemies[i].dodgeChance = dodgeChances[i]

        return True

class Mace(Weapon):
# does damage to target and can stun
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level = 0):
        super().__init__("mace", level)
        
        if type(self) == Mace:
            self.stunChance = (level + 3) // 2 # _ in 12, level/stunChance : 0/1, 1/2, 2/2, 3/3

    def inspect(self):
        gcd = math.gcd(self.stunChance, 12)
        print(f"Does {c.compare(self.damage + self.enchantment, self.damage)} damage, with a {self.stunChance // gcd} in {12 // gcd} chance to stun enemies.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot stun.")
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        if self.target.dodge(player):
            print(f"{self.target.name} dodges your attack!")
            return True
            
        damageDealt = self.target.hurt(player, damageDealt)

        if randint(0, 11) < self.stunChance and self.uses > 0:
            self.target.stunned = True
            print(f"You attack {self.target.name} for {c.red(damageDealt)} damage, leaving them {c.red('stunned')}.")
            return True

        print(f"You attack {self.target.name} for {c.red(damageDealt)} damage.")
        return True

class FlamingMace(Mace):
# same as mace can set enemies on fire
    name = "Flaming Mace"
    value = 100
    maxUses = 20

    damage = 5
    stunChance = 2

    def inspect(self):
        super().inspect()
        print("It sets enemies on fire, dealing damage over time and lowering their armor class (AC).")

    def attack(self, enemies):
        super().attack(enemies)

        self.target.affect(entities.OnFire(), randint(2, 3))

        return True
        
class Dagger(Weapon):
# does damage to target but uses DEX not STR, strong vs surprised enemies
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level = 0):
        super().__init__("dagger", level)

        if type(self) == Dagger:
            self.sneakBonus = level + 2

    def inspect(self):
        print(f"Does {c.compare(self.damage + self.enchantment, self.damage)} damage, and {self.sneakBonus} extra damage towards surprised enemies.")
        print("Does not gain any bonuses from strength (STR).")
        if self.uses < 0:
            print("Because it's broken it does less damage and doesn't do extra damage.")

    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        if self.target.dodge(player):
            print(f"{self.target.name} dodges your attack!")
            return True

        if self.target.has_effect(entities.Surprised):
            damageDealt += self.sneakBonus
            print("Sneak attack!")

        damageDealt = self.target.hurt(player, damageDealt, 0, 0)

        print(f"You attack {self.target.name} for {c.red(damageDealt)} damage.")
        return True

class EbonyDagger(Dagger):
# same as a dagger, but gain max health per kill
    name = "Ebony Dagger"
    value = 100
    maxUses = 50

    damage = 5
    sneakBonus = 4

    def inspect(self):
        super().inspect()
        print(f"This durable weapon heals you whenever you get a kill.")

    def attack(self, enemies):
        super().attack(enemies)

        # applies ebony dagger's effect
        if self.target.health <= 0:
            healing = player.heal(randint(5, 7))
            print("You absorb " + c.green(healing) + " health from " + self.target.name + ".")
        
        return True

class Wand(Item):
# recharges some uses every floor
    name = "wand"
    value = 50
    maxUses = 3

    enchantable = True

    reqInt = 1 # level of INT required to use the wand

    def status(self):
        return f"({self.uses + self.enchantment}/{self.maxUses + self.enchantment} charges)"

    def degrade(self):
        # if INT is less than 0, there's a 7.5 * INT % chance that item degrades twice
        if player.intelligence < 0:
            if -randint(0, 99) > player.intelligence * 10:
                self.uses -= 1
            self.uses -= 1
        # for every level of INT, there is a 7.5% that the item doesn't degrade
        else:
            if randint(0, 99) < player.intelligence * 10:
                print("Your wand gets a free charge because of your INT.")
                return False
            else:
                self.uses -= 1
                
        return True

    def recharge(self):
        self.uses += player.recharge
        
        if self.uses > self.maxUses:
            self.uses = self.maxUses

    def attack(self, enemies):
    # chooses a target
        if player.intelligence < self.reqInt:
            print(f"This wand requires {self.reqInt} intelligence (INT) to use!")
            return False
        
        if self.uses + self.enchantment > 0:
            target = enemies[0]
            
            if len(enemies) > 1:
                options = [] # gets a list of enemy names
                for enemy in enemies:
                    options.append(enemy.name)
        
                # gets player input
                target = enemies[gather_input("Who do you attack?", options)]
    
            self.degrade()
    
            return self.cast(target)
        else:
            print("That wand doesn't have enough charges!")
            return False

    def cast(self, target):
        return True

class HarmWand(Wand):
# (req 2 INT, 4 charges) does 5 + x direct damage, inflicts bleeding for x turns
    name = "wand of harming"
    value = 70
    maxUses = 4

    reqInt = 2

    def inspect(self):
        print(f"Does {5 + self.enchantment} direct damage to target.")
        if self.enchantment > 0:
            print(f"Inflicts target with bleeding for {self.enchantment} turns.")
        print("Requires at least 2 intelligence (INT).")

    def cast(self, target):
        target.health -= 5 + self.enchantment

        if self.enchantment > 0:
            target.affect(entities.Bleeding(), self.enchantment)
            print(f"Your wand of harm does {c.red(5 + self.enchantment)} damage to {target.name}, leaving them {c.effect(entities.Bleeding)}.")
            return True

        print(f"Your wand of harm does {c.red(5 + self.enchantment)} damage to {target.name}.")
        return True

class PoisonWand(Wand):
# (req 1 INT, 3 charges) inflicts poisoned for 5 + x turns, does x direct damage
    name = "wand of poison"
    value = 50
    maxUses = 3

    reqInt = 1

    def inspect(self):
        print(f"Inflicts poison to target for {7 + self.enchantment} turns.")
        if self.enchantment > 0:
            print(f"Does {self.enchantment} direct damage.")
        print("Requires at least 1 intelligence (INT).")

    def cast(self, target):
        target.affect(entities.Poisoned(), 7 + self.enchantment)

        if self.enchantment > 0:
            target.health -= self.enchantment
            print(f"Your wand of poison does {c.red(self.enchantment)} damage to {target.name}, and inflicts {c.effect(entities.Poisoned)}.")
            return True

        print(f"Your wand of poison inflicts {target.name} with {c.effect(entities.Poisoned)}.")
        return True

class LightningWand(Wand):
# (req 3 INT, 2 charges) electrocutes target for 5 + x turns
    name = "wand of lightning"
    value = 75
    maxUses = 2

    reqInt = 3

    def inspect(self):
        print(f"Electrocutes the target for {5 + self.enchantment} turns.")
        print(f"Electrocuted targets become stunned every other turn")
        print("Requires at least 3 intelligence (INT).")

    def cast(self, target):
        target.affect(entities.Electrocuted(), 5 + self.enchantment)
        print(f"Your wand of lightning inflicts {target.name} with {c.effect(entities.Electrocuted)}.")
        return True

class TeleportWand(Wand):
# (req 2 INT, 2 charges) teleports target to a random room
    name = "wand of teleportation"
    value = 65
    maxUses = 2

    reqInt = 2

    def inspect(self):
        print("Teleports the target to a random room.")
        print("Requires at least 2 intelligence (INT).")

    def cast(self, target):
        if issubclass(type(target), entities.Boss):
            print(f"{target.name} is too powerful for that spell!")
            return False
            
        currentRoom = player.currentFloor.get_room()

        roomList = []
        for row in player.currentFloor.layout:
            for room in row:
                if not room.blocked and room != currentRoom:
                    roomList.append(room)

        choice(roomList).threats.append(target)
        currentRoom.threats.remove(target)
        
        print(f"{target.name} disappears!")
        target.heal(6) # heals the target a bit
        return True
    
class Equipable(Item):
    usePrompt = "equip"
    gearType = None # replace with a string such as "armor", "ring" or "back"
    
    def status(self):
        suffix = ""
        if self.uses <= self.maxUses / 3:
            suffix = "damaged"
        elif self.uses <= self.maxUses * 2 / 3:
            suffix = "worn"

        return f"{suffix}"

    def get_name(self):
        if self == player.gear[self.gearType]:
            return super().get_name() + " (equipped)"
            
        return super().get_name()

    def put_on(self):
        if player.gear[self.gearType] != None:
            #player.inventory.append(player.armor)
            player.gear[self.gearType].unequip()
        player.gear[self.gearType] = self
        #player.inventory.remove(self)

    def consume(self, floor):
        self.equip()
        self.put_on()

    def attack(self, enemies):
        return self.consume(None)

    def unequip(self):
        return False
    
class Armor(Equipable):
# gives defense to player but lowers DEX
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    enchantable = True
    enchantValue = 0.25

    gearType = "armor"
    
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]

        self.name = material + " armor"
        self.value = 5 + (55 * level)
        self.maxUses = 20 + (12 * level)

        self.armorClass = level + 2
        self.dexLoss = 1

        if material in ["iron", "steel"]:
            self.dexLoss += 1

        super().__init__()

    def inspect(self):
        print(f"When equipped it gives you {c.compare(self.armorClass + self.enchantment, self.armorClass)} armor class but lowers your dexterity by {self.dexLoss}.")
        print("Worn as armor.")

    def equip(self):
        player.armorClass += self.armorClass + self.enchantment
        player.update_dex(-self.dexLoss)

    def unequip(self):
        # this is where it unequips
        player.armorClass -= self.armorClass + self.enchantment
        player.update_dex(self.dexLoss)

class LeatherArmor(Equipable):
# gives less defense than any other armor, but has no DEX penalty
    name = "leather armor"
    value = 35
    maxUses = 25
    enchantable = True
    enchantValue = 0.4

    gearType = "armor"

    def inspect(self):
        print(f"When equipped it gives you {c.compare(1 + self.enchantment, 1)} armor class.")
        print("Worn as armor.")

    def equip(self):
        player.armorClass += 1 + self.enchantment

    def unequip(self):
        player.armorClass -= 1 + self.enchantment

class MagicRobe(Equipable):
# provides 0 base armor, but increases wand recharge
    name = "magic robe"
    value = 40
    enchantable = True
    enchantValue = 0.8
    maxUses = 20

    gearType = "armor"

    def inspect(self):
        print("When equipped it recharges your wands an additional time each floor.")
        if self.enchantment != 0:
            print(f"It also provides {c.compare(self.enchantment, 0)} armor class.")
        print("Worn as armor.")

    def equip(self):
        # applies stats
        player.armorClass += self.enchantment
        player.recharge += 1

    def unequip(self):
        player.armorClass -= self.enchantment
        player.recharge -= 1

class Cloak(Equipable):
# provides 0 base armor, but +1 stealth
    name = "cloak"
    value = 50
    enchantable = True
    enchantValue = 0.6
    maxUses = 25

    gearType = "back"

    def inspect(self):
        print(f"When equipped it increases your stealth by 1.")
        if self.enchantment != 0:
            print(f"It also provides {c.compare(self.enchantment, 0)} armor class.")
        print("Worn as a back item.")

    def equip(self):
        # applies stats
        player.armorClass += self.enchantment
        player.stealth += 1

    def unequip(self):
        player.armorClass -= self.enchantment
        player.stealth -= 1

class ShadowCloak(Equipable):
# same as cloak, but enchantments affect stealth, not armor
# starts enchanted
    name = "Cloak of Shadows"
    value = 100
    maxUses = 30
    
    enchantable = True
    gearType = "back"

    def inspect(self):
        enchantment = self.enchantment
        if enchantment < 0: # ensures that -1 enchantment means -1 stealth
            enchantment -= 1
            
        print(f"When equipped it increases your dexterity (DEX) by {c.compare(1 + enchantment, 1)}.")
        print("Worn as a back item.")

    def equip(self):
        enchantment = self.enchantment
        if enchantment < 0: # ensures that -1 enchantment means -1 dex
            enchantment -= 1

        # applies stats
        player.update_dex(enchantment + 1)

    def unequip(self):
        enchantment = self.enchantment
        if enchantment < 0: # ensures that -1 enchantment means -1 dex
            enchantment -= 1
        
        player.update_dex(-enchantment - 1)
        
class InfernoRing(Equipable):
# increases strength, but burns you when attacked
    name = "Ring of Rage"
    value = 100

    enchantable = True
    gearType = "ring"

    def inspect(self):
        print(f"When equipped, increases your damage with weapons (excluding daggers) by {c.compare(0.75 + 0.75 * self.enchantment, 0.75)}.")
        print("Worn as a ring.")

    def equip(self):
        player.bonusDamage += (self.enchantment + 1) * 0.75

    def unequip(self):
        player.bonusDamage -= (self.enchantment + 1) * 0.75

class IllusionRing(Equipable):
# increases dodged, when you dodge the attacker is stunned
    name = "Ring of Illusion"
    value = 100

    enchantable = True
    gearType = "ring"

    def inspect(self):
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1

        print("Whenever you dodge an attack, the attacker gets stunned.")
        print(f"Increases your chance to dodge by {c.compare(5 + 5 * enchantment, 5)}%.")
        print("Worn as a ring.")

    def equip(self):
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1

        player.illusionRing = True
        player.dodgeChance += 5 + 5 * enchantment

    def unequip(self):
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1

        player.illusionRing = False
        player.dodgeChance -= 5 + 5 * enchantment

class ArtifactRing(Equipable):
# can accept up to two other rings, then provides the bonuses of each of them
# any enchantment levels are split between the two rings
    name = "Artifact Ring"
    value = 100

    usePrompt = "activate"

    ring1 = None
    ring2 = None

    enchantable = True
    gearType = "ring"

    def inspect(self):
        if self.ring2 == None:
            print("Can absorb the abilities of two other rings.")
        else:
            self.ring2.enchantment = self.enchantment // 2
            self.ring2.inspect()

        if self.ring1 != None:
            self.ring1.enchantment = (self.enchantment + 1) // 2
            self.ring1.inspect()

    def consume(self, floor):
        if self.usePrompt == "activate":
            options = ["cancel"]
            rings = []
            for item in player.inventory:
                if issubclass(type(item), Ring) and item != self:
                    options.append(item.get_name())
                    rings.append(item)

            if len(options) == 1:
                print(c.red("You don't have any rings to insert into Artifact Ring."))
            else:
                playerInput = gather_input("Select a ring to insert.", options, True) - 1
                if playerInput > -1:
                    ring = rings[playerInput]
                    if self.ring1 == None:
                        self.ring1 = ring
                    else:
                        self.ring2 = ring
                        self.usePrompt = "equip"
                    player.inventory.remove(ring)
                    if ring == player.ring:
                        ring.unequip()
                        player.ring = None
                    self.enchantment += ring.enchantment
                    print("Artifact Ring has absorbed the abilities of " + ring.get_name() + ".")
        else:
            super().consume(floor)

    def equip(self):
        self.ring1.enchantment = (self.enchantment + 1) // 2
        self.ring1.equip()
        self.ring2.enchantment = self.enchantment // 2
        self.ring2.equip()

    def unequip(self):
        self.ring1.unequip()
        self.ring2.unequip()

class Ring(Equipable):
# boosts one stat by 1 level
# 0 = stealth, 1 = dodge, 2 = health, 3 = resistance, 4 = awareness
    enchantable = True
    gearType = "ring"

    def __init__(self, ID = -1):
        self.value = 50
        self.maxUses = 1
        self.enchantValue = 0.9
        # decides what stat is boosted
        self.statID = ID
        if ID < 0:
            self.statID = randint(0, 5)
            
        self.stat = ["stealth", "dodge", "health", "resistance", "awareness", "critChance"][self.statID]
        self.name = "ring of " + ["shadows", "evasion", "resilience", "immunity", "vision", "power"][self.statID]

        super().__init__()

    def inspect(self):
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1

        print([
            f"Increases your stealth by {c.compare(1 + enchantment, 1)} level(s).",
            f"Increases your chance to dodge by {c.compare(5 + 5 * enchantment, 5)}%.",
            f"Increases your health by {c.compare(2 + 2 * enchantment, 2)}.",
            f"Increases your resistance to disease and injury by {c.compare(1 + enchantment, 1)} level(s).",
            f"Increases your awareness of nearby threats by {c.compare(1 + enchantment, 1)} level(s).",
            f"Increases your chance to get a critical hit by {c.compare(10 + 10 * enchantment, 10)}%."
        ][self.statID])
        print("Worn as a ring.")

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
            player.dodgeChance += 5 + 5 * enchantment
            
        elif self.stat == "health":
            player.maxHealth += 2 + 2 * enchantment
            player.health += 2 + 2 * enchantment
            
        elif self.stat == "resistance":
            player.resistance += 1 + enchantment

        elif self.stat == "awareness":
            player.awareness += 1 + enchantment

        elif self.stat == "critChance":
            player.critChance += 10 + 10 * enchantment

    def unequip(self):
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1
            
        if self.stat == "stealth":
            player.stealth -= 1 + enchantment
            
        elif self.stat == "dodge":
            player.dodgeChance -= 5 + 5 * enchantment
            
        elif self.stat == "health":
            player.maxHealth -= 2 + 2 * enchantment
            player.health -= 2 + 2 * enchantment
            
        elif self.stat == "resistance":
            player.resistance -= 1 + enchantment

        elif self.stat == "awareness":
            player.awareness -= 1 + enchantment

        elif self.stat == "critChance":
            player.critChance -= 10 + 10 * enchantment

class Medicine(Item): 
    usePrompt = "use"

    enchantable = True

    healing = 0
    effectApplied = None
    effectDuration = 0
    effectsCured = []

    def attack(self, enemies):
    # attack does the same thing as consume
        return self.consume(None)

    def consume(self, floor):
        self.degrade()

        # cures effects
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

        # heals and apples effects
        healingDone = player.heal(self.healing + self.enchantment + randint(-1, 1))

        if self.effectApplied != None:
            player.affect(self.effectApplied(), self.effectDuration + self.enchantment)

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
                    elif i > 0:
                        message += ", "

                    message += removedEffects[i]

        print(message + ".")

        return True

class HealingVial(Medicine):
# cures most effects, heals all health
    name = "vial of healing"
    value = 70
    maxUses = 1
    usePrompt = "drink"

    healing = 100
    effectsCured = [entities.RatDisease, entities.BrokenBones, entities.Bleeding, entities.Burned, entities.Poisoned]

    def status(self):
        return ""

    def inspect(self):
        print("Heals all of your health and cures most effects.")

    def degrade(self):
        player.inventory.remove(self)

class Bandage(Medicine):
# cures bleeding, heals some health, and applies regeneration
    name = "bandage"
    value = 40
    maxUses = 3

    healing = 6
    effectApplied = entities.Regeneration
    effectDuration = 4
    effectsCured = [entities.Bleeding]

    def status(self):
        message = ""
        if self.uses == 1:
            message = "(damaged)"
        elif self.uses == 2:
            message = "(worn)"

        return message

    def inspect(self):
        print(f"Heals around {c.compare(10 + 2 * self.enchantment, 10)} health over time.")
        print(f"Has multiple uses and cures bleeding.")
        if self.enchantment > 0:
            print(c.green("This item does extra healing."))
        elif self.enchantment < 0:
            print(c.red("This item does less healing."))
        
        print(f"\nYou currently have {c.health_status(player.health, player.maxHealth)} health.")

    def get_name(self):
        message = self.name

        if self.status() != "":
            message += " " + self.status()

        if self.enchantment > 0:
            message += c.green(f" (+{self.enchantment})")
        elif self.enchantment < 0:
            message += c.red(f" (-{-self.enchantment})")

        return message

# see gen_enemy() in entities.py for explanation
class Rations(Medicine):
# heals a lot of health but can't be used in combat
    name = "rations"
    value = 25
    maxUses = 1

    usePrompt = "consume"

    healing = 7
    effectApplied = entities.WellFed
    effectDuration = 4

    def status(self):
        return ""
        
    def inspect(self):
        print(f"Heals around {c.compare(15 + 3 * self.enchantment, 15)} health over time.")
        print("Cannot be eaten during combat.")
        print(f"\nYou currently have {c.health_status(player.health, player.maxHealth)} health.")
        if self.enchantment > 0:
            print(c.green("This item does extra healing."))
        elif self.enchantment < 0:
            print(c.red("This item does less healing."))

    def attack(self, enemies):
        print("You don't have enough time to eat!")
        return False

    def degrade(self):
        player.inventory.remove(self)

class Scroll(Item):
# one use item that is more powerful with higher intelligence
    maxUses = 1
    
    enchantable = True
    
    usePrompt = "read"

    def degrade(self):
        player.inventory.remove(self)
        return True

    def status(self):
        return ""

    def consume(self, floor):
        if self.enchantment < 0:
            print(c.red(f"Reading the cursed scroll drains {self.enchantment} health from you!"))
            player.health += self.enchantment
        return True

    def inspect(self):
        if self.enchantment > 0:
            print(c.green(f"This scroll is more powerful, it's effects will be boosted by {self.enchantment} INT."))
        elif self.enchantment < 0:
            print(c.red("This scroll may have undesirable effects."))

class ScrollCleanse(Scroll):
# reverses curses from all items, has an INT in 4 chance to enchant
    name = "scroll of cleansing"
    value = 35

    def inspect(self):
        print("Uncurses every cursed item in this floor and your inventory.")
        print("With higher levels of intelligence (INT) some items may also become blessed.")
        super().inspect()
    
    def consume(self, floor):
        power = player.intelligence + self.enchantment # intelligence boosts effectiveness

        # finds all items in the floor
        allItems = []
        allItems.extend(player.inventory)
        for row in player.currentFloor.layout:
            for room in row:
                for item in room.loot:
                    allItems.append(item)

        # uncurses and upgrades them
        upgradedItemsCount = 0
        for item in allItems:
            if type(item) != CursedSword:
                if item in player.gear.values():
                    item.unequip()

                if item.enchantment < 0:
                    item.enchantment = 0

                if randint(0, 8) < power and item.enchantable:
                    item.enchantment += 1
                    upgradedItemsCount += 1

                if item in player.gear.values():
                    item.equip()

        print("In a flash of cleansing light, all items in this floor have been uncursed.")
        if upgradedItemsCount > 0:
            print(f"{upgradedItemsCount} items have been upgraded.")

        super().consume(floor)

        self.degrade()
        return True

class ScrollEnchant(Scroll):
# adds 1 + INT/2 levels of enchantment to an item
    name = "scroll of enchantment"
    value = 65

    def inspect(self):
        print("Reading this scroll will bless one of your items.")
        print("It cannot be used on items with a higher level than your intelligence (INT).")
        super().inspect()

    def consume(self, floor):
        power = player.intelligence + self.enchantment
        
        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(item.get_name())

        itemIndex = gather_input(f"Choose an item with a level of {c.green(power)} or less to bless.", options, True)

        if itemIndex == 0: # 0 cancels
            return False
        else:
            itemIndex -= 1 # converts to proper index
            chosenItem = player.inventory[itemIndex]

            if chosenItem.enchantment > power: # checks intelligence
                print(c.red(f"You can only upgrade items with a level of {power} or less."))
                return False
            
            if chosenItem == self:
                print(c.red("The scroll cannot bless itself!"))
                return False

            if chosenItem.enchantable: # checks if item is valid
                if chosenItem in player.gear.values():
                    chosenItem.unequip()

                chosenItem.enchantment += 1
                print(chosenItem.name + " has been blessed.")
                super().consume(floor)
                self.degrade()

                if chosenItem in player.gear.values():
                    chosenItem.equip()
                return True
            else:
                print(c.red(chosenItem.name + " cannot be enchanted."))
                return False

class ScrollRepair(Scroll):
# fully repairs and item, higher levels of int increase its max uses
    name = "scroll of repair"
    value = 50

    def inspect(self):
        print("This scroll will fully restore the uses of one item.")
        print("Your intelligence (INT) can increase or decrease the chosen item's future durability.")
        super().inspect()

    def consume(self, floor):
        power = player.intelligence + self.enchantment # intelligence boosts effectiveness

        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(item.get_name())

        chosenItem = gather_input("What item do you repair?", options, True)

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
                super().consume(floor)
                self.degrade()
                return True
            else:
                print(item.name + " cannot be repaired")
                return False

class Consumable(Item):
# a one use item that varies slightly from the scroll
    maxUses = 1

    def degrade(self):
        player.inventory.remove(self)
        return True

    def status(self):
        return ""

class Bomb(Consumable):
    name = "bomb"
    value = 45

    enchantable = True

    canDig = True

    def inspect(self):
        print("Can destroy walls, possibly revealing secret rooms.")
        print("Can be used in combat to damage all enemies.")
        if self.enchantment > 0:
            print(c.green("This bomb does extra damage."))
        elif self.enchantment < 0:
            print(c.red("This bomb does less damage."))

    def attack(self, enemies):
        for enemy in enemies:
            damage = randint(13, 15) + self.enchantment * 2

            # does less damage against bosses (discourages spamming bombs)
            if issubclass(type(enemy), entities.Boss):
                damage = damage // 2

            # bombs are unaffected by crit chance
            crit = player.critChance
            player.critChance = 0
            
            damage = enemy.hurt(player, damage, 1, 0)

            # restores crit chance
            player.critChance = crit
            
            print(f"The bomb does {c.red(damage)} damage to {enemy.name}.")

        self.degrade()
        return True

class StunBomb(Consumable):
    name = "stun bomb"
    value = 35

    enchantable = True

    def inspect(self):
        print(f"Leaves enemies {c.effect(entities.Dazed)} and {c.effect(entities.Surprised)}, lowering their DEX and PER.")
        print(f"Allows you to escape from any enemy (except bosses), and stuns enemies for a couple turns.")
        if self.enchantment > 0:
            print(c.green(f"Dazed lasts longer."))
        elif self.enchantment <= 0:
            print(c.red(f"Does not inflict Dazed."))

    def attack(self, enemies):
        for enemy in enemies:
            enemy.affect(entities.Surprised(), 2)
            if self.enchantment >= 0:
                enemy.affect(entities.Dazed(True), 2 + self.enchantment)
                
        print(f"All enemies are {c.effect(entities.Surprised)} and {c.effect(entities.Dazed)}!")
        self.degrade()
        return True

class FireBomb(Consumable):
    name = "fire bomb"
    value = 55

    enchantable = True

    def inspect(Self):
        print("Damages all enemies and sets them on fire.")

    def attack(self, enemies):
        for enemy in enemies:
            damage = randint(13, 15) + self.enchantment

            # does less damage against bosses (discourages spamming bombs)
            if issubclass(type(enemy), entities.Boss):
                damage = damage // 2

            # bombs are unaffected by crit chance
            crit = player.critChance
            player.critChance = 0
            
            damage = enemy.hurt(player, damage, 2, 0)

            player.critChance = crit
            
            enemy.affect(entities.OnFire(), 5 + self.enchantment)
            print(f"The fire bomb does {c.red(damage)} damage to {enemy.name}, and sets them {c.effect(entities.OnFire)}.")

        self.degrade()
        return True

class StorageBook(Consumable):
# consuming grants +1 inventory size
# purchased from the golem in the crossroads
    name = "\"Forbidden Techniques: Storage\""
    value = 45

    usePrompt = "read"

    def inspect(self):
        print("Contains knowledge on how to manipulate the physical world.")
        print("Reading will increase your inventory size.")

    def consume(self, floor):
        player.inventorySize += 1
        print("Most of the knowledge contained in the book is incomparehensible to your mortal mind.")
        print("Shortly after being read, the book burns to ashes. You gain +1 inventory size.")
        self.degrade()
        return True
        
class ImmunityBook(Consumable):
# consuming grants +1 immunity
# found in the mines
    name = "\"Forbidden Techniques: Immunity\""
    value = 60

    usePrompt = "read"

    def inspect(self):
        print("Contains knowledge on how to escape the limits of mortality.")
        print("Reading will increase your resistance.")

    def consume(self, floor):
        player.resistance += 1
        print("Most of the knowledge contained in the book is incomparehensible to your mortal mind.")
        print("Shortly after being read, the book burns to ashes. You gain +1 resistance.")
        self.degrade()
        return True

class EvasionBook(Consumable):
# consuming grants +5% dodge chance
# purchased from the collector
    name = "\"Forbidden Techniques: Evasion\""
    value = 100

    usePrompt = "read"

    def inspect(self):
        print("Contains knowledge on how to harness your shadow form.")
        print("Reading will increase your dodge chance.")

    def consume(self, floor):
        player.dodgeChance += 5
        print("Most of the knowledge contained in the book is incomparehensible to your mortal mind.")
        print("Shortly after being read, the book burns to ashes. You gain +5% dodge chance.")
        self.degrade()
        return True

class VisionBook(Consumable):
# consuming grants +1 awareness
# found as an artifact
    name = "\"Forbidden Techniques: Vision\""
    value = 100

    usePrompt = "read"

    def inspect(self):
        print("Contains knowledge on sensing the presence of others shadow forms.")
        print("Reading will increase your awareness.")

    def consume(self, floor):
        player.awareness += 1
        print("Most of the knowledge contained in the book is incomparehensible to your mortal mind.")
        print("Shortly after being read, the book burns to ashes. You gain +1 awareness.")
        self.degrade()
        return True

class Pickaxe(Item):
# can destroy tiles and is reusable
    name = "pickaxe"
    value = 70
    maxUses = 3

    enchantable = True

    canDig = True

    def status(self):
        message = ""
        if self.uses == 1:
            message = "(damaged)"
        elif self.uses == 2:
            message = "(worn)"

        return message

    def degrade(self):
        player.intelligence += self.enchantment
        super().degrade()
        player.intelligence -= self.enchantment

    def inspect(self):
        print("Can destroy walls, has multiple uses.")
        if self.enchantment > 0:
            print(c.green("This pickaxe has more durability."))
        elif self.enchantment < 0:
            print(c.red("This pickaxe has less durability."))

class IronKey(Item):
    name = "iron key"
    value = 20
    maxUses = 1

    def status(self):
        return ""

    def inspect(self):
        print(f"This key can open an iron gate.")

class GoldKey(Item):
    name = "gold key"
    value = 50
    maxUses = 1

    def status(self):
        return ""

    def inspect(self):
        print(f"This key can open a gold chest.")

class GoldChunk(Item):
    name = "gold chunk"
    value = 50

    def status(self):
        return ""

    def inspect(self):
        print(f"This is a chunk of unrefined gold.")

# number 1 through 16 is chosen
# if standardLoot = [(Rations, 8), (Bandage, 14), (Bomb, 16)]
# there is a 8 in 16 chance for rations, 6 in 16 chance for bandage, and 2 in 16 for bomb
class KnowledgeBook(Item):
# improves one stat
    name = "book of knowledge"
    value = 70
    maxUses = 1

    usePrompt = "read"

    def status(self):
        return ""

    def inspect(self):
        print("Reading this will let you level up one stat.")

    def consume(self, floor):
        print(f"{player.baseSTR} STR | {player.baseCON} CON | {player.baseDEX} DEX | {player.basePER} PER | {player.baseINT} INT")
        
        options = ["cancel", "STR", "CON", "DEX", "PER", "INT"]
        chosenStat = gather_input("What stat do you improve?", options, True, False)

        if chosenStat == "cancel":
            return False

        if chosenStat == "STR":
            player.update_str(1)
            player.baseSTR += 1
            print("Your attacks are stronger, you can carry more items.")
        elif chosenStat == "CON":
            player.update_con(1)
            player.baseCON += 1
            print("Your health has been increased, diseases and injuries heal quicker.")
        elif chosenStat == "DEX":
            player.update_dex(1)
            player.baseDEX += 1
            print("You are stealthier, you are better at dodging.")
        elif chosenStat == "PER":
            player.update_per(1)
            player.basePER += 1
            print("You're more aware, your attacks are better timed.")
        elif chosenStat == "INT":
            player.update_int(1)
            player.baseINT += 1
            print("Your items break less, scrolls are stronger.")
        
        player.inventory.remove(self)
        return True

class SorcerersRock(Item):
# increases wand recharge
    name = "Sorcerers Rock"
    value = 100
    maxUses = 1

    def status(self):
        return ""

    def inspect(self):
        print("Your wands recharge an additional charge when traveling between floors.")
    
    def pickup(self):
        player.recharge += 1

    def discard(self):
        player.recharge -= 1

class SeeingOrb(Item):
# reveals the whole map, requires a scroll of repair to recharge
# holding increases perception by 1
    name = "Seeing Orb"
    value = 100
    maxUses = 1

    usePrompt = "gaze"

    def status(self):
        if self.uses == 0:
            return "(uncharged)"
        else:
            return ""

    def consume(self, floor):
        if self.uses == 0:
            print("The orb needs to be charged with a scroll of repair before using it again.")
            return False

        self.uses -= 1

        floor.map = floor.layout
        print("You gaze into the orb, the whole floor has been revealed.")
        
        return True

    def pickup(self):
        player.update_per(1)

    def discard(self):
        player.update_per(-1)

    def inspect(self):
        print("Looking into the orb will reveal the entire layout of the floor.")
        print("Once used, it requires a scroll of repair to recharge it.")
        print("Having this item increases your perception (PER) by 1.")

rareLoot = [ShadowCloak, InfernoRing, IllusionRing, SeeingOrb, EbonyDagger, FlamingMace, CursedSword, EnchantedSpear, VisionBook]

def gen_loot(quality):
    if len(rareLoot) == 0: # replaces artifacts with scrolls if there aren't enough
        return ScrollEnchant()

    item = choice(rareLoot)
    rareLoot.remove(item)
    item = item()

    if item.enchantable:
        item.enchantment += (quality + randint(0, 1)) // 3
    return item

def pick_item(itemPool, itemNum):
# used in functions for generating weapons, armor, and wands
    for item in itemPool:
        if itemNum <= item[1]:
            return item[0]
        else:
            itemNum -= item[1]
    # returns the last item if the number is too large
    return itemPool[-1][0]


# returns a random item (usually a consumable)
def gen_item(quality):
    itemPool = [(Rations, 5), (Bomb, 5), (Bandage, 3), (StunBomb, 2), (Pickaxe, 1), (FireBomb, 2), (ScrollRepair, 1), (ScrollEnchant, 1)]

    item = pick_item(itemPool, randint(1, 12) + quality)()

    if item.enchantable and randint(1, 4) == 1: # 25% chance that item is blessed
        item.enchantment += 1
    
    return item

previousCategory = ["misc"] # this is a list b/c variables outside of functions can't be changed
# returns a random item that's gear (weapon, armmor, etc.)
def gen_gear(quality):
    categories = ["brute", "stealth", "misc"]
    categories.remove(previousCategory[0])

    category = choice(categories)
    
    gearPools = {
        "brute":[(Sword, 2), (Mace, 2), (Spear, 2), (Armor, 3), (LeatherArmor, 1)],
        "stealth":[(Dagger, 6), (Cloak, 3), (LeatherArmor, 1)],
        "misc":[(Ring, 10)]
    }

    gear = pick_item(gearPools[category], randint(1, 10))

    # tracks what category was selected
    if gear in (Sword, Mace, Spear, Armor):
        previousCategory[0] = "brute"
    elif gear in (Dagger, Cloak):
        previousCategory[0] = "stealth"
    else:
        previousCategory[0] = "misc"
    
    # some gear can be made of different materials, others get upgraded by being blessedd
    if gear in (Sword, Mace, Spear, Armor, Dagger):
        level = (quality + 2) // 3
        if level > 3:
            level = 3
            
        gear = gear(level)
    else:
        gear = gear()
        gear.enchantment += quality // randint(3, 4)
    
    if gear.enchantable: # gear can be cursed or blessed
        gear.enchantment += randint(-1, 1)
    
    return gear

def gen_scroll(quality = 0):
    scrollPool = ((ScrollEnchant, 2), (ScrollCleanse, 1), (ScrollRepair, 1))
    scroll = pick_item(scrollPool, randint(1, 4))()

    if randint(2, 19) < quality: # 5% chance to be blessed for each point of quality over 2
        scroll.enchantment += 1
        
    return scroll
