from extra import add_message
from random import randint, choice
import color

c = color

class Creature:
    # identifying information (such as name or dialogue)
    name = "CREATURE"

    # the most basic stats
    maxHealth = 20
    gold = 0
    stealth = 0 # compared with opponents awareness in stealth checks
    awareness = 0 # compared with opponents stealth in awareness checks

    # other basic stats, not always modified by subclasses
    immuneTo = None # effects that cannot be applied
    armorClass = 0 # reduces incoming damage
    dodgeChance = 0 # percent chance to dodge
    resistance = 0 # higher values decrease the duration of certain effects
    critChance = 0 # percent chance to do x2 damage
    bonusDamage = 0 # damage added to spears, swords, and maces

    # these are mainly used for the player, mostly modify basic stats
    # note that besides strength and intelligence, changing these stats doesn't do much
    # use methods such as update_dex(num) instead of changing these stats directly
    strength = 0 # +damage +inventorySize
    dexterity = 0 # +dodge +stealth
    constitution = 0 # +maxHeatlh +resistance
    intelligence = 0 # increases gear durability and scroll effectiveness
    perception = 0 # +awareness +appraisal

    # temporary stats that keep track of combat status
    health = 0
    effects = None
    stunned = False
    canHeal = True

    def __init__(self):
        self.health = self.maxHealth

        self.immuneTo = []
        self.effects = []

    def update_str(self, increase):
    # strength is added to damage dealt and increases inventory size
        self.strength += increase
        self.bonusDamage += 0.75 * increase
        if issubclass(type(self), Player):
            self.inventorySize += increase

    def update_dex(self, increase):
    # dexterity improves stealth and dodge
        self.dexterity += increase

        self.stealth += increase
        self.dodgeChance += 5 * increase

    def update_con(self, increase):
    # constitution improves health and resistance
        self.constitution += increase

        self.resistance += increase
        self.maxHealth += 2 * increase
        self.health += 2 * increase

    def update_int(self, increase):
    # intelligence is how likely a used item or armor is to not break
        self.intelligence += increase
    
    def update_per(self, increase):
    # perception improves awareness and appraisal
        self.perception += increase

        self.awareness += increase
        self.critChance += 10 * increase
    
    def set_stats(self, str, con, dex, per, int):
    # sets all 5 stats at once
        self.update_str(str - self.strength)
        self.update_dex(dex - self.dexterity)
        self.update_con(con - self.constitution)
        self.update_int(int - self.intelligence)
        self.update_per(per - self.perception)

    def has_effect(self, effectType):
        for effect in self.effects:
            if type(effect) == effectType:
                return True
        return False

    def dodge(self, attacker):
        number = randint(0, 99)
        return self.dodgeChance > number

    def hurt(self, attacker, damage, piercing = 0, applyModifiers = True):
        bonusDamage = 0
        # apply modifiers enables crit chance and bonus damage
        if applyModifiers:
            bonusDamage += attacker.bonusDamage

            if attacker.critChance > 0:
                if randint(0, 100) < attacker.critChance:
                    bonusDamage += damage
                    add_message(attacker.name + " got a CRITICAL STIKE!")
            
        reduction = self.armorClass
        if reduction > 0 and piercing > 0: # piercing is only applied if AC > 0
            reduction -= piercing
            if reduction < 0: # piercing can't lead to -AC
                reduction = 0
                
        reduction /= 2.0 # each point of AC is only 0.5 damage reduction
        
        finalDamage = damage - reduction + bonusDamage
        
        # all attacks do at least 0.5 damage, (50% to do 1 damage)
        if finalDamage < 0.5:
            finalDamage = 0.5
        
        # if there is a decimal, it is treated as a chance to do extra damage
        # example: 5.4 damage has a 40% to do 6 damage, and 60% to do 5
        if (finalDamage != int(finalDamage)):
            dif = finalDamage - int(finalDamage)
            if randint(0, 99) < dif * 100:
                finalDamage += 1
        
        # calculations are made with floats but are returned as ints
        self.health -= int(finalDamage)
        return int(finalDamage)

    def heal(self, healthRestored):
    # heals health but makes sure it doesn't exceed max health
        if not self.canHeal:
            return 0
        
        finalHealthRestored = healthRestored
        if self.health + healthRestored > self.maxHealth:
            finalHealthRestored = self.maxHealth - self.health

        self.health += finalHealthRestored
        return finalHealthRestored

    def affect(self, effect, duration = 0):
    # applies resistance and immunities to an effect
        isPermanent = duration == 0
        
        # applies resistance
        if effect.natural and player.resistance > effect.level:
            if duration - self.resistance + effect.level > 3:
                return False
            elif not isPermanent:
                duration -= self.resistance - effect.level

        # checks for duplicate effects
        for i in range(len(self.effects)):
            if type(effect) == type(self.effects[i]):
                # checks which effect is longer
                if self.effects[i].duration < duration or duration < 0:
                    self.effects[i].reverse()
                    self.effects.pop(i)
                    break
                else:
                    return False

        # checks if immune to effect
        if not type(effect) in self.immuneTo:
            if isPermanent:
                effect.isPermanent = True
                duration = -1
            else:
                effect.duration = duration
                
            self.effects.append(effect)
            effect.apply(self)
            return True
        else:
            return False

class Player(Creature):
# has inventory and equipment slots
    name = "YOU"
    maxHealth = 20

    gold = 40

    inventorySize = 10
    inventory = []
    gear = {"armor":None, "ring":None, "back":None}
    recharge = 1 # wand recharge speed

    baseSTR = 0
    baseCON = 0
    baseDEX = 0
    basePER = 0
    baseINT = 0

    currentFloor = None

    # various stats for unusual effects
    infernoRing = False
    illusionRing = False

    def set_stats(self, str, con, dex, per, int):
        super().set_stats(str, con, dex, per, int)
        self.baseSTR = str
        self.baseCON = con
        self.baseDEX = dex
        self.basePER = per
        self.baseINT = int

    def dodge(self, attacker):
        dodged = super().dodge(attacker)

        if dodged and self.illusionRing:
            attacker.stunned = True
            add_message(f"Your Ring of Illusion stuns {attacker.name}.")

        return dodged

    def hurt(self, attacker, damage, piercing = 0, strength = None):
    # damages armor
        damageDealt = super().hurt(attacker, damage, piercing, strength)

        if self.gear["armor"] != None:
            self.gear["armor"].degrade()

        # applies inferno ring's effect
        if self.infernoRing:
            self.affect(Burned(), 3 + (player.resistance // 2)) # duration of burned scales with resistance, making resistance less effective

        return damageDealt
    
    def affect(self, effect, duration = 0):
        isAffected = super().affect(effect, duration)

        if not isAffected:
            add_message("You resisted the effect!")
        elif type(effect) != Surprised: # surprised triggers too often and doesn't appear properly
            add_message(effect.color(effect.name.upper()) + ": " + effect.inspect())

        return isAffected

player = Player() # creates the one and only instance of player

class Enemy(Creature):
# subclasses of Enemy require a method named attack()
    # more identifying information
    battleMessages = [] # names are only colored in stealth due to the need to alert the player
    stealthMessages = [c.red("ENEMY") + " not notice you"]
    warning = "You feel uneasy..."
    undead = False
    isSpecial = False # determines if the game should give a (!) with this enemy
    
    def __init__(self):
        super().__init__()
        self.gold = (self.gold * randint(8, 12)) // 10
        self.awareness += randint(-1, 1)
        self.stealth += randint(-1, 1)

    def do_turn(self, enemies):
        # parameter 'enemies' allows the method to see the whole battlefield
        if self.stunned:
            print(f"{self.name} is stunned and unable to fight")
            self.stunned = False
        else:
            self.attack(enemies)

class Boss(Enemy):
    isSpecial = True

    def do_turn(self, enemies):
    # less likely to be stunned
        if self.stunned:
            if randint(0, 1):
                print(f"{self.name} is stunned and unable to fight")
                self.stunned = False
            else:
                print(f"{self.name} resisted the stun")
                self.stunned = False
                self.attack(enemies)
        else:
            self.attack(enemies)

class Effect:
    natural = False
    level = 0
    isPermanent = False
    color = c.effect_neutral

    duration = 0 # only changed when effect is created
    
    def apply(self, target):
        self.target = target

    def update(self, enemies):
    # called every turn
        pass

    def reverse(self):
    # called when effect is removed
        pass

    def inspect(self):
    # tells the player what the effect does
        return("This is an effect.")

class Electrocuted(Effect):
# stuns the target every other turn
    name = "electrocuted"
    color = c.effect_bad

    def update(self, enemies):
        if self.duration % 2 == 0:
            self.target.stunned = True

    def inspect(self):
        return("Stuns the target every other turn.")

class Bleeding(Effect):
# does 1 damage per turn
    name = "bleeding"
    natural = True
    level = 1
    color = c.effect_bad

    def update(self, enemies):
        # lowers health by 1 every turn
        self.target.health -= 1

    def inspect(self):
        return(f"Does {c.red(1)} damage every turn.")

class Regeneration(Effect):
# heals 1 hp per turn
    name = "regeneration"
    color = c.effect_good

    def update(self, enemies):
        self.target.heal(1)

    def inspect(self):
        return(f"Heals {c.green(1)} health every turn.")

class WellFed(Effect):
# heals 2 health per turn
    name = "well fed"
    color = c.effect_good

    def update(self, enemies):
        self.target.heal(2)

    def inspect(self):
        return(f"Heals {c.green(2)} health every turn.")
        
class Dazed(Effect):
# lowers DEX
    name = "dazed"
    natural = True
    level = 2
    color = c.effect_bad

    def __init__(self, allowRun = False):
        self.allowRun = allowRun
    
    def apply(self, target):
        self.target = target

        self.target.update_dex(-1)
        self.target.update_per(-1)

        self.allowRun = self.allowRun and self.target.isSpecial and not issubclass(type(target), Boss)

        if self.allowRun:
            self.target.isSpecial = False
        

    def reverse(self):
        self.target.update_dex(1)
        self.target.update_per(1)

        if self.allowRun:
            self.target.isSpecial = True

    def inspect(self):
        return(f"Lowers DEX and PER by {c.red(1)}.")

class Surprised(Effect):
# lowers dodge chance
    name = "surprised"
    color = c.effect_bad

    def apply(self, target):
        self.target = target

        self.target.dodgeChance -= 20

    def reverse(self):
        self.target.dodgeChance += 20

    def inspect(self):
        return(f"Lowers dodge chance by {c.red(20)}%.")

class Decay(Effect):
# lowers CON, gets stronger over time
    name = "decay"
    color = c.effect_bad

    def apply(self, target):
        self.target = target

        self.decayLevel = 1
        self.turnsToProgress = 2

        self.name = "decay lvl " + str(self.decayLevel)

        self.target.update_con(-self.decayLevel)

    def update(self, enemies):
        self.turnsToProgress -= 1

        if self.turnsToProgress == 0:
            self.decayLevel += 1
            self.name = "decay lvl " + str(self.decayLevel)
            self.turnsToProgress = self.decayLevel + 1
            self.target.update_con(-1)

    def reverse(self):
        self.target.update_con(self.decayLevel)

    def inspect(self):
        return(f"Lowers CON by {c.red(self.decayLevel)}, becomes stronger over time.")

class BrokenBones(Effect):
# lowers DEX, STR, CON, permanently
# instantly kills skeletons
    name = "broken bones"
    natural = True
    level = 5
    color = c.effect_bad

    def apply(self, target):
        self.target = target

        if issubclass(type(self.target), Skeleton):
            self.target.health = 0
            add_message(self.target.name + " dies")

        self.target.update_dex(-1)
        self.target.update_str(-1)
        self.target.update_con(-1)
        
    def reverse(self):
        self.target.update_dex(1)
        self.target.update_str(1)
        self.target.update_con(1)

    def inspect(self):
        return(f"Lowers STR, CON, and DEX by {c.red(1)}.")

class Burned(Effect):
# lowers AC by 1
    name = "burned"
    natural = True
    level = 0
    color = c.effect_bad

    def apply(self, target):
        self.target = target

        self.target.armorClass -= 1

    def reverse(self):
        self.target.armorClass += 1

    def inspect(self):
        return(f"Lowers armor class by {c.red(1)}.")

class OnFire(Effect):
# does 2 damage per turn
# also applies burned
    name = "on fire"
    natural = True
    level = 4
    color = c.effect_bad

    def apply(self, target):
        self.target = target

    def update(self, enemies):
        self.target.affect(Burned(), 5)
        self.target.health -= 2

    def inspect(self):
        return(f"Does {c.red(2)} damage every turn, inflicts {c.effect(Burned)}.")

class Poisoned(Effect):
# does 1 damage per turn and lowers STR
    name = "poisoned"
    natural = True
    level = -1
    color = c.effect_bad

    def apply(self, target):
        self.target = target
        
        self.target.strength -= 1

    def update(self, enemies):
        self.target.health -= 1

    def reverse(self):
        self.target.strength += 1

    def inspect(self):
        return(f"Lowers STR by {c.red(1)}, does {c.red(1)} damage every turn.")

class Chilled(Effect):
# does 1 damage per turn and lowers DEX
    name = "chilled"
    natural = True
    level = 2
    color = c.effect_bad

    def apply(self, target):
        self.target = target
        
        self.target.update_dex(-1)

    def update(self, enemies):
        self.target.health -= 1

    def reverse(self):
        self.target.update_dex(1)

    def inspect(self):
        return(f"Lowers DEX by {c.red(1)}, does {c.red(1)} damage every turn.")

class HealingBlocked(Effect):
# prevents healing
    name = "healing blocked"
    color = c.effect_bad

    def apply(self, target):
        self.target = target
        
        self.target.canHeal = False

    def reverse(self):
        self.target.canHeal = True

    def inspect(self):
        return("Prevents healing.")

class Rage(Effect):
# +2 STR
    name = "rage"
    color = c.effect_good

    def apply(self, target):
        self.target = target

        self.target.update_str(2)

    def reverse(self):
        self.target.update_str(-2)

    def inspect(self):
        return(f"Increases STR by {c.green(2)}.")

class SteelFlesh(Effect):
# +2 CON
    name = "steel flesh"
    color = c.effect_good

    def apply(self, target):
        self.target = target

        self.target.update_con(2)

    def reverse(self):
        self.target.update_con(-2)

    def inspect(self):
        return(f"Increases CON by {c.green(2)}.")

class Invisibility(Effect):
# +2 DEX
    name = "invisibility"
    color = c.effect_good

    def apply(self, target):
        self.target = target

        self.target.update_dex(2)

    def reverse(self):
        self.target.update_dex(-2)

    def inspect(self):
        return(f"Increases DEX by {c.green(2)}.")

class Cloaked(Effect):
# hides targets name, +10 dodge chance
    name = "cloaked"
    color = c.effect_good

    def apply(self, target):
        self.target = target

        self.target.dodgeChance += 10

        # hides and stores name
        self.targetsName = self.target.name
        self.target.name = "CLOAKED"

    def reverse(self):
        self.target.dodgeChance -= 10

        self.target.name = self.targetsName

    def inspect(self):
        return(f"Increases dodge chance by {c.green(10)}%, hides the targets name.")

class RatDisease(Effect):
# has 4 stages, each inheriting the effects of the last:
# 1) nothing, 2) -1CON, 3) -2INT, 4) lose max health over time
    name = "rat disease lvl 1"
    color = c.effect_bad

    stage = 1
    progression = 14

    def update(self, enemies):
        self.progression -= 1

        if self.progression == 0:
            self.progression = 14 - self.stage
            if self.progression < 8:
                self.progression = 8
            self.stage += 1

            if self.stage == 2:
                self.target.update_str(-1)
                print(c.red("You feel weaker."))
                self.name = "rat disease lvl 2"

            elif self.stage == 3:
                self.target.update_int(-2)
                print(c.red("Your mind becomes clouded."))
                self.name = "rat disease lvl 3"

            else:
                self.target.maxHealth -= 2
                self.target.health -= 3
                self.name = "rat disease lvl 4"
                if self.stage == 4:
                    print(c.red("You begin to decay."))
                else:
                    print(c.red("You continue to decay."))

    def reverse(self):
        if self.stage > 1:
            self.target.update_stregth(1)
            print(c.green("Your strength returns."))

        if self.stage > 2:
            self.target.update_int(2)
            print(c.green("Your mind clears."))

        if self.stage > 3:
            self.target.maxHealth += self.stage - 3
            print(c.red("Your body heals, but some damage remains."))

    def inspect(self):
        if self.stage == 1:
            return(f"Has no current effect, becomes stronger over time.")
        elif self.stage == 2:
            return(f"Lowers STR by {c.red(1)}, becomes stronger over time.")
        elif self.stage == 3:
            return(f"Lowers STR by {c.red(1)} and INT by {c.red(2)}, becomes stronger over time.")

        else:
            return(f"Lowers STR by {c.red(1)} and INT by {c.red(2)}, permanently lowers your max health over time.")
            
class Draugr(Enemy):
# a rare enemy that can appear in earlier floors
# starts with armor but it degrades when hurt
# can inflict bleeding
    name = "DRAUGR"
    stealthMessages = [c.red("DRAUGR") + " is on the hunt for human.",
                      c.red("DRAUGR") + " is seeking."]
    undead = True
    isSpecial = True

    maxHealth = 18
    gold = 16
    awareness = 3
    stealth = 2

    critChance = 10
    resistance = 2
    armorClass = 3

    def hurt(self, attacker, damage, piercing = 0, strength = None):
        damageDealt = super().hurt(attacker, damage, piercing, strength)

        if randint(0, 1) or damageDealt > 4:
            self.resistance -= 1
            self.armorClass -= 1
            self.maxHealth -= 1
            self.health -= 1
            add_message("DRAUGR's armor degrades.")
        
        return damageDealt
        
    def attack(self, enemies):
        if player.dodge(self):
            print(f"You dodge DRAUGR's attack.")
            return

        if randint(1, 3) == 1:
            if player.affect(Bleeding(), 4):
                damage = player.hurt(self, 5)
                print(f"DRAUGR hits you with their axe for {c.red(damage)} damage, leaving you {c.effect(Bleeding)}!")
        else:
            damage = player.hurt(self, 6)
            print(f"DRAUGR hits you with their axe for {c.red(damage)} damage!")

class Ghoul(Enemy):
# an uncommon, more aware enemy that appears in the prison
# can dodge attacks and inflicts decay
    name = "GHOUL"
    warning = "You smell a foul stench..."
    stealthMessages = [c.red("GHOUL") + " is roaming.",
                      c.red("GHOUL") + " is waiting for human, they have yet to notice you."]
    undead = True

    maxHealth = 16
    gold = 10
    awareness = 4
    stealth = 1
    
    dodgeChance = 10
    strength = -1 # 4 damage felt like too much but 3 is too little, so this nerfs 4 a little bit

    def attack(self, enemies):
        if randint(1, 3) == 1:
            if player.affect(Decay(), 6):
                print(f"GHOUL curses you with {c.effect(Decay)}!")
                return
        
        if player.dodge(self):
            print("You dodge GHOUL's bite.")
            return

        damage = player.hurt(self, 4)
        print(f"GHOUL bites you for {c.red(damage)} damage!")

class Skeleton(Enemy):
# a common enemy type throughout the dungeon
# is immune to most natural effects and often staggers instead of attacking
    name = "SKELETON"
    warning = "You hear the shuffling of bones..."
    undead = True

    maxHealth = 15
    gold = 8
    awareness = 1
    stealth = 0
    
    damage = 3
    staggerChance = 2 # _ in 6
    
    def __init__(self):
        super().__init__()
        self.immuneTo.extend([Bleeding, Poisoned])

        if self.name == "SKELETON": # doesn't apply to subclasses
            self.weapon = choice(["sword", "spear", "mace"])
            self.battleMessages = [f"SKELETON grips their {self.weapon}!",
                                  "SKELETON finally gets to see some action!"]
            self.stealthMessages = [c.red("SKELETON") + f" is holding a {self.weapon}."]

    def do_turn(self, enemies):
    # there is a chance that skeletons stagger and don't attack
        if randint(0, 5) < self.staggerChance:
            print(f"{self.name} staggers and misses their attack.")
            self.stunned = False
        else:
            super().do_turn(enemies)

    def attack(self, enemies):
        # checks dodge
        if player.dodge(self):
            print(f"You dodge SKELETONS {self.weapon}.")
            return

        piercing = 0
        effect = None

        # spears can pierce
        if self.weapon == "spear" and randint(0, 1):
            piercing = 1

        # some weapons can inflict effects
        if randint(1, 4) == 1:
            # swords inflict bleeding
            if self.weapon == "sword":
                if player.affect(Bleeding(), 4):
                    effect = Bleeding

            # maces inflict dazed
            if self.weapon == "mace":
                if player.affect(Dazed(), 2):
                    effect = Dazed
        
        # does damage
        if effect == None:
            damage = player.hurt(self, self.damage, piercing)
            print(f"{self.name} attacks you with their {self.weapon} for {c.red(damage)} damage!")
        else:
            damage = player.hurt(self, self.damage, piercing)
            print(f"{self.name} attacks you with their {self.weapon} for {c.red(damage)} damage, leaving you {c.effect(effect)}!")

class SkeletonGuard(Skeleton):
# has more AC, staggers less, always has a spear, very aware
    name = "SKELETON GUARD"
    warning = "You hear the shuffling of bones..."
    stealthMessages = [c.red("SKELETON GUARD") + " had promised not to fall asleep this time."]
    isSpecial = True

    maxHealth = 17
    gold = 15
    awareness = 5
    stealth = -1

    armorClass = 4
    immuneTo = [Bleeding, Burned]

    staggerChance = 1 # _ in 6
    weapon = "spear"

class Thief(Enemy):
# an uncommon, stealthy and aware enemy
# hits you with a poison dart when at full health, might run away later in combat
    name = "THIEF"
    warning = "You are being watched..."
    battleMessages = ["\"I see you got some items there, the collector will be pleased.\"",
                     "You encounter a goblin THIEF!",
                     "THIEF equips a dart!"]
    stealthMessages = [c.red("THIEF") + " is looking for a victim.",
                      c.red("THIEF") + " is preparing poisons, and is unaware of your presence.",
                      "A goblin " + c.red("THIEF") + " is roaming."]

    maxHealth = 16
    gold = 6
    awareness = 2
    stealth = 4
    
    critChance = 5

    time = 0
    hasDart = True

    def do_turn(self, enemies):
    # as time goes on, they are more likely to run away
        super().do_turn(enemies)
        
        self.time += 1
        if randint(1, 4) < self.time:
            enemies.remove(self)
            print("THIEF runs away!")
            
        elif self.time == 3:
            print(choice(["THIEF seems eager to escape.", "THIEF wants to flee."]))

    def attack(self, enemies):
        if not self.hasDart:
            if player.dodge(self):
                print("You dodge THIEF's dagger.")
                return

            damage = player.hurt(self, 4)
            print(f"THIEF stabs you for {c.red(damage)} damage!")
        else:
            self.hasDart = False
            if player.dodge(self):
                print("You dodge THIEF's dart.")
                return
            
            if player.affect(Poisoned(), 6):
                print(f"THIEF hits you with a dart, inflicting {c.effect(Poisoned)}!")
            else:
                player.health -= 1
                print("THIEF hits you with a dart, but you resist its poison.")
    
class Ogre(Boss):
# big enemy, can inflict dazed, bleeding, and broken bones
    name = "OGRE"
    warning = "You hear the sounds of an ogre..."
    battleMessages = ["\"Long time it's been since human dared wander down here, you make tasty treat.\"",
                     "\"Me hungry, human tasty.\"",
                     "\"I CRUSH YOU!\""]

    maxHealth = 34
    gold = 40
    awareness = 3
    stealth = -1
    
    armorClass = 1
    resistance = 2
    dodgeChance = -10

    isRaged = False
    isCharging = False
    previousMove = "heavy"

    def attack(self, enemies):
        # becomes stronger when below 20 HP
        if self.health < 20 and not self.isRaged:
            self.isRaged = True
            self.bonusDamage += 2
            print("OGRE is enraged!")
        
        # choses move, can't do the same twice in a row
        choices = ["heavy", "slam", "attack"]
        choices.remove(self.previousMove)
        chosenMove = choice(choices)

        if not self.isCharging:
            self.previousMove = chosenMove

        if self.isCharging:
            self.isCharging = False

            player.dodgeChance += 10
            if player.dodge(self):
                print("You manage to dodge OGRE's heavy swing.")
                player.dodgeChance -= 10
                return
            player.dodgeChance -= 10
            
            damage = player.hurt(self, 7, 2)

            if damage > 8:
                if player.affect(BrokenBones()):
                    print(f"OGRE hits you with a heavy strike, dealing {c.red(damage)} and inflicting {c.effect(BrokenBones)}!")
                    return
            
            print(f"OGRE hits you with a heavy strike, dealing {c.red(damage)} damage!")
            
        elif chosenMove == "heavy":
            print("OGRE prepares a heavy swing!")
            self.isCharging = True

        elif chosenMove == "slam":
            if player.dodge(self):
                print("OGRE slams the ground, but you get out of the way.")
                return

            damage = player.hurt(self, 3, 3)
            if player.affect(Dazed(), 2):
                print(f"OGRE slams the ground, dealing {c.red(damage)} damage and leaving you {c.effect(Dazed)}!")
            else:
                print(f"OGRE slams the ground, dealing {c.red(damage)} damage!")            

        else:
            if player.dodge(self):
                print("You dodge OGRE's club!")
                return

            damage = player.hurt(self, 4, 2)

            if player.affect(Bleeding(), 3):
                print(f"OGRE hits you with their club, dealing {c.red(damage)} damage, leaving you {c.effect(Bleeding)}!")
            else:
                print(f"OGRE hits you with their club, delaing {c.red(damage)} damage!")

class Rat(Enemy):
# a weak enemy who spawns in large groups
# can inflict self with decay, then infects the player
    name = "RAT"
    warning = "You hear the rats..."
    battleMessages = ["You encounter a group of RATS!"]
    stealthMessages = ["You spot a decayed " + c.red("RAT") + ".",
                      c.red("RAT") + " is eating. They are a foul, decayed creature.",
                      "You see a hungry " + c.red("RAT") + ".",
                      c.red("RAT") + " is roaming."]

    maxHealth = 12
    gold = 5
    awareness = 2
    stealth = 1
    
    corruption = 0
    mutations = []
    isToxic = False
    isHungry = False

    def __init__(self):
        if "stronger" in self.mutations:
            self.maxHealth += 4
        
        self.isToxic = "toxic" in self.mutations
        self.isHungry = "hungrier" in self.mutations

        self.maxHealth -= randint(1, 4)

        super().__init__()

        self.health -= randint(0, 1)

    def do_turn(self, enemies):
        super().do_turn(enemies)

        if randint(0, 1):
            self.corruption += 1

    def attack(self, enemies):
        # inflicts self with decay
        if self.corruption == 1:
            effect = Decay
            if self.isToxic:
                effect = Poisoned

            self.affect(effect())
            print(f"RAT becomes infected with {c.effect(effect)}.")

        # rats are easier to dodge
        player.dodgeChance += 15
        if player.dodge(self):
            print("RAT leaps at you, but you avoid them.")
            player.dodgeChance -= 15
            return
        player.dodgeChance -= 15

        # inflicts player with decay
        if self.corruption == 1:
            self.corruption += 1
            
            bonusDuration = 0
            effect = Decay
            if self.isToxic:
                effect = Poisoned
                bonusDuration += 4

            # effect last longer if you already have it
            for i in range(len(player.effects)):
                if type(player.effects[i]) == effect:
                    bonusDuration = player.effects[i].duration - 1
                    break

            if player.affect(effect(), 4 + bonusDuration):
                damage = player.hurt(self, 4)
                print(f"RAT bites you for {c.red(damage)} damage, infecting you with {c.effect(effect)}!")
                return
            else:
                damage = player.hurt(self, 4)
                print(f"RAT bites you for {c.red(damage)} damage, but you resist {c.effect(effect)}!")
                return
        
        # eats teammate
        if self.health < 8 and randint(0, 1) and len(enemies) > 1 and self.isHungry:
            selfIndex = enemies.index(self)
            
            enemies.remove(self)
            target = choice(enemies)

            enemies.insert(selfIndex, self)

            damage = target.hurt(self, 3)
            healing = self.heal(5)
            print(f"RAT bites their teammate {target.name} for {c.red(damage)} damage, healing themselves {c.green(healing)} health!")
            return
            
        # nibbles through armor
        if randint(0, 2) == 2 and player.gear["armor"] != None:
            piercing = 2
            if player.armorClass > 4:
                piercing += 1
            player.gear["armor"].degrade()
            damage = player.hurt(self, 4, piercing)
            print(f"RAT nibbles through your armor, {c.red('degrading')} it and dealing {c.red(damage)} damage!")
            return

        # standard attack
        if self.isHungry and randint(0, 1):
            damage = player.hurt(self, 4)
            healing = self.heal(2)
            print(f"RAT bites you for {c.red(damage)} damage, restoring {c.green(healing)} health!")
        else:
            damage = player.hurt(self, 4)
            print(f"RAT leaps at you, biting you for {c.red(damage)} damage!")

class SewerRat(Enemy):
# a slightly tougher rat that can inflict bleeding and has an armor piercing attack
# if the player is bleeding, it can inflict rat disease
    name = "SEWER RAT"
    warning = "You hear the rats.."
    battleMessages = ["You encounter SEWER RAT!",
                      "SEWER RAT has found its next meal!"]
    stealthMessages = ["You find a mutated " + c.red("SEWER RAT") + ".",
                       "You spot an infected " + c.red("SEWER RAT") + ".",
                       c.red("SEWER RAT") + " is eating the decayed corpse of another rat."]
    
    maxHealth = 14
    gold = 5
    awareness = 4
    stealth = 1

    armorClass = 1
    dodgeChance = 5

    def attack(self, enemies):
        if player.dodge(self):
            print("You dodge SEWER RAT's attack.")
            return
        
        if randint(0, 1) and player.gear["armor"] != None:
            player.gear["armor"].degrade()
            damage = player.hurt(self, 3, 2)

            print(f"SEWER RAT nibbles through your armor, {c.red('degrading')} it and dealing {c.red(damage)} damage!")
            return
        
        else:
            damage = player.hurt(self, 3)

            isBleeding = player.has_effect(Bleeding)

            if isBleeding:
                player.affect(RatDisease())
                print(f"SEWER RAT bites you for {c.red(damage)} damage, infecting your wound with {c.effect(RatDisease)}!")
                return
            
            else:
                player.affect(Bleeding(), randint(4, 5))
                print(f"SEWER RAT bites you for {c.red(damage)} damage, leaving you {c.effect(Bleeding)}!")
                return


class RatBeast(Enemy):
# tough enemy, rages when low health, loses hp over time
# can bite and ram, starts injured and with a random effect
    name = "RAT BEAST"
    warning = "You hear a loud wheezing..."
    stealthMessages = [c.red("RAT BEAST") + " is wandering.",
                      c.red("RAT BEAST") + " is looking for their next meal.",
                      "You encounter " + c.red("RAT BEAST") + ", a rat the size of a bear."]

    maxHealth = 32
    gold = 14
    awareness = 5
    stealth = 1

    immunity = -1
    armorClass = 1

    isRaged = False

    def __init__(self):
        self.maxHealth -= randint(0, 2)
        super().__init__()
        self.health -= randint(0, 4)

        effect = choice([Bleeding, Decay, Dazed, Poisoned, Regeneration, WellFed, Burned])
        self.affect(effect(), randint(4, 6))

    def do_turn(self, enemies):
        super().do_turn(enemies)

        if randint(0, 1):
            print("RAT BEAST decays.")
            self.health -= randint(2, 3)
            self.maxHealth -= randint(1, 2)

        if self.health < 16 and not self.isRaged:
            self.isRaged = True
            self.strength += 2
            print(choice([
                "RAT BEAST is becoming desperate!",
                "RAT BEAST is enraged!"
            ]))

    def attack(self, enemies):
        if randint(0, 1):
            if player.dodge(self):
                print("RAT BEAST lunges at you, but you dodge.")
                return

            damage = player.hurt(self, 6)
            if randint(0, 1):
                player.affect(Bleeding(), randint(5, 7))
                print(f"RAT BEAST bites you for {c.red(damage)} damage, inflicting {c.effect(Bleeding)}!")
            else:
                print(f"RAT BEAST bites you for {c.red(damage)} damage!")

        else:
            player.dodgeChance += 5
            if player.dodge(self):
                print(f"You evade RAT BEAST and they hit a wall, leaving them {c.effect(Dazed)}.")
                self.affect(Dazed(), 2)
                player.dodgeChance -= 5
                return
            player.dodgeChance -= 5

            damage = player.hurt(self, 5, 3)
            player.affect(Dazed(), randint(1, 2))
            print(f"RAT BEAST rams you for {c.red(damage)} damage, leaving you {c.effect(Dazed)}!")

class Goblin(Enemy):
# dexterous enemy, has a dart that blocks healing and has a bandage
    name = "GOBLIN"
    warning = "You hear goblins..."
    battleMessages = ["You encounter a GOBLIN scout!",
                     "\"I'll be taking your gold!\"",
                     "\"You can't escape the collector!\""]
    stealthMessages = [c.red("GOBLIN") + " is waiting.",
                      c.red("GOBLIN") + " is keeping watch.",
                      c.red("GOBLIN") + " is sleeping."]

    maxHealth = 14
    gold = 9
    awareness = 4
    stealth = 4

    armorClass = 2
    critChance = 5

    hasDart = True
    hasBandage = True

    def attack(self, enemies):
        if self.hasBandage and self.health < 9:
            self.hasBandage = False
            healing = self.heal(4)
            self.affect(Regeneration(), 4)
            print(f"GOBLIN uses a bandage, restoring {c.green(healing)} health and applying {c.effect(Regeneration)}.")

        elif self.hasDart and player.health < 13 and not player.has_effect(HealingBlocked):
            self.hasDart = False
            if player.dodge(self):
                print("You dodge GOBLIN's dart.")
                return
            player.affect(HealingBlocked(), 3)
            print(f"GOBLIN hits you with a poisoned dart, inflicting you with {c.effect(HealingBlocked)}!")

        else:
            if player.dodge(self):
                print("You dodge GOBLIN's attack.")
                return
            damage = player.hurt(self, 4)
            print(f"GOBLIN attacks you for {c.red(damage)} damage!")

class BuffedGoblin(Goblin):
# same as goblin, but spawns alone and is stronger
    maxHealth = 16
    gold = 13

    armorClass = 3
    dodgeChance = 15
    strength = 2

class Trickster(Boss):
# can cloak self and allies, high dodge chance and attacks when they dodge list.insert(index, item)
    name = "TRICKSTER"
    battleMessages = ["\"I'm not allowed to let you pass, boss's orders.\"", "\"I'm the boss's champion, you're not going to get past me.\""]

    maxHealth = 30
    gold = 30
    
    armorClass = 2
    dodgeChance = 20
    
    hasSmoke = True
    
    def dodge(self, attacker):
        dodged = super().dodge(attacker)

        if dodged:
            player.affect(Poisoned(), 7)
            add_message(f"TRICKSTER retaliates by hitting you with dart, inflicting {c.effect(Poisoned)}!")

        return dodged
        
    def hurt(self, attacker, damage, piercing = 0, strength = None):
        damage = super().hurt(attacker, damage, piercing, strength)

        if self.health <= 0 and self.hasSmoke: # prevents being one-hit killed
            self.health = 1

        return damage

    def attack(self, enemies):
        if self.health < 10 and self.hasSmoke: # smoke bomb
            self.hasSmoke = False

            # summons 2 goblins and changes position
            enemies.extend([Goblin(), Goblin()])
            enemies.remove(self)
            enemies.insert(randint(0, 2), self)

            # affects all with cloaked and weakens the goblins
            for enemy in enemies:
                enemy.health = 18
                enemy.maxHealth = 18
                enemy.armorClass = 0
                
                for effect in enemy.effects:
                    effect.reverse()

                enemy.effects = []

                if enemy != self:
                    enemy.affect(Cloaked(), randint(4, 5))
                    enemy.strength -= 1
                    enemy.hasDart = False
                    enemy.hasBandage = False
                else:
                    self.isSpecial = False

            # affects self for longer because the effect triggers right after turn
            self.affect(Cloaked(), randint(5, 6))
            
            print(f"Two GOBLINs enter the arena, and TRICKSTER uses a smoke bomb, affecting all enemies with {c.effect(Cloaked)}!")
        else:
            damage = player.hurt(self, randint(4, 5), 2)
            print(f"TRICKSTER stabs you for {c.red(damage)} damage!")
     
class Alchemist(Enemy):
# buffs allies with Rage (+2 STR), Steel Flesh (+2 CON), and Invisibility (+2 DEX)
# runs away if alone
    name = "ALCHEMIST"
    warning = "You hear goblins..."
    battleMessages = ["You encounter ALCHEMIST!",
                      "\"The goblins just can't get enough of my potions!\"",
                     "\"The collector doesn't need to know about your death!\"",
                     "\"He wants to meet you, but I think I'll kill you instead!\""]
    stealthMessages = [c.red("ALCHEMIST") + " is mixing potions.",
                      c.red("ALCHEMIST") + " is selling potions to the goblins."]
    
    maxHealth = 20
    gold = 10
    stealth = 2
    awareness = 2

    armorClass = 1
    dodgeChance = 10

    def __init__(self):
        super().__init__()
        self.affect(Regeneration(), 5)

    def attack(self, enemies):
        if len(enemies) == 1:
            enemies.remove(self)
            print("ALCHEMIST runs away!")
        else:
            options = []
            for enemy in enemies:
                if enemy != self:
                    options.append(enemy)
            target = choice(options)

            potion = choice([Rage, SteelFlesh, Invisibility])
            target.affect(potion(), 5)
            
            print(f"ALCHEMIST gives {target.name} a potion of {c.effect(potion)}!")

class Worm(Enemy):
# appears in the walls of the mines
# can block healing and latch onto the player to drain their health
    name = "WORM"
    warning = c.red("You hear a soft rumbling in the walls...")
    battleMessages = ["You have disturbed WORM!",
                      "WORM has awoken!",
                      "You encounter WORM!"]
    stealthMessages = ["You see a sleeping " + c.red("WORM") +"."]

    maxHealth = 17
    gold = 3
    awareness = 7
    stealth = 1

    resistance = 3
    armorClass = 1

    isLatched = False

    def hurt(self, attacker, damage, piercing = 0, strength = None):
        damageDealt = super().hurt(attacker, damage, piercing, strength)

        if self.isLatched:
            player.affect(Bleeding(), 6)
            add_message(f"WORM detaches from you, leaving you {c.effect(Bleeding)}!")
            self.name = "WORM"
            self.isLatched = False
        
        return damageDealt

    def attack(self, enemies):
        if self.isLatched:
            damage = player.hurt(self, 4, 4)
            healing = self.heal(damage)
            print(f"WORM drains you for {c.red(damage)} damage, healing them for {c.green(healing)} health!")
        else:
            if player.dodge(self):
                print("You dodge WORM's attack!")
                return

            if randint(0, 1):
                damage = player.hurt(self, 5, 1)
                player.affect(HealingBlocked(), 4)
                print(f"WORM's venomous bite does {c.red(damage)} damage, and inflicts {c.effect(HealingBlocked)}!")
            else:
                self.isLatched = True
                self.name = "WORM (latched)"
                print(c.red("WORM latches onto you!"))

class AncientDraugr(Enemy):
# a rare enemy that can appear in the crossroads
# can throw axe, then switches to magic
    name = "ANCIENT DRAUGR"
    battleMessages = ["You encounter ANCIENT DRAUGR!",
                     "ANCIENT DRAUGR has killed many, and doesn't intend to stop!"]
    stealthMessages = [c.red("ANCIENT DRAUGR") + " is on the hunt for human.",
                        c.red("ANCIENT DRAUGR") + " has a freezing aura."]
    undead = True
    isSpecial = True

    maxHealth = 28
    gold = 26
    awareness = 8
    stealth = 2
    
    resistance = 2
    armorClass = 4

    hasAxe = True
        
    def attack(self, enemies):
        if self.hasAxe:
            if self.health < 26 and randint(0, 1):
                # axe throw
                self.hasAxe = False
                player.dodgeChance += 10
                if player.dodge(self):
                    print("ANCIENT DRAUGR throws their axe, but you dodge it.")
                    player.dodgeChance -= 10
                    return
                player.dodgeChance -= 10
                    
                damage = player.hurt(self, 6)
                player.affect(Bleeding(), 7)
                print(f"ANCIENT DRAUGR throws their axe at you, dealing {c.red(damage)} damage and inflicting {c.effect(Bleeding)}!")
            else:
                # standard attack
                if player.dodge(self):
                    print("You dodge ANCIENT DRAUGR's attack.")
                    return

                damage = player.hurt(self, 5, 1)
                print(f"ANCIENT DRAUGR attacks you with their axe for {c.red(damage)} damage!")
        else:
            # magic attack
            damage = player.hurt(self, randint(3, 4), 3)
            player.affect(Chilled(), 4)
            print(f"ANCIENT DRAUGR uses frost magic, dealing {damage} damage and inflicting {c.effect(Chilled)}!")

enemyPool = {
    "prison":[([Skeleton], 6), ([Thief], 3), ([Ghoul], 3)],
    "crossroads":[([Rat, Rat], 3), ([Rat, Rat, Rat], 3), ([RatBeast], 3), ([BuffedGoblin], 3)],
    "mines":[([Worm], 12)]
} # each number means _ in 12 chance
# enemies are ordered weakest to strongest

specialEnemyPool = {
    "prison":[([SkeletonGuard], 6), ([Skeleton, Skeleton], 3), ([Draugr], 3)],
    "crossroads":[([Alchemist, Goblin, Goblin], 8), ([AncientDraugr], 4)],
    "mines":[([AncientDraugr], 12)]
} # special enemies are stronger and less common

def gen_enemies(area, normalEnemies, specialEnemies, dangerModifier = 0):
    enemies = []

    while len(enemies) < normalEnemies:
        # enemies with higher numbers are stronger
        enemyNum = randint(1, 12) + dangerModifier

        # compares enemyNum to the number in each tuple
        for fight in enemyPool[area]:
            # checks if the number is small enough or it is the last enemy
            if enemyNum <= fight[1] or enemyPool[area].index(fight) == len(enemyPool[area]) - 1:
                addedEnemies = []
                for enemy in fight[0]:
                    addedEnemies.append(enemy())

                enemies.append(addedEnemies)

                break
            # prepares enemyNum for next iteration
            else:
                enemyNum -= fight[1]

    # same as above except with special enemies
    for i in range(specialEnemies):
        enemyNum = randint(1, 12)

        for fight in specialEnemyPool[area]:
            if enemyNum <= fight[1] or specialEnemyPool[area].index(fight) == len(specialEnemyPool[area]) - 1:
                addedEnemies = []
                for enemy in fight[0]:
                    addedEnemies.append(enemy())

                enemies.append(addedEnemies)

                break
            else:
                enemyNum -= fight[1]

    return enemies