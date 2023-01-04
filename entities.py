from random import randint, choice
import color

c = color

class Creature:
    def __init__(self, name, health, gold):
        self.name = name
        self.gold = gold
        
        self.stealth = 0 # compared with opponents awareness in stealth checks
        self.dodge = 0 # percent chance to dodge
        self.resistance = 0 # resistance to some effects
        self.maxHealth = health # amount of possible damage taken before death
        self.awareness = 0 # compared with opponents stealth in awareness checks
        self.appraisal = 50 # highest value item that the value can be identified

        self.immuneTo = [] # effects that cannot be applied
        self.armorClass = 0 # reduced from incoming damage

        self.effects = [] #
        self.effectDurations = []
        self.health = health
        self.stunned = False
        
        self.strength = 0
        self.dexterity = 0
        self.constitution = 0
        self.intelligence = 0
        self.perception = 0

    def update_strength(self, increase):
    # strength is added to damage dealt
        self.strength += increase

    def update_dexterity(self, increase):
    # dexterity improves stealth and dodge
        self.dexterity += increase

        self.stealth += increase
        self.dodge += 5 * increase

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

    
    def hurt(self, damageTaken, attackerStrength, message, armorPiercing = 0):
    # lowers health but applies armor class and dodge        
        # applies strength
        if attackerStrength > 0:
            damageTaken += randint(attackerStrength // 2, attackerStrength)
        elif attackerStrength < 0: # prevents error from randint
            damageTaken += randint(attackerStrength // -2, attackerStrength * -1) * -1
        
        # applies armor piercing to armor class
        damageReduction = self.armorClass
        if damageReduction > 0:
            damageReduction -= armorPiercing
            if damageReduction < 0:
                damageReduction = 0

        # applies armor class and randomness to damage
        finalDamageTaken = damageTaken + randint(-1, 1) - damageReduction
        if finalDamageTaken < 0:
            finalDamageTaken = 0

        # applies dodge
        elif self.dodge > 0:
            if randint(0, 99) < self.dodge:
                finalDamageTaken = 0
                message += " The attack was dodged!"
        # if dodge is negative the attack may be critical
        elif self.dodge < 0:
            if randint(0, 99) < (self.dodge) * -1:
                finalDamageTaken = int(finalDamageTaken * 1.5) + attackerStrength
                message += " The attack was a critical hit!"

        self.health -= finalDamageTaken

        # applies color to finalDamageTaken
        damageMessage = ""
        if type(self) == Player:
            damageMessage = c.harm(str(finalDamageTaken))
        else:
            damageMessage = c.player(str(finalDamageTaken))
        
        message = message.replace("_", damageMessage)
        print(message)
        return finalDamageTaken

    def heal(self, healthRestored):
    # heals health but makes sure it doesn't exceed max health
        finalHealthRestored = healthRestored
        if self.health + healthRestored > self.maxHealth:
            finalHealthRestored = self.maxHealth - self.health

        self.health += finalHealthRestored
        return finalHealthRestored

    def affect(self, effect, duration):
    # applies resistance and immunities to an effect
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
            self.effects.append(effect(self))
            self.effectDurations.append(duration)
            return True
        else:
            return False

class Player(Creature):
# has inventory and equipment slots
    def __init__(self):
        super().__init__("you", 20, 0)

        self.inventorySize = 10
        self.inventory = []
        self.ring = None
        self.armor = None

        # stats for different items
        self.infernoRing = False

    def hurt(self, damageTaken, attackerStrength, message, armorPiercing = 0):
    # damages armor
        damageDealt = super().hurt(damageTaken, attackerStrength, message, armorPiercing)

        if self.armor != None:
            self.armor.degrade()

        # applies inferno ring's effect
        if self.infernoRing and randint(1, 3) == 1:
            self.affect(Burned, 6 - self.ring.enchantment)
            print(f"Your ring of rage {c.harm('BURNS')} you!")

        return damageDealt

player = Player() # creates the one and only instance of player

class Enemy(Creature):
# subclasses of Enemy require a method named attack()
    undead = False
    isSpecial = False # determines if the game should give a warning with this enemy
    
    def __init__(self, name, health, gold, awareness, stealth):
        super().__init__(name, health, (gold * randint(8, 12)) // 10)
        self.warning = "you feel uneasy" # printed when player detects enemy
        self.awareness = awareness + randint(-1, 1)
        self.stealth = stealth + randint(-1, 1)

    def do_turn(self, enemies):
        # parameter 'enemies' allows the method to see the whole battlefield
        if self.stunned:
            print(f"{self.name} is stunned and unable to fight")
            self.stunned = False
        else:
            self.attack(enemies)

class Boss(Enemy):
    def __init__(self, name, health):
        super().__init__(name, health, 100, 50, 50)

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
    permanent = False
    color = c.effectNeutral
    
    def __init__(self, target):
        self.target = target

    def update(self):
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
    color = c.effectBad
    
    def __init__(self, target):
        self.target = target

    def update(self):
        # lowers health by 1 every turn
        self.target.health -= 1

    def inspect(self):
        print("Deals 1 damage every turn.")

class Regeneration(Effect):
# heals 1 hp per turn
    name = "regeneration"
    color = c.effectGood
    
    def __init__(self, target):
        self.target = target

    def update(self):
        self.target.heal(1)

    def inspect(self):
        print("Heals 1 health every turn.")

class WellFed(Effect):
# heals 2 health per turn
    name = "well fed"
    color = c.effectGood
    
    def __init__(self, target):
        self.target = target

    def update(self):
        self.target.heal(2)

    def inspect(self):
        print("Heals 2 health every turn.")
        
class Dazed(Effect):
# lowers DEX
    name = "dazed"
    natural = True
    level = 1
    color = c.effectBad
    
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
    color = c.effectBad

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
    color = c.effectBad

    def __init__(self, target):
        self.target = target

        self.decayLevel = 1
        self.turnsToProgress = 2

        self.name = "decay lvl " + str(self.decayLevel)

        self.target.update_constitution(-self.decayLevel)

    def update(self):
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
        print(f"This effect becomse stronger in {turnsToProgress} turns.")

class BrokenBones(Effect):
# lowers DEX, STR, permanent
# instantly kills skeletons
    name = "broken bones"
    natural = True
    level = 3
    permanent = True
    color = c.effectBad

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
    color = c.effectBad

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
    color = c.effectBad

    def __init__(self, target):
        self.target = target

    def update(self):
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
    color = c.effectBad

    def __init__(self, target):
        self.target = target
        
        self.target.strength -= 1

    def update(self):
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
    undead = True
    isSpecial = True
    
    def __init__(self):
        super().__init__("draugr", 18, 20, 5, 3)
        self.resistance = 2
        self.armorClass = 2

    def hurt(self, damageTaken, attackerStrength, message, armorPiercing = 0):
        damageDealt = super().hurt(damageTaken, attackerStrength, message, armorPiercing)

        if randint(1, 2) or damageDealt > 3:
            self.resistance -= 1
            self.armorClass -= 1
            self.maxHealth -= 1
            print("the DRAUGR's armor degrades")
        
        return damageDealt
        
    def attack(self, enemies):
        message = "the DRAUGR hits you with their axe for _ damage"
        if randint(1, 3) == 1:
            player.affect(Bleeding, 4)
            player.hurt(4, self.strength, message + f", leaving you {c.harm('BLEEDING')}!")
        else:
            player.hurt(5, self.strength, message + "!")

class Ghoul(Enemy):
# an uncommon, more aware enemy that appears in the prison
# can dodge attacks and inflicts decay
    undead = True
    
    def __init__(self):
        super().__init__("ghoul", 16, 11, 2, 2)
        self.dodge = 10
        
        self.warning = "you smell a foul stench"

    def attack(self, enemies):
        if randint(1, 3) == 1:
            print(f"the GHOUL curses you with {c.harm('DECAY')}, lowering your CON over time")

            player.affect(Decay, 6)
        else:
            player.hurt(4, self.strength, "the GHOUL attacks you for _ damage!")

class Skeleton(Enemy):
# a common enemy type throughout the dungeon
# is immune to most natural effects and often staggers instead of attacking
    undead = True
    
    def __init__(self):
        super().__init__("skeleton", 15, 8, 2, 1)
        self.immuneTo = [Bleeding, Burned]
        self.damage = 3
        self.staggerChance = 2 # _ in 6
        
        self.warning = "you hear bones moving around"
        self.weapon = choice(["sword", "spear", "mace"])

    def do_turn(self, enemies):
    # there is a chance that skeletons stagger and don't attack
        if randint(0, 5) < self.staggerChance:
            print(f"{self.name.upper()} staggers and misses their attack")
        else:
            super().do_turn(enemies)

    def attack(self, enemies):
        message = f"the {self.name.upper()} hits you with their {self.weapon} for _ damage"

        # spears  have armor piercing
        armorPiercing = 1
        if self.weapon == "spear" and randint(1, 3) < 3:
            armorPiercing += 1

        # swords can inflict bleeding
        inflictsBleeding = (randint(1, 4) == 1) and (self.weapon == "sword")
        if inflictsBleeding:
            inflictsBleeding = player.affect(Bleeding, 4)

        # maces can inflict dazed
        inflictsDazed = (randint(1, 4) == 1) and (self.weapon == "mace")
        if inflictsDazed:
            inflictsDazed = player.affect(Dazed, 1)

        # does damage
        if inflictsBleeding:
            player.hurt(self.damage, self.strength, message + f", leaving you {c.harm('BLEEDING')}!", armorPiercing)
        elif inflictsDazed:
            player.hurt(self.damage, self.strength, message + f", leaving you {c.harm('DAZED')}!", armorPiercing)
        else:
            player.hurt(self.damage, self.strength, message + "!", armorPiercing)

class ArmoredSkeleton(Skeleton):
# has some AC and staggers more, always has a mace
# currently unused
    def __init__(self):
        super().__init__()
        self.gold = 10
        
        self.staggerChance = 3
        self.armorClass = 1
        
        self.weapon = "mace"
        self.name = "armored skeleton"
        self.warning = "you hear the clanking of bones and metal"

class SkeletonGuard(Skeleton):
# has more AC, staggers less, always has a spear, very aware
    isSpecial = True
    
    def __init__(self):
        super().__init__()
        self.gold = 15
        
        self.staggerChance = 1
        self.armorClass = 2
        self.awareness = 4
        self.stealth = -1

        self.weapon = "spear"
        self.name = "skeleton guard"
        self.warning = "you hear the clanking of bones and metal"

class Thief(Enemy):
# an uncommon, stealthy and aware enemy
# hits you with a poison dart when at full health, might run away later in combat
    def __init__(self):
        super().__init__("thief", 18, 14, 4, 4)
        self.warning = "you sense that someone is watching you"

        self.time = 0

    def do_turn(self, enemies):
    # as time goes on, they are more likely to run away
        super().do_turn(enemies)
        
        self.time += 1
        if randint(1, 4) < self.time:
            self.health = 0
            print("the THIEF runs away")

    def attack(self, enemies):
        if player.health < player.maxHealth:
            player.hurt(4, self.strength, "the THIEF stabs you for _ damage!", randint(1, 2))
        else:
            print(f"the THIEF hits you with a dart, leaving you {c.harm('POISONED')}!")

            player.affect(Poisoned, 6)
    
class Ogre(Boss):
# big enemy, can inflict dazed, bleeding, and broken bones
    def __init__(self):
        super().__init__("ogre", 35)
        self.strength = 1
        self.armorClass = 1
        self.resistance = 2
        self.dodge = -10
        
        self.isRaged = False
        self.isCharging = False
        self.previousMove = "heavy"

    def attack(self, enemies):
        # becomes stronger when below 20 HP
        if self.health < 20 and not self.isRaged:
            self.isRaged = True
            self.strength += 3
            print("the OGRE is enraged, increasing their damage")
        
        # choses move, can't do the same twice in a row
        choices = ["heavy", "slam", "attack"]
        choices.remove(self.previousMove)
        chosenMove = choice(choices)

        if not self.isCharging:
            self.previousMove = chosenMove

        if self.isCharging:
            self.isCharging = False
            message = "the OGRE hits you with a devastating blow, dealing _ damage!"
            player.dodge -= 15 # attack is less likely to be dodge
            damageDealt = player.hurt(8, self.strength, message, 2)
            player.dodge += 15
            # if enough damage is dealt, it breaks bones
            if damageDealt > 8:
                if player.affect(BrokenBones, 1):
                    print("you have BROKEN BONES")
            
        elif chosenMove == "heavy":
            print("the OGRE is charging up a swing")
            self.isCharging = True

        elif chosenMove == "slam":
            message = "the OGRE slams the ground, dealing _ damage and leaving you DAZED!"
            player.hurt(3, self.strength, message, 1)
            player.affect(Dazed, 2)

        else:
            message = "the OGRE hits you with their club for _ damage"
            if player.affect(Bleeding, 3):
                message += ", leaving you BLEEDING"
            player.hurt(5, self.strength, message + "!", 0)    

enemyPool = {
    "prison":[([Skeleton], 6), ([Thief], 4), ([Ghoul], 2)],
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