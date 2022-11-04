from random import randint, choice

class Creature:
    def __init__(self, name, health):
        self.name = name
        
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
        damageTaken += randint(attackerStrength // 2, attackerStrength)
        
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
        message = message.replace("_", str(finalDamageTaken))
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
        super().__init__("you", 20)

        self.inventorySize = 10
        self.inventory = []
        self.ring = None
        self.armor = None

    def hurt(self, damageTaken, attackerStrength, message, armorPiercing = 0):
    # damages armor
        damageDealt = super().hurt(damageTaken, attackerStrength, message, armorPiercing)

        if self.armor != None:
            self.armor.degrade()

        return damageDealt

player = Player() # creates the one and only instance of player

class Enemy(Creature):
# subclasses of Enemy require a method named attack()
    def __init__(self, name, health, awareness, stealth):
        super().__init__(name, health)
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
        super().__init__(name, health, 50, 50)

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
    
    def __init__(self, target):
        self.target = target

    def update(self):
    # called every turn
        pass

    def reverse(self):
    # called when effect is removed
        pass

class Bleeding(Effect):
# does 1 damage per turn
    name = "bleeding"
    natural = True
    level = 0
    
    def __init__(self, target):
        self.target = target

    def update(self):
        # lowers health by 1 every turn
        self.target.health -= 1

class Regeneration(Effect):
# heals 1 hp per turn
    name = "regeneration"
    
    def __init__(self, target):
        self.target = target

    def update(self):
        self.target.heal(1)

class WellFed(Effect):
# heals 2 health per turn
    name = "well fed"
    
    def __init__(self, target):
        self.target = target

    def update(self):
        self.target.heal(2)
        
class Dazed(Effect):
# lowers DEX
    name = "dazed"
    natural = True
    level = 1
    
    def __init__(self, target):
        self.target = target

        self.target.update_dexterity(-1)

    def reverse(self):
        self.target.update_dexterity(1)

class Surprised(Effect):
# lowers DEX and AC
    name = "surprised"

    def __init__(self, target):
        self.target = target

        self.target.update_dexterity(-2)
        self.target.armorClass -= 1

    def reverse(self):
        self.target.update_dexterity(2)
        self.target.armorClass += 1

class Decay(Effect):
# lowers CON, gets stronger over time
    name = "decay"

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

class BrokenBones(Effect):
# lowers DEX, STR, permanent
# instantly kills skeletons
    name = "broken bones"
    natural = True
    level = 3
    permanent = True

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
    
class Draugr(Enemy):
# a rare enemy that can appear in earlier floors
# a tankier enemy who can inflict bleeding
    def __init__(self):
        super().__init__("draugr", 18, 2, 3)
        self.resistance = 2
        self.armorClass = 1

    def attack(self, enemies):
        message = "the DRAUGR hits you with their axe for _ damage"
        if randint(1, 4) == 1:
            player.affect(Bleeding, 5)
            player.hurt(3, self.strength, message + ", leaving you BLEEDING!")
        else:
            player.hurt(5, self.strength, message + "!")

class Ghoul(Enemy):
# an uncommon, stealthier enemy that appears in the prison
# can dodge attacks and inflicts decay
    def __init__(self):
        super().__init__("ghoul", 16, 4, 2)
        self.dodge = 10
        
        self.warning = "you smell a foul stench"

    def attack(self, enemies):
        if randint(1, 3) == 1:
            print("the GHOUL curses you with DECAY, lowering your CON over time")

            player.affect(Decay, 6)
        else:
            player.hurt(4, self.strength, "the GHOUL attacks you for _ damage!")

class Skeleton(Enemy):
# a common enemy type throughout the dungeon
# is immune to most natural effects and often staggers instead of attacking
    def __init__(self):
        super().__init__("skeleton", 16, 1, 0)
        self.immuneTo = [Bleeding]
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
        armorPiercing = 0
        if self.weapon == "spear" and randint(1, 3) < 3:
            armorPiercing = 1

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
            player.hurt(self.damage, self.strength, message + ", leaving you BLEEDING!", armorPiercing)
        elif inflictsDazed:
            player.hurt(self.damage, self.strength, message + ", leaving you DAZED!", armorPiercing)
        else:
            player.hurt(self.damage, self.strength, message + "!", armorPiercing)

class ArmoredSkeleton(Skeleton):
# has some AC and staggers more, always has a mace
    def __init__(self):
        super().__init__()
        self.staggerChance = 3
        self.armorClass = 1
        
        self.weapon = "mace"
        self.name = "armored skeleton"
        self.warning = "you hear the clanking of bones and metal"

class SkeletonGuard(Skeleton):
# has more AC, staggers less, always has a spear, very aware
    def __init__(self):
        super().__init__()
        self.staggerChance = 1
        self.armorClass = 2
        self.awareness = 4
        self.stealth = -1

        self.weapon = "spear"
        self.name = "skeleton guard"
        self.warning = "you hear the clanking of bones and metal"

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
    "prison":[(Skeleton, 7), (ArmoredSkeleton, 9), (Draugr, 10), (Ghoul, 12), (SkeletonGuard, 14)]
}

# numbers higher than 12 will only spawn with increased danger
# the actual chance to spawn is (current) number - previous number) in 12
# same as item randomness except the highest number is 12
# numbers higher than 12 only show up when danger is increased
# lower numbers are less likely when danger is increased
            
def gen_enemy(area, danger):
    enemyNum = randint(1, 12) + danger
    # enemyNum is less than highest spawn chance
    if enemyNum > enemyPool[area][-1][1]:
        enemyNum = 12

    for enemy in enemyPool[area]:
        if enemyNum <= enemy[1]:
            return enemy[0]()