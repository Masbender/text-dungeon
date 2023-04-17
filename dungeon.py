from random import randint, choice
from extra import clear_console, gather_input, slowprint, separator
import entities
import items
import color

c = color

player = entities.player


def unlock(key):
    keyIndex = -1
    for item in player.inventory:
        if type(item) == key:
            keyIndex = player.inventory.index(item)

    if keyIndex == -1:
        slowprint(f"You do not have a {key.name}.")
        return False
    else:
        options = ["cancel", "use key"]

        playerInput = bool(gather_input(f"Do you use a {key.name}?", options))

        if playerInput:
            player.inventory.pop(keyIndex)
            return True

        return False

def sort_inventory():
    weapons = []
    wands = []
    healing = []
    consumables = []
    apparel = []
    scrolls = []
    misc = []

    for item in player.inventory:
        if issubclass(type(item), items.Weapon):
            weapons.append(item)
        elif issubclass(type(item), items.Wand):
            wands.append(item)
        elif issubclass(type(item), items.Medicine):
            healing.append(item)
        elif issubclass(type(item), items.Scroll):
            scrolls.append(item)
        elif issubclass(type(item), items.Armor) or issubclass(type(item), items.Ring):
            apparel.append(item)
        elif issubclass(type(item), items.Consumable):
            consumables.append(item)
        else:
            misc.append(item)

    player.inventory = weapons + wands + healing + consumables + apparel + scrolls + misc

def item_list():
# returns a list of item names
    itemList = []
    for item in player.inventory:
        itemList.append(item.get_name())

    return itemList

def update_effects(creature, enemies = None):
# iterates through every effect
    effectDurations = []
    
    for i in range(len(creature.effects)):
        creature.effects[i].update(enemies)
        creature.effects[i].duration -= 1

        effectDurations.append(creature.effects[i].duration)

    # deletes expired effects
    while 0 in effectDurations:
        effectIndex = effectDurations.index(0)
        effectDurations.pop(effectIndex)
        creature.effects[effectIndex].reverse()
        creature.effects.pop(effectIndex)

def print_effects(creature):
    effects = []
    for i in range(len(creature.effects)):
        effect = creature.effects[i]
        if effect.isPermanent:
            effects.append(f"{effect.color(effect.name)}")
        else:
            effects.append(f"{effect.color(effect.name)} - {creature.effects[i].duration} turns")

    if len(effects) > 0:
        print(f"[{' | '.join(effects)}]")

def print_player_info():
# prints player health, effects, stats, and equipment
    separator()
    print(f"YOU: [{c.health_status(player.health, player.maxHealth)} ♥] [{player.armorClass} AC]")
    
    print_effects(player)

    statsDisplay = ""

    statsDisplay += f"[{c.compare(player.strength, player.baseSTR)} STR] "
    statsDisplay += f"[{c.compare(player.constitution, player.baseCON)} CON] "
    statsDisplay += f"[{c.compare(player.dexterity, player.baseDEX)} DEX] "
    statsDisplay += f"[{c.compare(player.perception, player.basePER)} PER] "
    statsDisplay += f"[{c.compare(player.intelligence, player.baseINT)} INT] "
    
    print(statsDisplay)
    separator()
                        
class Battle:
    def __init__(self, enemies, isSurprise = False):
        self.battleOver = False
        self.enemies = enemies
        self.isSurpriseAttack = isSurprise

    def start_battle(self):
        clear_console()
        if self.enemies[0].battleMessages == []:
            slowprint(c.blue(f"You encounter {self.enemies[0].name}!"))
        else:
            slowprint(c.blue(choice(self.enemies[0].battleMessages)))

        if self.enemies[0].isSpecial:
            slowprint(c.red(f"There is no escape from this fight."))
        separator()
        
        while not self.battleOver:
            if player.stunned:
                player.stunned = False
                print(c.red("You fail to notice their presence..."))
            else:
                self.player_turn()
            
            canRun = True
            allStunned = True
            for enemy in self.enemies:
                if not enemy.stunned: # tracks if any enemies are not stunned
                    allStunned = False
                if enemy.isSpecial:
                    canRun = False
            
                if enemy.health > 0:
                    self.enemy_turn(enemy)

            # checks if enemies should die
            removedEnemies = []
            for enemy in self.enemies:
                if enemy.health <= 0:
                    slowprint(f"{enemy.name} drops {enemy.gold} gold.")
                    player.gold += enemy.gold
                    removedEnemies.append(enemy)

            for enemy in removedEnemies:
                self.enemies.remove(enemy)

            if self.enemies == [] or player.health <= 0:
                self.battleOver = True
                break

            # handles escaping, cannot escape on the first turn of a sneak attack
            if allStunned and canRun and not self.isSurpriseAttack:
                self.run_prompt()

            self.isSurpriseAttack = False
            
        # detects if player won or lost
        if player.health > 0:
            return True
        else:
            return False

    def print_battle(self):
        for creature in self.enemies:
            print()
            print((c.red("(!) ") * creature.isSpecial) + f"{c.red(creature.name)} : [{c.health_status(creature.health, creature.maxHealth)} ♥] [{creature.armorClass} AC]")
            
            print_effects(creature)

        print_player_info()
    
    def enemy_turn(self, enemy):
        enemy.do_turn(self.enemies)
        update_effects(enemy, self.enemies)

    def player_turn(self):
        turnOver = False
        while not turnOver:
            self.print_battle()

            itemUsed = gather_input("What do you use?", item_list())

            turnOver = player.inventory[itemUsed].attack(self.enemies)

        update_effects(player, self.enemies)

    def run_prompt(self): # if all enemies are stunned, the player can choose to run
        playerInput = gather_input("All enemies are stunned, you have an opportunity to escape!", ["run", "fight"], False, False)

        if playerInput == "run":
            self.battleOver = True

            # heals the enemies a bit to make running less powerful
            for enemy in self.enemies:
                enemy.heal(5)

class Floor:
    def __init__(self, layout, posY, posX, entryMessage = ""): # posY and posX are player's position
        self.layout = layout
        self.posY = posY
        self.posX = posX
        self.entryMessage = entryMessage

        # forms the map
        self.map = []
        for i in range(len(self.layout)):
            self.map.append(['?'] * len(self.layout))

    # checks if an x or y coordinate is too big or small
    def check_pos(self, position):
        if position >= len(self.layout) or position < 0:
            return False
        else:
            return True

    # prints map
    def print_map(self):
        # prepares a list with the proper characters
        lines = []
        for i in range(len(self.map)):
            lines.append([])
            for I in range(len(self.map)):
                # player is represented as 'o'
                if i == self.posY and I == self.posX:
                    lines[i].append(c.blue('o'))
                # unknown is represented as '?'
                elif self.map[i][I] == '?':
                    lines[i].append('?')
                # walls are represented as '■'
                elif type(self.map[i][I]) == Wall and self.map[i][I].blocked:
                    if len(self.map[i][I].loot) > 0:
                        # walls with hidden loot are yellow
                        lines[i].append(c.yellow('■'))
                    else:
                        lines[i].append('■')
                # stairs are represented as ↓ or ↑
                elif "descend" in self.map[i][I].specialAction:
                    lines[i].append('↓')
                # shops and chests are represented as yellow !
                elif self.map[i][I].specialAction in ["shop", "unlock chest", "refine gold chunk"]:
                    lines[i].append(c.yellow('!'))
                # enemies are represented as red !
                elif self.map[i][I].check_detection():
                    lines[i].append(c.red('!'))
                # locked rooms appear as locks
                elif type(self.map[i][I]) == LockedRoom and self.map[i][I].blocked:
                    lines[i].append('x')
                # rooms are represented as ' '
                else:
                    lines[i].append(' ')
        # prints the map
        separator()
        for line in lines:
            print(" ".join(line))

    def update_room(self, y, x):
        self.map[y][x] = self.layout[y][x]
    # adds a room to the map
        
    def update_map(self):
    # adds nearby rooms to the map
    # warns player of nearby enemies
        y = self.posY
        x = self.posX

        messages = []
        nearbyEnemies = []
        
        if self.check_pos(y + 1):
            self.update_room(y + 1, x)
            nearbyEnemies.extend(self.layout[y + 1][x].threats)
            
        if self.check_pos(y - 1):
            self.update_room(y - 1, x)
            nearbyEnemies.extend(self.layout[y - 1][x].threats)
            
        if self.check_pos(x + 1):
            self.update_room(y, x + 1)
            nearbyEnemies.extend(self.layout[y][x + 1].threats)
            
        if self.check_pos(x - 1):
            self.update_room(y, x - 1)
            nearbyEnemies.extend(self.layout[y][x - 1].threats)
        
        for enemy in nearbyEnemies:
            if player.awareness >= enemy.stealth:
                if not enemy.warning in messages:
                    messages.append(enemy.warning)
                    slowprint(enemy.warning)

    def move_player(self, direction):
    # moves the player
    # directions : 0 = up/north, 1 = right/east, 2 = down/south, 3 = left/west
        newY = self.posY + [-1, 0, 1, 0][direction]
        newX = self.posX + [0, 1, 0, -1][direction]

        # checks if new position is too big or small
        if not (self.check_pos(newY) and self.check_pos(newX)):
            slowprint("The wall here is protected by magic and is indestructible.")
            return False

        # checks if new tile is a wall
        if self.layout[newY][newX].blocked:
            if self.layout[newY][newX].unblock():
                self.layout[newY][newX].blocked = False
            else:
                return False
        # updates players position
        self.posY = newY
        self.posX = newX
        return True

    def get_room(self):
    # retunrs the room that the player is in
        return self.layout[self.posY][self.posX]

    def get_options(self):
    # returns a list of options for the player to choose
        room = self.get_room()

        options = ["↑ North", "→ East", "↓ South", "← West", "wait", "view stats"]

        if player.inventory != []:
            options.append(f"inventory [{len(player.inventory)}/{player.inventorySize}]")
            
        if room.loot != []:
            options.append(c.yellow("take item"))
            # prints items
            if len(room.loot) == 1:
                print(f"There is a {c.yellow(room.loot[0].get_name())} here.")
            else:
                # gets a list of item names
                names = []
                for item in room.loot:
                    names.append(c.yellow(item.get_name()))
                    
                print(f"There is a {', '.join(names[0:-1])}, and a {names[-1]} here.")            

        # presents options to player and gathers input
        if room.specialAction != "":
            options.append(c.yellow(room.specialAction))

        if room.threats != []:
            options.append(c.red("surprise attack"))
            
            for enemy in room.threats:
                print(choice(enemy.stealthMessages))
    
        return options

    def action_move(self, direction):
    # called when player decides to move
        # - INPUT -
            """ (Unindent if change is reverted)
            options = ["cancel", "↑", "→", "↓", "←"]

            self.print_map()
            separator()
            playerInput = gather_input("What direction do you move?", options, True) - 1

            if playerInput > -1: # -1 is cancel
            """
            playerInput = ["↑", "→", "↓", "←"].index(direction) # delete if change is reverted

            # - MOVE -
            self.move_player(playerInput)
            
            self.update_map()
            update_effects(player)
    
            # - COMBAT -
            room = self.get_room()
            if room.threats != []:
                isNoticed = False
                isSurprised = True
                for enemy in room.threats: # checks if player is noticed
                    if enemy.awareness >= player.stealth:
                        isNoticed = True
                    if enemy.stealth <= player.awareness:
                        isSurprised = False
                        
                if isNoticed:
                    if isSurprised:
                        player.stunned = True
                        player.affect(entities.Surprised(), 1)
                    battle = Battle(room.threats)
                    battle.start_battle()

    def action_wait(self):
    # called when player chooses to wait
        self.update_map()
        update_effects(player)
        slowprint(choice(["You wait.", "You take a moment to enjoy your surroundings.", "You ponder existence.", "You fall asleep for an unknown amount of time."]))
        
    def action_view_stats(self):
    # called when player decides to view stats
        message = ""
        # strength
        message += f"{c.compare(player.strength, player.baseSTR)} STR : "
        message += f"you do {player.strength * 0.75} extra damage with weapons "
        message += f"and you can carry up to {c.compare(player.inventorySize, player.strength + 10)} items"

        # constitution
        message += f"\n\n{c.compare(player.constitution, player.baseCON)} CON : "
        message += f"your maximum health is {c.compare(player.maxHealth, 20 + player.constitution * 2)}, "
        message += f"and your resistance level is {c.compare(player.resistance, player.constitution)}\n\t"

        minor = [] # minor resistances
        major = [] # major resistances

        for effect in [entities.Poisoned, entities.Bleeding, entities.Burned, entities.Dazed, entities.OnFire, entities.BrokenBones]:
            if effect.level < player.resistance:
                if player.resistance - effect.level > 3:
                    major.append(effect.name)
                else:
                    minor.append(effect.name)

        if len(minor) > 0:
            message += f"you have minor resistance to ({', '.join(minor)}) "
        else:
            message += "you have no minor resistances "

        if len(major) > 0:
            message += f"and major resistance to ({', '.join(major)})"
        else:
            message += "and no major resistances"
        
        message += f"\n\n{c.compare(player.dexterity, player.baseDEX)} DEX : "
        message += f"you have a {c.compare(player.dodgeChance, player.dexterity * 5)}% chance to dodge attacks, and your stealth is level {c.compare(player.stealth, player.dexterity)}"
        
        message += f"\n\n{c.compare(player.perception, player.basePER)} PER : "
        message += f"your awareness is level {c.compare(player.awareness, player.perception)}, and you have a {c.compare(player.critChance, player.perception * 5)}% chance to deal double damage"
        
        message += f"\n\n{c.compare(player.intelligence, player.baseINT)} INT : "
        message += f"your gear degrades {100 - player.intelligence * 10}% of the time"

        print(message)

        print(f"\nYou have {player.armorClass} AC, granting {player.armorClass / 2} damage resistance.")

        # prints effects
        for i in range(len(player.effects)):
            effect = player.effects[i]

            title = effect.color(effect.name.upper())
            if not effect.isPermanent:
                title += f" ({player.effects[i].duration} turns remaining)"
            print(title)

            effect.inspect()

    def action_take_item(self):
    # called when player takes an item
        room = self.get_room()
        
        if len(player.inventory) >= player.inventorySize: # checks if inventory has space
            print(f"You are carrying too much, you can only have {player.inventorySize} items.")
            return

        # decides options
        options = ["cancel"]
        for item in room.loot:
            options.append(item.get_name())

        # gathers input if more than one item
        chosenItem = 0
        if len(room.loot) > 1:
            chosenItem = gather_input("What do you pickup?", options, True) - 1

        if chosenItem > -1: # -1 is cancel
            # moves item to inventory
            room.loot[chosenItem].pickup()
            player.inventory.append(room.loot.pop(chosenItem))
            slowprint(f"You take the {options[chosenItem + 1]}.")
    
            sort_inventory()

    def action_inventory(self):
        while True:
            options = ["back"] + item_list()
            
            if player.gold > 0:
                print(f"You have {c.yellow(str(player.gold))} gold.\n")
            playerInput = gather_input("Select an item to inspect or use:", options, True) - 1

            # exits the loop if player selects "back"
            if playerInput == -1:
                break
            
            # figures out what item was selected and prepares options
            options = ["back"]
            chosenItem = player.inventory[playerInput]

            if chosenItem == player.ring or chosenItem == player.armor:
                options.append("unequip")
                
            else:
                if chosenItem.usePrompt != None:
                    options.append(chosenItem.usePrompt)

                if chosenItem.enchantment >= 0:
                    options.append("drop")

            # prints info about the item
            print(chosenItem.get_name())
            chosenItem.inspect()
            if chosenItem.enchantment > 0:
                print(f"This item is {c.green('blessed')}.")
            elif chosenItem.enchantment < 0:
                print(f"This item is {c.red('cursed')}, and cannot be dropped.")

            # asks for input
            playerInput = gather_input("\nWhat do you do with " + chosenItem.get_name() + "?", options, True, False)

            if playerInput == chosenItem.usePrompt:
                chosenItem.consume(self)

            elif playerInput == "drop":
                chosenItem.discard()
                self.get_room().loot.append(chosenItem)
                player.inventory.remove(chosenItem)

            elif playerInput == "unequip":
                chosenItem.unequip()

                if chosenItem == player.armor:
                    player.armor = None
                else:
                    player.ring = None

                print("You unequip the " + chosenItem.get_name() + ".")

    def action_unlock_chest(self):
    # called when player uses an item
        room = self.get_room()
        
        room.unlock_chest()

    def action_surprise(self):
        room = self.get_room()
        
        if room.areEnemiesAware:
            slowprint("You have already fought these enemies, they will not be surprised.")
            playerInput = gather_input("Are you sure you want to surprise attack?", ["cancel", "surprise attack"], True)

            if playerInput == 0:
                return

        else:
            for enemy in room.threats: # makes sure all enemies are surprised and stunned
                enemy.affect(entities.Surprised(), 1)
                enemy.stunned = True

        battle = Battle(room.threats, True)
        battle.start_battle()

        room.areEnemiesAware = True
        
    def enter_floor(self):
    # starts when player enters the floor, ends when they exit
    # returns -1 or 1, representing the change in floor
        clear_console()

        if self.entryMessage != "":
            print(self.entryMessage)
        self.update_map()
        
        while player.health > 0:
            room = self.get_room()

            # ===== PRINTS INFORMATION =====
            self.print_map()
        
            if room.description != "":
                slowprint(room.description)
            options = self.get_options()
            
            print_player_info()
            playerInput = gather_input("What do you do?", options, False, False)

            actions = {
                #"move":self.action_move, 
                "wait":self.action_wait,
                "view stats":self.action_view_stats, f"inventory [{len(player.inventory)}/{player.inventorySize}]":self.action_inventory,
                c.yellow("take item"):self.action_take_item,
                c.yellow("unlock chest"):self.action_unlock_chest, c.red("surprise attack"):self.action_surprise
            }
            
            if playerInput in actions.keys(): # some actions aren't in the dictionary
                actions[playerInput]()
            
            elif "move " in playerInput and len(playerInput) == 6:
                self.action_move(playerInput[5])

            elif playerInput[0] in ["↑", "→", "↓", "←"]:
                self.action_move(playerInput[0])
                
            elif playerInput == "debug : reveal map":
                self.map = self.layout

            elif "descend" in playerInput:
                room.interact() # if it leads somewhere else it is in .interact()
                break

            else:
                room.interact()

class Room:
    blocked = False # determines if it counts as a wall or not
    description = ""
    specialAction = ""

    areEnemiesAware = False # once a combat is over, this is set to True, these enemies cannot be surprised if it's True
    
    def __init__(self, loot = [], threats = [], description = ""):
        self.loot = loot
        self.threats = threats
        if description != "":
            self.description = description

    def unblock(self): # called if the room needs a bomb or key to unlock
        return True
    
    def check_detection(self): # checks if player notices enemies here
        detected = False
        for enemy in self.threats:
            if player.awareness >= enemy.stealth:
                detected = True

        return detected

    def interact(self): # called when player uses special action
        pass

class Refinery(Room):
# used to refine gold chunks
    description = "There is an old, Dwarven refinery here. It looks rather simple, and you think that you could operate it."
    specialAction = "refine gold chunk"

    def __init__(self):
        self.loot = []
        self.threats = []

    def interact(self):
        goldIndex = -1
        for i in range(len(player.inventory)):
            if type(player.inventory[i]) == items.GoldChunk:
                goldIndex = i
                break

        if goldIndex == -1:
            print(c.red("You have nothing to refine!"))
        else:
            player.inventory.pop(goldIndex)
            gold = randint(20, 50)
            player.gold += gold
            print(f"The refinery produces {c.yellow(gold)} gold from your gold chunk.")
            
class Chest(Room):
    blocked = False
    description = "There is a " + c.yellow("chest") + " here with a " + c.yellow("gold lock") + "."
    specialAction = "unlock chest"

    def __init__(self, depth):
        self.loot = []
        self.threats = []
        self.hiddenLoot = [items.gen_loot(depth)]

    def unlock_chest(self):
        if unlock(items.GoldKey):
            self.loot.extend(self.hiddenLoot)

            slowprint("You unlock the chest.")
            self.description = ""
            self.specialAction = ""
            return True

        else:
            return False

class Wall(Room):
    blocked = True
    description = "You are in a tunnel, there is rubble everywhere."
    specialAction = ""

    def __init__(self):
        self.loot = []
        self.threats = []

    def unblock(self): # requires a bomb or pickaxe
        slowprint("There is a wall in the way.")
        
        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(item.get_name())
        
        itemUsed = gather_input("How do you destroy it?", options, True)

        # checks if item works then uses it
        tunnelDug = False
        if itemUsed > 0: # 0 is cancel
            itemUsed -= 1 # reverts back to proper index
            tunnelDug = player.inventory[itemUsed].dig()

        return tunnelDug

class LockedRoom(Room):
    blocked = True
    description = ""
    specialAction = ""

    def __init__(self, depth):
        self.loot = []
        self.threats = []

        self.loot = [items.gen_gear(depth + 1), choice([items.gen_item(depth + 2), items.ScrollRepair()])]

    def unblock(self): # requires a certain key
        print(f"This room is locked and requires a iron key.")

        if unlock(items.IronKey):
            print("The gate opens.")
            return True
        else:
            return False

class Chasm(Room):
    description = "There is a large chasm here, it would be risky to descend it without proper equipment."
    specialAction = "descend chasm"

    def interact(self):
        g = Generator()
        g.initialize_floor("mines", 5, 7)
        
        hasRope = False
        for item in player.inventory:
            if type(item) == items.Rope:
                player.inventory.remove(item)
                hasRope = True
                break

        if hasRope:
            g.entryMessage = c.blue("Using your rope, you manage to safely descend the chasm.\n")
        else:
            g.entryMessage = c.red("While trying to climb down the chasm, you slip and break your bones.\n")
            player.affect(entities.BrokenBones())
        
        g.generate_mines()
        floor = g.finalize_floor()
        floor.enter_floor()

class Stairs(Room):
    blocked = False
    description = "There are " + c.yellow("stairs") + " here that lead down."
    specialAction = "descend stairs"

    def __init__(self):
        self.loot = []
        self.threats = []

class Shop(Room):
    blocked = False
    description = "You stumble upon the " + c.yellow("SHOPKEEPER") + ", an ancient stone golem."
    specialAction = "shop"

    def __init__(self, depth):
        self.loot = []
        self.threats = []

        self.stock = []

        # has an enchanted gear of a next-area material
        self.stock.append(items.gen_gear(depth + 3))
        if self.stock[0].enchantable:
            self.stock[0].enchantment = randint(1, 2)
        
        # has an item or gear that can't be cursed
        self.stock.append(items.gen_gear(depth))
        if self.stock[1].enchantment < 0:
            self.stock[1].enchantment = 0

        # has an item from the next area
        self.stock.append(items.gen_item(depth + 4))

        # has a healing item
        self.stock.append(choice([items.Bandage, items.Rations])())
        
        if depth == 1:
            self.stock.append(items.Rope())
        elif depth == 4:
            self.stock.append(items.StorageBook())
        
        # items are more expensive in later floors
        for item in self.stock:
            item.value = int(item.value * (1.3 ** (depth // 3)))

    def interact(self):
        while True:
            options = ["cancel"]

            for item in self.stock:
                options.append(item.get_name() + f", costs {c.yellow(item.get_price())} gold")

            print(c.blue("The golem shows you it's wares."))
            playerInput = gather_input(f"You have {c.yellow(player.gold)} gold.", options, True) - 1

            if playerInput == -1: # cancel
                break
            else:
                purchase = self.stock[playerInput]

                if player.gold < purchase.get_price():
                    print(c.red(f"You need {purchase.get_price() - player.gold} more gold to purchase {purchase.get_name()}!"))

                elif len(player.inventory) == player.inventorySize:
                    print(c.red(f"Your inventory is full!"))
                    break

                else:
                    self.stock.remove(purchase)
                    player.gold -= purchase.get_price()
                    player.inventory.append(purchase)
                    sort_inventory()
                    print(f"You purchase {purchase.get_name()} for {purchase.get_price()} gold.")
                    break

def gen_room(area, depth, type):
    loot = []
    threats = []
    room = Room()

    # standard room
    if type == 1:
        if area == "prison":
            if randint(1, 3) == 1:
                room.description = "You are in an empty prison cell."

    # special room
    elif type == 2:
        if area == "prison":
            roomDesc = randint(1, 6)
            if roomDesc == 1:
                room.description = "You are in an old storage room."
            elif roomDesc == 2:
                room.description = "You are in what used to be an armory."
            elif roomDesc == 3:
                room.description = "You are in a large, empty room."

    # secret room
    elif type == 3:
        room.description = "This is a secret room."

        if area == "mines":
            loot.append(items.ImmunityBook())
        else:
            loot.append(items.gen_loot(depth))
        
        for i in range(randint(1, 2)):
            loot.append(items.gen_item(depth + 3 - i))

    room.threats = threats
    room.loot = loot
    
    return room
    
class Generator:
# generates floors
    def initialize_floor(self, area, depth, size):
        self.area = area
        self.depth = depth
        self.size = size

        self.modifier = "" 
        if self.size > 4 and randint(0, 1): # can assign a random modifier except on the first floor
            self.modifier = choice(["dangerous", "large", "cursed"])
        self.entryMessage = ""

        # adds these features before finishing generation
        self.addRooms = []
        self.addItems = []
        self.addEnemies = []

        # selects the generation format early, so it can be overriden
        self.generation = choice([self.gen_hall, self.gen_intersection, self.gen_square])

    def generate_floor(self):
        # stores the layout
        self.layoutNums = [] # this is the layout in integers
        self.layoutRooms = [] # layoutNums is converted into rooms
        self.startY = 0
        self.startX = 0

        # stores info for room placement
        self.rooms = []
        self.adjacentWalls = []
        self.hiddenWalls = []
        self.sideRooms = []

        if self.modifier != "":
            self.entryMessage += {
                "flooded":c.blue("The ground is flooded with water."),
                "large":c.blue("Your footsteps echo across the floor."),
                "dangerous":c.red("This floor is unusually crowded, watch your back."),
                "cursed":c.red("A malevolent energy lurks in the items here.")
            }[self.modifier] + "\n"

        # applies "large" modifier
        if self.modifier == "large":
            self.size += 1

        # forms a square in layoutNums
        for i in range(self.size):
            self.layoutNums.append([0] * self.size)

        # mutates rats
        if self.area == "crossroads" and self.depth > 3:
            # checks which mutations can be made
            mutationList = ["toxic", "stronger", "hungrier"]
            for mutation in entities.Rat.mutations:
                mutationList.remove(mutation)
            
            mutation = choice(mutationList)

            entities.Rat.mutations.append(mutation)
            self.entryMessage += c.red({
                "toxic":"The rats have mutated.\n",
                "stronger":"The rats grow stronger.\n",
                "hungrier":"The rats are hungry.\n"
            }[mutation])

        self.generation()

        # generates secret room
        if len(self.hiddenWalls) > 0:
            hiddenSpot = choice(self.hiddenWalls)
            self.layoutNums[hiddenSpot[0]][hiddenSpot[1]] = 3

        # creates layoutRooms based on the numbers in layoutNums
        for y in range(self.size):
            self.layoutRooms.append([])
            for x in range(self.size):
                room = Wall() # 0 = Wall
    
                if self.layoutNums[y][x] > 0:
                    room = gen_room(self.area, self.depth, self.layoutNums[y][x])
                    
                elif self.layoutNums[y][x] == -1:
                    room = Stairs()
                
                self.layoutRooms[y].append(room)

        self.addItems.extend(self.gen_random_items(self.size + randint(1, 2), self.size - randint(1, 2)))
        
        # spawns enemies
        if self.modifier == "dangerous":
            self.addEnemies.extend(entities.gen_enemies(self.area, self.size, self.depth % 3, self.depth % 3))
        elif self.modifier == "flooded":
            self.addEnemies.extend(entities.gen_enemies(self.area, self.size - 2, self.depth % 3, self.depth % 3))
            choice(self.addEnemies).append(entities.SewerRat())
            self.addEnemies.append([entities.SewerRat(), entities.SewerRat()])
        else:
            self.addEnemies.extend(entities.gen_enemies(self.area, self.size - 1, self.depth % 3, self.depth % 3))

    def generate_mines(self):
        self.modifier = ""
        self.generation = self.gen_mine
        self.entryMessage += c.blue("The walls are rough and lined with gold, the air is still and filled with silence. You have entered The Mines.")
        
        self.generate_floor()
        self.layoutRooms[self.size // 2][0] = Refinery()

        self.addEnemies = [[entities.AncientDraugr()]] # only an ancient draugr
        self.addItems = [items.Pickaxe(), items.Bomb()] # no loot
        self.addRooms = [] # no side rooms

        walls = self.hiddenWalls + self.adjacentWalls
        for i in range(10):
            wall = choice(walls)
            walls.remove(wall)
            self.layoutRooms[wall[0]][wall[1]].loot.append(items.GoldChunk())

        walls = self.hiddenWalls + self.adjacentWalls
        for i in range(15):
            wall = choice(walls)
            if len(self.layoutRooms[wall[0]][wall[1]].threats) > 0:
                walls.remove(wall)
            self.layoutRooms[wall[0]][wall[1]].threats.append(entities.Worm())

    def gen_mine(self):
    # generates two intersecting halls in the middle, without generating side rooms
        for i in range(self.size): 
            self.layoutNums[i][self.size // 2] = 1
            self.layoutNums[self.size // 2][i] = 1

        self.layoutNums[self.size - 1][self.size // 2] = -1
        self.startX = self.size // 2
        self.startY = 0
        self.count_rooms()
           
    def gen_hall(self):
    # generates a snake-like hall
        genOver = False
        x, y = 0, 0
    
        self.layoutNums[x][y] = 1
    
        while not genOver:
            chosenDirection = choice(['x', 'y'])
    
            # keeps the directions somewhat even
            if (x - 2) > y:
                chosenDirection = 'y'
            elif (y - 2) > x:
                chosenDirection = 'x'
    
            if chosenDirection == 'x':
                # checks if x is too big
                if (x + 1) < self.size:
                    x += 1
                else:
                    break
    
            elif chosenDirection == 'y':
                # checks if y is too big
                if (y + 1) < self.size:
                    y += 1
                else:
                    break
    
            self.layoutNums[y][x] = 1
    
        # addds stairs down at the end
        self.layoutNums[y][x] = -1
        
        self.count_rooms()
        self.gen_rooms(((self.size * self.size) - len(self.rooms)) // 3)

    def gen_intersection(self):
    # generates two intersecting halls
        offset = 1 # how close to the edge the halls are allowed to be
        if self.size > 5:
            offset = 2

        hallX = randint(offset, self.size - 1 - offset)
        hallY = randint(offset, self.size - 1 - offset)

        self.layoutNums[hallX] = [1] * self.size

        for y in range(self.size):
            self.layoutNums[y][hallY] = 1

        self.startX = randint(0, self.size - 1)
        self.startY = hallX

        self.layoutNums[choice([0, self.size - 1])][hallY] = -1
        
        self.count_rooms()
        self.gen_rooms(((self.size * self.size) - len(self.rooms)) // 3)

    def gen_square(self):
    # generates a ring around that leaves one wall between it and the border
        self.layoutNums[1] = [0] + ([1] * (self.size - 2)) + [0]
        self.layoutNums[self.size - 2] = [0] + ([1] * (self.size - 2)) + [0]

        for y in range(1, self.size - 2):
            self.layoutNums[y][1] = 1
            self.layoutNums[y][self.size - 2] = 1

        self.startX = choice([1, self.size - 2])
        self.startY = choice([1, self.size - 2])

        endX = self.startX
        endY = self.startY

        while endX == self.startX and endY == self.startY:
            endX = choice([1, self.size - 2])
            endY = choice([1, self.size - 2])

        self.layoutNums[endY][endX] = -1
        
        self.count_rooms()
        self.gen_rooms(((self.size * self.size) - len(self.rooms)) // 3)

    def gen_random(self):
    # generates a random layout
        # picks starting position
        x = randint(1, self.size) - 1
        y = randint(1, self.size) - 1

        self.startX = x
        self.startY = y

        self.layoutNums[y][x] = 1

        # generation starts here
        previousDirection = -3

        for i in range(int(self.size * 1.5)):
            direction = randint(0, 3)
            stepSize = randint(2, 3)

            if direction == (previousDirection + 2) % 4:
                direction = (direction + 1) % 4

            for i in range(stepSize):
                if direction == 0 and y > 0:
                    y -= 1
                elif direction == 1 and x < self.size - 1:
                    x += 1
                elif direction == 2 and y < self.size - 1:
                    y += 1
                elif direction == 3 and x > 0:
                    x -= 1

                self.layoutNums[y][x] = 1

        while (x == self.startX and y == self.startY):
            direction = randint(0, 3)
            stepSize = randint(2, 3)

            for i in range(stepSize):
                if direction == 0 and y > 0:
                    y -= 1
                elif direction == 1 and x < self.size - 1:
                    x += 1
                elif direction == 2 and y < self.size - 1:
                    y += 1
                elif direction == 3 and x > 0:
                    x -= 1

                self.layoutNums[y][x] = 1

        self.layoutNums[y][x] = -1
        
        self.count_rooms()
        self.gen_rooms(((self.size * self.size) - len(self.rooms)) // 3)

    def count_rooms(self):
        for y in range(self.size):
            for x in range(self.size):
                if self.layoutNums[y][x] != 0:
                    self.rooms.append([y, x])
                else:
                    # checks for walls adjacent to rooms
                    adjacentToRoom = False
                    for i in [[y - 1, x], [y + 1, x], [y, x - 1], [y, x + 1]]:
                        # if coords are too large it passes
                        if (i[0] < self.size) and (i[1] < self.size) and (i[0] >= 0) and (i[1] >= 0):
                            # checks if viable for being an adjacent room 
                            if self.layoutNums[i[0]][i[1]] != 0:
                                self.adjacentWalls.append([y, x])
                                adjacentToRoom = True
                                break

                    # checks if viable for secret room
                    if not adjacentToRoom:
                        self.hiddenWalls.append([y, x])

    def gen_rooms(self, amount):
        viableLocations = [] + self.adjacentWalls
        for i in range(amount):
            if len(viableLocations) > 0:
                # picks a spot for a room
                location = choice(viableLocations)
                # places room
                self.layoutNums[location[0]][location[1]] = 2
    
                # changes lists accordingly
                self.rooms.append(location)
                self.sideRooms.append(location)
                self.adjacentWalls.remove(location)
                viableLocations.remove(location)

                y = location[0]
                x = location[1]

                # adds nearby exposed walls to adjacentWalls
                for i in [[y - 1, x], [y + 1, x], [y, x - 1], [y, x + 1]]:
                    if (i[0] < self.size) and (i[1] < self.size) and (i[0] >= 0) and (i[1] >= 0):
                        if self.layoutNums[i[0]][i[1]] == 0 and not i in self.adjacentWalls:
                            self.adjacentWalls.append(i)
                            self.hiddenWalls.remove(i)

    def gen_random_items(self, gearAmount, itemAmount):
        spawnedItems = []
        
        # spawns gear
        #chosenGear = []
        lootPools = [items.gen_weapon, items.gen_armor]
        for i in range(gearAmount):
            lootpool = None
            if i < 2: # always generates at least one weapon, armor, and wand
                lootPool = lootPools[i]
            else:
                lootPool = choice(lootPools)
                if lootPool == items.gen_wand:
                    lootPools.remove(items.gen_wand)
            
            randomItem = lootPool(self.depth)

            # can't have more than 2 of the same item per floor
            #while chosenGear.count(type(randomItem)) > 1:
            #randomItem = lootPool(self.depth)

            # cursed modifier has a 1 in 3 chance to degrade every item
            if self.modifier == "cursed" and randomItem.enchantable and randint(1, 3) == 1:
                randomItem.enchantment -= 1

            #chosenGear.append(type(randomItem))
            spawnedItems.append(randomItem)

        # spawns items
        for i in range(itemAmount):
            randomItem = items.gen_item(self.depth)
            spawnedItems.append(randomItem)
        
        return spawnedItems

    def spawn_enemies(self):
        validRooms = self.rooms
        
        for enemy in self.addEnemies:
            # ERROR CATCHER
            if len(validRooms) == 0:
                for i in range(len(self.layoutNums)):
                    print(self.layoutNums[i])
                input("ERROR DETECTED, DISPLAYING MAP (ENTER TO DISMISS)")
            
            coords = choice(validRooms)
            room = self.layoutRooms[coords[0]][coords[1]]

            # spawns enemy
            room.threats.extend(enemy)

            validRooms.remove(coords)

    def spawn_rooms(self):
        for room in self.addRooms:
            # prefers side rooms
            if len(self.sideRooms) > 0:
                chosenSpot = choice(self.sideRooms)
                self.sideRooms.remove(chosenSpot)
                self.rooms.remove(chosenSpot)
                self.layoutRooms[chosenSpot[0]][chosenSpot[1]] = room
            else:
                chosenSpot = choice(self.rooms)
                self.rooms.remove(chosenSpot)
                self.layoutRooms[chosenSpot[0]][chosenSpot[1]] = room
    
    def spawn_items(self):
        validRooms = self.rooms + self.sideRooms # favors side rooms (they are included in rooms)
        
        for item in self.addItems:
            if len(validRooms) == 0:
                validRooms = self.rooms + self.sideRooms # resets valid rooms if there aren't enough

            coords = choice(validRooms)
            room = self.layoutRooms[coords[0]][coords[1]]

            # spawns enemy
            room.loot.append(item)

            validRooms.remove(coords)

    def finalize_floor(self):
        self.spawn_rooms()
        self.spawn_items()
        self.spawn_enemies()

        return Floor(self.layoutRooms, self.startY, self.startX, self.entryMessage)