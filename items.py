from random import randint, choice
from extra import gather_input, slowprint
import entities
import color

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
                print(self.name + " has broken")

            self.discard()
            if player.armor == self:
                player.armor = None
                self.unequip()
            elif player.ring == self:
                player.ring = None
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
        print(f"It does {self.damage + self.enchantment} damage, with a {self.bleedChance} in 6 chance to inflict bleeding for {self.bleedDuration} turns.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot inflict bleeding.")
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        if self.target.dodge(player):
            slowprint(f"{self.target.name} dodges your attack!")
            return True
            
        damageDealt = self.target.hurt(player, damageDealt)

        if randint(0, 5) < self.bleedChance and self.uses > 0:
            if self.target.affect(entities.Bleeding(), self.bleedDuration):
                slowprint(f"You attack {self.target.name} for {c.red(damageDealt)} damage, leaving them {c.effect(entities.Bleeding)}.")
                return True

        slowprint(f"You attack {self.target.name} for {c.red(damageDealt)} damage.")
        return True

class CursedSword(Sword):
# same as sword but extra damage and burning against undead
    name = "Cursed Blade"
    value = 100
    maxUses = 20

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
        print("Becomes stronger when cursed, and weaker when blessed.")
        print("You can sacrifice your max health to repair and curse the sword further.")
        print(f"You currently have {c.health_status(player.health, player.maxHealth)} health.")

    def consume(self, floor):
        self.uses = self.maxUses
        healthLost = 1
        # becomes more expensive depending the level of curse
        if self.enchantment < 0:
            healthLost -= self.enchantment
            
        self.enchantment -= 1
        player.maxHealth -= healthLost
        player.health -= healthLost

        player.affect(entities.Bleeding(), healthLost)

        print(f"Your sacrifice makes of {c.red(healthLost)} health the blade stronger, but you are now bleeding.")
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
        print(f"It does {self.damage + self.enchantment} damage and pierces {self.armorPiercing - 1} to {self.armorPiercing} points of armor.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot pierce armor.")
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        if self.target.dodge(player):
            slowprint(f"{self.target.name} dodges your attack!")
            return True
            
        damageDealt = self.target.hurt(player, damageDealt, self.armorPiercing - randint(0, 1))

        slowprint(f"You attack {self.target.name} for {c.red(damageDealt)} damage.")
        return True

class EnchantedSpear(Spear):
# same as spear but heals you when you attack alive enemies
    name = "Enchanted Spear"
    value = 100
    maxUses = 20

    damage = 5
    armorPiercing = 2

    def inspect(self):
        super().inspect()
        print("It heals you when you attack enemies.")

    def attack(self, enemies):
        super().attack(enemies)

        healing = player.heal(randint(1, 2))
        if healing > 0:
            print(f"You heal {c.green(healing)} health.")

        return True

class Mace(Weapon):
# does damage to target and can stun
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level = 0):
        super().__init__("mace", level)
        
        if type(self) == Mace:
            self.stunChance = (level + 3) // 2 # _ in 12, level/stunChance : 0/1, 1/2, 2/2, 3/3

    def inspect(self):
        print(f"It does {self.damage + self.enchantment} damage, with a {self.stunChance} in 12 chance to stun.")
        if self.uses < 0:
            print("Because it's broken it does less damage and cannot stun.")
    
    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        if self.target.dodge(player):
            slowprint(f"{self.target.name} dodges your attack!")
            return True
            
        damageDealt = self.target.hurt(player, damageDealt)

        if randint(0, 11) < self.stunChance and self.uses > 0:
            self.target.stunned = True
            slowprint(f"You attack {self.target.name} for {c.red(damageDealt)} damage, leaving them {c.red('stunned')}.")
            return True

        slowprint(f"You attack {self.target.name} for {c.red(damageDealt)} damage.")
        return True

class FlamingMace(Mace):
# same as mace can set enemies on fire
    name = "Flaming Mace"
    value = 100
    maxUses = 20

    damage = 5
    stunChance = 3

    def inspect(self):
        super().inspect()
        print("It can sets enemies on fire.")

    def attack(self, enemies):
        super().attack(enemies)

        if randint(0, 1):
            if self.target.affect(entities.OnFire(), randint(2, 3)):
                slowprint(f"{self.target.name} is set on fire.")

        return True
        
class Dagger(Weapon):
# does damage to target but uses DEX not STR, strong vs surprised enemies
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    def __init__(self, level = 0):
        super().__init__("dagger", level)

        if type(self) == Dagger:
            self.sneakBonus = level + 2

    def inspect(self):
        print(f"It does {self.damage + self.enchantment} damage, and {self.sneakBonus} extra damage towards surprised enemies.")
        print("Daggers do not gain any bonuses from strength (STR).")
        if self.uses < 0:
            print("Because it's broken it does less damage and doesn't gain bonus damage..")

    def attack(self, enemies):
        damageDealt = super().attack(enemies)

        if self.target.dodge(player):
            slowprint(f"{self.target.name} dodges your attack!")
            return True

        if self.target.has_effect(entities.Surprised):
            damageDealt += self.sneakBonus
            slowprint("Sneak attack!")

        damageDealt = self.target.hurt(player, damageDealt, 0, 0)

        slowprint(f"You attack {self.target.name} for {c.red(damageDealt)} damage.")
        return True

class EbonyDagger(Dagger):
# same as a dagger, but gain max health per kill
    name = "Ebony Dagger"
    value = 100
    maxUses = 20

    damage = 5
    sneakBonus = 4

    def inspect(self):
        super().inspect()
        print(f"Getting kills with this weapon can increase your max health.")

    def attack(self, enemies):
        super().attack(enemies)

        # applies ebony dagger's effect
        if self.target.health <= 0 and self.uses > 0 and randint(0, 2) < 2:
            player.maxHealth += 1
            slowprint("You absorb " + self.target.name + "'s power.")
        
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

    def consume(self, floor):
        self.equip()
        self.put_on()

    def attack(self, enemies):
        return self.consume(None)

    def unequip(self):
        return False
    
class HeavyArmor(Armor):
# gives defense to player but lowers DEX
# lvl 0 = bronze, lvl 1 = iron, lvl 2 = steel, lvl 3 = mithril
    enchantValue = 0.25
    
    def __init__(self, level):
        material = ["bronze", "iron", "steel", "mithril"][level]

        self.name = material + " armor"
        self.value = 5 + (55 * level)
        self.maxUses = 20 + (12 * level)

        self.armorClass = level + 1
        self.dexLoss = 1
        if material == "iron" or material == "steel":
            self.dexLoss += 1

        super().__init__()

    def inspect(self):
        print(f"When equipped it gives you {self.armorClass + self.enchantment} armor class but lowers your dexterity by {self.dexLoss}.")

    def equip(self):
        player.armorClass += self.armorClass + self.enchantment
        player.update_dex(-self.dexLoss)

    def unequip(self):
        # this is where it unequips
        player.armorClass -= self.armorClass + self.enchantment
        player.update_dex(self.dexLoss)

class MagicRobe(Armor):
# provides 0 base armor, but increases wand recharge
    name = "magic robe"
    value = 40
    enchantValue = 0.8
    maxUses = 20

    def inspect(self):
        print("When equipped it recharges your wands an additional time each floor.")
        if self.enchantment > 0:
            print(f"It also provides {self.enchantment} armor class.")

    def equip(self):
        # applies stats
        player.armorClass += self.enchantment
        player.recharge += 1

    def unequip(self):
        player.armorClass -= self.enchantment
        player.recharge -= 1

class Cloak(Armor):
# provides 0 base armor, but +1 stealth
    name = "cloak"
    value = 50
    enchantValue = 0.6
    maxUses = 25

    def inspect(self):
        print(f"When equipped it gives you {self.enchantment} armor class and increases your stealth by 1.")

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
    name = "Cloak of Shadows"
    value = 100
    maxUses = 30

    def inspect(self):
        enchantment = self.enchantment
        if enchantment < 0: # ensures that -1 enchantment means -1 stealth
            enchantment -= 1
            
        print(f"When equipped it gives you 0 armor class but increases your DEX by {1 + enchantment}.")

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
        
class Ring(Item):
    maxUses = 1

    enchantable = True

    usePrompt = "equip"
    
    def status(self):
        return ""

    def get_name(self):
        if self == player.ring:
            return super().get_name() + " (equipped)"
            
        return super().get_name()

    def consume(self, floor):
        self.equip()
        self.put_on()

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
    name = "Ring of Rage"
    value = 100

    def inspect(self):
        print(f"Increases your strength (STR) by {self.enchantment + 1}, but doesn't increase inventory size.")
        print("When you are attacked you get burned (-1 AC).")

    def equip(self):
        player.strength += self.enchantment + 1
        player.infernoRing = True

    def unequip(self):
        player.strength -= self.enchantment + 1
        player.infernoRing = False

class IllusionRing(Ring):
# increases dodged, when you dodge the attacker is stunned
    name = "Ring of Illusion"
    value = 100

    def inspect(self):
        enchantment = self.enchantment
        if self.enchantment < 0: # negative enchantment is strong enough to reverse the effect
            enchantment -= 1

        print("Whenever you dodge an attack, your attacker gets stunned.")
        print(f"Increases your chance to dodge by {5 + 5 * enchantment}%.")

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

class ArtifactRing(Ring):
# can accept up to two other rings, then provides the bonuses of each of them
# any enchantment levels are split between the two rings
    name = "Artifact Ring"
    value = 100

    usePrompt = "activate"

    ring1 = None
    ring2 = None

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

class BuffRing(Ring):
# boosts one stat by 1 level
# 0 = stealth, 1 = dodge, 2 = health, 3 = resistance, 4 = awareness
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
            f"Increases your stealth by {1 + enchantment} level(s).",
            f"Increases your chance to dodge by {5 + 5 * enchantment}%.",
            f"Increases your health by {2 + 2 * enchantment}.",
            f"Increases your resistance to disease and injury by {1 + enchantment} level(s).",
            f"Increases your awareness of nearby threats by {1 + enchantment} level(s).",
            f"Increases your chance to get a critical hit by {5 + 5 * enchantment}%."
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
            player.dodgeChance += 5 + 5 * enchantment
            
        elif self.stat == "health":
            player.maxHealth += 2 + 2 * enchantment
            player.health += 2 + 2 * enchantment
            
        elif self.stat == "resistance":
            player.resistance += 1 + enchantment

        elif self.stat == "awareness":
            player.awareness += 1 + enchantment

        elif self.stat == "critChance":
            player.critChance += 5 + 5 * enchantment

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
            player.critChance -= 5 + 5 * enchantment

class Medicine(Item): 
    usePrompt = "use"

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
        healingDone = player.heal(self.healing + randint(-1, 1))

        if self.effectApplied != None:
            player.affect(self.effectApplied(), self.effectDuration)

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
        print(f"It heals around 4 HP and applies REGENERATION.")
        print(f"Cures bleeding.")
        print(f"\nYou currently have {c.health_status(player.health, player.maxHealth)} health.")

    def get_name(self):
        message = self.name

        if self.status() != "":
            message += " " + self.status()

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
        print("Heals around 7 health instantly, and 8 more health over 4 turns.")
        print("You don't have enough time to eat this during combat.")
        print(f"\nYou currently have {c.health_status(player.health, player.maxHealth)} health.")

    def attack(self, enemies):
        print("You don't have enough time to eat!")
        return False

    def degrade(self):
        player.inventory.remove(self)

class Scroll(Item):
# one use item that is more powerful with higher intelligence
    maxUses = 1
    
    usePrompt = "read"

    def degrade(self):
        player.inventory.remove(self)
        return True

    def status(self):
        return ""

class ScrollRemoveCurse(Scroll):
# reverses curses from all items, has an INT in 4 chance to enchant
    name = "scroll of remove curse"
    value = 35

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
    name = "scroll of enchantment"
    value = 65

    def inspect(self):
        print("This scroll will bless one of your items.")
        print("It cannot be used on items with a higher level than your intelligence (INT).")

    def consume(self, floor):
        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(item.get_name())

        itemIndex = gather_input("What item do you bless?", options, True)

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
    name = "scroll of repair"
    value = 50

    def inspect(self):
        print("This scroll will fully restore the uses of one item.")
        print("Your intelligence (INT) can increase or decrease the item's durability.")

    def consume(self, floor):
        power = player.intelligence # intelligence boosts effectiveness

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
                
                self.degrade()
                return True
            else:
                print(item.name + " does not work with the scroll of repair")
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

    def inspect(self):
        print("Bombs can destroy walls, possibly revealing secrets.")
        print("It can be used in combat to harm all enemies.")

    def attack(self, enemies):
        for enemy in enemies:
            damage = 15

            # does less damage against bosses (discourages spamming bombs)
            if issubclass(type(enemy), entities.Boss):
                damage = 8

            # bombs are unaffected by crit chance
            crit = player.critChance
            player.critChance = 0
            
            damage = enemy.hurt(player, damage, 1, 0)

            # restores crit chance
            player.critChance = crit
            
            print(f"The bomb does {c.red(damage)} damage to {enemy.name}!")

        self.degrade()
        return True

    def dig(self):
        self.degrade()
        print("The bomb explodes, after the rubble clears you see that the wall has collapsed.")
        return True

class StunBomb(Consumable):
    name = "stun bomb"
    value = 35

    def inspect(self):
        print("Stuns every enemy, giving you an opportunity to escape. Allows you to escape from any non-boss fight.")
        print(f"Leaves enemies {c.effect(entities.Dazed)}, lowering their DEX and PER.")

    def attack(self, enemies):
        for enemy in enemies:
            enemy.stunned = True
            enemy.affect(entities.Dazed(True), 2)
        print(f"All enemies are {c.red('stunned')} and {c.effect(entities.Dazed)}!")
        self.degrade()
        return True

class FireBomb(Consumable):
    name = "fire bomb"
    value = 55

    def inspect(Self):
        print("Damages all enemies and sets them on fire.")

    def attack(self, enemies):
        for enemy in enemies:
            damage = 14

            # does less damage against bosses (discourages spamming bombs)
            if issubclass(type(enemy), entities.Boss):
                damage = 7

            # bombs are unaffected by crit chance
            crit = player.critChance
            player.critChance = 0
            
            damage = enemy.hurt(player, damage, 2, 0)

            # restores crit chance
            player.critChance = crit
            
            enemy.affect(entities.OnFire(), 5)
            print(f"The fire bomb does {c.red(damage)} damage to {enemy.name}, and sets them {c.effect(entities.OnFire)}!")

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
        print("Most of the knowledge contained in the book is incomprehensible to your mortal mind.")
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
        player.immunity += 1
        print("Most of the knowledge contained in the book is incomprehensible to your mortal mind.")
        print("Shortly after being read, the book burns to ashes. You gain +1 resistance.")
        self.degrade()
        return True

class EvasionBook(Consumable):
# consuming grants +5% dodge chance
# found as an artifact
    name = "\"Forbidden Techniques: Evasion\""
    value = 100

    usePrompt = "read"

    def inspect(self):
        print("Contains knowledge on how to harness your shadow form.")
        print("Reading will increase your dodge chance.")

    def consume(self, floor):
        player.dodgeChance += 5
        print("Most of the knowledge contained in the book is incomprehensible to your mortal mind.")
        print("Shortly after being read, the book burns to ashes. You gain +5% dodge chance.")
        self.degrade()
        return True

class VisionBook(Consumable):
# consuming grants +1 awareness
# purchased from the collector
    name = "\"Forbidden Techniques: Vision\""
    value = 100

    usePrompt = "read"

    def inspect(self):
        print("Contains knowledge on sensing the presence of others shadow forms.")
        print("Reading will increase your awareness.")

    def consume(self, floor):
        player.awareness += 1
        print("Most of the knowledge contained in the book is incomprehensible to your mortal mind.")
        print("Shortly after being read, the book burns to ashes. You gain +1 awareness.")
        self.degrade()
        return True

class Pickaxe(Item):
# can destroy tiles and is reusable
    name = "pickaxe"
    value = 70
    maxUses = 3

    def status(self):
        message = ""
        if self.uses == 1:
            message = "(damaged)"
        elif self.uses == 2:
            message = "(worn)"

        return message

    def dig(self):
        self.degrade()
        print("It takes a while, but you dig a tunnel through the wall.")
        return True

    def inspect(self):
        print("Can destroy walls, has multiple uses.")

class Rope(Item):
# used to descend the chasm safely
    name = "rope"
    value = 20

    def status(self):
        return ""

    def inspect(self):
        print("Useful when there's no stairs.")
    
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

standardLoot = [(Rations, 3), (ScrollRemoveCurse, 1), (Bomb, 4), (Bandage, 4), (StunBomb, 2), (Pickaxe, 1), (FireBomb, 3)]

rareLoot = [ShadowCloak, InfernoRing, IllusionRing, ArtifactRing, SeeingOrb, EbonyDagger, FlamingMace, CursedSword, EnchantedSpear, EvasionBook]

# generates an item such as a bomb or bandage
def gen_item(quality):
    # higher quality items have higher numbers
    itemNum = randint(1, 10) + quality

    # goes through each item until it finds one with a larger number than selected
    for item in standardLoot:
        if itemNum <= item[1]:
            chosenItem = item[0]
            return chosenItem()
        else:
            itemNum -= item[1]

    # if number is too high it returns the last one
    return standardLoot[-1][0]

def gen_loot(quality):
    if len(rareLoot) == 0: # replaces artifacts with scrolls if there aren't enough
        return ScrollEnchant()

    item = choice(rareLoot)
    rareLoot.remove(item)
    item = item()

    if item.enchantable:
        item.enchantment += (quality + randint(0, 1)) // 3
    return item

def gen_armor(quality):
    armorLoot = [(Cloak, 3), (HeavyArmor, 7), (BuffRing, 6)]

    finalArmor = None
    armor = gen_standard(armorLoot)

    if armor == HeavyArmor:
        gearLevel = (quality + 2) // 3
        if gearLevel > 3:
            gearLevel = 3
            
        finalArmor = armor(gearLevel)
    
    else:
        finalArmor = armor()
        finalArmor.enchantment += (quality + 1) // 4
    
    finalArmor.enchantment += randint(-1, 1)

    return finalArmor


def gen_weapon(quality):
    weaponLoot = [(Sword, 4), (Mace, 4), (Spear, 4), (Dagger, 4)]

    finalWeapon = gen_standard(weaponLoot)((quality + 2) // 3)

    finalWeapon.enchantment += randint(-1, 1)

    return finalWeapon

def gen_wand(quality):
    wandLoot = [(TeleportWand, 4), (LightningWand, 4), (HarmWand, 4), (PoisonWand, 4)]

    finalWand = gen_standard(wandLoot)()

    finalWand.enchantment += randint(-1, 1) + ((quality + 2) // 4)

    return finalWand

def gen_standard(gearList):
# used in functions for generating weapons, armor, and wands
    itemNum = randint(1, 16)

    for item in gearList:
        if itemNum <= item[1]:
            return item[0]
        else:
            itemNum -= item[1]

def gen_gear(quality):
    return choice([gen_armor, gen_weapon])(quality)