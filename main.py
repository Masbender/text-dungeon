import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(0), items.Bandage()])
enemies = [entities.Skeleton(), entities.Skeleton()]

battle = dungeon.Battle(enemies)
battle.start_battle()