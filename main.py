import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(0), items.Rations(), items.Bomb()])
player.set_stats(1, 0, 1, 1, 0)

dungeon.sort_inventory()

#battle = dungeon.Battle([entities.Ogre()])
#battle.start_battle()

generator = dungeon.Generator()

floors = [generator.gen_floor("prison", 0, 4), generator.gen_floor("prison", 1, 5), generator.gen_floor("prison", 2, 5), dungeon.Floor([[dungeon.Room([], [entities.Ogre()])]], 0, 0)]

floor = 0
while player.health > 0:
    floor += floors[floor].enter_floor()