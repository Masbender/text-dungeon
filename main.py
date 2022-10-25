import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(0), items.Bomb()])
player.update_dexterity(1)

layout1 = [
    [dungeon.Room(), dungeon.gen_room("prison", 0), dungeon.gen_room("prison", 0)],
    [dungeon.gen_room("prison", 0), dungeon.Wall(), dungeon.Wall()],
    [dungeon.gen_room("prison", 0), dungeon.StairsDown(), dungeon.Wall()]
]

layout2 = [
    [dungeon.gen_room("prison", 0), dungeon.gen_room("prison", 0), dungeon.gen_room("prison", 0)],
    [dungeon.gen_room("prison", 0), dungeon.gen_room("prison", 0), dungeon.Wall()],
    [dungeon.Wall(), dungeon.gen_room("prison", 0), dungeon.Wall()]
]

floors = [dungeon.Floor(layout1, 0, 0), dungeon.Floor(layout2, 1, 1)]

floor = 0
while player.health > 0:
    floor += floors[floor].enter_floor()