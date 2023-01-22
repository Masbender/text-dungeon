import dungeon
import entities
from extra import clear_console
from extra import gather_input
import items
from random import randint

player = entities.player

# placeholder character selection
playerInput = gather_input("Choose a character:", ["Warrior", "Thief", "Sorcerer"], False)

if playerInput == "Warrior":
    player.inventory.extend([items.Spear(0), items.HeavyArmor(0), items.Rations()])
    player.set_stats(1, 1, 0, 1, 0)

if playerInput == "Thief":
    player.inventory.extend([items.Dagger(0), items.Cloak(), items.Bomb()])
    player.set_stats(0, -1, 1, 2, 1)

if playerInput == "Sorcerer":
    player.inventory.extend([items.Mace(0), items.MagicRobe(), items.PoisonWand()])
    player.inventory[2].enchantment += 1
    player.set_stats(-1, 0, 1, 0, 3)

player.inventory[1].consume(None)

dungeon.sort_inventory()

# GENERATION START
goldKeyLocation = randint(0, 2)

areas = ["prison", "crossroads", "dungeon"]

floors = []

for i in range(6):
    generator = dungeon.Generator()
    area = areas[i // 3]

    generator.gen_floor(area, i, 4 + ((i + 2) // 3))

    if i == goldKeyLocation: # adds gold key
        generator.addItems.append(items.GoldKey())
    
    if i % 3 == 1: # adds shops
        generator.addRooms.append(dungeon.Shop(i))

    elif i % 3 == 2: # adds gold chest
        generator.addRooms.append(dungeon.Chest())

    floors.append(generator.finish_floor())

    if i % 3 == 2: # adds boss
        floors.append(dungeon.Floor([[dungeon.Room([items.Rations()], []), dungeon.Room([], [entities.Ogre()])], [dungeon.Wall(), dungeon.Stairs()]], 0, 0))
# GENERATION END

floor = 0
while True:
    player.currentFloor = floors[floor]
    floors[floor].enter_floor()
    floor += 1

    if player.health <= 0:
        clear_console()
        print("you died")
        break

    elif floor == len(floors):
        clear_console()
        print("thanks for playing")
        break

    for item in player.inventory:
        item.recharge()