import dungeon
import entities
from extra import clear_console, gather_input
import items
from random import randint

player = entities.player

playerInput = gather_input("Choose a character:", ["Warrior", "Thief"], False)

if playerInput == "Warrior":
    player.inventory.extend([items.Spear(0), items.HeavyArmor(0), items.Rations()])
    player.set_stats(1, 1, 0, 1, 0)

if playerInput == "Thief":
    player.inventory.extend([items.Dagger(0), items.Cloak(), items.Bomb()])
    player.set_stats(0, -1, 1, 2, 1)

dungeon.sort_inventory()

#battle = dungeon.Battle([entities.Ogre()])
#battle.start_battle()

goldKeyLocation = randint(0, 2)

floors = []

for i in range(3):
    generator = dungeon.Generator()
    generator.gen_floor("prison", i, 4 + ((i + 3) // 4))

    if i == goldKeyLocation: # adds gold key
        generator.addItems.append(items.Key(1))
    
    if i % 3 == 1: # adds shops
        generator.addRooms.append(dungeon.Shop(i))

    elif i % 3 == 2: # adds gold chest
        generator.addRooms.append(dungeon.Chest())

    floors.append(generator.finish_floor())

    if i % 3 == 2: # adds boss
        floors.append(dungeon.Floor([[dungeon.Room([items.Rations()], []), dungeon.Room([], [entities.Ogre()])], [dungeon.Wall(), dungeon.Wall()]], 0, 0))

floor = 0
while True:
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