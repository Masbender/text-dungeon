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
    
    def enemy_turn(self, enemy):
        enemy.do_turn(self.enemies)
        update_effects(enemy)

    def player_turn(self):
        turnOver = False
        while not turnOver:
            itemUsed = gather_input("What do you use?", item_list())

            turnOver = player.inventory[itemUsed].attack(self.enemies)

            if player.inventory[itemUsed].uses <= 0:
                player.inventory.pop(itemUsed)

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

                    player.inventory[itemUsed].consume()

                    if player.inventory[itemUsed].uses <= 0:
                        player.inventory.pop(itemUsed)

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
                
            elif playerInput == "inspect item":
                options = item_list()
                for item in room.loot:
                    options.append(item.name)

                chosenItem = gather_input("What do you inspect?", options)

                if chosenItem < len(player.inventory):
                    player.inventory[chosenItem].inspect()
                else:
                    room.loot[chosenItem - len(player.inventory)].inspect()
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
    
    def __init__(self, loot = [], threats = []):
        self.loot = loot
        self.threats = threats

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
    
            if player.inventory[itemUsed].uses <= 0:
                player.inventory.pop(itemUsed)

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

def gen_room(area, id):
    loot = []
    threats = []
    if id == 0:
        if randint(1, 3) == 1:
            if randint(1, 3) == 1:
                loot = [items.gen_item(area, 1)]
            else:
                loot = [items.gen_item(area, 0)]

        if randint(1, 3) == 1:
            if randint(1, 3) == 1:
                threats = entities.gen_enemies(area, 1)
            else:
                threats = entities.gen_enemies(area, 0)
        
        return Room(loot, threats)