from random import randint, choice
from extra import clear_console, gather_input
import entities
import items

player = entities.player

def item_list():
# returns a list of item names
    itemList = []
    for item in player.inventory:
        itemList.append(f"{item.name} {item.status()}")

    return itemList

def update_effects(creature):
# iterates through every effect
    for i in range(len(creature.effects)):
        creature.effects[i].update()
        creature.effectDurations[i] -= 1

    # deletes expired effects
    while 0 in creature.effectDurations:
        effectIndex = creature.effectDurations.index(0)
        creature.effects[effectIndex].reverse()

        creature.effects.pop(effectIndex)
        creature.effectDurations.pop(effectIndex)

class Battle:
    def __init__(self, enemies):
        self.battleOver = False
        self.enemies = enemies

    def start_battle(self):
        clear_console()
        print("You are ATTACKED!")
        while not self.battleOver:
            self.print_battle()
            self.player_turn()

            updatedEnemies = []
            for enemy in self.enemies:
                if enemy.health > 0:
                    self.enemy_turn(enemy)
                    if enemy.health > 0: # checks if enemy died during thier turn
                        updatedEnemies.append(enemy)
            self.enemies = updatedEnemies

            if self.enemies == [] or player.health <= 0:
                self.battleOver = True

        # detects if player won or lost
        if player.health > 0:
            return True
        else:
            return False

    def print_battle(self):
        print()
        creatures = self.enemies + [player]

        for creature in creatures:
            print(f"{creature.name.upper()} : {creature.health}/{creature.maxHealth} HP, {creature.armorClass} AC")
            
            effects = []
            for i in range(len(creature.effects)):
                effects.append(f"{creature.effects[i].name} - {creature.effectDurations[i]} turns")

            if len(effects) > 0:
                print(f"[{' | '.join(effects)}]")

            print()

        # prints out what you are wearing
        if player.armor != None or player.ring != None:
            equipmentMessage = "you are wearing "
            if player.armor != None:
                equipmentMessage += player.armor.name
                # if both are there it adds "and"
                if player.ring != None:
                    equipmentMessage += " and "
            if player.ring != None:
                equipmentMessage += "a " + player.ring.name
            print(equipmentMessage + "\n")
            print()
    
    def enemy_turn(self, enemy):
        enemy.do_turn(self.enemies)
        update_effects(enemy)

    def player_turn(self):
        turnOver = False
        while not turnOver:
            itemUsed = gather_input("What do you use?", item_list())

            turnOver = player.inventory[itemUsed].attack(self.enemies)

        update_effects(player)


class Floor:
    def __init__(self, layout, posY, posX): # posY and posX are player's position
        self.layout = layout
        self.posY = posY
        self.posX = posX

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
        lines = [''] * len(self.map)
        for i in range(len(self.map)):
            for I in range(len(self.map)):
                # player is represented as 'o'
                if i == self.posY and I == self.posX:
                    lines[i] += 'o'
                # unkown is represented as '?'
                elif self.map[i][I] == '?':
                    lines[i] += '?'
                # walls are represented as ' '
                elif self.map[i][I].blocked:
                    lines[i] += ' '
                # stairs are represented as ↓ or ↑
                elif self.map[i][I].specialAction == "stairs down":
                    lines[i] += '↓'
                elif self.map[i][I].specialAction == "stairs up":
                    lines[i] += '↑'
                # rooms are represented as '+'
                else:
                    lines[i] += '+'

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
            print("there is a wall there, it is protected by magic and is indestructible")
            return False

        # checks if new tile is a wall
        if self.layout[newY][newX].blocked:
            if self.layout[newY][newX].unblock():
                self.layout[newY][newX].blocked = False
                return True
            else:
                return False
        # updates players position
        else:
            self.posY = newY
            self.posX = newX
            return True

    def get_room(self):
    # retunrs the room that the player is in
        return self.layout[self.posY][self.posX]

    def enter_floor(self):
    # starts when player enters the floor, ends when they exit
    # returns -1 or 1, representing the change in floor
        clear_console()
        self.update_map()
        
        while player.health > 0:
            room = self.get_room()

            # ===== PRINTS INFORMATION =====
            self.print_map()
            print()
            
            if room.description != "":
                print(room.description)
                print()

            print(f"You have {player.health}/{player.maxHealth} HP")
            
            effects = []
            for i in range(len(player.effects)):
                effects.append(f"{player.effects[i].name} - {player.effectDurations[i]} turns")

            if len(effects) > 0:
                print(f"[{' | '.join(effects)}]")

            # prints out what you are wearing
            if player.armor != None or player.ring != None:
                equipmentMessage = "you are wearing "
                if player.armor != None:
                    equipmentMessage += player.armor.name
                    # if both are there it adds "and"
                    if player.ring != None:
                        equipmentMessage += " and "
                if player.ring != None:
                    equipmentMessage += "a " + player.ring.name
                print(equipmentMessage + "\n")

            # ===== CHECKS OPTIONS =====
            options = ["move", "wait"]
            if player.inventory != []:
                options.extend(["use item", "drop item"])
            if room.specialAction != "":
                options.append(room.specialAction)
            if room.threats != []:
                options.append("surprise attack")
                # prints enemies
                if len(room.threats) == 1:
                    print(f"there is a {room.threats[0].name.upper()} here!")
                else:
                    # gets a list of uppercase enemy names
                    names = []
                    for enemy in room.threats:
                        names.append(enemy.name.upper())
                        
                    print(f"there is a {', '.join(names[0:-1])}, and a {names[-1]} here!")
                    
                print("they do not notice you")
            if room.loot != []:
                options.append("take item")
                # prints items
                if len(room.loot) == 1:
                    print(f"there is a {room.loot[0].name} here")
                else:
                    # gets a list of item names
                    names = []
                    for item in room.loot:
                        names.append(item.name)
                        
                    print(f"there is a {', '.join(names[0:-1])}, and a {names[-1]} here")

            # presents options to player and gathers input
            if room.loot != [] or player.inventory != []:
                options.append("inspect item")
            playerInput = gather_input("\nWhat do you do?", options, False)
            
            # ===== MOVE =====
            if playerInput == "move":
                # gathers input and moves the player
                options = ["↑", "→", "↓", "←"]

                self.print_map()
                self.move_player(gather_input("\nWhat direction do you move?", options))

                self.update_map()
                update_effects(player)

                # handles stealth and combat
                room = self.get_room()
                if room.threats != []:
                    # decides if enemies detect player
                    isNoticed = False
                    for enemy in room.threats:
                        if (enemy.awareness + randint(-1, 1)) >= player.stealth:
                            isNoticed = True
                            
                    # does battle
                    if isNoticed:
                        battle = Battle(room.threats)
                        battle.start_battle()

                        room.threats = []

            # ===== USE ITEM =====
            elif playerInput == "wait":
                self.update_map()
                update_effects(player)
                print("you wait")
            elif playerInput == "use item":
                options = ["cancel"] + item_list()
                itemUsed = gather_input("what do you use?", options)

                if itemUsed != 0: # 0 is cancel, anything else is an item index
                    itemUsed -= 1 # reverts to proper index

                    player.inventory[itemUsed].consume(self)

            # ===== TAKE ITEM =====
            elif playerInput == "take item":
                if len(player.inventory) < player.inventorySize:
                    options = []
                    for item in room.loot:
                        options.append(item.name)
    
                    # if there are multiple items it asks for input
                    chosenItem = 0
                    if len(options) > 1:
                        chosenItem = gather_input("What do you pick up?", options)
    
                    # moves item to inventory
                    player.inventory.append(room.loot.pop(chosenItem))
                    print(f"you pickup the {options[chosenItem]}")
                else:
                    print(f"you are carrying too much, you can only have {player.inventorySize} items")

            # ===== SURPRISE ATTACK =====
            elif playerInput == "drop item":
                options = ["cancel"] + item_list()

                chosenItem = gather_input("What do you drop?", options)

                if chosenItem > 0: # 0 is cancel
                    chosenItem -= 1 # changes index back to normal
                    # removes item to inventory, leaving it in the room
                    room.loot.append(player.inventory.pop(chosenItem))
                    print(f"you drop the {options[chosenItem + 1]}")

            # ===== INSPECT ITEM =====
            elif playerInput == "inspect item":
                options = item_list()
                for item in room.loot:
                    options.append(item.name)

                chosenItem = gather_input("What do you inspect?", options)

                if chosenItem < len(player.inventory):
                    player.inventory[chosenItem].inspect()
                else:
                    room.loot[chosenItem - len(player.inventory)].inspect()

            # ===== SURPRISE ATTACK =====
            elif playerInput == "surprise attack":
                for enemy in room.threats:
                    enemy.affect(entities.Surprised, 2)
                    enemy.stunned = True

                battle = Battle(room.threats)
                battle.start_battle()

                room.threats = []

            # ===== STAIRS =====
            elif playerInput == "stairs up":
                return -1
            elif playerInput == "stairs down":
                return 1

class Room:
    blocked = False # determines if it counts as a wall or not
    description = ""
    specialAction = ""
    
    def __init__(self, loot = [], threats = [], description = ""):
        self.loot = loot
        self.threats = threats
        self.description = ""

    def unblock(self): # called if the room needs a bomb or key to unlock
        return True
    


class Wall(Room):
    blocked = True
    description = "you are in a tunnel, there is rubble everywhere"
    specialAction = None

    def __init__(self):
        self.loot = []
        self.threats = []

    def unblock(self): # requires a bomb or pickaxe
        print("there is a wall in the way")
        
        # gathers input
        options = ["cancel"]
        for item in player.inventory:
            options.append(f"{item.name} {item.status()}")
        
        itemUsed = gather_input("How do you destroy it?", options)

        # checks if item works then uses it
        tunnelDug = False
        if itemUsed > 0: # 0 is cancel
            itemUsed -= 1 # reverts back to proper index
            tunnelDug = player.inventory[itemUsed].dig()

        return tunnelDug

class StairsDown(Room):
    blocked = False
    description = "there are stairs here that lead down"
    specialAction = "stairs down"
    
    def __init__(self):
        self.loot = []
        self.threats = []

class StairsUp(Room):
    blocked = False
    description = "there are stairs here that lead up"
    specialAction = "stairs up"

    def __init__(self):
        self.loot = []
        self.threats = []

def gen_room(area, depth, type):
    loot = []
    threats = []
    room = Room()

    # standard room
    if type == 1:
        if area == "prison":
            if randint(1, 3) == 1:
                room.description = "you are in an empty prison cell"

    # special room
    elif type == 2:
        if area == "prison":
            roomDesc = randint(1, 6)
            if roomDesc == 1:
                room.description = "you are in a storage room"
            elif roomDesc == 2:
                room.description = "it appears that you are in what used to be an armory"
            elif roomDesc == 3:
                room.description = "you are in a large empty room"
        
        if randint(1, 2) <= 1:
            if randint(1, 3) == 1:
                loot.append(items.gen_gear(depth))
            else:
                loot.append(items.gen_item(depth))
    
        if randint(1, 3) == 1:
            threats.append(entities.gen_enemy(area, depth % 3))
            if randint(1, 3) == 1:
                threats.append(entities.gen_enemy(area, (depth % 3) - 4))

    # secret room
    elif type == 3:
        room.description = "this is a secret room, if you didn't use a bomb to find this then uh-oh"
        
        loot.append(items.gen_gear(depth + 3))
        for i in range(randint(1, 2)):
            loot.append(items.gen_item(depth + 2 - i))

    room.threats = threats
    room.loot = loot
    
    return room
    
class Generator:
# generates floors
    def gen_floor(self, area, depth, size):
        # stores info about progression
        self.area = area
        self.depth = depth

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

        # forms a square
        for i in range(self.size):
            self.layoutNums.append([0] * self.size)

        # generates rooms
        self.gen_hall()
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
                    room = StairsDown()
                
                self.layoutRooms[y].append(room)

        # generates starting room
        if self.depth == 0:
            self.layoutRooms[self.startY][self.startX] = Room()
        else:
            self.layoutRooms[self.startY][self.startX] = StairsUp()

        # adds consistent encounters (loot & enemies)
        self.spawn_item(items.Rations())
        self.spawn_item(items.gen_gear(self.depth))
        
        return Floor(self.layoutRooms, self.startY, self.startX)
    
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
                                break;

                    # checks if viable for secret room
                    if not adjacentToRoom:
                        self.hiddenWalls.append([y, x])

    def gen_rooms(self, amount):
        viableLocations = self.adjacentWalls
        for i in range(amount):
            if len(self.adjacentWalls) > 0:
                # picks a spot for a room
                location = choice(viableLocations)
                # places room
                self.layoutNums[location[0]][location[1]] = 2
    
                # changes lists accordingly
                self.rooms.append(location)
                self.adjacentWalls.remove(location)

                y = location[0]
                x = location[1]

                # adds nearby exposed walls to adjacentWalls
                for i in [[y - 1, x], [y + 1, x], [y, x - 1], [y, x + 1]]:
                    if (i[0] < self.size) and (i[1] < self.size) and (i[0] >= 0) and (i[1] >= 0):
                        if self.layoutNums[i[0]][i[1]] == 0 and not i in self.adjacentWalls:
                            self.adjacentWalls.append(i)

    def spawn_item(self, item):
        room = choice(self.rooms)
        self.layoutRooms[room[0]][room[1]].loot.append(item)