from random import randint, choice
from extra import clear_console, gather_input
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
        print(f"You do not have a {key.name}.")
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
    scrolls = []
    apparel = []
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
        else:
            misc.append(item)

    player.inventory = weapons + wands + healing + scrolls + apparel + misc

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
    print(f"You have {c.health_status(player.health, player.maxHealth)} HP, {player.armorClass} AC")
    
    print_effects(player)

    statsDisplay = ""

    statsDisplay += f"{c.compare(player.strength, player.baseSTR)} STR | "
    statsDisplay += f"{c.compare(player.constitution, player.baseCON)} CON | "
    statsDisplay += f"{c.compare(player.dexterity, player.baseDEX)} DEX | "
    statsDisplay += f"{c.compare(player.perception, player.basePER)} PER | "
    statsDisplay += f"{c.compare(player.intelligence, player.baseINT)} INT"
    
    print(statsDisplay)
                
class Battle:
    def __init__(self, enemies, isSurprise = False):
        self.battleOver = False
        self.enemies = enemies
        self.isSurpriseAttack = isSurprise

    def start_battle(self):
        clear_console()

        # prints message
        print(c.desc(choice(self.enemies[0].battleMessages)))

        canRun = True
        if self.enemies[0].isSpecial:
            print(c.warning(f"There is no escape from this fight."))
            canRun = False
        
        while not self.battleOver:
            self.player_turn()

            allStunned = True
            removedEnemies = []
            for enemy in self.enemies:
                if not enemy.stunned: # tracks if any enemies are not stunned
                    allStunned = False
            
                if enemy.health > 0:
                    self.enemy_turn(enemy)
                if enemy.health <= 0:
                    print(f"{enemy.name} drops {enemy.gold} gold.")
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
        print()

        for creature in self.enemies:
            print((c.threat("(!) ") * creature.isSpecial) + f"{c.threat(creature.name)} : {c.health_status(creature.health, creature.maxHealth)} HP, {creature.armorClass} AC")
            
            print_effects(creature)

            print()

        print_player_info()
        
        print()
    
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
        playerInput = gather_input("All enemies are stunned, you have an opportunity to escape!", ["run", "fight"], False)

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

    def check_pos(self, position):
    # checks if an x or y coordinate is too big or small
        if position >= len(self.layout) or position < 0:
            return False
        else:
            return True

    def print_map(self):
        # prepares a list with the proper characters
        lines = []
        for i in range(len(self.map)):
            lines.append([])
            for I in range(len(self.map)):
                # player is represented as 'o'
                if i == self.posY and I == self.posX:
                    lines[i].append(c.player('o'))
                # unknown is represented as '?'
                elif self.map[i][I] == '?':
                    lines[i].append('?')
                # walls are represented as ' '
                elif type(self.map[i][I]) == Wall and self.map[i][I].blocked:
                    lines[i].append('■')
                # stairs are represented as ↓ or ↑
                elif self.map[i][I].specialAction == "descend stairs":
                    lines[i].append('↓')
                # shops and chests are represented as yellow !
                elif self.map[i][I].specialAction == "shop" or self.map[i][I].specialAction == "unlock chest":
                    lines[i].append(c.special('!'))
                # enemies are represented as red !
                elif self.map[i][I].check_detection():
                    lines[i].append(c.threat('!'))
                # locked rooms appear as locks
                elif type(self.map[i][I]) == LockedRoom and self.map[i][I].blocked:
                    lines[i].append('x')
                # rooms are represented as '+'
                else:
                    lines[i].append(' ')

        # prints the map
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
                    print(enemy.warning)

    def move_player(self, direction):
    # moves the player
    # directions : 0 = up/north, 1 = right/east, 2 = down/south, 3 = left/west
        newY = self.posY + [-1, 0, 1, 0][direction]
        newX = self.posX + [0, 1, 0, -1][direction]

        # checks if new position is too big or small
        if not (self.check_pos(newY) and self.check_pos(newX)):
            print("The wall here is protected by magic and is indestructible.")
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

        options = ["move", "wait", "view stats"]

        if player.inventory != []:
            options.append("inventory")
            
        if room.loot != []:
            options.append(c.loot("take item"))
            # prints items
            if len(room.loot) == 1:
                print(f"\nThere is a {c.loot(room.loot[0].get_name())} here.")
            else:
                # gets a list of item names
                names = []
                for item in room.loot:
                    names.append(c.loot(item.get_name()))
                    
                print(f"\nThere is a {', '.join(names[0:-1])}, and a {names[-1]} here.")

        # presents options to player and gathers input
        if room.specialAction != "":
            options.append(c.special(room.specialAction))

        if room.threats != []:
            options.append(c.threat("surprise attack"))
            
            print()
            for enemy in room.threats:
                print(c.desc(choice(enemy.stealthMessages)))
    
        return options

    def action_move(self):
    # called when player decides to move
        # - INPUT -
        options = ["cancel", "↑", "→", "↓", "←"]

        self.print_map()
        playerInput = gather_input("\nWhat direction do you move?", options) - 1

        if playerInput > -1: # -1 is cancel
            # - MOVE -
            self.move_player(playerInput)
            
            self.update_map()
            update_effects(player)
    
            # - COMBAT -
            room = self.get_room()
            if room.threats != []:
                isNoticed = False
                for enemy in room.threats: # checks if player is noticed
                    if enemy.awareness >= player.stealth:
                        isNoticed = True
                        
                if isNoticed:
                    battle = Battle(room.threats)
                    battle.start_battle()

    def action_wait(self):
    # called when player chooses to wait
        self.update_map()
        update_effects(player)
        print(choice(["You wait.", "You take a moment to enjoy your surroundings.", "You ponder existence.", "You fall asleep for an unknown amount of time."]))
        
    def action_view_stats(self):
    # called when player decides to view stats
        print(f"resistance : {player.resistance} | decreases the duration of poisons and injuries")
        print(f"dodge : {player.dodgeChance}% | chance to avoid attacks")
        print(f"stealth : {player.stealth} | your ability to be unnoticed")
        print(f"awareness : {player.awareness} | detects enemies on the map")
        print(f"appraisal : {player.appraisal} gold | helps you detect fair prices")
        print()
        
        if player.gold > 0:
            print(f"You have {c.highlight(str(player.gold))} gold.\n")

        # prints effects
        for i in range(len(player.effects)):
            effect = player.effects[i]

            title = effect.color(effect.name.upper())
            if not effect.isPermanent:
                title += f" ({player.effects[i].duration} turns remaining)"
            print(title)

            effect.inspect()
            print()

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
            chosenItem = gather_input("What do you pickup?", options) - 1

        if chosenItem > -1: # -1 is cancel
            # moves item to inventory
            room.loot[chosenItem].pickup()
            player.inventory.append(room.loot.pop(chosenItem))
            print(f"You take the {options[chosenItem + 1]}.")
            print()
            #player.inventory[-1].inspect()
            print()
    
            sort_inventory()

    def action_inventory(self):
        while True:
            options = ["back"] + item_list()
            
            playerInput = gather_input("\nSelect an item:", options) - 1

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
                print(f"This item is {c.blessed('blessed')}.")
            elif chosenItem.enchantment < 0:
                print(f"This item is {c.cursed('cursed')}, and cannot be dropped.")
            print()

            # asks for input
            playerInput = gather_input("What do you do with " + chosenItem.get_name() + "?", options, False)

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
        
    def action_shop(self):
    # called when the player talks to the shopkeeper
        room = self.get_room()

        print("The golem doesn't even look alive, but you approach it anyways.\n")

        print("The golem shows you it's wares:")
        options = ["cancel"]
        # displays items and forms options
        for item in room.stock:
            options.append("buy " + item.get_name())
            print(f"{item.get_name()}, costs {item.get_price(True, True)} gold") # item.get_price(buyPrice?, returnString?)

        print(f"\nYou have {c.highlight(str(player.gold))} gold.")

        playerInput = gather_input(f"What would you like to buy?", options) - 1

        if playerInput > -1:
            golemsDeal = room.stock[playerInput]
            golemsPrice = golemsDeal.get_price(True, False)

            playersDeal = []
            playersPrice = 0

            while True:
                print(f"{golemsDeal.get_name()} costs {c.deal_bad(golemsDeal.get_price(True, True))} gold.\n")
                
                if len(playersDeal) > 0:
                    print(f"Your deal (worth {c.deal_good(str(playersPrice))} gold):")
                    for item in playersDeal:
                        print(f"{item.get_name()} is worth {item.get_price(False, True)} gold,")
                    print()
                
                if playersPrice < golemsPrice:
                    print(f"This deal will cost you {c.deal_bad(str(golemsPrice - playersPrice))} gold.")
                else:
                    print(c.deal_good("This deal will not cost you any gold."))

                options = ["cancel", "accept deal", "undo"]

                for item in player.inventory:
                    options.append(f"{item.get_name()}, worth {item.get_price(False, False)} gold")

                playerInput = gather_input(f"Do you add any items to the deal? (You have {c.highlight(str(player.gold))} gold)", options) - 3

                if playerInput == -3:
                    for item in playersDeal:
                        item.pickup()
                        player.inventory.append(item)
                    sort_inventory()
                    break

                elif playerInput == -2:
                    if playersPrice + player.gold < golemsPrice:
                        print(c.warning(choice(["\"YOU DARE TRY TO SCAM ME?\"", "\"DO YOU THINK I'M A FOOL?\"", "\"YOU CLEARLY CAN'T AFFORD THIS.\""])))
                    else:
                        goldSpent = 0
                        if playersPrice < golemsPrice:
                            goldSpent = golemsPrice - playersPrice
                            player.gold -= goldSpent
                            
                        print(f"You buy {c.highlight(golemsDeal.get_name())} for {c.highlight(goldSpent)} gold.")

                        if goldSpent > 0:
                            print("The golem absorbs the gold.")

                        if len(player.inventory) < player.inventorySize:
                            player.inventory.append(golemsDeal)
                            golemsDeal.pickup

                            sort_inventory()
                        else:
                            print("You drop the item because you are carrying too many things!")
                            room.loot.append(golemsDeal)

                        room.stock.remove(golemsDeal)
                        break

                elif playerInput == -1:
                    if len(playersDeal) > 0:
                        removedItem = playersDeal[-1]

                        playersPrice -= removedItem.get_price(False, False)
                        print(f"You remove {removedItem.get_name()} from the deal.")

                        removedItem.pickup()
                        player.inventory.append(removedItem)

                        sort_inventory()

                        playersDeal.pop(-1)
                    else:
                        print("There is nothing to undo!")

                else:
                    addedItem = player.inventory[playerInput]
                    playersDeal.append(addedItem)
                    playersPrice += addedItem.get_price(False, False)

                    if addedItem == player.armor:
                        addedItem.unequip()
                        player.armor = None

                    elif addedItem == player.ring:
                        addedItem.unequip()
                        player.ring = None

                    addedItem.discard()
                    player.inventory.remove(addedItem)

                    print(f"You add {addedItem.get_name()} to the deal.")

    def action_unlock_chest(self):
    # called when player uses an item
        room = self.get_room()
        
        room.unlock_chest()

    def action_surprise(self):
        room = self.get_room()
        
        if room.areEnemiesAware:
            print("You have already fought these enemies, they will not be surprised.")
            playerInput = gather_input("Are you sure you want to surprise attack?", ["cancel", "surprise attack"])

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
            print()
            
            if room.description != "":
                print(room.description)
                print()

            print_player_info()
            print(f"Your inventory contains {len(player.inventory)}/{player.inventorySize} items.")

            options = self.get_options()
            
            playerInput = gather_input("\nWhat do you do?", options, False)

            actions = {
                "move":self.action_move, "wait":self.action_wait, 
                "view stats":self.action_view_stats, "inventory":self.action_inventory,
                c.loot("take item"):self.action_take_item, c.special("shop"):self.action_shop,
                c.special("unlock chest"):self.action_unlock_chest, c.threat("surprise attack"):self.action_surprise
            }
            
            if playerInput in actions.keys(): # some actions aren't in the dictionary
                actions[playerInput]()
                
            elif playerInput == "debug : reveal map":
                self.map = self.layout

            elif playerInput == c.special("descend stairs"):
                break

class Room:
    blocked = False # determines if it counts as a wall or not
    description = ""
    specialAction = ""

    areEnemiesAware = False # once a combat is over, this is set to True, these enemies cannot be surprised if it's True
    
    def __init__(self, loot = [], threats = [], description = ""):
        self.loot = loot
        self.threats = threats
        self.description = description

    def unblock(self): # called if the room needs a bomb or key to unlock
        return True
    
    def check_detection(self): # checks if player notices enemies here
        detected = False
        for enemy in self.threats:
            if player.awareness >= enemy.stealth:
                detected = True

        return detected

class Chest(Room):
    blocked = False
    description = "There is a " + c.special("chest") + " here with a " + c.highlight("gold lock") + "."
    specialAction = "unlock chest"

    def __init__(self):
        self.loot = []
        self.threats = []
        self.hiddenLoot = [items.gen_loot()]

    def unlock_chest(self):
        if unlock(items.GoldKey):
            self.loot.extend(self.hiddenLoot)

            print("You unlock the chest.")
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
        print("There is a wall in the way.")
        
        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(item.get_name())
        
        itemUsed = gather_input("How do you destroy it?", options)

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

        self.loot = [items.gen_gear(depth + 1), items.gen_item(depth + 2)]

    def unblock(self): # requires a certain key
        print(f"This room is locked and requires a iron key.")

        if unlock(items.IronKey):
            print("The gate opens.")
            return True
        else:
            return False

class Stairs(Room):
    blocked = False
    description = "There are " + c.highlight("stairs") + " here that lead down."
    specialAction = "descend stairs"
    
    def __init__(self):
        self.loot = []
        self.threats = []

class Shop(Room):
    blocked = False
    description = "You stumble upon the " + c.highlight("SHOPKEEPER") + ", an ancient stone golem."
    specialAction = "shop"

    def __init__(self, depth):
        self.loot = []
        self.threats = []

        self.stock = [items.gen_gear(depth + 3), items.gen_gear(depth), items.gen_item(depth + 5), items.gen_loot()]
        if self.stock[0].enchantable:
            self.stock[0].enchantment += 1
        
        if self.stock[1].enchantable:
            self.stock[1].enchantment += randint(1, 2)

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
        
        loot.append(items.gen_loot())
        
        for i in range(randint(1, 2)):
            loot.append(items.gen_item(depth + 3 - i))

    room.threats = threats
    room.loot = loot
    
    return room
    
class Generator:
# generates floors
    def gen_floor(self, area, depth, size):
        # stores info about progression
        self.area = area
        self.depth = depth

        self.modifier = ""
        self.entryMessage = ""

        # stores info about the layout
        self.size = size
        self.layoutNums = [] # this is the layout in integers
        self.layoutRooms = [] # layoutNums is converted into rooms
        self.startY = 0
        self.startX = 0

        # stores info for room placement
        self.rooms = []
        self.adjacentWalls = []
        self.hiddenWalls = []
        self.sideRooms = []

        # adds these features before finishing generation
        self.addRooms = [LockedRoom(self.depth)]
        self.addItems = [items.IronKey(), items.KnowledgeBook(), items.Rations()]
        self.addEnemies = []
        
        # assigns modifier
        if self.size > 4 and randint(0, 1):
            self.modifier = choice(["dangerous", "large", "cursed"])

            self.entryMessage = {
                "dangerous":c.warning("You feel unsafe, watch your back."),
                "large":c.desc("You hear your footsteps echo across the floor."),
                "cursed":c.warning("A malevolent energy is lurking here.")
            }[self.modifier]

            if self.modifier == "large":
                self.size += 1

        # forms a square
        for i in range(self.size):
            self.layoutNums.append([0] * self.size)

        # generates rooms
        generation = choice([self.gen_hall, self.gen_random, self.gen_intersection, self.gen_square])
        generation()
            
        self.count_rooms()
        self.gen_rooms(((self.size * self.size) - len(self.rooms)) // 3)

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

        # generates starting room
        #self.layoutRooms[self.startY][self.startX] = Room()
        #if self.depth != 0:
        #    self.layoutRooms[self.startY][self.startX] = StairsUp()

        self.addItems.extend(self.gen_random_items(self.size + randint(0, 1), self.size - randint(2, 3)))
        
        # spawns enemies
        if self.modifier == "dangerous":
            self.addEnemies.extend(entities.gen_enemies(self.area, self.size, self.depth, self.depth % 3))
        else:
            self.addEnemies.extend(entities.gen_enemies(self.area, self.size - 1, self.depth, self.depth % 3))
    
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
        chosenGear = []
        for i in range(gearAmount):
            randomItem = items.gen_gear(self.depth)

            # can't have more than 2 of the same item per floor
            while chosenGear.count(type(randomItem)) > 1:
                 randomItem = items.gen_gear(self.depth)

            # cursed modifier has a 1 in 3 chance to degrade every item
            if self.modifier == "cursed" and randomItem.enchantable and randint(1, 3) == 1:
                randomItem.enchantment -= 1

            chosenGear.append(type(randomItem))
            spawnedItems.append(randomItem)

        # spawns items
        chosenItems = []
        for i in range(itemAmount):
            randomItem = items.gen_item(self.depth)
            
            while type(randomItem) in chosenItems:
                 randomItem = items.gen_item(self.depth)

            chosenItems.append(type(randomItem))
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

    def finish_floor(self):
        self.spawn_rooms()
        self.spawn_items()
        self.spawn_enemies()

        return Floor(self.layoutRooms, self.startY, self.startX, self.entryMessage)