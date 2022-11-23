import dungeon
import entities
from extra import clear_console
import items
from random import randint

player = entities.player

player.inventory.extend([items.JudgementSword(), items.EbonyDagger(), items.Rations(), items.Bomb()])
player.set_stats(1, 0, 1, 1, 0)

dungeon.sort_inventory()

#battle = dungeon.Battle([entities.Ogre()])
#battle.start_battle()

goldKeyLocation = randint(0, 2)

floors = []

for i in range(3):
    generator = dungeon.Generator()
    generator.gen_floor("prison", i, 4 + ((i + 2) // 3))

    if i == goldKeyLocation: # adds gold key
        generator.spawn_item(items.Key(1))
    
    if i % 3 == 1: # adds shops
        generator.add_room(dungeon.Shop(i))

    elif i % 3 == 2: # adds gold chest
        generator.add_room(dungeon.Chest())

    floors.append(dungeon.Floor(generator.layoutRooms, generator.startY, generator.startX, generator.entryMessage))

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