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
    
    def set_stats(self, str, dex, con, int, per):
    # sets all 5 stats at once
        self.updateStrength(str - self.strength)
        self.updateDexterity(dex - self.dexterity)
        self.updateConstitution(con - self.constitution)
        self.updateIntelligence(int - self.intelligence)
        self.updatePerception(int - self.perception)

    
    def hurt(self, damageTaken, message, armorPiercing = 0):
    # lowers health but applies armor class and dodge        
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
                finalDamageTaken = int(finalDamageTaken * 1.5)
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
        super().__init__("you", 30)

        self.inventorySize = 10
        self.inventory = []
        self.ring = None
        self.armor = None

player = Player() # creates the one and only instance of player

class Enemy(Creature):
# subclasses of Enemy require a method named attack()
    def __init__(self, name, health, awareness, stealth):
        super().__init__(name, health)
        self.warning = "you feel uneasy" # printed when player detects enemy
        self.awareness = awareness
        self.stealth = stealth

    def do_turn(self, enemies):
        # parameter 'enemies' allows the method to see the whole battlefield
        if self.stunned:
            print(f"{self.name} is stunned and unable to fight")
            self.stunned = False
        else:
            self.attack(enemies)

class Effect:
    natural = False
    level = 0
    
    def __init__(self, target):
        self.target = target

    def update(self):
    # called every turn
        pass

    def reverse(self):
    # called when effect is removed
        pass

class Bleeding(Effect):
# does 1 damage per turn, lowers AC by 1
    name = "bleeding"
    natural = True
    level = 0
    
    def __init__(self, target):
        self.target = target
        # AC only decreases when applied
        self.target.armorClass -= 1

    def update(self):
        # lowers health by 1 every turn
        self.target.health -= 1

    def reverse(self):
        # restores changes in __init__
        self.target.armorClass += 1

class Regeneration(Effect):
# heals 1 hp per turn
    name = "regeneration"
    
    def __init__(self, target):
        self.target = target

    def update(self):
        self.target.heal(1)

class Dazed(Effect):
# lowers DEX and STR
    name = "dazed"
    natural = True
    level = 1
    
    def __init__(self, target):
        self.target = target

        self.target.dexterity -= 1
        self.target.strength -= 1

    def reverse(self):
        self.target.dexterity += 1
        self.target.strength += 1

class Surprised(Effect):
# lowers DEX and AC
    name = "surprised"

    def __init__(self, target):
        self.target = target

        self.target.dexterity -= 2
        self.target.armorClass -= 1

    def reverse(self):
        self.target.dexterity += 2
        self.target.armorClass += 1

class Draugr(Enemy):
# an uncommon enemy that can appear in earlier floors
# a tankier enemy who can inflict bleeding
    def __init__(self):
        super().__init__("draugr", 20, 2, 1)
        self.resistance = 2
        self.armorClass = 1

    def attack(self, enemies):
        message = "the DRAUGR hits you with their axe for _ damage"
        if randint(1, 4) == 1:
            player.affect(Bleeding, 6)
            player.hurt(3 + self.strength, message + ", leaving you BLEEDING!")
        else:
            player.hurt(4 + self.strength, message + "!")

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
            player.hurt(self.damage, message + ", leaving you BLEEDING!", armorPiercing)
        elif inflictsDazed:
            player.hurt(self.damage, message + ", leaving you DAZED!", armorPiercing)
        else:
            player.hurt(self.damage, message + "!", armorPiercing)

class ArmoredSkeleton(Skeleton):
# has more AC and staggers less, always has a mace
    def __init__(self):
        super().__init__()
        self.staggerChance = 1
        self.armorClass = 2
        
        self.weapon = "mace"
        self.name = "armored skeleton"