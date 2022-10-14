import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(3), items.Spear(3), items.Bandage()])
enemies = [entities.ArmoredSkeleton(), entities.Draugr()]

battle = dungeon.Battle(enemies)
battle.start_battle()