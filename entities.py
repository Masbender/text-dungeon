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
    effectDurations = None
    stunned = False

    def __init__(self):
        self.health = self.maxHealth

        self.immuneTo = []
        self.effects = []
        self.effectDurations = []

    def update_strength(self, increase):
    # strength is added to damage dealt
        self.strength += increase

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
    # lowers health but applies armor class and strength
        # uses attackers strength as default
        if strength == None:
            strength = attacker.strength

        finalDamage = damage

        # applies strength
        if strength > 0:
            finalDamage += randint(strength // 2, strength)
        elif strength < 0:
            finalDamage += randint(strength, strength // 2)

        # applies piercing
        damageReduction = self.armorClass
        if damageReduction > 0:
            damageReduction -= piercing
            if damageReduction < 0:
                damageReduction = 0

        # applies armor class and randomnes
        finalDamage += + randint(-1, 1) - damageReduction 
        if finalDamage < 0:
            finalDamage = 0

        # applies damage
        self.health -= finalDamage
        return finalDamage

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
        if effect.natural and self.resistance > effect.level:
            if (duration - self.resistance + effect.level) > 0:
                duration += effect.level - self.resistance
            else:
                return False

        # checks for duplicate effects
        for i in range(len(self.effects)):
            if effect == type(self.effects[i]):
                # checks which effect is longer
                if self.effectDurations[i] < duration or duration < 0:
                    self.effects[i].reverse()
                    self.effectDurations.pop(i)
                    self.effects.pop(i)
                    break
                else:
                    return False

        # checks if immune to effect
        if not effect in self.immuneTo:
            effect = effect(self)

            if isPermanent:
                effect.isPermanent = True
                duration = -1
            
            self.effects.append(effect)
            self.effectDurations.append(duration)
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

    baseSTR = 0
    baseCON = 0
    baseDEX = 0
    basePER = 0
    baseINT = 0

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
            print(f"Your Ring of Illusion stuns {attacker.name}.")

        return dodged

    def hurt(self, attacker, damage, piercing = 0, strength = None):
    # damages armor
        damageDealt = super().hurt(attacker, damage, piercing, strength)

        if self.armor != None:
            self.armor.degrade()

        # applies inferno ring's effect
        if self.infernoRing and randint(1, 3) == 1:
            self.affect(Burned, 6 - self.ring.enchantment)
            print(f"You are {c.effect(Burned)} by your Ring of Rage!")

        return damageDealt

player = Player() # creates the one and only instance of player

class Enemy(Creature):
# subclasses of Enemy require a method named attack()
    # more identifying information
    battleMessages = ["ENEMY notices you!"] # note that ENEMY is only colored in stealth due to the need to alert the player
    stealthMessages = [c.threat("ENEMY") + " not notice you"]
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
    awareness = 100
    stealth = -100

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
    
    def __init__(self, target):
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

class Bleeding(Effect):
# does 1 damage per turn
    name = "bleeding"
    natural = True
    level = 0
    color = c.effect_bad
    
    def __init__(self, target):
        self.target = target

    def update(self, enemies):
        # lowers health by 1 every turn
        self.target.health -= 1

    def inspect(self):
        print("Deals 1 damage every turn.")

class Regeneration(Effect):
# heals 1 hp per turn
    name = "regeneration"
    color = c.effect_good
    
    def __init__(self, target):
        self.target = target

    def update(self, enemies):
        self.target.heal(1)

    def inspect(self):
        print("Heals 1 health every turn.")

class WellFed(Effect):
# heals 2 health per turn
    name = "well fed"
    color = c.effect_good
    
    def __init__(self, target):
        self.target = target

    def update(self, enemies):
        self.target.heal(2)

    def inspect(self):
        print("Heals 2 health every turn.")
        
class Dazed(Effect):
# lowers DEX
    name = "dazed"
    natural = True
    level = 1
    color = c.effect_bad
    
    def __init__(self, target):
        self.target = target

        self.target.update_dexterity(-1)

    def reverse(self):
        self.target.update_dexterity(1)

    def inspect(self):
        print("Lowers DEX by 1, reducing your stealth and dodge chance.")

class Surprised(Effect):
# lowers DEX and AC
    name = "surprised"
    color = c.effect_bad

    def __init__(self, target):
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

    def __init__(self, target):
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
# lowers DEX, STR, permanent
# instantly kills skeletons
    name = "broken bones"
    natural = True
    level = 3
    color = c.effect_bad

    def __init__(self, target):
        self.target = target

        if issubclass(type(self.target), Skeleton):
            self.target.health = 0
            print(self.target.name + " dies")

        self.target.update_dexterity(-4)
        self.target.update_strength(-1)
        
    def reverse(self):
        self.target.update_dexterity(4)
        self.target.update_strength(1)

    def inspect(self):
        print("Lowers DEX by 4 and STR by 1.")

class Burned(Effect):
# lowers AC by 1
    name = "burned"
    natural = True
    level = -2
    color = c.effect_bad

    def __init__(self, target):
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
    level = 3
    color = c.effect_bad

    def __init__(self, target):
        self.target = target

    def update(self, enemies):
        self.target.affect(Burned, 5)
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

    def __init__(self, target):
        self.target = target
        
        self.target.strength -= 1

    def update(self, enemies):
        self.target.health -= 1

    def reverse(self):
        self.target.strength +=1 

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
    stealthMessages = [c.threat("DRAUGR") + " is on the hunt for human.",
                      c.threat("DRAUGR") + " does not notice you, it's armor appears brittle and unlikely to withstand a long fight."]
    undead = True
    isSpecial = True

    maxHealth = 18
    gold = 20
    awareness = 2
    stealth = 2
    
    resistance = 2
    armorClass = 2

    def hurt(self, attacker, damage, piercing = 0, strength = None):
        damageDealt = super().hurt(attacker, damage, piercing, strength)

        if randint(0, 1) or damageDealt > 4:
            self.resistance -= 1
            self.armorClass -= 1
            self.maxHealth -= 1
            print("DRAUGR's armor degrades.")
        
        return damageDealt
        
    def attack(self, enemies):
        if player.dodge(self):
            print(f"You dodge DRAUGR's attack.")
            return

        if randint(1, 3) == 1:
            if player.affect(Bleeding, 4):
                damage = player.hurt(self, 4)
                print(f"DRAUGR hits you with their axe for {c.harm(damage)} damage, leaving you {c.effect(Bleeding)}!")
        else:
            damage = player.hurt(self, 5)
            print(f"DRAUGR hits you with their axe for {c.harm(damage)} damage!")

class Ghoul(Enemy):
# an uncommon, more aware enemy that appears in the prison
# can dodge attacks and inflicts decay
    name = "GHOUL"
    warning = "You smell a foul stench..."
    battleMessages = ["You confront GHOUL, a foul, agile beast!",
                     "GHOUL detects your presence! It can barely see but has an excellent sense of smell."]
    stealthMessages = [c.threat("GHOUL") + " is roaming.",
                      c.threat("GHOUL") + " is waiting for human, they have yet to notice you."]
    undead = True

    maxHealth = 16
    gold = 11
    awareness = 2
    stealth = 1
    
    dodgeChance = 10
    strength = -1 # 4 damage felt like too much but 3 is too little, so this nerfs 4 a little bit

    def attack(self, enemies):
        if randint(1, 3) == 1:
            if player.affect(Decay, 6):
                print(f"GHOUL curses you with {c.effect(Decay)}!")
                return
        
        if player.dodge(self):
            print("You dodge GHOUL's bite.")
            return

        damage = player.hurt(self, 4)
        print(f"GHOUL bites you for {c.harm(damage)} damage!")

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
        self.immuneTo.extend([Bleeding, Burned])

        if self.name == "SKELETON": # doesn't apply to subclasses
            self.weapon = choice(["sword", "spear", "mace"])
            self.battleMessages = [f"SKELETON grips their {self.weapon}!",
                                  "SKELETON finally gets to see some action!"]
            self.stealthMessages = [c.threat("SKELETON") + f" is holding a {self.weapon}, and is searching for a target."]

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
                if player.affect(Bleeding, 4):
                    effect = Bleeding

            # maces inflict dazed
            if self.weapon == "mace":
                if player.affect(Dazed, 2):
                    effect = Dazed
        
        # does damage
        if effect == None:
            damage = player.hurt(self, self.damage, piercing)
            print(f"{self.name} attacks you with their {self.weapon} for {c.harm(damage)} damage!")
        else:
            damage = player.hurt(self, self.damage, piercing)
            print(f"{self.name} attacks you with their {self.weapon} for {c.harm(damage)} damage, leaving you {c.effect(effect)}!")

class SkeletonGuard(Skeleton):
# has more AC, staggers less, always has a spear, very aware
    name = "SKELETON GUARD"
    warning = "You hear the clanking of bones and metal..."
    battleMessages = ["SKELETON GUARD raises their shield!",
                    "SKELETON GUARD will not let it's training go to waste!"]
    stealthMessages = [c.threat("SKELETON GUARD") + " is alert, but has failed to notice you.",
                      c.threat("SKELETON GUARD") + " is determined to let none pass, but seems to have have failed."]
    isSpecial = True

    maxHealth = 15
    gold = 16
    awareness = 4
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
    stealthMessages = [c.threat("THIEF") + " is looking for a victim.",
                      c.threat("THIEF") + " is preparing poisons, and is unaware of your presence."]

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
            print("THIEF runs away!")
            
        elif self.time == 3:
            print(choice(["THIEF seems eager to escape.", "THIEF wants to flee."]))

    def attack(self, enemies):
        if not self.hasDart:
            if player.dodge(self):
                print("You dodge THIEF's dagger.")
                return

            damage = player.hurt(self, 4)
            print(f"THIEF stabs you for {c.harm(damage)} damage!")
        else:
            self.hasDart = False
            if player.dodge(self):
                print("You dodge THIEF's dart.")
                return
            
            if player.affect(Poisoned, 6):
                print(f"THIEF hits you with a dart, inflicting {c.effect(Poisoned)}!")
            else:
                player.health -= 1
                print(f"THIEF hits you with a dart, but you resist it's poison.")
    
class Ogre(Boss):
# big enemy, can inflict dazed, bleeding, and broken bones
    name = "OGRE"
    warning = "You hear sounds that can only belong to a massive beast..."
    battleMessages = ["\"Long time it's been since human dared wander down here, you make tasty treat.\""]

    maxHealth = 35
    gold = 60
    
    strength = 1
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
            print("OGRE is enraged!")
        
        # choses move, can't do the same twice in a row
        choices = ["heavy", "slam", "attack"]
        choices.remove(self.previousMove)
        chosenMove = choice(choices)

        if not self.isCharging:
            self.previousMove = chosenMove

        if self.isCharging:
            self.isCharging = False

            if player.dodge(self):
                print("You manage to dodge OGRE's heavy swing.")
                return
            
            damage = player.hurt(self, 8, 1)

            if damage > 8:
                if player.affect(BrokenBones):
                    print(f"OGRE hits you with a heavy strike, dealing {c.harm(damage)} and inflicting {c.effect(BrokenBones)}!")
                    return
            
            print(f"OGRE hits you with a heavy strike, dealing {c.harm(damage)} damage!")
            
        elif chosenMove == "heavy":
            print("OGRE prepares a heavy swing!")
            self.isCharging = True

        elif chosenMove == "slam":
            if player.dodge(self):
                print("OGRE slams the ground, but you get out of the way.")
                return

            damage = player.hurt(self, 3, 3)
            if player.affect(Dazed, 2):
                print(f"OGRE slams the ground, dealing {c.harm(damage)} damage and leaving you {c.effect(Dazed)}!")
            else:
                print(f"OGRE slams the ground, dealing {c.harm(damage)}!")            

        else:
            if player.dodge(self):
                print("You dodge OGRE's club!")
                return

            damage = player.hurt(self, 5)

            if player.affect(Bleeding, 3):
                print(f"OGRE hits you with their club, dealing {c.harm(damage)} damage, leaving you {c.effect(Bleeding)}!")
            else:
                print(f"OGRE hits you with their club, delaing {c.harm(damage)} damage!")

enemyPool = {
    "prison":[([Skeleton], 6), ([Thief], 3), ([Ghoul], 3)],
} # each number means _ in 12 chance
# enemies are ordered weakest to strongest

specialEnemyPool = {
    "prison":[([SkeletonGuard], 6), ([Skeleton, Skeleton], 3), ([Draugr], 3)]
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