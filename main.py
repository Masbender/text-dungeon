import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(0), items.Bomb()])
player.update_dexterity(1)

layout1 = [
    [dungeon.Room(), dungeon.Room([items.Mace(2)]), dungeon.Room([], [entities.Skeleton(), entities.Skeleton()])],
    [dungeon.Room([items.Bandage()]), dungeon.Wall(), dungeon.Wall()],
    [dungeon.Room([items.Sword(3)], [entities.Draugr()]), dungeon.StairsDown(), dungeon.Wall()]
]

layout2 = [
    [dungeon.Room(), dungeon.Room(), dungeon.Room()],
    [dungeon.Room(), dungeon.StairsUp(), dungeon.Wall()],
    [dungeon.Wall(), dungeon.Room(), dungeon.Wall()]
]

floors = [dungeon.Floor(layout1, 0, 0), dungeon.Floor(layout2, 1, 1)]

floor = 0
while player.health > 0:
    floor += floors[floor].enter_floor()