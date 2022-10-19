import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(0)])
player.update_dexterity(1)

layout = [
    [dungeon.Room(), dungeon.Room([items.Mace(2)]), dungeon.Room([], [entities.Skeleton(), entities.Skeleton()])],
    [dungeon.Room([items.Bandage()]), dungeon.Wall(), dungeon.Wall()],
    [dungeon.Room([items.Sword(3)], [entities.Draugr()]), dungeon.Room(), dungeon.Wall()]
]

floor1 = dungeon.Floor(layout, 0, 0)
floor1.enter_floor()