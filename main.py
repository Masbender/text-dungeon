import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(0), items.Ring(2), items.Rations()])
player.update_dexterity(1)

generator = dungeon.Generator()

floors = [generator.gen_floor("prison", 0, 4), generator.gen_floor("prison", 1, 5)]

floor = 0
while player.health > 0:
    floor += floors[floor].enter_floor()