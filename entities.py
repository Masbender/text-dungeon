from random import randint, choice
from extra import slowprint
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
    armorClass = 0 # reduced from incoming damage
    dodgeChance = 0 # percent chance to dodge
    resistance = 0 # resistance to some effects
    appraisal = 50 # highest value item that the value can be identified

    # these are mainly used for the player, mostly modify basic stats
    strength = 0 # increases damage
    dexterity = 0 # +dodge +stealth
    constitution = 0 # +maxHeatlh +resistance
    intelligence = 0 # increases gear durability and scroll effectiveness
    perception = 0 # +awareness +appraisal

    # temporary stats that keep track of combat status
    health = 0
    effects = None
    stunned = False

    #portrait
    portrait = """ _____
|  O_O |
| [__] |
|_LL_L_|"""

    def __init__(self):
        self.health = self.maxHealth

        self.immuneTo = []
        self.effects = []

    def update_strength(self, increase):
    # strength is added to damage dealt
        self.strength += increase
        if issubclass(type(self), Player):
            self.inventorySize += increase

    def update_dexterity(self, increase):
    # dexterity improves stealth and dodge
        self.dexterity += increase

        self.stealth += increase
        self.dodgeChance += 5 * increase

    def update_constitution(self, increase):
    # constitution improves health and resistance
        self.constitution += increase

        self.resistance += increase
        self.maxHealth += 2 * increase
        self.health += 2 * increase

    def update_intelligence(self, increase):
    # intelligence is how likely a used item or armor is to not break
        self.intelligence += increase
    
    def update_perception(self, increase):
    # perception improves awareness and appraisal
        self.perception += increase

        self.awareness += increase
        self.appraisal += increase * 25
    
    def set_stats(self, str, con, dex, per, int):
    # sets all 5 stats at once
        self.update_strength(str - self.strength)
        self.update_dexterity(dex - self.dexterity)
        self.update_constitution(con - self.constitution)
        self.update_intelligence(int - self.intelligence)
        self.update_perception(per - self.perception)

    def dodge(self, attacker):
        number = randint(0, 99)
        return self.dodgeChance > number

    def hurt(self, attacker, damage, piercing = 0, strength = None):
        # uses attacker strength by default, but can be overridden
        if strength == None:
            strength = attacker.strength
            
        reduction = self.armorClass
        if reduction > 0 and piercing > 0: # piercing is only applied if AC > 0
            reduction -= piercing
            if reduction < 0: # piercing can't lead to -AC
                reduction = 0
                
        reduction /= 2.0 # each point of AC is only 0.5 damage reduction
        
        # applies reduction and strength, each point of strength is 0.75 extra damage
        finalDamage = damage - reduction + (strength * 0.75)
        
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
        finalHealthRestored = healthRestored
        if self.health + healthRestored > self.maxHealth:
            finalHealthRestored = self.maxHealth - self.health

        self.health += finalHealthRestored
        return finalHealthRestored

    def affect(self, effect, duration = 0):
    # applies resistance and immunities to an effect
        isPermanent = duration == 0
        
        # applies resistance
        if effect.natural and self.resistance > effect.level and not isPermanent:
            if (duration - self.resistance + effect.level) > 0:
                duration += effect.level - self.resistance
            else:
                return False

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

    inventorySize = 10
    inventory = []
    ring = None
    armor = None
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
            slowprint(f"Your Ring of Illusion stuns {attacker.name}.")

        return dodged

    def hurt(self, attacker, damage, piercing = 0, strength = None):
    # damages armor
        damageDealt = super().hurt(attacker, damage, piercing, strength)

        if self.armor != None:
            self.armor.degrade()

        # applies inferno ring's effect
        if self.infernoRing and randint(1, 3) == 1:
            self.affect(Burned(), 6 - self.ring.enchantment)
            slowprint(f"You are {c.effect(Burned)} by your Ring of Rage!")

        return damageDealt

player = Player() # creates the one and only instance of player

class Enemy(Creature):
# subclasses of Enemy require a method named attack()
    # more identifying information
    battleMessages = ["ENEMY notices you!"] # note that ENEMY is only colored in stealth due to the need to alert the player
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
            slowprint(f"{self.name} is stunned and unable to fight")
            self.stunned = False
        else:
            self.attack(enemies)

class Boss(Enemy):
    awareness = 100
    stealth = -100

    isSpecial = True

    def do_turn(self, enemies):
    # less likely to be stunned
        if self.stunned:
            if randint(0, 1):
                slowprint(f"{self.name} is stunned and unable to fight")
                self.stunned = False
            else:
                slowprint(f"{self.name} resisted the stun")
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
        print("This is an effect.")

class Electrocuted(Effect):
# stuns the target every other turn
    name = "electrocuted"
    color = c.effect_bad

    def update(self, enemies):
        if self.duration % 2 == 0:
            self.target.stunned = True

    def inspect(self):
        print("Stuns you every other turn.")

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
        print("Deals 1 damage every turn.")

class Regeneration(Effect):
# heals 1 hp per turn
    name = "regeneration"
    color = c.effect_good

    def update(self, enemies):
        self.target.heal(1)

    def inspect(self):
        print("Heals 1 health every turn.")

class WellFed(Effect):
# heals 2 health per turn
    name = "well fed"
    color = c.effect_good

    def update(self, enemies):
        self.target.heal(2)

    def inspect(self):
        print("Heals 2 health every turn.")
        
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

        self.target.update_dexterity(-1)
        self.target.update_perception(-1)

        self.allowRun = self.allowRun and self.target.isSpecial and not issubclass(type(target), Boss)

        if self.allowRun:
            self.target.isSpecial = False
        

    def reverse(self):
        self.target.update_dexterity(1)
        self.target.update_perception(1)

        if self.allowRun:
            self.target.isSpecial = True

    def inspect(self):
        print("Lowers DEX and PER by 1.")

class Surprised(Effect):
# lowers DEX and AC
    name = "surprised"
    color = c.effect_bad

    def apply(self, target):
        self.target = target

        self.target.update_dexterity(-2)
        self.target.armorClass -= 1

    def reverse(self):
        self.target.update_dexterity(2)
        self.target.armorClass += 1

    def inspect(self):
        print("Lowers armor class by 1 and DEX by 2.")

class Decay(Effect):
# lowers CON, gets stronger over time
    name = "decay"
    color = c.effect_bad

    def apply(self, target):
        self.target = target

        self.decayLevel = 1
        self.turnsToProgress = 2

        self.name = "decay lvl " + str(self.decayLevel)

        self.target.update_constitution(-self.decayLevel)

    def update(self, enemies):
        self.turnsToProgress -= 1

        if self.turnsToProgress == 0:
            self.decayLevel += 1
            self.name = "decay lvl " + str(self.decayLevel)
            self.turnsToProgress = self.decayLevel + 1
            self.target.update_constitution(-1)

    def reverse(self):
        self.target.update_constitution(self.decayLevel)

    def inspect(self):
        print(f"Lowers your CON by {self.decayLevel}.")
        print(f"This effect becomse stronger in {self.turnsToProgress} turns.")

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
            slowprint(self.target.name + " dies")

        self.target.update_dexterity(-1)
        self.target.update_strength(-1)
        self.target.update_constitution(-1)
        
    def reverse(self):
        self.target.update_dexterity(1)
        self.target.update_strength(1)
        self.target.update_constitution(1)

    def inspect(self):
        print("Lowers STR, CON, and DEX by 1.")

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
        print("Lowers armor class by 1.")

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
        print("Deals 2 damage every turn.")
        print("Applies burned.")

class Poisoned(Effect):
# does 1 damage per turn and lowers STR
    name = "poisoned"
    natural = True
    level = -1
    color = c.effect_bad

    def apply(self, target):
        self.target = target
        
        self.target.update_strength(-1)

    def update(self, enemies):
        self.target.health -= 1

    def reverse(self):
        self.target.update_strength(1)

    def inspect(self):
        print("Lowers STR by 1.")
        print("Deals 1 damage every turn.")

class Draugr(Enemy):
# a rare enemy that can appear in earlier floors
# starts with armor but it degrades when hurt
# can inflict bleeding
    name = "DRAUGR"
    battleMessages = ["DRAUGR readies their axe with malicious intent!",
                     "DRAUGR charges at you with their axe!"]
    stealthMessages = [c.red("DRAUGR") + " is on the hunt for human.",
                      c.red("DRAUGR") + " does not notice you, it's armor appears brittle and unlikely to withstand a long fight."]
    undead = True
    isSpecial = True

    maxHealth = 18
    gold = 20
    awareness = 2
    stealth = 2
    
    resistance = 2
    armorClass = 3

    def hurt(self, attacker, damage, piercing = 0, strength = None):
        damageDealt = super().hurt(attacker, damage, piercing, strength)

        if randint(0, 1) or damageDealt > 4:
            self.resistance -= 1
            self.armorClass -= 1
            self.maxHealth -= 1
            self.health -= 1
            slowprint("DRAUGR's armor degrades.")
        
        return damageDealt
        
    def attack(self, enemies):
        if player.dodge(self):
            slowprint(f"You dodge DRAUGR's attack.")
            return

        if randint(1, 3) == 1:
            if player.affect(Bleeding(), 4):
                damage = player.hurt(self, 4)
                slowprint(f"DRAUGR hits you with their axe for {c.red(damage)} damage, leaving you {c.effect(Bleeding)}!")
        else:
            damage = player.hurt(self, 5)
            slowprint(f"DRAUGR hits you with their axe for {c.red(damage)} damage!")

class Ghoul(Enemy):
# an uncommon, more aware enemy that appears in the prison
# can dodge attacks and inflicts decay
    name = "GHOUL"
    warning = "You smell a foul stench..."
    battleMessages = ["You confront GHOUL, a foul, agile beast!",
                     "GHOUL detects your presence! It can barely see but has an excellent sense of smell."]
    stealthMessages = [c.red("GHOUL") + " is roaming.",
                      c.red("GHOUL") + " is waiting for human, they have yet to notice you."]
    undead = True

    maxHealth = 16
    gold = 11
    awareness = 2
    stealth = 1
    
    dodgeChance = 10
    strength = -1 # 4 damage felt like too much but 3 is too little, so this nerfs 4 a little bit

    def attack(self, enemies):
        if randint(1, 3) == 1:
            if player.affect(Decay(), 6):
                slowprint(f"GHOUL curses you with {c.effect(Decay)}!")
                return
        
        if player.dodge(self):
            slowprint("You dodge GHOUL's bite.")
            return

        damage = player.hurt(self, 4)
        slowprint(f"GHOUL bites you for {c.red(damage)} damage!")

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
            self.stealthMessages = [c.red("SKELETON") + f" is holding a {self.weapon}, and is searching for a target."]

    def do_turn(self, enemies):
    # there is a chance that skeletons stagger and don't attack
        if randint(0, 5) < self.staggerChance:
            slowprint(f"{self.name} staggers and misses their attack.")
            self.stunned = False
        else:
            super().do_turn(enemies)

    def attack(self, enemies):
        # checks dodge
        if player.dodge(self):
            slowprint(f"You dodge SKELETONS {self.weapon}.")
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
            slowprint(f"{self.name} attacks you with their {self.weapon} for {c.red(damage)} damage!")
        else:
            damage = player.hurt(self, self.damage, piercing)
            slowprint(f"{self.name} attacks you with their {self.weapon} for {c.red(damage)} damage, leaving you {c.effect(effect)}!")

class SkeletonGuard(Skeleton):
# has more AC, staggers less, always has a spear, very aware
    name = "SKELETON GUARD"
    warning = "You hear the clanking of bones and metal..."
    battleMessages = ["SKELETON GUARD raises their shield!",
                    "SKELETON GUARD will not let it's training go to waste!"]
    stealthMessages = [c.red("SKELETON GUARD") + " promised not to fall asleep this time... but has failed.",
                       c.red("SKELETON GUARD") + " is determined to let none pass, but seems to have have failed."]
    isSpecial = True

    maxHealth = 17
    gold = 16
    awareness = 5
    stealth = -1

    armorClass = 2
    immuneTo = [Bleeding, Burned]

    staggerChance = 1 # _ in 6
    weapon = "spear"

class Thief(Enemy):
# an uncommon, stealthy and aware enemy
# hits you with a poison dart when at full health, might run away later in combat
    name = "THIEF"
    warning = "You are being watched..."
    battleMessages = ["THIEF prepares a poison dart!",
                     "THIEF eyes your gold pouch!"]
    stealthMessages = [c.red("THIEF") + " is looking for a victim.",
                      c.red("THIEF") + " is preparing poisons, and is unaware of your presence."]

    maxHealth = 16
    gold = 14
    awareness = 1
    stealth = 4

    time = 0
    hasDart = True

    def do_turn(self, enemies):
    # as time goes on, they are more likely to run away
        super().do_turn(enemies)
        
        self.time += 1
        if randint(1, 4) < self.time:
            self.health = 0
            slowprint("THIEF runs away!")
            
        elif self.time == 3:
            slowprint(choice(["THIEF seems eager to escape.", "THIEF wants to flee."]))

    def attack(self, enemies):
        if not self.hasDart:
            if player.dodge(self):
                slowprint("You dodge THIEF's dagger.")
                return

            damage = player.hurt(self, 4)
            slowprint(f"THIEF stabs you for {c.red(damage)} damage!")
        else:
            self.hasDart = False
            if player.dodge(self):
                slowprint("You dodge THIEF's dart.")
                return
            
            if player.affect(Poisoned(), 6):
                slowprint(f"THIEF hits you with a dart, inflicting {c.effect(Poisoned)}!")
            else:
                player.health -= 1
                slowprint(f"THIEF hits you with a dart, but you resist its poison.")
    
class Ogre(Boss):
# big enemy, can inflict dazed, bleeding, and broken bones
    name = "OGRE"
    warning = "You hear the sounds of an ogre..."
    battleMessages = ["\"Long time it's been since human dared wander down here, you make tasty treat.\""]

    maxHealth = 34
    gold = 60
    
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
            self.strength += 3
            slowprint("OGRE is enraged!")
        
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
                slowprint("You manage to dodge OGRE's heavy swing.")
                player.dodgeChance -= 10
                return
            player.dodgeChance -= 10
            
            damage = player.hurt(self, 8, 1)

            if damage > 8:
                if player.affect(BrokenBones()):
                    slowprint(f"OGRE hits you with a heavy strike, dealing {c.red(damage)} and inflicting {c.effect(BrokenBones)}!")
                    return
            
            slowprint(f"OGRE hits you with a heavy strike, dealing {c.red(damage)} damage!")
            
        elif chosenMove == "heavy":
            slowprint("OGRE prepares a heavy swing!")
            self.isCharging = True

        elif chosenMove == "slam":
            if player.dodge(self):
                slowprint("OGRE slams the ground, but you get out of the way.")
                return

            damage = player.hurt(self, 3, 3)
            if player.affect(Dazed(), 2):
                slowprint(f"OGRE slams the ground, dealing {c.red(damage)} damage and leaving you {c.effect(Dazed)}!")
            else:
                slowprint(f"OGRE slams the ground, dealing {c.red(damage)} damage!")            

        else:
            if player.dodge(self):
                slowprint("You dodge OGRE's club!")
                return

            damage = player.hurt(self, 5)

            if player.affect(Bleeding(), 3):
                slowprint(f"OGRE hits you with their club, dealing {c.red(damage)} damage, leaving you {c.effect(Bleeding)}!")
            else:
                slowprint(f"OGRE hits you with their club, delaing {c.red(damage)} damage!")

class Rat(Enemy):
# a weak enemy who spawns in large groups
# can inflict self with decay, then infects the player
    name = "RAT"
    warning = "You hear small creatures running around..."
    battleMessages = ["RAT snarls!", 
                      "RAT releases a battle cry!"]
    stealthMessages = [c.red("RAT") + " is sleeping. Some of their bones are visible.",
                      c.red("RAT") + " is eating. They are a foul, decayed creature.",
                      "You find " + c.red("RAT") + ", who is much more mutated than any rat on the surface.",
                      "You see " + c.red("RAT") + ", who is not in very good condition.",
                      c.red("RAT") + " is roaming."]

    maxHealth = 12
    gold = 7
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
        if randint(0, 2) == 2 and player.armor != None:
            piercing = 2
            if player.armorClass > 4:
                piercing += 1
            damage = player.hurt(self, 4, piercing)
            player.armor.degrade()
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

class RatBeast(Enemy):
# tough enemy, rages when low health, loses hp over time
# can bite and ram, starts injured and with a random effect
    name = "RAT BEAST"
    warning = "You hear a loud wheezing..."
    battleMessages = ["RAT BEAST lumbers towards you!",
                     "RAT BEAST lets out a loud roar!"]
    stealthMessages = [c.red("RAT BEAST") + " is wandering.",
                      c.red("RAT BEAST") + " is looking for their next meal.",
                      "You encounter a " + c.red("RAT BEAST") + ", a rat the size of a bear."]

    maxHealth = 32
    gold = 15
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
                print(f"You evade RAT BEAST, and they hit a wall, leaving them {c.effect(Dazed)}.")
                self.affect(Dazed(), 2)
                player.dodgeChance -= 5
                return
            player.dodgeChance -= 5

            damage = player.hurt(self, 5, 3)
            player.affect(Dazed(), randint(1, 2))
            print(f"RAT BEAST rams you for {c.red(damage)} damage, leaving you {c.effect(Dazed)}!")

enemyPool = {
    "prison":[([Skeleton], 6), ([Thief], 3), ([Ghoul], 3)],
    "crossroads":[([Rat, Rat], 3), ([Rat, Rat, Rat], 3), ([RatBeast,], 6)]
} # each number means _ in 12 chance
# enemies are ordered weakest to strongest

specialEnemyPool = {
    "prison":[([SkeletonGuard], 6), ([Skeleton, Skeleton], 3), ([Draugr], 3)],
    "crossroads":[([SkeletonGuard], 12)]
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