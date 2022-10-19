import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(0)])

layout = [
    [dungeon.Room(), dungeon.Room([items.Mace(2)]), dungeon.Room([], [entities.Skeleton()])],
    [dungeon.Room(), dungeon.Wall(), dungeon.Wall()],
    [dungeon.Room(), dungeon.Room(), dungeon.Wall()]
]

floor1 = dungeon.Floor(layout, 0, 0)
floor1.enter_floor()