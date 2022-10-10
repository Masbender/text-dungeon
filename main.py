import dungeon
import entities
import extra
import items

player = entities.player

player.inventory.extend([items.Sword(0)])
enemies = [entities.Draugr()]

battle = dungeon.Battle(enemies)
battle.start_battle()