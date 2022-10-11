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

    
    def hurt(self, damageTaken, message):
    # lowers health but applies armor class and dodge        
        finalDamageTaken = damageTaken + randint(-1, 1) - self.armorClass
        if finalDamageTaken < 0:
            finalDamageTaken = 0

        elif self.dodge > 0:
            if randint(0, 99) < self.dodge:
                finalDamageTaken = 0
                message += " The attack was dodged!"
            
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
        self.message = "you feel uneasy" # printed when player detects enemy

    def do_turn(self, enemies):
        # parameter 'enemies' allows the method to see the whole battlefield
        if self.stunned:
            print(f"{self.name} is stunned and unable to fight")
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