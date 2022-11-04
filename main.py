import dungeon
import entities
import extra
import items
from random import randint

player = entities.player

player.inventory.extend([items.Sword(0), items.Rations(), items.Bomb()])
player.set_stats(1, 0, 1, 1, 0)

dungeon.sort_inventory()

#battle = dungeon.Battle([entities.Ogre()])
#battle.start_battle()

floors = []

for i in range(3):
    generator = dungeon.Generator()
    floors.append(generator.gen_floor("prison", i, 4 + ((i + 2) // 3)))

floors.append(dungeon.Floor([[dungeon.Room([items.Rations()], []), dungeon.Room([], [entities.Ogre()])], [dungeon.Wall(), dungeon.Wall()]], 0, 0))

floor = 0
while player.health > 0:
    floor += floors[floor].enter_floor()