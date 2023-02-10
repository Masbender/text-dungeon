import dungeon
import entities
from extra import clear_console
from extra import gather_input
import items
import color
from random import randint
import pickle

player = entities.player
c = color

load = False
floors = []


if input("Load previous save? (y/n) : ").lower() == 'y':
    file1 = open("player.p", "rb")
    file2 = open("level.p", "rb")
    entities.player = pickle.load(file1)
    player = entities.player
    items.player = player
    dungeon.player = player
    floors = pickle.load(file2)
    file1.close()
    file2.close()
else:
    # placeholder character selection
    print("\nGuard is a well equipped soldier.\nThey were patrolling the prison when they found themselves lost in the dungeon.\n")
    print("Thief is well rounded but poorly equipped.\nThey escaped their cell but got lost in the dungeon.\n")
    print("Assassin is specialized in stealth.\nAfter the prison was cursed, they were the first to be sentenced to the dungeon.\n")
    playerInput = gather_input("Choose a character:", ["Warrior", "Thief", "Assassin"], False, False)
    
    introMessage = ""
    
    if playerInput == "Warrior":
        player.inventory.extend([items.Spear(0), items.HeavyArmor(0), items.Rations()])
        player.inventory[1].consume(None)
        player.set_stats(1, 0, 0, 2, 0)
        introMessage = "While patrolling the halls of the Prison you become lost, the halls feel like a maze and you cannot find the way back."
    
    if playerInput == "Thief":
        player.inventory.extend([items.Sword(0), items.Bandage()])
        player.set_stats(0, 1, 0, 1, 2)
        introMessage = "You manage to escape your cell, but you soon become lost in the halls of the Prison."

    if playerInput == "Assassin":
        player.inventory.extend([items.Dagger(1), items.Cloak(), items.StunBomb()])
        player.inventory[1].consume(None)
        player.inventory[0].uses = 10
        player.set_stats(-1, 0, 1, 0, 1)
        introMessage = "You have only recently been thrown into the cursed prison, yet all fresh air has already disappeared."
    
    if playerInput == "Sorcerer":
        player.inventory.extend([items.Mace(0), items.MagicRobe(), items.PoisonWand()])
        player.inventory[2].enchantment += 1
        player.set_stats(-1, 0, 1, 0, 3)
        player.inventory[1].consume(None)
    
    
    dungeon.sort_inventory()
    
    # GENERATION START
    goldKeyLocation = randint(0, 2)
    
    areas = ["prison", "crossroads", "stronghold"]
    
    floors = []
    
    for i in range(6):
        generator = dungeon.Generator()
        area = areas[i // 3]
    
        generator.gen_floor(area, i, 4 + ((i + 2) // 3))
    
        if i % 3 == 0:
            message = c.blue({
                "prison":"Welcome to the Dungeon. " + introMessage,
                "crossroads":"You have entered the Crossroads. The halls are sewer like and the sounds of rats are everywhere."
            }[area] + "\n")
            generator.entryMessage = message + generator.entryMessage
    
        if i == goldKeyLocation: # adds gold key
            generator.addItems.append(items.GoldKey())
        
        if i % 3 == 1: # adds shops
            generator.addRooms.append(dungeon.Shop(i))
    
        elif i % 3 == 2: # adds gold chest
            generator.addRooms.append(dungeon.Chest(i))
            goldKeyLocation = i + randint(1, 3)
    
        floors.append(generator.finish_floor())
    
        if i % 3 == 2: # adds boss
            floors.append(dungeon.Floor([[dungeon.Room([items.Rations()], []), dungeon.Room([], [entities.Ogre()])], [dungeon.Wall(), dungeon.Stairs()]], 0, 0))
    # GENERATION END


while True:
    player.currentFloor = floors[0]
    floors[0].enter_floor()
    floors.pop(0)

    if player.health <= 0:
        clear_console()
        print("you died")
        break

    elif 0 == len(floors):
        clear_console()
        print("thanks for playing")
        break

    for item in player.inventory:
        item.recharge()

    player.floor = None
    file1 = open("player.p", "wb")
    file2 = open("level.p", "wb")
    pickle.dump(player, file1)
    pickle.dump(floors, file2)
    file1.close()
    file2.close()